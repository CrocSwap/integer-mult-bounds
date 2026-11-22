"""rebind.py: rebind PR1319's T74 data (PLAN/SPEC) to new native provider directories with UNCHANGED interfaces (ports,
centres, widths), for discovery -> unpin -> freeze -> strict replay.  Updates only provider-derived fields:
provider_registry.<pid>.{actual_paid_profile, artifact_semantic_sha256, artifact_sha256, orientation_program_sha256},
provider_calls[*].local_program_sha256, PLAN.profile (recomputed from the dispatch and the new local paid profiles plus the
unchanged idle remainder), and SPEC.data.plan_sha256 / SPEC.expected.global_profile.
usage: rebind.py PR1319_PKG_DIR GAUGE44_LOCAL EXTRA_LOCAL OUT_DATA_DIR  (also writes PROFILE.json with the new global profile)"""
import collections, gzip, hashlib, json, shutil, sys
from pathlib import Path
pkg, loc_g, loc_e, out = map(Path, sys.argv[1:5]); sys.path.insert(0, str(pkg / 'code'))
from generated_identity import artifact_identities
def rd(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(parents=True, exist_ok=False)
for n in ['PLAN.json', 'PROFILE.json', 'OWNERS.json.gz', 'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz']: shutil.copy2(pkg / n, out / n)
plan = rd(pkg / 'PLAN.json'); spec = rd(pkg / 'new/SPEC.json'); old_profile = dict(plan['profile'])   # SPEC base = the frozen outer-refinement new/SPEC.json (rebound fields only are rewritten)
locs = {'gauge44': loc_g, 'extra': loc_e}; counts = collections.Counter(c['provider'] for c in plan['provider_calls']); changes = {}
for pid, d in locs.items():
    desc = plan['provider_registry'][pid]; word = rd(d / 'CANONICAL-WORD.json.gz'); checks = rd(d / 'LOCAL-CHECKS.json')
    assert word['ports'] == desc['ports'] and word['centers'] == desc['centers'], pid
    widths = [len(word['frames'][word['final'][r]]) - len(word['frames'][word['start'][r]]) for r in range(2 * 112, 2 * 112 + word['R'])]
    if widths != desc['widths']:   # width-changing rebind (borrowed words): helper count/widths come from the native word
        assert len(widths) == word['R'], pid
        desc['widths'] = widths
        for c in plan['per_call_widths']:
            if plan['provider_calls'][c['time']]['provider'] == pid: c['widths'] = widths
    new = dict(actual_paid_profile={str(k): v for k, v in sorted({int(k): v for k, v in checks['forward']['paid_profile'].items()}.items())},
               artifact_semantic_sha256=artifact_identities(d),
               artifact_sha256={name: sha(d / name) for name in desc['artifact_sha256']},
               orientation_program_sha256={o: checks[o]['sha256'] for o in ('backward', 'forward')})
    changes[pid] = {k: (desc.get(k), v) for k, v in new.items() if desc.get(k) != v}
    desc.update(new)
    for c in plan['provider_calls']:
        if c['provider'] == pid: c['local_program_sha256'] = checks[c['orientation']]['sha256']
prof = collections.Counter()
for pid, n in counts.items():
    for r, v in plan['provider_registry'][pid]['actual_paid_profile'].items(): prof[int(r)] += n * v
idle = {int(r): v for r, v in rd(pkg / 'CONSTRUCTION.json')['idle'].items()}   # exact idle ranks of the shipped owner fill
for r, v in idle.items(): prof[r] += v
new_profile = {str(k): v for k, v in sorted(prof.items())}
# sanity: the recomputation reproduces the OLD profile from the OLD local profiles
oldp = collections.Counter()
for pid, n in counts.items():
    for r, v in rd(pkg / 'PLAN.json')['provider_registry'][pid]['actual_paid_profile'].items(): oldp[int(r)] += n * v
for r, v in idle.items(): oldp[r] += v
assert {str(k): v for k, v in oldp.items()} == {k: v for k, v in old_profile.items()}, 'profile recomputation rule mismatch'
plan['profile'] = new_profile
(out / 'PROFILE.json').write_text(json.dumps(new_profile, separators=(',', ':')) + '\n')
(out / 'PLAN.json').write_text(json.dumps(plan, indent=2) + '\n')
spec['data']['plan_sha256'] = sha(out / 'PLAN.json'); spec['data']['owners_sha256'] = sha(pkg / 'OWNERS.json.gz'); spec['expected']['global_profile'] = new_profile
roles = rd(pkg / 'OWNERS.json.gz'); R = len(next(iter(plan['provider_registry'].values()))['widths'])
spec['expected'].update(idle_remainder_profile={str(k): v for k, v in sorted(idle.items())}, idle_remainders=sum(idle.values()), hosted_residuals=len(roles),
                        cross_replica_helper_roles=sum(z['replica'] != z['owner_replica'] for z in roles), physical=spec['expected']['live'] + 8 + R + 2)
for pid, desc in plan['provider_registry'].items(): spec['providers'].setdefault(pid, {})['inventory'] = {str(k): v for k, v in sorted(collections.Counter(desc['widths']).items())}
piv = {x['pivot'] for x in rd(pkg / spec['pivot_swap']['recipe'])['swaps']}   # same expectation as code/witness.py spot_widths()
assert all(desc['widths'][h] == (9 if 2 * 112 + h in piv else 8) for desc in plan['provider_registry'].values() for h in spec['width_spot_helpers']), 'spot helper width pins'
(out / 'SPEC.json').write_text(json.dumps(spec, indent=2) + '\n')
json.dump(dict(provider_counts=counts, old_profile=old_profile, new_profile=new_profile, changed_fields={p: sorted(c) for p, c in changes.items()},
               new_paid={p: plan['provider_registry'][p]['actual_paid_profile'] for p in locs}), open(out / 'REBIND.json', 'w'), indent=1, sort_keys=True)
print('provider counts', dict(counts), '| new profile', new_profile, '| changed', {p: sorted(c) for p, c in changes.items()})
