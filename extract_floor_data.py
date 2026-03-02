"""
Extract floor-level daily and daily+hourly data per building
Adds to viz_data.json: daily_floor_by_building, daily_hourly_floor_by_building
"""
import pandas as pd
import json
import warnings
warnings.filterwarnings('ignore')

print("Loading dataset...")
df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day'] = df['sessionStartDateTime'].dt.day
df['txRxBytes'] = df['txBytes'].fillna(0) + df['rxBytes'].fillna(0)
df['weak'] = df['rssi'] <= -71
# Extract floor number from "FL3" etc, handle non-numeric like "INN"
df['floor_num_str'] = df['Floor'].str.replace('FL', '', regex=False)
df['floor_num'] = pd.to_numeric(df['floor_num_str'], errors='coerce')
nonnumeric = df['floor_num'].isna().sum()
print(f"  Non-numeric floors dropped: {nonnumeric} ({nonnumeric/len(df)*100:.1f}%)")
df = df.dropna(subset=['floor_num'])
df['floor_num'] = df['floor_num'].astype(int)

# Load existing viz_data
with open('output/viz_data.json', 'r', encoding='utf-8') as f:
    viz_data = json.load(f)

# ========== Daily floor-level per building ==========
print("Computing daily floor data per building...")
daily_floor = df.groupby(['Building', 'day', 'floor_num']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    total_MB=('txRxBytes', lambda x: x.sum() / (1024**2)),
    weak_count=('weak', 'sum'),
).reset_index()
daily_floor['weak_pct'] = (daily_floor['weak_count'] / daily_floor['sessions'] * 100).round(1)

daily_floor_json = {}
for _, row in daily_floor.iterrows():
    bldg = row['Building']
    day = int(row['day'])
    fn = int(row['floor_num'])
    if bldg not in daily_floor_json:
        daily_floor_json[bldg] = {}
    key = f"{day}"
    if key not in daily_floor_json[bldg]:
        daily_floor_json[bldg][key] = {}
    daily_floor_json[bldg][key][str(fn)] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
        'total_MB': round(float(row['total_MB']), 1),
        'weak_pct': float(row['weak_pct']),
    }

# ========== Daily+Hourly floor-level per building ==========
print("Computing daily+hourly floor data per building...")
dh_floor = df.groupby(['Building', 'day', 'hour', 'floor_num']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    weak_count=('weak', 'sum'),
).reset_index()
dh_floor['weak_pct'] = (dh_floor['weak_count'] / dh_floor['sessions'] * 100).round(1)

dh_floor_json = {}
for _, row in dh_floor.iterrows():
    bldg = row['Building']
    day = int(row['day'])
    hour = int(row['hour'])
    fn = int(row['floor_num'])
    if bldg not in dh_floor_json:
        dh_floor_json[bldg] = {}
    key = f"{day}_{hour}"
    if key not in dh_floor_json[bldg]:
        dh_floor_json[bldg][key] = {}
    dh_floor_json[bldg][key][str(fn)] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
        'weak_pct': float(row['weak_pct']),
    }

# Update viz_data
viz_data['daily_floor_by_building'] = daily_floor_json
viz_data['daily_hourly_floor_by_building'] = dh_floor_json

# Summary
total_daily_entries = sum(sum(len(floors) for floors in days.values()) for days in daily_floor_json.values())
total_dh_entries = sum(sum(len(floors) for floors in hours.values()) for hours in dh_floor_json.values())
print(f"  Daily floor entries: {total_daily_entries}")
print(f"  Daily+Hourly floor entries: {total_dh_entries}")

# Sample check
print("\nSample B77 day=7:")
b77_d7 = daily_floor_json.get('B77', {}).get('7', {})
for fn in sorted(b77_d7.keys(), key=int):
    d = b77_d7[fn]
    print(f"  FL{fn}: users={d['users']}, sessions={d['sessions']}, rssi={d['avg_rssi']}, weak={d['weak_pct']}%")

print("\nSample B77 day=7 hour=12:")
b77_d7h12 = dh_floor_json.get('B77', {}).get('7_12', {})
for fn in sorted(b77_d7h12.keys(), key=int):
    d = b77_d7h12[fn]
    print(f"  FL{fn}: users={d['users']}, sessions={d['sessions']}, rssi={d['avg_rssi']}, weak={d['weak_pct']}%")

# Save
with open('output/viz_data.json', 'w', encoding='utf-8') as f:
    json.dump(viz_data, f, ensure_ascii=False, indent=2)

# Also copy to public
import shutil
shutil.copy('output/viz_data.json', 'campus-wifi-3d/public/viz_data.json')

print(f"\n[Saved] Updated viz_data.json with floor-level daily/hourly data")
orig_size = len(json.dumps(viz_data, ensure_ascii=False)) / 1024
print(f"  File size: {orig_size:.0f} KB")
print("Done!")
