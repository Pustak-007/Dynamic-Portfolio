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

# 2. Load Data
print("Loading Backtest Data...")
df = pd.read_csv(os.path.join(mod_dir, 'final_backtest_results.csv'), index_col='date', parse_dates=True)

# 3. Calculate Yearly Returns
# We resample to Year End ('YE') and take the last equity value
yearly_equity = df[['Dynamic_Equity', '60_40_Equity']].resample('YE').last()

# Calculate % Change from year to year
yearly_returns = yearly_equity.pct_change()

# Handle the first year (1971) which might be NaN due to pct_change
# We calculate it manually based on the start value (1.0)
first_year_idx = yearly_returns.index[0]
yearly_returns.loc[first_year_idx, 'Dynamic_Equity'] = yearly_equity.loc[first_year_idx, 'Dynamic_Equity'] - 1
yearly_returns.loc[first_year_idx, '60_40_Equity'] = yearly_equity.loc[first_year_idx, '60_40_Equity'] - 1

# Rename columns for display
yearly_returns.columns = ['Dynamic Strategy', '60/40 Benchmark']
yearly_returns.index = yearly_returns.index.year # Use just the year number

# Save Data
print("\n--- Yearly Returns (Tail) ---")
print(yearly_returns.tail())
yearly_returns.to_csv(os.path.join(results_dir, 'yearly_returns.csv'))
print("Yearly returns saved.")

# 4. Visualization (Heatmap)
plt.figure(figsize=(10, 15))  # Tall figure to fit 50+ years

# Create Heatmap
# cmap='RdYlGn' maps Red (Loss) to Green (Gain)
sns.heatmap(yearly_returns, annot=True, fmt=".1%", cmap='RdYlGn', center=0,
            cbar=False, linewidths=0.5, xticklabels=True)

# Move x-axis labels to top
plt.gca().xaxis.tick_top()
plt.gca().xaxis.set_label_position('top')

plt.title('Yearly Performance Heatmap (1971-Present)', fontsize=14)
plt.ylabel('Year')
plt.tight_layout()

save_path = os.path.join(fig_dir, 'yearly_heatmap.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Heatmap saved to: {save_path}")
plt.show()