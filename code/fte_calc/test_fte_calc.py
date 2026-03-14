"""Test harness for FT&E Scientific Calculator."""
import fte_calc


def test_regimes():
    """Verify regime classification matches expected."""
    cases = [
        # (beta, dc, T, expected_regime)
        (0.5, 0.5, 20, fte_calc.Regime.STAGNATION),   # ΔC below min
        (0.02, 6, 30, fte_calc.Regime.SUPPRESSION),    # F≈0, ΔC present
        (0.8, 4, 20, fte_calc.Regime.PRODUCTIVE),      # flow state
        (0.2, 8, 5, fte_calc.Regime.OVERWHELM),        # burnout
        (0.5, 0, 20, fte_calc.Regime.STAGNATION),      # zero ΔC
        (0.0, 0, 20, fte_calc.Regime.STAGNATION),      # zero everything
    ]
    passed = 0
    for beta, dc, t, expected in cases:
        s = fte_calc.FTEState(beta, dc, t)
        actual = s.regime
        ok = actual == expected
        status = "PASS" if ok else "FAIL"
        if not ok:
            print(f"  {status}: beta={beta} dC={dc} T={t}")
            print(f"    expected {expected.value}, got {actual.value}")
            print(f"    E*={s.e_star:.2f}, F*T={s.f_times_t:.2f}")
        else:
            passed += 1
            print(f"  {status}: beta={beta} dC={dc} T={t} -> {actual.value}")
    return passed, len(cases)


def test_inverted_u():
    """Verify E* has inverted-U shape: rises then falls with ΔC."""
    beta, t = 0.8, 20
    dc_values = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    e_values = []
    for dc in dc_values:
        s = fte_calc.FTEState(beta, dc, t)
        e_values.append(s.e_star)

    # Find peak
    peak_val = max(e_values)
    peak_idx = e_values.index(peak_val)

    # Should rise to peak then fall
    rising = all(e_values[i] <= e_values[i+1] for i in range(peak_idx))
    falling = all(e_values[i] >= e_values[i+1] for i in range(peak_idx, len(e_values)-1))
    # Peak should not be at either extreme
    interior_peak = peak_idx > 0 and peak_idx < len(e_values) - 1

    print(f"\n  Inverted-U test (beta={beta}, T={t}):")
    for dc, e in zip(dc_values, e_values):
        marker = " <-- peak" if e == peak_val else ""
        print(f"    dC={dc:4.1f}  E*={e:7.2f}{marker}")

    ok = rising and falling and interior_peak
    print(f"  Peak at index {peak_idx} of {len(e_values)-1}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"    rising={rising} falling={falling} interior={interior_peak}")
    return 1 if ok else 0, 1


def test_suppression_vs_metabolisation():
    """Verify metabolisation always produces more E* than suppression."""
    cases = [(3, 20), (5, 20), (7, 15), (2, 30)]
    passed = 0
    print(f"\n  Suppression vs Metabolisation:")
    for dc, t in cases:
        sup = fte_calc.FTEState(0.02, dc, t)
        met = fte_calc.FTEState(0.6, dc, t)
        ok = met.e_star > sup.e_star
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: dC={dc} T={t}  sup_E*={sup.e_star:.2f}  met_E*={met.e_star:.2f}")
        if ok:
            passed += 1
    return passed, len(cases)


def test_optimal():
    """Verify optimal ΔC calculation."""
    s = fte_calc.FTEState(0.8, 4, 20)
    opt = s.optimal_delta_c()
    print(f"\n  Optimal dC test:")
    print(f"    beta=0.8 T=20 -> optimal dC={opt:.1f}")

    # E* at optimal should be >= E* at current
    opt_state = fte_calc.FTEState(0.8, opt, 20)
    ok = opt_state.e_star >= s.e_star - 0.01  # tolerance
    print(f"    E* at optimal: {opt_state.e_star:.2f}")
    print(f"    E* at current: {s.e_star:.2f}")
    print(f"    {'PASS' if ok else 'FAIL'}")
    return 1 if ok else 0, 1


def test_presets():
    """Verify all presets produce valid diagnostics."""
    passed = 0
    print(f"\n  Preset tests:")
    for name, state in fte_calc.PRESETS.items():
        output = fte_calc.diagnose(state)
        ok = "REGIME:" in output and "E*" in output
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {name} -> {state.regime.value} (E*={state.e_star:.2f})")
        if ok:
            passed += 1
    return passed, len(fte_calc.PRESETS)


def test_diagnose_output():
    """Verify diagnose produces complete output."""
    s = fte_calc.FTEState(0.5, 4, 20)
    output = fte_calc.diagnose(s)
    checks = ["DIAGNOSTIC", "REGIME:", "F\u00b7T", "Inverted-U", "What to change"]
    passed = 0
    print(f"\n  Diagnostic output checks:")
    for check in checks:
        ok = check in output
        print(f"    {'PASS' if ok else 'FAIL'}: '{check}' in output")
        if ok:
            passed += 1
    return passed, len(checks)


# Run all tests
print("=" * 50)
print("  FT&E Scientific Calculator — Test Suite")
print("=" * 50)

total_pass = 0
total_tests = 0

for test_fn in [test_regimes, test_inverted_u, test_suppression_vs_metabolisation,
                test_optimal, test_presets, test_diagnose_output]:
    p, t = test_fn()
    total_pass += p
    total_tests += t

print(f"\n{'=' * 50}")
print(f"  TOTAL: {total_pass}/{total_tests} passed")
print(f"{'=' * 50}")
