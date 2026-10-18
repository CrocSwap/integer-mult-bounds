#!/usr/bin/env python3
"""double.py -- if #2917's T74 chronology is the exact interleaving of two copies of PR2833's T37 chronology
(order74[2k] = order37[k], order74[2k+1] = (stage, replica+37), dispatch copied), a T37 fill doubles into a T74 fill
on #2917's OWN chronology: row (t,h,o,c,p,z) -> (2t,h,o,c,p,z) and (2t+1,h,o+37,c,p,z).  Verified by the vendored engine.
Usage: python double.py T37_DIR OUT_DIR"""
import os, sys
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
import collections, hashlib, json, pathlib, types, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import root as R, relax as X, fill17 as F
src, out = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=False)
owner = types.ModuleType('frozen_owner'); exec(compile(F.ENGINE.read_bytes(), 'frozen_owner', 'exec'), owner.__dict__)
t37 = F.load_chronology('pr2833-t37'); t74 = F.load_chronology('pr2917-t74')
order37, disp37 = t37[2], {(s, r): p for s, r, p in t37[3]}
template, plan, order74, dispatch74, T = t74
disp74 = {(s, r): p for s, r, p in dispatch74}
ok_order = all(order74[2 * k] == order37[k] and order74[2 * k + 1] == [order37[k][0], order37[k][1] + 37] for k in range(333))
ok_disp = all(disp74[(s, r)] == disp37[(s, r)] and disp74[(s, r + 37)] == disp37[(s, r)] for s, r in map(tuple, order37))
print('order74 == interleave(order37, order37+37):', ok_order, '; dispatch copied:', ok_disp)
assert ok_order and ok_disp
fill37 = F.read(src / 'FILL.json.gz')
providers = F.load_providers(F.PKG17 / 'allocation/PROVIDERS.json')
assert F.read(src / 'PROVIDERS.json')['gauge44']['widths'] == providers['gauge44']['widths']
rows = []
for t, h, o, c, p, z in fill37['rows']:
    rows.append([2 * t, h, o, c, p, z]); rows.append([2 * t + 1, h, o + 37, c, p, z])
fill = {'columns': fill37['columns'], 'dispatch_overrides': [], 'method': fill37.get('method', '') + ' | doubled from the T37 fill onto #2917 T74 chronology (order74 = interleave of two T37 copies; double.py)', 'rows': sorted(rows)}
t0 = time.time()
result, _, _ = owner.check(T, order74, fill, disp74, None, plan, template, providers)
print('engine PASS in %.1f s' % (time.time() - t0), result['roles'], result['idle'], 'rank_mass', result['rank_mass'], 'live', result['live'])
profile = {int(k): v for k, v in result['profile'].items()}
prof37 = {int(k): v for k, v in F.read(src / 'PROFILE.json').items()}
assert profile == {r: 2 * n for r, n in prof37.items()}, 'profile is not 2x the T37 profile'
inv = collections.Counter(providers['gauge44']['widths'])
rel = X.relax(providers['gauge44']['actual_paid_profile'], dict(inv))
k_lo, k_hi, pr = F.price(profile, T, rel)
prov_out = {pid: {'actual_paid_profile': {str(r): n for r, n in providers[pid]['actual_paid_profile'].items()}, 'widths': providers[pid]['widths']} for pid in providers}
payload_sha = {}
for n, obj in [('ORDER.json', order74), ('FILL.json.gz', fill), ('DISPATCH.json', dispatch74), ('PROFILE.json', {str(k): v for k, v in sorted(profile.items())}), ('PROVIDERS.json', prov_out)]:
    F.save(out / n, obj); payload_sha[n] = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
check = dict(result, status='PASS_VENDORED_PR2839_OWNER_ENGINE_CHECK', solver='DOUBLED_FROM_T37_FILL ' + str(src), chronology='pr2917-t74', T=T, calls=len(order74),
             physical=result['live'] + 408 + 8 + 82 + 2, physical_formula='live + 408 helpers + 8 centres + 82 private buffers + 2 guards',
             inventory={pid: dict(sorted(inv.items())) for pid in providers}, local=providers['gauge44']['actual_paid_profile'], engine_sha256=F.ENGINE_SHA, payload_sha256=payload_sha, **pr)
F.save(out / 'OWNER-CHECK.json', check)
print('physical', check['physical'], 'KAPPA', pr['kappa_lower_decimal'], '..', pr['kappa_upper_decimal'], 'cap', rel['cap_upper_decimal'], 'gap %.3e' % pr['gap_to_relaxation_cap'], 'gain vs PR2917 claim %.6e' % pr['gain_vs_PR2917_claim_float'])
print('payload sha', payload_sha)
