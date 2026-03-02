import json

data = json.load(open('output/viz_data.json', 'r', encoding='utf-8'))
dh = data.get('daily_hourly_by_building', {})

# Compute actual peak daily-hourly users per building (matching new JS code)
peak_users = {}
for code, entries in dh.items():
    mx = 0
    for v in entries.values():
        if v['users'] > mx:
            mx = v['users']
    peak_users[code] = mx

print('=== PEAK USERS MAP (actual max per building) ===')
for code in ['B25','B31','B46','B67','B77','B79']:
    print(f'  {code}: peak={peak_users.get(code, 0)}')

def qualityColor(weakPct):
    if weakPct < 40: return '#38a169'   # green
    if weakPct < 55: return '#68d391'   # light green
    if weakPct < 65: return '#d69e2e'   # yellow
    if weakPct < 75: return '#ed8936'   # orange
    return '#e53e3e'                    # red

def heat_label(densityRatio):
    if densityRatio <= 0.05: return 'static-quality'
    if densityRatio < 0.25: return 'green #4ade80'
    if densityRatio < 0.45: return 'lime #a3e635'
    if densityRatio < 0.6: return 'yellow #facc15'
    if densityRatio < 0.8: return 'orange #f97316'
    return 'RED #ef4444'

# Test at several time points
test_points = [
    (7, 12, 'Weekday midday'),
    (8, 11, 'Peak day'),
    (1, 3, 'Late night'),
    (15, 8, 'Morning'),
    (20, 18, 'Evening'),
]

for day, hour, label in test_points:
    dhKey = f'{day}_{hour}'
    print(f'\n===== Day {day} Hour {hour} ({label}) =====')
    for b in data['buildings']:
        code = b['code']
        floors = b.get('floors', [])
        sorted_floors = sorted(floors, key=lambda x: x['floor_num'])
        numFloors = max(len(sorted_floors), 1)
        
        dhBuilding = dh.get(code, {})
        hourData = dhBuilding.get(dhKey)  # NO FALLBACK
        
        maxUsers = max(peak_users.get(code, 100), 1)
        densityRatio = min(hourData['users'] / maxUsers, 1) if hourData else 0
        
        totalFloorSessions = sum(f.get('sessions', 1) for f in sorted_floors)
        
        users = hourData['users'] if hourData else 0
        print(f'\n  {code}: users={users}/{maxUsers} -> density={densityRatio:.2f}')
        
        for i, floor in enumerate(sorted_floors):
            wp = floor['weak_pct']
            sess = floor.get('sessions', 1)
            floorWeight = sess / totalFloorSessions if totalFloorSessions > 0 else 1 / numFloors
            # NEW FORMULA: 60% base + 40% weighted
            floorDensity = densityRatio * (0.6 + 0.4 * floorWeight * numFloors)
            floorDensity = min(floorDensity, 1)
            
            base = qualityColor(wp)
            heat = heat_label(floorDensity)
            print(f'    FL{floor["floor_num"]}: weak={wp:.0f}% base={base} fDensity={floorDensity:.2f} -> {heat}')
