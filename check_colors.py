import json

data = json.load(open('output/viz_data.json', 'r', encoding='utf-8'))

print('=== PER-BUILDING FLOOR DATA ===')
for b in data['buildings']:
    code = b['code']
    floors = b.get('floors', [])
    max_floor = b.get('max_floor', 0)
    print(f'\n--- {code} (max_floor={max_floor}, num_floors={len(floors)}) ---')
    for f in sorted(floors, key=lambda x: x['floor_num']):
        fn = f['floor_num']
        wp = f['weak_pct']
        sess = f['sessions']
        rssi = f.get('avg_rssi', '?')
        aps = f.get('ap_count', '?')
        print(f'  FL{fn}: weak_pct={wp:.1f}%, sessions={sess}, avg_rssi={rssi}, aps={aps}')
    print(f'  overall_weak_pct={b.get("overall_weak_pct","?")}%, avg_rssi={b.get("avg_rssi","?")}')

print('\n\n=== HOURLY BY BUILDING (sample hours) ===')
dh = data.get('daily_hourly_by_building', {})
hb = data.get('hourly_by_building', {})
for code in ['B25', 'B31', 'B46', 'B67', 'B77', 'B79']:
    # Check a few sample hours
    for h in ['0', '8', '12', '18', '23']:
        h_val = hb.get(code, {}).get(h, {})
        if h_val:
            print(f'{code} hour={h}: users={h_val.get("users","?")}, sessions={h_val.get("sessions","?")}')
    # Daily hourly sample
    dh_val = dh.get(code, {}).get('7_12', {})
    if dh_val:
        print(f'{code} day7_hr12: users={dh_val.get("users","?")}, sessions={dh_val.get("sessions","?")}')
    print()

print('=== MAX USERS PER BUILDING ===')
mu = data.get('max_users_per_building', {})
for code in ['B25', 'B31', 'B46', 'B67', 'B77', 'B79']:
    print(f'{code}: max_users={mu.get(code, "?")}')

# Now simulate the color logic
print('\n\n=== SIMULATED COLOR PIPELINE ===')
def qualityColor(weakPct):
    if weakPct < 40: return '#38a169'   # green
    if weakPct < 55: return '#68d391'   # light green
    if weakPct < 65: return '#d69e2e'   # yellow
    if weakPct < 75: return '#ed8936'   # orange
    return '#e53e3e'                    # red

def floorColorHex(weakPct, densityRatio):
    base = qualityColor(weakPct)
    if densityRatio <= 0.05:
        return base, 'static-quality'
    if densityRatio < 0.25: heat = '#4ade80'
    elif densityRatio < 0.45: heat = '#a3e635'
    elif densityRatio < 0.6: heat = '#facc15'
    elif densityRatio < 0.8: heat = '#f97316'
    else: heat = '#ef4444'
    return f'blend({base}+{heat}@60%)', f'density={densityRatio:.2f}'

# Simulate for day=7 hour=12
currentDay = 7
currentHour = 12
dhKey = f'{currentDay}_{currentHour}'

for b in data['buildings']:
    code = b['code']
    floors = b.get('floors', [])
    sorted_floors = sorted(floors, key=lambda x: x['floor_num'])
    numFloors = max(len(sorted_floors), 1)
    
    # Building-level density
    dhBuilding = dh.get(code, {})
    hourData = dhBuilding.get(dhKey) or hb.get(code, {}).get(str(currentHour))
    
    maxUsersBuilding = 600 if code == 'B77' else 400
    densityRatio = min(hourData['users'] / maxUsersBuilding, 1) if hourData else 0
    
    totalFloorSessions = sum(f.get('sessions', 1) for f in sorted_floors)
    
    print(f'\n--- {code} (densityRatio={densityRatio:.3f}, users={hourData["users"] if hourData else 0}, max={maxUsersBuilding}) ---')
    
    for i, floor in enumerate(sorted_floors):
        wp = floor['weak_pct']
        sess = floor.get('sessions', 1)
        floorWeight = sess / totalFloorSessions if totalFloorSessions > 0 else 1 / numFloors
        floorDensity = densityRatio * (0.4 + floorWeight * numFloors * 0.6)
        floorDensity = min(floorDensity, 1)
        
        color, note = floorColorHex(wp, floorDensity)
        base = qualityColor(wp)
        print(f'  FL{floor["floor_num"]} (idx={i}): weak_pct={wp:.1f}%, base={base}, weight={floorWeight:.3f}, floorDensity={floorDensity:.3f}, color={color} ({note})')

# Check if hourly keys are strings vs ints
print('\n\n=== KEY TYPE CHECK ===')
for code in ['B77']:
    keys = list(hb.get(code, {}).keys())[:5]
    print(f'{code} hourly keys sample: {keys} (type={type(keys[0]) if keys else "?"})')
    dh_keys = list(dh.get(code, {}).keys())[:5]
    print(f'{code} daily_hourly keys sample: {dh_keys} (type={type(dh_keys[0]) if dh_keys else "?"})')
