import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import ScalarFormatter, FuncFormatter
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
res_dir = os.path.join(base_dir, 'results')
fig_dir = os.path.join(base_dir, 'figures')

# 2. Load Data (Consolidated)
print("Loading Consolidated Data for Dashboard...")
df = pd.read_csv(os.path.join(mod_dir, 'consolidated_portfolio_rebased.csv'), index_col='date', parse_dates=True)

# Load Stats
metrics = pd.read_csv(os.path.join(res_dir, 'metrics_overall_comprehensive.csv'), index_col=0)
turnover = pd.read_csv(os.path.join(res_dir, 'turnover_stats.csv'), index_col=0, header=None)

# 3. Data Prep
# Drawdowns
equity_df = df[['Dynamic_Equity', '60_40_Equity']].copy()
equity_df.columns = ['Dynamic', 'Benchmark']
dd = (equity_df / equity_df.cummax()) - 1

# Rolling Correlation Prep
# Using the returns from the consolidated file ensures perfect alignment
rolling_corr = df['Stock_Returns'].rolling(504, min_periods=100).corr(df['Bond_Returns']).dropna()
regime_daily = df[['Regime']].reindex(rolling_corr.index, method='ffill')

# 4. Dashboard Construction
fig = plt.figure(figsize=(20, 14))
gs = gridspec.GridSpec(3, 2, height_ratios=[2, 1.5, 1])

end_year = df.index[-1].year
fig.suptitle(f'Dynamic Regime-Based Asset Allocation: Executive Summary (1971-{end_year})', fontsize=20, y=0.95)

# --- CHART 1: EQUITY CURVE (Top Spanning) ---
ax1 = plt.subplot(gs[0, :])
ax1.plot(equity_df.index, equity_df['Dynamic'], color='purple', linewidth=2, label='Dynamic Strategy')
ax1.plot(equity_df.index, equity_df['Benchmark'], color='gray', linewidth=1.5, linestyle='--', label='60/40 Benchmark')
ax1.set_yscale('log')
ax1.set_ylabel('Growth of $1 (Log)')
ax1.set_title('Cumulative Performance', fontsize=12, loc='left')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(ScalarFormatter())

# --- CHART 2: DRAWDOWN (Middle Left) ---
ax2 = plt.subplot(gs[1, 0])
ax2.plot(dd.index, dd['Dynamic'], color='purple', linewidth=1, label='Dynamic')
ax2.fill_between(dd.index, dd['Dynamic'], 0, color='purple', alpha=0.2)
ax2.plot(dd.index, dd['Benchmark'], color='gray', linewidth=1, alpha=0.6, label='60/40')
ax2.set_title('Drawdown Profile', fontsize=12, loc='left')
ax2.set_ylabel('Drawdown %')
ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
ax2.grid(True, alpha=0.3)
ax2.legend(loc='lower left')

# --- CHART 3: CORRELATION & REGIMES (Middle Right) ---
ax3 = plt.subplot(gs[1, 1])
ax3.plot(rolling_corr.index, rolling_corr, color='black', linewidth=1)
ax3.axhline(0, color='red', linestyle='--', linewidth=0.8)
ax3.set_title('Stock-Bond Correlation (Regime Dependent)', fontsize=12, loc='left')
ax3.set_ylabel('24M Rolling Corr')
ax3.set_ylim(-1, 1)

# Simple Regime Shading (Stagflation Only)
mask = regime_daily['Regime'] == 'Stagflation'
if mask.any():
    ax3.fill_between(rolling_corr.index, -1, 1, where=mask, color='red', alpha=0.15, label='Stagflation')
ax3.legend(loc='upper right')
ax3.grid(True, alpha=0.3)

# --- TABLE 4: METRICS (Bottom) ---
ax4 = plt.subplot(gs[2, :])
ax4.axis('off')

# Select Rows (Dynamic vs 60/40)
stats_table = metrics.loc[['Dynamic', '60/40']].copy()

# Add Turnover info
try:
    ann_turnover = float(turnover.loc['Avg Switches Per Year'].iloc[0])
    net_cagr = turnover.loc['Net CAGR (After Cost)'].iloc[0]
except:
    ann_turnover = 0.0
    net_cagr = "N/A"

stats_table['Annual Turnover'] = [f"{ann_turnover:.2f}x", "0.00x"]
stats_table['Net CAGR'] = [net_cagr, stats_table['Return (Ann)'].iloc[1]]

# Format Table Text
cell_text = []
for row in range(len(stats_table)):
    formatted_row = []
    for val in stats_table.iloc[row]:
        if isinstance(val, (int, float)):
            formatted_row.append(f"{val:.2%}")
        else:
            formatted_row.append(str(val))
    cell_text.append(formatted_row)

table = ax4.table(cellText=cell_text, colLabels=stats_table.columns, rowLabels=stats_table.index, 
                  loc='center', cellLoc='center', colColours=['#f2f2f2']*len(stats_table.columns))
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 2)

plt.tight_layout(rect=[0, 0, 1, 0.95])
save_path = os.path.join(fig_dir, 'executive_dashboard.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Executive Dashboard saved to: {save_path}")

plt.show()