import pandas as pd
import numpy as np
from fredapi import Fred
import os

# 1. Directory Setup
base_dir = '/Users/pustak/Desktop/Dynamic Portfolio'
raw_dir = os.path.join(base_dir, 'raw_data')
mod_dir = os.path.join(base_dir, 'modified_data')

for path in [raw_dir, mod_dir]:
    os.makedirs(path, exist_ok=True)

# 2. Config & Connections
FRED_API_KEY = '23dd8644a8456a82f3dc0e07c51e2a9b'
START_DATE = '1970-01-01'
fred = Fred(api_key=FRED_API_KEY)

# 3. Download Risk-Free Rate (DTB3)
print("\nDownloading Risk-Free Rate (DTB3) from FRED...")
rf_series = fred.get_series('DTB3', observation_start=START_DATE)

# Save Raw Data
rf_df = rf_series.to_frame(name='DTB3')
rf_df.index.name = 'date'
rf_df.to_csv(os.path.join(raw_dir, 'fred_rf_raw.csv'))
print("Raw Risk-Free Yields saved.")

# 4. Geometric Conversion (The Rigorous Method)
# Formula: Daily_Return = (1 + Annual_Yield)^(1/252) - 1
# Input 'DTB3' is percent (e.g. 5.0), so we divide by 100 first.

rf_decimal = rf_series / 100
rf_daily = np.power(1 + rf_decimal, 1/252) - 1

rf_daily = rf_daily.to_frame(name='Risk_Free_Return')
rf_daily.index.name = 'date'

# Inspection
print("\n--- Risk Free Return Head (Geometric) ---")
print(rf_daily.head())

# Save Processed Data
rf_daily.to_csv(os.path.join(mod_dir, 'risk_free_daily.csv'))
print("Processed Daily Risk-Free Returns saved.")