"""Bind a frozen explicit owner map to exact native local artifacts.

This preparer nominates a witness. The separate serialized controller audit,
finite invoice, two exact moment engines and strict pinned replay admit it.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import shutil

from generated_identity import artifact_identities, FILES

assert __debug__, 'Assertions required'


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--parent', type=Path, required=True)
ap.add_argument('--owners', type=Path, required=True)
ap.add_argument('--local', type=Path, required=True)
ap.add_argument('--data', type=Path, required=True)
args = ap.parse_args()
args.data.mkdir(parents=True, exist_ok=True)
parent_path = args.parent / 'data/PLAN.json'
assert sha(parent_path) == '258a8b9baa245fa4096828671e2f1d1462b5af08d56890629622ef6125eaddda'
plan = read(parent_path)
word = read(args.local / 'CANONICAL-WORD.json.gz')
checks = read(args.local / 'LOCAL-CHECKS.json')
assert (word['v'], word['h'], word['R']) == (112, 9, 492)
widths = [len(word['frames'][word['final'][224+h]]) -
          len(word['frames'][word['start'][224+h]]) for h in range(492)]
profile = {int(k): v for k, v in word['local_profile'].items()}
assert profile == {1: 2514, 2: 404, 3: 448, 4: 160, 5: 56, 8: 8}
assert Counter(widths) == {4: 52, 5: 48, 7: 34, 8: 114, 9: 244}
assert sum(widths) == 3794
owners = read(args.owners)
assert len(owners) == 72 * 492
order = [tuple(x) for x in plan['order']]
times = {x: i for i, x in enumerate(order)}
used, call_helpers, call_families = defaultdict(set), defaultdict(set), defaultdict(set)
for z in owners:
    key = (z['stage'], z['replica'])
    h, i, rep, port = z['helper'], z['child'], z['owner_replica'], z['port']
    assert key in times and 0 <= h < 492 and 0 <= rep < 8 and 0 <= port < 112
    assert z['time'] == times[key] and h not in call_helpers[key]
    assert z['family'] not in call_families[key]
    call_helpers[key].add(h)
    call_families[key].add(z['family'])
    cap, allowed = plan['windows'][f'{rep},{i}']
    assert z['time'] in allowed and z['width'] == widths[h]
    assert z['copy'] == rep * 112 + port
    assert z['family'] == rep * 896 + (2*plan['pairs'][str(i)] + plan['sides'][str(i)])*112 + port
    assert 0 <= z['offset'] and z['offset'] + z['width'] <= cap
    cells = set(range(z['offset'], z['offset'] + z['width']))
    group = (i, rep, port)
    assert not used[group] & cells
    used[group].update(cells)
assert set(call_helpers) == set(order)
assert all(hs == set(range(492)) for hs in call_helpers.values())
idle = Counter()
for key, (cap, _) in plan['windows'].items():
    rep, i = map(int, key.split(','))
    for port in range(112):
        cells = used[i, rep, port]
        assert cells == set(range(len(cells)))
        left = cap - len(cells)
        if left:
            idle[left] += 1
global_profile = Counter({r: 72*n for r, n in profile.items()}) + idle
assert sum(r*n for r, n in global_profile.items()) == 520704
assert 73*7168 - sum(r*n for r, n in global_profile.items()) == 2560
pid = 'gauge44'
for c in plan['provider_calls']:
    c['provider'] = pid
    c['local_program_sha256'] = checks[c['orientation']]['sha256']
for c in plan['per_call_widths']:
    c['widths'] = widths
artifacts = {name: sha(args.local / name) for name in FILES}
identities = artifact_identities(args.local)
plan['provider_registry'] = {pid: dict(
    directory='providers/' + pid, artifact_sha256=artifacts,
    ports=word['ports'], centers=word['centers'], widths=widths,
    actual_paid_profile=word['local_profile'],
    orientation_program_sha256={k: v['sha256'] for k, v in checks.items()},
    artifact_semantic_sha256=identities)}
plan.update(status='FROZEN_EXPLICIT_GAUGE44_WHOLE_OWNER_NOMINATION',
            mode='gauge44-all72', profile=dict(sorted(global_profile.items())),
            solver_status='deterministic-capacity-matching', gap=None,
            source_plan_sha256=sha(parent_path),
            source_owners_sha256=sha(args.parent / 'data/OWNERS.json.gz'),
            assignment_sha256=sha(args.owners))
target_owners = args.data / 'OWNERS.json.gz'
if args.owners.resolve() != target_owners.resolve():
    shutil.copyfile(args.owners, target_owners)
dump(args.data / 'PLAN.json', plan)
spec = dict(schema='witness-spec/1', name='gauge44-all72',
            data=dict(plan_sha256=sha(args.data / 'PLAN.json'), owners_sha256=sha(target_owners)),
            dispatch=[[s, r, pid] for s in range(9) for r in range(8)],
            call_order=plan['order'], width_spot_helpers=[264, 276, 288, 300],
            providers={pid: {}}, expected=dict(gain_baseline_kappa='0.001636241501576388'))
dump(args.data / 'SPEC.json', spec)
dump(args.data / 'PREPARATION.json', dict(
    status='PASS_EXPLICIT_MAP_AND_FRESH_PROVIDER_NOMINATION',
    parent_plan_sha256=sha(parent_path), source_owners_sha256=sha(args.owners),
    global_profile=dict(sorted(global_profile.items())), idle_profile=dict(sorted(idle.items())),
    roles=len(owners), rank_mass=520704, deficit=2560,
    remaining='Independent emitted-controller audit, fresh finite invoice, exact moments and outer assembly.'))
print('Prepared all72 gauge44 candidate:', dict(sorted(global_profile.items())))
