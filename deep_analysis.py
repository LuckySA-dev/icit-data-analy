"""
Deep Analysis - Find new insights from raw dataset
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("Loading dataset...")
df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day'] = df['sessionStartDateTime'].dt.day
df['day_of_week'] = df['sessionStartDateTime'].dt.dayofweek
df['date'] = df['sessionStartDateTime'].dt.date
df['txRxBytes_MB'] = df['txRxBytes'] / (1024**2)
df['is_failed'] = df['txRxBytes'] < 1024
df['is_zero'] = df['txRxBytes'] == 0
df['is_weekend'] = df['day_of_week'].isin([5, 6])

print(f"Total rows: {len(df):,}")
print(f"Columns: {list(df.columns)}")

# =====================================================
print("\n" + "="*60)
print("SECTION A: BASIC OVERVIEW")
print("="*60)
print(f"Total sessions      : {len(df):,}")
print(f"Unique users        : {df['Username'].nunique():,}")
print(f"Unique APs          : {df['apName'].nunique():,}")
print(f"Unique buildings    : {df['Building'].nunique()}")
print(f"Date range          : {df['sessionStartDateTime'].min()} -> {df['sessionStartDateTime'].max()}")
print(f"Total data          : {df['txRxBytes'].sum()/(1024**3):.1f} GB")
print(f"Avg RSSI            : {df['rssi'].mean():.1f} dBm")
print(f"Avg SNR             : {df['snr'].mean():.1f} dB")

# =====================================================
print("\n" + "="*60)
print("SECTION B: ACCOUNT TYPE & FACULTY BREAKDOWN")
print("="*60)
print("\n-- Account Types --")
acct = df.groupby('account_type').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_data_MB=('txRxBytes_MB','mean'),
    fail_pct=('is_failed','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3))
).round(2)
acct['fail_pct'] = (acct['fail_pct']*100).round(1)
print(acct.to_string())

print("\n-- Top 10 Faculties by Sessions --")
fac = df.groupby('faculty_name').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    fail_pct=('is_failed','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3))
).sort_values('sessions', ascending=False).head(10).round(2)
fac['fail_pct'] = (fac['fail_pct']*100).round(1)
print(fac.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION C: SSID & RADIO TYPE ANALYSIS")
print("="*60)
print("\n-- SSID Usage --")
ssid = df.groupby('ssid').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    fail_pct=('is_failed','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3))
).sort_values('sessions', ascending=False).round(2)
ssid['fail_pct'] = (ssid['fail_pct']*100).round(1)
ssid['pct_of_total'] = (ssid['sessions']/len(df)*100).round(1)
print(ssid.to_string())

print("\n-- Radio Type Usage --")
radio = df.groupby('radioType').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    avg_data_MB=('txRxBytes_MB','mean'),
    fail_pct=('is_failed','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3))
).sort_values('sessions', ascending=False).round(2)
radio['fail_pct'] = (radio['fail_pct']*100).round(1)
radio['pct_of_total'] = (radio['sessions']/len(df)*100).round(1)
print(radio.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION D: DEVICE & OS ANALYSIS")
print("="*60)
print("\n-- Device Type --")
dev = df.groupby('deviceType').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_data_MB=('txRxBytes_MB','mean'),
    fail_pct=('is_failed','mean'),
).sort_values('sessions', ascending=False).round(2)
dev['fail_pct'] = (dev['fail_pct']*100).round(1)
dev['pct'] = (dev['sessions']/len(df)*100).round(1)
print(dev.to_string())

print("\n-- OS Type (Top 15) --")
os_stat = df.groupby('osType').agg(
    sessions=('id','count'),
    avg_rssi=('rssi','mean'),
    avg_data_MB=('txRxBytes_MB','mean'),
    fail_pct=('is_failed','mean'),
).sort_values('sessions', ascending=False).head(15).round(2)
os_stat['fail_pct'] = (os_stat['fail_pct']*100).round(1)
os_stat['pct'] = (os_stat['sessions']/len(df)*100).round(1)
print(os_stat.to_string())

print("\n-- OS Vendor --")
vendor = df.groupby('osVendorType').agg(
    sessions=('id','count'),
    avg_rssi=('rssi','mean'),
    fail_pct=('is_failed','mean'),
).sort_values('sessions', ascending=False).head(15).round(2)
vendor['fail_pct'] = (vendor['fail_pct']*100).round(1)
vendor['pct'] = (vendor['sessions']/len(df)*100).round(1)
print(vendor.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION E: SIGNAL QUALITY DEEP DIVE")
print("="*60)
print(f"\nRSSI Distribution:")
print(f"  Excellent (>= -50)  : {(df['rssi'] >= -50).sum():,} ({(df['rssi'] >= -50).mean()*100:.1f}%)")
print(f"  Very Good (-50~-60) : {((df['rssi'] < -50)&(df['rssi'] >= -60)).sum():,} ({((df['rssi'] < -50)&(df['rssi'] >= -60)).mean()*100:.1f}%)")
print(f"  Good (-60~-67)      : {((df['rssi'] < -60)&(df['rssi'] >= -67)).sum():,} ({((df['rssi'] < -60)&(df['rssi'] >= -67)).mean()*100:.1f}%)")
print(f"  Fair (-67~-70)      : {((df['rssi'] < -67)&(df['rssi'] >= -70)).sum():,} ({((df['rssi'] < -67)&(df['rssi'] >= -70)).mean()*100:.1f}%)")
print(f"  Weak (-70~-80)      : {((df['rssi'] < -70)&(df['rssi'] >= -80)).sum():,} ({((df['rssi'] < -70)&(df['rssi'] >= -80)).mean()*100:.1f}%)")
print(f"  Very Poor (< -80)   : {(df['rssi'] < -80).sum():,} ({(df['rssi'] < -80).mean()*100:.1f}%)")

print(f"\nSNR Distribution:")
print(f"  Excellent (>= 40)   : {(df['snr'] >= 40).sum():,} ({(df['snr'] >= 40).mean()*100:.1f}%)")
print(f"  Very Good (30-40)   : {((df['snr'] < 40)&(df['snr'] >= 30)).sum():,} ({((df['snr'] < 40)&(df['snr'] >= 30)).mean()*100:.1f}%)")
print(f"  Good (25-30)        : {((df['snr'] < 30)&(df['snr'] >= 25)).sum():,} ({((df['snr'] < 30)&(df['snr'] >= 25)).mean()*100:.1f}%)")
print(f"  Fair (20-25)        : {((df['snr'] < 25)&(df['snr'] >= 20)).sum():,} ({((df['snr'] < 25)&(df['snr'] >= 20)).mean()*100:.1f}%)")
print(f"  Weak (10-20)        : {((df['snr'] < 20)&(df['snr'] >= 10)).sum():,} ({((df['snr'] < 20)&(df['snr'] >= 10)).mean()*100:.1f}%)")
print(f"  Very Poor (< 10)    : {(df['snr'] < 10).sum():,} ({(df['snr'] < 10).mean()*100:.1f}%)")

# =====================================================
print("\n" + "="*60)
print("SECTION F: BUILDING-LEVEL ANALYSIS")
print("="*60)
bldg = df.groupby(['Building','BuildingName']).agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    aps=('apName','nunique'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    weak_pct=('rssi', lambda x: (x < -70).mean()*100),
    poor_pct=('rssi', lambda x: (x < -80).mean()*100),
    zero_pct=('is_zero','mean'),
    fail_pct=('is_failed','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
    upload_GB=('txBytes', lambda x: x.sum()/(1024**3)),
    download_GB=('rxBytes', lambda x: x.sum()/(1024**3)),
).sort_values('sessions', ascending=False).round(2)
bldg['fail_pct'] = (bldg['fail_pct']*100).round(1)
bldg['zero_pct'] = (bldg['zero_pct']*100).round(1)
bldg['users_per_ap'] = (bldg['users']/bldg['aps']).round(1)
bldg['sessions_per_ap'] = (bldg['sessions']/bldg['aps']).round(0)
bldg['ul_dl_ratio'] = (bldg['upload_GB']/bldg['download_GB'].replace(0,0.001)).round(2)
print(bldg[['sessions','users','aps','users_per_ap','avg_rssi','avg_snr','weak_pct','poor_pct','fail_pct','zero_pct','total_GB','ul_dl_ratio']].to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION G: MULTI-DEVICE USERS (Security Risk)")
print("="*60)
mac_per_user = df.groupby('Username')['clientMac'].nunique()
print(f"Users with 1 MAC address   : {(mac_per_user==1).sum():,} ({(mac_per_user==1).mean()*100:.1f}%)")
print(f"Users with 2 MACs          : {(mac_per_user==2).sum():,} ({(mac_per_user==2).mean()*100:.1f}%)")
print(f"Users with 3 MACs          : {(mac_per_user==3).sum():,} ({(mac_per_user==3).mean()*100:.1f}%)")
print(f"Users with 4+ MACs         : {(mac_per_user>=4).sum():,} ({(mac_per_user>=4).mean()*100:.1f}%)")
print(f"Max MACs by 1 user         : {mac_per_user.max()}")
print(f"\nTop 10 users by MAC count:")
for user, cnt in mac_per_user.nlargest(10).items():
    sessions = (df['Username']==user).sum()
    acct = df[df['Username']==user]['account_type'].iloc[0]
    print(f"  {user}: {cnt} MACs, {sessions} sessions, type={acct}")

# =====================================================
print("\n" + "="*60)
print("SECTION H: POWER USERS / DATA HOGS")
print("="*60)
user_data = df.groupby('Username').agg(
    sessions=('id','count'),
    total_MB=('txRxBytes_MB','sum'),
    avg_rssi=('rssi','mean'),
    account_type=('account_type','first'),
    faculty=('faculty_name','first'),
    buildings=('Building','nunique'),
).sort_values('total_MB', ascending=False)

total_data = user_data['total_MB'].sum()
top1pct = user_data.head(int(len(user_data)*0.01)+1)
top5pct = user_data.head(int(len(user_data)*0.05)+1)
top10pct = user_data.head(int(len(user_data)*0.10)+1)
print(f"Top 1% users  ({len(top1pct):,} users) consume: {top1pct['total_MB'].sum()/1024:.1f} GB = {top1pct['total_MB'].sum()/total_data*100:.1f}% of total data")
print(f"Top 5% users  ({len(top5pct):,} users) consume: {top5pct['total_MB'].sum()/1024:.1f} GB = {top5pct['total_MB'].sum()/total_data*100:.1f}% of total data")
print(f"Top 10% users ({len(top10pct):,} users) consume: {top10pct['total_MB'].sum()/1024:.1f} GB = {top10pct['total_MB'].sum()/total_data*100:.1f}% of total data")
print(f"\nTop 15 data users:")
for i, (user, row) in enumerate(user_data.head(15).iterrows(), 1):
    print(f"  {i:2d}. {user}: {row['total_MB']/1024:.1f} GB, {row['sessions']} sessions, type={row['account_type']}, fac={str(row['faculty'])[:30]}")

# =====================================================
print("\n" + "="*60)
print("SECTION I: ZERO-DATA / GHOST SESSIONS DEEP DIVE")
print("="*60)
zero_df = df[df['is_zero']]
fail_df = df[df['is_failed']]
print(f"Zero-byte sessions: {len(zero_df):,} ({len(zero_df)/len(df)*100:.1f}%)")
print(f"Failed (<1KB) sessions: {len(fail_df):,} ({len(fail_df)/len(df)*100:.1f}%)")

print("\nZero-byte by building:")
zero_bldg = zero_df.groupby('Building').agg(
    zero_sessions=('id','count'),
    total_sessions=('id', lambda x: len(df[df['Building']==x.name]))
)
zero_bldg['zero_pct'] = (zero_bldg['zero_sessions']/zero_bldg['total_sessions']*100).round(1)
print(zero_bldg.sort_values('zero_pct', ascending=False).to_string())

print("\nZero-byte by hour:")
zero_hour = df.groupby('hour').agg(
    total=('id','count'),
    zero=('is_zero','sum'),
).reset_index()
zero_hour['zero_pct'] = (zero_hour['zero']/zero_hour['total']*100).round(1)
print(zero_hour.to_string())

print("\nZero-byte by SSID:")
print(zero_df.groupby('ssid').size().sort_values(ascending=False).to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION J: HOURLY PATTERN (Peak Hours)")
print("="*60)
hourly = df.groupby('hour').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    fail_pct=('is_failed','mean'),
    zero_pct=('is_zero','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
).round(2)
hourly['fail_pct'] = (hourly['fail_pct']*100).round(1)
hourly['zero_pct'] = (hourly['zero_pct']*100).round(1)
peak_mask = hourly['users'] > hourly['users'].quantile(0.75)
hourly['peak'] = peak_mask.apply(lambda x: '*** PEAK' if x else '')
print(hourly.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION K: DAY OF WEEK PATTERN")
print("="*60)
dow_names = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
dow = df.groupby('day_of_week').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    fail_pct=('is_failed','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
).round(2)
dow.index = dow_names[:len(dow)]
dow['fail_pct'] = (dow['fail_pct']*100).round(1)
print(dow.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION L: CHANNEL ANALYSIS")
print("="*60)
ch = df.groupby('channel').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    fail_pct=('is_failed','mean'),
    aps=('apName','nunique'),
).sort_values('sessions', ascending=False).round(2)
ch['fail_pct'] = (ch['fail_pct']*100).round(1)
ch['pct'] = (ch['sessions']/len(df)*100).round(1)
ch['band'] = ch.index.map(lambda c: '2.4GHz' if c <= 14 else '5GHz')
print(ch.to_string())

band_summary = ch.groupby('band').agg(sessions=('sessions','sum'), avg_rssi=('avg_rssi','mean'), avg_snr=('avg_snr','mean'), fail_pct=('fail_pct','mean'))
print("\nBand Summary:")
print(band_summary.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION M: USER LOYALTY / REPEAT vs ONE-TIME USERS")
print("="*60)
user_sessions_count = df.groupby('Username').size()
print(f"One-time users (1 session)      : {(user_sessions_count==1).sum():,} ({(user_sessions_count==1).mean()*100:.1f}%)")
print(f"Light users (2-5 sessions)      : {((user_sessions_count>=2)&(user_sessions_count<=5)).sum():,} ({((user_sessions_count>=2)&(user_sessions_count<=5)).mean()*100:.1f}%)")
print(f"Regular users (6-20 sessions)   : {((user_sessions_count>=6)&(user_sessions_count<=20)).sum():,} ({((user_sessions_count>=6)&(user_sessions_count<=20)).mean()*100:.1f}%)")
print(f"Heavy users (21-100 sessions)   : {((user_sessions_count>=21)&(user_sessions_count<=100)).sum():,} ({((user_sessions_count>=21)&(user_sessions_count<=100)).mean()*100:.1f}%)")
print(f"Power users (>100 sessions)     : {(user_sessions_count>100).sum():,} ({(user_sessions_count>100).mean()*100:.1f}%)")
print(f"Max sessions by 1 user          : {user_sessions_count.max()}")

# =====================================================
print("\n" + "="*60)
print("SECTION N: HOSTNAME / DEVICE NAMING ANOMALY")
print("="*60)
# Check for unusual / suspicious hostnames
print(f"Total unique hostnames: {df['hostname'].nunique():,}")
# Check for empty/unknown hostnames
missing_host = df['hostname'].isna().sum() + (df['hostname']=='').sum() + (df['hostname']=='Unknown').sum()
print(f"Missing/Unknown hostnames: {missing_host:,} ({missing_host/len(df)*100:.1f}%)")
# Top hostnames
print("\nTop 20 most common hostnames:")
print(df['hostname'].value_counts().head(20).to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION O: UPLOAD vs DOWNLOAD RATIO PER BUILDING (Anomaly Detection)")
print("="*60)
ul_dl = df.groupby('Building').agg(
    total_sessions=('id','count'),
    upload_GB=('txBytes', lambda x: x.sum()/(1024**3)),
    download_GB=('rxBytes', lambda x: x.sum()/(1024**3)),
).round(2)
ul_dl['ratio_ul_dl'] = (ul_dl['upload_GB']/ul_dl['download_GB'].replace(0,0.001)).round(2)
ul_dl['total_GB'] = ul_dl['upload_GB'] + ul_dl['download_GB']
print(ul_dl.sort_values('ratio_ul_dl', ascending=False).to_string())
print(f"\nOverall Upload: {df['txBytes'].sum()/(1024**3):.1f} GB")
print(f"Overall Download: {df['rxBytes'].sum()/(1024**3):.1f} GB")
print(f"Overall UL/DL ratio: {df['txBytes'].sum()/df['rxBytes'].sum():.2f}")

# =====================================================
print("\n" + "="*60)
print("SECTION P: AP-LEVEL DEEP ANALYSIS")
print("="*60)
ap_stats = df.groupby('apName').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
    fail_pct=('is_failed','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
    building=('Building','first'),
    floor=('Floor','first'),
).sort_values('sessions', ascending=False).round(2)
ap_stats['fail_pct'] = (ap_stats['fail_pct']*100).round(1)

print("Top 20 Busiest APs:")
print(ap_stats.head(20).to_string())

print("\nTop 10 APs with Worst Signal (min 100 sessions):")
bad_signal = ap_stats[ap_stats['sessions'] >= 100].sort_values('avg_rssi').head(10)
print(bad_signal.to_string())

print("\nTop 10 APs with Highest Fail Rate (min 200 sessions):")
high_fail = ap_stats[ap_stats['sessions'] >= 200].sort_values('fail_pct', ascending=False).head(10)
print(high_fail.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION Q: SNR vs RSSI MISMATCH (Interference Indicator)")
print("="*60)
# High RSSI but Low SNR = high interference (noise floor is high)
df['rssi_snr_gap'] = df['rssi'].abs() - df['snr'].abs()
# Normal: RSSI + SNR <= ~-50+30 = RSSI = SNR + noise_floor
# If SNR much lower than expected, noise is high
df['expected_snr'] = df['rssi'] + 90  # rough: noise floor around -90dBm
df['snr_deficit'] = df['expected_snr'] - df['snr']  # positive = interference present
high_interference = df[df['snr_deficit'] > 15]
print(f"Sessions with high interference (SNR deficit >15): {len(high_interference):,} ({len(high_interference)/len(df)*100:.1f}%)")
print("\nBuildings with most interference:")
inf_by_bldg = df.groupby('Building').agg(
    avg_snr_deficit=('snr_deficit','mean'),
    high_interference_pct=('snr_deficit', lambda x: (x>15).mean()*100),
    avg_rssi=('rssi','mean'),
    avg_snr=('snr','mean'),
).round(2).sort_values('high_interference_pct', ascending=False)
print(inf_by_bldg.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION R: LATE NIGHT / UNUSUAL HOUR USAGE")
print("="*60)
late_night = df[(df['hour'] >= 22) | (df['hour'] <= 4)]
print(f"Sessions during 22:00-04:00: {len(late_night):,} ({len(late_night)/len(df)*100:.1f}%)")
print(f"Unique users late night: {late_night['Username'].nunique():,}")
print(f"Account types during late night:")
print(late_night['account_type'].value_counts().to_string())
print(f"\nBuildings active late night:")
print(late_night.groupby('Building').agg(sessions=('id','count'), users=('Username','nunique')).sort_values('sessions', ascending=False).to_string())
print(f"\nTop 10 late-night data users:")
ln_users = late_night.groupby('Username').agg(sessions=('id','count'), total_MB=('txRxBytes_MB','sum'), acct=('account_type','first')).sort_values('total_MB', ascending=False).head(10)
print(ln_users.to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION S: ROAMING DEPTH - How many APs do users connect to?")
print("="*60)
user_roam = df.groupby('Username').agg(
    n_aps=('apName','nunique'),
    n_floors=('Floor','nunique'),
    n_buildings=('Building','nunique'),
    sessions=('id','count'),
    account_type=('account_type','first'),
)
print(f"Users connecting to exactly 1 AP        : {(user_roam['n_aps']==1).sum():,} ({(user_roam['n_aps']==1).mean()*100:.1f}%)")
print(f"Users connecting to 2-5 APs             : {((user_roam['n_aps']>=2)&(user_roam['n_aps']<=5)).sum():,} ({((user_roam['n_aps']>=2)&(user_roam['n_aps']<=5)).mean()*100:.1f}%)")
print(f"Users connecting to 6-20 APs            : {((user_roam['n_aps']>=6)&(user_roam['n_aps']<=20)).sum():,} ({((user_roam['n_aps']>=6)&(user_roam['n_aps']<=20)).mean()*100:.1f}%)")
print(f"Users connecting to 21+ APs (heavy roam): {(user_roam['n_aps']>=21).sum():,} ({(user_roam['n_aps']>=21).mean()*100:.1f}%)")
print(f"Max APs by single user: {user_roam['n_aps'].max()} | Max buildings: {user_roam['n_buildings'].max()} | Max floors: {user_roam['n_floors'].max()}")

print("\nTop 10 roamers:")
for user, row in user_roam.nlargest(10, 'n_aps').iterrows():
    print(f"  {user}: {row['n_aps']} APs, {row['n_buildings']} buildings, {row['n_floors']} floors, {row['sessions']} sessions, {row['account_type']}")

print("\nRoaming by account type:")
print(user_roam.groupby('account_type').agg(avg_aps=('n_aps','mean'), avg_buildings=('n_buildings','mean')).round(2).to_string())

# =====================================================
print("\n" + "="*60)
print("SECTION T: DATA USAGE DISTRIBUTION (Pareto Analysis)")
print("="*60)
user_data2 = df.groupby('Username')['txRxBytes_MB'].sum().sort_values(ascending=False)
cumsum = user_data2.cumsum() / user_data2.sum() * 100
total_users = len(user_data2)
for pct in [10, 20, 30, 50, 80]:
    idx = int(total_users * pct / 100)
    data_pct = cumsum.iloc[idx-1] if idx > 0 else 0
    print(f"  Top {pct}% of users ({idx:,}) consume {data_pct:.1f}% of total data")

# =====================================================
print("\n" + "="*60)
print("SECTION U: DEPARTMENT (dep_name) ANALYSIS")
print("="*60)
dep = df.groupby('dep_name').agg(
    sessions=('id','count'),
    users=('Username','nunique'),
    avg_rssi=('rssi','mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
).sort_values('sessions', ascending=False).head(20).round(2)
print(dep.to_string())

print("\n\n✅ DEEP ANALYSIS COMPLETE")
