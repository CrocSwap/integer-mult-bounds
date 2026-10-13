#!/usr/bin/env python3
"""Independent structural check of the idle donor overlay (adapted from #1252's verify_overlay.py, Gonzalo-Mier).
CLI: --hosted-baseline H0 --hosted H1 --base B --owners O.json.gz --out RECEIPT.json
Checks, from the baseline emission and the overlay frames only (no builder code): every changed slot is a completely idle
rank-48 non-owner child; donors give disjoint axis triples, each receiver gets exactly one triple (rank 51); moved axes
commute with all stage X/Y translations, both children's terminal translations and the receiver's axes; every changed child's
axes stay an orthogonal independent set; the axis multiset of each (replica, port) group is unchanged (hence the exact
Z4 phase polynomial of the union); all other frames and template fields are unchanged; profile and guard."""
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
    changed = {}
    for d in ov['donors']:
        rep, port = d['replica'], d['port']; rec = recipes[port]
        ys = [int(s[k]) for s in rec['stage_alignment'] for k in ('entry_Y', 'exit_Y')] + [int(rec['terminal_Y_translation'])]
        xs = [int(s[k]) for s in rec['stage_alignment'] for k in ('entry_X', 'exit_X')]
        kd = (rep, port, d['donor_child']); a0 = old[kd]
        assert kd not in changed and kd not in roles
        assert a0['rank'] == 48 and a0['hosted'] == 0 and a0['pending_offset'] == 0
        dax = list(map(int, a0['orthogonal_axes'])); assert dax == d['old_axes_donor']
        gone = []
        for r in d['receivers']:
            kr = (rep, port, r['child']); b0 = old[kr]
            assert kr not in changed and kr not in roles and kr != kd
            assert b0['rank'] == 48 and b0['hosted'] == 0 and b0['pending_offset'] == 0
            rax = list(map(int, b0['orthogonal_axes'])); mv = list(map(int, r['moved_axes']))
            assert rax == r['old_axes'] and len(mv) == 3 and len(set(mv)) == 3 and all(v in dax for v in mv)
            assert not set(mv) & set(gone); gone += mv
            tr = [int(rec['idle_children'][c]['translation_after']) for c in (a0['child'], b0['child'])]
            assert all(dot(v, x) == 0 for v in mv for x in rax + ys + xs + tr)
            assert r['new_axes'] == rax + mv
            nb = new[kr]; assert nb['rank'] == 51 and list(map(int, nb['orthogonal_axes'])) == rax + mv and rank(rax + mv) == 51
            assert all(dot(x, y) == (i == j) for i, x in enumerate(rax + mv) for j, y in enumerate(rax + mv))
            changed[kr] = 51
        na = new[kd]; left = [v for v in dax if v not in gone]
        assert d['new_axes_donor'] == left and list(map(int, na['orthogonal_axes'])) == left and na['rank'] == 48 - len(gone) == rank(left)
        changed[kd] = na['rank']
    for k in old:
        if k in changed:
            o, n = dict(old[k]), dict(new[k]); o.pop('rank'); o.pop('orthogonal_axes'); n.pop('rank'); n.pop('orthogonal_axes'); assert o == n
        else:
            assert old[k] == new[k]
    grp0, grp1 = defaultdict(Counter), defaultdict(Counter)
    for k, r in old.items():
        if k in changed: grp0[k[:2]].update(map(int, r['orthogonal_axes']))
    for k in changed: grp1[k[:2]].update(map(int, new[k]['orthogonal_axes']))
    assert grp0 == grp1  # axis multiset per group unchanged
    c0, c1 = dict(t0), dict(t1); ch0, ch1 = c0.pop('idle_children'), c1.pop('idle_children')
    c0.pop('version'); c1.pop('version'); c1.pop('idle_axis_overlay'); assert c0 == c1
    o0 = {(x['replica'], x['port'], x['child']): x for x in ch0}; o1 = {(x['replica'], x['port'], x['child']): x for x in ch1}
    assert o0.keys() == o1.keys()
    for k in o0:
        x, y = dict(o0[k]), dict(o1[k])
        if k in changed: assert y['rank'] == changed[k]
        else: assert x == y
        x.pop('rank'); y.pop('rank'); assert x == y
    h0, h1 = read(H0 / 'HOSTED.json'), read(H1 / 'HOSTED.json')
    prof = Counter({int(k): v for k, v in h0['global_profile'].items()})
    prof.subtract(r['rank'] for r in f0); prof.update(r['rank'] for r in f1); prof = +prof
    assert {str(k): v for k, v in sorted(prof.items())} == ov['profile'] == h1['global_profile']
    assert sum(int(r) * n for r, n in ov['profile'].items()) == h0['rank_mass'] and 73 ** 2 > 2 * max(map(int, ov['profile'])) ** 2
    rec = dict(status='PASS_INDEPENDENT_IDLE_DONOR_OVERLAY', donors=len(ov['donors']), changed_children=len(changed), profile=ov['profile'],
               receivers=sum(len(d['receivers']) for d in ov['donors']))
    a.out.write_text(json.dumps(rec, indent=2) + '\n'); print(rec['status'], rec['donors'], rec['changed_children'])


if __name__ == '__main__':
    main()
