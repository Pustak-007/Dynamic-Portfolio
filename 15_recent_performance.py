import pandas as pd
import numpy as np
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')

# 2. Load Consolidated Data
print("Loading Master Data...")
df = pd.read_csv(os.path.join(mod_dir, 'consolidated_portfolio_rebased.csv'), index_col='date', parse_dates=True)

# 3. Slice for 2021-Present
start_date = '2021-01-01'
subset = df[df.index >= start_date].copy()

# Select only the Equity Columns
cols = ['Dynamic_Equity', '60_40_Equity', 'Stock_Equity', 'Bond_Equity']
subset = subset[cols]

# 4. Re-Base to 1.0 (To measure performance strictly starting from 2021)
subset = subset / subset.iloc[0]

# 5. Calculate Metrics
results = {}

for col in cols:
    # CAGR
    total_ret = subset[col].iloc[-1]
    years = (subset.index[-1] - subset.index[0]).days / 365.25
    cagr = (total_ret ** (1/years)) - 1
    
    # Max Drawdown
    peak = subset[col].cummax()
    dd = (subset[col] - peak) / peak
    max_dd = dd.min()
    
    results[col] = [f"{cagr:.2%}", f"{max_dd:.2%}"]

# 6. Display Report
metrics_df = pd.DataFrame(results, index=['CAGR (2021-Present)', 'Max Drawdown (2021-Present)'])
metrics_df.columns = ['Dynamic', '60/40', 'Stocks', 'Bonds']

print(f"\n--- Recent Performance Analysis ({start_date} to {subset.index[-1].date()}) ---")
print(metrics_df)