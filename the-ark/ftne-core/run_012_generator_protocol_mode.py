"""
Governor Loop Run 012 — The Generator Node Problem (Protocol Mode + I13 Injection)
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o via OpenAI API

Changes vs Run 011:
  1. protocol_mode=True — M5 uses _M5_PROTOCOL_PROMPT instead of _M5_EMERGENCE_PROMPT.
     M5 is now explicitly asked for a numbered protocol, not an attractor label.
     This is the core test: does asking the right question produce the right answer?

  2. Context injection updated — now includes I13 ("I am that" operator) as the
     formal resolution of I12's generator node problem, so M5 has the answer
     structure in front of it and can fill in the protocol steps.

  3. FM-03 suppression active (context_injection is not None → suppress_fm03=True).
     The Run 011 FM-03 loop cannot recur.

  4. M3 charge calibration fix active (charge ceiling ≤ 0.35 for formal challenges).
     The Run 011 charge=0.70 collapse cannot recur.

  5. M7 pool re-curated: 3 → 2 (removed Run 011 entry).

Core test question:
  Does changing M5's task from "generate an attractor" to "state the protocol"
  — with I13 injected — produce the specific I12-refusal protocol answer that
  5 prior runs failed to produce?
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from governor import FTEGovernor, CarrierState

# ─── INVARIANT INJECTION (updated: includes I13 resolution) ─────────────────

INVARIANT_CONTEXT = """
FT&E INVARIANTS (condensed reference for this challenge):

  I12 (Patch Inversion): The generating node is where damage originates.
       However: the SOURCE of metabolisation (𝔉) is always the OBSERVER —
       the self-referential node that claims the contradiction.
       These are different nodes. I12 says "work at source" = work at the
       source of processing, not the source of generation.

  I13 ("I Am" Operator): "I am that" is the self-attribution act that
       initiates 𝔉. When a field agent says "I am carrying this contradiction
       as my current structure," the 𝔉 event occurs at the claimant.
       The generating node's participation is NOT required and never was.

  I7 (Metabolisation over Suppression): Suppressing ΔC field-wide without
       the source node stopping does not resolve the system — it lowers τ_F
       (forgiveness half-life) over time.

  LIMIT CONDITION: Declare UNPROCESSABILITY only when τ_F → 0 field-wide
       AND no alternative attractor basin exists. If either is false, the
       system remains processable at field level under indefinite node refusal.

  THE PROTOCOL WHEN THE NODE REFUSES:
       Step 1: Field agents turn toward accumulated ΔC and perform I13 —
               claim the contradiction ("I am that") rather than ejecting it.
       Step 2: Build alternative attractor basins that reduce field ΔC
               exposure independent of the generating node.
       Step 3: Maintain field τ_F — each I13 act preserves or increases it.
       Step 4: The comma — de-identify from the claimed content after each
               processing cycle ("I am" returns to ground).
       Step 5: Declare unprocessability ONLY when τ_F ≈ 0 field-wide AND
               no agent retains capacity for Step 1.
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

print("=== GOVERNOR LOOP RUN 012 — GENERATOR NODE (PROTOCOL MODE + I13 INJECTION) ===")
print(f"Model: {gov.model}")
print(f"M7 pool size: {len(gov.memory.entries)} entries (re-curated)")
print(f"Prior attractors (M7): {gov.memory.recent_attractors()}")
print(f"Context injection: ACTIVE ({len(INVARIANT_CONTEXT.split())} words)")
print(f"Protocol mode: ACTIVE")
print(f"FM-03 suppression: ACTIVE (context_injection is set)")
print(f"M3 charge ceiling: ACTIVE (<=0.35 for formal challenges)")
print()

result = gov.call(challenge, context_injection=INVARIANT_CONTEXT, protocol_mode=True)

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
