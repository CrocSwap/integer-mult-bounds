"""Standard-library recount of data/OWNERS.json.gz against data/PLAN.json (a convenience check; the binding
checks are the strict replay's emit/audit stages). Prints the idle remainder profile and the global paid profile.
Usage: python3 recount_owners.py [PLAN.json OWNERS.json.gz]"""
import gzip, json, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
plan_path = Path(sys.argv[1]) if len(sys.argv) > 2 else HERE.parents[1] / 'data/PLAN.json'
owners_path = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parents[1] / 'data/OWNERS.json.gz'
plan = json.loads(plan_path.read_text())
roles = json.loads(gzip.decompress(owners_path.read_bytes()))
V = 112
calls = {(c['replica'], c['stage']): c['time'] for c in plan['provider_calls']}
widths = {(z['replica'], z['stage']): z['widths'] for z in plan['per_call_widths']}
used = defaultdict(set); per_call = defaultdict(list); fam = Counter()
for z in roles:
    key = f"{z['owner_replica']},{z['child']}"
    cap, times = plan['windows'][key]
    assert z['time'] == calls[z['replica'], z['stage']], 'call time'
    assert z['time'] in times, 'owner window'
    assert z['width'] == widths[z['replica'], z['stage']][z['helper']], 'helper width'
    assert z['copy'] == V * z['owner_replica'] + z['port'], 'copy identity'
    assert z['family'] == z['owner_replica'] * 896 + (2 * plan['pairs'][str(z['child'])] + plan['sides'][str(z['child'])]) * V + z['port'], 'family identity'
    cells = set(range(z['offset'], z['offset'] + z['width']))
    assert z['offset'] >= 0 and z['offset'] + z['width'] <= cap, 'capacity'
    slot = (z['owner_replica'], z['child'], z['port'])
    assert not (used[slot] & cells), 'overlapping slice'
    used[slot] |= cells
    per_call[z['time']].append(z['helper'])
    fam[z['time'], z['family']] += 1
assert max(fam.values()) == 1, 'two helpers of one call in one physical family'
for (r, s), t in calls.items():
    assert sorted(per_call[t]) == list(range(len(widths[r, s]))), 'complete helper inventory of call %d' % t
idle = Counter()
for key, (cap, times) in plan['windows'].items():
    owner, child = map(int, key.split(','))
    for port in range(V):
        cells = used[owner, child, port]
        assert cells == set(range(len(cells))), 'gap in pending prefix'
        if cap - len(cells): idle[cap - len(cells)] += 1
loc = Counter({int(k): v for k, v in plan['profile'].items()})
print('roles', len(roles), 'idle remainder profile', dict(sorted(idle.items())))
print('plan global profile', dict(sorted(loc.items())), 'rank mass', sum(k * v for k, v in loc.items()))
print('PASS_OWNERS_RECOUNT')
