"""
Extract daily + hourly density data per building for time slider
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
df['day'] = df['sessionStartDateTime'].dt.day
df['date'] = df['sessionStartDateTime'].dt.date
df['day_of_week'] = df['sessionStartDateTime'].dt.dayofweek
df['date_str'] = df['sessionStartDateTime'].dt.strftime('%Y-%m-%d')

# Load existing viz_data
with open('output/viz_data.json', 'r', encoding='utf-8') as f:
    viz_data = json.load(f)

# Get date range
dates = sorted(df['date'].unique())
date_range = [d.strftime('%Y-%m-%d') for d in dates]
print(f"Date range: {date_range[0]} to {date_range[-1]} ({len(dates)} days)")

# === Daily data per building ===
print("Computing daily building data...")
daily_bldg = df.groupby(['Building', 'day']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    total_MB=('txRxBytes', lambda x: x.sum() / (1024**2)),
).reset_index()

daily_bldg_json = {}
for _, row in daily_bldg.iterrows():
    bldg = row['Building']
    day = int(row['day'])
    if bldg not in daily_bldg_json:
        daily_bldg_json[bldg] = {}
    daily_bldg_json[bldg][day] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
        'total_MB': round(float(row['total_MB']), 1),
    }

# === Daily+Hourly per building ===
print("Computing daily+hourly building data...")
daily_hourly_bldg = df.groupby(['Building', 'day', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
).reset_index()

daily_hourly_json = {}
for _, row in daily_hourly_bldg.iterrows():
    bldg = row['Building']
    day = int(row['day'])
    hour = int(row['hour'])
    key = f"{day}_{hour}"
    if bldg not in daily_hourly_json:
        daily_hourly_json[bldg] = {}
    daily_hourly_json[bldg][key] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
    }

# === Daily campus total ===
print("Computing daily campus totals...")
daily_campus = df.groupby('day').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
).reset_index()

daily_campus_json = {}
for _, row in daily_campus.iterrows():
    daily_campus_json[int(row['day'])] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
    }

# === Daily+Hourly campus total ===
daily_hourly_campus = df.groupby(['day', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
).reset_index()

daily_hourly_campus_json = {}
for _, row in daily_hourly_campus.iterrows():
    key = f"{int(row['day'])}_{int(row['hour'])}"
    daily_hourly_campus_json[key] = {
        'sessions': int(row['sessions']),
        'users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
    }

# === Day of week mapping ===
dow_map = {}
for d in dates:
    day_num = int(d.strftime('%d'))
    dow = d.weekday()
    dow_names = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์', 'อาทิตย์']
    dow_en = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dow_map[day_num] = {
        'date': d.strftime('%Y-%m-%d'),
        'dow': dow,
        'dow_th': dow_names[dow],
        'dow_en': dow_en[dow],
        'is_weekday': dow < 5,
    }

# Update viz_data
viz_data['daily_by_building'] = daily_bldg_json
viz_data['daily_hourly_by_building'] = daily_hourly_json
viz_data['daily_campus'] = daily_campus_json
viz_data['daily_hourly_campus'] = daily_hourly_campus_json
viz_data['day_info'] = dow_map
viz_data['date_range'] = {
    'start': date_range[0],
    'end': date_range[-1],
    'days': len(dates),
    'start_day': int(date_range[0].split('-')[2]),
    'end_day': int(date_range[-1].split('-')[2]),
}

# Print summary
for day in sorted(daily_campus_json.keys()):
    info = daily_campus_json[day]
    di = dow_map[day]
    marker = '  ' if di['is_weekday'] else '🔴'
    print(f"  {marker} Day {day:2d} ({di['dow_en']}): {info['sessions']:>6,} sessions, {info['users']:>5,} users, RSSI {info['avg_rssi']:.1f}")

# Save
with open('output/viz_data.json', 'w', encoding='utf-8') as f:
    json.dump(viz_data, f, ensure_ascii=False, indent=2)

print(f"\n[Saved] Updated output/viz_data.json with daily data ({len(dates)} days)")
print("Done!")
