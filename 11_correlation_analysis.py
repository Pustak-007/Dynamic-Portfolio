"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

os.makedirs(fig_dir, exist_ok=True)

# 2. Load Data
print("Loading Data...")
bench_df = pd.read_csv(os.path.join(mod_dir, 'benchmark_portfolio_1970_2025.csv'), index_col='date', parse_dates=True)
macro_df = pd.read_csv(os.path.join(mod_dir, 'macro_regimes.csv'), index_col='date', parse_dates=True)

# Diagnostic: Check data quality
print(f"Loaded {len(bench_df)} rows of Benchmark Data.")
print(bench_df[['Stock_Returns', 'Bond_Returns']].head())

# Ensure numeric
bench_df['Stock_Returns'] = pd.to_numeric(bench_df['Stock_Returns'], errors='coerce')
bench_df['Bond_Returns'] = pd.to_numeric(bench_df['Bond_Returns'], errors='coerce')

# 3. Calculate Rolling Correlation
# Window: 24 Months (504 days)
# FIX: min_periods=100 allows for holidays/gaps without breaking the calculation
print("Calculating Rolling Correlation...")
window_days = 504
rolling_corr = bench_df['Stock_Returns'].rolling(window=window_days, min_periods=100).corr(bench_df['Bond_Returns'])
rolling_corr.dropna(inplace=True)

print(f"Correlation Data Points Calculated: {len(rolling_corr)}")

if len(rolling_corr) == 0:
    print("CRITICAL ERROR: Correlation calculation failed. Check input data for NaNs or Mismatches.")
    exit()

# 4. Align Regimes
regime_daily = macro_df[['Regime']].reindex(rolling_corr.index, method='ffill')

# 5. Visualization
fig, ax = plt.subplots(figsize=(15, 8))

# Plot Line
ax.plot(rolling_corr.index, rolling_corr, color='black', linewidth=1.5, label='Stock-Bond Correlation (24M Rolling)')

# Zero Line
ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)

# Shading
color_map = {
    'Goldilocks': 'green', 
    'Deflation': 'gray', 
    'Reflation': 'blue', 
    'Stagflation': 'red'
}

for regime_name in color_map.keys():
    mask = regime_daily['Regime'] == regime_name
    if mask.any():
        ax.fill_between(rolling_corr.index, -1, 1, where=mask, 
                        color=color_map[regime_name], alpha=0.2, label=regime_name, step='mid', linewidth=0)

# Formatting
end_year = rolling_corr.index[-1].year
ax.set_ylim(-1, 1)
ax.set_title(f'The Breakdown: Stock-Bond Correlation vs Macro Regimes (1971-{end_year})', fontsize=14)
ax.set_ylabel('Correlation')

ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc='lower left', ncol=5, frameon=True)

ax.grid(True, alpha=0.3)

plt.tight_layout()
save_path = os.path.join(fig_dir, 'correlation_regime_analysis.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Correlation Analysis saved to: {save_path}")
plt.show()
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

# 2. Load Data
print("Loading Data...")
bench_df = pd.read_csv(os.path.join(mod_dir, 'benchmark_portfolio_1970_2025.csv'), index_col='date', parse_dates=True)
macro_df = pd.read_csv(os.path.join(mod_dir, 'macro_regimes.csv'), index_col='date', parse_dates=True)

# Safety Check
bench_df['Stock_Returns'] = pd.to_numeric(bench_df['Stock_Returns'], errors='coerce')
bench_df['Bond_Returns'] = pd.to_numeric(bench_df['Bond_Returns'], errors='coerce')

# 3. Calculate Correlation
print("Calculating Rolling Correlation...")
window_days = 504 # 24 Months
rolling_corr = bench_df['Stock_Returns'].rolling(window=window_days, min_periods=100).corr(bench_df['Bond_Returns'])
rolling_corr.dropna(inplace=True)
rolling_corr.name = 'Correlation'

# 4. Align Regimes for Box Plot
# Merge the daily correlation with the daily regime signal
analysis_df = pd.DataFrame(rolling_corr).join(macro_df[['Regime']], how='inner') # Inner join to match dates

# ==========================================
# FIGURE 1: The Clean Timeline
# ==========================================
fig1, ax1 = plt.subplots(figsize=(15, 7))

ax1.plot(rolling_corr.index, rolling_corr, color='black', linewidth=1.5, label='Stock-Bond Returns Correlation')
ax1.axhline(0, color='red', linestyle='--', linewidth=1)

ax1.set_title('Historical Stock-Bond Returns Correlation (24M Rolling)', fontsize=14)
ax1.set_ylabel('Correlation')
ax1.set_ylim(-1, 1)

ax1.xaxis.set_major_locator(mdates.YearLocator(3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
ax1.grid(True, alpha=0.3)
ax1.legend()

plt.tight_layout()
#fig1.savefig(os.path.join(fig_dir, 'correlation_timeline.png'), dpi=300, bbox_inches='tight')
#print("Figure 1 (Timeline) saved.")

# ==========================================
# FIGURE 2: The Box Plot (Regime Analysis)
# ==========================================
fig2, ax2 = plt.subplots(figsize=(10, 7))

# Define Order: Deflationary First, Inflationary Second
order = ['Goldilocks', 'Deflation', 'Reflation', 'Stagflation']
palette = {'Goldilocks': 'green', 'Deflation': 'gray', 'Reflation': 'blue', 'Stagflation': 'red'}

sns.boxplot(data=analysis_df, x='Regime', y='Correlation', order=order, palette=palette, ax=ax2, width=0.5)

# Add Zero Line
ax2.axhline(0, color='black', linestyle='--', linewidth=1)

ax2.set_title('Stock-Bond Correlation by Macro Regime', fontsize=14)
ax2.set_ylabel('Correlation Distribution')
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
#fig2.savefig(os.path.join(fig_dir, 'correlation_boxplot.png'), dpi=300, bbox_inches='tight')
#print("Figure 2 (Boxplot) saved.")

plt.show()