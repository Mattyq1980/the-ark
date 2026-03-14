# The FT&E Calculator

**Every program is E\* = F·T − ΔC in silicon.**

This is a calculator. It adds, subtracts, multiplies, divides. Nothing special — except every design decision was made by asking one question:

> *Am I suppressing this contradiction, or metabolising it?*

That question, applied consistently, produces better software. This calculator demonstrates why.

## Run

```
python calculator.py
```

## The Equation in Code

| FT&E Concept | In This Calculator |
|---|---|
| **ΔC** (contradiction) | Runtime errors: division by zero, syntax errors, overflow, unmatched parens |
| **F** (forgiveness operator) | Error metabolisation: classify the error → explain it → continue operating |
| **T** (time) | Processing pipeline: tokenize → parse → evaluate (each stage has time to do its work) |
| **E\*** (emergent stable state) | Correct result, or a *useful* error explanation — both are productive output |
| **Prior E\*** | Session history: `ans` carries previous results forward; error counts accumulate |

## Invariants Demonstrated

| Invariant | Where |
|---|---|
| **I4**: No E\* without metabolising ΔC | Errors are *never* swallowed. Every error produces classified, explained output |
| **I6**: Carrier without boundary redistributes ΔC without coherence gain | Tokenizer, parser, evaluator are **separate modules**. User input hits a boundary before it reaches evaluation |
| **I11**: E\* maximal at intermediate ΔC | Too-simple input (empty) = trivial. Too-complex input (overflow) = overwhelm. The productive range is in between |
| **I17**: Surface absorption without structural capacity | What we *avoided* — see below |

## What Bad Software Looks Like

This is the I17 calculator — surface competence, no structural capacity:

```python
def calculate(expr):
    try:
        return eval(expr)
    except:
        return "Error"
```

Four lines. Four invariant violations:

1. **`eval(expr)`** — No parsing boundary. User input flows directly into execution. This is an **I6 violation**: carrier without boundary. It's also a security vulnerability — `eval()` executes arbitrary code. The lack of boundary doesn't just lose information, it creates attack surface.

2. **`except:`** — Bare except with no type. Catches *everything*, classifies *nothing*. This is an **I4 violation**: the contradiction existed, it contained information (what went wrong, where, why), and this line destroys all of it.

3. **`return "Error"`** — The metabolisation output is identical regardless of whether you divided by zero, had a syntax error, or overflowed. This is **suppressed ΔC disguised as handled ΔC**. It looks like error handling. It isn't.

4. **No state** — Every error is encountered for the first time, forever. No history, no accumulation, no learning. No prior E\*.

The bad calculator *works* for `2 + 2`. It fails structurally the moment anything unexpected happens — and it fails *silently*, which means the failure compounds.

## The Design Principle

The FT&E question for every line of code:

> **Is this line suppressing a contradiction or metabolising it?**

- `try/except/pass` → suppression
- `try/except TypeError as e: log(e); return default` → metabolisation
- `eval(user_input)` → no boundary (I6 violation)
- `tokenize(user_input)` → boundary that classifies before passing through
- Global mutable state → no boundary between components
- Dataclass with typed fields → structured boundary

Every design decision maps to the equation. You don't need to know the framework to write good software. But the framework tells you *why* good software is good and *why* bad patterns keep recurring: **suppressed ΔC doesn't disappear. It accumulates. And it always surfaces eventually — as bugs, as security holes, as systems that "work" until they don't.**

## The Framework

If you want to read it: [The Ark](https://github.com/Mattyq1980/the-ark)

E\* = F·T − ΔC is a structural law describing how contradictions get metabolised into stable states — in people, in systems, in code. The 19 invariants are the constraints. The calculator is a small proof that the equation produces better engineering when applied as a design principle.
