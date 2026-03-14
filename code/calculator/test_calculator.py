"""Quick test harness."""
import calculator

session = calculator.Session()

tests = [
    ("2 + 2", "4"),
    ("3 * (4 + 5)", "27"),
    ("10 / 3", "3.33333"),
    ("2 ^ 10", "1024"),
    ("-5 + 3", "-2"),
    ("100 / 0", "[domain]"),
    ("2 + + 3", "[syntax]"),
    ("(2 + 3", "[unbalanced]"),
    (")", "[unbalanced]"),
    ("", "[empty]"),
    ("1.2.3 + 4", "[syntax]"),
    ("2 @ 5", "[syntax]"),
    ("(-3) ^ 0.5", "[domain]"),
    ("999 ^ 999", "[overflow]"),
]

passed = 0
failed = 0

for expr, expected in tests:
    result = calculator.evaluate(expr, session)
    ok = expected in result.lower() or expected in result
    status = "PASS" if ok else "FAIL"
    if not ok:
        failed += 1
        print(f"  {status}: {repr(expr)}")
        print(f"    expected '{expected}' in output")
        print(f"    got: {result}")
    else:
        passed += 1
        print(f"  {status}: {repr(expr)}")

# Test 'ans'
ans_result = calculator.evaluate("ans + 1", session)
last = session.last_result()
print(f"\n  ans test: 'ans + 1' after 999^999 error")
print(f"    last result was: {last}")
print(f"    output: {ans_result}")

print(f"\n  {passed}/{passed + failed} passed, {failed} failed")
print(f"\n{session.summary()}")
