import json, pandas as pd

# Load viz_data
with open('output/viz_data.json','r',encoding='utf-8') as f:
    vd = json.load(f)

# Load raw dataset for verification
df = pd.read_excel('datasets/wifi-kmutnb-datasets.xlsx')
df['date'] = pd.to_datetime(df['sessionStartDateTime']).dt.date
df['day'] = pd.to_datetime(df['sessionStartDateTime']).dt.day
df['hour'] = pd.to_datetime(df['sessionStartDateTime']).dt.hour
df['RSSI'] = df['rssi']
df['Bytes'] = df['txRxBytes']
df['Floor_num'] = pd.to_numeric(df['Floor'].str.replace('FL',''), errors='coerce')

print('='*60)
print('VERIFY B77 day=9 hour=16 (from screenshot)')
print('='*60)

# Raw data for B77, day 9, hour 16
mask = (df['Building']=='B77') & (df['day']==9) & (df['hour']==16)
raw = df[mask]
print(f"Raw rows: {len(raw)}")
print(f"Raw unique users: {raw['clientMac'].nunique()}")
print(f"Raw avg RSSI: {raw['RSSI'].mean():.1f}")
print()

# Per floor from raw
raw_floor = raw.dropna(subset=['Floor_num'])
for fn in sorted(raw_floor['Floor_num'].unique()):
    fl = raw_floor[raw_floor['Floor_num']==fn]
    print(f"  Floor {int(fn)}: users={fl['clientMac'].nunique()}, sessions={len(fl)}, avg_rssi={fl['RSSI'].mean():.1f}")

print()

# From viz_data
dh = vd['daily_hourly_by_building'].get('B77',{}).get('9_16',{})
print(f"viz_data B77 9_16: {dh}")

dhf = vd.get('daily_hourly_floor_by_building',{}).get('B77',{}).get('9_16',{})
print(f"viz_data floor data 9_16:")
for fn in sorted(dhf.keys(), key=lambda x: int(x)):
    print(f"  Floor {fn}: {dhf[fn]}")

print()
print('='*60)
print('VERIFY BUILDING TOTALS (left sidebar)')
print('='*60)
for code in ['B25','B31','B46','B67','B77','B79']:
    b = next((x for x in vd['buildings'] if x['code']==code), None)
    if b:
        raw_b = df[df['Building']==code]
        raw_users = raw_b['clientMac'].nunique()
        raw_sessions = len(raw_b)
        raw_gb = raw_b['Bytes'].sum() / (1024**3)
        n_floors = len(b['floors'])
        print(f"{code}: viz_users={b['total_users']}, raw_users={raw_users} | "
              f"viz_sessions={b['total_sessions']}, raw_sessions={raw_sessions} | "
              f"viz_GB={b['total_GB']}, raw_GB={raw_gb:.2f} | floors={n_floors}")

print()
print('='*60)
print('VERIFY LEFT SIDEBAR HOURLY (day=9, hour=16)')
print('='*60)
for code in ['B25','B31','B46','B67','B77','B79']:
    dh = vd['daily_hourly_by_building'].get(code,{}).get('9_16',{})
    raw_h = df[(df['Building']==code) & (df['day']==9) & (df['hour']==16)]
    raw_u = raw_h['clientMac'].nunique()
    print(f"{code}: viz_users={dh.get('users','?')} raw_users={raw_u} | "
          f"viz_sessions={dh.get('sessions','?')} raw_sessions={len(raw_h)}")

print()
print('='*60)
print('VERIFY BOTTOM BAR TOTALS (day=9, hour=16)')
print('='*60)
campus_dh = vd.get('daily_hourly_campus',{}).get('9_16',{})
print(f"viz_data campus 9_16: {campus_dh}")
raw_campus = df[(df['day']==9) & (df['hour']==16)]
print(f"raw campus day=9 h=16: users={raw_campus['clientMac'].nunique()}, "
      f"sessions={len(raw_campus)}, avg_rssi={raw_campus['RSSI'].mean():.1f}")

# Also check the sum of per-building users vs campus
sum_bldg_users = sum(
    vd['daily_hourly_by_building'].get(c,{}).get('9_16',{}).get('users',0)
    for c in ['B25','B31','B46','B67','B77','B79']
)
print(f"Sum of building users: {sum_bldg_users}")
print(f"Campus users (viz): {campus_dh.get('users','?')}")
print(f"Note: campus users != sum(building users) because users can be in multiple buildings")

print()
print('='*60)
print('VERIFY FLOOR SUM vs BUILDING TOTAL for B77 day=9 hour=16')
print('='*60)
floor_user_sum = sum(dhf[fn]['users'] for fn in dhf)
floor_session_sum = sum(dhf[fn]['sessions'] for fn in dhf)
bldg_dh = vd['daily_hourly_by_building'].get('B77',{}).get('9_16',{})
print(f"Floor user sum: {floor_user_sum}, Building users: {bldg_dh.get('users','?')}")
print(f"Floor session sum: {floor_session_sum}, Building sessions: {bldg_dh.get('sessions','?')}")
print(f"Note: floor user sum > building users because same user on multiple floors")

# Check if screenshot values match
print()
print('='*60)
print('SCREENSHOT CHECK')
print('='*60)
print("Screenshot shows B77 at 16:00 day 9:")
print(f"  Users: 255 -> viz_data says: {bldg_dh.get('users','?')}")
print(f"  Sessions: 327 -> viz_data says: {bldg_dh.get('sessions','?')}")
print(f"  RSSI: -73.7 -> viz_data says: {bldg_dh.get('avg_rssi','?')}")
print()
print("Floor details from screenshot:")
screenshot_floors = {1: (120, -70.5), 2: (91, -74.2), 3: (51, -76.5), 4: (24, -80.9), 5: (1, -75.4), 6: (17, -79), 7: (25, -68)}
for fn, (users, rssi) in screenshot_floors.items():
    vf = dhf.get(str(fn), {})
    print(f"  F{fn}: screenshot=({users} users, {rssi} dBm) -> viz_data=({vf.get('users','?')} users, {vf.get('avg_rssi','?')} dBm) -> {'MATCH' if vf.get('users')==users else 'MISMATCH'}")
