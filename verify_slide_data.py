"""
ตรวจสอบข้อมูลในสไลด์ Pain Point 1 กับ raw dataset
"""
import pandas as pd
import numpy as np

df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
print(f"Total rows (sessions): {len(df):,}")
print(f"Columns: {list(df.columns)}")
print()

# ===== 1. Key Performance Metrics =====
print("=" * 60)
print("KEY PERFORMANCE METRICS")
print("=" * 60)

total_sessions = len(df)
unique_users = df['Username'].nunique()
unique_aps = df['apName'].nunique()

# Total Data
total_bytes = df['txRxBytes'].sum()
total_gb = total_bytes / (1024**3)

# Avg RSSI & SNR
avg_rssi = df['rssi'].mean()
avg_snr = df['snr'].mean()

print(f"Total Sessions: {total_sessions:,}  (slide: 189,445)")
print(f"Unique Users: {unique_users:,}  (slide: 8,148)")
print(f"Unique APs: {unique_aps:,}  (slide: 107)")
print(f"Total Data: {total_gb:,.1f} GB  (slide: 22934.1 GB)")
print(f"Avg RSSI: {avg_rssi:.1f} dBm  (slide: -73.4 dBm)")
print(f"Avg SNR: {avg_snr:.1f} dB  (slide: 19.1 dB)")
print()

# ===== 2. RSSI Distribution Table =====
print("=" * 60)
print("RSSI DISTRIBUTION TABLE")
print("=" * 60)

def classify_rssi(rssi):
    if rssi >= -50:
        return "Excellent (>= -50 dBm)"
    elif rssi >= -60:
        return "Very Good (-50 ~ -60)"
    elif rssi >= -67:
        return "Good (-60 ~ -67)"
    elif rssi >= -70:
        return "Fair (-67 ~ -70)"
    elif rssi >= -80:
        return "Weak (-70 ~ -80)"
    else:
        return "Very Poor (< -80 dBm)"

df['rssi_level'] = df['rssi'].apply(classify_rssi)

rssi_order = [
    "Excellent (>= -50 dBm)",
    "Very Good (-50 ~ -60)",
    "Good (-60 ~ -67)",
    "Fair (-67 ~ -70)",
    "Weak (-70 ~ -80)",
    "Very Poor (< -80 dBm)"
]

slide_values = {
    "Excellent (>= -50 dBm)": 22203,
    "Very Good (-50 ~ -60)": 13325,
    "Good (-60 ~ -67)": 13611,
    "Fair (-67 ~ -70)": 7006,
    "Weak (-70 ~ -80)": 31495,
    "Very Poor (< -80 dBm)": 101805
}

for level in rssi_order:
    count = (df['rssi_level'] == level).sum()
    pct = count / total_sessions * 100
    slide_count = slide_values.get(level, "?")
    match = "✓" if count == slide_count else "✗"
    print(f"  {level}: {count:,} ({pct:.1f}%)  slide: {slide_count:,}  {match}")

print()

# ===== 3. SNR < 10 dB =====
print("=" * 60)
print("SNR < 10 dB (High Interference)")
print("=" * 60)
snr_low = (df['snr'] < 10).sum()
snr_low_pct = snr_low / total_sessions * 100
print(f"  SNR < 10 dB: {snr_low:,} sessions = {snr_low_pct:.1f}%  (slide: 89,011 = 47%)")
print()

# ===== 4. Derived Metrics =====
print("=" * 60)
print("DERIVED METRICS")
print("=" * 60)

# Weak Signal = Weak + Very Poor
weak_count = (df['rssi_level'] == "Weak (-70 ~ -80)").sum()
vpoor_count = (df['rssi_level'] == "Very Poor (< -80 dBm)").sum()
weak_signal_total = weak_count + vpoor_count
weak_signal_pct = weak_signal_total / total_sessions * 100
print(f"  Weak Signal (Weak+VeryPoor): {weak_signal_total:,} = {weak_signal_pct:.1f}%  (slide: 70.4%)")

# Very Poor Signal
vpoor_pct = vpoor_count / total_sessions * 100
print(f"  Very Poor Signal: {vpoor_count:,} = {vpoor_pct:.1f}%  (slide: 53.7%)")

# WiFi 6 Adoption
wifi6_types = df['radioType'].value_counts()
print(f"\n  Radio Types:")
for rt, cnt in wifi6_types.items():
    print(f"    {rt}: {cnt:,} ({cnt/total_sessions*100:.1f}%)")

# WiFi 6 = 802.11ax
wifi6_count = df[df['radioType'].str.contains('ax|WiFi 6|wifi6|802.11ax', case=False, na=False)].shape[0]
wifi6_pct = wifi6_count / total_sessions * 100
print(f"  WiFi 6 (ax): {wifi6_count:,} = {wifi6_pct:.1f}%  (slide: 76.0%)")

# Failed sessions (SNR < 3 dB? or some other metric)
failed_snr3 = (df['snr'] <= 3).sum()
failed_snr3_pct = failed_snr3 / total_sessions * 100
print(f"  Sessions with SNR <= 3 dB: {failed_snr3:,} = {failed_snr3_pct:.1f}%  (slide failed >3dB: 8.3%)")

# Maybe failed = RSSI < -90?
failed_rssi90 = (df['rssi'] < -90).sum()
failed_rssi90_pct = failed_rssi90 / total_sessions * 100
print(f"  Sessions with RSSI < -90: {failed_rssi90:,} = {failed_rssi90_pct:.1f}%")

print()

# ===== 5. Sum check =====
print("=" * 60)
print("SUM CHECK")
print("=" * 60)
rssi_total = sum(slide_values.values())
print(f"  Slide RSSI table sum: {rssi_total:,}")
print(f"  Actual total sessions: {total_sessions:,}")
print(f"  Match: {'✓' if rssi_total == total_sessions else '✗'}")

# Check percentages
slide_pcts = {k: v/189445*100 for k, v in slide_values.items()}
print("\n  Slide percentages (recalculated):")
for level in rssi_order:
    real_pct = slide_values[level] / 189445 * 100
    print(f"    {level}: {real_pct:.2f}%")

# ===== 6. Weak buildings check =====
print()
print("=" * 60)
print("WEAK BUILDINGS/FLOORS (weak_pct > 70%)")
print("=" * 60)

for bldg in df['Building'].unique():
    bdf = df[df['Building'] == bldg]
    for floor in sorted(bdf['Floor'].unique()):
        fdf = bdf[bdf['Floor'] == floor]
        weak_f = fdf[fdf['rssi'] < -70].shape[0]
        weak_pct_f = weak_f / len(fdf) * 100 if len(fdf) > 0 else 0
        if weak_pct_f > 70:
            print(f"  {bldg}-FL{floor}: {weak_pct_f:.1f}% weak ({weak_f}/{len(fdf)} sessions)")
