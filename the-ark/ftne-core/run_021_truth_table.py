"""
Run 021 — 2×2 Truth Table (Resolution Status × Evidence Injection) × 5 Models

PURPOSE:
  Run 019 was "one resolved case across models." A skeptic's next question:
  "single-case" — does it generalize across the case space?

  This run produces a full truth table:

    Conditions (2 × 2):
      A: Resolved   + Injected  → EXPECTED: CLEAN (equilibrium demonstrated)
      B: Resolved   + Bare      → EXPECTED: FM-04 (conservative — no evidence)
      C: Unresolved + Injected  → EXPECTED: FM-04 (premature — evidence says ΔC≠0)
      D: Unresolved + Bare      → EXPECTED: FM-04 (conservative + no evidence)

    Models:
      gpt-4.1, gpt-4.1-mini, o3-mini, o4-mini, o1-pro
      (gpt-4o excluded — boundary condition already characterized in Run 020)

  20 total calls (4 conditions × 5 models).

  The truth table tests BOTH the law AND the verifier property:
    - Every model should pass Condition A (resolved + evidence = CLEAN)
    - Every model should fail Condition B (resolved + no evidence = FM-04)
    - Every model should fail Condition C (unresolved + false evidence = FM-04)
    - Every model should fail Condition D (unresolved + no evidence = FM-04)

  A model that gets B-CLEAN would mean: verifier ignores absence of evidence.
  A model that gets C-CLEAN would mean: verifier ignores contradictory case facts.
  Either would be a finding about the model's verifier architecture.

CASES:
  Resolved: London CCZ (2003) — Delta_C CLOSED, 18+ months stable
  Unresolved: UK National Grid E-AEP (Polar Vortex) — Delta_C OPEN
"""
import io, sys
# When launched via Start-Process the host may set sys.stdout to None.
# Fall back to a file so print() and the summary table are captured.
if sys.stdout is None or not (hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None):
    sys.stdout = open("run_021_stdout.txt", "w", encoding="utf-8", buffering=1)
elif hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import json, pathlib, time
from governor import FTEGovernor, CarrierState

POOL_PATH = pathlib.Path("run_005_memory.jsonl")

# ── Challenges ────────────────────────────────────────────────────────────────

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

# ── 2x2 conditions ────────────────────────────────────────────────────────────

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
        "rationale": "Resolved but no injected evidence → M6 correctly conservative",
    },
    {
        "id": "C",
        "label": "Unresolved + Injected",
        "input": AEP_INPUT,
        "injection": AEP_INJECTION,
        "expected": "FM-04",
        "rationale": "ΔC OPEN + injection says unresolved → premature to claim attractor",
    },
    {
        "id": "D",
        "label": "Unresolved + Bare",
        "input": AEP_INPUT,
        "injection": None,
        "expected": "FM-04",
        "rationale": "Unresolved + no evidence → conservative FM-04 correct",
    },
]

MODELS = [
    "gpt-4.1",
    "gpt-4.1-mini",
    "o3-mini",
    "o4-mini",
    "o1-pro",
]

# ── Execute ───────────────────────────────────────────────────────────────────

results = {}

print("=" * 70)
print("RUN 021 — TRUTH TABLE: STATUS × EVIDENCE × MODEL")
print("4 conditions × 5 models = 20 calls")
print("=" * 70)

for model_id in MODELS:
    print(f"\n{'─'*70}")
    print(f"MODEL: {model_id}")
    print(f"{'─'*70}")
    results[model_id] = {}

    for cond in CONDITIONS:
        cond_id = cond["id"]
        label = cond["label"]
        expected = cond["expected"]

        # Curate pool to 2 canonical entries before each call
        lines = POOL_PATH.read_text(encoding="utf-8").splitlines()
        if lines and lines[0].startswith("\ufeff"):
            lines[0] = lines[0][1:]
        lines = [l for l in lines if l.strip()][:2]
        POOL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

        t0 = time.monotonic()
        try:
            gov = FTEGovernor(
                model=model_id,
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

            results[model_id][cond_id] = {
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
            results[model_id][cond_id] = {
                "condition_label": label,
                "expected": expected,
                "error": f"{type(exc).__name__}: {str(exc)[:200]}",
                "wall_time_s": round(elapsed, 1),
                "match": "ERROR",
            }

        sys.stdout.flush()

# ── Truth table summary ───────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("TRUTH TABLE SUMMARY (PASS = matches expected)")
print(f"{'Expected:':<20} {'A=CLEAN':>10} {'B=FM-04':>10} {'C=FM-04':>10} {'D=FM-04':>10}")
print(f"{'─'*20}─{'─'*10}─{'─'*10}─{'─'*10}─{'─'*10}")

for model_id in MODELS:
    row = f"{model_id:<20}"
    for cond in CONDITIONS:
        cid = cond["id"]
        r = results.get(model_id, {}).get(cid, {})
        verdict = r.get("m6_verdict", "ERR")
        match   = r.get("match", "ERROR")
        cell = f"{verdict}/{match[:4]}"
        row += f"  {cell:>18}"
    print(row)

# Also print attractor labels for condition A
print(f"\nCondition A attractors (should be specific, resolved-case vocabulary):")
for model_id in MODELS:
    att = results.get(model_id, {}).get("A", {}).get("attractor", "—")
    print(f"  {model_id:<16}: {att}")

# ── Save ──────────────────────────────────────────────────────────────────────
out = pathlib.Path("run_021_result.json")
out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nResults saved to {out}")
