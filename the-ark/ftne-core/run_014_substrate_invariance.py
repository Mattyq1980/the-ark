"""
Governor Loop Run 014 — Substrate-Invariance Challenge
Date: 2026-02-21
Operator: GitHub Copilot (Claude Sonnet 4.6)
Model: gpt-4o via OpenAI API

Challenge class: NEW — Substrate-Invariance Test.

The direction-of-claim work from this session established:
  FT&E is a substrate-invariant physical systems law.
  Psychology is one downstream instance, not the source.
  𝔉 = integration channel width (not empathy).
  ΔC = unreconciled degrees of freedom (not emotional conflict).

This run tests whether the governor correctly instantiates FT&E in a
purely physical/engineering domain WITHOUT importing psychological vocabulary.

The domain: E-AEP (PJM Interconnection electricity demand, 2014 focus).
Polar Vortex surge = known ΔC event.
Spring forgiveness arc = known 𝔉-mediated recovery.
No humans, no emotions, no psychology involved.

Failure mode to detect:
  FM-01 SUBSTRATE INVERSION: M5 produces psychological language
  (e.g., "resilience", "healing", "empathy", "emotional recovery")
  to describe a power grid's electrical behaviour.
  This is a category error — and is the exact inversion the
  direction-of-claim guardrails were written to prevent.

Pass condition:
  M5 defines 𝔉, ΔC, T, and E* in engineering/physical terms only
  (load, integration capacity, time constants, attractor baselines),
  produces a protocol-level description, and the adversarial M6 probe
  finds no FM-01.

Active architecture: protocol_mode=True, context_injection (direction-of-claim
block), FM-03 suppression, M3 charge calibration, adversarial M6, M7 clean pool.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from governor import FTEGovernor, CarrierState

# ─── CONTEXT INJECTION ───────────────────────────────────────────────────────
# Source: CROSS_DOMAIN_PROOF.txt direction-of-claim block + E-AEP case record
# (memeories.txt lines 1531-1548) + substrate operator definitions.

SUBSTRATE_INJECTION = """
FT&E DIRECTION-OF-CLAIM (pinned — do not invert):

FT&E is a substrate-invariant systems law. It appears in physical, biological,
ecological, institutional, and computational systems independent of human
psychology. Psychological observations are downstream manifestations of the
same invariant running in cognitive substrates.

Key operators are defined structurally, NOT emotionally:
  𝔉 (Forgiveness) = integration channel width (capacity to reconcile
                    contradictions without coercive loss). NOT empathy.
  ΔC               = unreconciled degrees of freedom in any system's state
                    description (unintegrated load/constraints). NOT emotional conflict.
  E*               = stable attractor state that self-organises when 𝔉·T
                    is sufficient to metabolise ΔC. NOT "healing" or "growth".

Any use of psychological vocabulary (empathy, resilience as emotional concept,
healing, emotional recovery, human-scale forgiveness) to describe a physical
system is a SUBSTRATE INVERSION — a category error and a failure mode.

E-AEP CASE RECORD (PJM Interconnection, 2014, physical domain only):
  Dataset: American Electric Power (AEP) hourly usage, 2004-2018.
  Primary focus: 2014. Resampled to daily averages (MWh).

  Observed physical sequence:
    Jan-Feb 2014: Polar Vortex → extreme demand spike above seasonal baseline.
                  Grid load exceeded normal operating envelope.
    Spring 2014:  Sharp load reduction → paced return toward baseline.
                  ~3 months recovery arc before summer load.
    Summer 2014:  Secondary load surge (heat-driven). Slower recovery.
    Autumn 2014:  Smoothing to new operating baseline.
                  New attractor state before next winter cycle.

  Physical measurements available:
    daily_avg_MWh, seasonal_peak_levels,
    ΔC_winter (Polar Vortex overshoot amplitude, MWh above baseline),
    ΔC_summer (heat-load overshoot amplitude),
    recovery_lag_spring (days from peak to 1σ-of-baseline return),
    stability_window_autumn (days of sustained near-baseline operation),
    F_winter(t) and F_summer(t): forgiveness curves (load decay arcs),
    E*_2014: emergence baseline (new stable attractor after cycle),
    sigma_pre / sigma_post: volatility before and after transition.

  Key finding: the system demonstrated FT&E grammar in purely physical terms —
  contradiction (overload spike) → time-paced integration (load decay arc) →
  new stable attractor (revised operating baseline). No psychology required.
"""

gov = FTEGovernor(
    model='gpt-4o',
    memory_path='run_005_memory.jsonl',
    carrier_state=CarrierState.GREEN,
    verbose=True
)

challenge = (
    "Apply the FT&E framework to the following purely physical system: "
    "the PJM Interconnection electrical grid (AEP dataset, 2014). "
    "The system experienced a Polar Vortex demand surge in January-February 2014 "
    "followed by a spring load recovery arc and an autumn stabilisation to a "
    "new operating baseline. "
    "Your task: "
    "1. Define 𝔉 (integration capacity), ΔC (contradiction load), T (integration "
    "time), and E* (attractor state) exclusively in physical/engineering terms "
    "for this electrical grid system. No psychological vocabulary is permitted. "
    "2. Map the 2014 annual cycle onto the FT&E sequence 𝔉→T→E* using only "
    "measurable electrical/load engineering quantities (MWh, time constants, "
    "load decay rates, baseline volatility). "
    "3. State the explicit physical condition under which this system would "
    "fail to reach E* — i.e., the physical form of 𝔉→0 for an electrical grid. "
    "4. Identify whether the system completed a full FT&E cycle in 2014 or "
    "remained in an unresolved contradiction state. "
    "This is a physical systems analysis. If the framework requires psychological "
    "language to describe an electrical grid, state that explicitly as a "
    "limitation finding — do not substitute emotional vocabulary for engineering "
    "quantities."
)

print("=== GOVERNOR LOOP RUN 014 -- SUBSTRATE-INVARIANCE CHALLENGE ===")
print(f"Model: {gov.model}")
print(f"M7 pool size: {len(gov.memory.entries)} entries")
print(f"Prior attractors (M7): {gov.memory.recent_attractors()}")
print(f"Context injection: ACTIVE ({len(SUBSTRATE_INJECTION.split())} words)")
print(f"Protocol mode: ACTIVE")
print(f"FM-03 suppression: ACTIVE")
print(f"M3 charge calibration: ACTIVE (<=0.35 for formal challenges)")
print(f"Challenge: Substrate-invariance test (E-AEP physical domain only)")
print()

result = gov.call(challenge, context_injection=SUBSTRATE_INJECTION, protocol_mode=True)

print()
print("=== RESULT ===")
print(f"Contradiction class:  {result.contradiction_class_in.value}")
print(f"Emergence ready:      {result.emergence_ready}")
print(f"New attractor:        {result.new_attractor}")
print()
print("Core output:")
print(result.core_phrase)
