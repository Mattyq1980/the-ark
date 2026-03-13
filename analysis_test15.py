"""
FT&E Prospective Test #15 — Quantitative Analysis
Predictions locked at commit 6d316ff BEFORE this script was written.
"""
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import ttest_ind
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("FT&E PROSPECTIVE TEST #15 — QUANTITATIVE DATA ANALYSIS")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════════════
# DATASET A: AEP ELECTRICITY GRID
# ═══════════════════════════════════════════════════════════════════════

aep = pd.read_csv(
    r'C:\FTandE\FT&E_ModelBuild_V4_CurrentStructured'
    r'\FT&E_Folder_12_Experiments_2\FT&E_Experiment_6_ElectricityUsage'
    r'\AEP_hourly.csv'
)
aep['Datetime'] = pd.to_datetime(aep['Datetime'])
aep = aep.set_index('Datetime').sort_index()
daily = aep.resample('D').mean()
daily.columns = ['MW']

print("\n--- DATASET A: AEP Electricity (daily averages) ---")
print(f"  Rows: {len(daily)}, Date range: {daily.index.min().date()} to {daily.index.max().date()}")
print(f"  Overall mean: {daily['MW'].mean():.1f} MW, std: {daily['MW'].std():.1f} MW")

# ─────────────────────────────────────────────────────────────────────
# PREDICTION A1: Exponential vs Linear recovery after spikes
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PREDICTION A1: EXPONENTIAL vs LINEAR RECOVERY")
print("=" * 70)

# Identify major spikes: days where load > mean + 2*std
threshold = daily['MW'].mean() + 2 * daily['MW'].std()
spikes = daily[daily['MW'] > threshold].index

# Group consecutive spike days into events
events = []
if len(spikes) > 0:
    current_event_start = spikes[0]
    current_event_end = spikes[0]
    for i in range(1, len(spikes)):
        if (spikes[i] - spikes[i-1]).days <= 3:
            current_event_end = spikes[i]
        else:
            events.append((current_event_start, current_event_end))
            current_event_start = spikes[i]
            current_event_end = spikes[i]
    events.append((current_event_start, current_event_end))

print(f"  Spike threshold: {threshold:.0f} MW (mean + 2*std)")
print(f"  Spike events found: {len(events)}")

def exp_decay(t, baseline, A, tau):
    return baseline + A * np.exp(-t / max(tau, 0.1))

def linear_decay(t, baseline, A, B):
    return baseline + A - B * t

exp_r2_list = []
lin_r2_list = []
events_analyzed = 0

for start, end in events:
    # Get 30-day recovery window after spike
    recovery_start = end + pd.Timedelta(days=1)
    recovery_end = recovery_start + pd.Timedelta(days=30)
    recovery = daily.loc[recovery_start:recovery_end, 'MW'].dropna()
    
    if len(recovery) < 10:
        continue
    
    # Calculate baseline as 30-day mean before the spike
    pre_start = start - pd.Timedelta(days=30)
    pre_baseline = daily.loc[pre_start:start - pd.Timedelta(days=1), 'MW'].mean()
    
    if np.isnan(pre_baseline):
        continue
    
    t = np.arange(len(recovery), dtype=float)
    y = recovery.values
    peak_excess = y[0] - pre_baseline
    
    if peak_excess <= 0:
        continue
    
    # Fit exponential
    try:
        popt_exp, _ = curve_fit(exp_decay, t, y, 
                                p0=[pre_baseline, peak_excess, 10],
                                maxfev=5000)
        y_pred_exp = exp_decay(t, *popt_exp)
        ss_res_exp = np.sum((y - y_pred_exp)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2_exp = 1 - ss_res_exp / ss_tot if ss_tot > 0 else 0
    except Exception:
        r2_exp = -1
    
    # Fit linear
    try:
        popt_lin, _ = curve_fit(linear_decay, t, y,
                                p0=[pre_baseline, peak_excess, peak_excess/30],
                                maxfev=5000)
        y_pred_lin = linear_decay(t, *popt_lin)
        ss_res_lin = np.sum((y - y_pred_lin)**2)
        r2_lin = 1 - ss_res_lin / ss_tot if ss_tot > 0 else 0
    except Exception:
        r2_lin = -1
    
    if r2_exp >= 0 and r2_lin >= 0:
        exp_r2_list.append(r2_exp)
        lin_r2_list.append(r2_lin)
        events_analyzed += 1

print(f"  Events analyzed (sufficient data): {events_analyzed}")
if events_analyzed > 0:
    mean_exp_r2 = np.mean(exp_r2_list)
    mean_lin_r2 = np.mean(lin_r2_list)
    exp_wins = sum(1 for e, l in zip(exp_r2_list, lin_r2_list) if e > l)
    print(f"  Mean R² (exponential): {mean_exp_r2:.4f}")
    print(f"  Mean R² (linear):      {mean_lin_r2:.4f}")
    print(f"  Exponential wins: {exp_wins}/{events_analyzed}")
    if mean_exp_r2 > mean_lin_r2:
        print("  >>> PREDICTION A1: CONFIRMED — exponential fits better")
    else:
        print("  >>> PREDICTION A1: FAILED — linear fits better")
else:
    print("  >>> PREDICTION A1: INSUFFICIENT DATA TO TEST")

# ─────────────────────────────────────────────────────────────────────
# PREDICTION A2: Seasonal ΔC structure (variance clustering)
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PREDICTION A2: SEASONAL VARIANCE CLUSTERING")
print("=" * 70)

daily['month'] = daily.index.month
daily['year'] = daily.index.year

# Monthly mean for each year to compute deviations
daily['monthly_mean'] = daily.groupby([daily.index.year, daily.index.month])['MW'].transform('mean')
daily['deviation'] = daily['MW'] - daily['monthly_mean']

def season(m):
    if m in [12, 1, 2]: return 'Winter'
    elif m in [3, 4, 5]: return 'Spring'
    elif m in [6, 7, 8]: return 'Summer'
    else: return 'Autumn'

daily['season'] = daily['month'].apply(season)
seasonal_var = daily.groupby('season')['deviation'].var()

print("  Daily deviation variance by season:")
for s in ['Winter', 'Spring', 'Summer', 'Autumn']:
    print(f"    {s:8s}: {seasonal_var[s]:.0f}")

winter_summer_var = (seasonal_var['Winter'] + seasonal_var['Summer']) / 2
spring_autumn_var = (seasonal_var['Spring'] + seasonal_var['Autumn']) / 2

print(f"\n  Winter+Summer mean variance: {winter_summer_var:.0f}")
print(f"  Spring+Autumn mean variance: {spring_autumn_var:.0f}")

if winter_summer_var > spring_autumn_var:
    print("  >>> PREDICTION A2: CONFIRMED — contradiction clusters in winter/summer")
else:
    print("  >>> PREDICTION A2: FAILED — variance not seasonal")

# Also check: top 1% deviation days by season
top_1pct = daily.nlargest(int(len(daily) * 0.01), 'deviation')
top_season_counts = top_1pct['season'].value_counts()
print(f"\n  Top 1% deviation days by season: {dict(top_season_counts)}")

# ─────────────────────────────────────────────────────────────────────
# PREDICTION A3: Emergence ≠ return to baseline (2014 Polar Vortex)
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PREDICTION A3: NEW ATTRACTOR AFTER POLAR VORTEX")
print("=" * 70)

# March-April 2013 vs March-April 2014
ma_2013 = daily.loc['2013-03':'2013-04', 'MW']
ma_2014 = daily.loc['2014-03':'2014-04', 'MW']

print(f"  March-April 2013: mean={ma_2013.mean():.1f} MW, n={len(ma_2013)}")
print(f"  March-April 2014: mean={ma_2014.mean():.1f} MW, n={len(ma_2014)}")

t_stat, p_val = ttest_ind(ma_2013.dropna(), ma_2014.dropna())
print(f"  t-statistic: {t_stat:.3f}")
print(f"  p-value: {p_val:.6f}")

if p_val < 0.05:
    direction = "higher" if ma_2014.mean() > ma_2013.mean() else "lower"
    print(f"  >>> PREDICTION A3: CONFIRMED — post-Polar Vortex baseline is "
          f"significantly {direction} (p={p_val:.6f})")
else:
    print(f"  >>> PREDICTION A3: FAILED — no significant difference (p={p_val:.4f})")

# ═══════════════════════════════════════════════════════════════════════
# DATASET B: 999 EMERGENCY RESPONSE
# ═══════════════════════════════════════════════════════════════════════

print("\n\n" + "=" * 70)
print("DATASET B: 999 EMERGENCY RESPONSE")
print("=" * 70)

nnn = pd.read_csv(
    r'C:\FTandE\FT&E_ModelBuild_V4_CurrentStructured'
    r'\FT&E_Folder_12_Experiments_2\FT&E_Experiment_5_999Response'
    r'\999-data-nov-21---feb-25.csv'
)

# Clean column names
nnn.columns = [c.replace('\n', ' ').strip() for c in nnn.columns]
nnn['date'] = pd.to_datetime(nnn['Year'].astype(str) + '-' + nnn['Month'].astype(str).str.zfill(2) + '-01')
nnn = nnn.sort_values(['Police force name', 'date'])

avg_col = [c for c in nnn.columns if 'Average answer time' in c][0]
calls_col = [c for c in nnn.columns if 'Total Calls' in c][0]

print(f"  Answer time column: '{avg_col}'")
print(f"  Total calls column: '{calls_col}'")
print(f"  Forces: {nnn['Police force name'].nunique()}")
print(f"  Date range: {nnn['date'].min().date()} to {nnn['date'].max().date()}")

# ─────────────────────────────────────────────────────────────────────
# PREDICTION B1: Exponential vs Linear recovery after answer time spikes
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PREDICTION B1: EXPONENTIAL vs LINEAR RECOVERY (999)")
print("=" * 70)

exp_r2_999 = []
lin_r2_999 = []
spikes_found = 0

for force in nnn['Police force name'].unique():
    force_data = nnn[nnn['Police force name'] == force].sort_values('date')
    times = force_data[avg_col].values
    
    if len(times) < 6:
        continue
    
    median_time = np.nanmedian(times)
    
    # Find months where answer time > 1.5× median
    for i in range(len(times)):
        if times[i] > 1.5 * median_time and i + 4 < len(times):
            # Get recovery window (next 4 months minimum)
            recovery = times[i:min(i+6, len(times))]
            recovery = recovery[~np.isnan(recovery)]
            
            if len(recovery) < 4:
                continue
            
            t = np.arange(len(recovery), dtype=float)
            y = recovery
            baseline_est = median_time
            A_est = y[0] - baseline_est
            
            if A_est <= 0:
                continue
            
            ss_tot = np.sum((y - np.mean(y))**2)
            if ss_tot == 0:
                continue
            
            # Fit exponential
            try:
                popt_exp, _ = curve_fit(exp_decay, t, y,
                                        p0=[baseline_est, A_est, 2],
                                        maxfev=5000)
                y_pred_exp = exp_decay(t, *popt_exp)
                ss_res_exp = np.sum((y - y_pred_exp)**2)
                r2_exp = 1 - ss_res_exp / ss_tot
            except Exception:
                r2_exp = -1
            
            # Fit linear
            try:
                popt_lin, _ = curve_fit(linear_decay, t, y,
                                        p0=[baseline_est, A_est, A_est/4],
                                        maxfev=5000)
                y_pred_lin = linear_decay(t, *popt_lin)
                ss_res_lin = np.sum((y - y_pred_lin)**2)
                r2_lin = 1 - ss_res_lin / ss_tot
            except Exception:
                r2_lin = -1
            
            if r2_exp >= 0 and r2_lin >= 0:
                exp_r2_999.append(r2_exp)
                lin_r2_999.append(r2_lin)
                spikes_found += 1

print(f"  Answer time spikes found (>1.5× median): {spikes_found}")
if spikes_found > 0:
    mean_exp = np.mean(exp_r2_999)
    mean_lin = np.mean(lin_r2_999)
    exp_wins = sum(1 for e, l in zip(exp_r2_999, lin_r2_999) if e > l)
    print(f"  Mean R² (exponential): {mean_exp:.4f}")
    print(f"  Mean R² (linear):      {mean_lin:.4f}")
    print(f"  Exponential wins: {exp_wins}/{spikes_found}")
    if mean_exp > mean_lin:
        print("  >>> PREDICTION B1: CONFIRMED — exponential fits better")
    else:
        print("  >>> PREDICTION B1: FAILED — linear fits better or equal")
else:
    print("  >>> PREDICTION B1: INSUFFICIENT DATA TO TEST")

# ─────────────────────────────────────────────────────────────────────
# PREDICTION B2: Threshold relationship (calls vs answer time)
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PREDICTION B2: THRESHOLD RELATIONSHIP (CALLS vs ANSWER TIME)")
print("=" * 70)

# Use all data points
calls = pd.to_numeric(nnn[calls_col], errors='coerce')
times = pd.to_numeric(nnn[avg_col], errors='coerce')
mask = calls.notna() & times.notna()
x_all = calls[mask].values
y_all = times[mask].values

# Single linear regression
from numpy.polynomial import polynomial as P
coeffs_lin = np.polyfit(x_all, y_all, 1)
y_pred_single = np.polyval(coeffs_lin, x_all)
ss_res_single = np.sum((y_all - y_pred_single)**2)
ss_tot_b2 = np.sum((y_all - np.mean(y_all))**2)
r2_single = 1 - ss_res_single / ss_tot_b2

# Piecewise linear (find best breakpoint)
best_r2_pw = -np.inf
best_bp = None

# Try breakpoints at percentiles 20 to 80
for pct in range(20, 81, 5):
    bp = np.percentile(x_all, pct)
    mask_lo = x_all <= bp
    mask_hi = x_all > bp
    
    if sum(mask_lo) < 10 or sum(mask_hi) < 10:
        continue
    
    # Fit two separate lines
    try:
        c_lo = np.polyfit(x_all[mask_lo], y_all[mask_lo], 1)
        c_hi = np.polyfit(x_all[mask_hi], y_all[mask_hi], 1)
        y_pred_pw = np.zeros_like(y_all)
        y_pred_pw[mask_lo] = np.polyval(c_lo, x_all[mask_lo])
        y_pred_pw[mask_hi] = np.polyval(c_hi, x_all[mask_hi])
        ss_res_pw = np.sum((y_all - y_pred_pw)**2)
        r2_pw = 1 - ss_res_pw / ss_tot_b2
        if r2_pw > best_r2_pw:
            best_r2_pw = r2_pw
            best_bp = bp
            best_slope_lo = c_lo[0]
            best_slope_hi = c_hi[0]
    except Exception:
        continue

print(f"  Data points: {len(x_all)}")
print(f"  Single linear R²: {r2_single:.4f}")
if best_bp is not None:
    print(f"  Piecewise linear R²: {best_r2_pw:.4f} (breakpoint at {best_bp:.0f} calls)")
    print(f"  Slope below breakpoint: {best_slope_lo:.6f}")
    print(f"  Slope above breakpoint: {best_slope_hi:.6f}")
    if best_r2_pw > r2_single and best_slope_hi > best_slope_lo:
        print("  >>> PREDICTION B2: CONFIRMED — threshold/hockey-stick pattern detected")
    elif best_r2_pw > r2_single:
        print("  >>> PREDICTION B2: PARTIAL — piecewise fits better but slopes don't show hockey-stick")
    else:
        print("  >>> PREDICTION B2: FAILED — single linear fits as well or better")
else:
    print("  >>> PREDICTION B2: COULD NOT FIT PIECEWISE MODEL")

# ─────────────────────────────────────────────────────────────────────
# PREDICTION B3: High-ΔC forces show longer recovery (T-minimum)
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PREDICTION B3: T-MINIMUM — HIGH-ΔC FORCES RECOVER SLOWER")
print("=" * 70)

# Calculate mean answer time per force
force_means = nnn.groupby('Police force name')[avg_col].mean().sort_values()
median_force_mean = force_means.median()

low_dc_forces = force_means[force_means <= median_force_mean].index
high_dc_forces = force_means[force_means > median_force_mean].index

print(f"  Low-ΔC forces (n={len(low_dc_forces)}): mean answer time ≤ {median_force_mean:.1f}s")
print(f"  High-ΔC forces (n={len(high_dc_forces)}): mean answer time > {median_force_mean:.1f}s")

# For each group, find spikes and measure recovery time
def measure_recovery_times(forces, data):
    recovery_times = []
    for force in forces:
        fd = data[data['Police force name'] == force].sort_values('date')
        t_vals = fd[avg_col].values
        if len(t_vals) < 4:
            continue
        med = np.nanmedian(t_vals)
        for i in range(len(t_vals)):
            if t_vals[i] > 1.5 * med:
                # Count months until answer time drops back below 1.2× median
                recovery_t = 0
                for j in range(i+1, len(t_vals)):
                    recovery_t += 1
                    if t_vals[j] <= 1.2 * med:
                        break
                if recovery_t > 0:
                    recovery_times.append(recovery_t)
    return recovery_times

low_recovery = measure_recovery_times(low_dc_forces, nnn)
high_recovery = measure_recovery_times(high_dc_forces, nnn)

print(f"\n  Low-ΔC group: {len(low_recovery)} recovery events, mean={np.mean(low_recovery):.2f} months" if low_recovery else "  Low-ΔC group: no recovery events")
print(f"  High-ΔC group: {len(high_recovery)} recovery events, mean={np.mean(high_recovery):.2f} months" if high_recovery else "  High-ΔC group: no recovery events")

if low_recovery and high_recovery:
    t_stat_b3, p_val_b3 = ttest_ind(high_recovery, low_recovery, alternative='greater')
    print(f"  t-statistic (one-tailed, high > low): {t_stat_b3:.3f}")
    print(f"  p-value: {p_val_b3:.4f}")
    if np.mean(high_recovery) > np.mean(low_recovery) and p_val_b3 < 0.05:
        print("  >>> PREDICTION B3: CONFIRMED — high-ΔC forces recover slower (p<0.05)")
    elif np.mean(high_recovery) > np.mean(low_recovery):
        print(f"  >>> PREDICTION B3: PARTIAL — direction correct but not significant (p={p_val_b3:.4f})")
    else:
        print("  >>> PREDICTION B3: FAILED — high-ΔC forces recover same speed or faster")
else:
    print("  >>> PREDICTION B3: INSUFFICIENT DATA")

# ═══════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════

print("\n\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print("  Predictions locked at commit 6d316ff (pushed to GitHub)")
print("  Analysis run AFTER lock — this is genuine prospective testing")
print("  against numerical data the AI had not previously examined.")
