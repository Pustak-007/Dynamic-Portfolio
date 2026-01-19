import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, ScalarFormatter
import os

# 1. Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

os.makedirs(fig_dir, exist_ok=True)

# 2. Load Data
print("Loading Consolidated Data...")
macro = pd.read_csv(os.path.join(mod_dir, 'macro_regimes.csv'), index_col='date', parse_dates=True)
portfolio = pd.read_csv(os.path.join(mod_dir, 'consolidated_portfolio_rebased.csv'), index_col='date', parse_dates=True)

# 3. Define Plotting Function
def plot_and_save_period(start_date, end_date, period_name, filename, highlight_period=None):
    # Slice Data
    macro_sub = macro.loc[start_date:end_date]
    port_sub = portfolio.loc[start_date:end_date]
    
    if len(macro_sub) == 0:
        return

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    
    fig.suptitle(f'{period_name}: Macro Signals & Portfolio Response ({start_date[:4]}-{end_date[:4]})', 
                 fontsize=18, fontweight='bold', y=0.96)

    # --- PANEL 1: GROWTH ---
    ax1.plot(macro_sub.index, macro_sub['Growth_YoY'], color='blue', linewidth=2, label='Ind. Production (YoY)')
    ax1.axhline(0, color='black', linestyle='--', linewidth=1)
    ax1.fill_between(macro_sub.index, macro_sub['Growth_YoY'], 0, where=(macro_sub['Growth_YoY'] < 0), 
                    color='gray', alpha=0.2, label='Contraction')
    
    ax1.set_ylabel('Growth Rate (YoY)', fontweight='bold', fontsize=12)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')

    # --- PANEL 2: INFLATION ---
    ax2.plot(macro_sub.index, macro_sub['Inflation_YoY'], color='red', linewidth=2, label='CPI Inflation (YoY)')
    ax2.axhline(0.02, color='green', linestyle='--', linewidth=1, label='Target (2%)')
    ax2.fill_between(macro_sub.index, macro_sub['Inflation_YoY'], 0.04, where=(macro_sub['Inflation_YoY'] > 0.04), 
                    color='red', alpha=0.1, label='High Inflation')
    
    ax2.set_ylabel('Inflation Rate', fontweight='bold', fontsize=12)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right')

    # --- PANEL 3: EQUITY (ALL ASSETS) ---
    # Plot Components (Background)
    ax3.plot(port_sub.index, port_sub['Stock_Equity'], color='green', linewidth=1.5, alpha=0.6, label='Stocks (S&P 500)')
    ax3.plot(port_sub.index, port_sub['Bond_Equity'], color='red', linewidth=1.5, alpha=0.6, label='Bonds (10Y)')
    
    # Plot Strategies (Foreground)
    ax3.plot(port_sub.index, port_sub['60_40_Equity'], color='gray', linewidth=2.0, linestyle='--', label='60/40 Benchmark')
    ax3.plot(port_sub.index, port_sub['Dynamic_Equity'], color='purple', linewidth=2.5, label='Dynamic Strategy')
    
    ax3.set_ylabel('Portfolio Value ($)', fontweight='bold', fontsize=12)
    ax3.yaxis.set_major_formatter(ScalarFormatter())
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', ncol=2)

    # Apply Highlight to ALL Axes
    if highlight_period:
        for ax in [ax1, ax2, ax3]:
            ax.axvspan(pd.Timestamp(highlight_period[0]), pd.Timestamp(highlight_period[1]), 
                        color='orange', alpha=0.25, label='Focus Period')

    # X-Axis Formatting
    ax3.xaxis.set_major_locator(mdates.YearLocator(1))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax3.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
    
    plt.xticks(rotation=45)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_path = os.path.join(fig_dir, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {save_path}")
    
    plt.show()

# 4. Run & Save
# Post-COVID
plot_and_save_period('2020-01-01', '2024-12-31', 'Post-COVID Shock', 'zoom_2020_post_covid.png', 
                     highlight_period=('2022-08-01', '2022-10-01'))

# Post-DotCom
plot_and_save_period('2001-01-01', '2007-12-31', 'Post-DotCom Transition', 'zoom_2001_whipsaw.png',
                     highlight_period=('2002-06-01', '2002-08-01'))