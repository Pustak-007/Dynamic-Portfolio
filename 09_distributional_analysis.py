import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

os.makedirs(fig_dir, exist_ok=True)

# 2. Load Data
print("Loading Backtest Data...")
dyn_df = pd.read_csv(os.path.join(mod_dir, 'final_backtest_results.csv'), index_col='date', parse_dates=True)
bench_df = pd.read_csv(os.path.join(mod_dir, 'benchmark_portfolio_1970_2025.csv'), index_col='date', parse_dates=True)

# Merge Returns
df = pd.DataFrame(index=dyn_df.index)
df['Dynamic'] = dyn_df['Dynamic_Returns']
df['60/40'] = dyn_df['60_40_Returns']
df['Stocks'] = bench_df['Stock_Returns']
df['Bonds'] = bench_df['Bond_Returns']
df.dropna(inplace=True)

# 3. Stats Function
def get_detailed_stats(returns, name):
    mean = returns.mean() * 252
    std = returns.std() * np.sqrt(252)
    skew = returns.skew()
    kurt = returns.kurt()
    max_ret = returns.max()
    min_ret = returns.min()
    sigma = returns.std()
    prob_neg_2sigma = len(returns[returns < (-2 * sigma)]) / len(returns)
    prob_pos_2sigma = len(returns[returns > (2 * sigma)]) / len(returns)
    
    text = (
        f"{name}\n"
        f"-----------------------\n"
        f"Mean (Ann):  {mean:.2%}\n"
        f"Std (Ann):   {std:.2%}\n"
        f"Min Daily:   {min_ret:.2%}\n"
        f"Max Daily:   {max_ret:.2%}\n"
        f"Skewness:    {skew:.2f}\n"
        f"Exc. Kurt:   {kurt:.2f}\n"
        f"-----------------------\n"
        f"Prob < -2σ:  {prob_neg_2sigma:.2%}\n"
        f"Prob > +2σ:  {prob_pos_2sigma:.2%}"
    )
    return text

# ==========================================
# FIGURE 1: Dynamic vs 60/40 (KDE)
# ==========================================
fig1, ax1 = plt.subplots(figsize=(14, 8))

sns.kdeplot(df['Dynamic'], label='Dynamic Strategy', color='purple', linewidth=2.5, fill=True, alpha=0.1, gridsize=2000, ax=ax1)
sns.kdeplot(df['60/40'], label='60/40 Benchmark', color='gray', linewidth=2, linestyle='--', gridsize=2000, ax=ax1)

text_dyn = get_detailed_stats(df['Dynamic'], "Dynamic Strategy")
text_6040 = get_detailed_stats(df['60/40'], "60/40 Benchmark")

ax1.text(0.02, 0.95, text_dyn, transform=ax1.transAxes, fontsize=9, verticalalignment='top', 
         bbox=dict(boxstyle='round', facecolor='purple', alpha=0.1))
ax1.text(0.98, 0.95, text_6040, transform=ax1.transAxes, fontsize=9, verticalalignment='top', 
         horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='gray', alpha=0.1))

ax1.set_title('Strategy vs Benchmark Distribution', fontsize=14)
ax1.set_xlabel('Daily Return')
ax1.set_xlim(-0.04, 0.04)
ax1.grid(True, alpha=0.3)
ax1.legend()

plt.tight_layout()
fig1_path = os.path.join(fig_dir, 'distribution_strategy.png')
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
print(f"Figure 1 saved to: {fig1_path}")

# ==========================================
# FIGURE 2: Asset Classes (KDE)
# ==========================================
fig2, ax2 = plt.subplots(figsize=(14, 8))

sns.kdeplot(df['Stocks'], label='Stocks (S&P 500)', color='green', linewidth=1.5, gridsize=2000, ax=ax2)
sns.kdeplot(df['Bonds'], label='Bonds (10Y Treas)', color='red', linewidth=1.5, gridsize=2000, ax=ax2)
sns.kdeplot(df['60/40'], label='60/40 Benchmark', color='gray', linewidth=2.5, linestyle='--', gridsize=2000, ax=ax2)

text_stk = get_detailed_stats(df['Stocks'], "Stocks")
text_bnd = get_detailed_stats(df['Bonds'], "Bonds")
text_bm = get_detailed_stats(df['60/40'], "60/40")

ax2.text(0.02, 0.95, text_stk, transform=ax2.transAxes, fontsize=8, verticalalignment='top', 
         bbox=dict(boxstyle='round', facecolor='green', alpha=0.1))
ax2.text(0.02, 0.50, text_bnd, transform=ax2.transAxes, fontsize=8, verticalalignment='top', 
         bbox=dict(boxstyle='round', facecolor='red', alpha=0.1))
ax2.text(0.98, 0.95, text_bm, transform=ax2.transAxes, fontsize=8, verticalalignment='top', 
         horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='gray', alpha=0.1))

ax2.set_title('Asset Class Return Distributions', fontsize=14)
ax2.set_xlabel('Daily Return')
ax2.set_xlim(-0.04, 0.04)
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
fig2_path = os.path.join(fig_dir, 'distribution_assets.png')
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
print(f"Figure 2 saved to: {fig2_path}")

# ==========================================
# FIGURE 3: Q-Q Plots (Strategy vs Benchmark)
# ==========================================
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(16, 7))
fig3.suptitle('Normality Test: Dynamic Strategy vs 60/40', fontsize=16)

# Dynamic
stats.probplot(df['Dynamic'], dist="norm", plot=ax3a)
ax3a.get_lines()[0].set_markerfacecolor('purple')
ax3a.get_lines()[0].set_markeredgecolor('purple')
ax3a.get_lines()[0].set_alpha(0.6)
ax3a.get_lines()[0].set_markersize(2.0)
ax3a.get_lines()[1].set_color('black')
ax3a.set_title("Dynamic Strategy")
ax3a.grid(True, alpha=0.3)

# 60/40
stats.probplot(df['60/40'], dist="norm", plot=ax3b)
ax3b.get_lines()[0].set_markerfacecolor('gray')
ax3b.get_lines()[0].set_markeredgecolor('gray')
ax3b.get_lines()[0].set_alpha(0.6)
ax3b.get_lines()[0].set_markersize(2.0)
ax3b.get_lines()[1].set_color('black')
ax3b.set_title("60/40 Benchmark")
ax3b.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
fig3_path = os.path.join(fig_dir, 'qq_strategy.png')
plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
print(f"Figure 3 saved to: {fig3_path}")

# ==========================================
# FIGURE 4: Q-Q Plots (Stocks vs Bonds)
# ==========================================
fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(16, 7))
fig4.suptitle('Normality Test: Asset Classes', fontsize=16)

# Stocks
stats.probplot(df['Stocks'], dist="norm", plot=ax4a)
ax4a.get_lines()[0].set_markerfacecolor('green')
ax4a.get_lines()[0].set_markeredgecolor('green')
ax4a.get_lines()[0].set_alpha(0.6)
ax4a.get_lines()[0].set_markersize(2.0)
ax4a.get_lines()[1].set_color('black')
ax4a.set_title("Stocks (S&P 500)")
ax4a.grid(True, alpha=0.3)

# Bonds
stats.probplot(df['Bonds'], dist="norm", plot=ax4b)
ax4b.get_lines()[0].set_markerfacecolor('red')
ax4b.get_lines()[0].set_markeredgecolor('red')
ax4b.get_lines()[0].set_alpha(0.6)
ax4b.get_lines()[0].set_markersize(2.0)
ax4b.get_lines()[1].set_color('black')
ax4b.set_title("Bonds (10Y Treas)")
ax4b.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
fig4_path = os.path.join(fig_dir, 'qq_assets.png')
plt.savefig(fig4_path, dpi=300, bbox_inches='tight')
print(f"Figure 4 saved to: {fig4_path}")

plt.show()