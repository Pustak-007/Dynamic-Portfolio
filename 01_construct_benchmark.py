import pandas as pd
import numpy as np
import wrds
from fredapi import Fred
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter, NullLocator
import os

# 1. Directory Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
raw_dir = os.path.join(base_dir, 'raw_data')
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

for path in [raw_dir, mod_dir, fig_dir]:
    os.makedirs(path, exist_ok=True)

print(f"Directories checked/created at: {base_dir}")

# 2. Config & Connections
FRED_API_KEY = '23dd8644a8456a82f3dc0e07c51e2a9b'
START_DATE = '1970-01-01'

db = wrds.Connection()
fred = Fred(api_key=FRED_API_KEY)

# 3. Stocks (CRSP)
print("\nDownloading Stocks (CRSP)...")
stock_query = f"SELECT date, sprtrn FROM crsp.dsi WHERE date >= '{START_DATE}'"
stocks = db.raw_sql(stock_query)
stocks['date'] = pd.to_datetime(stocks['date'])
stocks.set_index('date', inplace=True)
stocks.columns = ['Stock_Returns']
stocks.index.name = 'date'

stocks.to_csv(os.path.join(raw_dir, 'crsp_stocks_raw.csv'))
print("Raw Stock Data saved.")

# 4. Bonds (FRED)
print("\nDownloading Bonds (FRED)...")
yield_series = fred.get_series('DGS10', observation_start=START_DATE)

# Convert Series to DataFrame for clean CSV saving
yield_df = yield_series.to_frame(name='DGS10')
yield_df.index.name = 'date'
yield_df.to_csv(os.path.join(raw_dir, 'fred_bonds_raw.csv'))
print("Raw Bond Data saved.")

# Duration Math
duration = 7.0
daily_yield_decimal = yield_series / 100
daily_income = daily_yield_decimal / 252
yield_change = daily_yield_decimal.diff()

bond_returns = daily_income - (duration * yield_change)
bond_returns.name = 'Bond_Returns'

# 5. Merge & Calculate Benchmark
print("\nMerging and Calculating...")
df = pd.merge(stocks, bond_returns, left_index=True, right_index=True, how='inner')

# Calculate Portfolio Returns
df['60_40_Returns'] = (0.60 * df['Stock_Returns']) + (0.40 * df['Bond_Returns'])

# Calculate Equity Curves (Growth of $1) for ALL components
df['Stock_Equity'] = (1 + df['Stock_Returns']).cumprod()
df['Bond_Equity']  = (1 + df['Bond_Returns']).cumprod()
df['60_40_Equity'] = (1 + df['60_40_Returns']).cumprod()

df.index.name = 'date'

print(df.head(10))

df.to_csv(os.path.join(mod_dir, 'benchmark_portfolio_1970_2025.csv'))
print("Modified Benchmark Data saved.")

# 6. Plotting
fig, ax = plt.subplots(figsize=(15, 8))

ax.plot(df.index, df['60_40_Equity'], label='60/40 Portfolio', linewidth=1.5, color='#1f77b4')
ax.set_yscale('log')

y_ticks = [1, 2, 5, 10, 20, 50, 100]
ax.set_yticks(y_ticks)
ax.get_yaxis().set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_locator(NullLocator())

ax.set_ylabel('Portfolio Value (Growth of $1)', fontsize=12)
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

ax.grid(True, which="major", ls="-", alpha=0.5)
ax.set_title('60/40 Portfolio Performance (1970-Present)', fontsize=14)
ax.legend(loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'benchmark_performance.png'), dpi=300, bbox_inches='tight')
print("Figure saved.")

plt.show()