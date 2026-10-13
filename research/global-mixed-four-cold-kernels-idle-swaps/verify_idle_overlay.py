#!/usr/bin/env python3
"""Independent structural check of the idle axis-reassignment overlay (legality conditions recomputed from the FINAL axis lists).
CLI: --hosted-baseline H0 --hosted H1 --base B --owners O.json.gz --out RECEIPT.json
For every (replica, port) group with a changed child (children: non-owner, unhosted, offset-0 rank-48 frames):
 (a) every moved axis v (src != dst) commutes (dot = 0) with each stage entry/exit X and Y translation, the terminal Y translation and the
     translation_after of both its source and destination child;
 (b) every child's final axes are an orthonormal set (dot(x_i, x_j) = [i == j]) of independent vectors, so rank = len;
 (c) final rank <= 51 (halving guard 73^2 > 2*51^2);
 (d) the group's axis multiset is unchanged and every child's final list = original list minus outgoing plus arrivals (claimed moves);
 no owner slot or hosted child is touched, every other frame, template field and the profile are unchanged."""
import argparse, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path


def read(p):
    p = Path(p); b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def dot(a, b): return (int(a) & int(b)).bit_count() & 1


def rank(vs):
    piv = {}
    for x in map(int, vs):
        while x:
            b = x.bit_length() - 1
            if b in piv: x ^= piv[b]
            else: piv[b] = x; break
    return len(piv)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_group(old_axes, new_axes, moves, recipe, children):
    """old_axes/new_axes: per-child axis lists in group order; moves: claimed [{axis,src,dst}]; recipe: DATA-PHASES port recipe."""
    n = len(old_axes); assert len(new_axes) == n == len(children)
    ys = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_Y', 'exit_Y')] + [int(recipe['terminal_Y_translation'])]
    xs = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_X', 'exit_X')]
    tr = [int(recipe['idle_children'][c]['translation_after']) for c in children]
    out = [list(map(int, x)) for x in old_axes]; arr = [[] for _ in range(n)]
    for m in moves:
        v, s, d = int(m['axis']), m['src'], m['dst']
        assert 0 <= s < n and 0 <= d < n and s != d, 'bad move indices'
        out[s].remove(v)                                   # axis must be present (not lost / not duplicated)
        arr[d].append(v)
        assert all(dot(v, x) == 0 for x in xs + ys), 'moved axis fails a stage translation'          # (a)
        assert dot(v, tr[s]) == 0 and dot(v, tr[d]) == 0, 'moved axis fails a child translation'      # (a)
    for i in range(n):
        assert list(map(int, new_axes[i])) == out[i] + arr[i], 'final list differs from claimed moves'   # (d)
        f = list(map(int, new_axes[i]))
        assert len(f) <= 51, 'rank above guard'                                                        # (c)
        assert all(dot(x, y) == (a == b) for a, x in enumerate(f) for b, y in enumerate(f)), 'final axes not orthonormal'   # (b)
        assert rank(f) == len(f), 'final axes dependent'
    assert Counter(v for x in old_axes for v in map(int, x)) == Counter(v for x in new_axes for v in map(int, x)), 'axis multiset changed'  # (d)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--hosted-baseline', type=Path, required=True)
    ap.add_argument('--hosted', type=Path, required=True); ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--owners', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    H0, H1 = a.hosted_baseline, a.hosted
    t0, t1 = read(H0 / 'GLOBAL-TEMPLATE.json.gz'), read(H1 / 'GLOBAL-TEMPLATE.json.gz')
    f0, f1 = read(H0 / 'IDLE-REMAINDER-FRAMES.json.gz'), read(H1 / 'IDLE-REMAINDER-FRAMES.json.gz')
    ov = read(H1 / 'IDLE-PAIR-OVERLAY.json')
    phases = read(a.base / 'work/complex-nine-native/DATA-PHASES.json'); recipes = {r['port']: r for r in phases['recipes']}
    roles = {(r['owner_replica'], r['port'], r['child']) for r in read(a.owners)}
    assert ov['source_template_sha256'] == sha(H0 / 'GLOBAL-TEMPLATE.json.gz') and ov['source_frames_sha256'] == sha(H0 / 'IDLE-REMAINDER-FRAMES.json.gz')
    assert ov['source_phases_sha256'] == sha(a.base / 'work/complex-nine-native/DATA-PHASES.json')
    old = {(r['replica'], r['port'], r['child']): r for r in f0}; new = {(r['replica'], r['port'], r['child']): r for r in f1}
    assert old.keys() == new.keys() and len(old) == len(f0)
    free = defaultdict(list)
    for r in f0:
        k = (r['replica'], r['port'], r['child'])
        if r['rank'] == 48 and r['hosted'] == 0 and r['pending_offset'] == 0 and k not in roles: free[r['replica'], r['port']].append(r['child'])
    seen = set(); changed = set(); nmoves = 0
    for g in ov['groups']:
        rep, port = g['key'] if 'key' in g else (g['replica'], g['port'])
        assert (rep, port) not in seen; seen.add((rep, port))
        kids = g['children']; assert kids == free[rep, port], 'group children are not exactly the free idle children'
        oa = [old[rep, port, c]['orthogonal_axes'] for c in kids]; na = [new[rep, port, c]['orthogonal_axes'] for c in kids]
        check_group(oa, na, g['moves'], recipes[port], kids)
        assert [new[rep, port, c]['rank'] for c in kids] == [len(x) for x in na] == g['ranks']
        nmoves += len(g['moves'])
        for c, x, y in zip(kids, oa, na):
            if list(map(int, x)) != list(map(int, y)): changed.add((rep, port, c))
    for label, fr in (('baseline', f0), ('overlay', f1)):        # X2 (#1312): pending axes of distinct idle children in one physical family are disjoint
        fam = defaultdict(Counter)
        for r in fr:
            fam[r['family']].update(map(int, r['orthogonal_axes']))
        assert all(max(c.values(), default=1) == 1 for c in fam.values()), ('X2 family axes not disjoint', label)
    for k in old:
        if k in changed:
            o, n = dict(old[k]), dict(new[k])
            for z in ('rank', 'orthogonal_axes'): o.pop(z); n.pop(z)
            assert o == n
        else:
            assert old[k] == new[k]
    c0, c1 = dict(t0), dict(t1); ch0, ch1 = c0.pop('idle_children'), c1.pop('idle_children')
    c0.pop('version'); c1.pop('version'); c1.pop('idle_axis_overlay'); assert c0 == c1
    o0 = {(x['replica'], x['port'], x['child']): x for x in ch0}; o1 = {(x['replica'], x['port'], x['child']): x for x in ch1}
    assert o0.keys() == o1.keys()
    for k in o0:
        x, y = dict(o0[k]), dict(o1[k])
        assert y['rank'] == new[k]['rank'] and (k in changed or x == y)
        x.pop('rank'); y.pop('rank'); assert x == y
    h0, h1 = read(H0 / 'HOSTED.json'), read(H1 / 'HOSTED.json')
    prof = Counter({int(k): v for k, v in h0['global_profile'].items()})
    prof.subtract(r['rank'] for r in f0); prof.update(r['rank'] for r in f1); prof = +prof
    assert {str(k): v for k, v in sorted(prof.items())} == ov['profile'] == h1['global_profile']
    assert sum(int(r) * n for r, n in ov['profile'].items()) == h0['rank_mass'] and 73 ** 2 > 2 * max(map(int, ov['profile'])) ** 2
    rec = dict(status='PASS_INDEPENDENT_IDLE_AXIS_REASSIGNMENT_OVERLAY', groups=len(ov['groups']), changed_children=len(changed), moved_axes=nmoves, profile=ov['profile'])
    a.out.write_text(json.dumps(rec, indent=2) + '\n'); print(rec['status'], rec['groups'], rec['changed_children'], nmoves)


if __name__ == '__main__':
    main()
