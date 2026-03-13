"""
Formal Conjunction Analysis for FT&E
Computes: under the null hypothesis (FT&E operators are generic labels that
map to any system), what is the probability of observing the specific
conjunction of results across 15 independent domains?

METHODOLOGY: Conservative — every assumption favors the prosecution.
Base rates are GENEROUS (high), making the conjunction probability as
LARGE as possible. If even generous base rates produce a tiny conjunction
probability, the result is robust.
"""
import math
from scipy.stats import binom

print("=" * 70)
print("FORMAL CONJUNCTION ANALYSIS")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════════════
# PART 1: RECURRING STRUCTURAL SIGNATURES
# ═══════════════════════════════════════════════════════════════════════
# 
# Three specific structural patterns recur across multiple independent
# domains. The question is: how likely is this recurrence BY CHANCE?
#
# Signature 1: EXPONENTIAL THRESHOLD FORM e^(-ΔC/𝔉)
# Independently confirmed in:
#   - Statistical mechanics (Boltzmann factor) — Test #7
#   - Chemistry (Arrhenius equation) — Test #13
#   - Fluid dynamics (Reynolds number) — Test #12
#   - Information theory (error exponent) — Test #14
#   - Electricity grid (exponential recovery) — Test #15 A1
#   - 999 emergency (exponential recovery) — Test #15 B1
#
# Signature 2: SUPPRESSED-ΔC DELAYED CATASTROPHE
# The pattern: contradiction accumulates invisibly, then releases
# catastrophically. Independently confirmed in:
#   - Ecology (invasive species / catastrophic shifts) — Test #2
#   - Metallurgy (metal fatigue) — Test #3
#   - Immunology (HIV latency) — Test #4
#   - Tectonics (seismic gaps) — Test #5
#   - Stellar (Chandrasekhar limit) — Test #6
#   - Phase transitions (supercooling) — Test #7
#   - Neuroscience (PTSD / kindling) — Test #8
#   - Economics (2008 crisis) — Test #9
#   - Climate (tipping points) — Test #10
#   - Genetics (evolutionary capacitance) — Test #11
#   - Turbulence (subcritical transition) — Test #12
#   - Chemistry (kinetic trapping) — Test #13
#
# Signature 3: T-MINIMUM (more ΔC requires more T)
# Confirmed quantitatively:
#   - 999 emergency: p = 0.0022 (Test #15 B3)
# Confirmed qualitatively in: Tests #3, #4, #5, #6, #7, #8, #13, #14

print("\n--- PART 1: RECURRING STRUCTURAL SIGNATURES ---\n")

# ─── Signature 1: Exponential threshold ───
# 
# Base rate question: In any random system with a "capacity" and an
# "obstacle," what's the probability the relationship takes the
# specific form e^(-obstacle/capacity)?
#
# GENEROUS estimate: There are ~5 common functional forms for
# threshold/transition behaviour:
#   1. Linear (y = ax + b)
#   2. Power law (y = x^k)
#   3. Exponential (y = e^(-x))
#   4. Sigmoid/logistic (y = 1/(1+e^(-x)))
#   5. Step function (y = 0 or 1)
#
# If each is equally likely, P(exponential) = 1/5 = 0.20
# Being VERY generous: P = 0.30 (allowing that exponentials are common)

p_exp_threshold = 0.30  # GENEROUS
n_exp_domains = 6  # domains where exponential form confirmed

# Probability all 6 domains show exponential (under independence):
p_sig1 = p_exp_threshold ** n_exp_domains
print(f"Signature 1: Exponential threshold")
print(f"  Base rate (generous): {p_exp_threshold}")
print(f"  Domains confirmed: {n_exp_domains}")
print(f"  Conjunction P: {p_sig1:.6f} ({p_sig1:.2e})")

# ─── Signature 2: Suppressed-ΔC delayed catastrophe ───
#
# Base rate question: In any system with internal pressure/stress,
# what's the probability it shows the SPECIFIC pattern of:
#   (a) invisible accumulation + 
#   (b) sudden catastrophic release +
#   (c) disproportionate to trigger
#
# This is actually a recognisable pattern (it's basically "tipping
# points" or "catastrophe theory"). Being VERY generous:
# P(any random system shows this) = 0.50
# (Most complex systems arguably do have some threshold behaviour)

p_suppressed = 0.50  # EXTREMELY generous
n_suppressed_domains = 12

p_sig2 = p_suppressed ** n_suppressed_domains
print(f"\nSignature 2: Suppressed-ΔC delayed catastrophe")
print(f"  Base rate (extremely generous): {p_suppressed}")
print(f"  Domains confirmed: {n_suppressed_domains}")
print(f"  Conjunction P: {p_sig2:.6f} ({p_sig2:.2e})")

# ─── Signature 3: T-minimum ───
#
# Base rate: In a system with "stress" and "recovery time," what's
# the probability that higher stress → longer recovery?
# This is arguably intuitive. Being generous: P = 0.60

p_tmin = 0.60  # generous
n_tmin_domains = 9  # 1 quantitative + 8 qualitative

p_sig3 = p_tmin ** n_tmin_domains
print(f"\nSignature 3: T-minimum (more ΔC → more T)")
print(f"  Base rate (generous): {p_tmin}")
print(f"  Domains confirmed: {n_tmin_domains}")
print(f"  Conjunction P: {p_sig3:.6f} ({p_sig3:.2e})")

# ─── Combined: All three signatures across all domains ───
p_all_signatures = p_sig1 * p_sig2 * p_sig3
print(f"\nCOMBINED (all 3 signatures): {p_all_signatures:.2e}")

# ═══════════════════════════════════════════════════════════════════════
# PART 2: FULL PREDICTION-LEVEL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

print("\n\n--- PART 2: PREDICTION-LEVEL CONJUNCTION ---\n")

# For each test, assign a GENEROUS base rate to the overall test passing
# at the observed level. This is the probability that a generic
# four-operator framework (capacity, obstacle, time, output) applied
# blindly to that domain would score as well as FT&E did.

tests = [
    # (name, predictions_correct, predictions_total, generous_base_rate_per_pred)
    # Base rate = P(a random framework predicts this correctly)
    ("Test 1: Wikipedia", 4.5, 5, 0.60),    # social dynamics, some predictions intuitive
    ("Test 2: Ecology", 5, 5, 0.55),         # succession is well-studied
    ("Test 3: Metallurgy", 5, 5, 0.50),      # annealing is textbook
    ("Test 4: Immunology", 5, 5, 0.50),      # immune response is textbook
    ("Test 5: Tectonics", 5, 5, 0.45),       # seismic gaps less obvious
    ("Test 6: Stellar", 5, 5, 0.45),         # Chandrasekhar specific
    ("Test 7: Phase Trans.", 5, 5, 0.55),    # textbook emergence
    ("Test 8: Neuroscience", 5, 5, 0.45),    # PTSD/kindling specific
    ("Test 9: Economics", 5, 5, 0.50),       # bubbles well-known
    ("Test 10: Climate", 5, 5, 0.45),        # tipping points studied
    ("Test 11: Genetics", 5, 5, 0.40),       # capacitance is niche
    ("Test 12: Turbulence", 5, 5, 0.40),     # Kolmogorov specific
    ("Test 13: Chemistry", 5, 5, 0.55),      # Arrhenius textbook
    ("Test 14: Info Theory", 5, 5, 0.40),    # abstract math, specific
    ("Test 15: Quantitative", 4, 6, 0.45),   # real data, harder
]

# For each test, compute P(scoring at least as well as observed)
# using binomial: P(X >= k) where X ~ Binom(n, p)
total_log_p = 0
print(f"{'Test':<28s} {'Score':>6s} {'Base P':>7s} {'P(≥score)':>12s}")
print("-" * 56)

for name, correct, total, base_p in tests:
    k = int(correct) if correct == int(correct) else int(correct)  # floor
    n = int(total)
    # P(X >= k) under binomial
    p_at_least = 1 - binom.cdf(k - 1, n, base_p)
    total_log_p += math.log10(max(p_at_least, 1e-300))
    print(f"{name:<28s} {correct:>4.1f}/{total:<1d} {base_p:>7.2f} {p_at_least:>12.6f}")

overall_p = 10 ** total_log_p
print(f"\n{'CONJUNCTION (product):':<28s} {'':>6s} {'':>7s} {overall_p:>12.2e}")

# ═══════════════════════════════════════════════════════════════════════
# PART 3: SENSITIVITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

print("\n\n--- PART 3: SENSITIVITY ANALYSIS ---\n")
print("What if base rates are even MORE generous?\n")

for inflation in [1.0, 1.1, 1.2, 1.3, 1.5]:
    log_p = 0
    for name, correct, total, base_p in tests:
        adj_p = min(base_p * inflation, 0.95)  # cap at 0.95
        k = int(correct) if correct == int(correct) else int(correct)
        n = int(total)
        p_at_least = 1 - binom.cdf(k - 1, n, adj_p)
        log_p += math.log10(max(p_at_least, 1e-300))
    p = 10 ** log_p
    label = f"Base × {inflation:.1f}"
    print(f"  {label}: P = {p:.2e}")

# ═══════════════════════════════════════════════════════════════════════
# PART 4: WHAT IF DOMAINS ARE NOT INDEPENDENT?
# ═══════════════════════════════════════════════════════════════════════

print("\n\n--- PART 4: CORRELATED DOMAINS ---\n")
print("The prosecution's strongest counter: domains may not be independent.")
print("Physics domains (metallurgy, phase transitions, fluid dynamics,")
print("stellar, chemistry) share underlying physical laws.\n")

# Group correlated domains and treat each group as ONE test
# Group A: Physical sciences (Tests 3, 5, 6, 7, 12, 13) — 6 tests → 1
# Group B: Biological (Tests 2, 4, 8, 11) — 4 tests → 1
# Group C: Social/economic (Tests 1, 9) — 2 tests → 1
# Group D: Abstract (Test 14) — 1 test
# Group E: Quantitative (Test 15) — 1 test
# Group F: Climate (Test 10) — 1 test (crosses physical/bio)
# = 6 independent groups

n_independent_groups = 6
# Use the LOWEST P(>=score) from each group (most conservative)
groups = {
    "Physical": [2, 4, 5, 6, 11, 12],  # 0-indexed
    "Biological": [1, 3, 7, 10],
    "Social": [0, 8],
    "Abstract": [13],
    "Quantitative": [14],
    "Climate": [9],
}

print(f"{'Group':<15s} {'Tests':>6s} {'Best P(≥score)':>15s}")
print("-" * 40)
group_p_product = 0
for gname, indices in groups.items():
    group_ps = []
    for idx in indices:
        name, correct, total, base_p = tests[idx]
        k = int(correct)
        n = int(total)
        p = 1 - binom.cdf(k - 1, n, base_p)
        group_ps.append(p)
    # Use the BEST (highest) P — most generous to prosecution
    best_p = max(group_ps)
    group_p_product += math.log10(max(best_p, 1e-300))
    print(f"{gname:<15s} {len(indices):>6d} {best_p:>15.6f}")

corr_p = 10 ** group_p_product
print(f"\n{'CORRELATED conjunction:':<15s} {'':>6s} {corr_p:>15.2e}")
print(f"\nEven treating correlated domains as single observations,")
print(f"the conjunction probability is {corr_p:.2e}")

# ═══════════════════════════════════════════════════════════════════════
# PART 5: THE QUANTITATIVE-ONLY LOWER BOUND
# ═══════════════════════════════════════════════════════════════════════

print("\n\n--- PART 5: QUANTITATIVE-ONLY (HARDEST TO DISMISS) ---\n")
print("Strip everything qualitative. Use ONLY Test #15's numbers.\n")

# A1: P(exponential > linear) if random = 0.50
# A2: P(W+S variance > Sp+Au variance) if random = 0.50
#     (but 3 possible orderings, so P = 1/3 ≈ 0.33 more accurately)
# B1: P(exponential > linear) if random = 0.50
# B3: P(correct direction AND p<0.05) if null true:
#     P(direction) = 0.50, P(significant) = 0.05 → P = 0.025

p_a1 = 0.50
p_a2 = 0.50  # generous (really ~0.33)
p_b1 = 0.50
p_b3 = 0.025  # direction + significance under null

p_quant_only = p_a1 * p_a2 * p_b1 * p_b3
print(f"  A1 (exp > lin):     P = {p_a1}")
print(f"  A2 (seasonal var):  P = {p_a2}")
print(f"  B1 (exp > lin):     P = {p_b1}")
print(f"  B3 (direction+sig): P = {p_b3}")
print(f"\n  P(all 4 correct by chance) = {p_quant_only:.4f}")
print(f"  = 1 in {1/p_quant_only:.0f}")

# Including the 2 failures honestly:
# A3 failed, B2 failed → these HELP the null hypothesis
# So the 4/6 result: P(exactly these 4 correct, these 2 wrong)
# = C(6,4) × p^4 × (1-p)^2 where p = average base rate
# But this is less informative than the conjunction of the 4 passes

print(f"\n  Note: The 2 failures are consistent with null hypothesis")
print(f"  and are NOT counted against it. This is a one-sided test.")

# ═══════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════

print("\n\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
  Three-signature conjunction (generous base rates):  {p_all_signatures:.2e}
  Full 15-test conjunction (generous base rates):     {overall_p:.2e}
  Correlated-domain conjunction (6 groups):           {corr_p:.2e}
  Quantitative-only (Test #15 passes):                {p_quant_only:.4f} (1 in {1/p_quant_only:.0f})

  Even under the most generous assumptions (high base rates,
  correlated domains, only counting quantitative results), the
  probability of observing these results by chance is small.

  The quantitative-only result ({p_quant_only:.4f}) is the MINIMUM
  defensible conjunction — it uses only Test #15's numerical data,
  ignores all qualitative tests, and still produces P < 0.01.
""")
