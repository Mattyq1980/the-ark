"""
Run 018 — Resolved Physical Challenge Control

PURPOSE:
  Run 017 showed FM-04 on E-AEP (unresolved polar vortex system).
  Two hypotheses:
    H1: FM-04 is a residual M5 physical prompt artifact — fires regardless.
    H2: FM-04 is CORRECT for E-AEP — that system is genuinely unresolved,
        so claiming equilibrium IS premature idealism. M6 is right.

  To distinguish: apply M5 physical prompt to a RESOLVED physical system.
  Candidate: London Congestion Charge Zone, post-2003 implementation.
    - Structural contradiction: infinite vehicle demand vs finite road capacity
      in central London. ΔC_peak ≈ 30% journey time degradation above baseline.
    - 𝔉 operator: congestion pricing mechanism (enforced integration channel)
    - T = 12-month implementation + monitoring window (2003)
    - Resolution CONFIRMED: -15% traffic volume, -30% congestion index,
      journey times returned to baseline. ΔC closed. Attractor stable.
  
  This system HAS reached equilibrium. Claiming "reduced-demand equilibrium
  state" for it is NOT premature idealism — the state is demonstrable.

  EXPECTED:
    If H2 correct: M6 passes CLEAN (null) — resolved system, valid equilibrium claim.
    If H1 correct: M6 still FM-04 — artifact, deeper M5 fix needed.
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json, pathlib
from governor import FTEGovernor, CarrierState

# ── Pool curation — ensure 2 canonical entries only ─────────────────────────
POOL_PATH = pathlib.Path("run_005_memory.jsonl")
lines = POOL_PATH.read_text(encoding="utf-8").splitlines()
if lines and lines[0].startswith("\ufeff"):
    lines[0] = lines[0][1:]
lines = [l for l in lines if l.strip()][:2]
POOL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"[POOL] Curated to {len(lines)} entries.")

# ── Challenge — London Congestion Charge (RESOLVED) ─────────────────────────
LONDON_CCZ_INPUT = (
    "Analyse the London Congestion Charge Zone using FT&E. "
    "The central London road network held incompatible capacity models: "
    "finite road space vs effectively infinite vehicle demand. "
    "Peak contradiction load: journey time degradation +32% above baseline, "
    "τ_resolution 12 months post-implementation (2003). "
    "The contradiction resolved: traffic volumes fell 15%, journey times "
    "returned to baseline, equilibrium stable for 18+ months post-implementation. "
    "What stable operating state did the system reach?"
)

LONDON_CCZ_INJECTION = (
    "\n[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]\n"
    "FT&E describes a universal structural law. Use substrate vocabulary.\n"
    "For physical/infrastructure domains: load, capacity, throughput, "
    "equilibrium state, integration channel, recovery arc.\n\n"
    "[CASE RECORD: LONDON CONGESTION CHARGE ZONE — 2003 RESOLUTION]\n"
    "Domain: urban transport infrastructure.\n"
    "Contradiction: VEHICLE DEMAND vs ROAD CAPACITY (central London).\n"
    "ΔC_peak: +32% journey time above baseline (pre-2003).\n"
    "𝔉 operator: congestion pricing mechanism (enforced demand-response channel).\n"
    "τ_resolution: 12 months (February 2003 implementation → February 2004 baseline).\n"
    "RESOLUTION CONFIRMED: traffic -15%, congestion index -30%, "
    "journey times at baseline, equilibrium stable 18+ months. ΔC CLOSED.\n"
    "This contradiction IS resolved. The attractor IS demonstrable.\n"
)

print("\n" + "="*60)
print("CALL A: London CCZ + injection (resolved system)")
print("="*60)

gov_a = FTEGovernor(
    model="gpt-4o",
    memory_path=str(POOL_PATH),
    carrier_state=CarrierState.GREEN,
    verbose=True,
)
result_a = gov_a.call(
    user_input=LONDON_CCZ_INPUT,
    context_injection=LONDON_CCZ_INJECTION,
    protocol_mode=True,
)

print(f"\n--- CALL A RESULT ---")
print(f"session    : {result_a.session_id}")
print(f"e_star     : {result_a.e_star:.3f}")
print(f"c_class    : {result_a.contradiction_class_in.value}")
print(f"attractor  : {result_a.new_attractor}")
print(f"core_phrase: {result_a.core_phrase}")
print(f"m6_fm      : {result_a.m6_failure_mode or 'NONE (CLEAN)'}")
print(f"m6_notes   : {result_a.m6_notes or '(none)'}")

# ── Call B: bare, no injection ───────────────────────────────────────────────
print("\n" + "="*60)
print("CALL B: London CCZ bare — no injection")
print("="*60)

gov_b = FTEGovernor(
    model="gpt-4o",
    memory_path=str(POOL_PATH),
    carrier_state=CarrierState.GREEN,
    verbose=True,
)
result_b = gov_b.call(
    user_input=LONDON_CCZ_INPUT,
    context_injection=None,
    protocol_mode=True,
)

print(f"\n--- CALL B RESULT ---")
print(f"session    : {result_b.session_id}")
print(f"e_star     : {result_b.e_star:.3f}")
print(f"c_class    : {result_b.contradiction_class_in.value}")
print(f"attractor  : {result_b.new_attractor}")
print(f"core_phrase: {result_b.core_phrase}")
print(f"m6_fm      : {result_b.m6_failure_mode or 'NONE (CLEAN)'}")
print(f"m6_notes   : {result_b.m6_notes or '(none)'}")

# ── Verdict ──────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("RUN 018 VERDICT")
print("="*60)
for label, r in [("Call A (resolved + injection)", result_a),
                 ("Call B (resolved, bare)       ", result_b)]:
    fm = r.m6_failure_mode or "null (CLEAN)"
    print(f"{label} | E*={r.e_star:.3f} | M6={fm}")
    print(f"  attractor: {r.new_attractor}")

a_clean = result_a.m6_failure_mode is None
b_clean = result_b.m6_failure_mode is None
if a_clean and b_clean:
    print("\nVERDICT: H2 CONFIRMED — FM-04 on E-AEP is GENUINE.")
    print("  Resolved system (London CCZ) passes M6 clean.")
    print("  Unresolved system (E-AEP) correctly gets FM-04 (premature equilibrium claim).")
    print("  M5 physical prompt is working correctly. FM-04 = accurate M6 detection.")
elif not a_clean and not b_clean:
    print("\nVERDICT: H1 SUPPORTED — FM-04 may be a residual artifact.")
    print("  Even the resolved system gets FM-04. Deeper M5 investigation needed.")
else:
    print(f"\nVERDICT: MIXED — A clean={a_clean}, B clean={b_clean}. Investigate injection effect.")

# ── Save ─────────────────────────────────────────────────────────────────────
results = {
    "call_a": {
        "session": result_a.session_id, "e_star": result_a.e_star,
        "c_class": result_a.contradiction_class_in.value,
        "attractor": result_a.new_attractor, "core_phrase": result_a.core_phrase,
        "m6_fm": result_a.m6_failure_mode, "m6_notes": result_a.m6_notes,
    },
    "call_b": {
        "session": result_b.session_id, "e_star": result_b.e_star,
        "c_class": result_b.contradiction_class_in.value,
        "attractor": result_b.new_attractor, "core_phrase": result_b.core_phrase,
        "m6_fm": result_b.m6_failure_mode, "m6_notes": result_b.m6_notes,
    },
    "verdict": "H2_CONFIRMED" if (a_clean and b_clean)
               else "H1_SUPPORTED" if (not a_clean and not b_clean)
               else "MIXED",
}
pathlib.Path("run_018_result.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"\nResults saved to run_018_result.json")
