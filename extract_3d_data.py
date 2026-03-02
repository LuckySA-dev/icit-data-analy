"""
Extract data for 3D visualization and deeper insights
Maps building codes to campus positions based on the map
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
df['txRxBytes_MB'] = df['txRxBytes'] / (1024*1024)

def classify_rssi(rssi):
    if rssi >= -50: return 'Excellent'
    elif rssi >= -60: return 'Very Good'
    elif rssi >= -67: return 'Good'
    elif rssi >= -70: return 'Fair'
    elif rssi >= -80: return 'Weak'
    else: return 'Very Poor'

# === Building mapping from campus map ===
# From the map images, building positions (approximate relative coordinates)
building_info = {
    'B25': {'name': 'อาคารอเนกประสงค์', 'name_en': 'Multipurpose Building', 'number': 25},
    'B77': {'name': 'อาคาร 40 ปี มจพ. และโรงอาหารกลาง', 'name_en': '40th Anniversary & Canteen', 'number': 77},
    'B67': {'name': 'อาคารวิทยาลัยเทคโนโลยีอุตสาหกรรม', 'name_en': 'College of Industrial Technology', 'number': 67},
    'B23': {'name': 'อาคารนวมินทรราชินี', 'name_en': 'Navamindrarachinee Building', 'number': 23},
    'B46': {'name': 'อาคารคณะศิลปศาสตร์ประยุกต์และโรงอาหาร', 'name_en': 'Applied Arts & Cafeteria', 'number': 46},
    'B79': {'name': 'อาคารสโมสรบุคลากร มจพ.', 'name_en': 'Staff Club', 'number': 79},
}

# === Extract building-floor level data ===
print("\n--- Building-Floor Data Extraction ---")
bldg_floor_data = df.groupby(['Building', 'BuildingName', 'Floor']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    unique_aps=('apName', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    median_rssi=('rssi', 'median'),
    min_rssi=('rssi', 'min'),
    max_rssi=('rssi', 'max'),
    avg_snr=('snr', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    weak_count=('rssi', lambda x: (x <= -71).sum()),
    poor_count=('rssi', lambda x: (x < -80).sum()),
    zero_data=('txRxBytes', lambda x: (x == 0).sum()),
    avg_data_MB=('txRxBytes_MB', 'mean'),
).reset_index()

bldg_floor_data['weak_pct'] = bldg_floor_data['weak_count'] / bldg_floor_data['sessions'] * 100
bldg_floor_data['poor_pct'] = bldg_floor_data['poor_count'] / bldg_floor_data['sessions'] * 100
bldg_floor_data['zero_pct'] = bldg_floor_data['zero_data'] / bldg_floor_data['sessions'] * 100

# Floor number extraction
def floor_num(f):
    if f == 'FLINN': return 0  # ground/innovation floor
    return int(f.replace('FL', ''))

bldg_floor_data['floor_num'] = bldg_floor_data['Floor'].apply(floor_num)

# === Extract AP-level data with building-floor mapping ===
ap_data = df.groupby(['apName', 'Building', 'BuildingName', 'Floor']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    weak_pct=('rssi', lambda x: (x <= -71).sum() / len(x) * 100),
).reset_index()

# === Hourly patterns per building ===
bldg_hourly = df.groupby(['Building', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
).reset_index()

# === Build JSON for 3D visualization ===
print("\n--- Building JSON for 3D Visualization ---")
buildings_3d = []

for bldg_code in sorted(bldg_floor_data['Building'].unique()):
    bldg_info = building_info.get(bldg_code, {'name': bldg_code, 'name_en': bldg_code, 'number': 0})
    bldg_df = bldg_floor_data[bldg_floor_data['Building'] == bldg_code].sort_values('floor_num')
    
    floors = []
    for _, row in bldg_df.iterrows():
        floors.append({
            'floor': row['Floor'],
            'floor_num': int(row['floor_num']),
            'sessions': int(row['sessions']),
            'unique_users': int(row['unique_users']),
            'unique_aps': int(row['unique_aps']),
            'avg_rssi': round(float(row['avg_rssi']), 1),
            'avg_snr': round(float(row['avg_snr']), 1),
            'total_GB': round(float(row['total_GB']), 2),
            'weak_pct': round(float(row['weak_pct']), 1),
            'poor_pct': round(float(row['poor_pct']), 1),
            'zero_pct': round(float(row['zero_pct']), 1),
            'avg_data_MB': round(float(row['avg_data_MB']), 2),
            'quality': classify_rssi(row['avg_rssi']),
        })
    
    # Building-level totals
    total_sessions = bldg_df['sessions'].sum()
    total_users = df[df['Building'] == bldg_code]['Username'].nunique()
    
    buildings_3d.append({
        'code': bldg_code,
        'name': bldg_info['name'],
        'name_en': bldg_info['name_en'],
        'number': bldg_info['number'],
        'total_sessions': int(total_sessions),
        'total_users': int(total_users),
        'total_GB': round(float(bldg_df['total_GB'].sum()), 2),
        'avg_rssi': round(float(df[df['Building'] == bldg_code]['rssi'].mean()), 1),
        'avg_snr': round(float(df[df['Building'] == bldg_code]['snr'].mean()), 1),
        'overall_weak_pct': round(float(bldg_df['weak_count'].sum() / total_sessions * 100), 1),
        'floor_count': len(floors),
        'max_floor': int(bldg_df['floor_num'].max()),
        'floors': floors,
    })
    
    print(f"\n{bldg_code} - {bldg_info['name_en']}:")
    print(f"  Total: {total_sessions:,} sessions, {total_users:,} users, {bldg_df['total_GB'].sum():.1f} GB")
    print(f"  Floors: {len(floors)} ({bldg_df['floor_num'].min()} to {bldg_df['floor_num'].max()})")
    print(f"  Avg RSSI: {df[df['Building'] == bldg_code]['rssi'].mean():.1f}, Weak%: {bldg_df['weak_count'].sum()/total_sessions*100:.1f}%")
    for f in floors:
        icon = "🔴" if f['weak_pct'] > 70 else "🟡" if f['weak_pct'] > 50 else "🟢"
        print(f"    {icon} {f['floor']}: RSSI={f['avg_rssi']}, Weak={f['weak_pct']}%, "
              f"Users={f['unique_users']}, APs={f['unique_aps']}, Data={f['total_GB']}GB")

# === AP-level detail for 3D (dots on floors) ===
aps_3d = []
for _, row in ap_data.iterrows():
    aps_3d.append({
        'name': row['apName'],
        'building': row['Building'],
        'floor': row['Floor'],
        'floor_num': floor_num(row['Floor']),
        'sessions': int(row['sessions']),
        'unique_users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
        'avg_snr': round(float(row['avg_snr']), 1),
        'total_GB': round(float(row['total_GB']), 2),
        'weak_pct': round(float(row['weak_pct']), 1),
        'quality': classify_rssi(row['avg_rssi']),
    })

# === Hourly data for animation ===
hourly_3d = []
for _, row in bldg_hourly.iterrows():
    hourly_3d.append({
        'building': row['Building'],
        'hour': int(row['hour']),
        'sessions': int(row['sessions']),
        'unique_users': int(row['unique_users']),
        'avg_rssi': round(float(row['avg_rssi']), 1),
    })

# === DEEPER INSIGHTS ===
print("\n" + "=" * 70)
print("DEEPER INSIGHTS")
print("=" * 70)

# Insight: Correlation between user density and signal degradation
print("\n--- Signal Degradation under Load ---")
for bldg_code in sorted(df['Building'].unique()):
    bldg = df[df['Building'] == bldg_code]
    # Compare peak vs off-peak
    peak = bldg[bldg['hour'].between(10, 14)]
    offpeak = bldg[~bldg['hour'].between(10, 14)]
    if len(peak) > 0 and len(offpeak) > 0:
        delta = peak['rssi'].mean() - offpeak['rssi'].mean()
        print(f"  {bldg_code}: Peak RSSI={peak['rssi'].mean():.1f}, OffPeak={offpeak['rssi'].mean():.1f}, "
              f"Delta={delta:+.1f} dBm, Peak Users/hr={peak.groupby('hour')['Username'].nunique().mean():.0f}")

# Insight: AP that needs splitting (too many users)
print("\n--- APs Needing Splitting (>500 unique users) ---")
hot_aps = ap_data[ap_data['unique_users'] > 500].sort_values('unique_users', ascending=False)
for _, row in hot_aps.iterrows():
    print(f"  {row['apName']} ({row['Building']}-{row['Floor']}): "
          f"{row['unique_users']} users, RSSI={row['avg_rssi']}, {row['total_GB']:.1f} GB")

# Insight: Floor-to-floor signal comparison within each building
print("\n--- Floor Signal Spread (within each building) ---")
for bldg_code in sorted(bldg_floor_data['Building'].unique()):
    bldg = bldg_floor_data[bldg_floor_data['Building'] == bldg_code]
    if len(bldg) > 1:
        best = bldg.loc[bldg['avg_rssi'].idxmax()]
        worst = bldg.loc[bldg['avg_rssi'].idxmin()]
        spread = best['avg_rssi'] - worst['avg_rssi']
        print(f"  {bldg_code}: Best={best['Floor']}({best['avg_rssi']:.1f}), "
              f"Worst={worst['Floor']}({worst['avg_rssi']:.1f}), Spread={spread:.1f} dBm")

# Insight: eduroam vs @KMUTNB per building
print("\n--- SSID Performance by Building ---")
ssid_bldg = df.groupby(['Building', 'ssid']).agg(
    sessions=('id', 'count'),
    avg_rssi=('rssi', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean')
).reset_index()
for bldg in sorted(ssid_bldg['Building'].unique()):
    subset = ssid_bldg[ssid_bldg['Building'] == bldg]
    print(f"  {bldg}:")
    for _, row in subset.iterrows():
        print(f"    {row['ssid']:10s}: {row['sessions']:>6,} sessions, RSSI={row['avg_rssi']:.1f}, Avg Data={row['avg_data_MB']:.1f}MB")

# Insight: Device type impact per building
print("\n--- Device Type Distribution by Building ---")
dev_bldg = df.groupby(['Building', 'deviceType']).size().unstack(fill_value=0)
dev_bldg_pct = dev_bldg.div(dev_bldg.sum(axis=1), axis=0) * 100
print(dev_bldg_pct.round(1).to_string())

# Insight: Connection failure by building
print("\n--- Zero-Data Sessions by Building ---")
zero_bldg = df.groupby('Building').apply(lambda x: pd.Series({
    'total': len(x),
    'zero': (x['txRxBytes'] == 0).sum(),
    'zero_pct': (x['txRxBytes'] == 0).sum() / len(x) * 100,
    'low_1kb': (x['txRxBytes'] < 1024).sum(),
    'low_pct': (x['txRxBytes'] < 1024).sum() / len(x) * 100,
}))
print(zero_bldg.to_string())

# Save data for 3D viz
viz_data = {
    'buildings': buildings_3d,
    'aps': aps_3d,
    'hourly': hourly_3d,
    'summary': {
        'total_sessions': int(len(df)),
        'total_users': int(df['Username'].nunique()),
        'total_aps': int(df['apName'].nunique()),
        'total_GB': round(float(df['txRxBytes'].sum() / (1024**3)), 1),
        'avg_rssi': round(float(df['rssi'].mean()), 1),
        'avg_snr': round(float(df['snr'].mean()), 1),
        'weak_pct': round(float((df['rssi'] <= -71).sum() / len(df) * 100), 1),
        'date_range': f"{df['sessionStartDateTime'].min().strftime('%Y-%m-%d')} ~ {df['sessionStartDateTime'].max().strftime('%Y-%m-%d')}",
    }
}

with open('output/viz_data.json', 'w', encoding='utf-8') as f:
    json.dump(viz_data, f, ensure_ascii=False, indent=2)

print(f"\n[Saved] output/viz_data.json ({len(buildings_3d)} buildings, {len(aps_3d)} APs)")
print("Done!")
