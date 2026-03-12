"""
Governor Loop Run 008 — The Measurement Instruments
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o-mini via OpenAI API

Run 007 deflected — produced a characterisation, not a measurement
instrument. This run provides draft instruments and forces the
governor to evaluate, correct, or falsify each one.
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
    "The tautology challenge requires pre-outcome measurement of F, T, and deltaC. "
    "Run 007 produced a characterisation instead of a measurement protocol. "
    "Here are three draft measurement instruments. Evaluate each one: "
    "accept, refine, or falsify it. Give a specific reason for each verdict. "
    ""
    "DRAFT INSTRUMENT 1 — F (Forgiveness Capacity): "
    "Score = the proportion of contradiction events in the current session "
    "that were acknowledged and processed without dismissal, humiliation, or "
    "deflection. Scored from session transcript prior to E* formation. "
    "Range 0.0–1.0. Observable by an external coder with no knowledge of "
    "whether E* will form. "
    ""
    "DRAFT INSTRUMENT 2 — T (Time): "
    "Clock time in seconds from M2 signal classification to M5 emergence "
    "decision. Already implemented in the governor. The governor's own "
    "t_elapsed field is this measurement. No subjectivity. No assumption "
    "of E* formation. "
    ""
    "DRAFT INSTRUMENT 3 — deltaC (Contradiction Load): "
    "Stack count = the number of distinct M2-classified contradictions that "
    "are active (classified but not yet resolved by M7 write) at the moment "
    "processing begins. Each contradiction is a discrete, countable unit. "
    "An external observer can count the open M2 signals in the governor log "
    "before any M5 or M7 runs. "
    ""
    "FALSIFICATION CONDITION: "
    "If the equation E* = F * T_normalised - deltaC_normalised predicts E* > 0 "
    "using the three measurements above, but M5 returns emergence_ready=False, "
    "then the equation is falsified for that instance. "
    "This can happen. If F is high (0.8), T is adequate (20s), deltaC is low "
    "(0.3), the equation predicts E* = 0.86 — but if M5 fails to form an "
    "attractor, we have a counterexample. "
    ""
    "Evaluate all three instruments and the falsification condition. "
    "For any instrument you accept: confirm it satisfies the pre-outcome, "
    "observer-independence criteria. "
    "For any you reject: state the specific failure of independence or "
    "pre-outcome status. "
    "Do not produce a general characterisation. Engage with each instrument."
)

print("=== GOVERNOR LOOP RUN 008 — THE MEASUREMENT INSTRUMENTS ===")
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
