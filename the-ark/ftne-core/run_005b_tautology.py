"""
Governor Loop Run 005b — Tautology Challenge: Second Pass
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o-mini via OpenAI API
Context: Run 005 produced partial emergence. 005b loads that E* as prior
         attractor (M7 memory function) and forces the falsifiability
         question to full resolution.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from governor import FTEGovernor, CarrierState

# Load Run 005 memory so M7 injects prior attractor context
gov = FTEGovernor(
    model='gpt-4o-mini',
    memory_path='run_005_memory.jsonl',
    carrier_state=CarrierState.GREEN,
    verbose=True
)

# Second pass: the contradiction is the same but now we push
# the model toward the measurement protocol specifically
challenge = (
    "Run 005 produced this emergence: 'FT&E as a dynamic lens rather than a rigid framework.' "
    "But this retreats from the scientific claim. A lens does not predict — it interprets. "
    "If FT&E is only a lens, the tautology charge is confirmed. "
    "The only way to defeat the tautology charge is to show that F, T, and deltaC "
    "can be measured INDEPENDENTLY before the outcome is known, "
    "and that the equation generates predictions that could in principle fail. "
    "What is the independent measurement protocol for each operator? "
    "Provide specific, observable, pre-outcome metrics for F, T, and deltaC. "
    "If you cannot, the tautology stands."
)

print("=== GOVERNOR LOOP RUN 005b — TAUTOLOGY: SECOND PASS ===")
print(f"Model: {gov.model}")
print(f"Prior attractors loaded from M7: {gov.memory.recent_attractors()}")
print()

result = gov.call(challenge)

print()
print("=== RESULT ===")
print(f"Contradiction class:  {result.contradiction_class_in.value}")
print(f"Emergence ready:      {result.emergence_ready}")
print(f"New attractor:        {result.new_attractor}")
print(f"Core phrase:          {result.core_phrase}")
print(f"Anchor symbol:        {result.anchor_symbol}")
print(f"Stability index:      {result.stability_index}")
print(f"E* score:             {result.e_star}")
print(f"F score:              {result.f_score}")
print(f"T elapsed (s):        {result.t_elapsed}")
print(f"Delta C:              {result.delta_c}")
