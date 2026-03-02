"""
ICIT Data Insight & Analytics Challenge 2026
Part 1: Questions 1.1, 1.2, 1.3
Wi-Fi usage data analysis for KMUTNB
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Setup Thai font support
# ============================================================
matplotlib.rcParams['font.family'] = 'sans-serif'
# Try common Thai-supporting fonts on Windows
for font in ['Tahoma', 'Angsana New', 'TH SarabunPSK', 'Cordia New', 'Leelawadee UI', 'Segoe UI']:
    try:
        matplotlib.rcParams['font.sans-serif'] = [font, 'DejaVu Sans', 'Arial']
        break
    except:
        continue
matplotlib.rcParams['axes.unicode_minus'] = False

os.makedirs("output", exist_ok=True)

# ============================================================
# Load Data
# ============================================================
print("=" * 70)
print("ICIT Data Insight & Analytics Challenge 2026")
print("Wi-Fi Network Analysis - KMUTNB")
print("=" * 70)
print("\nLoading dataset...")
df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
print(f"Total records: {len(df):,}")
print(f"Columns: {len(df.columns)}")

# Parse datetime
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['date'] = df['sessionStartDateTime'].dt.date
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day_of_week'] = df['sessionStartDateTime'].dt.dayofweek  # 0=Mon, 6=Sun
df['day_name'] = df['sessionStartDateTime'].dt.day_name()

# RSSI Quality classification
def classify_rssi(rssi):
    if rssi >= -50:
        return 'Excellent (≥-50)'
    elif rssi >= -60:
        return 'Very Good (-51~-60)'
    elif rssi >= -67:
        return 'Good (-61~-67)'
    elif rssi >= -70:
        return 'Fair (-68~-70)'
    elif rssi >= -80:
        return 'Weak (-71~-80)'
    else:
        return 'Very Poor (<-80)'

def classify_snr(snr):
    if snr >= 40:
        return 'Excellent (≥40)'
    elif snr >= 30:
        return 'Very Good (30-39)'
    elif snr >= 25:
        return 'Good (25-29)'
    elif snr >= 20:
        return 'Fair (20-24)'
    elif snr >= 10:
        return 'Weak (10-19)'
    else:
        return 'Very Poor (<10)'

df['rssi_quality'] = df['rssi'].apply(classify_rssi)
df['snr_quality'] = df['snr'].apply(classify_snr)

# Convert bytes to MB for readability
df['txRxBytes_MB'] = df['txRxBytes'] / (1024 * 1024)
df['txBytes_MB'] = df['txBytes'] / (1024 * 1024)
df['rxBytes_MB'] = df['rxBytes'] / (1024 * 1024)

print("\n" + "=" * 70)
print("DATA OVERVIEW")
print("=" * 70)
print(f"Date range: {df['sessionStartDateTime'].min()} to {df['sessionStartDateTime'].max()}")
print(f"Unique users: {df['Username'].nunique():,}")
print(f"Unique devices (MAC): {df['clientMac'].nunique():,}")
print(f"Unique Access Points: {df['apName'].nunique()}")
print(f"Unique Buildings: {df['BuildingName'].nunique()}")
print(f"SSIDs: {df['ssid'].unique()}")
print(f"Account types: {df['account_type'].unique()}")

# ============================================================
# 1.1 Top 10 Faculty/Department by Usage Count, grouped by SSID
# ============================================================
print("\n" + "=" * 70)
print("1.1 TOP 10 FACULTY/DEPARTMENT BY USAGE (BY SSID)")
print("=" * 70)

# Faculty by SSID
faculty_ssid = df.groupby(['faculty_name', 'ssid']).size().reset_index(name='usage_count')
faculty_ssid = faculty_ssid.dropna(subset=['faculty_name'])

for ssid_name in df['ssid'].unique():
    subset = faculty_ssid[faculty_ssid['ssid'] == ssid_name].nlargest(10, 'usage_count')
    print(f"\n--- SSID: {ssid_name} ---")
    for i, row in enumerate(subset.itertuples(), 1):
        print(f"  {i:2d}. {row.faculty_name}: {row.usage_count:,} sessions")

# Visualization 1.1
fig, axes = plt.subplots(1, 2, figsize=(22, 10))
ssids = df['ssid'].unique()
colors_map = {'@KMUTNB': plt.cm.Blues, 'eduroam': plt.cm.Oranges}

for idx, ssid_name in enumerate(ssids):
    ax = axes[idx]
    subset = faculty_ssid[faculty_ssid['ssid'] == ssid_name].nlargest(10, 'usage_count')
    cmap = colors_map.get(ssid_name, plt.cm.Greens)
    colors = cmap(np.linspace(0.4, 0.9, len(subset)))
    
    bars = ax.barh(range(len(subset)), subset['usage_count'].values, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(subset)))
    ax.set_yticklabels(subset['faculty_name'].values, fontsize=9)
    ax.set_xlabel('Usage Count (Sessions)', fontsize=11)
    ax.set_title(f'Top 10 Faculty/Department\nSSID: {ssid_name}', fontsize=13, fontweight='bold')
    ax.invert_yaxis()
    
    for bar, val in zip(bars, subset['usage_count'].values):
        ax.text(bar.get_width() + max(subset['usage_count'].values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{val:,}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('output/1_1_top10_faculty_by_ssid.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[Saved] output/1_1_top10_faculty_by_ssid.png")

# Also show combined (both SSIDs)
faculty_total = df.groupby('faculty_name').size().reset_index(name='usage_count')
faculty_total = faculty_total.dropna(subset=['faculty_name']).nlargest(10, 'usage_count')
print(f"\n--- Combined (All SSIDs) ---")
for i, row in enumerate(faculty_total.itertuples(), 1):
    print(f"  {i:2d}. {row.faculty_name}: {row.usage_count:,} sessions")

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(faculty_total)))
bars = ax.barh(range(len(faculty_total)), faculty_total['usage_count'].values, color=colors, edgecolor='white')
ax.set_yticks(range(len(faculty_total)))
ax.set_yticklabels(faculty_total['faculty_name'].values, fontsize=10)
ax.set_xlabel('Usage Count (Sessions)', fontsize=11)
ax.set_title('Top 10 Faculty/Department by Wi-Fi Usage (All SSIDs)', fontsize=14, fontweight='bold')
ax.invert_yaxis()
for bar, val in zip(bars, faculty_total['usage_count'].values):
    ax.text(bar.get_width() + max(faculty_total['usage_count'].values)*0.01, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('output/1_1_top10_faculty_combined.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_1_top10_faculty_combined.png")

# ============================================================
# 1.2 Top 10 Days with Highest Unique User Count (>1 session/day = 1 user)
# ============================================================
print("\n" + "=" * 70)
print("1.2 TOP 10 DAYS WITH HIGHEST USER DENSITY")
print("=" * 70)

# Count unique users per day
daily_users = df.groupby('date')['Username'].nunique().reset_index(name='unique_users')
daily_users = daily_users.sort_values('unique_users', ascending=False)

top10_days = daily_users.head(10)
print("\nTop 10 days with most unique users:")
for i, row in enumerate(top10_days.itertuples(), 1):
    day_name = pd.Timestamp(row.date).day_name()
    print(f"  {i:2d}. {row.date} ({day_name}): {row.unique_users:,} unique users")

# Additional stats
daily_sessions = df.groupby('date').size().reset_index(name='total_sessions')
daily_combined = daily_users.merge(daily_sessions, on='date')
daily_combined['sessions_per_user'] = daily_combined['total_sessions'] / daily_combined['unique_users']
top10_days_full = daily_combined.sort_values('unique_users', ascending=False).head(10)

fig, axes = plt.subplots(2, 1, figsize=(16, 12))

# Chart 1: Top 10 days by unique users
ax1 = axes[0]
dates_str = [str(d) for d in top10_days_full['date'].values]
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(top10_days_full)))
bars = ax1.bar(range(len(top10_days_full)), top10_days_full['unique_users'].values, color=colors, edgecolor='white')
ax1.set_xticks(range(len(top10_days_full)))
ax1.set_xticklabels(dates_str, rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Unique Users', fontsize=11)
ax1.set_title('Top 10 Days with Highest Wi-Fi User Density', fontsize=14, fontweight='bold')
for bar, val in zip(bars, top10_days_full['unique_users'].values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Chart 2: Daily user trend over all dates
ax2 = axes[1]
daily_users_sorted = daily_users.sort_values('date')
ax2.fill_between(range(len(daily_users_sorted)), daily_users_sorted['unique_users'].values, alpha=0.3, color='steelblue')
ax2.plot(range(len(daily_users_sorted)), daily_users_sorted['unique_users'].values, color='steelblue', linewidth=1.5)
ax2.set_xlabel('Date', fontsize=11)
ax2.set_ylabel('Unique Users', fontsize=11)
ax2.set_title('Daily Unique User Trend', fontsize=13, fontweight='bold')

# Add x-tick labels for every 7th date
tick_positions = list(range(0, len(daily_users_sorted), max(1, len(daily_users_sorted)//15)))
ax2.set_xticks(tick_positions)
ax2.set_xticklabels([str(daily_users_sorted['date'].values[i]) for i in tick_positions], rotation=45, ha='right', fontsize=8)

plt.tight_layout()
plt.savefig('output/1_2_top10_days_user_density.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_2_top10_days_user_density.png")

# ============================================================
# 1.3 For each day of week: AP with highest total data transfer
# ============================================================
print("\n" + "=" * 70)
print("1.3 AP WITH HIGHEST DATA TRANSFER BY DAY OF WEEK")
print("=" * 70)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Group by day of week and AP
day_ap_data = df.groupby(['day_name', 'apName'])['txRxBytes'].sum().reset_index()
day_ap_data['txRxBytes_GB'] = day_ap_data['txRxBytes'] / (1024**3)

# For each day, find the AP with max data
print("\nHighest data transfer AP per day of week:")
results_1_3 = []
for day in day_order:
    day_data = day_ap_data[day_ap_data['day_name'] == day]
    if len(day_data) > 0:
        top_ap = day_data.loc[day_data['txRxBytes_GB'].idxmax()]
        results_1_3.append({
            'day': day,
            'apName': top_ap['apName'],
            'total_GB': top_ap['txRxBytes_GB']
        })
        print(f"  {day:12s}: {top_ap['apName']:30s} ({top_ap['txRxBytes_GB']:.2f} GB)")

# Visualization
results_df = pd.DataFrame(results_1_3)

fig, axes = plt.subplots(2, 1, figsize=(18, 14))

# Chart 1: Top AP per day
ax1 = axes[0]
day_colors = plt.cm.Set2(np.linspace(0, 1, 7))
bars = ax1.bar(range(len(results_df)), results_df['total_GB'].values, color=day_colors, edgecolor='white', linewidth=1.5)
ax1.set_xticks(range(len(results_df)))
ax1.set_xticklabels([f"{r['day']}\n({r['apName']})" for _, r in results_df.iterrows()], fontsize=8, ha='center')
ax1.set_ylabel('Total Data Transfer (GB)', fontsize=11)
ax1.set_title('Access Point with Highest Data Transfer per Day of Week', fontsize=14, fontweight='bold')
for bar, val in zip(bars, results_df['total_GB'].values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f'{val:.2f} GB', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Chart 2: Heatmap of top 10 APs across days of week
ax2 = axes[1]
# Get top 10 APs overall by data transfer
top10_aps = day_ap_data.groupby('apName')['txRxBytes_GB'].sum().nlargest(10).index
heatmap_data = day_ap_data[day_ap_data['apName'].isin(top10_aps)].pivot_table(
    index='apName', columns='day_name', values='txRxBytes_GB', fill_value=0
)
# Reorder columns
heatmap_data = heatmap_data[[d for d in day_order if d in heatmap_data.columns]]

im = ax2.imshow(heatmap_data.values, aspect='auto', cmap='YlOrRd')
ax2.set_xticks(range(len(heatmap_data.columns)))
ax2.set_xticklabels(heatmap_data.columns, fontsize=9)
ax2.set_yticks(range(len(heatmap_data.index)))
ax2.set_yticklabels(heatmap_data.index, fontsize=8)
ax2.set_title('Top 10 APs - Data Transfer Heatmap (GB) by Day of Week', fontsize=13, fontweight='bold')
plt.colorbar(im, ax=ax2, label='GB')

# Add text annotations
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        val = heatmap_data.values[i, j]
        color = 'white' if val > heatmap_data.values.max() * 0.5 else 'black'
        ax2.text(j, i, f'{val:.1f}', ha='center', va='center', fontsize=7, color=color)

plt.tight_layout()
plt.savefig('output/1_3_ap_highest_data_by_day.png', dpi=150, bbox_inches='tight')
plt.close()
print("[Saved] output/1_3_ap_highest_data_by_day.png")

# Also show top 5 APs per day for deeper insight
print("\n--- Top 5 APs per day of week ---")
for day in day_order:
    day_data = day_ap_data[day_ap_data['day_name'] == day].nlargest(5, 'txRxBytes_GB')
    print(f"\n  {day}:")
    for i, row in enumerate(day_data.itertuples(), 1):
        print(f"    {i}. {row.apName}: {row.txRxBytes_GB:.2f} GB")

print("\n" + "=" * 70)
print("Part 1 Complete! Outputs saved to /output/")
print("=" * 70)
