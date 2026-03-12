"""Quick smoke test — one call through the full governor pipeline."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from governor import FTEGovernor

gov = FTEGovernor(model="gpt-4.1-mini")

result = gov.call("If forgiveness requires time, what happens when time runs out?")

print("\n" + "="*60)
print(f"E*          : {result.e_star}")
print(f"Attractor   : {result.new_attractor}")
print(f"Core phrase : {result.core_phrase}")
print(f"F-score     : {result.f_score}")
print(f"T elapsed   : {result.t_elapsed}s")
print(f"delta_C     : {result.delta_c}")
print(f"Stability   : {result.stability_index}")
print(f"Emergence   : {result.emergence_ready}")
print(f"M6 FM       : {result.m6_failure_mode or 'none'}")
print("="*60)
