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
for n in ['PLAN.json', 'SPEC.json', 'PROFILE.json', 'OWNERS.json.gz', 'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz']: shutil.copy2(pkg / n, out / n)
plan = rd(pkg / 'PLAN.json'); spec = rd(pkg / 'SPEC.json'); old_profile = dict(plan['profile'])
locs = {'gauge44': loc_g, 'extra': loc_e}; counts = collections.Counter(c['provider'] for c in plan['provider_calls']); changes = {}
for pid, d in locs.items():
    desc = plan['provider_registry'][pid]; word = rd(d / 'CANONICAL-WORD.json.gz'); checks = rd(d / 'LOCAL-CHECKS.json')
    assert word['ports'] == desc['ports'] and word['centers'] == desc['centers'], pid
    widths = [len(word['frames'][word['final'][r]]) - len(word['frames'][word['start'][r]]) for r in range(2 * 112, 2 * 112 + word['R'])]
    assert widths == desc['widths'], (pid, 'widths changed')
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
idle = {int(r): v for r, v in spec['expected']['idle_remainder_profile'].items()}
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
spec['data']['plan_sha256'] = sha(out / 'PLAN.json'); spec['expected']['global_profile'] = new_profile
(out / 'SPEC.json').write_text(json.dumps(spec, indent=2) + '\n')
json.dump(dict(provider_counts=counts, old_profile=old_profile, new_profile=new_profile, changed_fields={p: sorted(c) for p, c in changes.items()},
               new_paid={p: plan['provider_registry'][p]['actual_paid_profile'] for p in locs}), open(out / 'REBIND.json', 'w'), indent=1, sort_keys=True)
print('provider counts', dict(counts), '| new profile', new_profile, '| changed', {p: sorted(c) for p, c in changes.items()})
