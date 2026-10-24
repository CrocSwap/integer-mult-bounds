"""Delete the eight isolated coordinate ports from the PR514 local supplier.

Prepared for icekylinx with GPT-6 Astra assistance.  Apache-2.0.
This is an exact restriction of the attributed PR507/PR514 scalar construction;
helper identities, entrance gauges, kernel relations, and gate frames survive.
No hosting or global-exponent claim is made by this local transformation.
"""
from pathlib import Path
from collections import Counter
import copy, gzip, hashlib, json, sys


def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def dump(p, obj):
    raw = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    p.write_bytes(gzip.compress(raw, mtime=0) if p.suffix == '.gz' else raw)


src, out = map(Path, sys.argv[1:3])
out.mkdir(parents=True, exist_ok=False)
w = read(src / 'FULL-WORD.json.gz')
c = read(src / 'CANONICAL-WORD.json.gz')
old_v, new_v = 120, 112
R = w['report']['R']
axes = [i for i, row in enumerate(w['root_lines']) if sum(x != 0 for x in row) == 1]
assert axes == list(range(8))
assert w['centers'][8:] == axes
assert list(map(len, w['center_frames'])) == [8] * 8 + [1] * 8
assert len(w['ports']) == old_v and c['v'] == old_v and c['R'] == R


def restriction(old, removed, canonical=False):
    """Reject any purportedly deleted data register used by a body gate."""
    keep = [i for i in range(old_v) if i not in removed]
    rank = {s: i for i, s in enumerate(keep)}
    mp = dict(rank)
    mp.update({old_v + s: new_v + i for s, i in rank.items()})
    mp.update({2 * old_v + h: 2 * new_v + h for h in range(R)})
    deleted = set(removed) | {old_v + i for i in removed}
    z = copy.deepcopy(old)
    deleted_events = Counter()
    for seq in ['A', 'B', 'cleanup', 'precondition', 'cut'] + (['compensation'] if canonical else []):
        events = []
        for e in old[seq]:
            regs = [e[1]] + ([e[2]] if e[0] == 'add' else [])
            if deleted.intersection(regs):
                assert seq == 'cut' and e[0] == 'add'
                assert e[1] - old_v == e[2] and e[2] in removed
                assert e[3:5] == [1, 1]
                deleted_events[seq] += 1
                continue
            a = copy.deepcopy(e)
            a[1] = mp[a[1]]
            if a[0] == 'add':
                a[2] = mp[a[2]]
            events.append(a)
        z[seq] = events
    assert deleted_events == {'cut': 8}
    ci = [j for j, r in enumerate(old['centers']) if r not in deleted]
    assert len(ci) == 8
    z['centers'] = [mp[old['centers'][j]] for j in ci]
    z['center_frames'] = [old['center_frames'][j] for j in ci]
    z['ports'] = [old['ports'][s] for s in keep]
    z['target_levels'] = {str(rank[int(t)]): E for t, E in old.get('target_levels', {}).items() if int(t) not in removed}
    assert len(z['target_levels']) == len(old.get('target_levels', {}))
    if canonical:
        z['v'] = new_v
        z['start'] = [old['start'][r] for r in sorted(mp, key=mp.get)]
        z['final'] = [old['final'][r] for r in sorted(mp, key=mp.get)]
        z['local_profile'] = dict(Counter({int(r): n for r, n in old['local_profile'].items()}) - Counter({1: 8, 8: 16}))
    else:
        z['root_lines'] = [old['root_lines'][s] for s in keep]
        z['scatter'] = [[old['scatter'][s][j] for j in ci] for s in keep]
        z['start_extra'] = {str(mp[int(r)]): E for r, E in old.get('start_extra', {}).items()}
        H = Counter({int(r): n for r, n in old['report']['local_profile'].items()})
        H.subtract({1: 8, 8: 16})
        assert all(n > 0 for n in H.values())
        z['report'] = {
            'status': 'EXACT_PORT_RESTRICTION_PENDING_LOCAL_REPLAY',
            'h': 9, 'v': new_v, 'R': R, 'cst': 64,
            'm': 73, 'local_profile': dict(sorted(H.items())),
            'centre_ranks': [8] * 8,
            'entering_helpers': len(z['start_extra']),
            'entrance_rank': sum(len(E) for E in z['start_extra'].values()),
            'source_columns_exact': new_v,
            'borrowed_output_pairs': old['report']['borrowed_output_pairs'],
            'selection_sha256': old['report']['selection_sha256'],
            'inherited_helper_indices': True,
            'scalar_operations_A': len(z['A']), 'scalar_operations_B': len(z['B']),
        }
    return z, mp, sorted(removed), deleted_events


new_w, wm, _, we = restriction(w, set(axes))
tau = lambda x: x ^ (43 if (x & 43).bit_count() % 2 else 0)
assert {tau(p) for p in w['ports']} == set(c['ports'])
canonical_removed = {c['ports'].index(tau(w['ports'][i])) for i in axes}
new_c, cm, _, ce = restriction(c, canonical_removed, True)
assert {tau(p) for p in new_w['ports']} == set(new_c['ports'])
dump(out / 'FULL-WORD.json.gz', new_w)
dump(out / 'CANONICAL-WORD.json.gz', new_c)
port_mapping = {
    'old_to_new': {i: cm[i] for i in range(old_v) if i in cm},
    'new_to_old': sorted(i for i in range(old_v) if i in cm),
    'old_to_new_hamming': {i: wm[i] for i in range(old_v) if i in wm},
    'tau_hamming_axes_to_old_canonical': [c['ports'].index(tau(w['ports'][i])) for i in axes],
}
assert len(port_mapping['new_to_old']) == new_v
assert all(port_mapping['old_to_new'][old] == new for new, old in enumerate(port_mapping['new_to_old']))
(out / 'PORT-MAPPING.json').write_text(json.dumps(port_mapping, indent=2) + '\n')
receipt = {
    'status': 'PASS_EXACT_LOCAL_PORT_RESTRICTION',
    'source_files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (src / 'FULL-WORD.json.gz', src / 'CANONICAL-WORD.json.gz')},
    'removed_hamming_source_indices': axes,
    'removed_canonical_source_indices': sorted(canonical_removed),
    'full_register_map': wm, 'canonical_register_map': cm,
    'only_deleted_explicit_operations': dict(we),
    'preserved_helper_indices': list(range(R)),
    'before': {'v': old_v, 'R': R, 'cst': 72, 'local_profile': c['local_profile']},
    'after': {'v': new_v, 'R': R, 'cst': 64, 'local_profile': new_c['local_profile']},
    'saved_local_children': {1: 8, 8: 16},
    'scope': 'Exact restriction of all scalar body, compensation, cleanup, and frame labels. Global hosting and outer exponent require fresh certificates.',
}
dump(out / 'RESTRICTION.json', receipt)
print(json.dumps({k: receipt[k] for k in ['status', 'removed_canonical_source_indices', 'before', 'after']}, indent=2))
