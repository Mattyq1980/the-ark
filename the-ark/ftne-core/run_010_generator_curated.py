"""
Governor Loop Run 010 — The Generator Node Problem (Curated Pool + Adversarial M6)
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o-mini via OpenAI API

Re-run of Run 009 with two architectural changes active:
  1. M7 pool curated: 8 entries → 2 entries. Removed generic
     "resilience/innovation" attractors from runs 007–009. Retained only:
       — 005b: "independently assessing forgiveness, time, and contradiction
                load" (E*=0.329, compass/fog anchor)
       — 006:  "iterative refinement of local insights into adaptable universal
                truths" (E*=0.594, Spiral anchor, C3_FOUNDATIONAL)
  2. FM-01 adversarial M6 fix active: second M6 call in clean context window
     receives ONLY the raw challenge + proposed attractor (not M5 context).
     Tests genericity by substitutability: would the attractor fit any topic?

Test question: does a clean M7 pool with two strong attractors allow M5 to
produce something more specific to the generator node problem than Run 009's
generic "resilience and innovation" deflection?
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

print("=== GOVERNOR LOOP RUN 010 — GENERATOR NODE (CURATED POOL + ADV M6) ===")
print(f"Model: {gov.model}")
print(f"M7 pool size: {len(gov.memory.entries)} entries (curated from 8)")
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
