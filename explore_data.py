import pandas as pd
import sys

# Read the dataset
print("Loading dataset...")
df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
print(f"Shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nDtypes:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")
print(f"\nInfo:")
df.info()
print(f"\nNull counts:\n{df.isnull().sum()}")
print(f"\nUnique counts:")
for col in df.columns:
    print(f"  {col}: {df[col].nunique()}")
print(f"\nSample values for key columns:")
for col in ['account_type', 'faculty_name', 'ssid', 'BuildingName', 'Floor', 'radioType', 'osType', 'deviceType']:
    if col in df.columns:
        print(f"\n  {col}: {df[col].unique()[:20]}")
print(f"\nSession Start Date Time sample:\n{df['Session Start Date Time'].head(10)}")
print(f"\nRSSI describe:\n{df['rssi'].describe()}")
print(f"\nSNR describe:\n{df['snr'].describe()}")
print(f"\ntxRxbytes describe:\n{df['txRxbytes'].describe()}")
