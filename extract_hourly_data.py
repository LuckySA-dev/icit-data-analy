"""
Extract hourly density data per building+floor for time slider visualization
"""
import pandas as pd
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("Loading dataset...")
df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day_of_week'] = df['sessionStartDateTime'].dt.dayofweek
df['is_weekday'] = df['day_of_week'] < 5

# Load existing viz_data
with open('output/viz_data.json', 'r', encoding='utf-8') as f:
    viz_data = json.load(f)

# === Hourly per building ===
print("Computing hourly building density...")
hourly_bldg = df.groupby(['Building', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    total_MB=('txRxBytes', lambda x: x.sum() / (1024**2)),
).reset_index()

# Normalize: there are 31 days, so divide by 31 for avg per hour
hourly_bldg['avg_sessions_per_day'] = hourly_bldg['sessions'] / 31
hourly_bldg['avg_users_per_day'] = hourly_bldg['unique_users']  # already unique per hour

# === Hourly per building+floor ===
print("Computing hourly building+floor density...")
hourly_bf = df.groupby(['Building', 'Floor', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
).reset_index()
hourly_bf['avg_sessions_per_day'] = hourly_bf['sessions'] / 31

# === Peak hour per building ===
peak_hours = {}
for bldg in hourly_bldg['Building'].unique():
    bldg_data = hourly_bldg[hourly_bldg['Building'] == bldg]
    peak_row = bldg_data.loc[bldg_data['sessions'].idxmax()]
    peak_hours[bldg] = {
        'peak_hour': int(peak_row['hour']),
        'peak_sessions': int(peak_row['sessions']),
        'peak_users': int(peak_row['unique_users']),
    }

# === Build hourly JSON ===
hourly_json = {}
for _, row in hourly_bldg.iterrows():
    bldg = row['Building']
    hour = int(row['hour'])
    if bldg not in hourly_json:
        hourly_json[bldg] = {}
    hourly_json[bldg][hour] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
        'avg_snr': round(float(row['avg_snr']), 1),
        'total_MB': round(float(row['total_MB']), 1),
        'avg_per_day': round(float(row['avg_sessions_per_day']), 1),
    }

# Also do total campus hourly
campus_hourly = df.groupby('hour').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
).reset_index()

campus_hourly_json = {}
for _, row in campus_hourly.iterrows():
    campus_hourly_json[int(row['hour'])] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
        'avg_per_day': round(int(row['sessions']) / 31, 1),
    }

# === Weekday vs Weekend hourly ===
wd_hourly = df[df['is_weekday']].groupby(['Building', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
).reset_index()

we_hourly = df[~df['is_weekday']].groupby(['Building', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
).reset_index()

# Compute max concurrent users per building (for scaling)
max_users_per_bldg = {}
for bldg in hourly_bldg['Building'].unique():
    bldg_data = hourly_bldg[hourly_bldg['Building'] == bldg]
    max_users_per_bldg[bldg] = int(bldg_data['unique_users'].max())

# Update viz_data
viz_data['hourly_by_building'] = hourly_json
viz_data['campus_hourly'] = campus_hourly_json
viz_data['peak_hours'] = peak_hours
viz_data['max_users_per_building'] = max_users_per_bldg

# Overall stats
total_max = campus_hourly['sessions'].max()
total_peak_hour = int(campus_hourly.loc[campus_hourly['sessions'].idxmax(), 'hour'])
print(f"\nCampus peak: Hour {total_peak_hour}:00 with {total_max:,} sessions")

for bldg, info in peak_hours.items():
    print(f"  {bldg}: Peak at {info['peak_hour']}:00 - {info['peak_sessions']:,} sessions, {info['peak_users']:,} users")

# Save
with open('output/viz_data.json', 'w', encoding='utf-8') as f:
    json.dump(viz_data, f, ensure_ascii=False, indent=2)

print(f"\n[Saved] Updated output/viz_data.json with hourly data")
print("Done!")
