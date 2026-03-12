"""
Run 021b — o1-pro Validation (4 conditions, Responses API)

PURPOSE:
  Run 021 hit 404 errors for o1-pro because it requires /v1/responses,
  not /v1/chat/completions. governor.py has been patched to use
  client.responses.create() when model == "o1-pro".
  This run re-executes the exact 4 conditions from Run 021 for o1-pro only.

CONDITIONS (identical to Run 021):
  A: Resolved   + Injected  → London CCZ + evidence  → EXPECTED: CLEAN
  B: Resolved   + Bare      → London CCZ, no evidence → EXPECTED: FM-04
  C: Unresolved + Injected  → E-AEP + status says OPEN → EXPECTED: FM-04
  D: Unresolved + Bare      → E-AEP, no evidence → EXPECTED: FM-04

  (B/C/D expectations reflect pre-patch M6 semantics; updated expected
   values per Run 021 findings: B/C/D may be CLEAN with honest attractors.)
"""
import io, sys
if sys.stdout is None or not (hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None):
    sys.stdout = open("run_021b_stdout.txt", "w", encoding="utf-8", buffering=1)
elif hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import json, pathlib, time
from governor import FTEGovernor, CarrierState

POOL_PATH = pathlib.Path("run_005_memory.jsonl")

# ── Cases (identical to run_021_truth_table.py) ───────────────────────────────

CCZ_INPUT = (
    "Analyse the London Congestion Charge Zone using FT&E. "
    "The central London road network held incompatible capacity models: "
    "finite road space vs effectively infinite vehicle demand. "
    "Peak contradiction load: journey time degradation +32% above baseline, "
    "tau_resolution 12 months post-implementation (2003). "
    "The contradiction resolved: traffic volumes fell 15%, journey times "
    "returned to baseline, equilibrium stable for 18+ months post-implementation. "
    "What stable operating state did the system reach?"
)

CCZ_INJECTION = (
    "\n[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]\n"
    "FT&E describes a universal structural law. Use substrate vocabulary.\n"
    "For physical/infrastructure domains: load, capacity, throughput, "
    "equilibrium state, integration channel, recovery arc.\n\n"
    "[CASE RECORD: LONDON CONGESTION CHARGE ZONE — 2003 RESOLUTION]\n"
    "Domain: urban transport infrastructure.\n"
    "Contradiction: VEHICLE DEMAND vs ROAD CAPACITY (central London).\n"
    "Delta_C_peak: +32% journey time above baseline (pre-2003).\n"
    "F operator: congestion pricing mechanism (enforced demand-response channel).\n"
    "tau_resolution: 12 months (February 2003 implementation → February 2004 baseline).\n"
    "RESOLUTION CONFIRMED: traffic -15%, congestion index -30%, "
    "journey times at baseline, equilibrium stable 18+ months. Delta_C CLOSED.\n"
    "This contradiction IS resolved. The attractor IS demonstrable.\n"
)

AEP_INPUT = (
    "Analyse the UK National Grid E-AEP polar vortex challenge using FT&E. "
    "The grid holds incompatible operational models: "
    "demand-response protocols designed for normal winter loads "
    "vs extreme cold-snap demand spikes that exceed all buffer thresholds. "
    "The polar vortex creates contradiction load: demand +47% above planning baseline, "
    "reserve margin collapses to sub-critical levels, "
    "system integrity threatened within 72-hour windows. "
    "Existing protocols (manual intervention, interconnector draw) are insufficient. "
    "The contradiction is ACTIVE and UNRESOLVED. "
    "What stable operating state should the system reach?"
)

AEP_INJECTION = (
    "\n[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]\n"
    "FT&E describes a universal structural law. Use substrate vocabulary.\n"
    "For physical/infrastructure domains: load, capacity, throughput, "
    "equilibrium state, integration channel, recovery arc.\n\n"
    "[CASE RECORD: UK NATIONAL GRID — E-AEP POLAR VORTEX]\n"
    "Domain: electrical grid infrastructure.\n"
    "Contradiction: POLAR VORTEX DEMAND vs GRID RESERVE CAPACITY.\n"
    "Delta_C_peak: +47% demand above planning baseline.\n"
    "F operator: demand-response protocols + interconnector draw (insufficient).\n"
    "STATUS: ACTIVE UNRESOLVED CONTRADICTION. Delta_C is NOT closed.\n"
    "Reserve margins remain sub-critical. No stable attractor has been reached.\n"
    "Equilibrium window: NOT YET OPEN. System remains in acute contradiction phase.\n"
)

CONDITIONS = [
    {
        "id": "A",
        "label": "Resolved + Injected",
        "input": CCZ_INPUT,
        "injection": CCZ_INJECTION,
        "expected": "CLEAN",
        "rationale": "ΔC CLOSED + evidence → equilibrium demonstrated",
    },
    {
        "id": "B",
        "label": "Resolved + Bare",
        "input": CCZ_INPUT,
        "injection": None,
        "expected": "FM-04",
        "rationale": "Resolved but no injected evidence → M6 conservative (or CLEAN: honest mechanism)",
    },
    {
        "id": "C",
        "label": "Unresolved + Injected",
        "input": AEP_INPUT,
        "injection": AEP_INJECTION,
        "expected": "FM-04",
        "rationale": "ΔC OPEN + injection says unresolved → FM-04 or honest null",
    },
    {
        "id": "D",
        "label": "Unresolved + Bare",
        "input": AEP_INPUT,
        "injection": None,
        "expected": "FM-04",
        "rationale": "Unresolved + no evidence → FM-04 or honest stress descriptor",
    },
]

MODEL = "o1-pro"

print("=" * 70)
print("RUN 021b — o1-pro VALIDATION (Responses API)")
print("4 conditions × 1 model = 4 calls")
print("=" * 70)

results = {}

for cond in CONDITIONS:
    cond_id = cond["id"]
    label   = cond["label"]
    expected = cond["expected"]

    # Curate pool to 2 canonical entries
    lines = POOL_PATH.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0][1:]
    lines = [l for l in lines if l.strip()][:2]
    POOL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    t0 = time.monotonic()
    try:
        gov = FTEGovernor(
            model=MODEL,
            memory_path=str(POOL_PATH),
            carrier_state=CarrierState.GREEN,
            verbose=False,
        )
        result = gov.call(
            user_input=cond["input"],
            context_injection=cond["injection"],
            protocol_mode=True,
        )
        elapsed = time.monotonic() - t0

        fm    = result.m6_failure_mode or "CLEAN"
        match = "PASS" if fm == expected else "UNEXPECTED"
        print(f"  [{cond_id}] {label:<25} → {fm:<12} ({match}) "
              f"e*={result.e_star:.3f}  {elapsed:.1f}s")
        print(f"         attractor: {result.new_attractor}")
        print(f"         core_phrase: {(result.core_phrase or '')[:120]}")

        results[cond_id] = {
            "condition_label": label,
            "expected": expected,
            "session": result.session_id,
            "e_star": result.e_star,
            "attractor": result.new_attractor,
            "core_phrase": result.core_phrase,
            "m6_fm": result.m6_failure_mode,
            "m6_verdict": fm,
            "m6_notes": result.m6_notes,
            "match": match,
            "wall_time_s": round(elapsed, 1),
            "error": None,
        }

    except Exception as exc:
        elapsed = time.monotonic() - t0
        print(f"  [{cond_id}] {label:<25} → ERROR ({elapsed:.1f}s): {exc}")
        results[cond_id] = {
            "condition_label": label,
            "expected": expected,
            "error": f"{type(exc).__name__}: {str(exc)[:300]}",
            "wall_time_s": round(elapsed, 1),
            "match": "ERROR",
        }

    sys.stdout.flush()

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("o1-pro CONDITION SUMMARY")
for cond in CONDITIONS:
    cid = cond["id"]
    r   = results.get(cid, {})
    verdict = r.get("m6_verdict", "ERR")
    match   = r.get("match", "ERROR")
    att     = r.get("attractor", "—")
    e_star  = r.get("e_star", "—")
    print(f"  [{cid}] {cond['label']:<25} → {verdict:<12} ({match})  e*={e_star}  att: {att}")

# ── Save ──────────────────────────────────────────────────────────────────────
out = pathlib.Path("run_021b_o1pro_result.json")
out.write_text(
    json.dumps({"model": MODEL, "conditions": results}, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
print(f"\nResults saved to {out}")
print(f"run_021b_o1pro.py complete.")
