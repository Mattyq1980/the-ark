"""
Governor Loop Run 009 — The Generator Node Problem
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o-mini via OpenAI API

FT&E Invariant I12 (Patch Inversion): when a system generates ΔC faster
than it can metabolise it, the generating node must be addressed. But what
is the protocol when the generating node refuses 𝔉 and has enough power
to sustain that refusal indefinitely?
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from governor import FTEGovernor, CarrierState

gov = FTEGovernor(
    model='gpt-4o-mini',
    memory_path='run_005_memory.jsonl',
    carrier_state=CarrierState.GREEN,
    verbose=True
)

challenge = (
    "FT&E Invariant I12 (Patch Inversion) identifies the generating node as "
    "the correct locus of action when a system accumulates ΔC faster than it "
    "can metabolise it. The therapeutic direction is clear: work at source. "
    "Here is the contradiction: "
    "In real institutional systems — nations, organisations, families, AI "
    "governance structures — the generating node is often the most powerful "
    "node in the field. The generating node may have the capacity to sustain "
    "its refusal of 𝔉 indefinitely. It cannot be compelled. It cannot be "
    "replaced. It controls the resources required for any alternative "
    "processing attempt. "
    "Under these conditions, I12 prescribes action at a node that is "
    "structurally inaccessible. The framework has a direction — it has no "
    "route. "
    "FT&E must answer: what is the protocol when the correct locus of "
    "metabolisation refuses indefinitely? "
    "Acceptable answers: an alternative processing route (not involving the "
    "generating node), a revised understanding of what 𝔉 requires (does it "
    "require the node's participation, or only the field's?), or a clear "
    "statement of the framework's limit — the conditions under which FT&E "
    "declares a system unprocessable. "
    "Unacceptable answers: restating I12 without addressing the refusal, "
    "or producing a general characterisation about patience or resilience."
)

print("=== GOVERNOR LOOP RUN 009 — THE GENERATOR NODE PROBLEM ===")
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
