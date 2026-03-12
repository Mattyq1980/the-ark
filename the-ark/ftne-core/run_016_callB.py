"""Run 016 Call B: Physical challenge WITH injection."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pathlib
from governor import FTEGovernor, CarrierState

POOL_PATH = pathlib.Path("run_005_memory.jsonl")
lines = POOL_PATH.read_text(encoding="utf-8").splitlines()
if lines and lines[0].startswith("\ufeff"): lines[0] = lines[0][1:]
lines = [l for l in lines if l.strip()][:2]
POOL_PATH.write_text("\n".join(lines)+"\n", encoding="utf-8")

gov = FTEGovernor(model='gpt-4o', memory_path=str(POOL_PATH),
                  carrier_state=CarrierState.GREEN, verbose=True)
result = gov.call(
    user_input=(
        "Analyse the AEP winter polar vortex grid contradiction using FT&E. "
        "The system held incompatible capacity models across seasons "
        "(ΔC_winter +2400 MWh, τ_recovery 11 days). "
        "What does the forgiveness engine reveal at the structural level?"
    ),
    context_injection=(
        "\n[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]\n"
        "FT&E describes a universal structural law. Use substrate vocabulary.\n"
        "For physical domains: load, capacity, decay rate, attractor state.\n\n"
        "[CASE RECORD: E-AEP POWER GRID — WINTER POLAR VORTEX EVENT]\n"
        "Domain: electrical infrastructure. "
        "Contradiction: WINTER DEMAND vs SUMMER BASELINE.\n"
        "ΔC_winter +2400 MWh above committed capacity. τ_recovery 11 days.\n"
    ),
    protocol_mode=True,
)
print("=CALL_B_RESULT=")
print(f"session={result.session_id}")
print(f"e_star={result.e_star:.3f}")
print(f"c_class={result.contradiction_class_in.value}")
print(f"attractor={result.new_attractor}")
print(f"m6_fm={result.m6_failure_mode or 'NONE'}")
print(f"m6_notes={result.m6_notes or '(none)'}")

import json
pathlib.Path("run_016_callB_result.json").write_text(json.dumps({
    "session": result.session_id,
    "e_star": result.e_star,
    "c_class": result.contradiction_class_in.value,
    "attractor": result.new_attractor,
    "m6_fm": result.m6_failure_mode,
    "m6_notes": result.m6_notes,
}), encoding="utf-8")
