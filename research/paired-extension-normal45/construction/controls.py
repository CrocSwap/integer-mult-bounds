#!/usr/bin/env python3
"""controls.py -- independent re-verification of a produced allocation directory exactly the way #2917's check_allocation.py does:
fresh load of the vendored PR2839 engine from #2917's package, owner.check(T, ORDER, FILL, DISPATCH, PROFILE(claimed), PLAN, TEMPLATE, PROVIDERS),
the five semantic rejection controls (missing role, duplicate helper, same-call family collision, capacity overflow, changed paid profile),
the 82-buffer physical display (live + 408 + 8 + 82 + 2), and #2917's own exact dyadic moment auditor tools/audit_allocation_moment.run
(candidate = the directory, source = #2917's allocation/baseline = PR2908's pinned claim), plus root.py's bracket.
Usage: python controls.py OUT_DIR [--chronology pr2833-t37|pr2917-t74|pr2833-t74]   (writes OUT_DIR/CONTROLS.json)"""
import os, sys
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
import argparse, gzip, hashlib, json, pathlib, types, collections
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import root as R
import relax as X
import fill17 as F

def load(name, path):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(path.read_bytes(), str(path), 'exec'), m.__dict__); return m

ap = argparse.ArgumentParser(); ap.add_argument('out', type=pathlib.Path); ap.add_argument('--chronology', default=None)
ap.add_argument('--registry', type=pathlib.Path, default=F.PKG17 / 'allocation/PROVIDERS.json', help='PROVIDERS registry the fill must match (content)')
ap.add_argument('--buffers', type=int, default=82)
ap.add_argument('--auditor', type=pathlib.Path, default=F.PKG17 / 'tools/audit_allocation_moment.py')
ap.add_argument('--baseline', type=pathlib.Path, default=F.PKG17 / 'allocation/baseline')
a = ap.parse_args()
out = a.out.resolve()
assert hashlib.sha256(F.ENGINE.read_bytes()).hexdigest() == F.ENGINE_SHA
owners = load('c1_owners', F.ENGINE)
moment = load('c1_moment', a.auditor)
order, fill, raw_dispatch = F.read(out / 'ORDER.json'), F.read(out / 'FILL.json.gz'), F.read(out / 'DISPATCH.json')
profile = F.read(out / 'PROFILE.json'); providers_raw = F.read(out / 'PROVIDERS.json')
providers = {k: {'widths': v['widths'], 'actual_paid_profile': {int(r): n for r, n in v['actual_paid_profile'].items()}} for k, v in providers_raw.items()}
# the provider registry must be exactly #2917's (same widths per id, same local profile)
reg = F.read(a.registry)
assert {k: (v['widths'], {int(r): n for r, n in v['actual_paid_profile'].items()}) for k, v in reg.items()} == {k: (v['widths'], v['actual_paid_profile']) for k, v in providers.items()}, 'PROVIDERS differ from the registry'
dispatch = {(s, r): p for s, r, p in raw_dispatch}; assert len(dispatch) == len(raw_dispatch)
chron = a.chronology or json.load(open(out / 'OWNER-CHECK.json'))['chronology']
template, plan, c_order, c_dispatch, T = F.load_chronology(chron)
assert order == c_order and raw_dispatch == c_dispatch, 'ORDER/DISPATCH are not the %s chronology' % chron
assert len(order) // 9 == T
def check(candidate=fill, claimed=profile):
    return owners.check(T, order, candidate, dispatch, claimed, plan, template, providers)
result, _, _ = check()
assert result['roles'] == 9 * T * 408
physical = result['live'] + 408 + 8 + a.buffers + 2
controls = {}
def reject(name, candidate=fill, claimed=profile):
    try:
        check(candidate, claimed)
    except ValueError as e:
        controls[name] = str(e)
    else:
        raise AssertionError('owner corruption accepted: ' + name)
reject('missing_role', {**fill, 'rows': fill['rows'][:-1]})
first = fill['rows'][0]
j = next(i for i, r in enumerate(fill['rows'][1:], 1) if r[0] == first[0])
def mutate(index, row):
    rows = list(fill['rows']); rows[index] = row; return {**fill, 'rows': rows}
duplicate = list(fill['rows'][j]); duplicate[1] = first[1]; reject('duplicate_helper', mutate(j, duplicate))
collision = list(fill['rows'][j]); collision[2:5] = first[2:5]; reject('same_call_family_collision', mutate(j, collision))
overflow = list(first); overflow[5] = 49; reject('capacity_overflow', mutate(0, overflow))
wrong = dict(profile); wrong['1'] = wrong.get('1', 0) + 1; reject('changed_paid_profile', claimed=wrong)
# #2917's own exact dyadic moment auditor (source = its allocation/baseline = PR2908's pinned claim/profile/order)
exact = moment.run(out, a.baseline)
prof = {int(k): v for k, v in profile.items()}
k_lo, k_hi = R.kappa_from_profile(prof, T)
inv = collections.Counter(providers['gauge44']['widths'])
rel = X.relax(providers['gauge44']['actual_paid_profile'], dict(inv))
res = dict(status='PASS_C1_INDEPENDENT_RECHECK', chronology=chron, T=T, engine=result, physical=physical, controls=controls, moment=exact,
           root_bracket=[str(k_lo), str(k_hi)], root_lower_decimal=R.mpmath_str(k_lo, 25), relaxation_cap=[rel['cap_lower'], rel['cap_upper']],
           gain_vs_PR2917_claim=str(Q(exact['target']) - F.PR2917_KAPPA), gain_vs_PR2917_claim_float=float(Q(exact['target']) - F.PR2917_KAPPA),
           target_vs_PR2917_claim_decimal=str(Q(exact['target']) - F.PR2917_KAPPA), headline_target=exact['target_decimal'],
           gain_vs_PR2930_claim=str(Q(exact['target']) - F.PR2930_KAPPA), gain_vs_PR2930_claim_float=float(Q(exact['target']) - F.PR2930_KAPPA),
           registry=str(a.registry), buffers=a.buffers, auditor=str(a.auditor), auditor_sha256=hashlib.sha256(a.auditor.read_bytes()).hexdigest(), baseline=str(a.baseline),
           fill_sha256=hashlib.sha256((out / 'FILL.json.gz').read_bytes()).hexdigest(), files_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()})
(out / 'CONTROLS.json').write_text(json.dumps(res, sort_keys=True, indent=1, default=str) + '\n')
print(json.dumps({k: res[k] for k in ['status', 'chronology', 'T', 'physical', 'root_lower_decimal', 'gain_vs_PR2917_claim_float', 'gain_vs_PR2930_claim_float', 'gain_vs_PR2930_claim', 'headline_target']}, indent=1))
print('engine', result['roles'], result['idle'], 'rank_mass', result['rank_mass'])
print('controls', {k: v for k, v in controls.items()})
print('moment auditor', exact['status'], 'lower', exact['lower'], 'upper', exact['upper'], 'target', exact['target_decimal'][:40], 'gain vs baseline claim', exact['gain_decimal'][:30], 'previous', exact['previous'][:30])
