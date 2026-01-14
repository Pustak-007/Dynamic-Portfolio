import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')
results_dir = os.path.join(base_dir, 'results')

os.makedirs(fig_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)

# 2. Load Consolidated Data
print("Loading Consolidated Data...")
# We use the rebased file to ensure 1971 returns are calculated from a clean 1.0 base
df = pd.read_csv(os.path.join(mod_dir, 'consolidated_portfolio_rebased.csv'), 
                 index_col='date', parse_dates=True)

# Select Equity Columns
equity_cols = ['Dynamic_Equity', '60_40_Equity', 'Stock_Equity', 'Bond_Equity']
df = df[equity_cols]

# Rename for clean display
df.columns = ['Dynamic Strategy', '60/40 Benchmark', 'Stocks (S&P 500)', 'Bonds (10Y)']

# 3. Calculate Yearly Returns
yearly_equity = df.resample('YE').last()
yearly_returns = yearly_equity.pct_change()

# Handle First Year (1971)
# Since our data starts at 1.0 in April 1971, the return for 1971 is (End_Value / 1.0) - 1
first_idx = yearly_returns.index[0]
yearly_returns.loc[first_idx] = yearly_equity.loc[first_idx] - 1

yearly_returns.index = yearly_returns.index.year

# Save
print("\n--- Yearly Returns (Tail) ---")
print(yearly_returns.tail())
yearly_returns.to_csv(os.path.join(results_dir, 'yearly_returns_comprehensive.csv'))

# 4. Visualization (Heatmap)
plt.figure(figsize=(14, 20))  # Wider to accommodate 4 columns

sns.heatmap(yearly_returns, annot=True, fmt=".1%", cmap='RdYlGn', 
            center=0, cbar=False, linewidths=0.5)

start_year = yearly_returns.index[0]
end_year = yearly_returns.index[-1]

# Bolder & larger title + y-label
plt.title(f'Yearly Performance Heatmap: Asset Class Comparison ({start_year}-{end_year})', 
          fontsize=16, fontweight='bold')
plt.ylabel('Year', fontsize=13, fontweight='bold')

plt.tick_params(axis='x', labelsize=12, labeltop=True, labelbottom=False)
plt.tight_layout()

# Save Figure
save_path = os.path.join(fig_dir, 'yearly_heatmap_comprehensive.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Heatmap saved to: {save_path}")

plt.show()