"""
Governor Loop Run 011 — The Generator Node Problem (gpt-4o + Invariant Injection)
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o via OpenAI API

Architectural changes active vs Run 010:
  1. Model upgraded: gpt-4o-mini → gpt-4o
     Test: does larger model produce protocol-level specificity without context?
  2. Context injection: compressed FT&E invariant set injected into M5 prompt
     Provides: I1-I12, field-level 𝔉 processing, limit conditions, τ_F concept
     Test: does invariant context allow model to answer the structural refusal
           problem the challenge explicitly requires?
  3. M7 pool re-curated: 4 → 2 (removed aborted-010-attempt and 010-corrected)
     Pool contains only 005b (E*=0.329) and 006-C3 (E*=0.594)
  4. Adversarial M6 remains active from governor.py (no change)

The core unsolved question from runs 007-010:
  The generator node challenge requires one of:
    A. An alternative processing route that bypasses the refusing node
    B. A clarification of whether 𝔉 requires node participation or only field-level
    C. A formal declaration of FT&E's unprocessability limit condition

  All prior runs produced generic "resilience/shared power" attractors.
  This run tests whether: (a) model scale, (b) injected invariant context,
  or (c) both together finally produce one of A, B, or C above.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from governor import FTEGovernor, CarrierState

# ─── COMPRESSED INVARIANT INJECTION ─────────────────────────────────────────
# Sourced from FT&E framework (memeories.txt, formal documents).
# Injected into M5 prompt as context for C2/C3 challenges.
# Length: ~180 tokens — deliberately kept under 200 to preserve M5 reasoning space.

INVARIANT_CONTEXT = """
FT&E INVARIANTS (condensed reference for this challenge):
  I12 (Patch Inversion): The generating node is the correct locus of metabolisation.
       However: 𝔉 (Forgiveness) is a FIELD property, not a node property.
       𝔉 can be processed by the surrounding field even when the generating node
       refuses — this is called distributed forgiveness processing.
  I7 (Metabolisation over Suppression): Suppressing ΔC (contradiction load) at the
       field level while the source node continues generating does not resolve the
       system — it lowers the field's τ_F (forgiveness half-life) over time.
  I5 (Field Primacy): Emergence is a field-level event. The generating node's
       refusal gates the field's emergence but does not prevent field-level 𝔉.
  LIMIT CONDITION (FT&E formal): A system is declared UNPROCESSABLE when:
       (a) τ_F → 0 across the majority of the field (field forgiveness-capacity collapse),
       AND (b) no alternative attractor basin exists to absorb ongoing ΔC generation.
       If either condition is false, the system remains processable at field level
       even under indefinite node refusal.
  PROTOCOL WHEN NODE REFUSES: The framework directs field-level agents to:
       (1) Maintain their own 𝔉 capacity (not collapse into mirror-opposition),
       (2) Build alternative attractor basins that reduce field ΔC exposure,
       (3) Declare the system conditionally unprocessable ONLY when τ_F ≈ 0 field-wide.
"""

gov = FTEGovernor(
    model='gpt-4o',
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

print("=== GOVERNOR LOOP RUN 011 — GENERATOR NODE (gpt-4o + INVARIANT INJECTION) ===")
print(f"Model: {gov.model}")
print(f"M7 pool size: {len(gov.memory.entries)} entries (re-curated)")
print(f"Prior attractors (M7): {gov.memory.recent_attractors()}")
print(f"Context injection: ACTIVE ({len(INVARIANT_CONTEXT.split())} words)")
print()

result = gov.call(challenge, context_injection=INVARIANT_CONTEXT)

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
