"""
The FT&E Calculator
===================
Every program is E* = F·T − ΔC in silicon.

Errors are contradictions. Good software metabolises them.
Bad software suppresses them.

This calculator demonstrates the difference.

Run:  python calculator.py
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# ΔC CLASSIFICATION
#
# Contradictions have types. Typed errors get routed.
# Untyped errors get swallowed.
#
# Invariant 4: No E* without metabolising ΔC.
#   → Every error must be classified and produce output. Never swallowed.
#
# Invariant 11: E* maximal at intermediate ΔC.
#   → Too-simple input is trivial (no contradiction). Too-complex
#     input overwhelms. The productive range is in between.
# ---------------------------------------------------------------------------

class ErrorKind(Enum):
    SYNTAX = "syntax"
    DOMAIN = "domain"
    OVERFLOW = "overflow"
    EMPTY = "empty"
    UNBALANCED = "unbalanced"


METABOLISATION_GUIDES = {
    ErrorKind.SYNTAX:      "Check operator placement and valid characters.",
    ErrorKind.DOMAIN:      "This operation is mathematically undefined.",
    ErrorKind.OVERFLOW:    "Result too large to represent. Try smaller values.",
    ErrorKind.EMPTY:       "Enter an expression to evaluate.",
    ErrorKind.UNBALANCED:  "Check that every '(' has a matching ')'.",
}


@dataclass
class Contradiction:
    """A classified error — ΔC that has been through M2 (identification).

    The key structural choice: this is a DATA OBJECT, not an exception.
    Exceptions propagate invisibly. Data objects flow through the same
    pipeline as results. Nothing gets suppressed.
    """
    kind: ErrorKind
    message: str
    expression: str
    position: Optional[int] = None

    def metabolise(self) -> str:
        """F operator: transform the contradiction into useful output.

        A bad program returns "" or raises SystemExit here.
        A good program classifies, explains, and continues.
        """
        pointer = ""
        if self.position is not None:
            pointer = f"\n  {'.' * self.position}^"

        return (
            f"  [{self.kind.value}] {self.message}"
            f"{pointer}\n"
            f"  > {METABOLISATION_GUIDES[self.kind]}"
        )


# ---------------------------------------------------------------------------
# TOKENIZER
#
# Invariant 6: Carrier without boundary redistributes ΔC without
# coherence gain.
#   → The tokenizer IS a boundary. It separates raw text (unbounded
#     user input) from structured tokens (bounded internal data).
#     Without this boundary, user input flows directly into evaluation
#     — which is what eval() does, and why eval() is dangerous.
# ---------------------------------------------------------------------------

class TokenKind(Enum):
    NUMBER  = "number"
    PLUS    = "+"
    MINUS   = "-"
    STAR    = "*"
    SLASH   = "/"
    CARET   = "^"
    LPAREN  = "("
    RPAREN  = ")"
    END     = "end"


@dataclass
class Token:
    kind: TokenKind
    value: str
    pos: int


OPERATOR_MAP = {
    "+": TokenKind.PLUS,   "-": TokenKind.MINUS,
    "*": TokenKind.STAR,   "/": TokenKind.SLASH,
    "^": TokenKind.CARET,  "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
}


def tokenize(expr: str) -> list[Token] | Contradiction:
    """Convert expression string to tokens, or classify the contradiction."""
    tokens: list[Token] = []
    i = 0
    while i < len(expr):
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        # Numbers (including decimals like .5 and 5.)
        if ch.isdigit() or ch == ".":
            start = i
            dot_count = 0
            while i < len(expr) and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    dot_count += 1
                i += 1
            num_str = expr[start:i]
            if dot_count > 1:
                return Contradiction(
                    ErrorKind.SYNTAX,
                    f"Invalid number '{num_str}' — multiple decimal points",
                    expr, start,
                )
            tokens.append(Token(TokenKind.NUMBER, num_str, start))
            continue

        # Operators and parentheses
        if ch in OPERATOR_MAP:
            tokens.append(Token(OPERATOR_MAP[ch], ch, i))
            i += 1
            continue

        # Anything else is a classified contradiction
        return Contradiction(
            ErrorKind.SYNTAX,
            f"Unexpected character '{ch}'",
            expr, i,
        )

    tokens.append(Token(TokenKind.END, "", len(expr)))
    return tokens


# ---------------------------------------------------------------------------
# PARSER — Recursive descent
#
# Grammar (precedence low→high):
#   expr   → term (('+' | '-') term)*
#   term   → power (('*' | '/') power)*
#   power  → unary ('^' power)?          [right-associative]
#   unary  → '-' unary | atom
#   atom   → NUMBER | '(' expr ')'
#
# Each level is a MODULE BOUNDARY (I6). Precedence errors are caught
# at the level where they occur, not somewhere downstream.
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens: list[Token], expr: str):
        self.tokens = tokens
        self.expr = expr
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self) -> float | Contradiction:
        result = self._expr()
        if isinstance(result, Contradiction):
            return result
        if self.peek().kind != TokenKind.END:
            tok = self.peek()
            return Contradiction(
                ErrorKind.SYNTAX,
                f"Unexpected '{tok.value}' after complete expression",
                self.expr, tok.pos,
            )
        return result

    # --- Grammar rules ---

    def _expr(self) -> float | Contradiction:
        left = self._term()
        if isinstance(left, Contradiction):
            return left
        while self.peek().kind in (TokenKind.PLUS, TokenKind.MINUS):
            op = self.advance()
            right = self._term()
            if isinstance(right, Contradiction):
                return right
            left = (left + right) if op.kind == TokenKind.PLUS else (left - right)
        return left

    def _term(self) -> float | Contradiction:
        left = self._power()
        if isinstance(left, Contradiction):
            return left
        while self.peek().kind in (TokenKind.STAR, TokenKind.SLASH):
            op = self.advance()
            right = self._power()
            if isinstance(right, Contradiction):
                return right
            if op.kind == TokenKind.STAR:
                left = left * right
            else:
                if right == 0:
                    return Contradiction(
                        ErrorKind.DOMAIN,
                        "Division by zero",
                        self.expr, op.pos,
                    )
                left = left / right
        return left

    def _power(self) -> float | Contradiction:
        base = self._unary()
        if isinstance(base, Contradiction):
            return base
        if self.peek().kind == TokenKind.CARET:
            self.advance()
            exp = self._power()  # right-associative
            if isinstance(exp, Contradiction):
                return exp
            try:
                result = base ** exp
            except OverflowError:
                return Contradiction(
                    ErrorKind.OVERFLOW,
                    f"{base}^{exp} exceeds representable range",
                    self.expr,
                )
            if isinstance(result, complex):
                return Contradiction(
                    ErrorKind.DOMAIN,
                    f"Negative base with fractional exponent produces complex number",
                    self.expr,
                )
            if math.isinf(result):
                return Contradiction(
                    ErrorKind.OVERFLOW,
                    f"{base}^{exp} exceeds representable range",
                    self.expr,
                )
            return result
        return base

    def _unary(self) -> float | Contradiction:
        if self.peek().kind == TokenKind.MINUS:
            self.advance()
            operand = self._unary()
            if isinstance(operand, Contradiction):
                return operand
            return -operand
        return self._atom()

    def _atom(self) -> float | Contradiction:
        tok = self.peek()

        if tok.kind == TokenKind.NUMBER:
            self.advance()
            return float(tok.value)

        if tok.kind == TokenKind.LPAREN:
            self.advance()
            result = self._expr()
            if isinstance(result, Contradiction):
                return result
            closing = self.peek()
            if closing.kind != TokenKind.RPAREN:
                return Contradiction(
                    ErrorKind.UNBALANCED,
                    "Missing closing ')'",
                    self.expr, tok.pos,
                )
            self.advance()
            return result

        if tok.kind == TokenKind.RPAREN:
            return Contradiction(
                ErrorKind.UNBALANCED,
                "Unexpected ')' without matching '('",
                self.expr, tok.pos,
            )

        if tok.kind == TokenKind.END:
            return Contradiction(
                ErrorKind.SYNTAX,
                "Unexpected end of expression",
                self.expr, tok.pos,
            )

        return Contradiction(
            ErrorKind.SYNTAX,
            f"Expected number or '(', got '{tok.value}'",
            self.expr, tok.pos,
        )


# ---------------------------------------------------------------------------
# SESSION — Prior E*
#
# The calculator remembers. Resolved expressions become available
# via 'ans'. Error patterns accumulate. This is the structural
# trace — what the system has been through changes what it can do next.
#
# A bad calculator is stateless: every error is encountered for the
# first time, forever. No accumulation, no learning, no E*.
# ---------------------------------------------------------------------------

@dataclass
class SessionEntry:
    expression: str
    result: Optional[float] = None
    error: Optional[Contradiction] = None


class Session:
    def __init__(self):
        self.history: list[SessionEntry] = []
        self.error_counts: dict[ErrorKind, int] = {k: 0 for k in ErrorKind}

    def record_success(self, expr: str, result: float):
        self.history.append(SessionEntry(expr, result=result))

    def record_error(self, expr: str, error: Contradiction):
        self.history.append(SessionEntry(expr, error=error))
        self.error_counts[error.kind] += 1

    def last_result(self) -> Optional[float]:
        for entry in reversed(self.history):
            if entry.result is not None:
                return entry.result
        return None

    def summary(self) -> str:
        total = len(self.history)
        errors = sum(1 for e in self.history if e.error)
        successes = total - errors
        lines = [f"  {successes} resolved, {errors} contradictions metabolised"]
        active = {k: v for k, v in self.error_counts.items() if v > 0}
        if active:
            lines.append("  Error profile: " + ", ".join(
                f"{k.value}={v}" for k, v in active.items()
            ))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# FORMAT
# ---------------------------------------------------------------------------

def format_result(value: float) -> str:
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    if abs(value) < 0.001 or abs(value) > 1e12:
        return f"{value:.6e}"
    return f"{value:g}"


# ---------------------------------------------------------------------------
# EVALUATE — The full pipeline
#
# Input → tokenize → parse → result OR classified contradiction.
# Nothing is suppressed. Every path produces output.
# ---------------------------------------------------------------------------

def evaluate(expr: str, session: Session) -> str:
    stripped = expr.strip()

    if not stripped:
        error = Contradiction(ErrorKind.EMPTY, "Empty input", expr)
        session.record_error(expr, error)
        return error.metabolise()

    # 'ans' substitution — prior E* flowing into current computation
    last = session.last_result()
    if last is not None:
        stripped = re.sub(r"\bans\b", format_result(last), stripped)

    tokens = tokenize(stripped)
    if isinstance(tokens, Contradiction):
        session.record_error(expr, tokens)
        return tokens.metabolise()

    parser = Parser(tokens, stripped)
    result = parser.parse()
    if isinstance(result, Contradiction):
        session.record_error(expr, result)
        return result.metabolise()

    if math.isnan(result):
        error = Contradiction(ErrorKind.DOMAIN, "Result is undefined (NaN)", stripped)
        session.record_error(expr, error)
        return error.metabolise()
    if math.isinf(result):
        error = Contradiction(
            ErrorKind.OVERFLOW, "Result exceeds representable range", stripped,
        )
        session.record_error(expr, error)
        return error.metabolise()

    session.record_success(expr, result)
    return f"  = {format_result(result)}"


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

BANNER = """\
+------------------------------------------+
|  The FT&E Calculator                     |
|  E* = F*T - dC  -- in silicon            |
|                                          |
|  Errors are metabolised, not suppressed. |
|  Type 'help' for commands, 'quit' to exit|
+------------------------------------------+
"""


def main():
    session = Session()
    print(BANNER)

    while True:
        try:
            expr = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            print(session.summary())
            break

        cmd = expr.strip().lower()

        if cmd in ("quit", "exit", "q"):
            print(session.summary())
            break

        if cmd == "help":
            print("  Operators: + - * / ^ ()")
            print("  'ans'     use previous result")
            print("  'history' session log")
            print("  'errors'  error profile")
            print("  'quit'    exit")
            continue

        if cmd == "history":
            if not session.history:
                print("  No history yet.")
            else:
                for i, entry in enumerate(session.history, 1):
                    if entry.result is not None:
                        print(f"  [{i}] {entry.expression} = {format_result(entry.result)}")
                    else:
                        print(f"  [{i}] {entry.expression} -> [{entry.error.kind.value}]")
            continue

        if cmd == "errors":
            print(session.summary())
            continue

        print(evaluate(expr, session))


if __name__ == "__main__":
    main()
