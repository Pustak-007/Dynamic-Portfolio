import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter, NullLocator
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_path = os.path.join(base_dir, 'modified_data', 'benchmark_portfolio_1970_2025.csv')
fig_path = os.path.join(base_dir, 'figures', 'asset_class_comparison.png')

# 2. Load Data
print("Loading processed benchmark data...")
df = pd.read_csv(mod_path, index_col='date', parse_dates=True)

# Calculate Component Equity Curves
df['Stock_Equity'] = (1 + df['Stock_Returns']).cumprod()
df['Bond_Equity'] = (1 + df['Bond_Returns']).cumprod()
df['60_40_Equity'] = (1 + df['60_40_Returns']).cumprod()

# 3. Plotting
fig, ax = plt.subplots(figsize=(15, 8))

# Plot Lines
ax.plot(df.index, df['Stock_Equity'], label='Stocks (S&P 500)', linewidth=1.2, color='#2ca02c', alpha=0.8)
ax.plot(df.index, df['Bond_Equity'], label='Bonds (10Y Treasury)', linewidth=1.2, color='#d62728', alpha=0.8)
ax.plot(df.index, df['60_40_Equity'], label='60/40 Portfolio', linewidth=2.0, color='#1f77b4')

# Log Scale Formatting
ax.set_yscale('log')

# Manual Ticks (Extended range to cover Stocks high performance)
y_ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500] 
ax.set_yticks(y_ticks)
ax.get_yaxis().set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_locator(NullLocator())

# Labels & Ticks
ax.set_ylabel('Portfolio Value (Growth of $1)', fontsize=12)
ax.set_title('Asset Class Performance Comparison (1970-Present)', fontsize=14)

ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

ax.grid(True, which="major", ls="-", alpha=0.5)
ax.legend(loc='upper left', fontsize=11)

plt.tight_layout()

# Save & Show
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"Figure saved to: {fig_path}")

plt.show()