import pandas as pd

df = pd.read_excel('datasets/wifi-kmutnb-datasets.xlsx')
df['day'] = pd.to_datetime(df['sessionStartDateTime']).dt.day
df['hour'] = pd.to_datetime(df['sessionStartDateTime']).dt.hour

# Check how users might differ
b77 = df[df['Building']=='B77']
print("B77 total:")
print(f"  clientMac unique: {b77['clientMac'].nunique()}")
print(f"  Username unique: {b77['Username'].nunique()}")
print(f"  sessions (rows): {len(b77)}")

# Check hourly
b77_9_16 = b77[(b77['day']==9) & (b77['hour']==16)]
print(f"B77 day=9 h=16:")
print(f"  clientMac unique: {b77_9_16['clientMac'].nunique()}")
print(f"  Username unique: {b77_9_16['Username'].nunique()}")

print(f"  Has NaN clientMac: {b77['clientMac'].isna().sum()}")
print(f"  Has NaN Username: {b77['Username'].isna().sum()}")

print()
print("ALL BUILDINGS - clientMac vs Username nunique:")
for code in ['B25','B31','B46','B67','B77','B79']:
    bb = df[df['Building']==code]
    print(f"  {code}: clientMac={bb['clientMac'].nunique()}, Username={bb['Username'].nunique()}")
