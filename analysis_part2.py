"""
ICIT Data Insight & Analytics Challenge 2026
Part 2: Questions 1.4, 1.5 + Additional Views
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

# ============================================================
# 1.4 Buildings & Floors with Weak/Poor Signal (RSSI/SNR)
# ============================================================
print("\n" + "=" * 70)
print("1.4 BUILDINGS & FLOORS WITH WEAK/POOR SIGNAL QUALITY")
print("=" * 70)

# RSSI Analysis by Building-Floor
bldg_floor_rssi = df.groupby(['BuildingName', 'Floor']).agg(
    avg_rssi=('rssi', 'mean'),
    median_rssi=('rssi', 'median'),
    min_rssi=('rssi', 'min'),
    avg_snr=('snr', 'mean'),
    median_snr=('snr', 'median'),
    session_count=('id', 'count'),
    unique_users=('Username', 'nunique'),
    weak_rssi_count=('rssi', lambda x: (x <= -71).sum()),
    very_poor_rssi_count=('rssi', lambda x: (x < -80).sum()),
    weak_snr_count=('snr', lambda x: (x < 20).sum()),
    very_poor_snr_count=('snr', lambda x: (x < 10).sum()),
).reset_index()

bldg_floor_rssi['weak_rssi_pct'] = (bldg_floor_rssi['weak_rssi_count'] / bldg_floor_rssi['session_count'] * 100)
bldg_floor_rssi['very_poor_rssi_pct'] = (bldg_floor_rssi['very_poor_rssi_count'] / bldg_floor_rssi['session_count'] * 100)
bldg_floor_rssi['poor_signal_pct'] = bldg_floor_rssi['weak_rssi_pct']  # Weak + Very Poor combined percentage
bldg_floor_rssi['weak_snr_pct'] = (bldg_floor_rssi['weak_snr_count'] / bldg_floor_rssi['session_count'] * 100)

# Sort by worst signal
worst_rssi = bldg_floor_rssi.sort_values('avg_rssi', ascending=True)
print("\n--- Worst Average RSSI by Building-Floor ---")
for i, row in enumerate(worst_rssi.head(15).itertuples(), 1):
    quality = classify_rssi(row.avg_rssi)
    print(f"  {i:2d}. {row.BuildingName} - {row.Floor}: "
          f"Avg RSSI={row.avg_rssi:.1f} dBm ({quality}), "
          f"Avg SNR={row.avg_snr:.1f}, "
          f"Weak%={row.weak_rssi_pct:.1f}%, "
          f"Sessions={row.session_count:,}")

print("\n--- Highest % of Weak/Very Poor RSSI Sessions ---")
worst_pct = bldg_floor_rssi.sort_values('weak_rssi_pct', ascending=False)
for i, row in enumerate(worst_pct.head(15).itertuples(), 1):
    print(f"  {i:2d}. {row.BuildingName} - {row.Floor}: "
          f"Weak RSSI={row.weak_rssi_pct:.1f}% ({row.weak_rssi_count:,}/{row.session_count:,}), "
          f"Very Poor={row.very_poor_rssi_pct:.1f}%")

# Figure 1.4a: RSSI Heatmap by Building-Floor
fig, axes = plt.subplots(2, 2, figsize=(22, 16))

# Heatmap: Average RSSI
ax = axes[0, 0]
pivot_rssi = bldg_floor_rssi.pivot_table(index='BuildingName', columns='Floor', values='avg_rssi')
# Sort floors naturally
floor_order = sorted(pivot_rssi.columns, key=lambda x: int(x.replace('FL','').replace('INN','99')))
pivot_rssi = pivot_rssi[floor_order]
im = ax.imshow(pivot_rssi.values, aspect='auto', cmap='RdYlGn', vmin=-80, vmax=-40)
ax.set_xticks(range(len(pivot_rssi.columns)))
ax.set_xticklabels(pivot_rssi.columns, fontsize=8)
ax.set_yticks(range(len(pivot_rssi.index)))
ax.set_yticklabels(pivot_rssi.index, fontsize=8)
ax.set_title('Average RSSI (dBm) by Building-Floor\n(Green=Good, Red=Poor)', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax, label='dBm')
for i in range(len(pivot_rssi.index)):
    for j in range(len(pivot_rssi.columns)):
        val = pivot_rssi.values[i, j]
        if not np.isnan(val):
            color = 'white' if val < -65 else 'black'
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=7, color=color, fontweight='bold')

# Heatmap: Average SNR
ax = axes[0, 1]
pivot_snr = bldg_floor_rssi.pivot_table(index='BuildingName', columns='Floor', values='avg_snr')
pivot_snr = pivot_snr[[c for c in floor_order if c in pivot_snr.columns]]
im = ax.imshow(pivot_snr.values, aspect='auto', cmap='RdYlGn', vmin=10, vmax=50)
ax.set_xticks(range(len(pivot_snr.columns)))
ax.set_xticklabels(pivot_snr.columns, fontsize=8)
ax.set_yticks(range(len(pivot_snr.index)))
ax.set_yticklabels(pivot_snr.index, fontsize=8)
ax.set_title('Average SNR (dB) by Building-Floor\n(Green=Good, Red=Poor)', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax, label='dB')
for i in range(len(pivot_snr.index)):
    for j in range(len(pivot_snr.columns)):
        val = pivot_snr.values[i, j]
        if not np.isnan(val):
            color = 'white' if val < 25 else 'black'
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=7, color=color, fontweight='bold')

# Heatmap: % Weak RSSI sessions
ax = axes[1, 0]
pivot_weak = bldg_floor_rssi.pivot_table(index='BuildingName', columns='Floor', values='weak_rssi_pct')
pivot_weak = pivot_weak[[c for c in floor_order if c in pivot_weak.columns]]
im = ax.imshow(pivot_weak.values, aspect='auto', cmap='Reds', vmin=0)
ax.set_xticks(range(len(pivot_weak.columns)))
ax.set_xticklabels(pivot_weak.columns, fontsize=8)
ax.set_yticks(range(len(pivot_weak.index)))
ax.set_yticklabels(pivot_weak.index, fontsize=8)
ax.set_title('% of Weak RSSI Sessions (≤-71 dBm)\nby Building-Floor (Darker=Worse)', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax, label='%')
for i in range(len(pivot_weak.index)):
    for j in range(len(pivot_weak.columns)):
        val = pivot_weak.values[i, j]
        if not np.isnan(val):
            color = 'white' if val > 50 else 'black'
            ax.text(j, i, f'{val:.0f}%', ha='center', va='center', fontsize=7, color=color, fontweight='bold')

# Bar chart: Building-Floor sorted by weak RSSI %
ax = axes[1, 1]
top_weak = worst_pct.head(12).copy()
top_weak['label'] = top_weak['BuildingName'].str[:20] + '\n' + top_weak['Floor']
colors_bar = plt.cm.Reds(np.linspace(0.3, 0.9, len(top_weak)))
bars = ax.barh(range(len(top_weak)), top_weak['weak_rssi_pct'].values, color=colors_bar)
ax.set_yticks(range(len(top_weak)))
ax.set_yticklabels(top_weak['label'].values, fontsize=7)
ax.set_xlabel('% Weak RSSI Sessions', fontsize=10)
ax.set_title('Top 12 Worst Signal Locations\n(% Weak/Very Poor RSSI)', fontsize=12, fontweight='bold')
ax.invert_yaxis()
for bar, val in zip(bars, top_weak['weak_rssi_pct'].values):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', va='center', fontsize=8)

plt.tight_layout()
plt.savefig('output/1_4_signal_quality_building_floor.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[Saved] output/1_4_signal_quality_building_floor.png")

# RSSI distribution per building
fig, ax = plt.subplots(figsize=(16, 8))
buildings = df['BuildingName'].unique()
rssi_quality_order = ['Excellent', 'Very Good', 'Good', 'Fair', 'Weak', 'Very Poor']
rssi_colors = {'Excellent': '#2ecc71', 'Very Good': '#27ae60', 'Good': '#f1c40f', 'Fair': '#e67e22', 'Weak': '#e74c3c', 'Very Poor': '#c0392b'}

bldg_quality = df.groupby(['BuildingName', 'rssi_quality']).size().unstack(fill_value=0)
bldg_quality_pct = bldg_quality.div(bldg_quality.sum(axis=1), axis=0) * 100
bldg_quality_pct = bldg_quality_pct[[c for c in rssi_quality_order if c in bldg_quality_pct.columns]]

bottom = np.zeros(len(bldg_quality_pct))
for col in bldg_quality_pct.columns:
    ax.barh(range(len(bldg_quality_pct)), bldg_quality_pct[col].values, left=bottom, 
            color=rssi_colors[col], label=col, edgecolor='white', linewidth=0.5)
    bottom += bldg_quality_pct[col].values

ax.set_yticks(range(len(bldg_quality_pct)))
ax.set_yticklabels(bldg_quality_pct.index, fontsize=8)
ax.set_xlabel('Percentage (%)', fontsize=11)
ax.set_title('RSSI Signal Quality Distribution by Building', fontsize=14, fontweight='bold')
ax.legend(loc='lower right', fontsize=9)
ax.set_xlim(0, 100)
plt.tight_layout()
plt.savefig('output/1_4_rssi_distribution_building.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_4_rssi_distribution_building.png")

# ============================================================
# 1.5 ADDITIONAL DASHBOARD VIEWS
# ============================================================
print("\n" + "=" * 70)
print("1.5 ADDITIONAL DASHBOARD VIEWS")
print("=" * 70)

# --- 1.5a: Hourly Usage Pattern ---
print("\n--- 1.5a: Hourly Usage Pattern ---")
hourly = df.groupby('hour').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    total_data_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    avg_rssi=('rssi', 'mean')
).reset_index()

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

ax = axes[0, 0]
ax.bar(hourly['hour'], hourly['sessions'], color=plt.cm.Blues(np.linspace(0.3, 0.9, 24)), edgecolor='white')
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Total Sessions')
ax.set_title('Wi-Fi Sessions by Hour of Day', fontsize=12, fontweight='bold')
ax.set_xticks(range(24))

ax = axes[0, 1]
ax.bar(hourly['hour'], hourly['unique_users'], color=plt.cm.Greens(np.linspace(0.3, 0.9, 24)), edgecolor='white')
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Unique Users')
ax.set_title('Unique Users by Hour of Day', fontsize=12, fontweight='bold')
ax.set_xticks(range(24))

# --- 1.5b: Account Type Distribution ---
ax = axes[1, 0]
acct_counts = df['account_type'].value_counts()
acct_colors = plt.cm.Set3(np.linspace(0, 0.8, len(acct_counts)))
wedges, texts, autotexts = ax.pie(acct_counts.values, labels=acct_counts.index, autopct='%1.1f%%',
       colors=acct_colors, startangle=90, textprops={'fontsize': 9})
ax.set_title('Wi-Fi Usage by Account Type', fontsize=12, fontweight='bold')

# --- 1.5c: Device Type Distribution ---
ax = axes[1, 1]
device_counts = df['deviceType'].value_counts()
device_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
wedges, texts, autotexts = ax.pie(device_counts.values, labels=device_counts.index, autopct='%1.1f%%',
       colors=device_colors[:len(device_counts)], startangle=90, textprops={'fontsize': 9})
ax.set_title('Wi-Fi Usage by Device Type', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('output/1_5a_hourly_account_device.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_5a_hourly_account_device.png")

# --- 1.5d: Radio Type Analysis ---
print("\n--- 1.5d: Radio Type & Channel Analysis ---")
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

ax = axes[0]
radio_counts = df['radioType'].value_counts().dropna()
bars = ax.barh(range(len(radio_counts)), radio_counts.values, color=plt.cm.Set2(np.linspace(0, 1, len(radio_counts))))
ax.set_yticks(range(len(radio_counts)))
ax.set_yticklabels(radio_counts.index, fontsize=10)
ax.set_xlabel('Session Count')
ax.set_title('Wi-Fi Sessions by Radio Type', fontsize=12, fontweight='bold')
for bar, val in zip(bars, radio_counts.values):
    ax.text(bar.get_width() + max(radio_counts.values)*0.01, bar.get_y() + bar.get_height()/2, f'{val:,}', va='center', fontsize=9)

ax = axes[1]
# Top 15 channels
channel_counts = df['channel'].value_counts().head(15)
bars = ax.bar(range(len(channel_counts)), channel_counts.values, color='steelblue', edgecolor='white')
ax.set_xticks(range(len(channel_counts)))
ax.set_xticklabels(channel_counts.index, fontsize=9)
ax.set_xlabel('Channel')
ax.set_ylabel('Session Count')
ax.set_title('Wi-Fi Sessions by Channel (Top 15)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('output/1_5b_radio_channel.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_5b_radio_channel.png")

# --- 1.5e: Data Transfer by Building ---
print("\n--- 1.5e: Data Transfer by Building ---")
bldg_data = df.groupby('BuildingName').agg(
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    avg_MB=('txRxBytes_MB', 'mean'),
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique')
).reset_index().sort_values('total_GB', ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(20, 8))

ax = axes[0]
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(bldg_data)))
bars = ax.barh(range(len(bldg_data)), bldg_data['total_GB'].values, color=colors)
ax.set_yticks(range(len(bldg_data)))
ax.set_yticklabels(bldg_data['BuildingName'].values, fontsize=8)
ax.set_xlabel('Total Data Transfer (GB)')
ax.set_title('Total Data Transfer by Building', fontsize=12, fontweight='bold')
ax.invert_yaxis()
for bar, val in zip(bars, bldg_data['total_GB'].values):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f} GB', va='center', fontsize=9)

ax = axes[1]
bars = ax.barh(range(len(bldg_data)), bldg_data['unique_users'].values, color=plt.cm.plasma(np.linspace(0.3, 0.9, len(bldg_data))))
ax.set_yticks(range(len(bldg_data)))
ax.set_yticklabels(bldg_data['BuildingName'].values, fontsize=8)
ax.set_xlabel('Unique Users')
ax.set_title('Unique Users by Building', fontsize=12, fontweight='bold')
ax.invert_yaxis()
for bar, val in zip(bars, bldg_data['unique_users'].values):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, f'{val:,}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('output/1_5c_data_transfer_building.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_5c_data_transfer_building.png")

# --- 1.5f: Day of Week Patterns ---
print("\n--- 1.5f: Day of Week Usage Patterns ---")
day_order_num = [0, 1, 2, 3, 4, 5, 6]
day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

dow_stats = df.groupby('day_of_week').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    avg_rssi=('rssi', 'mean')
).reindex(day_order_num)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

ax = axes[0, 0]
colors = ['#3498db']*5 + ['#e74c3c']*2
ax.bar(range(7), dow_stats['sessions'].values, color=colors, edgecolor='white')
ax.set_xticks(range(7))
ax.set_xticklabels(day_labels)
ax.set_ylabel('Sessions')
ax.set_title('Total Sessions by Day of Week\n(Red=Weekend)', fontsize=12, fontweight='bold')

ax = axes[0, 1]
ax.bar(range(7), dow_stats['unique_users'].values, color=colors, edgecolor='white')
ax.set_xticks(range(7))
ax.set_xticklabels(day_labels)
ax.set_ylabel('Unique Users')
ax.set_title('Unique Users by Day of Week', fontsize=12, fontweight='bold')

ax = axes[1, 0]
ax.bar(range(7), dow_stats['total_GB'].values, color=colors, edgecolor='white')
ax.set_xticks(range(7))
ax.set_xticklabels(day_labels)
ax.set_ylabel('Total Data (GB)')
ax.set_title('Total Data Transfer by Day of Week', fontsize=12, fontweight='bold')

# Hour x DayOfWeek heatmap
ax = axes[1, 1]
hour_dow = df.groupby(['hour', 'day_of_week']).size().unstack(fill_value=0)
hour_dow = hour_dow[day_order_num]
im = ax.imshow(hour_dow.values, aspect='auto', cmap='YlOrRd', interpolation='nearest')
ax.set_xlabel('Day of Week')
ax.set_ylabel('Hour')
ax.set_xticks(range(7))
ax.set_xticklabels(day_labels)
ax.set_yticks(range(0, 24, 2))
ax.set_yticklabels(range(0, 24, 2))
ax.set_title('Usage Heatmap: Hour × Day of Week', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax, label='Sessions')

plt.tight_layout()
plt.savefig('output/1_5d_day_of_week_patterns.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_5d_day_of_week_patterns.png")

# --- 1.5g: SSID Comparison ---
print("\n--- 1.5g: SSID Comparison ---")
ssid_stats = df.groupby('ssid').agg(
    sessions=('id', 'count'),
    unique_users=('Username', 'nunique'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    avg_rssi=('rssi', 'mean'),
    avg_snr=('snr', 'mean'),
    avg_data_MB=('txRxBytes_MB', 'mean')
).reset_index()
print(ssid_stats.to_string(index=False))

# --- 1.5h: OS/Vendor Analysis ---
print("\n--- 1.5h: OS Vendor Type Analysis ---")
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

ax = axes[0]
vendor_counts = df['osVendorType'].value_counts()
ax.barh(range(len(vendor_counts)), vendor_counts.values, color=plt.cm.Pastel1(np.linspace(0, 1, len(vendor_counts))))
ax.set_yticks(range(len(vendor_counts)))
ax.set_yticklabels(vendor_counts.index, fontsize=10)
ax.set_xlabel('Session Count')
ax.set_title('Sessions by OS Vendor Type', fontsize=12, fontweight='bold')
for i, val in enumerate(vendor_counts.values):
    ax.text(val + max(vendor_counts.values)*0.01, i, f'{val:,} ({val/len(df)*100:.1f}%)', va='center', fontsize=9)

# SSID by account type
ax = axes[1]
ssid_acct = df.groupby(['ssid', 'account_type']).size().unstack(fill_value=0)
ssid_acct_pct = ssid_acct.div(ssid_acct.sum(axis=1), axis=0) * 100
acct_colors_list = plt.cm.Set2(np.linspace(0, 0.8, len(ssid_acct_pct.columns)))
bottom = np.zeros(len(ssid_acct_pct))
for i, col in enumerate(ssid_acct_pct.columns):
    ax.barh(range(len(ssid_acct_pct)), ssid_acct_pct[col].values, left=bottom, 
            color=acct_colors_list[i], label=col, edgecolor='white')
    bottom += ssid_acct_pct[col].values
ax.set_yticks(range(len(ssid_acct_pct)))
ax.set_yticklabels(ssid_acct_pct.index, fontsize=10)
ax.set_xlabel('Percentage (%)')
ax.set_title('Account Type Distribution by SSID', fontsize=12, fontweight='bold')
ax.legend(loc='lower right', fontsize=8)
ax.set_xlim(0, 100)

plt.tight_layout()
plt.savefig('output/1_5e_os_vendor_ssid.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_5e_os_vendor_ssid.png")

# --- 1.5i: Top 20 Power Users ---
print("\n--- 1.5i: Top 20 Power Users ---")
user_stats = df.groupby('Username').agg(
    sessions=('id', 'count'),
    total_GB=('txRxBytes', lambda x: x.sum() / (1024**3)),
    unique_devices=('clientMac', 'nunique'),
    unique_buildings=('BuildingName', 'nunique'),
    avg_rssi=('rssi', 'mean'),
    account_type=('account_type', 'first')
).sort_values('sessions', ascending=False)
print(user_stats.head(20).to_string())

fig, ax = plt.subplots(figsize=(16, 8))
top20 = user_stats.head(20)
colors = {'student': '#3498db', 'personnel': '#e74c3c', 'alumni': '#2ecc71', 'retirement': '#f39c12', 'templecturer': '#9b59b6'}
bar_colors = [colors.get(t, 'gray') for t in top20['account_type']]
bars = ax.barh(range(len(top20)), top20['sessions'].values, color=bar_colors, edgecolor='white')
ax.set_yticks(range(len(top20)))
ax.set_yticklabels(top20.index, fontsize=8)
ax.set_xlabel('Total Sessions')
ax.set_title('Top 20 Power Users by Session Count\n(Blue=Student, Red=Personnel, Green=Alumni)', fontsize=12, fontweight='bold')
ax.invert_yaxis()
for bar, val, gb in zip(bars, top20['sessions'].values, top20['total_GB'].values):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, f'{val:,} sessions | {gb:.1f} GB', va='center', fontsize=8)

plt.tight_layout()
plt.savefig('output/1_5f_power_users.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_5f_power_users.png")

# --- 1.5j: Upload vs Download ratio ---
print("\n--- 1.5j: Upload vs Download Analysis ---")
total_tx = df['txBytes'].sum() / (1024**3)
total_rx = df['rxBytes'].sum() / (1024**3)
print(f"  Total Upload: {total_tx:.2f} GB")
print(f"  Total Download: {total_rx:.2f} GB")
print(f"  Download/Upload Ratio: {total_rx/total_tx:.2f}x")

fig, axes = plt.subplots(1, 3, figsize=(20, 7))

# Overall TX vs RX
ax = axes[0]
ax.bar(['Upload (TX)', 'Download (RX)'], [total_tx, total_rx], color=['#e74c3c', '#3498db'], edgecolor='white')
ax.set_ylabel('Total (GB)')
ax.set_title(f'Upload vs Download\n(Ratio: {total_rx/total_tx:.2f}x)', fontsize=12, fontweight='bold')
for i, val in enumerate([total_tx, total_rx]):
    ax.text(i, val + 1, f'{val:.1f} GB', ha='center', fontsize=10, fontweight='bold')

# TX/RX by building
ax = axes[1]
bldg_txrx = df.groupby('BuildingName').agg(
    tx_GB=('txBytes', lambda x: x.sum() / (1024**3)),
    rx_GB=('rxBytes', lambda x: x.sum() / (1024**3))
).reset_index()
x = range(len(bldg_txrx))
width = 0.35
ax.barh([i - width/2 for i in x], bldg_txrx['tx_GB'].values, width, label='Upload', color='#e74c3c', edgecolor='white')
ax.barh([i + width/2 for i in x], bldg_txrx['rx_GB'].values, width, label='Download', color='#3498db', edgecolor='white')
ax.set_yticks(list(x))
ax.set_yticklabels(bldg_txrx['BuildingName'].values, fontsize=7)
ax.set_xlabel('GB')
ax.set_title('Upload vs Download by Building', fontsize=12, fontweight='bold')
ax.legend()
ax.invert_yaxis()

# Hourly TX/RX pattern
ax = axes[2]
hourly_txrx = df.groupby('hour').agg(
    tx_GB=('txBytes', lambda x: x.sum() / (1024**3)),
    rx_GB=('rxBytes', lambda x: x.sum() / (1024**3))
)
ax.plot(hourly_txrx.index, hourly_txrx['tx_GB'], 'r-o', label='Upload', markersize=4)
ax.plot(hourly_txrx.index, hourly_txrx['rx_GB'], 'b-o', label='Download', markersize=4)
ax.set_xlabel('Hour')
ax.set_ylabel('GB')
ax.set_title('Hourly Upload vs Download Pattern', fontsize=12, fontweight='bold')
ax.legend()
ax.set_xticks(range(24))

plt.tight_layout()
plt.savefig('output/1_5g_upload_download.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_5g_upload_download.png")

print("\n" + "=" * 70)
print("Part 2 Complete! Outputs saved to /output/")
print("=" * 70)
