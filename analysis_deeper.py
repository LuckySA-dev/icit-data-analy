"""
ICIT Data Insight & Analytics Challenge 2026
DEEP INSIGHT ANALYSIS - Additional findings with solutions
Generates matplotlib PNGs for new insights
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Tahoma'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

print("Loading dataset...")
df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day_of_week'] = df['sessionStartDateTime'].dt.dayofweek
df['date'] = df['sessionStartDateTime'].dt.date
df['txRxBytes_MB'] = df['txRxBytes'] / (1024**2)
df['txBytes_MB'] = df['txBytes'] / (1024**2)
df['rxBytes_MB'] = df['rxBytes'] / (1024**2)
df['is_zero'] = df['txRxBytes'] == 0
df['is_failed'] = df['txRxBytes'] < 1024  # <1KB = likely failed

DOW_NAMES = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
HOUR_LABELS = [f'{h:02d}:00' for h in range(24)]

def classify_rssi(rssi):
    if rssi >= -50: return 'Excellent'
    elif rssi >= -60: return 'Very Good'
    elif rssi >= -67: return 'Good'
    elif rssi >= -70: return 'Fair'
    elif rssi >= -80: return 'Weak'
    else: return 'Very Poor'

df['rssi_quality'] = df['rssi'].apply(classify_rssi)

INSIGHT_RESULTS = {}

# =====================================================
# INSIGHT 7: User Roaming Pattern Analysis
# =====================================================
print("\n=== INSIGHT 7: User Roaming Patterns ===")
user_ap_count = df.groupby('Username')['apName'].nunique()
user_bldg_count = df.groupby('Username')['Building'].nunique()

roaming_stats = pd.DataFrame({
    'ap_count': user_ap_count,
    'bldg_count': user_bldg_count
})
roaming_stats['is_roamer'] = roaming_stats['ap_count'] > 3
roaming_stats['is_multi_bldg'] = roaming_stats['bldg_count'] > 1

print(f"  Users connecting to 1 AP only: {(roaming_stats['ap_count']==1).sum()} ({(roaming_stats['ap_count']==1).mean()*100:.1f}%)")
print(f"  Users connecting to 2-3 APs: {((roaming_stats['ap_count']>=2)&(roaming_stats['ap_count']<=3)).sum()}")
print(f"  Roamers (>3 APs): {roaming_stats['is_roamer'].sum()} ({roaming_stats['is_roamer'].mean()*100:.1f}%)")
print(f"  Multi-building users: {roaming_stats['is_multi_bldg'].sum()} ({roaming_stats['is_multi_bldg'].mean()*100:.1f}%)")
print(f"  Max APs by single user: {roaming_stats['ap_count'].max()}")
print(f"  Max buildings by single user: {roaming_stats['bldg_count'].max()}")

top_roamers = roaming_stats.nlargest(10, 'ap_count')
print(f"\n  Top roamers (by AP count):")
for u, row in top_roamers.iterrows():
    print(f"    {u}: {row['ap_count']} APs, {row['bldg_count']} buildings")

INSIGHT_RESULTS['roaming'] = {
    'single_ap_pct': float((roaming_stats['ap_count']==1).mean()*100),
    'roamer_pct': float(roaming_stats['is_roamer'].mean()*100),
    'multi_bldg_pct': float(roaming_stats['is_multi_bldg'].mean()*100),
    'max_aps': int(roaming_stats['ap_count'].max()),
    'max_bldgs': int(roaming_stats['bldg_count'].max()),
}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('INSIGHT 7: User Roaming Pattern Analysis', fontsize=16, fontweight='bold', color='#1a1a2e')

# AP count distribution
ap_bins = [0, 1, 2, 4, 10, 20, 50, 100]
ap_labels = ['1', '2-3', '4-9', '10-19', '20-49', '50-99', '100+']
ap_counts = pd.cut(roaming_stats['ap_count'], bins=ap_bins, labels=ap_labels).value_counts().sort_index()
colors = ['#2ecc71','#27ae60','#f39c12','#e67e22','#e74c3c','#c0392b','#8e44ad']
axes[0].bar(ap_counts.index, ap_counts.values, color=colors[:len(ap_counts)])
axes[0].set_title('Users by Number of APs Connected', fontweight='bold')
axes[0].set_xlabel('Number of Unique APs')
axes[0].set_ylabel('Number of Users')
for i, v in enumerate(ap_counts.values):
    if v > 0:
        axes[0].text(i, v + 30, str(v), ha='center', fontsize=9, fontweight='bold')

# Building count distribution
bldg_counts = roaming_stats['bldg_count'].value_counts().sort_index()
colors2 = ['#3498db','#2980b9','#e67e22','#e74c3c','#c0392b','#8e44ad']
axes[1].bar(bldg_counts.index, bldg_counts.values, color=colors2[:len(bldg_counts)])
axes[1].set_title('Users by Number of Buildings Visited', fontweight='bold')
axes[1].set_xlabel('Number of Buildings')
axes[1].set_ylabel('Number of Users')
for i, (k, v) in enumerate(bldg_counts.items()):
    axes[1].text(k, v + 30, str(v), ha='center', fontsize=9, fontweight='bold')

# Roaming vs signal quality
roamers = roaming_stats[roaming_stats['is_roamer']].index
non_roamers = roaming_stats[~roaming_stats['is_roamer']].index
roamer_rssi = df[df['Username'].isin(roamers)]['rssi'].mean()
non_roamer_rssi = df[df['Username'].isin(non_roamers)]['rssi'].mean()
roamer_fail = df[df['Username'].isin(roamers)]['is_failed'].mean()*100
non_roamer_fail = df[df['Username'].isin(non_roamers)]['is_failed'].mean()*100

x = np.arange(2)
w = 0.35
bars1 = axes[2].bar(x - w/2, [non_roamer_rssi, roamer_rssi], w, label='Avg RSSI (dBm)', color=['#3498db','#e74c3c'])
ax2r = axes[2].twinx()
bars2 = ax2r.bar(x + w/2, [non_roamer_fail, roamer_fail], w, label='Failed Sessions %', color=['#85c1e9','#f1948a'], alpha=0.7)
axes[2].set_xticks(x)
axes[2].set_xticklabels(['Non-Roamers\n(≤3 APs)', 'Roamers\n(>3 APs)'])
axes[2].set_ylabel('Avg RSSI (dBm)')
ax2r.set_ylabel('Failed Sessions %')
axes[2].set_title('Signal Quality: Roamers vs Non-Roamers', fontweight='bold')
axes[2].legend(loc='upper left')
ax2r.legend(loc='upper right')

for bar in bars1:
    axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f'{bar.get_height():.1f}', ha='center', fontsize=9, fontweight='bold')
for bar in bars2:
    ax2r.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, f'{bar.get_height():.1f}%', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('output/insight_7_roaming_patterns.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_7_roaming_patterns.png")

# =====================================================
# INSIGHT 8: Channel Congestion Analysis
# =====================================================
print("\n=== INSIGHT 8: Channel Congestion ===")
channel_stats = df.groupby('channel').agg(
    sessions=('id', 'count'),
    users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
    fail_rate=('is_failed', 'mean'),
).sort_values('sessions', ascending=False)

print(f"  Total unique channels: {len(channel_stats)}")
print(f"  Top 5 most used channels:")
for ch, row in channel_stats.head(5).iterrows():
    print(f"    Ch {ch}: {row['sessions']:,.0f} sessions, RSSI={row['avg_rssi']:.1f}, SNR={row['avg_snr']:.1f}, Fail={row['fail_rate']*100:.1f}%")

# Identify 2.4GHz vs 5GHz channels
channel_stats['band'] = channel_stats.index.map(lambda c: '2.4 GHz' if c <= 14 else '5 GHz')
band_summary = channel_stats.groupby('band').agg(
    sessions=('sessions', 'sum'),
    users=('users', 'sum'),
    avg_rssi=('avg_rssi', 'mean'),
    avg_snr=('avg_snr', 'mean'),
    total_GB=('total_GB', 'sum'),
    fail_rate=('fail_rate', 'mean'),
)
print(f"\n  Band comparison:")
for band, row in band_summary.iterrows():
    print(f"    {band}: {row['sessions']:,.0f} sessions, RSSI={row['avg_rssi']:.1f}, SNR={row['avg_snr']:.1f}")

INSIGHT_RESULTS['channel'] = {
    'total_channels': int(len(channel_stats)),
    'top_channel': int(channel_stats.index[0]),
    'top_channel_sessions': int(channel_stats.iloc[0]['sessions']),
}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('INSIGHT 8: Channel Congestion Analysis', fontsize=16, fontweight='bold', color='#1a1a2e')

# Top 15 channels by sessions
top_ch = channel_stats.head(15)
colors_ch = ['#e74c3c' if c <= 14 else '#3498db' for c in top_ch.index]
axes[0,0].barh([f'Ch {c}' for c in top_ch.index], top_ch['sessions'], color=colors_ch)
axes[0,0].set_title('Top 15 Channels by Session Count', fontweight='bold')
axes[0,0].set_xlabel('Sessions')
axes[0,0].legend(handles=[
    mpatches.Patch(color='#e74c3c', label='2.4 GHz'),
    mpatches.Patch(color='#3498db', label='5 GHz')
])

# RSSI by channel
axes[0,1].scatter(channel_stats.index, channel_stats['avg_rssi'], 
                  s=channel_stats['sessions']/200, alpha=0.7,
                  c=['#e74c3c' if c<=14 else '#3498db' for c in channel_stats.index])
axes[0,1].axhline(y=-70, color='orange', linestyle='--', alpha=0.5, label='Fair threshold')
axes[0,1].axhline(y=-80, color='red', linestyle='--', alpha=0.5, label='Weak threshold')
axes[0,1].set_title('RSSI by Channel (bubble=sessions)', fontweight='bold')
axes[0,1].set_xlabel('Channel Number')
axes[0,1].set_ylabel('Avg RSSI (dBm)')
axes[0,1].legend()

# Band comparison
bands = band_summary.index.tolist()
x = np.arange(len(bands))
w = 0.3
axes[1,0].bar(x - w, band_summary['avg_rssi'], w, label='Avg RSSI', color=['#e74c3c','#3498db'])
ax_snr = axes[1,0].twinx()
ax_snr.bar(x + w, band_summary['avg_snr'], w, label='Avg SNR', color=['#f1948a','#85c1e9'], alpha=0.7)
axes[1,0].set_xticks(x)
axes[1,0].set_xticklabels(bands)
axes[1,0].set_ylabel('Avg RSSI (dBm)')
ax_snr.set_ylabel('Avg SNR (dB)')
axes[1,0].set_title('Signal Quality by Frequency Band', fontweight='bold')
axes[1,0].legend(loc='upper left')
ax_snr.legend(loc='upper right')

# Fail rate by channel
top20 = channel_stats.head(20)
colors_fail = ['#e74c3c' if r > 0.1 else '#f39c12' if r > 0.05 else '#2ecc71' for r in top20['fail_rate']]
axes[1,1].bar([f'Ch{c}' for c in top20.index], top20['fail_rate']*100, color=colors_fail)
axes[1,1].set_title('Failed Session Rate by Channel (Top 20)', fontweight='bold')
axes[1,1].set_ylabel('Failed Rate %')
axes[1,1].tick_params(axis='x', rotation=45)
axes[1,1].axhline(y=10, color='red', linestyle='--', alpha=0.5, label='10% threshold')
axes[1,1].legend()

plt.tight_layout()
plt.savefig('output/insight_8_channel_congestion.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_8_channel_congestion.png")

# =====================================================
# INSIGHT 9: Weekend vs Weekday & Time-based Degradation
# =====================================================
print("\n=== INSIGHT 9: Weekday vs Weekend Signal Degradation ===")
df['is_weekend'] = df['day_of_week'].isin([5, 6])

time_signal = df.groupby(['is_weekend', 'hour']).agg(
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    sessions=('id', 'count'),
    users=('Username', 'nunique'),
    fail_rate=('is_failed', 'mean'),
    weak_pct=('rssi', lambda x: (x <= -71).mean() * 100),
).reset_index()

weekday = time_signal[~time_signal['is_weekend']]
weekend = time_signal[time_signal['is_weekend']]

print(f"  Weekday avg RSSI: {df[~df['is_weekend']]['rssi'].mean():.1f} dBm")
print(f"  Weekend avg RSSI: {df[df['is_weekend']]['rssi'].mean():.1f} dBm")
print(f"  Weekday avg sessions/hour: {weekday['sessions'].mean():.0f}")
print(f"  Weekend avg sessions/hour: {weekend['sessions'].mean():.0f}")

# Find peak degradation hours
peak_hours = weekday.nlargest(3, 'sessions')
print(f"\n  Peak weekday hours (most sessions):")
for _, row in peak_hours.iterrows():
    print(f"    {int(row['hour']):02d}:00 - {row['sessions']:,.0f} sessions, RSSI={row['avg_rssi']:.1f}, Weak={row['weak_pct']:.1f}%")

INSIGHT_RESULTS['time_degradation'] = {
    'weekday_rssi': float(df[~df['is_weekend']]['rssi'].mean()),
    'weekend_rssi': float(df[df['is_weekend']]['rssi'].mean()),
    'peak_hour': int(peak_hours.iloc[0]['hour']),
    'peak_sessions': int(peak_hours.iloc[0]['sessions']),
    'peak_weak_pct': float(peak_hours.iloc[0]['weak_pct']),
}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('INSIGHT 9: Weekday vs Weekend Signal Quality Over Time', fontsize=16, fontweight='bold', color='#1a1a2e')

# RSSI over hour
axes[0,0].plot(weekday['hour'], weekday['avg_rssi'], 'b-o', label='Weekday', linewidth=2, markersize=5)
axes[0,0].plot(weekend['hour'], weekend['avg_rssi'], 'r-s', label='Weekend', linewidth=2, markersize=5)
axes[0,0].axhline(y=-70, color='orange', linestyle='--', alpha=0.3)
axes[0,0].axhline(y=-80, color='red', linestyle='--', alpha=0.3)
axes[0,0].fill_between(weekday['hour'], weekday['avg_rssi'], weekend['avg_rssi'], alpha=0.1, color='purple')
axes[0,0].set_title('Average RSSI by Hour', fontweight='bold')
axes[0,0].set_xlabel('Hour')
axes[0,0].set_ylabel('Avg RSSI (dBm)')
axes[0,0].legend()
axes[0,0].set_xticks(range(0,24,2))

# Sessions over hour
axes[0,1].bar(weekday['hour']-0.2, weekday['sessions'], 0.4, label='Weekday', color='#3498db', alpha=0.8)
axes[0,1].bar(weekend['hour']+0.2, weekend['sessions'], 0.4, label='Weekend', color='#e74c3c', alpha=0.8)
axes[0,1].set_title('Session Volume by Hour', fontweight='bold')
axes[0,1].set_xlabel('Hour')
axes[0,1].set_ylabel('Sessions')
axes[0,1].legend()
axes[0,1].set_xticks(range(0,24,2))

# Weak% over hour
axes[1,0].plot(weekday['hour'], weekday['weak_pct'], 'b-o', label='Weekday', linewidth=2)
axes[1,0].plot(weekend['hour'], weekend['weak_pct'], 'r-s', label='Weekend', linewidth=2)
axes[1,0].axhline(y=70, color='red', linestyle='--', alpha=0.3, label='70% danger zone')
axes[1,0].fill_between(weekday['hour'], weekday['weak_pct'], alpha=0.15, color='blue')
axes[1,0].fill_between(weekend['hour'], weekend['weak_pct'], alpha=0.15, color='red')
axes[1,0].set_title('Weak Signal Percentage by Hour', fontweight='bold')
axes[1,0].set_xlabel('Hour')
axes[1,0].set_ylabel('Weak Sessions %')
axes[1,0].legend()
axes[1,0].set_xticks(range(0,24,2))

# Heatmap: day of week x hour
pivot_rssi = df.pivot_table(values='rssi', index='day_of_week', columns='hour', aggfunc='mean')
pivot_rssi.index = [DOW_NAMES[i] for i in pivot_rssi.index]
im = axes[1,1].imshow(pivot_rssi.values, cmap='RdYlGn', aspect='auto', vmin=-80, vmax=-65)
axes[1,1].set_yticks(range(7))
axes[1,1].set_yticklabels(pivot_rssi.index)
axes[1,1].set_xticks(range(0,24,2))
axes[1,1].set_xticklabels([f'{h:02d}' for h in range(0,24,2)])
axes[1,1].set_title('RSSI Heatmap (Day × Hour)', fontweight='bold')
axes[1,1].set_xlabel('Hour')
plt.colorbar(im, ax=axes[1,1], label='RSSI (dBm)')

plt.tight_layout()
plt.savefig('output/insight_9_weekday_weekend.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_9_weekday_weekend.png")

# =====================================================
# INSIGHT 10: WiFi Radio Type Performance Comparison
# =====================================================
print("\n=== INSIGHT 10: WiFi Radio Technology Performance ===")
radio_stats = df.groupby('radioType').agg(
    sessions=('id', 'count'),
    users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
    fail_rate=('is_failed', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean'),
).sort_values('sessions', ascending=False)

print(f"  Radio types found: {list(radio_stats.index)}")
for rt, row in radio_stats.iterrows():
    print(f"    {rt}: {row['sessions']:,.0f} sessions ({row['sessions']/len(df)*100:.1f}%), "
          f"RSSI={row['avg_rssi']:.1f}, SNR={row['avg_snr']:.1f}, Fail={row['fail_rate']*100:.1f}%, "
          f"Avg data={row['avg_data_MB']:.1f} MB/session")

# Per building x radio type
bldg_radio = df.groupby(['Building', 'radioType']).agg(
    sessions=('id', 'count'),
    avg_rssi=('rssi', 'mean'),
).reset_index()
bldg_radio_pivot = bldg_radio.pivot_table(values='sessions', index='Building', columns='radioType', fill_value=0)

INSIGHT_RESULTS['radio'] = {rt: {
    'sessions': int(row['sessions']),
    'pct': float(row['sessions']/len(df)*100),
    'rssi': float(row['avg_rssi']),
    'snr': float(row['avg_snr']),
    'fail_rate': float(row['fail_rate']*100),
} for rt, row in radio_stats.iterrows()}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('INSIGHT 10: WiFi Radio Technology Performance', fontsize=16, fontweight='bold', color='#1a1a2e')

# Sessions by radio type
radio_colors = {'802.11ax': '#2ecc71', '802.11ac': '#3498db', '802.11n': '#e67e22', '802.11a': '#e74c3c', '802.11g': '#9b59b6'}
colors_r = [radio_colors.get(r, '#95a5a6') for r in radio_stats.index]
axes[0,0].pie(radio_stats['sessions'], labels=radio_stats.index, autopct='%1.1f%%', colors=colors_r, 
              startangle=90, textprops={'fontsize': 10})
axes[0,0].set_title('Session Distribution by Radio Type', fontweight='bold')

# RSSI comparison
x = np.arange(len(radio_stats))
axes[0,1].bar(x, radio_stats['avg_rssi'], color=colors_r, edgecolor='white')
axes[0,1].set_xticks(x)
axes[0,1].set_xticklabels(radio_stats.index, rotation=15)
axes[0,1].set_ylabel('Avg RSSI (dBm)')
axes[0,1].set_title('Avg RSSI by Radio Type', fontweight='bold')
axes[0,1].axhline(y=-70, color='orange', linestyle='--', alpha=0.5)
for i, v in enumerate(radio_stats['avg_rssi']):
    axes[0,1].text(i, v + 0.3, f'{v:.1f}', ha='center', fontsize=9, fontweight='bold')

# Avg data per session
axes[1,0].bar(x, radio_stats['avg_data_MB'], color=colors_r, edgecolor='white')
axes[1,0].set_xticks(x)
axes[1,0].set_xticklabels(radio_stats.index, rotation=15)
axes[1,0].set_ylabel('Avg Data per Session (MB)')
axes[1,0].set_title('Data Efficiency by Radio Type', fontweight='bold')
for i, v in enumerate(radio_stats['avg_data_MB']):
    axes[1,0].text(i, v + 0.3, f'{v:.1f}', ha='center', fontsize=9, fontweight='bold')

# Per building radio distribution (stacked bar)
if len(bldg_radio_pivot.columns) > 0:
    bldg_radio_pct = bldg_radio_pivot.div(bldg_radio_pivot.sum(axis=1), axis=0) * 100
    bottom = np.zeros(len(bldg_radio_pct))
    x_b = np.arange(len(bldg_radio_pct))
    for col in bldg_radio_pct.columns:
        c = radio_colors.get(col, '#95a5a6')
        axes[1,1].bar(x_b, bldg_radio_pct[col], bottom=bottom, label=col, color=c)
        bottom += bldg_radio_pct[col].values
    axes[1,1].set_xticks(x_b)
    axes[1,1].set_xticklabels(bldg_radio_pct.index, rotation=15)
    axes[1,1].set_ylabel('Percentage %')
    axes[1,1].set_title('Radio Type Distribution per Building', fontweight='bold')
    axes[1,1].legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('output/insight_10_radio_performance.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_10_radio_performance.png")

# =====================================================
# INSIGHT 11: Upload/Download Ratio Anomaly per Building
# =====================================================
print("\n=== INSIGHT 11: Upload/Download Ratio Anomaly ===")
bldg_ul_dl = df.groupby('Building').agg(
    upload_GB=('txBytes', lambda x: x.sum()/(1024**3)),
    download_GB=('rxBytes', lambda x: x.sum()/(1024**3)),
).reset_index()
bldg_ul_dl['ratio'] = bldg_ul_dl['upload_GB'] / bldg_ul_dl['download_GB'].replace(0, 0.001)
bldg_ul_dl['total_GB'] = bldg_ul_dl['upload_GB'] + bldg_ul_dl['download_GB']

print(f"  Overall Upload: {bldg_ul_dl['upload_GB'].sum():.1f} GB, Download: {bldg_ul_dl['download_GB'].sum():.1f} GB")
print(f"  Overall UL/DL ratio: {bldg_ul_dl['upload_GB'].sum()/bldg_ul_dl['download_GB'].sum():.1f}x")
for _, row in bldg_ul_dl.iterrows():
    print(f"    {row['Building']}: UL={row['upload_GB']:.1f} GB, DL={row['download_GB']:.1f} GB, Ratio={row['ratio']:.1f}x")

# Per hour UL/DL
hourly_ul_dl = df.groupby('hour').agg(
    upload_GB=('txBytes', lambda x: x.sum()/(1024**3)),
    download_GB=('rxBytes', lambda x: x.sum()/(1024**3)),
).reset_index()
hourly_ul_dl['ratio'] = hourly_ul_dl['upload_GB'] / hourly_ul_dl['download_GB'].replace(0, 0.001)

INSIGHT_RESULTS['ul_dl'] = {
    'total_upload_GB': float(bldg_ul_dl['upload_GB'].sum()),
    'total_download_GB': float(bldg_ul_dl['download_GB'].sum()),
    'ratio': float(bldg_ul_dl['upload_GB'].sum()/bldg_ul_dl['download_GB'].sum()),
}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('INSIGHT 11: Upload/Download Ratio Anomaly', fontsize=16, fontweight='bold', color='#1a1a2e')

# Per building stacked
x = np.arange(len(bldg_ul_dl))
axes[0].bar(x, bldg_ul_dl['upload_GB'], label='Upload', color='#e74c3c')
axes[0].bar(x, bldg_ul_dl['download_GB'], bottom=bldg_ul_dl['upload_GB'], label='Download', color='#3498db')
axes[0].set_xticks(x)
axes[0].set_xticklabels(bldg_ul_dl['Building'])
axes[0].set_ylabel('Data (GB)')
axes[0].set_title('Upload vs Download per Building', fontweight='bold')
axes[0].legend()

# UL/DL ratio
axes[1].bar(x, bldg_ul_dl['ratio'], color=['#e74c3c' if r > 15 else '#f39c12' if r > 10 else '#2ecc71' for r in bldg_ul_dl['ratio']])
axes[1].set_xticks(x)
axes[1].set_xticklabels(bldg_ul_dl['Building'])
axes[1].set_ylabel('Upload/Download Ratio')
axes[1].set_title('UL/DL Ratio per Building (Normal ≈ 1:3)', fontweight='bold')
axes[1].axhline(y=1, color='green', linestyle='--', alpha=0.5, label='Normal (1:1)')
for i, v in enumerate(bldg_ul_dl['ratio']):
    axes[1].text(i, v + 0.2, f'{v:.1f}x', ha='center', fontsize=9, fontweight='bold')
axes[1].legend()

# Hourly trend
axes[2].plot(hourly_ul_dl['hour'], hourly_ul_dl['upload_GB'], 'r-o', label='Upload', linewidth=2)
axes[2].plot(hourly_ul_dl['hour'], hourly_ul_dl['download_GB'], 'b-s', label='Download', linewidth=2)
axes[2].fill_between(hourly_ul_dl['hour'], hourly_ul_dl['upload_GB'], alpha=0.2, color='red')
axes[2].fill_between(hourly_ul_dl['hour'], hourly_ul_dl['download_GB'], alpha=0.2, color='blue')
axes[2].set_title('Hourly Upload vs Download Trend', fontweight='bold')
axes[2].set_xlabel('Hour')
axes[2].set_ylabel('Data (GB)')
axes[2].legend()
axes[2].set_xticks(range(0,24,2))

plt.tight_layout()
plt.savefig('output/insight_11_upload_download_ratio.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_11_upload_download_ratio.png")

# =====================================================
# INSIGHT 12: Failed Session Heatmap (Location × Time)
# =====================================================
print("\n=== INSIGHT 12: Failed Session Patterns ===")
fail_by_bldg_hour = df.groupby(['Building', 'hour']).agg(
    sessions=('id', 'count'),
    failed=('is_failed', 'sum'),
    zero_data=('is_zero', 'sum'),
).reset_index()
fail_by_bldg_hour['fail_pct'] = fail_by_bldg_hour['failed'] / fail_by_bldg_hour['sessions'] * 100

# Top failure spots
fail_by_ap = df.groupby('apName').agg(
    sessions=('id', 'count'),
    failed=('is_failed', 'sum'),
    fail_rate=('is_failed', 'mean'),
    avg_rssi=('rssi', 'mean'),
).reset_index()
fail_by_ap['fail_pct'] = fail_by_ap['fail_rate'] * 100
high_fail_aps = fail_by_ap[(fail_by_ap['sessions'] > 100) & (fail_by_ap['fail_pct'] > 10)].sort_values('fail_pct', ascending=False)

print(f"  Total failed sessions (<1KB): {df['is_failed'].sum():,} ({df['is_failed'].mean()*100:.1f}%)")
print(f"  Total zero-byte sessions: {df['is_zero'].sum():,} ({df['is_zero'].mean()*100:.1f}%)")
print(f"  APs with >10% failure rate (min 100 sessions): {len(high_fail_aps)}")
if len(high_fail_aps) > 0:
    print(f"  Top 5 worst APs:")
    for _, row in high_fail_aps.head(5).iterrows():
        print(f"    {row['apName']}: {row['fail_pct']:.1f}% fail ({row['sessions']:,} sessions, RSSI={row['avg_rssi']:.1f})")

INSIGHT_RESULTS['failures'] = {
    'total_failed': int(df['is_failed'].sum()),
    'failed_pct': float(df['is_failed'].mean()*100),
    'zero_byte_pct': float(df['is_zero'].mean()*100),
    'high_fail_aps': int(len(high_fail_aps)),
}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('INSIGHT 12: Failed Session Pattern Analysis', fontsize=16, fontweight='bold', color='#1a1a2e')

# Heatmap: building x hour fail rate
pivot_fail = fail_by_bldg_hour.pivot_table(values='fail_pct', index='Building', columns='hour', fill_value=0)
im = axes[0,0].imshow(pivot_fail.values, cmap='Reds', aspect='auto', vmin=0, vmax=20)
axes[0,0].set_yticks(range(len(pivot_fail.index)))
axes[0,0].set_yticklabels(pivot_fail.index)
axes[0,0].set_xticks(range(0,24,2))
axes[0,0].set_xticklabels([f'{h:02d}' for h in range(0,24,2)])
axes[0,0].set_title('Failed Session % (Building × Hour)', fontweight='bold')
plt.colorbar(im, ax=axes[0,0], label='Failed %')

# Top failed APs
if len(high_fail_aps) > 0:
    top_fail = high_fail_aps.head(15)
    colors_f = ['#c0392b' if r > 20 else '#e74c3c' if r > 15 else '#f39c12' for r in top_fail['fail_pct']]
    axes[0,1].barh(top_fail['apName'], top_fail['fail_pct'], color=colors_f)
    axes[0,1].set_title('Top APs by Failure Rate (>10%, min 100 sessions)', fontweight='bold')
    axes[0,1].set_xlabel('Failed Session %')

# Failed by hour
hourly_fail = df.groupby('hour').agg(fail_pct=('is_failed', 'mean')).reset_index()
hourly_fail['fail_pct'] *= 100
colors_h = ['#e74c3c' if f > 10 else '#f39c12' if f > 7 else '#2ecc71' for f in hourly_fail['fail_pct']]
axes[1,0].bar(hourly_fail['hour'], hourly_fail['fail_pct'], color=colors_h)
axes[1,0].set_title('Failed Session Rate by Hour', fontweight='bold')
axes[1,0].set_xlabel('Hour')
axes[1,0].set_ylabel('Failed %')
axes[1,0].set_xticks(range(0,24,2))
axes[1,0].axhline(y=10, color='red', linestyle='--', alpha=0.5)

# RSSI vs fail rate scatter
axes[1,1].scatter(fail_by_ap['avg_rssi'], fail_by_ap['fail_pct'], 
                  s=fail_by_ap['sessions']/50, alpha=0.5, c='#e74c3c', edgecolors='white', linewidths=0.5)
axes[1,1].set_title('RSSI vs Failure Rate (bubble=sessions)', fontweight='bold')
axes[1,1].set_xlabel('Avg RSSI (dBm)')
axes[1,1].set_ylabel('Failed Session %')
axes[1,1].axvline(x=-70, color='orange', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('output/insight_12_failed_sessions.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_12_failed_sessions.png")

# =====================================================
# INSIGHT 13: Device Type Performance per Building
# =====================================================
print("\n=== INSIGHT 13: Device Ecosystem Analysis ===")
device_stats = df.groupby('deviceType').agg(
    sessions=('id', 'count'),
    users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    fail_rate=('is_failed', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean'),
).sort_values('sessions', ascending=False)

print(f"  Device types: {len(device_stats)}")
for dt, row in device_stats.iterrows():
    print(f"    {dt}: {row['sessions']:,} ({row['sessions']/len(df)*100:.1f}%), RSSI={row['avg_rssi']:.1f}, Fail={row['fail_rate']*100:.1f}%")

# OS vendor analysis
os_stats = df.groupby('osType').agg(
    sessions=('id', 'count'),
    avg_rssi=('rssi', 'mean'),
    fail_rate=('is_failed', 'mean'),
).sort_values('sessions', ascending=False).head(10)

INSIGHT_RESULTS['device'] = {dt: {
    'sessions': int(row['sessions']),
    'rssi': float(row['avg_rssi']),
    'fail_rate': float(row['fail_rate']*100),
} for dt, row in device_stats.iterrows()}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('INSIGHT 13: Device Ecosystem & Performance', fontsize=16, fontweight='bold', color='#1a1a2e')

# Device type pie
dev_colors = {'Smart Phone': '#3498db', 'Laptop': '#2ecc71', 'Tablet': '#e67e22', 'Desktop': '#9b59b6', 'IoT': '#e74c3c'}
colors_d = [dev_colors.get(d, '#95a5a6') for d in device_stats.index]
axes[0,0].pie(device_stats['sessions'], labels=device_stats.index, autopct='%1.1f%%',
              colors=colors_d, startangle=90, textprops={'fontsize': 10})
axes[0,0].set_title('Sessions by Device Type', fontweight='bold')

# RSSI by device
x = np.arange(len(device_stats))
axes[0,1].bar(x, device_stats['avg_rssi'], color=colors_d, edgecolor='white')
axes[0,1].set_xticks(x)
axes[0,1].set_xticklabels(device_stats.index, rotation=15)
axes[0,1].set_ylabel('Avg RSSI (dBm)')
axes[0,1].set_title('Signal Quality by Device Type', fontweight='bold')
axes[0,1].axhline(y=-70, color='orange', linestyle='--', alpha=0.5)
for i, v in enumerate(device_stats['avg_rssi']):
    axes[0,1].text(i, v + 0.3, f'{v:.1f}', ha='center', fontsize=9, fontweight='bold')

# Top OS types
x_os = np.arange(len(os_stats))
os_colors = ['#3498db' if 'Android' in o or 'Chrome' in o else '#95a5a6' if 'Unknown' in o else '#333' for o in os_stats.index]
axes[1,0].barh(os_stats.index, os_stats['sessions'], color='#3498db')
axes[1,0].set_title('Top 10 OS Types by Session Count', fontweight='bold')
axes[1,0].set_xlabel('Sessions')

# Fail rate by device per building
dev_bldg = df.groupby(['Building', 'deviceType']).agg(fail_rate=('is_failed', 'mean')).reset_index()
dev_bldg_pivot = dev_bldg.pivot_table(values='fail_rate', index='Building', columns='deviceType', fill_value=0) * 100
if len(dev_bldg_pivot.columns) > 0:
    dev_bldg_pivot.plot(kind='bar', ax=axes[1,1], colormap='Set2', edgecolor='white')
    axes[1,1].set_title('Failure Rate by Device × Building', fontweight='bold')
    axes[1,1].set_ylabel('Failed %')
    axes[1,1].legend(fontsize=8)
    axes[1,1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('output/insight_13_device_ecosystem.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_13_device_ecosystem.png")

# =====================================================
# INSIGHT 14: AP Capacity & Overload Analysis
# =====================================================
print("\n=== INSIGHT 14: AP Capacity & Overload ===")
ap_hourly = df.groupby(['apName', 'hour']).agg(
    sessions=('id', 'count'),
    users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
).reset_index()

ap_peak = ap_hourly.groupby('apName').agg(
    peak_hour_sessions=('sessions', 'max'),
    peak_hour_users=('users', 'max'),
    peak_hour=('sessions', 'idxmax'),
).reset_index()

# Merge with AP overall stats
ap_overall = df.groupby('apName').agg(
    total_sessions=('id', 'count'),
    total_users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    building=('Building', 'first'),
    floor=('Floor', 'first'),
    fail_rate=('is_failed', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
).reset_index()

ap_combined = ap_overall.merge(ap_peak, on='apName')

# Overloaded APs: >200 peak users AND poor signal
overloaded = ap_combined[(ap_combined['peak_hour_users'] > 100) & (ap_combined['avg_rssi'] < -70)]
print(f"  Overloaded APs (peak>100users + RSSI<-70): {len(overloaded)}")
for _, row in overloaded.nlargest(10, 'peak_hour_users').iterrows():
    print(f"    {row['apName']} ({row['building']}/{row['floor']}): "
          f"Peak {row['peak_hour_users']} users, RSSI={row['avg_rssi']:.1f}, {row['total_GB']:.1f} GB")

# Users per AP ratio
bldg_ap_ratio = df.groupby('Building').agg(
    users=('Username', 'nunique'),
    aps=('apName', 'nunique'),
).reset_index()
bldg_ap_ratio['users_per_ap'] = bldg_ap_ratio['users'] / bldg_ap_ratio['aps']

INSIGHT_RESULTS['capacity'] = {
    'overloaded_aps': int(len(overloaded)),
    'highest_peak_users': int(ap_combined['peak_hour_users'].max()),
    'highest_peak_ap': str(ap_combined.loc[ap_combined['peak_hour_users'].idxmax(), 'apName']),
}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('INSIGHT 14: AP Capacity & Overload Analysis', fontsize=16, fontweight='bold', color='#1a1a2e')

# Peak users per AP bar
top_aps = ap_combined.nlargest(20, 'peak_hour_users')
colors_a = ['#e74c3c' if r < -70 else '#f39c12' if r < -65 else '#2ecc71' for r in top_aps['avg_rssi']]
axes[0,0].barh(top_aps['apName'], top_aps['peak_hour_users'], color=colors_a)
axes[0,0].set_title('Top 20 APs by Peak Hour Users', fontweight='bold')
axes[0,0].set_xlabel('Peak Concurrent Users')
axes[0,0].legend(handles=[
    mpatches.Patch(color='#e74c3c', label='RSSI < -70 (Weak)'),
    mpatches.Patch(color='#f39c12', label='-70 ~ -65 (Fair)'),
    mpatches.Patch(color='#2ecc71', label='> -65 (Good)'),
], fontsize=8)

# Users per AP ratio by building
axes[0,1].bar(bldg_ap_ratio['Building'], bldg_ap_ratio['users_per_ap'], 
              color=['#e74c3c' if r > 200 else '#f39c12' if r > 100 else '#2ecc71' for r in bldg_ap_ratio['users_per_ap']])
axes[0,1].set_title('Users-to-AP Ratio per Building', fontweight='bold')
axes[0,1].set_ylabel('Users per AP')
axes[0,1].axhline(y=50, color='green', linestyle='--', alpha=0.5, label='Recommended max (50)')
axes[0,1].axhline(y=150, color='red', linestyle='--', alpha=0.5, label='Critical (150)')
for i, v in enumerate(bldg_ap_ratio['users_per_ap']):
    axes[0,1].text(i, v + 5, f'{v:.0f}', ha='center', fontsize=9, fontweight='bold')
axes[0,1].legend()

# Scatter: peak users vs avg RSSI
axes[1,0].scatter(ap_combined['peak_hour_users'], ap_combined['avg_rssi'], 
                  s=ap_combined['total_GB']*3+5, alpha=0.5, c='#3498db', edgecolors='white', linewidths=0.5)
axes[1,0].axhline(y=-70, color='orange', linestyle='--', alpha=0.3)
axes[1,0].axvline(x=100, color='red', linestyle='--', alpha=0.3)
axes[1,0].set_title('Peak Users vs Signal Quality (bubble=data volume)', fontweight='bold')
axes[1,0].set_xlabel('Peak Hour Users')
axes[1,0].set_ylabel('Avg RSSI (dBm)')
# Highlight overloaded zone
if len(overloaded) > 0:
    axes[1,0].fill_between([100, ap_combined['peak_hour_users'].max()+10], -100, -70, alpha=0.1, color='red')
    axes[1,0].text(150, -85, '⚠️ OVERLOADED ZONE', fontsize=10, color='red', fontweight='bold')

# Data throughput distribution
axes[1,1].hist(ap_combined['total_GB'], bins=30, color='#3498db', edgecolor='white', alpha=0.7)
axes[1,1].axvline(x=ap_combined['total_GB'].mean(), color='red', linestyle='--', label=f'Mean: {ap_combined["total_GB"].mean():.1f} GB')
axes[1,1].axvline(x=ap_combined['total_GB'].median(), color='green', linestyle='--', label=f'Median: {ap_combined["total_GB"].median():.1f} GB')
axes[1,1].set_title('Data Volume Distribution Across APs', fontweight='bold')
axes[1,1].set_xlabel('Total Data (GB)')
axes[1,1].set_ylabel('Number of APs')
axes[1,1].legend()

plt.tight_layout()
plt.savefig('output/insight_14_ap_capacity.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_14_ap_capacity.png")

# =====================================================
# INSIGHT 15: Account Type (Staff vs Student) Behavior
# =====================================================
print("\n=== INSIGHT 15: Staff vs Student Usage Patterns ===")
acct_stats = df.groupby('account_type').agg(
    sessions=('id', 'count'),
    users=('Username', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean'),
    total_GB=('txRxBytes', lambda x: x.sum()/(1024**3)),
    fail_rate=('is_failed', 'mean'),
).sort_values('sessions', ascending=False)

for at, row in acct_stats.iterrows():
    print(f"  {at}: {row['sessions']:,} sessions, {row['users']:,} users, RSSI={row['avg_rssi']:.1f}, "
          f"Fail={row['fail_rate']*100:.1f}%, Avg={row['avg_data_MB']:.1f}MB/session")

# Hourly pattern by account type
acct_hourly = df.groupby(['account_type', 'hour']).agg(
    sessions=('id', 'count'),
    avg_rssi=('rssi', 'mean'),
).reset_index()

INSIGHT_RESULTS['account'] = {at: {
    'sessions': int(row['sessions']),
    'users': int(row['users']),
    'rssi': float(row['avg_rssi']),
    'fail_rate': float(row['fail_rate']*100),
} for at, row in acct_stats.iterrows()}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('INSIGHT 15: Staff vs Student Usage Patterns', fontsize=16, fontweight='bold', color='#1a1a2e')

# Sessions by account type
acct_colors = {'student': '#3498db', 'staff': '#e74c3c', 'guest': '#f39c12', 'other': '#95a5a6'}
colors_ac = [acct_colors.get(a.lower(), '#95a5a6') for a in acct_stats.index]
axes[0].pie(acct_stats['sessions'], labels=acct_stats.index, autopct='%1.1f%%',
            colors=colors_ac, startangle=90, textprops={'fontsize': 11})
axes[0].set_title('Sessions by Account Type', fontweight='bold')

# Hourly pattern
for at in acct_stats.index:
    subset = acct_hourly[acct_hourly['account_type'] == at]
    c = acct_colors.get(at.lower(), '#95a5a6')
    axes[1].plot(subset['hour'], subset['sessions'], '-o', label=at, color=c, linewidth=2, markersize=4)
axes[1].set_title('Hourly Usage Pattern by Account Type', fontweight='bold')
axes[1].set_xlabel('Hour')
axes[1].set_ylabel('Sessions')
axes[1].legend()
axes[1].set_xticks(range(0,24,2))

# Comparison metrics
x = np.arange(len(acct_stats))
w = 0.3
bars1 = axes[2].bar(x - w/2, acct_stats['avg_data_MB'], w, label='Avg Data (MB/session)', color='#3498db')
ax2 = axes[2].twinx()
bars2 = ax2.bar(x + w/2, acct_stats['fail_rate']*100, w, label='Fail Rate %', color='#e74c3c', alpha=0.7)
axes[2].set_xticks(x)
axes[2].set_xticklabels(acct_stats.index)
axes[2].set_ylabel('Avg Data (MB/session)')
ax2.set_ylabel('Failed Session %')
axes[2].set_title('Data Usage vs Failure Rate', fontweight='bold')
axes[2].legend(loc='upper left')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig('output/insight_15_account_type.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  → Saved insight_15_account_type.png")

# =====================================================
# PRINT SUMMARY OF ALL NEW INSIGHTS
# =====================================================
print("\n" + "="*80)
print("SUMMARY OF ALL NEW INSIGHTS (7-15)")
print("="*80)

print("""
📡 INSIGHT 7 - User Roaming Patterns
  Problem: {roaming_pct:.1f}% of users are roamers (connect to >3 APs), suggesting handoff issues.
           Multi-building users ({multi_bldg:.1f}%) may experience disconnections during transitions.
  Solution: Enable fast roaming (802.11r/k/v), configure proper AP handoff thresholds,
           ensure seamless roaming between buildings with overlapping coverage zones.

📡 INSIGHT 8 - Channel Congestion
  Problem: {n_channels} channels in use. Some channels are heavily overloaded.
           2.4GHz channels face more interference due to limited non-overlapping channels (1, 6, 11).
  Solution: Implement dynamic channel selection (DCA), migrate high-density areas to 5GHz,
           use channel width management (reduce from 80MHz to 40MHz in congested areas).

📡 INSIGHT 9 - Weekday vs Weekend Signal Degradation
  Problem: Weekday RSSI ({wd_rssi:.1f} dBm) vs Weekend ({we_rssi:.1f} dBm) shows load-dependent degradation.
           Peak hour ({peak_h}:00) has {peak_weak:.1f}% weak sessions.
  Solution: Implement load balancing across APs during peak hours, consider
           time-based QoS policies, add temporary AP capacity for peak periods.

📡 INSIGHT 10 - WiFi Radio Technology
  Problem: Older radio types (802.11n) may drag down overall network performance.
           Mixed-mode operation reduces efficiency for newer devices.
  Solution: Upgrade legacy APs to WiFi 6/6E, enable band steering to push capable
           devices to 5GHz, consider minimum RSSI threshold to disconnect weak clients.

📡 INSIGHT 11 - Upload/Download Ratio Anomaly
  Problem: Upload ({ul_gb:.0f} GB) >> Download ({dl_gb:.0f} GB), ratio = {ul_dl_ratio:.1f}x (abnormal!).
           Normal ratio should be ~1:3 (DL > UL). This suggests monitoring/scanning traffic or misconfiguration.
  Solution: Investigate traffic patterns, check for malware/scanning activity,
           review QoS policies, implement traffic shaping for uploads.

📡 INSIGHT 12 - Failed Sessions
  Problem: {fail_pct:.1f}% failed sessions (<1KB), {zero_pct:.1f}% zero-byte sessions.
           {high_fail_aps} APs have >10% failure rate.
  Solution: Investigate DHCP/DNS failures, check authentication timeouts,
           increase AP resources, perform firmware updates on problematic APs.

📡 INSIGHT 13 - Device Ecosystem
  Problem: Different device types have varying signal reception capabilities.
           Some device types have significantly higher failure rates.
  Solution: Optimize AP settings for dominant device types, adjust beacon intervals,
           consider device-specific QoS profiles.

📡 INSIGHT 14 - AP Capacity & Overload
  Problem: {overloaded_aps} APs are overloaded (>100 peak users + poor signal).
           Highest peak: {peak_ap} with {peak_users} concurrent users.
  Solution: Split overloaded APs, add new APs in high-density areas,
           implement client load balancing, use directional antennas.

📡 INSIGHT 15 - Staff vs Student
  Problem: Different account types have different usage patterns and failure rates.
  Solution: Implement role-based QoS, prioritize staff traffic for critical work,
           allocate bandwidth proportionally to usage patterns.
""".format(
    roaming_pct=INSIGHT_RESULTS['roaming']['roamer_pct'],
    multi_bldg=INSIGHT_RESULTS['roaming']['multi_bldg_pct'],
    n_channels=INSIGHT_RESULTS['channel']['total_channels'],
    wd_rssi=INSIGHT_RESULTS['time_degradation']['weekday_rssi'],
    we_rssi=INSIGHT_RESULTS['time_degradation']['weekend_rssi'],
    peak_h=INSIGHT_RESULTS['time_degradation']['peak_hour'],
    peak_weak=INSIGHT_RESULTS['time_degradation']['peak_weak_pct'],
    ul_gb=INSIGHT_RESULTS['ul_dl']['total_upload_GB'],
    dl_gb=INSIGHT_RESULTS['ul_dl']['total_download_GB'],
    ul_dl_ratio=INSIGHT_RESULTS['ul_dl']['ratio'],
    fail_pct=INSIGHT_RESULTS['failures']['failed_pct'],
    zero_pct=INSIGHT_RESULTS['failures']['zero_byte_pct'],
    high_fail_aps=INSIGHT_RESULTS['failures']['high_fail_aps'],
    overloaded_aps=INSIGHT_RESULTS['capacity']['overloaded_aps'],
    peak_ap=INSIGHT_RESULTS['capacity']['highest_peak_ap'],
    peak_users=INSIGHT_RESULTS['capacity']['highest_peak_users'],
))

print("\n✅ All new insight PNGs generated successfully!")
print("Files created:")
for i in range(7, 16):
    print(f"  output/insight_{i}_*.png")
