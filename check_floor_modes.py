import json
with open('output/viz_data.json','r',encoding='utf-8') as f:
    vd = json.load(f)

b77 = next(b for b in vd['buildings'] if b['code']=='B77')
print("B77 monthly floor totals (bldg.floors):")
for f in sorted(b77['floors'], key=lambda x: x['floor_num']):
    print(f"  F{f['floor_num']}: users={f['unique_users']}, sessions={f['sessions']}, avg_rssi={f['avg_rssi']}, weak_pct={f['weak_pct']}")

print()
print("B77 daily floor (day=9):")
day9 = vd.get('daily_floor_by_building',{}).get('B77',{}).get('9',{})
for fn in sorted(day9.keys(), key=lambda x: int(x)):
    d = day9[fn]
    print(f"  F{fn}: users={d['users']}, sessions={d['sessions']}, avg_rssi={d['avg_rssi']}, weak_pct={d['weak_pct']}")

print()
print("B77 hourly floor (day=9, hour=16):")
dh = vd.get('daily_hourly_floor_by_building',{}).get('B77',{}).get('9_16',{})
for fn in sorted(dh.keys(), key=lambda x: int(x)):
    d = dh[fn]
    print(f"  F{fn}: users={d['users']}, sessions={d['sessions']}, avg_rssi={d['avg_rssi']}, weak_pct={d['weak_pct']}")

print()
# Specifically check: does screenshot F3=51 users, F1=-70.5 come from any mode?
print("=== CROSS-CHECK SCREENSHOT VALUES ===")
print("Screenshot F3 shows 51 users, -76.5 dBm")
print(f"  Monthly F3: users={b77['floors'][2]['unique_users'] if len(b77['floors'])>2 else '?'}")
print(f"  Daily F3: users={day9.get('3',{}).get('users','?')}")
print(f"  Hourly F3: users={dh.get('3',{}).get('users','?')}")

print()
print("Screenshot F1 shows -70.5 dBm, 120 users")
print(f"  Monthly F1: rssi={b77['floors'][0]['avg_rssi']}, users={b77['floors'][0]['unique_users']}")
print(f"  Daily F1: rssi={day9.get('1',{}).get('avg_rssi','?')}, users={day9.get('1',{}).get('users','?')}")
print(f"  Hourly F1: rssi={dh.get('1',{}).get('avg_rssi','?')}, users={dh.get('1',{}).get('users','?')}")

print()
print("Screenshot F2 shows -74.2 dBm, 91 users")
print(f"  Monthly F2: rssi={b77['floors'][1]['avg_rssi']}, users={b77['floors'][1]['unique_users']}")
print(f"  Daily F2: rssi={day9.get('2',{}).get('avg_rssi','?')}, users={day9.get('2',{}).get('users','?')}")
print(f"  Hourly F2: rssi={dh.get('2',{}).get('avg_rssi','?')}, users={dh.get('2',{}).get('users','?')}")
