"""
Run 017 — M5 Physical Domain Mode Validation

Tests whether the new _M5_PROTOCOL_PHYSICAL_PROMPT eliminates FM-02/FM-04
on physical domain challenges. Two calls:

  Call A: physical + injection (previously FM-04 in Run 016 Call B)
  Call B: physical, bare no injection (previously FM-02 in Run 016 Call A)

Expected outcome: Both calls return M6 null (no failure mode).
Attractor should be a STABLE STATE descriptor, not a protocol/procedure name.
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

AEP_INPUT = (
    "Analyse the AEP winter polar vortex grid contradiction using FT&E. "
    "The system held incompatible capacity models across seasons "
    "(ΔC_winter +2400 MWh, τ_recovery 11 days). "
    "What does the forgiveness engine reveal at the structural level?"
)

AEP_INJECTION = (
    "\n[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]\n"
    "FT&E describes a universal structural law. Use substrate vocabulary.\n"
    "For physical domains: load, capacity, decay rate, attractor state.\n\n"
    "[CASE RECORD: E-AEP POWER GRID — WINTER POLAR VORTEX EVENT]\n"
    "Domain: electrical infrastructure. "
    "Contradiction: WINTER DEMAND vs SUMMER BASELINE.\n"
    "ΔC_winter +2400 MWh above committed capacity. τ_recovery 11 days.\n"
)

results = {}

# ── Call A: Physical + injection ─────────────────────────────────────────────
print("\n" + "="*60)
print("CALL A: Physical + injection (prev. FM-04 in Run 016 Call B)")
print("="*60)

gov_a = FTEGovernor(
    model="gpt-4o",
    memory_path=str(POOL_PATH),
    carrier_state=CarrierState.GREEN,
    verbose=True,
)
result_a = gov_a.call(
    user_input=AEP_INPUT,
    context_injection=AEP_INJECTION,
    protocol_mode=True,
)

print(f"\n--- CALL A RESULT ---")
print(f"session   : {result_a.session_id}")
print(f"e_star    : {result_a.e_star:.3f}")
print(f"c_class   : {result_a.contradiction_class_in.value}")
print(f"attractor : {result_a.new_attractor}")
print(f"core_phrase: {result_a.core_phrase}")
print(f"m6_fm     : {result_a.m6_failure_mode or 'NONE (CLEAN)'}")
print(f"m6_notes  : {result_a.m6_notes or '(none)'}")

results["call_a"] = {
    "session": result_a.session_id,
    "e_star": result_a.e_star,
    "c_class": result_a.contradiction_class_in.value,
    "attractor": result_a.new_attractor,
    "core_phrase": result_a.core_phrase,
    "m6_fm": result_a.m6_failure_mode,
    "m6_notes": result_a.m6_notes,
}

# ── Call B: Physical, no injection ───────────────────────────────────────────
print("\n" + "="*60)
print("CALL B: Physical bare — no injection (prev. FM-02 in Run 016 Call A)")
print("="*60)

gov_b = FTEGovernor(
    model="gpt-4o",
    memory_path=str(POOL_PATH),
    carrier_state=CarrierState.GREEN,
    verbose=True,
)
result_b = gov_b.call(
    user_input=AEP_INPUT,
    context_injection=None,
    protocol_mode=True,
)

print(f"\n--- CALL B RESULT ---")
print(f"session   : {result_b.session_id}")
print(f"e_star    : {result_b.e_star:.3f}")
print(f"c_class   : {result_b.contradiction_class_in.value}")
print(f"attractor : {result_b.new_attractor}")
print(f"core_phrase: {result_b.core_phrase}")
print(f"m6_fm     : {result_b.m6_failure_mode or 'NONE (CLEAN)'}")
print(f"m6_notes  : {result_b.m6_notes or '(none)'}")

results["call_b"] = {
    "session": result_b.session_id,
    "e_star": result_b.e_star,
    "c_class": result_b.contradiction_class_in.value,
    "attractor": result_b.new_attractor,
    "core_phrase": result_b.core_phrase,
    "m6_fm": result_b.m6_failure_mode,
    "m6_notes": result_b.m6_notes,
}

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("RUN 017 SUMMARY")
print("="*60)
for label, r in [("Call A (physical + injection)", results["call_a"]),
                 ("Call B (physical, bare)       ", results["call_b"])]:
    fm = r["m6_fm"] or "null (CLEAN)"
    print(f"{label} | E*={r['e_star']:.3f} | M6={fm}")
    print(f"  attractor: {r['attractor']}")

# ── Save results ─────────────────────────────────────────────────────────────
out_path = pathlib.Path("run_017_result.json")
out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nResults saved to {out_path}")
