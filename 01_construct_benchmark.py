import pandas as pd
import numpy as np
import wrds
from fredapi import Fred
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter, NullLocator

# Configuration
FRED_API_KEY = '23dd8644a8456a82f3dc0e07c51e2a9b'
START_DATE = '1970-01-01'

# Connections
db = wrds.Connection()
fred = Fred(api_key=FRED_API_KEY)

# 1. Stock Data
print("Downloading Stocks (CRSP)...")
stock_query = f"SELECT date, sprtrn FROM crsp.dsi WHERE date >= '{START_DATE}'"
stocks = db.raw_sql(stock_query)
stocks['date'] = pd.to_datetime(stocks['date'])
stocks.set_index('date', inplace=True)
stocks.columns = ['Stock_Returns']

# 2. Bond Data
print("Downloading Bonds (FRED)...")
yield_data = fred.get_series('DGS10', observation_start=START_DATE)

duration = 7.0
daily_yield_decimal = yield_data / 100
daily_income = daily_yield_decimal / 252
yield_change = daily_yield_decimal.diff()

bond_returns = daily_income - (duration * yield_change)
bond_returns.name = 'Bond_Returns'

# 3. Merge & Construct
print("Merging and Calculating...")
df = pd.merge(stocks, bond_returns, left_index=True, right_index=True, how='inner')
df['60_40_Returns'] = (0.60 * df['Stock_Returns']) + (0.40 * df['Bond_Returns'])

# Equity Curves
df['60_40_Equity'] = (1 + df['60_40_Returns']).cumprod()

#Print Check
print(df.head(10))

# 4. PLOTTING (Cleaned Ticks)
fig, ax = plt.subplots(figsize=(15, 8))

# Plot
ax.plot(df.index, df['60_40_Equity'], label='60/40 Portfolio', linewidth=1.5, color='#1f77b4')

# Log Scale
ax.set_yscale('log')

# Y-Axis Formatting (Manual & Clean)
y_ticks = [1, 2, 5, 10, 20, 50, 100]
ax.set_yticks(y_ticks)
ax.get_yaxis().set_major_formatter(ScalarFormatter())

# THIS IS THE FIX: Remove the "Unnecessary" minor ticks
ax.yaxis.set_minor_locator(NullLocator())

ax.set_ylabel('Portfolio Value (Growth of $1)', fontsize=12)

# X-Axis Formatting (Every 2 Years)
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

# Grid and Titles
ax.grid(True, which="major", ls="-", alpha=0.5) # Only Major Grid
ax.set_title('60/40 Portfolio Performance (1970-Present)', fontsize=14)
ax.legend(loc='upper left')

plt.tight_layout()
plt.show()

