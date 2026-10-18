"""Independent candidate native profile, widths, owner intervals and exact moment.

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0. The independent rational
interval engine is Chafik Boukhalfa's retained PR626 extras/exact_intervals.py.
This checker does not import PR627 construction or global accounting code.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--package', type=Path, required=True)
ap.add_argument('--replay', type=Path, required=True)

ap.add_argument('--out', type=Path, required=True)

a = ap.parse_args()

def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)

def need(value, message):
    if not value:
        raise ValueError(message)

spec = read(a.package/'data/SPEC.json')
plan = read(a.package/'data/PLAN.json')
roles = read(a.package/'data/OWNERS.json.gz')
reference = Path(__file__).resolve().parent/'REFERENCE.json'
need(hashlib.sha256(reference.read_bytes()).hexdigest() == 'b0025f5823a38ce4c80c2ca82101f495decfa12e1970c6d7c716baabf59f5094', 'reference geometry pin')
old = read(reference)
expected_changes = old['expected_width_changes']
for key in ('order', 'windows', 'pairs', 'sides'):
    need(plan[key] == old[key], 'inherited geometry '+key)
widths = {}
profiles = {}
for pid in ('jp8', 'ck', 'j249'):
    word = read(a.replay/(pid+'-local')/'CANONICAL-WORD.json.gz')
    program = read(a.replay/(pid+'-local')/'LOCAL-PROGRAMS.json.gz')
    need((word['v'], word['h'], word['R']) == (112,9,492), 'native shape')
    widths[pid] = [len(word['frames'][word['final'][h]]) - len(word['frames'][word['start'][h]]) for h in range(224,716)]
    profiles[pid] = Counter(e[-1] for e in program['forward'] if e[0] in ('climb','center'))
    need(profiles[pid] == Counter(e[-1] for e in program['backward'] if e[0] in ('climb','center')), 'reflected profile')
    need(widths[pid] == spec['providers'][pid]['complete_contract']['widths'], 'native width declarations')
    changes = [(i,u,v) for i,(u,v) in enumerate(zip(old['provider_registry'][pid]['widths'],widths[pid])) if u != v]
    need([list(c) for c in changes] == expected_changes[pid], 'reviewed native width changes')
    need(profiles[pid] == Counter({int(r):n for r,n in plan['provider_registry'][pid]['actual_paid_profile'].items()}), 'native paid registry profile')
calls = {c['time']:c for c in plan['provider_calls']}
need(set(calls) == set(range(72)), 'complete calls')
need(len(plan['provider_calls']) == 72 and all(c['provider'] in widths for c in calls.values()), 'unique valid dispatch')
paid = sum((profiles[c['provider']] for c in calls.values()), Counter())
used = defaultdict(set)
helpers = defaultdict(set)
families = defaultdict(set)
for r in roles:
    t = r['time']; c = calls[t]; h = r['helper']
    need((c['stage'],c['replica']) == (r['stage'],r['replica']) == tuple(plan['order'][t]), 'call ordering')
    need(0 <= h < 492 and h not in helpers[t], 'helper uniqueness')
    need(0 <= r['port'] < 112 and 0 <= r['owner_replica'] < 8, 'owner/port range')
    need(r['family'] not in families[t], 'family uniqueness')
    helpers[t].add(h); families[t].add(r['family'])
    width = widths[c['provider']][h]
    need(r['width'] == width, 'actual width')
    need(r['family'] == r['owner_replica']*896+(2*plan['pairs'][str(r['child'])]+plan['sides'][str(r['child'])])*112+r['port'], 'physical family')
    need(r['copy'] == r['owner_replica']*112+r['port'], 'physical copy')
    key = r['owner_replica'],r['child'],r['port']
    cap,window = plan['windows'][str(key[0])+','+str(key[1])]
    need(t in window and 0 <= r['offset'] <= r['offset']+width <= cap, 'window and capacity')
    cells = set(range(r['offset'],r['offset']+width))
    need(not cells & used[key], 'disjoint intervals')
    used[key].update(cells)
need(len(roles) == 35424 and all(helpers[t] == set(range(492)) for t in calls), 'all roles')
idle = Counter()
for key,(cap,_) in plan['windows'].items():
    rep,ch = map(int,key.split(','))
    for port in range(112):
        cells = used[rep,ch,port]
        need(cells == set(range(len(cells))), 'compact interval')
        if len(cells) < cap:
            idle[cap-len(cells)] += 1
paid.update(idle)
need(dict(paid) == {int(k):v for k,v in plan['profile'].items()} == {int(k):v for k,v in spec['expected']['global_profile'].items()}, 'native plus idle profile')
need(sum(k*v for k,v in paid.items()) == 520704, 'rank mass')
need(73*7168-sum(k*v for k,v in paid.items()) == 2560, 'deficit')
interval_path = Path(__file__).resolve().parent/'exact_intervals.py'
need(hashlib.sha256(interval_path.read_bytes()).hexdigest() == 'aa3c2327c5d3742248b720a87b2de0bbe2e34ed2af89a578e3c8d5bd2656a9cf', 'independent interval engine pin')
s = importlib.util.spec_from_file_location('independent_intervals', interval_path)
E = importlib.util.module_from_spec(s); s.loader.exec_module(E)
q = Q(spec['expected']['complex_lower']); lower = upper = Q(0)
for rank,count in paid.items():
    lo,hi = E.log(Q(73,rank)); lo,hi = E.exp(q*lo,q*hi)
    lower += Q(rank*count,73*7168)*lo; upper += Q(rank*count,73*7168)*hi
need(upper < 1, 'strict exact moment')
kappa = Q(spec['expected']['kappa']); old_kappa = Q('0.001636464689763295')
need(kappa <= q/(1+q) and kappa > old_kappa, 'strict frontier gain and conversion')
report = dict(status='PASS_INDEPENDENT_NATIVE_OWNERS_AND_MOMENT', roles=len(roles), calls=len(calls), native_profiles={p:dict(c) for p,c in profiles.items()}, idle=dict(idle), global_profile=dict(paid), complex_lower=str(q), moment_lower=str(lower), moment_upper=str(upper), strict_margin_lower=str(1-upper), kappa=str(kappa), previous_verified_kappa=str(old_kappa), absolute_kappa_gain=str(kappa-old_kappa), relative_kappa_gain=str(kappa/old_kappa-1), interval_engine_sha256=hashlib.sha256(interval_path.read_bytes()).hexdigest(), scope='Literal finite native profile and width/owner interval accounting with a separate rational moment engine; strict supplier/physical/phase/outer admission is checked by the separate full replay.')
a.out.write_text(json.dumps(report,indent=2)+'\n')
print(report['status'])
