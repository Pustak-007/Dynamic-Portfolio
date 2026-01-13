"""import pandas as pd
import numpy as np
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
results_dir = os.path.join(base_dir, 'results')

os.makedirs(results_dir, exist_ok=True)

# 2. Load Data
print("Loading Backtest Data...")
df = pd.read_csv(os.path.join(mod_dir, 'final_backtest_results.csv'), index_col='date', parse_dates=True)

# 3. Map Regimes to Assets (The "Portfolio State")
# We need to know what we are holding to calculate turnover
# Goldilocks -> Stocks
# Deflation -> Bonds
# Reflation/Stagflation -> Commodities

asset_map = {
    'Goldilocks': 'Stocks',
    'Deflation': 'Bonds',
    'Reflation': 'Commodities',
    'Stagflation': 'Commodities'
}

df['Holding'] = df['Regime'].map(asset_map)

# 4. Calculate Switches
# A "Trade" happens only when the Holding changes (e.g. Stocks -> Bonds)
# We shift(1) to compare today vs yesterday
df['Trade_Occurred'] = df['Holding'] != df['Holding'].shift(1)

# The first day is always a "Trade" (Entry), but usually excluded from turnover stats
# We set the first row to False to measure *changes*
df.iloc[0, df.columns.get_loc('Trade_Occurred')] = False

total_trades = df['Trade_Occurred'].sum()
years = (df.index[-1] - df.index[0]).days / 365.25

# 5. Calculate Friction Metrics
# Assumption: 10 basis points (0.10%) cost per switch (Sell + Buy slippage/commissions)
cost_per_trade = 0.0010 

annual_turnover = total_trades / years
total_friction_cost = total_trades * cost_per_trade
annual_friction_drag = total_friction_cost / years

# 6. Net Performance
gross_cagr = (df['Dynamic_Equity'].iloc[-1] / df['Dynamic_Equity'].iloc[0]) ** (1/years) - 1
net_cagr = gross_cagr - annual_friction_drag

# 7. Generate Report
stats = pd.Series({
    'Total Years': years,
    'Total Asset Switches': total_trades,
    'Avg Switches Per Year': annual_turnover,
    'Avg Holding Period (Months)': (years * 12) / total_trades,
    'Assumed Cost Per Trade': f"{cost_per_trade:.2%}",
    'Annual Friction Drag': f"{annual_friction_drag:.4%}",
    'Gross CAGR (No Cost)': f"{gross_cagr:.2%}",
    'Net CAGR (After Cost)': f"{net_cagr:.2%}"
}, name='Turnover Analysis')

print("\n--- Turnover & Friction Report ---")
print(stats)

# Save Report
stats.to_csv(os.path.join(results_dir, 'turnover_stats.csv'))
print(f"\nReport saved to: {os.path.join(results_dir, 'dynamic_turnover_stats.csv')}")
"""

import pandas as pd
import numpy as np
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
results_dir = os.path.join(base_dir, 'results')

os.makedirs(results_dir, exist_ok=True)

# 2. Load Data
print("Loading Backtest Data...")
df = pd.read_csv(os.path.join(mod_dir, 'final_backtest_results.csv'), index_col='date', parse_dates=True)

# 3. Map Regimes to Assets
asset_map = {
    'Goldilocks': 'Stocks',
    'Deflation': 'Bonds',
    'Reflation': 'Commodities',
    'Stagflation': 'Commodities'
}

df['Holding'] = df['Regime'].map(asset_map)

# 4. Calculate Switches
df['Trade_Occurred'] = df['Holding'] != df['Holding'].shift(1)
df.iloc[0, df.columns.get_loc('Trade_Occurred')] = False

total_trades = df['Trade_Occurred'].sum()

# FIX: Use Trading Years (252) to match Module 8's methodology
years = len(df) / 252

# 5. Calculate Friction Metrics
# Assumption: 10 basis points (0.10%) cost per switch
cost_per_trade = 0.0010 

annual_turnover = total_trades / years
total_friction_cost = total_trades * cost_per_trade
annual_friction_drag = total_friction_cost / years

# 6. Net Performance (Using Geometric CAGR Formula consistent with Module 8)
# Formula: (End / Start)^(1/N) - 1
gross_cagr = (df['Dynamic_Equity'].iloc[-1] / df['Dynamic_Equity'].iloc[0]) ** (1/years) - 1
net_cagr = gross_cagr - annual_friction_drag

# 7. Generate Report
stats = pd.Series({
    'Total Trading Years (252)': f"{years:.2f}",
    'Total Asset Switches': total_trades,
    'Avg Switches Per Year': f"{annual_turnover:.2f}",
    'Assumed Cost Per Trade': f"{cost_per_trade:.2%}",
    'Annual Friction Drag': f"{annual_friction_drag:.4%}",
    'Gross CAGR (No Cost)': f"{gross_cagr:.2%}",
    'Net CAGR (After Cost)': f"{net_cagr:.2%}"
}, name='Turnover Analysis')

print("\n--- Turnover & Friction Report (Standardized to Trading Years) ---")
print(stats)

# Save
stats.to_csv(os.path.join(results_dir, 'turnover_stats.csv'))
print(f"\nReport saved to: {os.path.join(results_dir, 'turnover_stats.csv')}")