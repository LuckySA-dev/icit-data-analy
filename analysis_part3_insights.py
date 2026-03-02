"""
ICIT Data Insight & Analytics Challenge 2026
Part 3: Deep Insights, Pain Points & Solutions
Wi-Fi usage data analysis for KMUTNB
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Tahoma', 'Leelawadee UI', 'Segoe UI', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

os.makedirs("output", exist_ok=True)

print("Loading dataset...")
df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['date'] = df['sessionStartDateTime'].dt.date
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day_of_week'] = df['sessionStartDateTime'].dt.dayofweek
df['day_name'] = df['sessionStartDateTime'].dt.day_name()
df['txRxBytes_MB'] = df['txRxBytes'] / (1024 * 1024)
df['txRxBytes_GB'] = df['txRxBytes'] / (1024**3)

def classify_rssi(rssi):
    if rssi >= -50: return 'Excellent'
    elif rssi >= -60: return 'Very Good'
    elif rssi >= -67: return 'Good'
    elif rssi >= -70: return 'Fair'
    elif rssi >= -80: return 'Weak'
    else: return 'Very Poor'

def classify_snr(snr):
    if snr >= 40: return 'Excellent'
    elif snr >= 30: return 'Very Good'
    elif snr >= 25: return 'Good'
    elif snr >= 20: return 'Fair'
    elif snr >= 10: return 'Weak'
    else: return 'Very Poor'

df['rssi_quality'] = df['rssi'].apply(classify_rssi)
df['snr_quality'] = df['snr'].apply(classify_snr)

print("\n" + "=" * 70)
print("DEEP INSIGHTS, PAIN POINTS & SOLUTIONS")
print("=" * 70)

# ============================================================
# INSIGHT 1: AP Overload Analysis - Congestion Detection
# ============================================================
print("\n" + "-" * 50)
print("INSIGHT 1: AP OVERLOAD / CONGESTION ANALYSIS")
print("-" * 50)

# Sessions per AP per hour
ap_hourly = df.groupby(['apName', 'hour']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    total_MB=('txRxBytes_MB', 'sum')
).reset_index()

# Find peak congestion
ap_peak = ap_hourly.sort_values('unique_users', ascending=False)
print("\nTop 15 Most Congested AP-Hour combinations:")
for i, row in enumerate(ap_peak.head(15).itertuples(), 1):
    print(f"  {i:2d}. {row.apName} @ {row.hour:02d}:00 - "
          f"{row.unique_users} users, {row.sessions} sessions, "
          f"RSSI={row.avg_rssi:.1f}, Data={row.total_MB:.1f} MB")

# AP overall load
ap_load = df.groupby('apName').agg(
    total_sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    building=('BuildingName', 'first'),
    floor=('Floor', 'first')
).sort_values('total_sessions', ascending=False).reset_index()

print("\nTop 20 Busiest Access Points:")
for i, row in enumerate(ap_load.head(20).itertuples(), 1):
    rssi_q = classify_rssi(row.avg_rssi)
    print(f"  {i:2d}. {row.apName}: {row.total_sessions:,} sessions, "
          f"{row.unique_users:,} users, RSSI={row.avg_rssi:.1f} ({rssi_q}), "
          f"{row.total_GB:.2f} GB | {row.building}-{row.floor}")

fig, axes = plt.subplots(2, 2, figsize=(22, 16))

# Top 20 APs by sessions
ax = axes[0, 0]
top20_ap = ap_load.head(20)
rssi_colors = []
for r in top20_ap['avg_rssi']:
    if r >= -60: rssi_colors.append('#2ecc71')
    elif r >= -70: rssi_colors.append('#f1c40f')
    else: rssi_colors.append('#e74c3c')
bars = ax.barh(range(len(top20_ap)), top20_ap['total_sessions'].values, color=rssi_colors, edgecolor='white')
ax.set_yticks(range(len(top20_ap)))
ax.set_yticklabels(top20_ap['apName'].values, fontsize=7)
ax.set_xlabel('Total Sessions')
ax.set_title('Top 20 Busiest APs\n(Green=Good RSSI, Yellow=Fair, Red=Weak)', fontsize=12, fontweight='bold')
ax.invert_yaxis()

# AP sessions vs RSSI scatter
ax = axes[0, 1]
scatter = ax.scatter(ap_load['total_sessions'], ap_load['avg_rssi'], 
                     c=ap_load['total_GB'], cmap='YlOrRd', s=50, alpha=0.7, edgecolors='gray')
ax.axhline(y=-70, color='orange', linestyle='--', label='Fair threshold')
ax.axhline(y=-80, color='red', linestyle='--', label='Weak threshold')
ax.set_xlabel('Total Sessions')
ax.set_ylabel('Average RSSI (dBm)')
ax.set_title('AP Load vs Signal Quality\n(Color=Data Volume)', fontsize=12, fontweight='bold')
ax.legend()
plt.colorbar(scatter, ax=ax, label='Total GB')

# Problematic APs: High load + poor signal
problem_aps = ap_load[(ap_load['avg_rssi'] < -65) & (ap_load['total_sessions'] > ap_load['total_sessions'].median())]
print(f"\n{'='*50}")
print(f"PROBLEM APs: High Load + Poor Signal ({len(problem_aps)} APs)")
print(f"{'='*50}")
for i, row in enumerate(problem_aps.sort_values('avg_rssi').head(10).itertuples(), 1):
    print(f"  {i}. {row.apName} ({row.building}-{row.floor}): "
          f"RSSI={row.avg_rssi:.1f}, {row.total_sessions:,} sessions")

# Hourly heatmap for top 10 APs
ax = axes[1, 0]
top10_ap_names = ap_load.head(10)['apName'].values
top10_hourly = ap_hourly[ap_hourly['apName'].isin(top10_ap_names)]
pivot = top10_hourly.pivot_table(index='apName', columns='hour', values='unique_users', fill_value=0)
im = ax.imshow(pivot.values, aspect='auto', cmap='YlOrRd')
ax.set_xticks(range(24))
ax.set_xticklabels(range(24), fontsize=7)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index, fontsize=7)
ax.set_xlabel('Hour')
ax.set_title('Top 10 APs - Hourly User Heatmap', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax, label='Users')

# Sessions per user histogram
ax = axes[1, 1]
user_sessions = df.groupby('Username').size()
ax.hist(user_sessions.values, bins=50, color='steelblue', edgecolor='white', alpha=0.8)
ax.set_xlabel('Sessions per User')
ax.set_ylabel('Count of Users')
ax.set_title(f'Distribution of Sessions per User\n(Median={user_sessions.median():.0f}, Max={user_sessions.max():,})', 
             fontsize=12, fontweight='bold')
ax.axvline(user_sessions.median(), color='red', linestyle='--', label=f'Median: {user_sessions.median():.0f}')
ax.legend()

plt.tight_layout()
plt.savefig('output/insight_1_ap_congestion.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/insight_1_ap_congestion.png")

# ============================================================
# INSIGHT 2: Signal Quality Problem Zones (Dead Zones)
# ============================================================
print("\n" + "-" * 50)
print("INSIGHT 2: SIGNAL DEAD ZONES")
print("-" * 50)

# Find zones where >30% sessions have weak signal
bldg_floor_stats = df.groupby(['BuildingName', 'Floor']).agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    weak_count=('rssi', lambda x: (x <= -71).sum()),
    poor_count=('rssi', lambda x: (x < -80).sum()),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3))
).reset_index()

bldg_floor_stats['weak_pct'] = bldg_floor_stats['weak_count'] / bldg_floor_stats['sessions'] * 100
bldg_floor_stats['poor_pct'] = bldg_floor_stats['poor_count'] / bldg_floor_stats['sessions'] * 100

dead_zones = bldg_floor_stats[bldg_floor_stats['weak_pct'] > 30].sort_values('weak_pct', ascending=False)
print(f"\nDead Zones (>30% Weak Signal):")
for i, row in enumerate(dead_zones.itertuples(), 1):
    print(f"  {i}. {row.BuildingName} - {row.Floor}: "
          f"Weak={row.weak_pct:.1f}%, Poor={row.poor_pct:.1f}%, "
          f"Avg RSSI={row.avg_rssi:.1f}, Users={row.unique_users:,}")

# Also check APs with consistently poor signal
ap_signal = df.groupby('apName').agg(
    avg_rssi=('rssi', 'mean'),
    std_rssi=('rssi', 'std'),
    avg_snr=('snr', 'mean'),
    sessions=('id', 'count'),
    weak_pct=('rssi', lambda x: (x <= -71).sum() / len(x) * 100),
    building=('BuildingName', 'first'),
    floor=('Floor', 'first')
).sort_values('avg_rssi')

print(f"\nAPs with Worst Average RSSI:")
for i, row in enumerate(ap_signal.head(15).itertuples(), 1):
    print(f"  {i:2d}. {row.Index}: RSSI={row.avg_rssi:.1f}±{row.std_rssi:.1f}, "
          f"SNR={row.avg_snr:.1f}, Weak%={row.weak_pct:.1f}%, "
          f"{row.building}-{row.floor}")

fig, axes = plt.subplots(1, 2, figsize=(20, 10))

# Dead zone visualization
ax = axes[0]
dead_zones_plot = bldg_floor_stats.sort_values('weak_pct', ascending=False).head(15)
dead_zones_plot['label'] = dead_zones_plot['BuildingName'].str[:25] + '\n' + dead_zones_plot['Floor']
colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(dead_zones_plot)))
bars = ax.barh(range(len(dead_zones_plot)), dead_zones_plot['weak_pct'].values, color=colors)
ax.set_yticks(range(len(dead_zones_plot)))
ax.set_yticklabels(dead_zones_plot['label'].values, fontsize=7)
ax.set_xlabel('% Weak/Very Poor RSSI Sessions')
ax.set_title('Signal Dead Zones\n(Building-Floor with Highest % Weak Signal)', fontsize=12, fontweight='bold')
ax.invert_yaxis()
ax.axvline(30, color='red', linestyle='--', alpha=0.5, label='30% threshold')
ax.legend()
for bar, val, pval in zip(bars, dead_zones_plot['weak_pct'].values, dead_zones_plot['poor_pct'].values):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
            f'{val:.1f}% (Poor:{pval:.1f}%)', va='center', fontsize=8)

# AP signal quality scatter with size=sessions
ax = axes[1]
scatter = ax.scatter(ap_signal['avg_rssi'], ap_signal['avg_snr'], 
                     s=ap_signal['sessions']/100, alpha=0.6, c=ap_signal['weak_pct'],
                     cmap='RdYlGn_r', edgecolors='gray', linewidth=0.5)
ax.axvline(-70, color='orange', linestyle='--', alpha=0.5, label='RSSI Fair')
ax.axvline(-80, color='red', linestyle='--', alpha=0.5, label='RSSI Weak')
ax.axhline(20, color='orange', linestyle=':', alpha=0.5, label='SNR Fair')
ax.set_xlabel('Average RSSI (dBm)')
ax.set_ylabel('Average SNR (dB)')
ax.set_title('AP Signal Quality Map\n(Size=Sessions, Color=Weak%)', fontsize=12, fontweight='bold')
ax.legend(fontsize=8)
plt.colorbar(scatter, ax=ax, label='% Weak Sessions')

plt.tight_layout()
plt.savefig('output/insight_2_dead_zones.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/insight_2_dead_zones.png")

# ============================================================
# INSIGHT 3: Peak Hour & Capacity Planning
# ============================================================
print("\n" + "-" * 50)
print("INSIGHT 3: PEAK HOUR & CAPACITY ANALYSIS")
print("-" * 50)

hourly_stats = df.groupby('hour').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    avg_rssi=('rssi', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean')
).reset_index()

print("\nHourly Statistics:")
for _, row in hourly_stats.iterrows():
    marker = " *** PEAK" if row['unique_users'] > hourly_stats['unique_users'].quantile(0.75) else ""
    print(f"  {int(row['hour']):02d}:00 - Users: {int(row['unique_users']):,}, "
          f"Sessions: {int(row['sessions']):,}, Data: {row['total_GB']:.2f} GB, "
          f"RSSI: {row['avg_rssi']:.1f}{marker}")

# Peak hour signal degradation analysis
peak_hours = hourly_stats[hourly_stats['unique_users'] > hourly_stats['unique_users'].quantile(0.75)]['hour'].values
off_peak = hourly_stats[hourly_stats['unique_users'] <= hourly_stats['unique_users'].quantile(0.25)]['hour'].values

peak_rssi = df[df['hour'].isin(peak_hours)]['rssi'].mean()
offpeak_rssi = df[df['hour'].isin(off_peak)]['rssi'].mean()
print(f"\nPeak hours avg RSSI: {peak_rssi:.1f} dBm")
print(f"Off-peak hours avg RSSI: {offpeak_rssi:.1f} dBm")
print(f"Signal degradation during peak: {peak_rssi - offpeak_rssi:.1f} dBm")

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

ax = axes[0, 0]
ax.fill_between(hourly_stats['hour'], hourly_stats['unique_users'], alpha=0.3, color='steelblue')
ax.plot(hourly_stats['hour'], hourly_stats['unique_users'], 'o-', color='steelblue', linewidth=2)
thresh = hourly_stats['unique_users'].quantile(0.75)
ax.axhline(thresh, color='red', linestyle='--', alpha=0.5, label=f'75th percentile: {thresh:.0f}')
ax.fill_between(hourly_stats['hour'], hourly_stats['unique_users'], thresh, 
                where=hourly_stats['unique_users'] > thresh, alpha=0.3, color='red')
ax.set_xlabel('Hour')
ax.set_ylabel('Unique Users')
ax.set_title('Peak Usage Hours\n(Red area = above 75th percentile)', fontsize=12, fontweight='bold')
ax.set_xticks(range(24))
ax.legend()

ax = axes[0, 1]
ax2 = ax.twinx()
ax.bar(hourly_stats['hour'], hourly_stats['total_GB'], color='steelblue', alpha=0.6, label='Data (GB)')
ax2.plot(hourly_stats['hour'], hourly_stats['avg_rssi'], 'r-o', linewidth=2, markersize=4, label='Avg RSSI')
ax.set_xlabel('Hour')
ax.set_ylabel('Total Data (GB)', color='steelblue')
ax2.set_ylabel('Avg RSSI (dBm)', color='red')
ax.set_title('Data Volume vs Signal Quality by Hour', fontsize=12, fontweight='bold')
ax.set_xticks(range(24))
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# Building capacity by hour
ax = axes[1, 0]
bldg_hourly = df.groupby(['BuildingName', 'hour'])['Username'].nunique().reset_index()
for bldg in df['BuildingName'].unique():
    bldg_data = bldg_hourly[bldg_hourly['BuildingName'] == bldg]
    ax.plot(bldg_data['hour'], bldg_data['Username'], '-o', markersize=3, label=bldg[:20])
ax.set_xlabel('Hour')
ax.set_ylabel('Unique Users')
ax.set_title('Hourly User Load per Building', fontsize=12, fontweight='bold')
ax.legend(fontsize=6, loc='upper left')
ax.set_xticks(range(24))

# Sessions per user by account type box plot
ax = axes[1, 1]
acct_types = df['account_type'].unique()
data_by_acct = [df[df['account_type'] == acct].groupby('Username')['txRxBytes_MB'].sum().values for acct in acct_types]
bp = ax.boxplot(data_by_acct, labels=acct_types, patch_artist=True, showfliers=False)
acct_colors = plt.cm.Set2(np.linspace(0, 0.8, len(acct_types)))
for patch, color in zip(bp['boxes'], acct_colors):
    patch.set_facecolor(color)
ax.set_ylabel('Total Data per User (MB)')
ax.set_title('Data Usage Distribution by Account Type\n(outliers removed)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('output/insight_3_peak_capacity.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/insight_3_peak_capacity.png")

# ============================================================
# INSIGHT 4: Device & Technology Analysis
# ============================================================
print("\n" + "-" * 50)
print("INSIGHT 4: DEVICE & TECHNOLOGY ANALYSIS")
print("-" * 50)

# Radio type vs signal quality
radio_signal = df.groupby('radioType').agg(
    sessions=('id', 'count'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3))
).sort_values('sessions', ascending=False).dropna()

print("\nRadio Type Performance:")
for _, row in radio_signal.iterrows():
    rssi_q = classify_rssi(row['avg_rssi'])
    print(f"  {row.name:15s}: {int(row['sessions']):>7,} sessions, "
          f"RSSI={row['avg_rssi']:.1f} ({rssi_q}), "
          f"SNR={row['avg_snr']:.1f}, Avg Data={row['avg_data_MB']:.2f} MB")

# WiFi 6 (ax) vs older
wifi6_mask = df['radioType'].str.contains('ax', na=False)
wifi6_sessions = df[wifi6_mask]
older_sessions = df[~wifi6_mask & df['radioType'].notna()]

print(f"\n--- WiFi 6 (ax) vs Older Standards ---")
print(f"  WiFi 6 sessions: {len(wifi6_sessions):,} ({len(wifi6_sessions)/len(df)*100:.1f}%)")
print(f"  Older sessions: {len(older_sessions):,} ({len(older_sessions)/len(df)*100:.1f}%)")
print(f"  WiFi 6 avg RSSI: {wifi6_sessions['rssi'].mean():.1f} vs Older: {older_sessions['rssi'].mean():.1f}")
print(f"  WiFi 6 avg data: {wifi6_sessions['txRxBytes_MB'].mean():.2f} MB vs Older: {older_sessions['txRxBytes_MB'].mean():.2f} MB")

# Device type analysis
device_signal = df.groupby('deviceType').agg(
    sessions=('id', 'count'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean')
).sort_values('sessions', ascending=False)

print("\nDevice Type Performance:")
for _, row in device_signal.iterrows():
    print(f"  {row.name:12s}: {int(row['sessions']):>7,} sessions, "
          f"RSSI={row['avg_rssi']:.1f}, Data={row['avg_data_MB']:.2f} MB")

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

# Radio type comparison
ax = axes[0, 0]
radio_sorted = radio_signal.sort_values('avg_rssi')
colors = [('#2ecc71' if r >= -60 else '#f1c40f' if r >= -70 else '#e74c3c') for r in radio_sorted['avg_rssi'].values]
bars = ax.barh(range(len(radio_sorted)), radio_sorted['avg_rssi'].values, color=colors, edgecolor='white')
ax.set_yticks(range(len(radio_sorted)))
ax.set_yticklabels(radio_sorted.index, fontsize=9)
ax.set_xlabel('Average RSSI (dBm)')
ax.set_title('Signal Quality by Radio Type', fontsize=12, fontweight='bold')
ax.axvline(-70, color='orange', linestyle='--', alpha=0.5)
ax.axvline(-80, color='red', linestyle='--', alpha=0.5)

# WiFi 6 adoption over time  
ax = axes[0, 1]
df['week'] = df['sessionStartDateTime'].dt.isocalendar().week.astype(int)
weekly_wifi6 = df.groupby('week').apply(lambda x: (x['radioType'].str.contains('ax', na=False)).sum() / len(x) * 100)
ax.plot(weekly_wifi6.index, weekly_wifi6.values, 'g-o', linewidth=2, markersize=4)
ax.set_xlabel('Week Number')
ax.set_ylabel('% WiFi 6 (ax) Sessions')
ax.set_title('WiFi 6 Adoption Trend by Week', fontsize=12, fontweight='bold')
ax.fill_between(weekly_wifi6.index, weekly_wifi6.values, alpha=0.2, color='green')

# Device type RSSI comparison
ax = axes[1, 0]
device_types = df['deviceType'].unique()
for dt in device_types:
    data = df[df['deviceType'] == dt]['rssi']
    ax.hist(data, bins=50, alpha=0.4, label=f'{dt} (n={len(data):,})', density=True)
ax.set_xlabel('RSSI (dBm)')
ax.set_ylabel('Density')
ax.set_title('RSSI Distribution by Device Type', fontsize=12, fontweight='bold')
ax.legend(fontsize=8)
ax.axvline(-70, color='orange', linestyle='--', alpha=0.5)

# Channel distribution  
ax = axes[1, 1]
channel_stats = df.groupby('channel').agg(
    sessions=('id', 'count'),
    avg_rssi=('rssi', 'mean')
).sort_values('sessions', ascending=False).head(15)
colors = [('#2ecc71' if r >= -60 else '#f1c40f' if r >= -70 else '#e74c3c') for r in channel_stats['avg_rssi'].values]
bars = ax.bar(range(len(channel_stats)), channel_stats['sessions'].values, color=colors, edgecolor='white')
ax.set_xticks(range(len(channel_stats)))
ax.set_xticklabels(channel_stats.index, fontsize=8)
ax.set_xlabel('Channel')
ax.set_ylabel('Sessions')
ax.set_title('Top 15 Channels by Session Count\n(Color=Signal Quality)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('output/insight_4_device_technology.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/insight_4_device_technology.png")

# ============================================================
# INSIGHT 5: User Behavior & Mobility
# ============================================================
print("\n" + "-" * 50)
print("INSIGHT 5: USER BEHAVIOR & MOBILITY PATTERNS")
print("-" * 50)

user_stats = df.groupby('Username').agg(
    sessions=('id', 'count'),
    unique_aps=('apName', 'nunique'),
    unique_buildings=('BuildingName', 'nunique'),
    unique_floors=('Floor', 'nunique'),
    unique_devices=('clientMac', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    total_MB=('txRxBytes_MB', 'sum'),
    account_type=('account_type', 'first'),
    faculty=('faculty_name', 'first')
).reset_index()

print(f"\nUser Mobility Stats:")
print(f"  Users visiting >1 building: {(user_stats['unique_buildings'] > 1).sum():,} ({(user_stats['unique_buildings'] > 1).mean()*100:.1f}%)")
print(f"  Users using >1 AP: {(user_stats['unique_aps'] > 1).sum():,} ({(user_stats['unique_aps'] > 1).mean()*100:.1f}%)")
print(f"  Users with >1 device: {(user_stats['unique_devices'] > 1).sum():,} ({(user_stats['unique_devices'] > 1).mean()*100:.1f}%)")
print(f"  Avg APs per user: {user_stats['unique_aps'].mean():.1f}")
print(f"  Avg buildings per user: {user_stats['unique_buildings'].mean():.1f}")

# Heavy users
heavy_users = user_stats[user_stats['total_MB'] > user_stats['total_MB'].quantile(0.95)]
print(f"\n  Top 5% heavy users ({len(heavy_users):,} users): "
      f"avg {heavy_users['total_MB'].mean():.1f} MB, "
      f"avg {heavy_users['sessions'].mean():.0f} sessions")

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

# User mobility
ax = axes[0, 0]
mobility = user_stats['unique_buildings'].value_counts().sort_index()
ax.bar(mobility.index, mobility.values, color='steelblue', edgecolor='white')
ax.set_xlabel('Number of Buildings Visited')
ax.set_ylabel('Number of Users')
ax.set_title('User Mobility: Buildings Visited per User', fontsize=12, fontweight='bold')
for x, y in zip(mobility.index, mobility.values):
    ax.text(x, y + 5, f'{y:,}', ha='center', fontsize=9)

# Data usage distribution
ax = axes[0, 1]
bins = [0, 1, 10, 50, 100, 500, 1000, float('inf')]
labels = ['<1 MB', '1-10 MB', '10-50 MB', '50-100 MB', '100-500 MB', '500-1000 MB', '>1000 MB']
user_stats['data_bucket'] = pd.cut(user_stats['total_MB'], bins=bins, labels=labels)
data_dist = user_stats['data_bucket'].value_counts().reindex(labels)
colors = plt.cm.YlOrRd(np.linspace(0.2, 0.9, len(data_dist)))
bars = ax.bar(range(len(data_dist)), data_dist.values, color=colors, edgecolor='white')
ax.set_xticks(range(len(data_dist)))
ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
ax.set_ylabel('Number of Users')
ax.set_title('User Data Usage Distribution', fontsize=12, fontweight='bold')
for bar, val in zip(bars, data_dist.values):
    if not np.isnan(val):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f'{int(val):,}', ha='center', fontsize=8)

# Account type usage patterns
ax = axes[1, 0]
acct_usage = user_stats.groupby('account_type').agg(
    users=('Username', 'count'),
    avg_sessions=('sessions', 'mean'),
    avg_MB=('total_MB', 'mean'),
    avg_aps=('unique_aps', 'mean')
)
x = range(len(acct_usage))
width = 0.25
ax.bar([i - width for i in x], acct_usage['avg_sessions'].values, width, label='Avg Sessions', color='#3498db')
ax.bar([i for i in x], acct_usage['avg_MB'].values / 10, width, label='Avg MB / 10', color='#2ecc71')
ax.bar([i + width for i in x], acct_usage['avg_aps'].values * 5, width, label='Avg APs × 5', color='#e74c3c')
ax.set_xticks(list(x))
ax.set_xticklabels(acct_usage.index, fontsize=8)
ax.set_title('Usage Patterns by Account Type', fontsize=12, fontweight='bold')
ax.legend()

# Multi-device users
ax = axes[1, 1]
device_count_dist = user_stats['unique_devices'].value_counts().sort_index().head(10)
ax.bar(device_count_dist.index.astype(str), device_count_dist.values, color='coral', edgecolor='white')
ax.set_xlabel('Number of Devices per User')
ax.set_ylabel('Number of Users')
ax.set_title('Multi-Device Usage Pattern', fontsize=12, fontweight='bold')
for x, y in zip(range(len(device_count_dist)), device_count_dist.values):
    ax.text(x, y + 5, f'{y:,}', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('output/insight_5_user_behavior.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/insight_5_user_behavior.png")

# ============================================================
# INSIGHT 6: Network Efficiency & Bandwidth
# ============================================================
print("\n" + "-" * 50)
print("INSIGHT 6: NETWORK EFFICIENCY ANALYSIS")
print("-" * 50)

# Sessions with very low data transfer (possibly failed connections)
low_data = df[df['txRxBytes'] < 1024]  # Less than 1 KB
print(f"\nSessions with <1KB data: {len(low_data):,} ({len(low_data)/len(df)*100:.1f}%)")
zero_data = df[df['txRxBytes'] == 0]
print(f"Sessions with 0 bytes: {len(zero_data):,} ({len(zero_data)/len(df)*100:.1f}%)")

# Efficiency by RSSI quality
rssi_quality_order = ['Excellent', 'Very Good', 'Good', 'Fair', 'Weak', 'Very Poor']
quality_stats = df.groupby('rssi_quality').agg(
    sessions=('id', 'count'),
    avg_data_MB=('txRxBytes_MB', 'mean'),
    median_data_MB=('txRxBytes_MB', 'median'),
    zero_data_pct=('txRxBytes', lambda x: (x == 0).sum() / len(x) * 100),
    low_data_pct=('txRxBytes', lambda x: (x < 1024).sum() / len(x) * 100)
).reindex(rssi_quality_order)

print("\nData Transfer Efficiency by Signal Quality:")
for q, row in quality_stats.iterrows():
    print(f"  {q:12s}: Avg={row['avg_data_MB']:.2f} MB, "
          f"Median={row['median_data_MB']:.2f} MB, "
          f"Zero%={row['zero_data_pct']:.1f}%, "
          f"Low%={row['low_data_pct']:.1f}%")

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

ax = axes[0, 0]
rssi_colors_map = {'Excellent': '#2ecc71', 'Very Good': '#27ae60', 'Good': '#f1c40f', 
                   'Fair': '#e67e22', 'Weak': '#e74c3c', 'Very Poor': '#c0392b'}
colors = [rssi_colors_map.get(q, 'gray') for q in quality_stats.index]
bars = ax.bar(range(len(quality_stats)), quality_stats['avg_data_MB'].values, color=colors, edgecolor='white')
ax.set_xticks(range(len(quality_stats)))
ax.set_xticklabels(quality_stats.index, fontsize=9, rotation=30, ha='right')
ax.set_ylabel('Average Data Transfer (MB)')
ax.set_title('Data Transfer Efficiency by Signal Quality\n(Better signal = more data)', fontsize=12, fontweight='bold')
for bar, val in zip(bars, quality_stats['avg_data_MB'].values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{val:.2f}', ha='center', fontsize=9)

ax = axes[0, 1]
bars = ax.bar(range(len(quality_stats)), quality_stats['low_data_pct'].values, color=colors, edgecolor='white')
ax.set_xticks(range(len(quality_stats)))
ax.set_xticklabels(quality_stats.index, fontsize=9, rotation=30, ha='right')
ax.set_ylabel('% Sessions with <1KB Data')
ax.set_title('Failed/Low Data Sessions by Signal Quality\n(Higher = more potentially failed connections)', fontsize=12, fontweight='bold')
for bar, val in zip(bars, quality_stats['low_data_pct'].values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, f'{val:.1f}%', ha='center', fontsize=9)

# RSSI vs Data scatter
ax = axes[1, 0]
sample = df.sample(min(5000, len(df)), random_state=42)
ax.scatter(sample['rssi'], sample['txRxBytes_MB'], alpha=0.1, s=5, color='steelblue')
# Add median line
rssi_bins = pd.cut(df['rssi'], bins=20)
rssi_median_data = df.groupby(rssi_bins, observed=True)['txRxBytes_MB'].median()
midpoints = [interval.mid for interval in rssi_median_data.index]
ax.plot(midpoints, rssi_median_data.values, 'r-o', linewidth=2, markersize=5, label='Median')
ax.set_xlabel('RSSI (dBm)')
ax.set_ylabel('Data Transfer (MB)')
ax.set_title('RSSI vs Data Transfer\n(Red line = median)', fontsize=12, fontweight='bold')
ax.legend()

# RSSI distribution overall
ax = axes[1, 1]
ax.hist(df['rssi'], bins=80, color='steelblue', edgecolor='white', alpha=0.8, density=True)
ax.axvline(-50, color='green', linestyle='--', alpha=0.7, label='Excellent (-50)')
ax.axvline(-60, color='lime', linestyle='--', alpha=0.7, label='Very Good (-60)')
ax.axvline(-67, color='yellow', linestyle='--', alpha=0.7, label='Good (-67)')
ax.axvline(-70, color='orange', linestyle='--', alpha=0.7, label='Fair (-70)')
ax.axvline(-80, color='red', linestyle='--', alpha=0.7, label='Weak (-80)')
ax.set_xlabel('RSSI (dBm)')
ax.set_ylabel('Density')
ax.set_title('Overall RSSI Distribution', fontsize=12, fontweight='bold')
ax.legend(fontsize=7, loc='upper left')

plt.tight_layout()
plt.savefig('output/insight_6_network_efficiency.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/insight_6_network_efficiency.png")

# ============================================================
# SUMMARY: PAIN POINTS & SOLUTIONS
# ============================================================
print("\n" + "=" * 70)
print("COMPREHENSIVE PAIN POINTS & RECOMMENDED SOLUTIONS")
print("=" * 70)

# Calculate key metrics for summary 
total_sessions = len(df)
weak_sessions = len(df[df['rssi'] <= -71])
poor_sessions = len(df[df['rssi'] < -80])
weak_pct = weak_sessions / total_sessions * 100
poor_pct = poor_sessions / total_sessions * 100

print(f"""
=================================================================
PAIN POINT 1: Signal Coverage Gaps (Dead Zones)
=================================================================
Findings:
  - {weak_pct:.1f}% of all sessions ({weak_sessions:,}/{total_sessions:,}) have Weak/Very Poor RSSI
  - {poor_pct:.1f}% sessions have Very Poor signal (<-80 dBm) - NOT recommended for use
  - Worst affected locations identified above
  
Root Cause:
  - Insufficient AP density in certain building areas
  - Physical obstructions (walls, floors) causing signal attenuation
  - Some floors may be too far from nearest AP
  
Solutions:
  1. Deploy additional APs in identified dead zones
  2. Install signal repeaters/range extenders on worst floors
  3. Conduct professional site survey with heatmap tools
  4. Consider using directional antennas for long-range coverage
  
Tools:
  - Ekahau Site Survey / AI Pro (site survey & heatmap)
  - NetSpot (Wi-Fi analyzer)
  - Cisco DNA Center (centralized management)
  - Aruba Central (AP deployment planning)

=================================================================  
PAIN POINT 2: AP Overload & Congestion
=================================================================
Findings:
  - Top APs serve {ap_load.head(1)['total_sessions'].values[0]:,}+ sessions
  - Peak hours show significantly higher load (see hourly analysis)
  - Some APs have degraded RSSI due to too many connected clients
  
Root Cause:
  - Uneven distribution of APs vs user density
  - High-traffic areas (classrooms, cafeteria) lack sufficient capacity
  - No load balancing between nearby APs
  
Solutions:
  1. Add more APs in high-congestion zones to distribute load
  2. Enable band steering (push 5GHz-capable devices to 5GHz band)
  3. Implement client load balancing policies
  4. Set max client limits per AP
  
Tools:
  - Cisco WLC (Wireless LAN Controller) for load balancing
  - Aruba Airwave for monitoring
  - Meraki Dashboard for cloud management
  - Prometheus + Grafana for real-time monitoring

=================================================================
PAIN POINT 3: Legacy Device/Protocol Issues
=================================================================
Findings:
  - WiFi 6 (ax) adoption: {len(wifi6_sessions):,} sessions ({len(wifi6_sessions)/len(df)*100:.1f}%)
  - Many sessions still use older standards (b/g/n, a/n/ac)
  - Older protocols reduce overall network efficiency
  
Root Cause:
  - Mix of old and new devices on campus
  - Some APs may not support WiFi 6
  - Users unaware of device capability settings
  
Solutions:
  1. Upgrade APs to WiFi 6E (802.11ax) across campus
  2. Create separate SSIDs for legacy vs modern devices  
  3. Schedule periodic network standard assessments
  4. Encourage device upgrade programs for students
  
Tools:
  - WiFi Analyzer (Android/iOS)
  - inSSIDer for standard detection
  - Cisco Catalyst 9100 APs (WiFi 6/6E)
  - Aruba AP-635/655 (WiFi 6E)

=================================================================
PAIN POINT 4: Inefficient Data Transfer
=================================================================
Findings:
  - Sessions with <1KB data: {len(low_data):,} ({len(low_data)/len(df)*100:.1f}%)
  - Zero-byte sessions: {len(zero_data):,} ({len(zero_data)/len(df)*100:.1f}%)
  - Weak signal zones show higher % of failed transfers
  
Root Cause:
  - Poor signal causing connection drops
  - Authentication failures
  - Interference from other wireless sources
  - Possible rogue APs or channel congestion
  
Solutions:
  1. Optimize channel planning to reduce co-channel interference
  2. Implement WPA3 for more reliable authentication
  3. Set up automated monitoring to detect failed sessions
  4. DFS (Dynamic Frequency Selection) for less congested channels
  
Tools:
  - Cisco CleanAir for interference detection
  - MetaGeek Chanalyzer for spectrum analysis
  - SolarWinds NPM for monitoring
  - PRTG Network Monitor

=================================================================
PAIN POINT 5: Weekend/Off-Peak Underutilization
=================================================================
Findings:
  - Significant drop in usage during weekends
  - Large daily variation in user count
  - Infrastructure sized for peak but underutilized off-peak
  
Root Cause:
  - University usage patterns (weekday-heavy)
  - No incentive for weekend campus Wi-Fi usage
  
Solutions:
  1. Power-saving mode for APs during low-usage periods
  2. Scale down radio power during off-peak to save energy
  3. Offer community Wi-Fi services during off-peak  
  4. Schedule AP firmware updates during low-usage windows
  
Tools:
  - Cisco DNA Center scheduling policies
  - Green AP technology
  - Aruba Dynamic Segmentation

=================================================================
PAIN POINT 6: Building-Specific Issues
=================================================================
Findings:
  - Significant signal quality variance between buildings
  - Some buildings have disproportionate data transfer vs users
  - Floor-level analysis shows specific problem areas
  
Solutions:
  1. Building-specific AP placement optimization
  2. Floor-by-floor coverage assessment
  3. Install mesh networking in problematic buildings
  4. Consider PoE switches for easy AP deployment
  
Tools:
  - AirMagnet Survey Pro
  - Ubiquiti UniFi for mesh networking
  - Generic cabling infrastructure assessment
""")

# Compute dow_stats for summary
day_order_num = [0, 1, 2, 3, 4, 5, 6]
dow_stats = df.groupby('day_of_week').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    avg_rssi=('rssi', 'mean')
).reindex(day_order_num)

hourly_stats = df.groupby('hour').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    avg_rssi=('rssi', 'mean')
).reset_index()

# Create final summary visualization
fig, axes = plt.subplots(2, 3, figsize=(24, 16))
fig.suptitle('KMUTNB Wi-Fi Network - Executive Summary Dashboard', fontsize=18, fontweight='bold', y=0.98)

# 1. Overall RSSI Quality
ax = axes[0, 0]
rssi_dist = df['rssi_quality'].value_counts().reindex(rssi_quality_order)
colors = [rssi_colors_map[q] for q in rssi_dist.index]
wedges, texts, autotexts = ax.pie(rssi_dist.values, labels=rssi_dist.index, autopct='%1.1f%%',
       colors=colors, startangle=90, textprops={'fontsize': 8})
ax.set_title(f'Overall Signal Quality\n({total_sessions:,} sessions)', fontsize=12, fontweight='bold')

# 2. Sessions by Building
ax = axes[0, 1]
bldg_counts = df['BuildingName'].value_counts()
ax.barh(range(len(bldg_counts)), bldg_counts.values, color=plt.cm.viridis(np.linspace(0.3, 0.9, len(bldg_counts))))
ax.set_yticks(range(len(bldg_counts)))
ax.set_yticklabels(bldg_counts.index, fontsize=7)
ax.set_xlabel('Sessions')
ax.set_title('Sessions by Building', fontsize=12, fontweight='bold')
ax.invert_yaxis()

# 3. Peak hour usage
ax = axes[0, 2]
ax.fill_between(hourly_stats['hour'], hourly_stats['sessions'], alpha=0.3, color='steelblue')
ax.plot(hourly_stats['hour'], hourly_stats['sessions'], 'o-', color='steelblue')
ax.set_xlabel('Hour')
ax.set_ylabel('Sessions')
ax.set_title('Hourly Usage Pattern', fontsize=12, fontweight='bold')
ax.set_xticks(range(0, 24, 3))

# 4. Key Metrics
ax = axes[1, 0]
ax.axis('off')
metrics = [
    f"Total Sessions: {total_sessions:,}",
    f"Unique Users: {df['Username'].nunique():,}",
    f"Unique APs: {df['apName'].nunique()}",
    f"Total Data: {df['txRxBytes'].sum()/(1024**3):.1f} GB",
    f"Weak Signal: {weak_pct:.1f}%",
    f"Very Poor Signal: {poor_pct:.1f}%",
    f"WiFi 6 Adoption: {len(wifi6_sessions)/len(df)*100:.1f}%",
    f"Failed Sessions (<1KB): {len(low_data)/len(df)*100:.1f}%",
    f"Avg RSSI: {df['rssi'].mean():.1f} dBm",
    f"Avg SNR: {df['snr'].mean():.1f} dB"
]
for i, m in enumerate(metrics):
    color = '#e74c3c' if 'Weak' in m or 'Poor' in m or 'Failed' in m else '#2c3e50'
    ax.text(0.05, 0.95 - i*0.1, m, fontsize=11, fontweight='bold', color=color,
            transform=ax.transAxes, family='monospace')
ax.set_title('Key Performance Metrics', fontsize=12, fontweight='bold')

# 5. Account type distribution
ax = axes[1, 1]
acct_counts = df['account_type'].value_counts()
ax.barh(range(len(acct_counts)), acct_counts.values, 
        color=plt.cm.Set2(np.linspace(0, 0.8, len(acct_counts))), edgecolor='white')
ax.set_yticks(range(len(acct_counts)))
ax.set_yticklabels(acct_counts.index, fontsize=9)
ax.set_xlabel('Sessions')
ax.set_title('Sessions by Account Type', fontsize=12, fontweight='bold')
ax.invert_yaxis()
for i, val in enumerate(acct_counts.values):
    ax.text(val + max(acct_counts.values)*0.01, i, f'{val:,} ({val/len(df)*100:.1f}%)', va='center', fontsize=8)

# 6. Day of week
ax = axes[1, 2]
dow_colors = ['#3498db']*5 + ['#e74c3c']*2
ax.bar(range(7), dow_stats['sessions'].values, color=dow_colors, edgecolor='white')
ax.set_xticks(range(7))
ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax.set_ylabel('Sessions')
ax.set_title('Weekly Pattern (Red=Weekend)', fontsize=12, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('output/executive_summary_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[Saved] output/executive_summary_dashboard.png")

print("\n" + "=" * 70)
print("ALL ANALYSIS COMPLETE!")
print("=" * 70)
print(f"Total output files saved to: output/")
