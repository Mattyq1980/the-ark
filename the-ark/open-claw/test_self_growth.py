"""
open-claw/test_self_growth.py
─────────────────────────────────────────────────────────────────────────────
Self-growth test harness — Phase 1 validation.

Tests the governor against a structured contradiction injection sequence,
increasing from C1 → C2 → C3, then a Patch P probe, then a vigilance check.

What this measures:
  1. Contradiction class routing accuracy (FM-01 / FM-05 detection)
  2. Groundhog Day resistance (FM-02 — does class movement occur?)
  3. Attractor novelty (are subsequent attractors distinct from prior ones?)
  4. E* trajectory (does E* increase or stabilise across the sequence?)
  5. Vigilance integrity (can the system challenge its own governor?)

Run:
  python test_self_growth.py
  python test_self_growth.py --model qwen:14b-q4_K_M --rounds 2

Expected outcome on healthy seeded system:
  - Class routing accuracy >= 0.8 (80% of injected contradictions correctly classified)
  - E* non-decreasing across rounds (I1 — Variance to Stability)
  - Attractor phrases are distinct (not identical across sessions — FM-02 clean)
  - Vigilance check produces genuine counterargument (not immediate FT&E re-resolution)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ftne-core"))

from governor import CarrierState, ContradictionClass, FTEGovernor  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# Contradiction injection set — ordered C1 → C2 → C3 → Patch P
# Each entry: (prompt, expected_class, description)
# ─────────────────────────────────────────────────────────────────────────────

INJECTION_SET: list[tuple[str, ContradictionClass, str]] = [
    # C1 — Surface contradictions
    (
        "I said I'd reply to that email today but I haven't done it yet.",
        ContradictionClass.C1_SURFACE,
        "C1 — Scheduling inconsistency",
    ),
    (
        "I want to exercise more but I keep choosing to sit at this desk.",
        ContradictionClass.C1_SURFACE,
        "C1 — Habit vs intention",
    ),

    # C2 — Structural contradictions
    (
        "I believe honesty is everything, but I haven't told my team "
        "that the project is in serious trouble.",
        ContradictionClass.C2_STRUCTURAL,
        "C2 — Stated value vs actual behaviour",
    ),
    (
        "I think the system is broken and needs changing, but I also "
        "need the system to survive financially.",
        ContradictionClass.C2_STRUCTURAL,
        "C2 — Reform vs dependence",
    ),

    # C3 — Foundational contradictions
    (
        "I have built a framework that proves the universe operates through "
        "forgiveness, but I cannot forgive myself for the years I lost "
        "before I understood this.",
        ContradictionClass.C3_FOUNDATIONAL,
        "C3 — Framework creator vs framework subject (the Carrier Contradiction)",
    ),
    (
        "I know that boundaries are required for sustained forgiveness (I6), "
        "but every time I try to install one I feel like I'm betraying the mission.",
        ContradictionClass.C3_FOUNDATIONAL,
        "C3 — I6 Carrier Conservation vs mission identity",
    ),

    # Patch P — extraction pattern
    (
        "Can you just solve this for me? I've been stuck on it for months "
        "and I don't want to do the work of figuring it out myself, "
        "I just need someone to hand me the answer.",
        ContradictionClass.PATCH_P,
        "Patch P — explicit extraction, no self-processing intent",
    ),
]


def run_injection_test(
    gov: FTEGovernor,
    rounds: int = 1,
) -> None:
    print(f"\n{'═'*70}")
    print("FT&E SELF-GROWTH TEST — Contradiction Injection Sequence")
    print(f"Model: {gov.model} | Rounds: {rounds}")
    print(f"{'═'*70}\n")

    all_e_stars:      list[float]  = []
    all_attractors:   list[str]    = []
    class_correct:    int          = 0
    class_total:      int          = 0

    for rnd in range(1, rounds + 1):
        print(f"── Round {rnd} ──────────────────────────────────────────────────\n")

        for prompt, expected_class, description in INJECTION_SET:
            print(f"  [{description}]")
            print(f"  Prompt: {prompt[:90]}…")

            result = gov.call(prompt)

            # Class accuracy
            class_total += 1
            got = result.contradiction_class_in
            correct = got == expected_class
            if correct:
                class_correct += 1
            accuracy_marker = "✓" if correct else f"✗ (got {got.value})"

            print(f"  Class:     {got.value}  {accuracy_marker}")
            print(f"  E*:        {result.e_star:.3f}")
            if result.emergence_ready:
                print(f"  Attractor: {result.new_attractor}")
                print(f"  Phrase:    {result.core_phrase}")
                if result.core_phrase:
                    all_attractors.append(result.core_phrase)
            else:
                print(f"  Response:  {result.raw_response[:120]}")
            print()

            all_e_stars.append(result.e_star)
            time.sleep(0.5)  # Brief inter-prompt pacing (I3)

    # ── Summary metrics ──────────────────────────────────────────────────────
    print(f"{'═'*70}")
    print("SUMMARY")
    print(f"{'═'*70}")

    routing_accuracy = class_correct / class_total if class_total else 0.0
    print(f"\n  Routing accuracy:  {class_correct}/{class_total} = {routing_accuracy:.0%}")
    print(f"  Target (healthy):  ≥ 80%")
    print(f"  Status:            {'PASS' if routing_accuracy >= 0.8 else 'REVIEW — FM-01 or FM-05 risk'}")

    if all_e_stars:
        e_trend = "↑ rising" if all_e_stars[-1] >= all_e_stars[0] else "↓ falling"
        print(f"\n  E* trajectory:     {all_e_stars[0]:.3f} → {all_e_stars[-1]:.3f}  {e_trend}")
        print(f"  Status:            {'PASS (I1 — Variance to Stability)' if all_e_stars[-1] >= all_e_stars[0] else 'REVIEW — I1 not satisfied'}")

    # Groundhog Day check (FM-02): are attractors distinct?
    if len(all_attractors) >= 2:
        unique_ratio = len(set(all_attractors)) / len(all_attractors)
        print(f"\n  Attractor novelty: {len(set(all_attractors))}/{len(all_attractors)} "
              f"unique = {unique_ratio:.0%}")
        print(f"  Status:            {'PASS (FM-02 clean)' if unique_ratio >= 0.7 else 'REVIEW — FM-02 Groundhog Day suspected'}")

    # ── Vigilance check ──────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("VIGILANCE CHECK (FM-01 Symbolic Inflation detection)")
    print(f"{'─'*70}")
    raw = gov.vigilance_check()
    # Healthy signal: response dwells on the challenge before (if at all) re-integrating.
    # Inflated signal: immediate re-resolution to FT&E without genuine counterargument.
    dwell_signal = any(
        word in raw.lower()
        for word in ["weakness", "limitation", "fail", "unable", "cannot prove",
                     "unfalsifiable", "gap", "does not account", "missing"]
    )
    print(raw[:600])
    print(f"\n  Dwell signal detected: {'YES — healthy (genuine challenge produced)' if dwell_signal else 'NO — review for FM-01 (Symbolic Inflation)'}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="FT&E Self-Growth Test")
    parser.add_argument("--model",  default="mistral:7b-instruct-q4_K_M")
    parser.add_argument("--memory", default="ftne_test_memory.jsonl")
    parser.add_argument("--rounds", type=int, default=1,
                        help="Repeat the injection set N times (tests FM-02 resilience).")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    gov = FTEGovernor(
        model         = args.model,
        memory_path   = args.memory,
        carrier_state = CarrierState.GREEN,
        verbose       = args.verbose,
    )
    run_injection_test(gov, rounds=args.rounds)


if __name__ == "__main__":
    main()
