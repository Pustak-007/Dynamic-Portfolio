import pandas as pd
import numpy as np
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
results_dir = os.path.join(base_dir, 'results')

os.makedirs(results_dir, exist_ok=True)

# 2. Load Data
print("Loading Data...")
# Load Strategy Returns
dyn_df = pd.read_csv(os.path.join(mod_dir, 'final_backtest_results.csv'), index_col='date', parse_dates=True)

# Load Risk-Free Rate (Daily)
rf_df = pd.read_csv(os.path.join(mod_dir, 'risk_free_daily.csv'), index_col='date', parse_dates=True)

# 3. Merge & Align Risk-Free Rate
# We align Rf to the Strategy Timeline. ffill() handles weekends/holidays if needed.
df = dyn_df.join(rf_df, how='left').ffill()

# 4. Calculate Excess Returns (The "Professional" Step)
# Strategy Return minus Risk-Free Rate
df['Dyn_Excess']   = df['Dynamic_Returns'] - df['Risk_Free_Return']
df['60_40_Excess'] = df['60_40_Returns'] - df['Risk_Free_Return']

# 5. Define Metric Engine
def calculate_metrics(returns, excess_returns):
    """
    Calculates Annualized Metrics.
    For Regimes (discontinuous data), we use Annualized Average Return (Mean * 252).
    """
    if len(returns) < 2:
        return pd.Series([0,0,0,0,0], index=['Ann. Return', 'Volatility', 'Sharpe', 'Sortino', 'Max DD'])
    
    # 1. Annualized Return (Run Rate)
    # We use arithmetic mean * 252 for regime attribution (standard attribution practice)
    ann_return = returns.mean() * 252
    
    # 2. Volatility (Annualized)
    volatility = returns.std() * np.sqrt(252)
    
    # 3. Sharpe Ratio (The Core Metric)
    # (Mean Daily Excess Return * 252) / (Std Dev of Excess * sqrt(252))
    sharpe = (excess_returns.mean() * 252) / (excess_returns.std() * np.sqrt(252))
    
    # 4. Sortino Ratio (Penalizes only downside volatility)
    # We take returns below 0, calculate their std dev
    negative_returns = returns[returns < 0]
    downside_dev = negative_returns.std() * np.sqrt(252)
    sortino = (excess_returns.mean() * 252) / (downside_dev + 1e-9)
    
    # 5. Max Drawdown (While IN this specific state)
    # We reconstruct a theoretical equity curve just for this slice
    cum_ret = (1 + returns).cumprod()
    peak = cum_ret.cummax()
    drawdown = (cum_ret - peak) / peak
    max_dd = drawdown.min()
    
    return pd.Series([ann_return, volatility, sharpe, sortino, max_dd], 
                     index=['Ann. Return', 'Volatility', 'Sharpe', 'Sortino', 'Max DD'])

# 6. Calculate OVERALL Metrics
print("\n--- Calculating Overall Metrics ---")
stats_dyn = calculate_metrics(df['Dynamic_Returns'], df['Dyn_Excess'])
stats_6040 = calculate_metrics(df['60_40_Returns'], df['60_40_Excess'])

overall_df = pd.DataFrame({'Dynamic Strategy': stats_dyn, '60/40 Benchmark': stats_6040}).T
print(overall_df)

# 7. Calculate REGIME-SPECIFIC Metrics
print("\n--- Calculating Regime Breakdown ---")
regimes = ['Goldilocks', 'Reflation', 'Stagflation', 'Deflation']
results_list = []

for regime in regimes:
    # Filter for specific days
    subset = df[df['Regime'] == regime]
    
    # Calc Metrics for Dynamic
    dyn_res = calculate_metrics(subset['Dynamic_Returns'], subset['Dyn_Excess'])
    dyn_res.name = f'Dynamic ({regime})'
    
    # Calc Metrics for Benchmark
    bench_res = calculate_metrics(subset['60_40_Returns'], subset['60_40_Excess'])
    bench_res.name = f'60/40 ({regime})'
    
    results_list.append(dyn_res)
    results_list.append(bench_res)

regime_df = pd.DataFrame(results_list)
print(regime_df)
'''
# 8. Save Reports
overall_path = os.path.join(results_dir, 'performance_summary_overall.csv')
regime_path = os.path.join(results_dir, 'performance_summary_regimes.csv')

overall_df.to_csv(overall_path)
regime_df.to_csv(regime_path)

print(f"\nReports saved to: {results_dir}")
'''