import pandas as pd
import numpy as np
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
results_dir = os.path.join(base_dir, 'results')

os.makedirs(results_dir, exist_ok=True)

# 2. Load Data (Consolidated Master File)
print("Loading Consolidated Data...")
df = pd.read_csv(os.path.join(mod_dir, 'consolidated_portfolio_rebased.csv'), index_col='date', parse_dates=True)

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

# Standardized Trading Years (252)
years = len(df) / 252

# 5. Calculate Friction Metrics
# Assumption: 10 basis points (0.10%) cost per switch
cost_per_trade = 0.0010 

annual_turnover = total_trades / years
total_friction_cost = total_trades * cost_per_trade
annual_friction_drag = total_friction_cost / years

# 6. Net Performance
# Since consolidated file starts at 1.0, we can just use the final value
gross_cagr = (df['Dynamic_Equity'].iloc[-1]) ** (1/years) - 1
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

print("\n--- Turnover & Friction Report (Consolidated Data) ---")
print(stats)

# Save
stats.to_csv(os.path.join(results_dir, 'turnover_stats.csv'))
print(f"\nReport saved to: {os.path.join(results_dir, 'turnover_stats.csv')}")