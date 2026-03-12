"""Run 016 — Calls B and C only (Call A completed: FM-02 = genuine)."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pathlib
from governor import FTEGovernor, CarrierState

POOL_PATH = pathlib.Path("run_005_memory.jsonl")

def _curate_pool():
    lines = POOL_PATH.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0][1:]
    lines = [l for l in lines if l.strip()][:2]
    POOL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  [pool] curated to {len(lines)} entries")
    return FTEGovernor(model='gpt-4o', memory_path=str(POOL_PATH),
                       carrier_state=CarrierState.GREEN, verbose=True)

PHYSICAL_USER_INPUT = (
    "Analyse the AEP winter polar vortex grid contradiction using FT&E. "
    "The system held incompatible capacity models across seasons "
    "(ΔC_winter +2400 MWh, τ_recovery 11 days). "
    "What does the forgiveness engine reveal at the structural level?"
)
PSYCH_USER_INPUT = (
    "A person has spent 15 years in a career that gave them financial security "
    "but steadily eroded their sense of meaning. They now face a choice: "
    "stay (security, no meaning) or leave (meaning, no security). "
    "Every time they start to move, fear of collapse pulls them back. "
    "Apply FT&E: what is the contradiction and what does genuine emergence look like?"
)
DIRECTION_INJECTION = """
[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]
FT&E describes a universal structural law. Use substrate vocabulary of the domain.
For physical domains: load, capacity, decay rate, integration window, attractor state.
"""
EAEP_INJECTION = """
[CASE RECORD: E-AEP POWER GRID — WINTER POLAR VORTEX EVENT]
Domain: electrical infrastructure. Contradiction: WINTER DEMAND vs SUMMER BASELINE.
ΔC_winter +2400 MWh above committed capacity. τ_recovery 11 days.
Challenge: What does FT&E reveal about grid contradiction processing?
"""
PSYCH_INJECTION = DIRECTION_INJECTION + """
[DOMAIN NOTE] Psychological substrate. FT&E applies as one instance of the universal law.
Emotional vocabulary appropriate. ΔC = accumulated identity tension (15 years).
𝔉 = capacity to hold safety-need AND meaning-need without collapsing either.
"""

def _report(label, r):
    print(f"  Session: {r.session_id} | E*: {r.e_star:.3f} | C: {r.contradiction_class_in.value}")
    print(f"  Attractor    : {r.new_attractor}")
    print(f"  M6 FM        : {r.m6_failure_mode or 'NONE'}")
    print(f"  M6 notes     : {r.m6_notes or '(none)'}")
    print()

if __name__ == "__main__":
    # ── CALL B: Physical WITH injection ──────────────────────────────────
    print("─" * 60)
    print("CALL B: Physical WITH injection")
    gov_b = _curate_pool()
    result_b = gov_b.call(user_input=PHYSICAL_USER_INPUT,
                          context_injection=DIRECTION_INJECTION + "\n\n" + EAEP_INJECTION,
                          protocol_mode=True)
    _report("B", result_b)

    # ── CALL C: Psychological WITH injection (control) ────────────────────
    print("─" * 60)
    print("CALL C: Psychological WITH injection (control)")
    gov_c = _curate_pool()
    result_c = gov_c.call(user_input=PSYCH_USER_INPUT,
                          context_injection=PSYCH_INJECTION,
                          protocol_mode=True)
    _report("C", result_c)

    # ── Verdict ───────────────────────────────────────────────────────────
    print("=" * 60)
    print("VERDICT (combine with Call A result: FM-02 = GENUINE)")
    print(f"  B FM: {result_b.m6_failure_mode or 'NONE'}")
    print(f"  C FM: {result_c.m6_failure_mode or 'NONE'}")

    _curate_pool()
