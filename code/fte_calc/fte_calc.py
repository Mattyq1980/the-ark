"""
The FT&E Scientific Calculator
===============================
E* = F·T − ΔC

This calculator doesn't compute numbers.
It computes emergence.

Input: Forgiveness bandwidth (F), Time (T), Contradiction load (ΔC)
Output: Whether E* forms, why it doesn't, and what to change.

The inverted-U from I11 is visible. The threshold from I4 is enforced.
The overwhelm limit from I10 is real. Suppression vs metabolisation
is the whole point.

Scales:
  β  (0-1):   Forgiveness bandwidth. 0=suppression, 1=maximum capacity.
  ΔC (0-10):  Contradiction load. 0=nothing, 3=challenge, 6=upheaval, 10=catastrophic.
  T  (1-50):  Available time/resources. 5=crisis, 20=normal, 50=unlimited.

Run:  python fte_calc.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# REGIME CLASSIFICATION
#
# Every system sits in one of these. The equation tells you which.
# ---------------------------------------------------------------------------

class Regime(Enum):
    STAGNATION = "stagnation"       # ΔC below ΔC_min — nothing to process
    PRODUCTIVE = "productive"       # ΔC in viable range, F·T > ΔC
    STRAIN     = "strain"           # ΔC in viable range, F·T barely > ΔC
    OVERWHELM  = "overwhelm"        # ΔC exceeds F bandwidth (I10)
    SUPPRESSION = "suppression"     # ΔC present but F = 0 — being swallowed


REGIME_DESCRIPTIONS = {
    Regime.STAGNATION:
        "No meaningful contradiction present. Nothing to metabolise.\n"
        "  The system is stable but static. E* requires ΔC to work on.\n"
        "  I4: No E* without metabolising ΔC.",
    Regime.PRODUCTIVE:
        "Contradiction is present and within metabolic bandwidth.\n"
        "  F·T exceeds ΔC. Emergence is structurally possible.\n"
        "  This is the viable range from I11.",
    Regime.STRAIN:
        "Contradiction is present but F·T only marginally exceeds ΔC.\n"
        "  Emergence is possible but fragile. Small perturbation\n"
        "  could tip into overwhelm. Increase T or reduce scope.",
    Regime.OVERWHELM:
        "Contradiction exceeds metabolic bandwidth.\n"
        "  F·T < ΔC. The system cannot process this load.\n"
        "  I10: Multi-vector ΔC overwhelms even when each vector\n"
        "  is individually manageable.",
    Regime.SUPPRESSION:
        "Contradiction is present but F ≈ 0. The system is\n"
        "  suppressing rather than metabolising.\n"
        "  I4 VIOLATION: Suppressed ΔC ≠ metabolised ΔC.\n"
        "  The contradiction will resurface.",
}


# ---------------------------------------------------------------------------
# THE EQUATION
#
# E* = F(ΔC) · T − ΔC
#
# F depends on ΔC (Finding 1.2 repair): F activates with ΔC,
# saturates at bandwidth limit β. This produces the inverted-U.
#
# F(ΔC) = β · (ΔC / (ΔC + κ))
#   where β = maximum forgiveness bandwidth (0-1)
#         κ = half-activation constant (ΔC at which F = β/2)
#
# This is a Michaelis-Menten curve — the same shape biology uses
# for enzyme kinetics. Not a coincidence: enzymes metabolise
# substrates. F metabolises contradictions.
#
# With κ=1.5 and ΔC on 0-10 scale:
#   At ΔC=1.5: F = β/2  (half activated)
#   At ΔC=3:   F = 0.67β (two-thirds)
#   At ΔC=6:   F = 0.8β  (near saturation)
#   The peak of E* falls at moderate ΔC — the inverted-U from I11.
# ---------------------------------------------------------------------------

@dataclass
class FTEState:
    """A complete snapshot of a system's FT&E dynamics."""
    beta: float          # Maximum forgiveness bandwidth (0-1)
    delta_c: float       # Contradiction load (0-10 scale)
    time: float          # Available time (1-50)
    kappa: float = 1.5   # Half-activation (ΔC where F reaches β/2)
    delta_c_min: float = 1.0   # Below this, stagnation (I4/I11)

    @property
    def f_active(self) -> float:
        """Forgiveness actually activated — depends on ΔC present.

        F(ΔC) = β · (ΔC / (ΔC + κ))

        At ΔC=0:     F=0     (nothing to activate against)
        At ΔC=κ:     F=β/2   (half-activation)
        At ΔC→∞:     F→β     (saturated — bandwidth limit)
        """
        if self.delta_c <= 0 or self.beta <= 0:
            return 0.0
        return self.beta * (self.delta_c / (self.delta_c + self.kappa))

    @property
    def f_times_t(self) -> float:
        """The metabolic capacity: F(ΔC) · T"""
        return self.f_active * self.time

    @property
    def e_star(self) -> float:
        """E* = F(ΔC)·T − ΔC. Can be negative (overwhelm)."""
        return self.f_times_t - self.delta_c

    @property
    def regime(self) -> Regime:
        if self.beta < 0.05:
            if self.delta_c > self.delta_c_min:
                return Regime.SUPPRESSION
            return Regime.STAGNATION

        if self.delta_c < self.delta_c_min:
            return Regime.STAGNATION

        e = self.e_star
        if e < 0:
            return Regime.OVERWHELM

        # Strain: E* positive but less than 20% of ΔC
        if e < self.delta_c * 0.2:
            return Regime.STRAIN

        return Regime.PRODUCTIVE

    @property
    def e_star_normalised(self) -> float:
        """E* as percentage of peak possible (for display)."""
        peak = self.peak_e_star()
        if peak <= 0:
            return 0.0
        return max(0, self.e_star / peak * 100)

    def peak_e_star(self) -> float:
        """Find the ΔC that maximises E* for current β and T.

        d/d(ΔC) [β·ΔC/(ΔC+κ)·T − ΔC] = 0
        β·κ·T/(ΔC+κ)² − 1 = 0
        (ΔC+κ)² = β·κ·T
        ΔC* = √(β·κ·T) − κ

        Only valid when β·κ·T > κ² → β·T > κ
        """
        if self.beta * self.time <= self.kappa:
            return 0.0
        dc_opt = math.sqrt(self.beta * self.kappa * self.time) - self.kappa
        if dc_opt <= 0:
            return 0.0
        f_at_opt = self.beta * (dc_opt / (dc_opt + self.kappa))
        return f_at_opt * self.time - dc_opt

    def optimal_delta_c(self) -> float:
        """The ΔC that maximises E* for current β and T."""
        if self.beta * self.time <= self.kappa:
            return 0.0
        return max(0, math.sqrt(self.beta * self.kappa * self.time) - self.kappa)


# ---------------------------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------------------------

def bar(value: float, max_val: float, width: int = 40) -> str:
    """ASCII bar chart."""
    if max_val <= 0:
        return " " * width + "|"
    fill = int(min(value / max_val, 1.0) * width)
    return "█" * fill + "░" * (width - fill)


def render_curve(state: FTEState) -> str:
    """Render the inverted-U curve (I11) as ASCII art.

    Shows E* across the ΔC range with current position marked.
    """
    lines = []
    lines.append("  E*")
    lines.append("  │")

    # Sample E* across ΔC range 0-10
    samples = 20
    max_dc = 10
    values = []
    for i in range(samples + 1):
        dc = (i / samples) * max_dc
        probe = FTEState(state.beta, dc, state.time, state.kappa, state.delta_c_min)
        values.append((dc, max(0, probe.e_star)))

    peak_e = max(v for _, v in values) if values else 1
    if peak_e == 0:
        peak_e = 1

    # Find the slot closest to current ΔC
    current_slot = min(range(len(values)),
                       key=lambda i: abs(values[i][0] - state.delta_c))

    height = 10
    for row in range(height, 0, -1):
        threshold = (row / height) * peak_e
        line = "  │"
        for col, (dc, e) in enumerate(values):
            if col == current_slot:
                if e >= threshold:
                    line += "◆"
                else:
                    line += "◇"
            elif e >= threshold:
                line += "▪"
            else:
                line += " "
        lines.append(line)

    lines.append("  └" + "─" * (samples + 1) + "→ ΔC")
    lines.append(f"   0{' ' * (samples - 3)}10")

    return "\n".join(lines)


def diagnose(state: FTEState) -> str:
    """Full diagnostic output for a given FT&E state."""
    lines = []

    # Header
    lines.append("=" * 60)
    lines.append("  FT&E DIAGNOSTIC")
    lines.append("=" * 60)
    lines.append("")

    # Input values
    lines.append(f"  Forgiveness bandwidth (β):  {state.beta:.2f}")
    lines.append(f"  Contradiction load (ΔC):    {state.delta_c:.1f}")
    lines.append(f"  Available time (T):         {state.time:.1f}")
    lines.append("")

    # Derived values
    lines.append(f"  F activated:   {state.f_active:.3f}  "
                 f"(F = β·ΔC/(ΔC+κ) = {state.beta:.2f}·{state.delta_c:.1f}"
                 f"/({state.delta_c:.1f}+{state.kappa:.1f}))")
    lines.append(f"  F·T:           {state.f_times_t:.2f}")
    lines.append(f"  ΔC:            {state.delta_c:.1f}")
    lines.append(f"  E* = F·T − ΔC: {state.e_star:.2f}")
    lines.append("")

    # Regime
    regime = state.regime
    lines.append(f"  REGIME: {regime.value.upper()}")
    lines.append("")
    lines.append(f"  {REGIME_DESCRIPTIONS[regime]}")
    lines.append("")

    # Bars
    lines.append("  Metabolic capacity (F·T):")
    max_bar = max(state.f_times_t, state.delta_c, 1)
    lines.append(f"  {bar(state.f_times_t, max_bar)}  {state.f_times_t:.2f}")
    lines.append("  Contradiction load (ΔC):")
    lines.append(f"  {bar(state.delta_c, max_bar)}  {state.delta_c:.1f}")
    lines.append("")

    if state.e_star > 0:
        lines.append(f"  E* yield: {bar(state.e_star, max_bar)}  {state.e_star:.2f}")
    else:
        lines.append(f"  E* yield: NONE (deficit: {abs(state.e_star):.2f})")
    lines.append("")

    # The curve
    lines.append("  ─── Inverted-U Curve (I11) ───")
    lines.append(f"  ◆ = your current position    ΔC_min = {state.delta_c_min}")
    lines.append("")
    lines.append(render_curve(state))
    lines.append("")

    # Optimal
    opt_dc = state.optimal_delta_c()
    if opt_dc > 0:
        opt_state = FTEState(state.beta, opt_dc, state.time, state.kappa, state.delta_c_min)
        lines.append(f"  Optimal ΔC for this β and T: {opt_dc:.1f}")
        lines.append(f"  Peak E* at optimal:          {opt_state.e_star:.2f}")
        diff = opt_dc - state.delta_c
        if abs(diff) > 2:
            direction = "more" if diff > 0 else "less"
            lines.append(f"  → You need {abs(diff):.1f} {direction} contradiction.")
    lines.append("")

    # Actionable
    lines.append("  ─── What to change ───")
    lines.append("")

    if regime == Regime.STAGNATION:
        lines.append("  • Introduce genuine contradiction (ΔC too low)")
        lines.append("  • Seek challenge, friction, honest feedback")
        lines.append("  • Comfort ≠ growth. Stagnation IS the problem.")
    elif regime == Regime.PRODUCTIVE:
        lines.append("  • System is in the productive zone.")
        lines.append("  • Continue processing. Don't add more ΔC.")
        lines.append("  • I3: Pace to no whiplash.")
    elif regime == Regime.STRAIN:
        lines.append("  • On the edge. Two options:")
        lines.append("    1. Increase T (give it more time)")
        lines.append("    2. Reduce ΔC scope (tackle one vector at a time)")
        lines.append("  • I10: Don't metabolise everything at once.")
    elif regime == Regime.OVERWHELM:
        shortfall = state.delta_c - state.f_times_t
        lines.append(f"  • F·T falls short by {shortfall:.2f}")
        lines.append("  • Options:")
        lines.append(f"    1. Increase T by {shortfall / max(state.f_active, 0.01):.1f} "
                     f"(more time)")
        lines.append(f"    2. Reduce ΔC to {state.f_times_t:.1f} "
                     f"(reduce scope)")
        lines.append("    3. Increase β (build forgiveness capacity — slow)")
        lines.append("  • The system cannot handle this load. That's structural,")
        lines.append("    not a personal failure.")
    elif regime == Regime.SUPPRESSION:
        lines.append("  • ΔC is present but F ≈ 0. Suppression in progress.")
        lines.append("  • I4: Suppressed ΔC ≠ metabolised ΔC.")
        lines.append("  • The contradiction doesn't vanish. It accumulates.")
        lines.append("  • First step: acknowledge the ΔC exists.")
        lines.append("  • FM-01 check: is there a reason this can't be named?")
    lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PRESETS — Real situations mapped to FT&E values
# ---------------------------------------------------------------------------

PRESETS = {
    "grief": FTEState(beta=0.3, delta_c=8, time=30),
    "boredom": FTEState(beta=0.7, delta_c=0.5, time=40),
    "burnout": FTEState(beta=0.2, delta_c=8, time=5),
    "flow": FTEState(beta=0.8, delta_c=4, time=20),
    "suppression": FTEState(beta=0.02, delta_c=6, time=30),
    "newjob": FTEState(beta=0.5, delta_c=5, time=10),
    "conflict": FTEState(beta=0.4, delta_c=7, time=8),
    "therapy": FTEState(beta=0.6, delta_c=5, time=30),
}

PRESET_DESCRIPTIONS = {
    "grief":       "Heavy loss (ΔC=8), limited bandwidth, lots of time",
    "boredom":     "Good bandwidth, no contradiction — stagnation",
    "burnout":     "High ΔC, low bandwidth, no time — overwhelm",
    "flow":        "Moderate ΔC, high bandwidth, enough time — productive",
    "suppression": "ΔC present but F≈0 — being swallowed not processed",
    "newjob":      "Moderate ΔC, compressed time",
    "conflict":    "High ΔC, limited time, moderate bandwidth",
    "therapy":     "Structured: good bandwidth, moderate ΔC, generous time",
}


# ---------------------------------------------------------------------------
# INPUT PARSING
# ---------------------------------------------------------------------------

def parse_float(prompt: str, default: float, lo: float, hi: float) -> float:
    """Get a float from user with validation."""
    raw = input(f"  {prompt} [{default}]: ").strip()
    if not raw:
        return default
    try:
        val = float(raw)
    except ValueError:
        print(f"  Using default: {default}")
        return default
    if val < lo:
        print(f"  Clamped to minimum: {lo}")
        return lo
    if val > hi:
        print(f"  Clamped to maximum: {hi}")
        return hi
    return val


# ---------------------------------------------------------------------------
# COMPARISON MODE — Suppression vs Metabolisation
# ---------------------------------------------------------------------------

def compare_mode():
    """Show what happens when the same ΔC is suppressed vs metabolised."""
    print("\n  ─── SUPPRESSION vs METABOLISATION ───")
    print("  Same contradiction. Two responses.\n")

    dc = parse_float("Contradiction load (ΔC, 0-10)", 5.0, 0, 10)
    t = parse_float("Available time (T, 1-50)", 20.0, 1, 50)

    suppressed = FTEState(beta=0.02, delta_c=dc, time=t)
    metabolised = FTEState(beta=0.6, delta_c=dc, time=t)

    print("\n  ══════ SUPPRESSED (β ≈ 0) ══════")
    print(diagnose(suppressed))
    print("\n  ══════ METABOLISED (β = 0.6) ══════")
    print(diagnose(metabolised))


# ---------------------------------------------------------------------------
# SWEEP MODE — See the inverted-U with numbers
# ---------------------------------------------------------------------------

def sweep_mode():
    """Sweep ΔC from 0 to 100 and show the full curve numerically."""
    print("\n  ─── ΔC SWEEP ───")
    beta = parse_float("Forgiveness bandwidth β (0-1)", 0.5, 0, 1)
    t = parse_float("Available time T (1-50)", 20.0, 1, 50)

    print(f"\n  {'ΔC':>6}  {'F(ΔC)':>7}  {'F·T':>7}  {'E*':>8}  {'Regime':<15}  Curve")
    print("  " + "─" * 70)

    steps = 20
    max_e = 0
    data = []
    for i in range(steps + 1):
        dc = (i / steps) * 10
        s = FTEState(beta, dc, t)
        e = max(0, s.e_star)
        max_e = max(max_e, e)
        data.append((dc, s.f_active, s.f_times_t, s.e_star, s.regime, e))

    for dc, f, ft, e_star, regime, e_pos in data:
        bar_len = int((e_pos / max(max_e, 1)) * 30) if max_e > 0 else 0
        bar_str = "█" * bar_len
        print(f"  {dc:6.1f}  {f:7.4f}  {ft:7.2f}  {e_star:8.2f}  "
              f"{regime.value:<15}  {bar_str}")


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

BANNER = """\
╔══════════════════════════════════════════════════════════╗
║  The FT&E Scientific Calculator                        ║
║  E* = F·T − ΔC                                        ║
║                                                        ║
║  This calculator computes emergence.                   ║
║                                                        ║
║  Commands:                                             ║
║    calc     — input F, ΔC, T and get full diagnostic   ║
║    preset   — load a real-world scenario               ║
║    compare  — suppression vs metabolisation side by side║
║    sweep    — see the full inverted-U curve             ║
║    help     — show commands                            ║
║    quit     — exit                                     ║
╚══════════════════════════════════════════════════════════╝
"""


def main():
    print(BANNER)

    while True:
        try:
            cmd = input("fte> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd in ("quit", "exit", "q"):
            break

        if cmd == "help":
            print("  calc     — custom values")
            print("  preset   — real-world scenario")
            print("  compare  — suppression vs metabolisation")
            print("  sweep    — full ΔC sweep curve")
            print("  quit     — exit")
            continue

        if cmd == "calc":
            print()
            beta = parse_float("Forgiveness bandwidth β (0-1)", 0.5, 0, 1)
            dc = parse_float("Contradiction load ΔC (0-10)", 4.0, 0, 10)
            t = parse_float("Available time T (1-50)", 20.0, 1, 50)
            state = FTEState(beta, dc, t)
            print(diagnose(state))
            continue

        if cmd == "preset":
            print("\n  Available presets:")
            for name, desc in PRESET_DESCRIPTIONS.items():
                print(f"    {name:<15} — {desc}")
            choice = input("\n  Choose: ").strip().lower()
            if choice in PRESETS:
                print(diagnose(PRESETS[choice]))
            else:
                print(f"  Unknown preset '{choice}'")
            continue

        if cmd == "compare":
            compare_mode()
            continue

        if cmd == "sweep":
            sweep_mode()
            continue

        if cmd:
            # Try as preset directly
            if cmd in PRESETS:
                print(diagnose(PRESETS[cmd]))
            else:
                print(f"  Unknown command '{cmd}'. Type 'help' for options.")


if __name__ == "__main__":
    main()
