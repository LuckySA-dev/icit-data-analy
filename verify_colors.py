import json
data = json.load(open('output/viz_data.json','r',encoding='utf-8'))
dh = data.get('daily_hourly_by_building', {})

peaks = {}
for code, entries in dh.items():
    mx = 0
    for v in entries.values():
        if v['users'] > mx: mx = v['users']
    peaks[code] = mx

def impact_color(weakPct, densityRatio):
    if densityRatio <= 0.02: return 'GRAY #b0bec5'
    qBad = weakPct / 100
    impact = min(densityRatio * (0.3 + 0.7 * qBad), 1)
    fadeIn = min(densityRatio / 0.15, 1)
    fade_note = f' (fade={fadeIn:.0%})' if fadeIn < 1 else ''
    if impact < 0.33: return f'GREEN->YELLOW (impact={impact:.2f}){fade_note}'
    elif impact < 0.66: return f'YELLOW->ORANGE (impact={impact:.2f}){fade_note}'
    else: return f'ORANGE->RED (impact={impact:.2f}){fade_note}'

tests = [
    (15, 23, '23:00 late night (SCREENSHOT)'),
    (15, 3,  '03:00 deep night'),
    (7, 12,  '12:00 weekday peak'),
    (8, 11,  '11:00 absolute peak'),
    (15, 8,  '08:00 morning'),
    (20, 18, '18:00 evening'),
]

for day, hour, label in tests:
    key = f'{day}_{hour}'
    print(f'\n=== {label} (day {day} hour {hour}) ===')
    for b in data['buildings']:
        code = b['code']
        hd = dh.get(code, {}).get(key)
        pk = max(peaks.get(code, 100), 1)
        users = hd['users'] if hd else 0
        dr = min(users / pk, 1) if hd else 0
        floors = sorted(b.get('floors', []), key=lambda x: x['floor_num'])
        print(f'  {code}: {users}/{pk} users (density={dr:.3f})')
        for f in floors[:3]:
            fn = f['floor_num']
            wp = f['weak_pct']
            c = impact_color(wp, dr)
            print(f'    FL{fn}: weak={wp:.0f}% -> {c}')
        if len(floors) > 3:
            print(f'    ... ({len(floors)} floors total)')
