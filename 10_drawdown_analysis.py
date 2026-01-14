import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.offsetbox import AnchoredText
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

os.makedirs(fig_dir, exist_ok=True)

# 2. Load Data (Updated to use Consolidated File)
print("Loading Data...")
master_df = pd.read_csv(os.path.join(mod_dir, 'consolidated_portfolio_rebased.csv'), 
                        index_col='date', parse_dates=True)

# Prepare DataFrame for Drawdown Analysis
df = pd.DataFrame(index=master_df.index)
df['Dynamic'] = master_df['Dynamic_Equity']
df['60/40']   = master_df['60_40_Equity']
df['Stocks']  = master_df['Stock_Equity']
df['Bonds']   = master_df['Bond_Equity']
df.dropna(inplace=True)

# 3. Calculate Drawdowns
dd = (df / df.cummax()) - 1

# 4. Helper: Calculate Advanced Drawdown Statistics
def get_dd_stats(series):
    is_dd = series < 0
    starts = (~is_dd).shift(1, fill_value=False) & is_dd
    ends = is_dd.shift(1, fill_value=False) & (~is_dd)
    
    start_dates = series.index[starts]
    end_dates = series.index[ends]
    
    if len(start_dates) > len(end_dates):
        end_dates = end_dates.append(pd.Index([series.index[-1]]))
        
    stats = []
    for s, e in zip(start_dates, end_dates):
        window = series.loc[s:e]
        trough_val = window.min()
        duration = (e - s).days
        trough_date = window.idxmin()
        recovery = (e - trough_date).days
        
        stats.append({
            'depth': trough_val,
            'duration': duration,
            'recovery': recovery
        })
        
    if not stats:
        return None
        
    df_stats = pd.DataFrame(stats)
    
    return {
        'avg_dd': df_stats['depth'].mean(),
        'med_dd': df_stats['depth'].median(),
        'max_dd': df_stats['depth'].min(),
        'avg_rec': df_stats['recovery'].mean(),
        'med_rec': df_stats['recovery'].median(),
        'avg_dur': df_stats['duration'].mean(),
        'med_dur': df_stats['duration'].median(),
        'count': len(df_stats)
    }

# 5. Helper: Plotting with Stats Box
def plot_drawdown(ax, series, name, color, stats_loc='lower left'):
    ax.plot(series.index, series, label=name, color=color, linewidth=1.5, alpha=0.9)
    ax.fill_between(series.index, series, 0, color=color, alpha=0.1)
    
    stats = get_dd_stats(series)
    
    if stats:
        text_str = (
            f"Statistics ({name}):\n"
            f"---------------------------\n"
            f"Avg DD: {stats['avg_dd']:.2%}\n"
            f"Median DD: {stats['med_dd']:.2%}\n"
            f"Max DD: {stats['max_dd']:.2%}\n"
            f"---------------------------\n"
            f"Avg Recovery: {stats['avg_rec']:.0f} days\n"
            f"Med Recovery: {stats['med_rec']:.0f} days\n"
            f"---------------------------\n"
            f"Avg Duration: {stats['avg_dur']:.0f} days\n"
            f"Med Duration: {stats['med_dur']:.0f} days\n"
            f"---------------------------\n"
            f"Total Drawdowns: {stats['count']}"
        )
        
        at = AnchoredText(text_str, loc=stats_loc, prop=dict(size=8), frameon=True)
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        at.patch.set_facecolor(color)
        at.patch.set_alpha(0.1)
        ax.add_artist(at)

# ==========================================
# FIGURE 1: Dynamic vs 60/40
# ==========================================
fig1, ax1 = plt.subplots(figsize=(15, 8)) 

plot_drawdown(ax1, dd['Dynamic'], 'Dynamic Strategy', 'purple', 'lower right')
plot_drawdown(ax1, dd['60/40'], '60/40 Benchmark', 'gray', 'lower left')

ax1.set_title('Drawdown Analysis: Strategy vs Benchmark', 
              fontsize=16, fontweight='bold')                    # ← updated
ax1.set_ylabel('Drawdown (%)', 
               fontsize=13, fontweight='bold')                   # ← updated

ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
ax1.xaxis.set_major_locator(mdates.YearLocator(3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right') 

plt.tight_layout()
fig1.savefig(os.path.join(fig_dir, 'drawdown_strategy.png'), dpi=300, bbox_inches='tight')
print("Figure 1 saved.")

# ==========================================
# FIGURE 2: Asset Classes (Stacked)
# ==========================================
fig2, (ax2a, ax2b, ax2c) = plt.subplots(3, 1, figsize=(15, 12), sharex=True)

plot_drawdown(ax2a, dd['Stocks'], 'Stocks (S&P 500)', 'green', 'lower left')
plot_drawdown(ax2b, dd['Bonds'], 'Bonds (10Y Treas)', 'red', 'lower left')
plot_drawdown(ax2c, dd['60/40'], '60/40 Benchmark', 'gray', 'lower left')

ax2a.set_title('Drawdown Analysis: Asset Classes', 
               fontsize=16, fontweight='bold')                    # ← updated

for ax in [ax2a, ax2b, ax2c]:
    ax.set_ylabel('Drawdown (%)', 
                  fontsize=13, fontweight='bold')                 # ← updated
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

ax2c.xaxis.set_major_locator(mdates.YearLocator(3))
ax2c.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

plt.tight_layout()
fig2.savefig(os.path.join(fig_dir, 'drawdown_assets.png'), dpi=300, bbox_inches='tight')
print("Figure 2 saved.")

# ==========================================
# FIGURE 3: Dynamic vs Stocks
# ==========================================
fig3, ax3 = plt.subplots(figsize=(15, 8))

plot_drawdown(ax3, dd['Stocks'], 'Stocks (S&P 500)', 'green', 'lower left')
plot_drawdown(ax3, dd['Dynamic'], 'Dynamic Strategy', 'purple', 'lower right')

ax3.set_title('Drawdown Analysis: Strategy vs Stocks', 
              fontsize=16, fontweight='bold')                    # ← updated
ax3.set_ylabel('Drawdown (%)', 
               fontsize=13, fontweight='bold')                   # ← updated

ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
ax3.xaxis.set_major_locator(mdates.YearLocator(3))
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
ax3.grid(True, alpha=0.3)
ax3.legend(loc='upper right')

plt.tight_layout()
fig3.savefig(os.path.join(fig_dir, 'drawdown_vs_stocks.png'), dpi=300, bbox_inches='tight')
print("Figure 3 saved.")

plt.show()