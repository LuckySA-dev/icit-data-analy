"""
Final Comprehensive Analysis - ICIT Data Insight & Analytics 2026
KMUTNB WiFi Dataset: 189,445 sessions, Jan 1-31, 2026
"""
import pandas as pd
import numpy as np
from collections import Counter

df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day'] = df['sessionStartDateTime'].dt.day
df['weekday'] = df['sessionStartDateTime'].dt.dayofweek  # 0=Mon
df['weekday_name'] = df['sessionStartDateTime'].dt.day_name()
df['is_weekend'] = df['weekday'] >= 5

def rssi_level(r):
    if r >= -50: return 'Excellent'
    elif r >= -60: return 'Very Good'
    elif r >= -67: return 'Good'
    elif r >= -70: return 'Fair'
    elif r >= -80: return 'Weak'
    else: return 'Very Poor'

df['rssi_level'] = df['rssi'].apply(rssi_level)
df['is_weak'] = df['rssi'] < -70
df['is_vpoor'] = df['rssi'] < -80
df['is_wifi6'] = df['radioType'].str.contains('ax', case=False, na=False)

total = len(df)
print("=" * 80)
print("PART 1: OVERALL SIGNAL QUALITY ANALYSIS")
print("=" * 80)

# RSSI distribution
for lv in ['Excellent', 'Very Good', 'Good', 'Fair', 'Weak', 'Very Poor']:
    c = (df['rssi_level'] == lv).sum()
    print(f"  {lv}: {c:,} ({c/total*100:.1f}%)")

weak_total = df['is_weak'].sum()
vpoor_total = df['is_vpoor'].sum()
print(f"\n  Weak+VeryPoor combined: {weak_total:,} ({weak_total/total*100:.1f}%)")
print(f"  VeryPoor alone: {vpoor_total:,} ({vpoor_total/total*100:.1f}%)")

# SNR analysis
snr_low = (df['snr'] < 10).sum()
snr_vlow = (df['snr'] < 5).sum()
print(f"\n  SNR < 10 dB (high interference): {snr_low:,} ({snr_low/total*100:.1f}%)")
print(f"  SNR < 5 dB (critical interference): {snr_vlow:,} ({snr_vlow/total*100:.1f}%)")
print(f"  Avg RSSI: {df['rssi'].mean():.1f} dBm, Median: {df['rssi'].median():.1f} dBm")
print(f"  Avg SNR: {df['snr'].mean():.1f} dB, Median: {df['snr'].median():.1f} dB")

print("\n" + "=" * 80)
print("PART 2: BUILDING-LEVEL ANALYSIS")
print("=" * 80)

for bldg in sorted(df['Building'].unique()):
    bdf = df[df['Building'] == bldg]
    bname = bdf['BuildingName'].iloc[0] if len(bdf) > 0 else ''
    users = bdf['Username'].nunique()
    sessions = len(bdf)
    avg_rssi = bdf['rssi'].mean()
    avg_snr = bdf['snr'].mean()
    weak_pct = bdf['is_weak'].mean() * 100
    vpoor_pct = bdf['is_vpoor'].mean() * 100
    wifi6_pct = bdf['is_wifi6'].mean() * 100
    aps = bdf['apName'].nunique()
    floors = bdf['Floor'].nunique()
    data_gb = bdf['txRxBytes'].sum() / (1024**3)
    
    print(f"\n  {bldg} ({bname})")
    print(f"    Sessions: {sessions:,} | Users: {users:,} | APs: {aps} | Floors: {floors}")
    print(f"    Avg RSSI: {avg_rssi:.1f} dBm | Avg SNR: {avg_snr:.1f} dB")
    print(f"    Weak: {weak_pct:.1f}% | VeryPoor: {vpoor_pct:.1f}%")
    print(f"    WiFi6: {wifi6_pct:.1f}% | Data: {data_gb:.1f} GB")

print("\n" + "=" * 80)
print("PART 3: FLOOR-LEVEL CRITICAL ZONES")
print("=" * 80)

floor_stats = df.groupby(['Building', 'Floor']).agg(
    sessions=('id', 'count'),
    users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    weak_pct=('is_weak', 'mean'),
    vpoor_pct=('is_vpoor', 'mean'),
    aps=('apName', 'nunique'),
    data_gb=('txRxBytes', lambda x: x.sum()/(1024**3))
).reset_index()

floor_stats['weak_pct'] *= 100
floor_stats['vpoor_pct'] *= 100

# Top 10 worst floors by weak%
print("\n  TOP 10 WORST FLOORS (by weak signal %):")
worst = floor_stats.nlargest(10, 'weak_pct')
for _, r in worst.iterrows():
    print(f"    {r['Building']}-{r['Floor']}: {r['weak_pct']:.1f}% weak, {r['vpoor_pct']:.1f}% very poor | RSSI={r['avg_rssi']:.1f} | SNR={r['avg_snr']:.1f} | {r['sessions']:,} sessions | {r['aps']} APs")

# Top 10 busiest floors
print("\n  TOP 10 BUSIEST FLOORS (by sessions):")
busiest = floor_stats.nlargest(10, 'sessions')
for _, r in busiest.iterrows():
    print(f"    {r['Building']}-{r['Floor']}: {r['sessions']:,} sessions, {r['users']:,} users | RSSI={r['avg_rssi']:.1f} | weak={r['weak_pct']:.1f}% | {r['aps']} APs")

# Users per AP ratio
floor_stats['users_per_ap'] = floor_stats['users'] / floor_stats['aps']
floor_stats['sessions_per_ap'] = floor_stats['sessions'] / floor_stats['aps']
print("\n  TOP 10 OVERLOADED FLOORS (sessions per AP):")
overloaded = floor_stats.nlargest(10, 'sessions_per_ap')
for _, r in overloaded.iterrows():
    print(f"    {r['Building']}-{r['Floor']}: {r['sessions_per_ap']:.0f} sessions/AP ({r['sessions']:,} sessions, {r['aps']} APs) | weak={r['weak_pct']:.1f}%")

print("\n" + "=" * 80)
print("PART 4: TIME PATTERNS")
print("=" * 80)

# Hourly pattern
print("\n  HOURLY SESSIONS:")
hourly = df.groupby('hour').agg(sessions=('id','count'), users=('Username','nunique'), avg_rssi=('rssi','mean')).reset_index()
for _, r in hourly.iterrows():
    bar = '█' * int(r['sessions'] / 500)
    print(f"    {int(r['hour']):02d}:00  {r['sessions']:>6,} sessions  {r['users']:>5,} users  RSSI={r['avg_rssi']:.1f}  {bar}")

# Peak hours vs off-peak signal quality
peak_hours = [9, 10, 11, 12, 13, 14, 15, 16]
off_peak_hours = [0, 1, 2, 3, 4, 5, 6, 22, 23]

peak_df = df[df['hour'].isin(peak_hours)]
offpeak_df = df[df['hour'].isin(off_peak_hours)]

print(f"\n  PEAK (9-16h): {len(peak_df):,} sessions, RSSI={peak_df['rssi'].mean():.1f}, SNR={peak_df['snr'].mean():.1f}, Weak={peak_df['is_weak'].mean()*100:.1f}%")
print(f"  OFF-PEAK (22-6h): {len(offpeak_df):,} sessions, RSSI={offpeak_df['rssi'].mean():.1f}, SNR={offpeak_df['snr'].mean():.1f}, Weak={offpeak_df['is_weak'].mean()*100:.1f}%")

# Weekday vs Weekend
wd_df = df[~df['is_weekend']]
we_df = df[df['is_weekend']]
print(f"\n  WEEKDAY: {len(wd_df):,} sessions ({len(wd_df)/total*100:.1f}%), Avg users/day={wd_df.groupby('day')['Username'].nunique().mean():.0f}")
print(f"  WEEKEND: {len(we_df):,} sessions ({len(we_df)/total*100:.1f}%), Avg users/day={we_df.groupby('day')['Username'].nunique().mean():.0f}")

# Daily pattern
print("\n  DAILY SESSIONS:")
daily = df.groupby('day').agg(
    sessions=('id','count'), 
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    weekday=('weekday','first')
).reset_index()
for _, r in daily.iterrows():
    wd = "SAT" if r['weekday']==5 else "SUN" if r['weekday']==6 else "   "
    bar = '█' * int(r['sessions'] / 200)
    print(f"    Day {int(r['day']):>2} {wd}  {r['sessions']:>6,} sessions  {r['users']:>5,} users  RSSI={r['avg_rssi']:.1f}  {bar}")

print("\n" + "=" * 80)
print("PART 5: DEVICE & USER ANALYSIS")
print("=" * 80)

# Device types
print("\n  DEVICE TYPES:")
dev = df['deviceType'].value_counts()
for d, c in dev.head(10).items():
    print(f"    {d}: {c:,} ({c/total*100:.1f}%)")

# OS types
print("\n  OS TYPES:")
os_types = df['osType'].value_counts()
for o, c in os_types.head(10).items():
    print(f"    {o}: {c:,} ({c/total*100:.1f}%)")

# OS Vendor
print("\n  OS VENDORS:")
vendors = df['osVendorType'].value_counts()
for v, c in vendors.head(10).items():
    print(f"    {v}: {c:,} ({c/total*100:.1f}%)")

# Account types
print("\n  ACCOUNT TYPES:")
acc = df['account_type'].value_counts()
for a, c in acc.items():
    print(f"    {a}: {c:,} ({c/total*100:.1f}%)")

# Faculty distribution
print("\n  TOP FACULTIES (by sessions):")
fac = df['faculty_name'].value_counts()
for f, c in fac.head(15).items():
    users_f = df[df['faculty_name'] == f]['Username'].nunique()
    print(f"    {f}: {c:,} sessions ({c/total*100:.1f}%), {users_f:,} users")

print("\n" + "=" * 80)
print("PART 6: SSID ANALYSIS")
print("=" * 80)

ssid_stats = df.groupby('ssid').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    weak_pct=('is_weak','mean')
).reset_index()
ssid_stats['weak_pct'] *= 100

for _, r in ssid_stats.sort_values('sessions', ascending=False).iterrows():
    print(f"  {r['ssid']}: {r['sessions']:,} sessions, {r['users']:,} users, RSSI={r['avg_rssi']:.1f}, SNR={r['avg_snr']:.1f}, Weak={r['weak_pct']:.1f}%")

print("\n" + "=" * 80)
print("PART 7: RADIO TYPE / WIFI 6 ANALYSIS")
print("=" * 80)

radio_stats = df.groupby('radioType').agg(
    sessions=('id','count'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    weak_pct=('is_weak','mean'),
    avg_data=('txRxBytes','mean')
).reset_index()
radio_stats['weak_pct'] *= 100
radio_stats['avg_data_mb'] = radio_stats['avg_data'] / (1024**2)

for _, r in radio_stats.sort_values('sessions', ascending=False).iterrows():
    print(f"  {r['radioType']}: {r['sessions']:,} sessions, RSSI={r['avg_rssi']:.1f}, SNR={r['avg_snr']:.1f}, Weak={r['weak_pct']:.1f}%, AvgData={r['avg_data_mb']:.1f} MB/session")

# WiFi 6 vs non-WiFi 6 comparison
wifi6 = df[df['is_wifi6']]
non_wifi6 = df[~df['is_wifi6']]
print(f"\n  WiFi 6 devices: {len(wifi6):,} ({len(wifi6)/total*100:.1f}%)")
print(f"    RSSI={wifi6['rssi'].mean():.1f}, SNR={wifi6['snr'].mean():.1f}, Weak={wifi6['is_weak'].mean()*100:.1f}%, Data={wifi6['txRxBytes'].mean()/(1024**2):.1f} MB/session")
print(f"  Non-WiFi 6: {len(non_wifi6):,} ({len(non_wifi6)/total*100:.1f}%)")
print(f"    RSSI={non_wifi6['rssi'].mean():.1f}, SNR={non_wifi6['snr'].mean():.1f}, Weak={non_wifi6['is_weak'].mean()*100:.1f}%, Data={non_wifi6['txRxBytes'].mean()/(1024**2):.1f} MB/session")

print("\n" + "=" * 80)
print("PART 8: CHANNEL ANALYSIS")
print("=" * 80)

ch_stats = df.groupby('channel').agg(
    sessions=('id','count'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    weak_pct=('is_weak','mean'),
    aps=('apName','nunique')
).reset_index()
ch_stats['weak_pct'] *= 100

print("\n  TOP 15 CHANNELS (by sessions):")
for _, r in ch_stats.nlargest(15, 'sessions').iterrows():
    band = "2.4GHz" if r['channel'] <= 14 else "5GHz"
    print(f"    Ch {int(r['channel']):>3} ({band}): {r['sessions']:>6,} sessions, RSSI={r['avg_rssi']:.1f}, SNR={r['avg_snr']:.1f}, Weak={r['weak_pct']:.1f}%, APs={int(r['aps'])}")

# 2.4GHz vs 5GHz
df['band'] = df['channel'].apply(lambda c: '2.4GHz' if c <= 14 else '5GHz')
band24 = df[df['band'] == '2.4GHz']
band5 = df[df['band'] == '5GHz']
print(f"\n  2.4GHz: {len(band24):,} ({len(band24)/total*100:.1f}%), RSSI={band24['rssi'].mean():.1f}, SNR={band24['snr'].mean():.1f}, Weak={band24['is_weak'].mean()*100:.1f}%")
print(f"  5GHz: {len(band5):,} ({len(band5)/total*100:.1f}%), RSSI={band5['rssi'].mean():.1f}, SNR={band5['snr'].mean():.1f}, Weak={band5['is_weak'].mean()*100:.1f}%")

print("\n" + "=" * 80)
print("PART 9: CORRELATION ANALYSIS")
print("=" * 80)

# High traffic + Bad signal correlation
print("\n  DANGER ZONES: High traffic + Bad signal (busiest floors with weak > 70%):")
danger = floor_stats[(floor_stats['sessions'] > 3000) & (floor_stats['weak_pct'] > 70)]
danger = danger.sort_values('sessions', ascending=False)
for _, r in danger.iterrows():
    print(f"    {r['Building']}-{r['Floor']}: {r['sessions']:,} sessions, {r['users']:,} users, weak={r['weak_pct']:.1f}%, {r['aps']} APs, {r['sessions_per_ap']:.0f} sessions/AP")

# Peak hour degradation per building
print("\n  SIGNAL DEGRADATION DURING PEAK HOURS (per building):")
for bldg in sorted(df['Building'].unique()):
    bdf = df[df['Building'] == bldg]
    peak_b = bdf[bdf['hour'].isin(peak_hours)]
    offpeak_b = bdf[bdf['hour'].isin([7, 8, 19, 20, 21])]
    if len(peak_b) > 100 and len(offpeak_b) > 100:
        delta_rssi = peak_b['rssi'].mean() - offpeak_b['rssi'].mean()
        delta_snr = peak_b['snr'].mean() - offpeak_b['snr'].mean()
        print(f"    {bldg}: Peak RSSI={peak_b['rssi'].mean():.1f} vs Other={offpeak_b['rssi'].mean():.1f} (Δ={delta_rssi:+.1f} dBm) | Peak SNR={peak_b['snr'].mean():.1f} vs Other={offpeak_b['snr'].mean():.1f} (Δ={delta_snr:+.1f} dB)")

# Multi-device users
print("\n  MULTI-DEVICE USERS:")
user_devices = df.groupby('Username')['clientMac'].nunique()
multi_dev = (user_devices > 1).sum()
single_dev = (user_devices == 1).sum()
max_dev = user_devices.max()
print(f"    Single device: {single_dev:,}")
print(f"    Multi device: {multi_dev:,} ({multi_dev/(single_dev+multi_dev)*100:.1f}%)")
print(f"    Max devices per user: {max_dev}")
print(f"    Distribution:")
for n in range(1, min(max_dev+1, 8)):
    c = (user_devices == n).sum()
    if c > 0:
        print(f"      {n} device(s): {c:,} users")

# Data consumption patterns
print("\n  DATA CONSUMPTION BY BUILDING:")
bldg_data = df.groupby('Building').agg(
    total_gb=('txRxBytes', lambda x: x.sum()/(1024**3)),
    sessions=('id','count'),
    avg_mb=('txRxBytes', lambda x: x.mean()/(1024**2))
).reset_index()
for _, r in bldg_data.sort_values('total_gb', ascending=False).iterrows():
    print(f"    {r['Building']}: {r['total_gb']:.1f} GB total, {r['avg_mb']:.1f} MB/session, {r['sessions']:,} sessions")

# Roaming analysis (same user, multiple buildings)
print("\n  USER ROAMING (users seen in multiple buildings):")
user_bldgs = df.groupby('Username')['Building'].nunique()
for n in range(1, 7):
    c = (user_bldgs == n).sum()
    if c > 0:
        print(f"    {n} building(s): {c:,} users")

print("\n" + "=" * 80)
print("PART 10: AP ANALYSIS")
print("=" * 80)

ap_stats = df.groupby('apName').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    weak_pct=('is_weak','mean'),
    building=('Building','first'),
    floor=('Floor','first')
).reset_index()
ap_stats['weak_pct'] *= 100

print("\n  TOP 10 BUSIEST APs:")
for _, r in ap_stats.nlargest(10, 'sessions').iterrows():
    print(f"    {r['apName']} ({r['building']}-{r['floor']}): {r['sessions']:,} sessions, {r['users']:,} users, RSSI={r['avg_rssi']:.1f}, Weak={r['weak_pct']:.1f}%")

print("\n  TOP 10 WORST APs (by weak %, min 500 sessions):")
ap_min500 = ap_stats[ap_stats['sessions'] >= 500]
for _, r in ap_min500.nlargest(10, 'weak_pct').iterrows():
    print(f"    {r['apName']} ({r['building']}-{r['floor']}): Weak={r['weak_pct']:.1f}%, RSSI={r['avg_rssi']:.1f}, {r['sessions']:,} sessions")

# AP density per floor
print("\n  AP DENSITY (sessions/AP per floor, sorted by load):")
floor_stats_sorted = floor_stats.sort_values('sessions_per_ap', ascending=False)
for _, r in floor_stats_sorted.head(15).iterrows():
    print(f"    {r['Building']}-{r['Floor']}: {r['sessions_per_ap']:.0f} sessions/AP ({r['sessions']:,} sessions / {r['aps']} APs)")

print("\n" + "=" * 80)
print("PART 11: FACULTY-BUILDING CROSS ANALYSIS")
print("=" * 80)

# Which faculties use which buildings
fac_bldg = df.groupby(['faculty_name', 'Building']).agg(sessions=('id','count')).reset_index()
top_facs = df['faculty_name'].value_counts().head(10).index

for fac in top_facs:
    fb = fac_bldg[fac_bldg['faculty_name'] == fac].sort_values('sessions', ascending=False)
    total_fac = fb['sessions'].sum()
    buildings_str = ", ".join([f"{r['Building']}({r['sessions']:,})" for _, r in fb.head(3).iterrows()])
    print(f"  {fac}: {total_fac:,} sessions → {buildings_str}")

print("\n" + "=" * 80)
print("PART 12: UNUSUAL PATTERNS")
print("=" * 80)

# Late night usage
late_night = df[df['hour'].isin([0, 1, 2, 3, 4, 5])]
print(f"\n  LATE NIGHT (0-5h): {len(late_night):,} sessions ({len(late_night)/total*100:.1f}%)")
print(f"    Users: {late_night['Username'].nunique():,}")
ln_bldg = late_night['Building'].value_counts()
for b, c in ln_bldg.items():
    print(f"    {b}: {c:,} sessions")

# Heavy data users
user_data = df.groupby('Username')['txRxBytes'].sum().sort_values(ascending=False)
top_users_data = user_data.head(10)
print(f"\n  TOP 10 DATA CONSUMERS:")
for u, d in top_users_data.items():
    gb = d / (1024**3)
    sess = len(df[df['Username'] == u])
    print(f"    {u}: {gb:.1f} GB, {sess:,} sessions")

# Sessions with 0 data
zero_data = (df['txRxBytes'] == 0).sum()
print(f"\n  ZERO DATA SESSIONS: {zero_data:,} ({zero_data/total*100:.1f}%)")

# Very short sessions (low data = possible connection failures)
low_data = (df['txRxBytes'] < 1024).sum()  # < 1KB
print(f"  VERY LOW DATA (<1KB): {low_data:,} ({low_data/total*100:.1f}%)")

print("\n" + "=" * 80)
print("PART 13: GUEST vs STUDENT vs STAFF")
print("=" * 80)

for acc_type in df['account_type'].unique():
    adf = df[df['account_type'] == acc_type]
    print(f"\n  {acc_type}:")
    print(f"    Sessions: {len(adf):,} ({len(adf)/total*100:.1f}%)")
    print(f"    Users: {adf['Username'].nunique():,}")
    print(f"    Avg RSSI: {adf['rssi'].mean():.1f} | Avg SNR: {adf['snr'].mean():.1f}")
    print(f"    Weak: {adf['is_weak'].mean()*100:.1f}% | VeryPoor: {adf['is_vpoor'].mean()*100:.1f}%")
    print(f"    WiFi6: {adf['is_wifi6'].mean()*100:.1f}%")
    print(f"    Data: {adf['txRxBytes'].sum()/(1024**3):.1f} GB total, {adf['txRxBytes'].mean()/(1024**2):.1f} MB/session")

print("\n\nDONE!")
