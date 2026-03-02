"""
Final Slide Graphs - ICIT Data Insight & Analytics 2026
สร้างรูปกราฟทั้งหมดสำหรับสไลด์ Pain Points & Insights
อ้างอิงข้อมูลจริง 189,445 sessions
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ===== Thai Font Setup =====
plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['axes.unicode_minus'] = False

# Try to use Thai font
try:
    from matplotlib import font_manager
    thai_fonts = [f for f in font_manager.findSystemFonts() if 'tahoma' in f.lower() or 'angsana' in f.lower() or 'cordia' in f.lower() or 'sarabun' in f.lower()]
    if thai_fonts:
        import matplotlib
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=thai_fonts[0]).get_name()
except:
    pass

# Color palette
COLORS = {
    'critical': '#E53935',
    'high': '#FF7043', 
    'medium': '#FFB300',
    'low': '#66BB6A',
    'excellent': '#2E7D32',
    'very_good': '#43A047',
    'good': '#66BB6A',
    'fair': '#FFB300',
    'weak': '#FF7043',
    'very_poor': '#E53935',
    'bg': '#FFFFFF',
    'text': '#333333',
    'accent': '#00BCD4',
    'grid': '#CCCCCC',
    'b25': '#FF6B6B',
    'b31': '#4ECDC4',
    'b46': '#45B7D1',
    'b67': '#96CEB4',
    'b77': '#FFEAA7',
    'b79': '#DDA0DD',
}

RSSI_COLORS = ['#2E7D32', '#43A047', '#66BB6A', '#FFB300', '#FF7043', '#E53935']

df = pd.read_excel("datasets/wifi-kmutnb-datasets.xlsx")
df['sessionStartDateTime'] = pd.to_datetime(df['sessionStartDateTime'])
df['hour'] = df['sessionStartDateTime'].dt.hour
df['day'] = df['sessionStartDateTime'].dt.day
df['weekday'] = df['sessionStartDateTime'].dt.dayofweek
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
df['band'] = df['channel'].apply(lambda c: '2.4GHz' if c <= 14 else '5GHz')
total = len(df)

print("Generating graphs...")

# ===========================
# GRAPH 1: PAIN 1 - Overall Signal Quality (Pie + Bar)
# ===========================
fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=COLORS['bg'])
fig.suptitle('PAIN 1: Signal Quality Crisis — 70.4% Weak Signal', 
             fontsize=20, fontweight='bold', color=COLORS['critical'], y=0.98)

rssi_order = ['Excellent', 'Very Good', 'Good', 'Fair', 'Weak', 'Very Poor']
rssi_counts = [df[df['rssi_level']==lv].shape[0] for lv in rssi_order]
rssi_pcts = [c/total*100 for c in rssi_counts]

# Pie
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
explode = (0, 0, 0, 0, 0.05, 0.1)
wedges, texts, autotexts = ax1.pie(rssi_counts, labels=rssi_order, colors=RSSI_COLORS,
    autopct='%1.1f%%', startangle=90, explode=explode, textprops={'color': '#333333', 'fontsize': 11})
for t in autotexts:
    t.set_fontsize(10)
    t.set_fontweight('bold')
ax1.set_title('RSSI Distribution\n(189,445 sessions)', color='#333333', fontsize=14, pad=10)

# Bar
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
bars = ax2.barh(rssi_order[::-1], [rssi_counts[i] for i in range(5,-1,-1)], 
                color=[RSSI_COLORS[i] for i in range(5,-1,-1)], edgecolor='#333333', linewidth=0.5)
for bar, count, pct in zip(bars, rssi_counts[::-1], rssi_pcts[::-1]):
    ax2.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2, 
             f'{count:,} ({pct:.1f}%)', va='center', color='#333333', fontsize=11, fontweight='bold')
ax2.set_xlabel('Sessions', color='#333333', fontsize=12)
ax2.set_title('Sessions by Signal Level', color='#333333', fontsize=14, pad=10)
ax2.tick_params(colors='#333333')
ax2.set_xlim(0, 130000)
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Add summary box
fig.text(0.5, 0.02, 
    f'Weak+VeryPoor = 133,300 (70.4%)  |  Median RSSI = -83.0 dBm  |  SNR < 10 dB = 89,011 (47.0%)',
    ha='center', fontsize=12, color=COLORS['critical'], fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE0E0', edgecolor=COLORS['critical'], alpha=0.9))

plt.tight_layout(rect=[0, 0.06, 1, 0.94])
plt.savefig('output/slide_pain1_signal_quality.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [1/12] Pain 1 - Signal Quality ✓")

# ===========================
# GRAPH 2: PAIN 2 - SNR Interference
# ===========================
fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=COLORS['bg'])
fig.suptitle('PAIN 2: High Interference — 47% SNR < 10 dB', 
             fontsize=20, fontweight='bold', color=COLORS['critical'], y=0.98)

# SNR Distribution histogram
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
snr_bins = range(-5, 60, 2)
n, bins, patches = ax1.hist(df['snr'], bins=snr_bins, color=COLORS['accent'], alpha=0.8, edgecolor='#333333', linewidth=0.3)
for i, p in enumerate(patches):
    bin_center = (bins[i] + bins[i+1]) / 2
    if bin_center < 5:
        p.set_facecolor('#E53935')
    elif bin_center < 10:
        p.set_facecolor('#FF7043')
    elif bin_center < 20:
        p.set_facecolor('#FFB300')
    else:
        p.set_facecolor('#66BB6A')

ax1.axvline(x=10, color='red', linewidth=2, linestyle='--', label='SNR=10 dB (47% below)')
ax1.axvline(x=5, color='#FF6B6B', linewidth=2, linestyle=':', label='SNR=5 dB (29.8% below)')
ax1.axvline(x=df['snr'].median(), color='#0277BD', linewidth=2, linestyle='-', label=f'Median={df["snr"].median():.0f} dB')
ax1.set_xlabel('SNR (dB)', color='#333333', fontsize=12)
ax1.set_ylabel('Sessions', color='#333333', fontsize=12)
ax1.set_title('SNR Distribution', color='#333333', fontsize=14)
ax1.legend(fontsize=10, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax1.tick_params(colors='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# RSSI vs SNR scatter (sampled)
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
sample = df.sample(min(5000, len(df)), random_state=42)
scatter = ax2.scatter(sample['rssi'], sample['snr'], c=sample['snr'], cmap='RdYlGn', 
                      alpha=0.4, s=8, vmin=0, vmax=40)
ax2.axhline(y=10, color='red', linewidth=1.5, linestyle='--', alpha=0.7)
ax2.axvline(x=-70, color='orange', linewidth=1.5, linestyle='--', alpha=0.7)
ax2.set_xlabel('RSSI (dBm)', color='#333333', fontsize=12)
ax2.set_ylabel('SNR (dB)', color='#333333', fontsize=12)
ax2.set_title('RSSI vs SNR Correlation', color='#333333', fontsize=14)
ax2.tick_params(colors='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Quadrant labels
ax2.text(-60, 2, 'Good Signal\nHigh Noise', color='orange', fontsize=9, ha='center', fontweight='bold')
ax2.text(-90, 30, 'Bad Signal\nLow Noise', color='#B8860B', fontsize=9, ha='center', fontweight='bold')
ax2.text(-60, 30, 'IDEAL', color='#2E7D32', fontsize=11, ha='center', fontweight='bold')
ax2.text(-90, 2, 'WORST', color='red', fontsize=11, ha='center', fontweight='bold')

cb = plt.colorbar(scatter, ax=ax2, shrink=0.8)
cb.set_label('SNR (dB)', color='#333333')
cb.ax.tick_params(colors='#333333')

fig.text(0.5, 0.02,
    'SNR < 10 dB = 89,011 (47.0%)  |  SNR < 5 dB = 56,425 (29.8%)  |  Median SNR = 11.0 dB',
    ha='center', fontsize=12, color=COLORS['critical'], fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE0E0', edgecolor=COLORS['critical'], alpha=0.9))

plt.tight_layout(rect=[0, 0.06, 1, 0.94])
plt.savefig('output/slide_pain2_interference.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [2/12] Pain 2 - Interference ✓")

# ===========================
# GRAPH 3: PAIN 3 - B77 Overloaded
# ===========================
fig = plt.figure(figsize=(18, 8), facecolor=COLORS['bg'])
fig.suptitle('PAIN 3: B77 Overloaded — 43.7% Traffic, Only 16 APs', 
             fontsize=20, fontweight='bold', color=COLORS['critical'], y=0.98)

gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.3)

buildings = ['B25', 'B31', 'B46', 'B67', 'B77', 'B79']
bldg_colors = [COLORS['b25'], COLORS['b31'], COLORS['b46'], COLORS['b67'], COLORS['b77'], COLORS['b79']]

# Sessions by building
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor(COLORS['bg'])
bldg_sessions = [len(df[df['Building']==b]) for b in buildings]
bars = ax1.bar(buildings, bldg_sessions, color=bldg_colors, edgecolor='#333333', linewidth=0.5)
for bar, s in zip(bars, bldg_sessions):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500, 
             f'{s:,}', ha='center', color='#333333', fontsize=9, fontweight='bold')
ax1.set_title('Sessions by Building', color='#333333', fontsize=12)
ax1.set_ylabel('Sessions', color='#333333')
ax1.tick_params(colors='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# APs by building
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor(COLORS['bg'])
bldg_aps = [df[df['Building']==b]['apName'].nunique() for b in buildings]
bars = ax2.bar(buildings, bldg_aps, color=bldg_colors, edgecolor='#333333', linewidth=0.5)
for bar, a in zip(bars, bldg_aps):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
             f'{a}', ha='center', color='#333333', fontsize=11, fontweight='bold')
ax2.set_title('APs per Building', color='#333333', fontsize=12)
ax2.set_ylabel('APs', color='#333333')
ax2.tick_params(colors='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Sessions per AP (load)
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor(COLORS['bg'])
sess_per_ap = [s/a for s, a in zip(bldg_sessions, bldg_aps)]
bars = ax3.bar(buildings, sess_per_ap, color=bldg_colors, edgecolor='#333333', linewidth=0.5)
ax3.axhline(y=2000, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Overload threshold')
for bar, v in zip(bars, sess_per_ap):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
             f'{v:,.0f}', ha='center', color='#333333' if v < 4000 else 'red', fontsize=10, fontweight='bold')
ax3.set_title('Sessions/AP (Load)', color='#333333', fontsize=12)
ax3.set_ylabel('Sessions per AP', color='#333333')
ax3.legend(fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax3.tick_params(colors='#333333')
ax3.spines['bottom'].set_color(COLORS['grid'])
ax3.spines['left'].set_color(COLORS['grid'])
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# B77 Floor detail
ax4 = fig.add_subplot(gs[1, :])
ax4.set_facecolor(COLORS['bg'])

b77 = df[df['Building'] == 'B77']
b77_floors = sorted(b77['Floor'].unique())
floor_sessions = [len(b77[b77['Floor']==f]) for f in b77_floors]
floor_aps = [b77[b77['Floor']==f]['apName'].nunique() for f in b77_floors]
floor_weak = [b77[b77['Floor']==f]['is_weak'].mean()*100 for f in b77_floors]
floor_names = [str(f).replace('FL','') for f in b77_floors]

x = np.arange(len(b77_floors))
w = 0.35
bars1 = ax4.bar(x - w/2, floor_sessions, w, label='Sessions', color=COLORS['b77'], edgecolor='#333333', linewidth=0.5)
ax4_twin = ax4.twinx()
bars2 = ax4_twin.bar(x + w/2, floor_weak, w, label='Weak %', color=COLORS['critical'], alpha=0.7, edgecolor='#333333', linewidth=0.5)

for bar, s, aps in zip(bars1, floor_sessions, floor_aps):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200, 
             f'{s:,}\n({aps} APs)', ha='center', color='#333333', fontsize=8, fontweight='bold')
for bar, w_pct in zip(bars2, floor_weak):
    ax4_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                  f'{w_pct:.0f}%', ha='center', color='#FF6B6B', fontsize=9, fontweight='bold')

ax4.set_xticks(x)
ax4.set_xticklabels([f'Floor {n}' for n in floor_names], color='#333333')
ax4.set_ylabel('Sessions', color=COLORS['b77'], fontsize=11)
ax4_twin.set_ylabel('Weak Signal %', color=COLORS['critical'], fontsize=11)
ax4.set_title('B77 Floor Breakdown — FL1: 11,306 sessions/AP (3 APs for 33,919 sessions)', 
              color='#333333', fontsize=13, fontweight='bold')
ax4.tick_params(colors='#333333')
ax4_twin.tick_params(colors='#FF6B6B')
ax4.spines['bottom'].set_color(COLORS['grid'])
ax4.spines['left'].set_color(COLORS['b77'])
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4_twin.spines['right'].set_color(COLORS['critical'])

ax4.legend(loc='upper left', fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax4_twin.legend(loc='upper right', fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')

plt.savefig('output/slide_pain3_b77_overloaded.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [3/12] Pain 3 - B77 Overloaded ✓")

# ===========================
# GRAPH 4: PAIN 4+5 - Floor Danger Zones Heatmap
# ===========================
fig, axes = plt.subplots(1, 2, figsize=(18, 9), facecolor=COLORS['bg'])
fig.suptitle('PAIN 4-5: Critical Floor Zones — B25-FL9 (85% Weak), B31 AP Imbalance', 
             fontsize=18, fontweight='bold', color=COLORS['high'], y=0.98)

# Heatmap: Building x Floor weak%
wifi_buildings = ['B25', 'B31', 'B46', 'B67', 'B77', 'B79']
all_floors_set = set()
for b in wifi_buildings:
    bdf = df[df['Building']==b]
    for f in bdf['Floor'].unique():
        all_floors_set.add(str(f).replace('FL',''))

# Build matrix
floor_data = {}
for b in wifi_buildings:
    bdf = df[df['Building']==b]
    for f in bdf['Floor'].unique():
        fname = str(f).replace('FL','')
        fdf = bdf[bdf['Floor']==f]
        if len(fdf) > 50:
            floor_data[(b, fname)] = {
                'weak_pct': fdf['is_weak'].mean()*100,
                'sessions': len(fdf),
                'aps': fdf['apName'].nunique(),
                'sess_per_ap': len(fdf) / fdf['apName'].nunique()
            }

# Top 15 danger zones
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
danger_list = [(k, v) for k, v in floor_data.items()]
danger_list.sort(key=lambda x: x[1]['weak_pct'], reverse=True)
top15 = danger_list[:15]

labels = [f"{k[0]}-FL{k[1]}" for k, v in top15]
weak_vals = [v['weak_pct'] for k, v in top15]
sessions_vals = [v['sessions'] for k, v in top15]

bar_colors = ['#E53935' if w > 80 else '#FF7043' if w > 70 else '#FFB300' for w in weak_vals]
bars = ax1.barh(labels[::-1], weak_vals[::-1], color=bar_colors[::-1], edgecolor='#333333', linewidth=0.5)

for bar, w, s in zip(bars, weak_vals[::-1], sessions_vals[::-1]):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{w:.1f}% ({s:,} sess)', va='center', color='#333333', fontsize=9, fontweight='bold')

ax1.set_xlabel('Weak Signal %', color='#333333', fontsize=12)
ax1.set_title('Top 15 Floors by Weak Signal %', color='#333333', fontsize=13)
ax1.axvline(x=70, color='red', linestyle='--', linewidth=1, alpha=0.5)
ax1.set_xlim(0, 100)
ax1.tick_params(colors='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# AP density per floor (sessions/AP)
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
density_list = [(k, v) for k, v in floor_data.items()]
density_list.sort(key=lambda x: x[1]['sess_per_ap'], reverse=True)
top15d = density_list[:15]

labels_d = [f"{k[0]}-FL{k[1]}" for k, v in top15d]
density_vals = [v['sess_per_ap'] for k, v in top15d]
aps_vals = [v['aps'] for k, v in top15d]

bar_colors_d = ['#E53935' if d > 5000 else '#FF7043' if d > 2000 else '#FFB300' if d > 1000 else '#66BB6A' for d in density_vals]
bars = ax2.barh(labels_d[::-1], density_vals[::-1], color=bar_colors_d[::-1], edgecolor='#333333', linewidth=0.5)

for bar, d, aps in zip(bars, density_vals[::-1], aps_vals[::-1]):
    ax2.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, 
             f'{d:,.0f} ({aps} APs)', va='center', color='#333333', fontsize=9, fontweight='bold')

ax2.set_xlabel('Sessions per AP', color='#333333', fontsize=12)
ax2.set_title('Top 15 Floors by Load (Sessions/AP)', color='#333333', fontsize=13)
ax2.axvline(x=2000, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Overload line')
ax2.tick_params(colors='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('output/slide_pain4_5_floor_danger.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [4/12] Pain 4-5 - Floor Danger Zones ✓")

# ===========================  
# GRAPH 5: PAIN 6 - Student vs Staff Signal Gap
# ===========================
fig, axes = plt.subplots(1, 3, figsize=(18, 7), facecolor=COLORS['bg'])
fig.suptitle('PAIN 6: Student Signal Gap — 72.9% Weak vs Staff 58.0%', 
             fontsize=20, fontweight='bold', color=COLORS['high'], y=0.98)

acc_types = ['student', 'personnel', 'alumni', 'retirement', 'templecturer']
acc_labels = ['Student', 'Personnel', 'Alumni', 'Retirement', 'Temp Lect.']
acc_colors = ['#4FC3F7', '#FF8A65', '#81C784', '#BA68C8', '#FFD54F']

# Weak % comparison
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
acc_weak = [df[df['account_type']==a]['is_weak'].mean()*100 for a in acc_types]
bars = ax1.bar(acc_labels, acc_weak, color=acc_colors, edgecolor='#333333', linewidth=0.5)
for bar, w in zip(bars, acc_weak):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f'{w:.1f}%', ha='center', color='#333333', fontsize=11, fontweight='bold')
ax1.set_title('Weak Signal % by Account Type', color='#333333', fontsize=13)
ax1.set_ylabel('Weak %', color='#333333')
ax1.tick_params(colors='#333333', labelrotation=20)
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Avg RSSI
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
acc_rssi = [df[df['account_type']==a]['rssi'].mean() for a in acc_types]
bars = ax2.bar(acc_labels, acc_rssi, color=acc_colors, edgecolor='#333333', linewidth=0.5)
for bar, r in zip(bars, acc_rssi):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 1.5, 
             f'{r:.1f}', ha='center', color='#333333', fontsize=11, fontweight='bold')
ax2.set_title('Avg RSSI (dBm) by Account Type', color='#333333', fontsize=13)
ax2.set_ylabel('RSSI (dBm)', color='#333333')
ax2.axhline(y=-70, color='red', linestyle='--', alpha=0.5, label='Weak threshold')
ax2.tick_params(colors='#333333', labelrotation=20)
ax2.legend(fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Sessions share pie
ax3 = axes[2]
ax3.set_facecolor(COLORS['bg'])
acc_sessions = [len(df[df['account_type']==a]) for a in acc_types]
wedges, texts, autotexts = ax3.pie(acc_sessions, labels=acc_labels, colors=acc_colors,
    autopct='%1.1f%%', startangle=90, textprops={'color': '#333333', 'fontsize': 10})
for t in autotexts:
    t.set_fontsize(10)
    t.set_fontweight('bold')
ax3.set_title('Sessions by Account Type', color='#333333', fontsize=13)

fig.text(0.5, 0.02,
    'Student: Weak 72.9%, RSSI -74.0, SNR 15.2  |  Personnel: Weak 58.0%, RSSI -70.8, SNR 21.1  |  Gap: 14.9%',
    ha='center', fontsize=11, color=COLORS['high'], fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF3E0', edgecolor=COLORS['high'], alpha=0.9))

plt.tight_layout(rect=[0, 0.06, 1, 0.94])
plt.savefig('output/slide_pain6_student_gap.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [5/12] Pain 6 - Student Gap ✓")

# ===========================
# GRAPH 6: PAIN 7+8+9 - eduroam, Failed Sessions, Worst APs
# ===========================
fig = plt.figure(figsize=(18, 7), facecolor=COLORS['bg'])
fig.suptitle('PAIN 7-9: eduroam Gap, Failed Sessions (9.1%), Worst APs (93.7% Weak)', 
             fontsize=17, fontweight='bold', color=COLORS['medium'], y=0.98)
gs = GridSpec(1, 3, figure=fig, wspace=0.3)

# SSID comparison
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor(COLORS['bg'])
ssids = ['@KMUTNB', 'eduroam']
ssid_metrics = {
    'Weak %': [df[df['ssid']==s]['is_weak'].mean()*100 for s in ssids],
    'Avg RSSI': [abs(df[df['ssid']==s]['rssi'].mean()) for s in ssids],
}
x = np.arange(len(ssids))
w = 0.35
bars1 = ax1.bar(x - w/2, ssid_metrics['Weak %'], w, label='Weak %', color='#FF7043')
bars2 = ax1.bar(x + w/2, ssid_metrics['Avg RSSI'], w, label='|Avg RSSI|', color='#4FC3F7')
for bar, v in zip(bars1, ssid_metrics['Weak %']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{v:.1f}%', 
             ha='center', color='#333333', fontsize=10, fontweight='bold')
for bar, v in zip(bars2, ssid_metrics['Avg RSSI']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'-{v:.1f}', 
             ha='center', color='#333333', fontsize=10, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(ssids, color='#333333', fontsize=12)
ax1.set_title('SSID Comparison', color='#333333', fontsize=13)
ax1.legend(fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax1.tick_params(colors='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Failed sessions
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor(COLORS['bg'])
zero_data = (df['txRxBytes'] == 0).sum()
low_data = ((df['txRxBytes'] > 0) & (df['txRxBytes'] < 1024)).sum()
normal_data = (df['txRxBytes'] >= 1024).sum()
fail_labels = ['Zero Data\n(Connected but\nno transfer)', 'Very Low\n(<1KB)', 'Normal\n(>=1KB)']
fail_vals = [zero_data, low_data, normal_data]
fail_colors = ['#E53935', '#FF7043', '#66BB6A']
wedges, texts, autotexts = ax2.pie(fail_vals, labels=fail_labels, colors=fail_colors,
    autopct=lambda p: f'{p:.1f}%\n({int(p*total/100):,})', startangle=90, 
    textprops={'color': '#333333', 'fontsize': 9})
for t in autotexts:
    t.set_fontsize(8)
    t.set_fontweight('bold')
ax2.set_title('Session Data Transfer Status', color='#333333', fontsize=13)

# Worst APs
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor(COLORS['bg'])
ap_stats = df.groupby('apName').agg(
    sessions=('id','count'), weak_pct=('is_weak','mean'), avg_rssi=('rssi','mean'),
    building=('Building','first'), floor=('Floor','first')
).reset_index()
ap_stats['weak_pct'] *= 100
ap_worst = ap_stats[ap_stats['sessions'] >= 500].nlargest(10, 'weak_pct')

labels_ap = [f"{r['apName']}" for _, r in ap_worst.iterrows()]
weak_ap = ap_worst['weak_pct'].values

bar_colors_ap = ['#E53935' if w > 90 else '#FF7043' if w > 80 else '#FFB300' for w in weak_ap]
bars = ax3.barh(labels_ap[::-1], weak_ap[::-1], color=bar_colors_ap[::-1], edgecolor='#333333', linewidth=0.5)
for bar, w in zip(bars, weak_ap[::-1]):
    ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, 
             f'{w:.1f}%', va='center', color='#333333', fontsize=9, fontweight='bold')
ax3.set_xlabel('Weak %', color='#333333')
ax3.set_title('Top 10 Worst APs (min 500 sess)', color='#333333', fontsize=13)
ax3.set_xlim(0, 105)
ax3.tick_params(colors='#333333', labelsize=8)
ax3.spines['bottom'].set_color(COLORS['grid'])
ax3.spines['left'].set_color(COLORS['grid'])
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('output/slide_pain7_8_9_misc.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [6/12] Pain 7-8-9 ✓")

# ===========================
# GRAPH 7: INSIGHT 1+2 - Time Patterns (Double Peak + Weekday)
# ===========================
fig, axes = plt.subplots(2, 1, figsize=(16, 10), facecolor=COLORS['bg'])
fig.suptitle('INSIGHT 1-2: Double-Peak Pattern + Weekday 15x > Weekend', 
             fontsize=20, fontweight='bold', color=COLORS['accent'], y=0.98)

# Hourly pattern
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
hourly = df.groupby('hour').agg(sessions=('id','count'), users=('Username','nunique'), avg_rssi=('rssi','mean')).reset_index()

colors_h = []
for h in hourly['hour']:
    if h in [8, 11, 12, 15]:
        colors_h.append(COLORS['critical'])
    elif h in [9, 10, 13, 14, 16]:
        colors_h.append(COLORS['high'])
    elif h in [7, 17, 18]:
        colors_h.append(COLORS['medium'])
    else:
        colors_h.append(COLORS['accent'])

bars = ax1.bar(hourly['hour'], hourly['sessions'], color=colors_h, edgecolor='#333333', linewidth=0.3)
ax1_twin = ax1.twinx()
ax1_twin.plot(hourly['hour'], hourly['users'], color='#0277BD', linewidth=2, marker='o', markersize=5, label='Unique Users')

# Annotate peaks
for h, s, u in zip(hourly['hour'], hourly['sessions'], hourly['users']):
    if h in [8, 12, 15]:
        ax1.annotate(f'{s:,}\n({u:,} users)', xy=(h, s), xytext=(h, s+1500),
                     ha='center', color='#333333', fontsize=8, fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='#333333', lw=0.8))

ax1.set_xlabel('Hour', color='#333333', fontsize=12)
ax1.set_ylabel('Sessions', color=COLORS['high'], fontsize=12)
ax1_twin.set_ylabel('Unique Users', color='#0277BD', fontsize=12)
ax1.set_title('Hourly Usage Pattern — Peak: 08h (Entry), 11-12h (Lunch), 15h (Afternoon)', color='#333333', fontsize=13)
ax1.set_xticks(range(24))
ax1.tick_params(colors='#333333')
ax1_twin.tick_params(colors='#0277BD')
ax1_twin.legend(loc='upper left', fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['high'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1_twin.spines['right'].set_color('#0277BD')

# Daily pattern with weekend highlight
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
daily = df.groupby('day').agg(sessions=('id','count'), users=('Username','nunique'), weekday=('weekday','first')).reset_index()

daily_colors = ['#66BB6A' if wd < 5 else '#FF7043' for wd in daily['weekday']]
bars = ax2.bar(daily['day'], daily['sessions'], color=daily_colors, edgecolor='#333333', linewidth=0.3)
ax2_twin = ax2.twinx()
ax2_twin.plot(daily['day'], daily['users'], color='#0277BD', linewidth=2, marker='o', markersize=4)

ax2.set_xlabel('Day of January 2026', color='#333333', fontsize=12)
ax2.set_ylabel('Sessions', color='#333333', fontsize=12)
ax2_twin.set_ylabel('Unique Users', color='#0277BD', fontsize=12)
ax2.set_title('Daily Usage — Weekday avg 2,755 users/day vs Weekend 534 users/day (15x difference)', color='#333333', fontsize=13)
ax2.set_xticks(range(1, 32))
ax2.tick_params(colors='#333333')
ax2_twin.tick_params(colors='#0277BD')

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#66BB6A', label='Weekday'), Patch(facecolor='#FF7043', label='Weekend')]
ax2.legend(handles=legend_elements, fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2_twin.spines['right'].set_color('#0277BD')

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('output/slide_insight1_2_time_patterns.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [7/12] Insight 1-2 - Time Patterns ✓")

# ===========================
# GRAPH 8: INSIGHT 3+4 - Multi-device + iOS Dominance
# ===========================
fig, axes = plt.subplots(1, 3, figsize=(18, 7), facecolor=COLORS['bg'])
fig.suptitle('INSIGHT 3-4: 50.2% Multi-device Users + iOS Dominates 47.9%', 
             fontsize=20, fontweight='bold', color=COLORS['accent'], y=0.98)

# Multi-device distribution
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
user_devices = df.groupby('Username')['clientMac'].nunique()
dev_dist = user_devices.value_counts().sort_index()
dev_labels = [f'{n} dev' for n in dev_dist.index[:7]]
dev_counts = dev_dist.values[:7]
dev_colors_list = ['#66BB6A', '#4FC3F7', '#FFB300', '#FF7043', '#E53935', '#BA68C8', '#FF6B6B']

bars = ax1.bar(dev_labels, dev_counts, color=dev_colors_list[:len(dev_labels)], edgecolor='#333333', linewidth=0.5)
for bar, c in zip(bars, dev_counts):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30, 
             f'{c:,}', ha='center', color='#333333', fontsize=10, fontweight='bold')
ax1.set_title('Devices per User\n(50.2% have 2+ devices)', color='#333333', fontsize=13)
ax1.set_ylabel('Users', color='#333333')
ax1.tick_params(colors='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# OS Vendor pie
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
vendors = df['osVendorType'].value_counts()
vendor_labels = vendors.index[:5].tolist()
vendor_vals = vendors.values[:5].tolist()
vendor_colors = ['#4FC3F7', '#9E9E9E', '#66BB6A', '#42A5F5', '#FF7043']
wedges, texts, autotexts = ax2.pie(vendor_vals, labels=vendor_labels, colors=vendor_colors,
    autopct='%1.1f%%', startangle=90, textprops={'color': '#333333', 'fontsize': 10})
for t in autotexts:
    t.set_fontsize(10)
    t.set_fontweight('bold')
ax2.set_title('OS Vendor Distribution', color='#333333', fontsize=13)

# Device type pie
ax3 = axes[2]
ax3.set_facecolor(COLORS['bg'])
devtypes = df['deviceType'].value_counts()
dt_labels = devtypes.index.tolist()
dt_vals = devtypes.values.tolist()
dt_colors = ['#4FC3F7', '#9E9E9E', '#FF7043', '#66BB6A']
wedges, texts, autotexts = ax3.pie(dt_vals, labels=dt_labels, colors=dt_colors,
    autopct='%1.1f%%', startangle=90, textprops={'color': '#333333', 'fontsize': 10})
for t in autotexts:
    t.set_fontsize(10)
    t.set_fontweight('bold')
ax3.set_title('Device Type Distribution', color='#333333', fontsize=13)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('output/slide_insight3_4_devices.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [8/12] Insight 3-4 - Devices ✓")

# ===========================
# GRAPH 9: INSIGHT 5 - WiFi 6 Paradox
# ===========================
fig, axes = plt.subplots(1, 3, figsize=(18, 7), facecolor=COLORS['bg'])
fig.suptitle('INSIGHT 5: WiFi 6 Paradox — 79.6% Adoption but Worse Signal than Non-WiFi 6', 
             fontsize=18, fontweight='bold', color=COLORS['accent'], y=0.98)

wifi6 = df[df['is_wifi6']]
non_wifi6 = df[~df['is_wifi6']]

# Weak % comparison
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
cats = ['WiFi 6\n(79.6%)', 'Non-WiFi 6\n(20.4%)']
weak_comp = [wifi6['is_weak'].mean()*100, non_wifi6['is_weak'].mean()*100]
bars = ax1.bar(cats, weak_comp, color=['#4FC3F7', '#FF7043'], edgecolor='#333333', linewidth=0.5, width=0.5)
for bar, w in zip(bars, weak_comp):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f'{w:.1f}%', ha='center', color='#333333', fontsize=14, fontweight='bold')
ax1.set_title('Weak Signal %', color='#333333', fontsize=14)
ax1.set_ylabel('Weak %', color='#333333')
ax1.tick_params(colors='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# SNR comparison
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
snr_comp = [wifi6['snr'].mean(), non_wifi6['snr'].mean()]
bars = ax2.bar(cats, snr_comp, color=['#4FC3F7', '#FF7043'], edgecolor='#333333', linewidth=0.5, width=0.5)
for bar, s in zip(bars, snr_comp):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
             f'{s:.1f} dB', ha='center', color='#333333', fontsize=14, fontweight='bold')
ax2.set_title('Avg SNR (dB)', color='#333333', fontsize=14)
ax2.set_ylabel('SNR (dB)', color='#333333')
ax2.tick_params(colors='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Band breakdown for WiFi6
ax3 = axes[2]
ax3.set_facecolor(COLORS['bg'])
radio_stats = df.groupby('radioType').agg(
    sessions=('id','count'), weak_pct=('is_weak','mean'), avg_snr=('snr','mean')
).reset_index()
radio_stats['weak_pct'] *= 100
radio_stats = radio_stats.sort_values('sessions', ascending=True).tail(6)

bar_c = ['#66BB6A' if 'ax' in r else '#FF7043' for r in radio_stats['radioType']]
bars = ax3.barh(radio_stats['radioType'], radio_stats['weak_pct'], color=bar_c, edgecolor='#333333', linewidth=0.5)
for bar, w, s in zip(bars, radio_stats['weak_pct'], radio_stats['sessions']):
    ax3.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{w:.1f}% ({s:,})', va='center', color='#333333', fontsize=9, fontweight='bold')
ax3.set_xlabel('Weak %', color='#333333')
ax3.set_title('Weak % by Radio Type\n(Green=WiFi6)', color='#333333', fontsize=13)
ax3.set_xlim(0, 95)
ax3.tick_params(colors='#333333')
ax3.spines['bottom'].set_color(COLORS['grid'])
ax3.spines['left'].set_color(COLORS['grid'])
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

fig.text(0.5, 0.02,
    'WiFi 6 uses 5GHz (shorter range) → more weak signals despite better technology. AP placement matters more than protocol.',
    ha='center', fontsize=11, color='#0277BD', fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#E0F7FA', edgecolor='#0277BD', alpha=0.9))

plt.tight_layout(rect=[0, 0.06, 1, 0.94])
plt.savefig('output/slide_insight5_wifi6_paradox.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [9/12] Insight 5 - WiFi 6 Paradox ✓")

# ===========================
# GRAPH 10: INSIGHT 6+7 - Faculty Concentration + Roaming
# ===========================
fig, axes = plt.subplots(1, 2, figsize=(18, 8), facecolor=COLORS['bg'])
fig.suptitle('INSIGHT 6-7: Top 3 Faculties = 69% Traffic + 53.7% Roam 3+ Buildings', 
             fontsize=18, fontweight='bold', color=COLORS['accent'], y=0.98)

# Faculty-Building matrix
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
top_facs = df['faculty_name'].value_counts().head(8)
fac_names_short = {
    list(top_facs.index)[0]: 'CIT',
    list(top_facs.index)[1]: 'Sci',
    list(top_facs.index)[2]: 'Eng',
    list(top_facs.index)[3]: 'Edu',
    list(top_facs.index)[4]: 'President',
    list(top_facs.index)[5]: 'Arch',
    list(top_facs.index)[6]: 'STPD',
    list(top_facs.index)[7]: 'BID',
}

fac_bldg_data = []
for fac in top_facs.index:
    row = []
    for bldg in wifi_buildings:
        cnt = len(df[(df['faculty_name']==fac) & (df['Building']==bldg)])
        row.append(cnt)
    fac_bldg_data.append(row)

fac_bldg_arr = np.array(fac_bldg_data)
im = ax1.imshow(fac_bldg_arr, cmap='YlOrRd', aspect='auto')
ax1.set_xticks(range(len(wifi_buildings)))
ax1.set_xticklabels(wifi_buildings, color='#333333', fontsize=11)
ax1.set_yticks(range(len(top_facs)))
ax1.set_yticklabels([fac_names_short.get(f, f[:15]) for f in top_facs.index], color='#333333', fontsize=10)

for i in range(len(top_facs)):
    for j in range(len(wifi_buildings)):
        val = fac_bldg_arr[i, j]
        if val > 0:
            color = 'white' if val > 5000 else 'black'
            ax1.text(j, i, f'{val:,}', ha='center', va='center', color=color, fontsize=8, fontweight='bold')

ax1.set_title('Faculty × Building (sessions)', color='#333333', fontsize=13)
cb = plt.colorbar(im, ax=ax1, shrink=0.8)
cb.set_label('Sessions', color='#333333')
cb.ax.tick_params(colors='#333333')

# Roaming distribution
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
user_bldgs = df.groupby('Username')['Building'].nunique()
roam_dist = user_bldgs.value_counts().sort_index()

roam_colors = ['#66BB6A', '#4FC3F7', '#FFB300', '#FF7043', '#E53935', '#BA68C8']
bars = ax2.bar(roam_dist.index, roam_dist.values, color=roam_colors[:len(roam_dist)], edgecolor='#333333', linewidth=0.5)
for bar, c in zip(bars, roam_dist.values):
    pct = c / user_bldgs.shape[0] * 100
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30, 
             f'{c:,}\n({pct:.1f}%)', ha='center', color='#333333', fontsize=10, fontweight='bold')
ax2.set_xlabel('Buildings visited', color='#333333', fontsize=12)
ax2.set_ylabel('Users', color='#333333', fontsize=12)
ax2.set_title('User Roaming Behavior\n(53.7% visit 3+ buildings)', color='#333333', fontsize=13)
ax2.tick_params(colors='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('output/slide_insight6_7_faculty_roaming.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [10/12] Insight 6-7 - Faculty & Roaming ✓")

# ===========================
# GRAPH 11: INSIGHT 9 - B46 Best Practice vs others
# ===========================
fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=COLORS['bg'])
fig.suptitle('INSIGHT 9: B46 = Best Practice Model (AP/Floor = 5.25 → Only 48.5% Weak)', 
             fontsize=18, fontweight='bold', color=COLORS['accent'], y=0.98)

# Building comparison radar-like bar chart
ax1 = axes[0]
ax1.set_facecolor(COLORS['bg'])
metrics_names = ['Weak %', 'VeryPoor %', 'Avg |RSSI|', 'AP/Floor']
b_data = {}
for b in wifi_buildings:
    bdf = df[df['Building']==b]
    floors = bdf['Floor'].nunique()
    aps = bdf['apName'].nunique()
    b_data[b] = {
        'Weak %': bdf['is_weak'].mean()*100,
        'VeryPoor %': bdf['is_vpoor'].mean()*100,
        'Avg |RSSI|': abs(bdf['rssi'].mean()),
        'AP/Floor': aps/max(floors,1)
    }

x = np.arange(len(wifi_buildings))
width = 0.2
for i, metric in enumerate(['Weak %', 'VeryPoor %']):
    vals = [b_data[b][metric] for b in wifi_buildings]
    c = '#E53935' if 'VeryPoor' in metric else '#FF7043'
    bars = ax1.bar(x + i*width, vals, width, label=metric, color=c, alpha=0.8, edgecolor='#333333', linewidth=0.3)
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f'{v:.0f}%', ha='center', color='#333333', fontsize=8, fontweight='bold')

ax1.set_xticks(x + width/2)
ax1.set_xticklabels(wifi_buildings, color='#333333', fontsize=12)
ax1.set_ylabel('Percentage', color='#333333')
ax1.set_title('Signal Quality by Building', color='#333333', fontsize=13)
ax1.legend(fontsize=9, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax1.tick_params(colors='#333333')
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Highlight B46
ax1.annotate('BEST', xy=(2, b_data['B46']['Weak %']), xytext=(2, b_data['B46']['Weak %']-15),
             ha='center', color='#2E7D32', fontsize=14, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2))

# AP/Floor ratio vs Weak%
ax2 = axes[1]
ax2.set_facecolor(COLORS['bg'])
ap_floor_ratios = [b_data[b]['AP/Floor'] for b in wifi_buildings]
weak_pcts_b = [b_data[b]['Weak %'] for b in wifi_buildings]

for b, afr, wp, col in zip(wifi_buildings, ap_floor_ratios, weak_pcts_b, bldg_colors):
    ax2.scatter(afr, wp, c=col, s=200, edgecolors='#666666', linewidths=1.5, zorder=5)
    ax2.annotate(b, (afr, wp), textcoords="offset points", xytext=(10, 5), 
                 color='#333333', fontsize=12, fontweight='bold')

# Trend line
z = np.polyfit(ap_floor_ratios, weak_pcts_b, 1)
p = np.poly1d(z)
x_line = np.linspace(min(ap_floor_ratios)-0.5, max(ap_floor_ratios)+0.5, 100)
ax2.plot(x_line, p(x_line), '--', color='#0277BD', linewidth=1.5, alpha=0.7, label=f'Trend: more APs → less weak')

ax2.set_xlabel('APs per Floor', color='#333333', fontsize=13)
ax2.set_ylabel('Weak Signal %', color='#333333', fontsize=13)
ax2.set_title('AP Density vs Signal Quality\n(More APs/Floor = Better Signal)', color='#333333', fontsize=13)
ax2.legend(fontsize=10, facecolor=COLORS['bg'], edgecolor='#333333', labelcolor='#333333')
ax2.tick_params(colors='#333333')
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('output/slide_insight9_best_practice.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [11/12] Insight 9 - Best Practice ✓")

# ===========================
# GRAPH 12: PRIORITY MATRIX SUMMARY
# ===========================
fig, ax = plt.subplots(figsize=(18, 12), facecolor=COLORS['bg'])
ax.set_facecolor(COLORS['bg'])
fig.suptitle('PRIORITY MATRIX — Pain Points & Insights Summary', 
             fontsize=22, fontweight='bold', color='#333333', y=0.97)

# Data for priority matrix
items = [
    # (label, priority_score, impact_users_pct, type)
    ('P1: 70.4% Weak Signal', 10, 70.4, 'pain'),
    ('P2: 47% High Interference', 9.5, 47.0, 'pain'),
    ('P3: B77 Overloaded\n(11,306 sess/AP)', 9, 43.7, 'pain'),
    ('P4: B25-FL9 85% Weak', 8, 5.0, 'pain'),
    ('P5: B31 AP Imbalance', 7.5, 10.7, 'pain'),
    ('P6: Student Gap 14.9%', 8, 80.1, 'pain'),
    ('P7: eduroam 76.2% Weak', 6, 12.3, 'pain'),
    ('P8: 9.1% Failed Sessions', 6.5, 9.1, 'pain'),
    ('P9: Worst APs 93.7%', 7, 3.6, 'pain'),
    ('P10: 5GHz Weak > 2.4GHz', 4, 92.0, 'pain'),
    ('I1: Double-Peak Pattern', 8, 71.5, 'insight'),
    ('I2: Weekday 15x Weekend', 7, 93.7, 'insight'),
    ('I3: 50.2% Multi-device', 8, 50.2, 'insight'),
    ('I4: iOS 47.9%', 5, 47.9, 'insight'),
    ('I5: WiFi6 Paradox', 8.5, 79.6, 'insight'),
    ('I6: Top3 Fac = 69%', 6, 69.0, 'insight'),
    ('I7: 53.7% Roam 3+ Bldg', 6.5, 53.7, 'insight'),
    ('I9: B46 Best Practice', 7, 6.1, 'insight'),
]

for label, severity, impact, typ in items:
    color = '#E53935' if typ == 'pain' else '#00BCD4'
    marker = 's' if typ == 'pain' else '^'
    size = severity * 40
    alpha = 0.9 if severity >= 8 else 0.7
    ax.scatter(impact, severity, c=color, s=size, marker=marker, alpha=alpha, edgecolors='#666666', linewidths=1.5, zorder=5)
    ax.annotate(label, (impact, severity), textcoords="offset points", 
                xytext=(8, 5), color=color, fontsize=8, fontweight='bold')

# Quadrant lines
ax.axhline(y=7, color='#333333', linestyle='--', linewidth=0.5, alpha=0.3)
ax.axvline(x=50, color='#333333', linestyle='--', linewidth=0.5, alpha=0.3)

# Quadrant labels
ax.text(75, 9.5, 'CRITICAL\n(High Severity + Wide Impact)', color='red', fontsize=12, 
        ha='center', fontweight='bold', alpha=0.7)
ax.text(25, 9.5, 'HIGH\n(High Severity + Focused)', color='orange', fontsize=12, 
        ha='center', fontweight='bold', alpha=0.7)
ax.text(75, 4.5, 'MEDIUM\n(Low Severity + Wide)', color='#B8860B', fontsize=10, 
        ha='center', fontweight='bold', alpha=0.5)
ax.text(25, 4.5, 'LOW\n(Low Severity + Focused)', color='green', fontsize=10, 
        ha='center', fontweight='bold', alpha=0.5)

ax.set_xlabel('Impact Scope (% of sessions/users affected)', color='#333333', fontsize=14)
ax.set_ylabel('Severity Score', color='#333333', fontsize=14)
ax.set_xlim(0, 100)
ax.set_ylim(3, 11)
ax.tick_params(colors='#333333')
ax.spines['bottom'].set_color(COLORS['grid'])
ax.spines['left'].set_color(COLORS['grid'])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#E53935', markersize=12, label='Pain Point', linestyle='None'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor='#00BCD4', markersize=12, label='Insight', linestyle='None'),
]
ax.legend(handles=legend_elements, fontsize=12, facecolor=COLORS['bg'], edgecolor='#333333', 
          labelcolor='#333333', loc='lower right')

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('output/slide_priority_matrix.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
plt.close()
print("  [12/12] Priority Matrix ✓")

print("\n" + "=" * 60)
print("ALL 12 GRAPHS GENERATED SUCCESSFULLY!")
print("=" * 60)
print("\nFiles created in output/:")
print("  slide_pain1_signal_quality.png")
print("  slide_pain2_interference.png")
print("  slide_pain3_b77_overloaded.png")
print("  slide_pain4_5_floor_danger.png")
print("  slide_pain6_student_gap.png")
print("  slide_pain7_8_9_misc.png")
print("  slide_insight1_2_time_patterns.png")
print("  slide_insight3_4_devices.png")
print("  slide_insight5_wifi6_paradox.png")
print("  slide_insight6_7_faculty_roaming.png")
print("  slide_insight9_best_practice.png")
print("  slide_priority_matrix.png")
