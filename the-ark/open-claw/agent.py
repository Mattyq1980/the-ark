"""
open-claw/agent.py
─────────────────────────────────────────────────────────────────────────────
Open-Claw — minimal agent base that delegates every decision to the FT&E governor.

The agent has no opinions. It has a governor.
All contradiction intake routes through FTEGovernor.call().
The agent's job: receive input, route it, act on the EmergenceResult.

Usage:
  python agent.py
  python agent.py --model qwen:14b-q4_K_M --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ftne-core"))

from governor import CarrierState, FTEGovernor, NodeRole  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Open-Claw FT&E Agent")
    parser.add_argument(
        "--model",
        default="mistral:7b-instruct-q4_K_M",
        help="Ollama model tag (default: mistral:7b-instruct-q4_K_M). "
             "Recommend 13B+ for M3/M5 quality.",
    )
    parser.add_argument(
        "--memory",
        default="ftne_memory.jsonl",
        help="Path to persistent attractor memory file (M7).",
    )
    parser.add_argument(
        "--node-role",
        default="COORDINATOR",
        choices=[r.value for r in NodeRole],
        help="Cluster node role. COORDINATOR runs all modules (single-node default).",
    )
    parser.add_argument(
        "--carrier-state",
        default="GREEN",
        choices=[s.value for s in CarrierState],
        help="I6 carrier state. AMBER defers C3. RED accepts C1 only.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Log each module's raw LLM output."
    )
    parser.add_argument(
        "--lite", action="store_true", default=True,
        help="Single LLM call per input (default ON). Use on CPU-only hardware. "
             "Disable with --no-lite on GPU machines for full M2-M6 pipeline.",
    )
    parser.add_argument("--no-lite", dest="lite", action="store_false")
    parser.add_argument(
        "--vigilance", action="store_true",
        help="Run FM-01 (Symbolic Inflation) self-check before entering main loop.",
    )
    args = parser.parse_args()

    gov = FTEGovernor(
        model         = args.model,
        memory_path   = args.memory,
        carrier_state = CarrierState(args.carrier_state),
        node_role     = NodeRole(args.node_role),
        verbose       = args.verbose,
    )

    mode_label = "LITE (1 LLM call)" if args.lite else "FULL (4 LLM calls)"
    print(f"Mode: {mode_label}")
    if args.lite:
        print("Tip: use --no-lite on a GPU machine for the full M2-M6 pipeline.\n")

    if args.vigilance:
        print("\n── Vigilance Check (FM-01) ──")
        raw = gov.vigilance_check()
        print(raw)
        print("────────────────────────────\n")

    print("Open-Claw agent ready. Type your input, or 'quit' to exit.")
    print("Special commands:  :state green|amber|red  (set carrier state)")
    print("                   :memory                (show recent attractors)")
    print("                   :vigilance             (run FM-01 self-check)\n")

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        # Meta-commands
        if user_input.startswith(":state "):
            _, state_arg = user_input.split(None, 1)
            try:
                gov.set_carrier_state(CarrierState(state_arg.upper()))
            except ValueError:
                print(f"Unknown state: {state_arg}. Use green, amber, or red.")
            continue

        if user_input == ":memory":
            attractors = gov.memory.recent_attractors(n=10)
            if attractors:
                print("Recent attractors (M7):")
                for i, a in enumerate(attractors, 1):
                    print(f"  {i}. {a}")
            else:
                print("No attractors in memory yet.")
            continue

        if user_input == ":vigilance":
            print("── Vigilance Check (FM-01) ──")
            raw = gov.vigilance_check()
            print(raw)
            print("────────────────────────────")
            continue

        # Main governor loop
        result = gov.lite_call(user_input) if args.lite else gov.call(user_input)

        print("\n── FT&E Result ──────────────────────────")
        print(f"  Session:   {result.session_id}")
        print(f"  Class:     {result.contradiction_class_in.value}")
        print(f"  E* score:  {result.e_star:.3f}  "
              f"(F={result.f_score:.2f} × T={result.t_elapsed:.1f}s − ΔC={result.delta_c:.2f})")
        if result.emergence_ready:
            print(f"  Attractor: {result.new_attractor}")
            print(f"  Symbol:    {result.anchor_symbol}")
            print(f"  Phrase:    {result.core_phrase}")
            print(f"  Stability: {result.stability_index:.2f}")
        else:
            print(f"  Response:  {result.raw_response}")
        print("─────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
