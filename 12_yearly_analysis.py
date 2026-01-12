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

# 2. Load Data (All Components)
print("Loading Data...")
dyn_df = pd.read_csv(os.path.join(mod_dir, 'final_backtest_results.csv'), index_col='date', parse_dates=True)
comp_df = pd.read_csv(os.path.join(mod_dir, 'benchmark_portfolio_1970_2025.csv'), index_col='date', parse_dates=True)

# Merge Equity Curves
df = pd.DataFrame(index=dyn_df.index)
df['Dynamic'] = dyn_df['Dynamic_Equity']
df['60/40'] = dyn_df['60_40_Equity']
# Align Stocks/Bonds to the same start date
common_index = df.index.intersection(comp_df.index)
df['Stocks'] = comp_df.loc[common_index, 'Stock_Equity']
df['Bonds'] = comp_df.loc[common_index, 'Bond_Equity']

# 3. Calculate Yearly Returns
yearly_equity = df.resample('YE').last()
yearly_returns = yearly_equity.pct_change()

# Handle First Year (Manual Calculation from 1.0 base or first available)
# Since curves start > 1.0 sometimes due to indexing, pct_change is safer, 
# but for the very first row, we check the growth from the start of data.
first_idx = yearly_returns.index[0]
start_val = df.iloc[0]
end_val = yearly_equity.iloc[0]
yearly_returns.loc[first_idx] = (end_val / start_val) - 1

yearly_returns.index = yearly_returns.index.year

# Save
print("\n--- Yearly Returns (Tail) ---")
print(yearly_returns.tail())
yearly_returns.to_csv(os.path.join(results_dir, 'yearly_returns_comprehensive.csv'))

# 4. Visualization (Heatmap)
plt.figure(figsize=(12, 18)) # Wider and Taller

sns.heatmap(yearly_returns, annot=True, fmt=".1%", cmap='RdYlGn', center=0, cbar=False, linewidths=0.5)

plt.title('Yearly Performance Heatmap: Asset Class Comparison', fontsize=16)
plt.ylabel('Year')
plt.tick_params(axis='x', labelsize=12, labeltop=True, labelbottom=False) # Put labels on top for readability
plt.tight_layout()

save_path = os.path.join(fig_dir, 'yearly_heatmap_comprehensive.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Heatmap saved to: {save_path}")

plt.show()