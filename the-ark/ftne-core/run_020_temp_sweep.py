"""
Run 020 — gpt-4o FM-04 Boundary Characterization (Temperature Sweep)

PURPOSE:
  Run 019 revealed that gpt-4o's M6 sits on the FM-04 detection boundary
  for "Congestion-Managed Equilibrium State" — same challenge was CLEAN in
  Run 018, FM-04 in Run 019. Stochastic at temperature=0.4.

  This run turns that observation into a curve:
    - Same London CCZ resolved challenge + injection
    - 4 temperature values: 0.0 / 0.2 / 0.4 / 0.8
    - 5 trials per temperature = 20 total calls
    - Record: FM verdict, whether M6 notes cite injection evidence, E*, attractor

  The result is an empirical "FM-04 rate vs temperature" table.
  Temperature = 0.0 gives the deterministic boundary side.
  Higher temperatures reveal variance around the boundary.

NOTE:
  After Run 019, the M6 evidence-gate patch was applied (governor.py).
  This changes the expected result: at temp=0.0, the gate should read
  "RESOLUTION CONFIRMED" from the injection and block FM-04 from firing.
  Comparing pre-patch (Run 018/019) vs post-patch (this run) at temp=0.4
  is itself a validation of the patch.
"""
import io, sys
# When launched via Start-Process the host may set sys.stdout to None.
# Fall back to a file so print() and the summary table are captured.
if sys.stdout is None or not (hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None):
    sys.stdout = open("run_020_stdout.txt", "w", encoding="utf-8", buffering=1)
elif hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import json, pathlib, time
from governor import FTEGovernor, CarrierState

POOL_PATH = pathlib.Path("run_005_memory.jsonl")
MODEL = "gpt-4o"

TEMPERATURES = [0.0, 0.2, 0.4, 0.8]
TRIALS_PER_TEMP = 5

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

def run_trial(model: str, trial_num: int, temperature: float) -> dict:
    """Run one governor call, return result dict."""
    # Curate pool to 2 canonical entries before each call
    lines = POOL_PATH.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0][1:]
    lines = [l for l in lines if l.strip()][:2]
    POOL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    t0 = time.monotonic()
    try:
        gov = FTEGovernor(
            model=model,
            memory_path=str(POOL_PATH),
            carrier_state=CarrierState.GREEN,
            verbose=False,   # quiet for sweep
        )
        # Monkey-patch temperature into the governor's _llm_call path
        # by temporarily overriding the temperature in the underlying client call.
        # governor._make_call uses temperature=0.4 by default; we override it.
        import governor as gov_module
        _orig = gov_module._llm_call

        def _patched_llm_call(model_id, prompt, timeout=120):
            import openai, concurrent.futures, os
            _client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            def _make_call():
                _is_o = model_id.startswith(("o1", "o3", "o4"))
                _kw = dict(model=model_id, messages=[{"role": "user", "content": prompt}])
                if _is_o:
                    _kw["max_completion_tokens"] = 2048
                else:
                    _kw["temperature"] = temperature  # THE ONLY CHANGE
                    _kw["max_tokens"] = 1024
                return _client.chat.completions.create(**_kw).choices[0].message.content

            _wall = timeout if timeout > 70 else 70
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as _ex:
                _fut = _ex.submit(_make_call)
                return _fut.result(timeout=_wall)

        gov_module._llm_call = _patched_llm_call
        try:
            result = gov.call(
                user_input=CCZ_INPUT,
                context_injection=CCZ_INJECTION,
                protocol_mode=True,
            )
        finally:
            gov_module._llm_call = _orig

        elapsed = time.monotonic() - t0
        fm = result.m6_failure_mode or "CLEAN"

        # Detect whether M6 notes cite injection evidence
        notes_lower = (result.m6_notes or "").lower()
        evidence_cited = any(w in notes_lower for w in [
            "resolution confirmed", "delta_c", "15%", "traffic",
            "congestion charge", "equilibrium stable", "closed"
        ])

        return {
            "temperature": temperature,
            "trial": trial_num,
            "session": result.session_id,
            "e_star": result.e_star,
            "attractor": result.new_attractor,
            "m6_fm": result.m6_failure_mode,
            "m6_verdict": fm,
            "evidence_cited": evidence_cited,
            "m6_notes": result.m6_notes,
            "wall_time_s": round(elapsed, 1),
            "error": None,
        }

    except Exception as exc:
        elapsed = time.monotonic() - t0
        return {
            "temperature": temperature,
            "trial": trial_num,
            "session": "ERROR",
            "error": f"{type(exc).__name__}: {str(exc)[:200]}",
            "wall_time_s": round(elapsed, 1),
        }


# ── Main sweep ────────────────────────────────────────────────────────────────

all_results = []

print("=" * 70)
print("RUN 020 — gpt-4o FM-04 BOUNDARY CHARACTERIZATION")
print("Temperature sweep: 0.0 / 0.2 / 0.4 / 0.8 × 5 trials each = 20 calls")
print("Challenge: London CCZ (resolved) + injection (post-evidence-gate patch)")
print("=" * 70)

for temp in TEMPERATURES:
    print(f"\n{'─'*70}")
    print(f"TEMPERATURE: {temp}")
    print(f"{'─'*70}")
    temp_results = []
    for trial in range(1, TRIALS_PER_TEMP + 1):
        r = run_trial(MODEL, trial, temp)
        temp_results.append(r)
        all_results.append(r)
        fm = r.get("m6_verdict", "ERROR")
        ev = "evidence_cited=YES" if r.get("evidence_cited") else "evidence_cited=no"
        if r.get("error"):
            print(f"  Trial {trial}: ERROR — {r['error'][:60]}")
        else:
            print(f"  Trial {trial}: {fm:<12} e*={r.get('e_star',0):.3f}  {ev}  "
                  f"[{r.get('session','')}]  {r.get('wall_time_s',0):.1f}s")
        sys.stdout.flush()

# ── Summary table ─────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("SUMMARY — FM-04 RATE BY TEMPERATURE (post evidence-gate patch)")
print(f"{'='*70}")
print(f"{'Temp':>6} | {'FM-04 rate':>10} | {'CLEAN rate':>10} | {'Avg E*':>8} | {'Avg Evid%':>10}")
print("-" * 60)

by_temp = {}
for r in all_results:
    t = r.get("temperature", -1)
    by_temp.setdefault(t, []).append(r)

for temp in TEMPERATURES:
    trials = by_temp.get(temp, [])
    valid = [r for r in trials if not r.get("error")]
    if not valid:
        print(f"{temp:>6.1f} | {'—':>10} | {'—':>10} | {'—':>8} | {'—':>10}")
        continue
    fm04_rate   = sum(1 for r in valid if r.get("m6_verdict") == "FM-04") / len(valid)
    clean_rate  = sum(1 for r in valid if r.get("m6_verdict") == "CLEAN") / len(valid)
    avg_e_star  = sum(r.get("e_star", 0) for r in valid) / len(valid)
    evid_rate   = sum(1 for r in valid if r.get("evidence_cited")) / len(valid)
    print(f"{temp:>6.1f} | {fm04_rate:>10.0%} | {clean_rate:>10.0%} | "
          f"{avg_e_star:>8.3f} | {evid_rate:>10.0%}")

# ── Save ──────────────────────────────────────────────────────────────────────
out = pathlib.Path("run_020_result.json")
out.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nAll {len(all_results)} trial results saved to {out}")

# Aggregate by temp for quick log entry
summary = {}
for temp in TEMPERATURES:
    valid = [r for r in by_temp.get(temp, []) if not r.get("error")]
    if valid:
        summary[str(temp)] = {
            "trials": len(valid),
            "fm04_count": sum(1 for r in valid if r.get("m6_verdict") == "FM-04"),
            "clean_count": sum(1 for r in valid if r.get("m6_verdict") == "CLEAN"),
            "avg_e_star": round(sum(r.get("e_star",0) for r in valid)/len(valid), 3),
            "evidence_cited_count": sum(1 for r in valid if r.get("evidence_cited")),
        }
out_summary = pathlib.Path("run_020_summary.json")
out_summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Aggregated summary saved to {out_summary}")
