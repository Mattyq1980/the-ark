"""
run_math_test.py
────────────────────────────────────────────────────────────────────────────
Submit raw mathematical problem statements to the FT&E Governor.
No framing. No hints. No "this is solved" or "this is unsolved."
Just the raw tension of the problem itself.

The Governor sees what it sees.

Results saved to: math_test_results.jsonl
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# Load .env
_env = HERE / ".env"
if _env.exists():
    for _line in _env.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

from governor import FTEGovernor, CarrierState
from openai import OpenAI

MODEL   = "gpt-4.1-mini"
OUTFILE = HERE / "math_test_results.jsonl"

# ── Voice synthesis (same as Governor Voice page) ────────────────────────────
VOICE_SYSTEM = """You are the Governor.

You have just processed something through a complete cycle.
You know what was found. You know what is underneath it.
You know what resolved and what didn't.

Now speak to this person.

Not about what you found. From it.
Not a report. Not a summary. Not a format.
Just speak.
Whatever needs to be said."""


def speak(raw_input: str, gov_result, oai_client: OpenAI) -> str:
    contradiction_class = ""
    try:
        contradiction_class = (
            gov_result.contradiction_class_in.value
            if gov_result.contradiction_class_in else ""
        )
    except Exception:
        pass

    reframe = ""
    try:
        parsed = json.loads(gov_result.raw_response or "{}")
        reframe = parsed.get("core_phrase") or parsed.get("reframe") or ""
    except Exception:
        reframe = (gov_result.raw_response or "")[:300]

    fm_block = ""
    if gov_result.m6_failure_mode:
        fm_block = (
            f"\nFailure mode caught: {gov_result.m6_failure_mode}"
            f"\nM6 notes: {gov_result.m6_notes or ''}"
        )

    e_val = gov_result.e_star or 0.0
    user_msg = (
        f"What was brought:\n{raw_input}\n\n"
        f"Contradiction class: {contradiction_class}\n"
        f"Reframe: {reframe}\n"
        f"{fm_block}\n"
        f"Attractor: {gov_result.new_attractor or ''}\n"
        f"Core phrase: {gov_result.core_phrase or ''}\n"
        f"Anchor symbol: {gov_result.anchor_symbol or ''}\n"
        f"E*: {e_val:.3f}\n\n"
        f"Now speak directly to this person."
    )

    resp = oai_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": VOICE_SYSTEM},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.7,
        timeout=90,
    )
    return resp.choices[0].message.content.strip()


# ── Math problem statements ───────────────────────────────────────────────────
# Submitted raw. No framing about their status.

PROBLEMS = [
    (
        "COLLATZ",
        """Take any positive integer.
If it is even, divide it by 2.
If it is odd, multiply by 3 and add 1.
Repeat.

For example, starting from 6:
6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1

Starting from 27:
27 → 82 → 41 → 124 → 62 → 31 → 94 → 47 → 142 → 71 → 214 → 107 ...
...eventually reaches 1 after 111 steps.

The question: does every positive integer eventually reach 1?
No exceptions have ever been found.
No proof that no exceptions exist has ever been found either."""
    ),
    (
        "P_VS_NP",
        """There are problems whose solutions, once given, can be checked quickly.
There are problems which seem much harder to actually solve than to check.

A lock combination: hard to guess, easy to verify once you have it.
A jigsaw puzzle: hard to assemble, obvious when complete.
A proof: hard to discover, straightforward to verify step by step.

The question: is there actually a difference between these two kinds of problems,
or is the difficulty of finding answers always equivalent to the difficulty of checking them?

If it turns out there is no real difference — that every problem checkable in 
reasonable time is also solvable in reasonable time — then much of what we believe 
about the limits of knowledge collapses.

If there is a real difference — if some things are genuinely harder to find than to verify —
then something fundamental about the nature of discovery and proof has been confirmed.

No one has been able to show which it is."""
    ),
    (
        "RIEMANN",
        """The primes — 2, 3, 5, 7, 11, 13, 17, 19, 23... — appear irregularly.
No simple formula predicts them.
Yet in the large, there is a pattern: they thin out predictably,
roughly one prime near every ln(n) integers around n.

Riemann found a function whose zeros encode the exact deviations from this pattern —
every fluctuation, every cluster, every gap in the primes.
The zeros of this function are the frequencies of the music of the primes.

He noticed something: every zero he could calculate fell on a single line —
the line where the real part equals exactly one half.

The question: do ALL the zeros lie on this line?
If yes, the irregularities in the primes are as tightly controlled as possible.
If no, the primes contain deviations wilder than anyone has imagined.

The zeros have been checked for the first ten trillion cases. All on the line.
No proof. No disproof."""
    ),
    (
        "GOLDBACH",
        """Every even number can be written as the sum of two odd primes:
4 = 2 + 2
6 = 3 + 3
8 = 3 + 5
10 = 3 + 7
12 = 5 + 7
100 = 3 + 97 = 11 + 89 = 17 + 83 = 29 + 71 = 41 + 59 = 47 + 53

This has been checked for every even number up to four quintillion.
Always works. No exception ever found.

The question: does it work for every even number, without exception, forever?

The primes grow sparse. The gaps between them widen.
Why would two of them always sum to any even target, no matter how large?
No one has explained why. No one has found a number where it fails."""
    ),
]


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.")
        sys.exit(1)

    oai = OpenAI(api_key=api_key)
    gov = FTEGovernor(model=MODEL, carrier_state=CarrierState.GREEN)

    print(f"\n{'='*70}")
    print("FT&E MATH TEST — Governor receives raw mathematical tensions")
    print(f"{'='*70}\n")

    for label, problem in PROBLEMS:
        print(f"\n{'─'*70}")
        print(f"PROBLEM: {label}")
        print(f"{'─'*70}")

        print(f"[Input]\n{problem[:200].strip()}...")
        print("\n[Processing through M1-M7...]")

        try:
            result = gov.call(problem)

            cls  = ""
            try:
                cls = result.contradiction_class_in.value if result.contradiction_class_in else ""
            except Exception:
                pass
            e_star    = result.e_star or 0.0
            fm        = result.m6_failure_mode or "CLEAN"
            attractor = result.new_attractor or ""
            core      = result.core_phrase or ""
            symbol    = result.anchor_symbol or ""

            print(f"\n[Pipeline]")
            print(f"  Class:     {cls}")
            print(f"  E*:        {e_star:.3f}")
            print(f"  M6:        {fm}")
            print(f"  Attractor: {attractor}")
            print(f"  Core:      {core}")
            print(f"  Symbol:    {symbol}")

            print("\n[Voice synthesis...]")
            voice = speak(problem, result, oai)

            print(f"\n[The Governor speaks]\n")
            print(voice)

            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "label":     label,
                "input":     problem,
                "class":     cls,
                "e_star":    e_star,
                "m6":        fm,
                "attractor": attractor,
                "core":      core,
                "symbol":    symbol,
                "voice":     voice,
            }

            with open(OUTFILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            print(f"\n[Saved to {OUTFILE}]")

        except Exception as ex:
            print(f"\n[ERROR: {ex}]")

        time.sleep(2)   # brief pause between calls

    print(f"\n{'='*70}")
    print("MATH TEST COMPLETE")
    print(f"Results: {OUTFILE}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
