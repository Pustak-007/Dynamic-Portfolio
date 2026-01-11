import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter, NullLocator
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

os.makedirs(fig_dir, exist_ok=True)

# 2. Load Data
print("Loading Data...")
dyn_df = pd.read_csv(os.path.join(mod_dir, 'final_backtest_results.csv'), index_col='date', parse_dates=True)
comp_df = pd.read_csv(os.path.join(mod_dir, 'benchmark_portfolio_1970_2025.csv'), index_col='date', parse_dates=True)

# Merge into one view
df = dyn_df[['Dynamic_Equity', '60_40_Equity']].join(comp_df[['Stock_Equity', 'Bond_Equity']], how='inner')

# 3. Calculate Final Values
initial_vals = df.iloc[0]
final_vals = df.iloc[-1]
print("\n--- Final Portfolio Values (Growth of $1) ---")
print(final_vals)

# 4. Visualization
fig, ax = plt.subplots(figsize=(15, 9))

# Plot Lines with Change in Legend
ax.plot(df.index, df['Stock_Equity'], label=f'Stocks (S&P 500): ${initial_vals["Stock_Equity"]:.2f} → ${final_vals["Stock_Equity"]:.2f}',
         color='green', linewidth=1, alpha=0.6)

ax.plot(df.index, df['Bond_Equity'], label=f'Bonds (10Y Treas): ${initial_vals["Bond_Equity"]:.2f} → ${final_vals["Bond_Equity"]:.2f}',
         color='red', linewidth=1, alpha=0.6)

ax.plot(df.index, df['60_40_Equity'], label=f'60/40 Benchmark: ${initial_vals["60_40_Equity"]:.2f} → ${final_vals["60_40_Equity"]:.2f}',
         color='gray', linewidth=1.5, linestyle='--')

ax.plot(df.index, df['Dynamic_Equity'], label=f'Dynamic Strategy: ${initial_vals["Dynamic_Equity"]:.2f} → ${final_vals["Dynamic_Equity"]:.2f}',
         color='purple', linewidth=2.5)

# Formatting
ax.set_yscale('log')
y_ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500]
ax.set_yticks(y_ticks)
ax.get_yaxis().set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_locator(NullLocator())

# Dynamic Title
start_year = df.index[0].year
end_year = df.index[-1].year
ax.set_title(f'Comprehensive Asset Comparison ({start_year}-{end_year})', fontsize=14)
ax.set_ylabel('Portfolio Value (Growth of $1)')

# X-Axis: Every 3 Years
ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

ax.grid(True, which="major", ls="-", alpha=0.5)
ax.legend(loc='upper left', fontsize=11, frameon=True)

plt.tight_layout()

# 5. Save & Show
save_path = os.path.join(fig_dir, 'comprehensive_comparison.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Comparison Figure saved to: {save_path}")

plt.show()