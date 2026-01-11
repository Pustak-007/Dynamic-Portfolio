import pandas as pd
import numpy as np
from fredapi import Fred
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import os
import pandas as pd
import numpy as np
from fredapi import Fred
import matplotlib.pyplot as plt

# 1. Config & Connections
FRED_API_KEY = '23dd8644a8456a82f3dc0e07c51e2a9b'
START_DATE = '1970-01-01'
fred = Fred(api_key=FRED_API_KEY)

# 2. Download Commodities (PPI - All Commodities)
# Proxy for a broad basket of "Real Assets" (Gold, Oil, Lumber, etc.)
print("\nDownloading Commodities Data (PPIACO)...")
commodities = fred.get_series('PPIACO', observation_start=START_DATE)
commodities = commodities.to_frame(name='Commodities_Price')
commodities.index.name = 'date'

# 3. Download Oil (WTI Spot Monthly)
# Specific Energy Hedge
print("Downloading Oil Data (WTISPLC)...")
oil = fred.get_series('WTISPLC', observation_start=START_DATE)
oil = oil.to_frame(name='Oil_Price')
oil.index.name = 'date'

# 4. Merge and Resample to Daily
# Since these are monthly, we forward fill values to simulate holding the asset
print("Merging and Resampling to Daily...")
alts = pd.merge(commodities, oil, left_index=True, right_index=True, how='outer')

# Resample to Daily and Forward Fill (Holding the physical asset)
alts = alts.resample('D').ffill().dropna()

# 5. Inspection (No Saving)
print("\n--- Alternative Assets Head ---")
print(alts.head(10))
print("\n--- Alternative Assets Tail ---")
print(alts.tail(10))

# 6. Visualization Check
fig, ax = plt.subplots(figsize=(15, 8))
alts.plot(ax=ax, secondary_y='Oil_Price')
ax.set_title('Inflation Hedges: Commodities (PPI) vs Oil (1970-Present)')
ax.set_ylabel('Commodities Index')
ax.right_ax.set_ylabel('Oil Price ($)')
ax.grid(True, alpha=0.3)
plt.show()
# 1. Directory Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
raw_dir = os.path.join(base_dir, 'raw_data')
mod_dir = os.path.join(base_dir, 'modified_data')
fig_dir = os.path.join(base_dir, 'figures')

for path in [raw_dir, mod_dir, fig_dir]:
    os.makedirs(path, exist_ok=True)

print(f"Directories checked: {base_dir}")

# 2. Config & Connections
FRED_API_KEY = '23dd8644a8456a82f3dc0e07c51e2a9b'
START_DATE = '1970-01-01'
fred = Fred(api_key=FRED_API_KEY)

# 3. Download & Save Raw Data (Explicit DF conversion)
print("\nDownloading Macro Data (FRED)...")

# Inflation (CPI)
cpi = fred.get_series('CPIAUCSL', observation_start=START_DATE)
cpi = cpi.to_frame(name='CPI')
cpi.index.name = 'date'
cpi.to_csv(os.path.join(raw_dir, 'fred_cpi_raw.csv'))
print("Raw CPI Data saved.")

# Growth (INDPRO)
indpro = fred.get_series('INDPRO', observation_start=START_DATE)
indpro = indpro.to_frame(name='INDPRO')
indpro.index.name = 'date'
indpro.to_csv(os.path.join(raw_dir, 'fred_indpro_raw.csv'))
print("Raw INDPRO Data saved.")


# 4. Process Signals
macro = pd.merge(cpi, indpro, left_index=True, right_index=True, how='inner')

# Fix: Add fill_method=None to silence the warning
macro['Inflation_YoY'] = macro['CPI'].pct_change(12, fill_method=None)
macro['Growth_YoY']    = macro['INDPRO'].pct_change(12, fill_method=None)

# Trends (3-month smooth)
macro['Inflation_Delta'] = macro['Inflation_YoY'].diff(3)
macro['Growth_Delta']    = macro['Growth_YoY'].diff(3)
macro.dropna(inplace=True)

# 5. Define Regimes
conditions = [
    (macro['Growth_Delta'] > 0) & (macro['Inflation_Delta'] <= 0), # Goldilocks
    (macro['Growth_Delta'] > 0) & (macro['Inflation_Delta'] > 0),  # Reflation
    (macro['Growth_Delta'] <= 0) & (macro['Inflation_Delta'] > 0), # Stagflation
    (macro['Growth_Delta'] <= 0) & (macro['Inflation_Delta'] <= 0) # Deflation
]
choices = ['Goldilocks', 'Reflation', 'Stagflation', 'Deflation']
macro['Regime'] = np.select(conditions, choices, default='Uncertain')

# 6. Inspection & Saving Modified Data
print("\n--- Macro Regimes Tail ---")
print(macro.tail(10))

print("\n--- Regime Counts ---")
print(macro['Regime'].value_counts())

macro.to_csv(os.path.join(mod_dir, 'macro_regimes.csv'))
print("Processed Regime Data saved.")

# 7. Visualization
color_map = {'Goldilocks': 'green', 'Reflation': 'blue', 'Stagflation': 'red', 'Deflation': 'gray'}

fig, ax = plt.subplots(figsize=(15, 6))

ax.plot(macro.index, macro['Inflation_YoY'], color='black', linewidth=1, label='Inflation (CPI YoY)')

for regime_name, color in color_map.items():
    mask = macro['Regime'] == regime_name
    ax.fill_between(macro.index, macro['Inflation_YoY'].min(), macro['Inflation_YoY'].max(), 
                    where=mask, color=color, alpha=0.3, label=regime_name, step='mid')

ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

ax.set_title('US Macroeconomic Regimes (1971-Present)', fontsize=14)
ax.set_ylabel('Inflation Rate (YoY)')
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'macro_regimes_history.png'), dpi=300, bbox_inches='tight')
print("Figure saved.")

plt.show()