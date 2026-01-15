import pandas as pd
import numpy as np
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
results_dir = os.path.join(base_dir, 'results')

os.makedirs(results_dir, exist_ok=True)

# 2. Load Data (Simplified)
print("Loading Master Dataset...")
# We now load only the Consolidated file (which has Stocks, Bonds, Dynamic, 60/40, and Regimes)
df = pd.read_csv(os.path.join(mod_dir, 'consolidated_portfolio_rebased.csv'), index_col='date', parse_dates=True)

# Load Risk-Free Rate
rf_df = pd.read_csv(os.path.join(mod_dir, 'risk_free_daily.csv'), index_col='date', parse_dates=True)

# Merge Risk-Free Rate into Master DF
df = df.join(rf_df, how='left').ffill().dropna()

# 3. Calculate Excess Returns (Strategy - Rf)
strategies = {
    'Dynamic': 'Dynamic_Returns',
    '60/40': '60_40_Returns',
    'Stocks': 'Stock_Returns',
    'Bonds': 'Bond_Returns'
}

for name, col in strategies.items():
    df[f'{name}_Excess'] = df[col] - df['Risk_Free_Return']

# 4. Define Smart Metric Engine
def calculate_metrics(returns, excess_returns, is_continuous=False):
    if len(returns) < 2:
        return pd.Series([0,0,0,0,0], index=['Return (Ann)', 'Volatility', 'Sharpe', 'Sortino', 'Max DD'])
    
    # Return Calculation
    if is_continuous:
        # CAGR (Geometric) for Overall
        total_ret = (1 + returns).prod()
        n_years = len(returns) / 252
        ann_return = (total_ret ** (1 / n_years)) - 1
    else:
        # Arithmetic Mean for Regimes (Run Rate)
        ann_return = returns.mean() * 252
    
    # Volatility
    vol = returns.std() * np.sqrt(252)
    
    # Sharpe
    sharpe = (excess_returns.mean() * 252) / (excess_returns.std() * np.sqrt(252) + 1e-9)
    
    # Sortino
    downside = returns[returns < 0]
    downside_vol = downside.std() * np.sqrt(252)
    sortino = (excess_returns.mean() * 252) / (downside_vol + 1e-9)
    
    # Max DD
    cum = (1 + returns).cumprod()
    dd = (cum - cum.cummax()) / cum.cummax()
    max_dd = dd.min()
    
    return pd.Series([ann_return, vol, sharpe, sortino, max_dd], 
                     index=['Return (Ann)', 'Volatility', 'Sharpe', 'Sortino', 'Max DD'])

# 5. Calculate OVERALL Metrics (Continuous = True)
print("\n--- Overall Performance (1971-2024) ---")
overall_results = {}
for name, col in strategies.items():
    overall_results[name] = calculate_metrics(df[col], df[f'{name}_Excess'], is_continuous=True)

overall_df = pd.DataFrame(overall_results).T
print(overall_df)

# 6. Calculate REGIME Metrics (Continuous = False)
print("\n--- Performance by Macro Regime ---")
regime_data = {}

for regime in ['Goldilocks', 'Reflation', 'Stagflation', 'Deflation']:
    subset = df[df['Regime'] == regime]
    regime_results = {}
    
    for name, col in strategies.items():
        stats = calculate_metrics(subset[col], subset[f'{name}_Excess'], is_continuous=False)
        regime_results[name] = stats
    
    # Create a DataFrame for this regime and add to list
    regime_df = pd.DataFrame(regime_results).T
    print(f"\n[{regime} Stats]")
    print(regime_df)
    regime_data[regime] = regime_df

# 7. Save Reports
'''
overall_df.to_csv(os.path.join(results_dir, 'metrics_overall_comprehensive2.csv'))
combined_regime_df = pd.concat(regime_data, axis=0)
combined_regime_df.to_csv(os.path.join(results_dir, 'metrics_regime_comprehensive2.csv'))
'''
print(f"\nComprehensive Reports saved to: {results_dir}")