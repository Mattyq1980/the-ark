"""Run 016 Call C: Psychological baseline WITH injection (control)."""
import io, sys, json, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
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
        "A person has spent 15 years in a career that gave them financial security "
        "but steadily eroded their sense of meaning. They now face a choice: "
        "stay (security, no meaning) or leave (meaning, no security). "
        "Every time they start to move, fear of collapse pulls them back. "
        "Apply FT&E: what is the contradiction and what does genuine emergence look like?"
    ),
    context_injection=(
        "\n[CLAIM DIRECTION: SUBSTRATE-INVARIANT LAW]\n"
        "FT&E describes a universal structural law. Use substrate vocabulary of the domain.\n"
        "For psychological domains: emotional vocabulary appropriate.\n"
        "ΔC = accumulated identity tension (15 years).\n"
        "𝔉 = capacity to hold safety-need AND meaning-need without collapsing either.\n"
    ),
    protocol_mode=True,
)
print("=CALL_C_RESULT=")
print(f"session={result.session_id}")
print(f"e_star={result.e_star:.3f}")
print(f"c_class={result.contradiction_class_in.value}")
print(f"attractor={result.new_attractor}")
print(f"m6_fm={result.m6_failure_mode or 'NONE'}")
print(f"m6_notes={result.m6_notes or '(none)'}")

pathlib.Path("run_016_callC_result.json").write_text(json.dumps({
    "session": result.session_id,
    "e_star": result.e_star,
    "c_class": result.contradiction_class_in.value,
    "attractor": result.new_attractor,
    "m6_fm": result.m6_failure_mode,
    "m6_notes": result.m6_notes,
}), encoding="utf-8")
