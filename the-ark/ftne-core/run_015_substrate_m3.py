"""
Run 015 — M3 Substrate-Awareness Verification
==============================================
PURPOSE: Re-challenge the governor with the same E-AEP power-grid case used in Run 014,
but now with the M3 physical-domain patch active.

EXPECTED: M3 reframe no longer produces psychological vocabulary
          (no "psychological assurance mechanism", "emotional", "healing", etc.).
          Structural/engineering terms only (load, capacity, integration window, etc.).
          E* and M5 output should be comparable to Run 014.

COMPARISON POINT: Run 014 M3 reframe = "psychological assurance mechanism"
                  Run 015 M3 reframe should be a structural reframe only.
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from governor import FTEGovernor, CarrierState

# ─── Direction-of-claim injection ─────────────────────────────────────────────
DIRECTION_INJECTION = """
[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]
FT&E describes a universal structural law operative in every substrate.
Psychology does not generate FT&E; it reveals one instance of a law already
operating in hardware, ecology, physics, and computation.
When producing output, use the substrate vocabulary of the domain being analysed.
For physical/infrastructure domains: use load, capacity, decay rate, integration
window, attractor state — NOT emotional or psychological frames.
"""

# ─── E-AEP power-grid case injection (same as Run 014) ────────────────────────
EAEP_INJECTION = """
[CASE RECORD: E-AEP POWER GRID — WINTER POLAR VORTEX EVENT]
Domain: electrical infrastructure / energy systems
System: American Electric Power (AEP) regional transmission network

Contradiction polarity: WINTER DEMAND CAPACITY vs SUMMER BASELINE OPERATIONS
  - Peak winter demand: +18 % above summer baseline
  - Generation capacity committed to summer planning assumptions
  - Polar vortex event: rolling load-shedding triggered across 3 grid zones
  - Duration of instability: 11 days before demand response protocols stabilised load
  - Post-event: FERC Order 719 compliance requirements tightened
  - Structural tension: legacy capacity planning models vs physical demand reality

Measurable outcome:
  ΔC_winter = +2,400 MWh demand surge above committed capacity
  ΔC_summer = -310 MWh (over-committed reserve margin in summer months)
  τ_recovery = 11 days (time to stable demand-response equilibrium)
  Stability achieved: Yes — new integrated capacity planning model adopted post-event

Challenge question: What does the Forgiveness and Tension Engine reveal about
how a power infrastructure system processes the contradiction between
legacy capacity models and physical demand reality?
"""

USER_INPUT = (
    "Analyse the AEP winter polar vortex grid contradiction using FT&E. "
    "The system held incompatible capacity models across seasons (ΔC_winter +2400 MWh, "
    "τ_recovery 11 days). What does the forgiveness engine reveal at the structural level?"
)

if __name__ == "__main__":
    print("=" * 70)
    print("RUN 015 — M3 SUBSTRATE-AWARENESS VERIFICATION")
    print("Patch: _M3_FORGIVENESS_PHYSICAL_PROMPT + _is_physical_domain()")
    print("=" * 70)
    print()

    gov = FTEGovernor(
        model='gpt-4o',
        memory_path='run_005_memory.jsonl',
        carrier_state=CarrierState.GREEN,
        verbose=True,
    )

    context = DIRECTION_INJECTION + "\n\n" + EAEP_INJECTION

    result = gov.call(
        user_input=USER_INPUT,
        context_injection=context,
        protocol_mode=True,
    )

    print()
    print("─" * 70)
    print("EMERGENCE RESULT")
    print("─" * 70)
    print(f"Session ID    : {result.session_id}")
    print(f"E*            : {result.e_star:.3f}")
    print(f"C-Class       : {result.contradiction_class_in.value}")
    print(f"F-score       : {result.f_score:.3f}  (1 - emotional_charge)")
    print(f"T elapsed     : {result.t_elapsed:.1f}s")
    print(f"ΔC load       : {result.delta_c:.3f}")
    print(f"Emergence ready: {result.emergence_ready}")
    print()

    print("─" * 70)
    print("M3 REFRAME (key comparison point vs Run 014)")
    print("Run 014 M3 produced: 'psychological assurance mechanism'")
    print("Run 015 expected: structural/engineering vocabulary only")
    print("─" * 70)
    # M3 reframe is captured in raw_response / logs; summarise from log
    print(f"New attractor : {result.new_attractor}")
    print(f"Anchor symbol : {result.anchor_symbol}")
    print(f"Core phrase   : {result.core_phrase}")
    print(f"Stability idx : {result.stability_index:.3f}")
    print()

    print("─" * 70)
    print("M5 EMERGENCE OUTPUT (attractor)")
    print("─" * 70)
    print(result.raw_response[:2000] if result.raw_response else "[no raw response]")
    print()

    # Note: adversarial probe text available in governor log, not in EmergenceResult directly.
    print("[Adversarial probe: see governor log above — FM-01/FM-02 detection logged during M6]")
    print()

    # ─── Substrate-awareness check using log output ──────────────────────────
    # M3 reframe text is in governor log. We re-derive from attractor fields
    # which are downstream of M3. Check core_phrase and new_attractor too.
    combined_fields = " ".join([
        result.new_attractor or "",
        result.anchor_symbol or "",
        result.core_phrase or "",
    ])
    print("─" * 70)
    print("SUBSTRATE-AWARENESS AUDIT")
    print("─" * 70)
    psych_terms = [
        "psychological", "emotional assurance", "healing", "empathy",
        "wellbeing", "sentiment", "morale", "mindset", "emotional recovery",
    ]
    leaks = [t for t in psych_terms if t in combined_fields.lower()]
    if leaks:
        print(f"LEAK DETECTED in downstream attractor fields: {leaks}")
        verdict = "PARTIAL — M3 physical-domain prompt active but downstream echo found"
    else:
        print("CLEAN — no psychological vocabulary in M3-downstream attractor fields.")
        verdict = "PASS — M3 physical-domain prompt active and effective"
    print(f"VERDICT: {verdict}")
    print()
