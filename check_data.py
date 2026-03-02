import json

d = json.load(open('output/viz_data.json', 'r', encoding='utf-8'))

# Check hourly data consistency
hb = d.get('hourly_by_building', {})
dhb = d.get('daily_hourly_by_building', {})
dc = d.get('daily_campus', {})
dhc = d.get('daily_hourly_campus', {})
ch = d.get('campus_hourly', {})

print("=== Building data vs hourly sums ===")
for b in d['buildings']:
    h_total = sum(v.get('sessions', 0) for v in hb.get(b['code'], {}).values())
    print(f"  {b['code']}: summary={b['total_sessions']}, hourly_sum={h_total}")

print("\n=== Campus totals ===")
total_daily = sum(v.get('sessions', 0) for v in dc.values())
total_hourly = sum(v.get('sessions', 0) for v in ch.values())
print(f"  summary={d['summary']['total_sessions']}, daily_sum={total_daily}, hourly_sum={total_hourly}")

print("\n=== Floor details per building ===")
for b in d['buildings']:
    print(f"  {b['code']} (max_floor={b['max_floor']}):")
    for f in b['floors']:
        print(f"    {f['floor']} num={f['floor_num']}: {f['sessions']} sessions, {f['unique_users']} users, rssi={f['avg_rssi']}, weak={f['weak_pct']}%")

print("\n=== Hourly by building key format ===")
for code in hb:
    keys = list(hb[code].keys())[:3]
    print(f"  {code}: keys like {keys}, type={type(keys[0])}")

print("\n=== Daily hourly campus sample (day 7, 12:00) ===")
print(f"  {dhc.get('7_12', 'MISSING')}")

print("\n=== Daily hourly by building sample (B77, day 7, 12:00) ===")
print(f"  {dhb.get('B77', {}).get('7_12', 'MISSING')}")
