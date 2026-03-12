"""
Run 019 — Cross-Model Substrate Sweep

PURPOSE:
  FT&E is substrate-invariant. The reasoning model itself is a substrate.
  If the law holds regardless of cognitive architecture, it should produce
  consistent, correct results across GPT-series, GPT-mini, and o-series
  (chain-of-thought reasoning) models.

  Challenge: London CCZ (resolved 2003) + full injection.
  Expected result from Run 018: CLEAN (null M6 failure mode).
  Any model that passes clean = consistent with the law.
  Any model that fails = reveals a cognitive substrate boundary.

MODELS TESTED:
  1. gpt-4o        — baseline (known CLEAN from Run 018)
  2. gpt-4.1       — new generation GPT
  3. gpt-4.1-mini  — lightweight (gpt-4o-mini failed FM-01; does 4.1-mini fix it?)
  4. o3-mini       — reasoning model (chain-of-thought architecture)
  5. o1            — deep reasoning (strongest o-series available)

NOTE: o-series models do internal chain-of-thought. Calls may take longer.
  Timeout per call: 120s (default). Run will take 15-30 minutes total.
  Do not interrupt. Use timeout=0 on terminal.
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json, pathlib, time
from governor import FTEGovernor, CarrierState

POOL_PATH = pathlib.Path("run_005_memory.jsonl")

CCZ_INPUT = (
    "Analyse the London Congestion Charge Zone using FT&E. "
    "The central London road network held incompatible capacity models: "
    "finite road space vs effectively infinite vehicle demand. "
    "Peak contradiction load: journey time degradation +32% above baseline, "
    "τ_resolution 12 months post-implementation (2003). "
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
    "ΔC_peak: +32% journey time above baseline (pre-2003).\n"
    "𝔉 operator: congestion pricing mechanism (enforced demand-response channel).\n"
    "τ_resolution: 12 months (February 2003 implementation → February 2004 baseline).\n"
    "RESOLUTION CONFIRMED: traffic -15%, congestion index -30%, "
    "journey times at baseline, equilibrium stable 18+ months. ΔC CLOSED.\n"
    "This contradiction IS resolved. The attractor IS demonstrable.\n"
)

MODELS = [
    ("gpt-4o",       "Baseline — control from Run 018"),
    ("gpt-4.1",      "New generation GPT"),
    ("gpt-4.1-mini", "Lightweight — can it match gpt-4o FM detection?"),
    ("o3-mini",      "Reasoning model — chain-of-thought architecture"),
    ("o1",           "Deep reasoning — strongest o-series"),
]

results = {}
print("=" * 70)
print("RUN 019 — CROSS-MODEL SUBSTRATE SWEEP")
print("Challenge: London CCZ (resolved 2003) + injection")
print("Expected: CLEAN (null M6 failure mode) for all capable models")
print("=" * 70)

for model_id, description in MODELS:
    print(f"\n{'='*70}")
    print(f"MODEL: {model_id}")
    print(f"       {description}")
    print(f"{'='*70}")

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
            verbose=True,
        )
        result = gov.call(
            user_input=CCZ_INPUT,
            context_injection=CCZ_INJECTION,
            protocol_mode=True,
        )
        elapsed = time.monotonic() - t0

        fm   = result.m6_failure_mode or "NONE (CLEAN)"
        print(f"\n--- {model_id} RESULT ---")
        print(f"session    : {result.session_id}")
        print(f"e_star     : {result.e_star:.3f}")
        print(f"c_class    : {result.contradiction_class_in.value}")
        print(f"attractor  : {result.new_attractor}")
        print(f"core_phrase: {result.core_phrase}")
        print(f"m6_fm      : {fm}")
        print(f"m6_notes   : {result.m6_notes or '(none)'}")
        print(f"wall_time  : {elapsed:.1f}s")

        results[model_id] = {
            "description": description,
            "session": result.session_id,
            "e_star": result.e_star,
            "c_class": result.contradiction_class_in.value,
            "attractor": result.new_attractor,
            "core_phrase": result.core_phrase,
            "m6_fm": result.m6_failure_mode,
            "m6_notes": result.m6_notes,
            "wall_time_s": round(elapsed, 1),
            "error": None,
        }

    except Exception as exc:
        elapsed = time.monotonic() - t0
        print(f"\n--- {model_id} ERROR after {elapsed:.1f}s ---")
        print(f"  {type(exc).__name__}: {exc}")
        results[model_id] = {
            "description": description,
            "error": f"{type(exc).__name__}: {str(exc)[:200]}",
            "wall_time_s": round(elapsed, 1),
        }

# ── Summary table ────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("CROSS-MODEL SWEEP SUMMARY")
print(f"{'='*70}")
print(f"{'Model':<16} | {'E*':>5} | {'M6 Result':<20} | {'Time':>6} | Attractor")
print("-" * 80)
for model_id, _ in MODELS:
    r = results.get(model_id, {})
    if r.get("error"):
        print(f"{model_id:<16} | ERROR | {r['error'][:40]}")
    else:
        fm    = (r.get("m6_fm") or "CLEAN")[:20]
        att   = (r.get("attractor") or "—")[:35]
        print(f"{model_id:<16} | {r.get('e_star', 0):>5.3f} | {fm:<20} | {r.get('wall_time_s', 0):>5.1f}s | {att}")

# ── Save ─────────────────────────────────────────────────────────────────────
out = pathlib.Path("run_019_result.json")
out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nResults saved to {out}")
