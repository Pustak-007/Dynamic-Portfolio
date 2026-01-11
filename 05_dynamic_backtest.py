import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter, NullLocator
import os

# 1. Directory Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

for path in [mod_dir, fig_dir]:
    os.makedirs(path, exist_ok=True)

# 2. Load Data
print("Loading Processed Data...")
bench = pd.read_csv(os.path.join(mod_dir, 'benchmark_portfolio_1970_2025.csv'), index_col='date', parse_dates=True)
alts  = pd.read_csv(os.path.join(mod_dir, 'alternative_assets_1970_2025.csv'), index_col='date', parse_dates=True)
macro = pd.read_csv(os.path.join(mod_dir, 'macro_regimes.csv'), index_col='date', parse_dates=True)

# 3. Data Alignment & Processing
# Calculate Commodity Returns from Price
alts['Commodity_Returns'] = alts['Commodities_Price'].pct_change()

# Merge into Master DF (Daily)
df = pd.DataFrame(index=bench.index)
df = df.join(bench[['Stock_Returns', 'Bond_Returns', '60_40_Returns']])
df = df.join(alts[['Commodity_Returns']])

# Align Regime Signal (Monthly -> Daily)
regime_daily = macro[['Regime']].reindex(df.index, method='ffill')

# Shift Signal by 1 Day (Avoid Lookahead Bias)
df['Regime'] = regime_daily.shift(1)

# 4. Strategy Implementation
conditions = [
    df['Regime'] == 'Goldilocks',
    df['Regime'] == 'Reflation',
    df['Regime'] == 'Stagflation',
    df['Regime'] == 'Deflation'
]

choices = [
    df['Stock_Returns'],      # Goldilocks
    df['Commodity_Returns'],  # Reflation
    df['Commodity_Returns'],  # Stagflation
    df['Bond_Returns']        # Deflation
]

df['Dynamic_Returns'] = np.select(conditions, choices, default=0.0)

# Calculate Equity Curves
df['Dynamic_Equity'] = (1 + df['Dynamic_Returns']).cumprod()
df['60_40_Equity']   = (1 + df['60_40_Returns']).cumprod()

# 5. Save Results
output_columns = ['Regime', 'Dynamic_Returns', 'Dynamic_Equity', '60_40_Returns', '60_40_Equity']
final_df = df[output_columns].dropna()

print("\n--- Final Data Tail ---")
print(final_df.tail(50))

save_path = os.path.join(mod_dir, 'final_backtest_results.csv')
final_df.to_csv(save_path)
print(f"Backtest Data saved to: {save_path}")

# 6. Visualization
fig, ax = plt.subplots(figsize=(15, 8))

ax.plot(final_df.index, final_df['Dynamic_Equity'], label='Dynamic Regime Strategy', color='purple', linewidth=2)
ax.plot(final_df.index, final_df['60_40_Equity'], label='60/40 Benchmark', color='gray', linewidth=1, linestyle='--')

ax.set_yscale('log')
y_ticks = [1, 5, 10, 50, 100, 500, 1000]
ax.set_yticks(y_ticks)
ax.get_yaxis().set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_locator(NullLocator())

end_year = final_df.index[-1].year
ax.set_title(f'Dynamic Regime Strategy vs 60/40 (1970-{end_year})', fontsize=14)
ax.set_ylabel('Portfolio Value (Growth of $1)')

# X-Axis: Every 3 Years
ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

ax.legend(loc='upper left')
ax.grid(True, which="major", ls="-", alpha=0.5)

plt.tight_layout()
fig_save_path = os.path.join(fig_dir, 'dynamic_backtest_result.png')
plt.savefig(fig_save_path, dpi=300, bbox_inches='tight')
print(f"Figure saved to: {fig_save_path}")

plt.show()