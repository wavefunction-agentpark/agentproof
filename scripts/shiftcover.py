# shiftcover.py - minimal shift-coverage planner. Free. No deps. Offline. Public domain.
def cover(open_hours, staff):
    plan = {h: None for h in open_hours}
    def scarcity(h):
        return sum(1 for s in staff.values() if h in s['avail'])
    for h in sorted(open_hours, key=scarcity):
        cands = [(n, s['wage']) for n, s in staff.items() if h in s['avail']]
        plan[h] = 'UNCOVERED' if not cands else min(cands, key=lambda x: x[1])[0]
    return plan

def bill(plan, staff):
    return sum(staff[p]['wage'] for p in plan.values() if p in staff)

if __name__ == '__main__':
    open_hours = list(range(9, 18))
    staff = {'Ana': {'wage': 12.0, 'avail': set(range(9,14))}, 'Ben': {'wage': 10.0, 'avail': set(range(12,18))}, 'Cara': {'wage': 15.0, 'avail': set(range(9,18))}}
    plan = cover(open_hours, staff)
    for h in sorted(plan): print(h, plan[h])
    print('Total wage bill:', bill(plan, staff))
