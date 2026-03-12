"""
Governor Loop Run 006 — The Scale Paradox
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o-mini via OpenAI API

Contradiction: FT&E claims scale invariance (I15) but the governor is
radically local (CPU, single node, 3B model). How does a locally-validated
system scale without violating I5 (Localise then Generalise)?
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from governor import FTEGovernor, CarrierState

# Load full memory — 005 and 005b attractors available to M7
gov = FTEGovernor(
    model='gpt-4o-mini',
    memory_path='run_005_memory.jsonl',
    carrier_state=CarrierState.GREEN,
    verbose=True
)

challenge = (
    "FT&E Invariant I15 states the sequence E* = F * T - deltaC is scale invariant: "
    "it operates the same way in a personal insight, a family conflict, a national "
    "reconciliation, and an AI system. "
    "But Invariant I5 states: Localise then Generalise. A sequence must be validated "
    "locally before being claimed universally. "
    "The FT&E governor currently runs on a single CPU, a 3B parameter model, "
    "one user, one conversation at a time. "
    "Here is the contradiction: if I15 is true, the sequence should already work "
    "at civilisational scale. But if I5 is true, we cannot claim I15 until local "
    "validation is complete. These two invariants are in direct conflict. "
    "A framework that claims scale invariance before completing local validation "
    "is making a universal claim on local evidence. "
    "How does FT&E resolve this without either abandoning I15 or violating I5?"
)

print("=== GOVERNOR LOOP RUN 006 — THE SCALE PARADOX ===")
print(f"Model: {gov.model}")
print(f"Prior attractors (M7): {gov.memory.recent_attractors()}")
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
print(f"Failure mode:         {getattr(result, 'failure_mode', 'none')}")
