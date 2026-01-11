import pandas as pd
import numpy as np
from fredapi import Fred
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

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

# 3. Download Commodities (PPI - All Commodities)
print("\nDownloading Commodities Data (PPIACO)...")
commodities = fred.get_series('PPIACO', observation_start=START_DATE)
commodities = commodities.to_frame(name='Commodities_Price')
commodities.index.name = 'date'
commodities.to_csv(os.path.join(raw_dir, 'fred_commodities_raw.csv'))
print("Raw Commodities Data saved.")

# 4. Download Oil (WTI Spot Monthly)
print("\nDownloading Oil Data (WTISPLC)...")
oil = fred.get_series('WTISPLC', observation_start=START_DATE)
oil = oil.to_frame(name='Oil_Price')
oil.index.name = 'date'
oil.to_csv(os.path.join(raw_dir, 'fred_oil_raw.csv'))
print("Raw Oil Data saved.")

# 5. Merge and Resample to Daily
print("\nMerging and Resampling...")
alts = pd.merge(commodities, oil, left_index=True, right_index=True, how='outer')

# Forward fill to simulate daily holding of the physical asset
alts = alts.resample('D').ffill().dropna()
alts.index.name = 'date'

# Inspection & Saving
print(alts.tail(10))
alts.to_csv(os.path.join(mod_dir, 'alternative_assets_1970_2025.csv'))
print("Processed Alternative Assets saved.")

# 6. Visualization (Dual Axis)
fig, ax1 = plt.subplots(figsize=(15, 8))

# Plot Commodities (Left Axis)
ax1.plot(alts.index, alts['Commodities_Price'], color='brown', label='Commodities (PPI)', linewidth=1.5)
ax1.set_ylabel('PPI Commodities Index', color='brown', fontsize=12)
ax1.tick_params(axis='y', labelcolor='brown')

# Plot Oil (Right Axis)
ax2 = ax1.twinx()
ax2.plot(alts.index, alts['Oil_Price'], color='black', label='WTI Oil ($)', linewidth=1.5, linestyle='--')
ax2.set_ylabel('WTI Crude Oil ($)', color='black', fontsize=12)
ax2.tick_params(axis='y', labelcolor='black')

# Formatting
current_year = alts.index[-1].year
ax1.set_title(f'Inflation Hedges: Commodities vs Oil (1970-{current_year})', fontsize=14)

# X-Axis: Every 3 Years
ax1.xaxis.set_major_locator(mdates.YearLocator(3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
fig.autofmt_xdate() # Rotation

ax1.grid(True, alpha=0.3)

# Combined Legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'alternative_assets_history.png'), dpi=300, bbox_inches='tight')
print("Figure saved.")

plt.show()