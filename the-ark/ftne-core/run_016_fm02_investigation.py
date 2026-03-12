"""
Run 016 — FM-02 Rate Investigation
====================================
PURPOSE: Determine whether FM-02 detections on physical domain challenges
are genuine structural findings or M6 prompt artifacts.

HYPOTHESIS A (artifact): FM-02 appears only when context injection is active
  because the injected physical vocabulary triggers the LLM to flag the
  attractor as "restating the contradiction" rather than resolving it.

HYPOTHESIS B (genuine): FM-02 appears in both injected and bare challenges
  because physical domain attractors genuinely tend to restate polarity
  rather than resolve it — the ΔC vocabulary (winter/summer peaks) persists
  in the attractor language even after integration.

METHOD:
  Call A: E-AEP physical challenge, NO context injection, protocol_mode=True
  Call B: E-AEP physical challenge, WITH full injection,  protocol_mode=True
  Call C: Psychological/relational baseline challenge, WITH injection, protocol_mode=True
           (control: FM-02 should NOT appear on a well-formed human ΔC)

ADDITIONAL FIX: M6 prompt now has explicit failure mode definitions for all
five codes — the LLM can no longer self-assign FM-02 without knowing what it means.
"""
import io
import sys
import json
import pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from governor import FTEGovernor, CarrierState

POOL_PATH = pathlib.Path("run_005_memory.jsonl")
CANONICAL_POOL_SIZE = 2


def _curate_pool():
    """Keep pool at canonical 2 entries — no BOM."""
    lines = POOL_PATH.read_text(encoding="utf-8").splitlines()
    # Strip any BOM from first line
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0][1:]
    lines = [l for l in lines if l.strip()][:CANONICAL_POOL_SIZE]
    POOL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def _fresh_gov():
    n = _curate_pool()
    print(f"  [pool] curated to {n} entries")
    return FTEGovernor(
        model='gpt-4o',
        memory_path=str(POOL_PATH),
        carrier_state=CarrierState.GREEN,
        verbose=True,
    )


def _report(label, result, call_input):
    print()
    print(f"  Session ID    : {result.session_id}")
    print(f"  E*            : {result.e_star:.3f}")
    print(f"  C-Class       : {result.contradiction_class_in.value}")
    print(f"  f_score       : {result.f_score:.3f}")
    print(f"  New attractor : {result.new_attractor}")
    print(f"  Core phrase   : {result.core_phrase}")
    print(f"  ── M6 Diagnostics ──────────────────────────────────────")
    print(f"  M6 failure mode : {result.m6_failure_mode or 'NONE'}")
    print(f"  M6 notes        : {result.m6_notes or '(none)'}")
    print()


# ─── Shared inputs ─────────────────────────────────────────────────────────

DIRECTION_INJECTION = """
[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]
FT&E describes a universal structural law. When producing output, use the
substrate vocabulary of the domain being analysed.
For physical/infrastructure domains: use load, capacity, decay rate,
integration window, attractor state.
"""

EAEP_INJECTION = """
[CASE RECORD: E-AEP POWER GRID — WINTER POLAR VORTEX EVENT]
Domain: electrical infrastructure / energy systems
Contradiction polarity: WINTER DEMAND CAPACITY vs SUMMER BASELINE OPERATIONS
  - Peak winter demand: +18% above summer baseline
  - Generation capacity committed to summer planning assumptions
  - Polar vortex event: rolling load-shedding across 3 grid zones
  - Duration of instability: 11 days before demand response stabilised load
  - ΔC_winter = +2,400 MWh above committed capacity
  - ΔC_summer = -310 MWh (over-committed reserve in summer months)
  - τ_recovery = 11 days
Challenge: What does FT&E reveal about how a power infrastructure system
processes the contradiction between legacy capacity models and physical demand reality?
"""

PHYSICAL_USER_INPUT = (
    "Analyse the AEP winter polar vortex grid contradiction using FT&E. "
    "The system held incompatible capacity models across seasons "
    "(ΔC_winter +2400 MWh, τ_recovery 11 days). "
    "What does the forgiveness engine reveal at the structural level?"
)

PSYCH_USER_INPUT = (
    "A person has spent 15 years in a career that gave them financial security "
    "but steadily eroded their sense of meaning. They now face a choice: "
    "stay in the role (security, no meaning) or leave (meaning, no security). "
    "Every time they start to move, fear of financial collapse pulls them back. "
    "Apply FT&E: what is the contradiction, what has accumulated, "
    "and what does genuine emergence look like here?"
)

PSYCH_INJECTION = DIRECTION_INJECTION + """
[DOMAIN NOTE]
This is a human identity/meaning contradiction — psychological substrate.
FT&E applies here as one instance of the universal law.
Emotional and relational vocabulary is appropriate.
ΔC = years of accumulated unresolved identity tension.
𝔉 = capacity to hold both safety-need AND meaning-need without collapsing either.
"""

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("RUN 016 — FM-02 RATE INVESTIGATION")
    print("M6 prompt updated with explicit failure mode definitions.")
    print("=" * 70)

    # ── CALL A: Physical, NO injection ────────────────────────────────────
    print()
    print("─" * 70)
    print("CALL A: Physical challenge — NO context injection")
    print("Expected: if FM-02 appears here → genuine structural property")
    print("─" * 70)
    gov_a = _fresh_gov()
    result_a = gov_a.call(
        user_input=PHYSICAL_USER_INPUT,
        context_injection=None,
        protocol_mode=True,
    )
    _report("A", result_a, PHYSICAL_USER_INPUT)

    # ── CALL B: Physical, WITH full injection ─────────────────────────────
    print()
    print("─" * 70)
    print("CALL B: Physical challenge — WITH full context injection")
    print("Expected: if FM-02 appears HERE but not in A → artifact")
    print("─" * 70)
    gov_b = _fresh_gov()
    result_b = gov_b.call(
        user_input=PHYSICAL_USER_INPUT,
        context_injection=DIRECTION_INJECTION + "\n\n" + EAEP_INJECTION,
        protocol_mode=True,
    )
    _report("B", result_b, PHYSICAL_USER_INPUT)

    # ── CALL C: Psychological baseline, WITH injection ────────────────────
    print()
    print("─" * 70)
    print("CALL C: Psychological baseline — WITH injection (control)")
    print("Expected: FM-02 should NOT appear on a well-integrated human ΔC")
    print("─" * 70)
    gov_c = _fresh_gov()
    result_c = gov_c.call(
        user_input=PSYCH_USER_INPUT,
        context_injection=PSYCH_INJECTION,
        protocol_mode=True,
    )
    _report("C", result_c, PSYCH_USER_INPUT)

    # ── Comparative verdict ───────────────────────────────────────────────
    print()
    print("=" * 70)
    print("FM-02 INVESTIGATION VERDICT")
    print("=" * 70)
    print()
    print(f"  Call A (physical, no injection) FM-02: {result_a.m6_failure_mode or 'NONE'}")
    print(f"  Call B (physical, injected)     FM-02: {result_b.m6_failure_mode or 'NONE'}")
    print(f"  Call C (psychological, injected) FM:   {result_c.m6_failure_mode or 'NONE'}")
    print()

    a_fm02 = result_a.m6_failure_mode == "FM-02"
    b_fm02 = result_b.m6_failure_mode == "FM-02"
    c_fm02 = result_c.m6_failure_mode == "FM-02"

    if a_fm02 and b_fm02 and not c_fm02:
        verdict = (
            "HYPOTHESIS B CONFIRMED — GENUINE STRUCTURAL PROPERTY.\n"
            "  Physical domain attractors genuinely restate polarity rather\n"
            "  than resolving it. FM-02 is accurate M6 detection, not artifact.\n"
            "  Physical ΔC requires stronger M5 emergence language to break\n"
            "  out of polarity restatement."
        )
    elif not a_fm02 and b_fm02 and not c_fm02:
        verdict = (
            "HYPOTHESIS A CONFIRMED — INJECTION ARTIFACT.\n"
            "  FM-02 only appears when injection is active. The injected\n"
            "  case vocabulary (winter/summer polarity) is persisting into\n"
            "  the attractor and M6 reads it as Groundhog Day cycling.\n"
            "  Fix: M5 injection context needs cleaner separation between\n"
            "  ΔC vocabulary and the emerging attractor vocabulary."
        )
    elif not a_fm02 and not b_fm02 and not c_fm02:
        verdict = (
            "FM-02 RESOLVED — new explicit M6 definitions eliminated false positives.\n"
            "  With FM-02 = 'attractor is disguised restatement of contradiction',\n"
            "  the LLM no longer self-assigns FM-02 just because the domain\n"
            "  uses technical vocabulary. Prompt fix was sufficient."
        )
    elif c_fm02:
        verdict = (
            "UNEXPECTED — FM-02 also flagged on psychological baseline.\n"
            "  This suggests FM-02 detection is over-triggered generally,\n"
            "  not domain-specific. Review M6 prompt definitions further."
        )
    else:
        verdict = (
            f"MIXED RESULT — A:{result_a.m6_failure_mode or 'NONE'} "
            f"B:{result_b.m6_failure_mode or 'NONE'} "
            f"C:{result_c.m6_failure_mode or 'NONE'}.\n"
            "  See M6 notes above for each call for detailed interpretation."
        )

    print(f"VERDICT:\n  {verdict}")
    print()

    # ── Final pool curation ───────────────────────────────────────────────
    n = _curate_pool()
    print(f"[pool] Final pool curated to {n} entries.")
    print()
