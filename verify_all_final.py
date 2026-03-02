"""
Final Verification — ตรวจสอบตัวเลขทุกตัวที่ใช้ใน Pain Points & Insights
เทียบกับ raw dataset โดยตรง
"""
import pandas as pd
import numpy as np

df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day'] = df['sessionStartDateTime'].dt.day
df['weekday'] = df['sessionStartDateTime'].dt.dayofweek
df['is_weekend'] = df['weekday'] >= 5
df['is_weak'] = df['rssi'] < -70
df['is_vpoor'] = df['rssi'] < -80
df['is_wifi6'] = df['radioType'].str.contains('ax', case=False, na=False)
df['band'] = df['channel'].apply(lambda c: '2.4GHz' if c <= 14 else '5GHz')

total = len(df)
passed = 0
failed = 0
warnings = 0

def check(label, expected, actual, tolerance=0.05):
    global passed, failed, warnings
    if isinstance(expected, float):
        diff = abs(expected - actual)
        pct_diff = diff / abs(expected) * 100 if expected != 0 else diff
        if pct_diff <= tolerance:
            print(f"  ✅ {label}: expected={expected}, actual={actual} (diff={pct_diff:.2f}%)")
            passed += 1
        else:
            print(f"  ❌ {label}: expected={expected}, actual={actual} (diff={pct_diff:.2f}%)")
            failed += 1
    else:
        if expected == actual:
            print(f"  ✅ {label}: {actual}")
            passed += 1
        else:
            print(f"  ❌ {label}: expected={expected}, actual={actual}")
            failed += 1

print("=" * 80)
print("VERIFICATION: PAIN POINT 1 — Signal Quality")
print("=" * 80)

# Total sessions
check("Total sessions", 189445, total)

# RSSI levels
def rssi_level(r):
    if r >= -50: return 'Excellent'
    elif r >= -60: return 'Very Good'
    elif r >= -67: return 'Good'
    elif r >= -70: return 'Fair'
    elif r >= -80: return 'Weak'
    else: return 'Very Poor'

df['rssi_level'] = df['rssi'].apply(rssi_level)

check("Excellent count", 22203, (df['rssi_level']=='Excellent').sum())
check("Very Good count", 13325, (df['rssi_level']=='Very Good').sum())
check("Good count", 13611, (df['rssi_level']=='Good').sum())
check("Fair count", 7006, (df['rssi_level']=='Fair').sum())
check("Weak count", 31495, (df['rssi_level']=='Weak').sum())
check("Very Poor count", 101805, (df['rssi_level']=='Very Poor').sum())

weak_total = df['is_weak'].sum()
check("Weak+VeryPoor total", 133300, weak_total)
check("Weak+VeryPoor %", 70.4, round(weak_total/total*100, 1))
check("VeryPoor %", 53.7, round(df['is_vpoor'].sum()/total*100, 1))

check("Avg RSSI", -73.4, round(df['rssi'].mean(), 1))
check("Median RSSI", -83.0, round(float(df['rssi'].median()), 1))

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 2 — Interference (SNR)")
print("=" * 80)

snr_lt10 = (df['snr'] < 10).sum()
snr_lt5 = (df['snr'] < 5).sum()
check("SNR < 10 dB count", 89011, snr_lt10)
check("SNR < 10 dB %", 47.0, round(snr_lt10/total*100, 1))
check("SNR < 5 dB count", 56425, snr_lt5)
check("SNR < 5 dB %", 29.8, round(snr_lt5/total*100, 1))
check("Avg SNR", 16.1, round(df['snr'].mean(), 1))
check("Median SNR", 11.0, round(float(df['snr'].median()), 1))

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 3 — B77 Overloaded")
print("=" * 80)

b77 = df[df['Building'] == 'B77']
check("B77 sessions", 82875, len(b77))
check("B77 % of total", 43.7, round(len(b77)/total*100, 1))
check("B77 users", 7318, b77['Username'].nunique())
check("B77 APs", 16, b77['apName'].nunique())
check("B77 Avg RSSI", -74.1, round(b77['rssi'].mean(), 1))
check("B77 Weak %", 74.6, round(b77['is_weak'].mean()*100, 1))
check("B77 VeryPoor %", 59.1, round(b77['is_vpoor'].mean()*100, 1))

# B77 floors
b77f1 = b77[b77['Floor'].str.contains('1', na=False) & ~b77['Floor'].str.contains('11', na=False)]
# More precise floor matching
for floor_name in sorted(b77['Floor'].unique()):
    fdf = b77[b77['Floor'] == floor_name]
    print(f"  INFO: B77-{floor_name}: {len(fdf):,} sessions, {fdf['Username'].nunique():,} users, {fdf['apName'].nunique()} APs, weak={fdf['is_weak'].mean()*100:.1f}%")

b77_fl1 = b77[b77['Floor'] == 'FL1']
check("B77-FL1 sessions", 33919, len(b77_fl1))
check("B77-FL1 users", 6174, b77_fl1['Username'].nunique())
check("B77-FL1 APs", 3, b77_fl1['apName'].nunique())
check("B77-FL1 sessions/AP", 11306, len(b77_fl1) // b77_fl1['apName'].nunique())

b77_fl2 = b77[b77['Floor'] == 'FL2']
check("B77-FL2 sessions", 30878, len(b77_fl2))
check("B77-FL2 Weak %", 75.7, round(b77_fl2['is_weak'].mean()*100, 1))

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 4 — B25")
print("=" * 80)

b25 = df[df['Building'] == 'B25']
check("B25 sessions", 62470, len(b25))
check("B25 users", 6420, b25['Username'].nunique())
check("B25 APs", 35, b25['apName'].nunique())
check("B25 Weak %", 72.5, round(b25['is_weak'].mean()*100, 1))

b25_fl9 = b25[b25['Floor'] == 'FL9']
check("B25-FL9 sessions", 9507, len(b25_fl9))
check("B25-FL9 Weak %", 85.0, round(b25_fl9['is_weak'].mean()*100, 1))
check("B25-FL9 VeryPoor %", 71.9, round(b25_fl9['is_vpoor'].mean()*100, 1))
check("B25-FL9 APs", 4, b25_fl9['apName'].nunique())
check("B25-FL9 RSSI", -81.2, round(b25_fl9['rssi'].mean(), 1))

# Worst AP
b25_fl9_ap04 = df[df['apName'] == 'B25-FL9-AP04']
check("B25-FL9-AP04 sessions", 6910, len(b25_fl9_ap04))
check("B25-FL9-AP04 Weak %", 93.7, round(b25_fl9_ap04['is_weak'].mean()*100, 1))

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 5 — B31")
print("=" * 80)

b31 = df[df['Building'] == 'B31']
check("B31 sessions", 20276, len(b31))

for floor_name in sorted(b31['Floor'].unique()):
    fdf = b31[b31['Floor'] == floor_name]
    print(f"  INFO: B31-{floor_name}: {len(fdf):,} sessions, {fdf['apName'].nunique()} APs, weak={fdf['is_weak'].mean()*100:.1f}%")

b31_fl1 = b31[b31['Floor'] == 'FL1']
check("B31-FL1 Weak %", 81.3, round(b31_fl1['is_weak'].mean()*100, 1))
check("B31-FL1 APs", 4, b31_fl1['apName'].nunique())

b31_fl3 = b31[b31['Floor'] == 'FL3']
check("B31-FL3 Weak %", 82.1, round(b31_fl3['is_weak'].mean()*100, 1))
check("B31-FL3 APs", 1, b31_fl3['apName'].nunique())

b31_fl11 = b31[b31['Floor'] == 'FL11']
check("B31-FL11 APs (best floor)", 7, b31_fl11['apName'].nunique())

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 6 — Student vs Staff")
print("=" * 80)

students = df[df['account_type'] == 'student']
personnel = df[df['account_type'] == 'personnel']

check("Student sessions", 151732, len(students))
check("Student %", 80.1, round(len(students)/total*100, 1))
check("Student Avg RSSI", -74.0, round(students['rssi'].mean(), 1))
check("Student Avg SNR", 15.2, round(students['snr'].mean(), 1))
check("Student Weak %", 72.9, round(students['is_weak'].mean()*100, 1))
check("Student VeryPoor %", 56.6, round(students['is_vpoor'].mean()*100, 1))

check("Personnel sessions", 31816, len(personnel))
check("Personnel %", 16.8, round(len(personnel)/total*100, 1))
check("Personnel Avg RSSI", -70.8, round(personnel['rssi'].mean(), 1))
check("Personnel Avg SNR", 21.1, round(personnel['snr'].mean(), 1))
check("Personnel Weak %", 58.0, round(personnel['is_weak'].mean()*100, 1))

gap = round(students['is_weak'].mean()*100, 1) - round(personnel['is_weak'].mean()*100, 1)
check("Gap Student-Personnel Weak%", 14.9, round(gap, 1))

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 7 — eduroam vs @KMUTNB")
print("=" * 80)

kmutnb = df[df['ssid'] == '@KMUTNB']
eduroam = df[df['ssid'] == 'eduroam']

check("@KMUTNB sessions", 166075, len(kmutnb))
check("@KMUTNB Weak %", 69.5, round(kmutnb['is_weak'].mean()*100, 1))
check("@KMUTNB RSSI", -73.0, round(kmutnb['rssi'].mean(), 1))

check("eduroam sessions", 23370, len(eduroam))
check("eduroam Weak %", 76.2, round(eduroam['is_weak'].mean()*100, 1))
check("eduroam RSSI", -76.9, round(eduroam['rssi'].mean(), 1))

check("eduroam-KMUTNB gap", 6.7, round(eduroam['is_weak'].mean()*100 - kmutnb['is_weak'].mean()*100, 1))

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 8 — Failed Sessions")  
print("=" * 80)

zero_data = (df['txRxBytes'] == 0).sum()
low_data = (df['txRxBytes'] < 1024).sum()
check("Zero data sessions", 13849, zero_data)
check("Zero data %", 7.3, round(zero_data/total*100, 1))
check("Low data (<1KB) sessions", 17278, low_data)
check("Low data %", 9.1, round(low_data/total*100, 1))

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 9 — Worst APs")
print("=" * 80)

worst_aps = [
    ('B25-FL9-AP04', 93.7),
    ('B67-FL3-AP10', 92.2),
    ('B77-F2-AP01', 90.5),
]
for ap_name, expected_weak in worst_aps:
    apdf = df[df['apName'] == ap_name]
    actual_weak = round(apdf['is_weak'].mean()*100, 1)
    check(f"{ap_name} Weak %", expected_weak, actual_weak)
    check(f"{ap_name} sessions >= 500", True, len(apdf) >= 500)

print("\n" + "=" * 80)
print("VERIFICATION: PAIN POINT 10 — 5GHz vs 2.4GHz")
print("=" * 80)

band5 = df[df['band'] == '5GHz']
band24 = df[df['band'] == '2.4GHz']

check("5GHz sessions", 174369, len(band5))
check("5GHz %", 92.0, round(len(band5)/total*100, 1))
check("5GHz RSSI", -73.7, round(band5['rssi'].mean(), 1))
check("5GHz Weak %", 70.4, round(band5['is_weak'].mean()*100, 1))

check("2.4GHz sessions", 15076, len(band24))
check("2.4GHz RSSI", -70.2, round(band24['rssi'].mean(), 1))

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 1 — Hourly Double Peak")
print("=" * 80)

for h in [8, 11, 12, 15]:
    hdf = df[df['hour'] == h]
    print(f"  INFO: Hour {h:02d}: {len(hdf):,} sessions, {hdf['Username'].nunique():,} users")

h08 = df[df['hour'] == 8]
h12 = df[df['hour'] == 12]
h15 = df[df['hour'] == 15]
check("Hour 08 sessions", 20473, len(h08))
check("Hour 12 sessions", 26153, len(h12))
check("Hour 15 sessions", 15749, len(h15))
check("Hour 12 users", 5619, h12['Username'].nunique())

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 2 — Weekday vs Weekend")
print("=" * 80)

weekday_df = df[~df['is_weekend']]
weekend_df = df[df['is_weekend']]

check("Weekday sessions", 177464, len(weekday_df))
check("Weekday %", 93.7, round(len(weekday_df)/total*100, 1))
check("Weekend sessions", 11981, len(weekend_df))

# Users per day
wd_days = weekday_df['day'].nunique()
we_days = weekend_df['day'].nunique()
wd_users_per_day = weekday_df.groupby('day')['Username'].nunique().mean()
we_users_per_day = weekend_df.groupby('day')['Username'].nunique().mean()
print(f"  INFO: Weekday avg users/day = {wd_users_per_day:.0f} ({wd_days} days)")
print(f"  INFO: Weekend avg users/day = {we_users_per_day:.0f} ({we_days} days)")
ratio = wd_users_per_day / we_users_per_day
print(f"  INFO: Ratio weekday/weekend = {ratio:.1f}x")

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 3 — Multi-device Users")
print("=" * 80)

user_devices = df.groupby('Username')['clientMac'].nunique()
total_users = len(user_devices)
multi = (user_devices > 1).sum()
single = (user_devices == 1).sum()

check("Total unique users", 8546, total_users)
check("Single device users", 4258, single)
check("Multi device users", 4288, multi)
check("Multi device %", 50.2, round(multi/total_users*100, 1))
check("Max devices/user", 23, user_devices.max())

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 4 — iOS Dominance")
print("=" * 80)

ios_count = (df['osVendorType'] == 'iOS').sum()
check("iOS sessions", 90702, ios_count)
check("iOS %", 47.9, round(ios_count/total*100, 1))

smartphone = (df['deviceType'] == 'Smartphone').sum()
check("Smartphone sessions", 110188, smartphone)
check("Smartphone %", 58.2, round(smartphone/total*100, 1))

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 5 — WiFi 6 Paradox")
print("=" * 80)

wifi6 = df[df['is_wifi6']]
non_wifi6 = df[~df['is_wifi6']]

check("WiFi 6 sessions", 150741, len(wifi6))
check("WiFi 6 %", 79.6, round(len(wifi6)/total*100, 1))
check("WiFi 6 RSSI", -73.7, round(wifi6['rssi'].mean(), 1))
check("WiFi 6 SNR", 15.5, round(wifi6['snr'].mean(), 1))
check("WiFi 6 Weak %", 71.5, round(wifi6['is_weak'].mean()*100, 1))

check("Non-WiFi6 sessions", 38704, len(non_wifi6))
check("Non-WiFi6 RSSI", -72.6, round(non_wifi6['rssi'].mean(), 1))
check("Non-WiFi6 SNR", 18.5, round(non_wifi6['snr'].mean(), 1))
check("Non-WiFi6 Weak %", 66.0, round(non_wifi6['is_weak'].mean()*100, 1))

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 6 — Top 3 Faculties")
print("=" * 80)

fac_counts = df['faculty_name'].value_counts()
top3_facs = fac_counts.head(3)
top3_total = top3_facs.sum()
top3_pct = round(top3_total/total*100, 1)

for fac, cnt in top3_facs.items():
    users = df[df['faculty_name'] == fac]['Username'].nunique()
    print(f"  INFO: {fac}: {cnt:,} sessions ({cnt/total*100:.1f}%), {users:,} users")

check("Top 3 faculties sessions", 130812, top3_total)
check("Top 3 faculties %", 69.0, top3_pct)

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 7 — User Roaming")
print("=" * 80)

user_bldgs = df.groupby('Username')['Building'].nunique()
roam_3plus = (user_bldgs >= 3).sum()
total_u = len(user_bldgs)

check("Users visiting 1 building", 1864, (user_bldgs == 1).sum())
check("Users visiting 2 buildings", 2093, (user_bldgs == 2).sum())
check("Users visiting 3+ buildings", 4589, roam_3plus)
check("Roaming 3+ %", 53.7, round(roam_3plus/total_u*100, 1))
check("Users visiting all 6", 301, (user_bldgs == 6).sum())

print("\n" + "=" * 80)
print("VERIFICATION: INSIGHT 9 — B46 Best Practice")
print("=" * 80)

b46 = df[df['Building'] == 'B46']
check("B46 Avg RSSI", -66.8, round(b46['rssi'].mean(), 1))
check("B46 Avg SNR", 25.4, round(b46['snr'].mean(), 1))
check("B46 Weak %", 48.5, round(b46['is_weak'].mean()*100, 1))
check("B46 VeryPoor %", 17.2, round(b46['is_vpoor'].mean()*100, 1))
check("B46 APs", 21, b46['apName'].nunique())
check("B46 Floors", 4, b46['Floor'].nunique())

ap_per_floor_b46 = b46['apName'].nunique() / b46['Floor'].nunique()
b77_apf = b77['apName'].nunique() / b77['Floor'].nunique()
print(f"  INFO: B46 AP/Floor = {ap_per_floor_b46:.2f} vs B77 AP/Floor = {b77_apf:.2f}")

print("\n" + "=" * 80)
print("VERIFICATION: BUILDING OVERVIEW")
print("=" * 80)

for bldg in ['B25', 'B31', 'B46', 'B67', 'B77', 'B79']:
    bdf = df[df['Building'] == bldg]
    print(f"  {bldg}: {len(bdf):,} sessions, {bdf['Username'].nunique():,} users, {bdf['apName'].nunique()} APs, "
          f"{bdf['Floor'].nunique()} floors, RSSI={bdf['rssi'].mean():.1f}, SNR={bdf['snr'].mean():.1f}, "
          f"Weak={bdf['is_weak'].mean()*100:.1f}%, WiFi6={bdf['is_wifi6'].mean()*100:.1f}%")

print("\n" + "=" * 80)
print(f"FINAL RESULT: {passed} PASSED / {failed} FAILED / {warnings} WARNINGS")
print("=" * 80)

if failed == 0:
    print("🎉 ALL DATA VERIFIED — EVERY NUMBER MATCHES THE RAW DATASET!")
else:
    print(f"⚠️  {failed} checks failed — review needed!")
