#!/usr/bin/env python3
"""Idle 48+48 -> 45+51 pair exchanges (#1252 method, Gonzalo-Mier) applied to an emitted hosted directory.

Selects disjoint pairs of completely idle rank-48 children inside each (replica, port) group whose three
moved axes commute with every stage X/Y translation and both children's terminal translations,
neither slot being an owner slot.  Writes a new hosted directory (template, frames, HOSTED.json,
IDLE-PAIR-OVERLAY.json) leaving the source hosted directory untouched.
CLI: --hosted H --base B --owners O.json.gz --out OUT
"""
import argparse, gzip, hashlib, json, shutil
from collections import Counter, defaultdict
from pathlib import Path


def read(p):
    p = Path(p); raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def dot(a, b):
    return (int(a) & int(b)).bit_count() & 1


def rank(vectors):
    pivots = {}
    for x in map(int, vectors):
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    return len(pivots)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def portable_gzip(raw):
    data = bytearray(gzip.compress(raw, mtime=0)); data[9] = 255
    return bytes(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--hosted', type=Path, required=True)
    ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--owners', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--moves', type=Path, required=True)
    a = ap.parse_args()
    hosted, out = a.hosted.resolve(), a.out.resolve()
    assert not out.exists()
    frame_path, template_path = hosted / 'IDLE-REMAINDER-FRAMES.json.gz', hosted / 'GLOBAL-TEMPLATE.json.gz'
    phases_path = a.base.resolve() / 'work/complex-nine-native/DATA-PHASES.json'
    template, phases = read(template_path), read(phases_path)
    if not frame_path.exists():  # literal export of the checked pending-child axes, byte-identical to the audit's export
        lit = [dict(z, orthogonal_axes=list(map(int, phases['recipes'][z['port']]['idle_children'][z['child']]['orthogonal_axes']))[z['pending_offset']:])
               for z in template['idle_children']]
        assert all(len(z['orthogonal_axes']) == z['rank'] for z in lit)
        frame_path.write_bytes(portable_gzip(canonical(lit)))
    frames = read(frame_path)
    owners = read(a.owners)
    hosted_summary = read(hosted / 'HOSTED.json')
    base_profile = {int(k): v for k, v in hosted_summary['global_profile'].items()}
    base_mass = hosted_summary['rank_mass']
    recipes = {x['port']: x for x in phases['recipes']}
    owner_slots = {(x['owner_replica'], x['port'], x['child']) for x in owners}
    grouped = defaultdict(list)
    for row in frames:
        if (row['rank'] == 48 and row['hosted'] == 0 and row['pending_offset'] == 0
                and (row['replica'], row['port'], row['child']) not in owner_slots):
            grouped[row['replica'], row['port']].append(row)
    # Axis reassignment among the idle rank-48 children of each (replica, port) group, supplied as frozen data
    # (SWAP-MOVES.json.gz, found by an external exact optimiser; NOTHING here trusts it: verify_idle_overlay.py
    # recomputes every legality condition from the final axis lists). Final axes of a child = original axes
    # minus one occurrence of each outgoing axis plus arrivals appended in move order.
    moves = read(a.moves)
    selected = []
    edits = {}
    for g in moves:
        if not g['moves']:
            continue                              # singles / unchanged groups
        replica, port = g['key']
        rows = grouped[replica, port]
        assert [r['child'] for r in rows] == g['children'], ('group order', replica, port)
        axes = [list(map(int, r['orthogonal_axes'])) for r in rows]
        outl = [list(x) for x in axes]
        arrive = [[] for _ in rows]
        for m in g['moves']:
            assert m['src'] != m['dst']
            outl[m['src']].remove(int(m['axis']))      # ValueError if the axis is not present
            arrive[m['dst']].append(int(m['axis']))
        final = [outl[i] + arrive[i] for i in range(len(rows))]
        assert [len(f) for f in final] == g['ranks'], ('ranks', replica, port)
        for i, r in enumerate(rows):
            if final[i] != axes[i]:
                edits[replica, port, r['child']] = (len(final[i]), final[i])
        selected.append(dict(replica=replica, port=port, children=g['children'], ranks=g['ranks'], moves=g['moves']))
    n = len(selected)
    new_frames = []
    for row in frames:
        o = dict(row)
        new = edits.get((row['replica'], row['port'], row['child']))
        if new:
            o['rank'], o['orthogonal_axes'] = new
        new_frames.append(o)
    profile = Counter(base_profile)
    for (rep, port, child), (r, _) in edits.items():
        profile[48] -= 1; profile[r] += 1
    profile = +profile
    assert sum(r * k for r, k in profile.items()) == base_mass
    assert 73 ** 2 > 2 * max(profile) ** 2
    overlay = dict(status='PASS_EMITTED_%d_IDLE_48_AXIS_REASSIGNMENTS' % n,
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path),
        source_phases_sha256=sha(phases_path),
        groups=selected, changed_children=len(edits), profile={str(k): v for k, v in sorted(profile.items())},
        scope='Replica-local residual pair repartitions; preserves each pair axis union.')
    shutil.copytree(hosted, out)
    overlay_path = out / 'IDLE-PAIR-OVERLAY.json'
    overlay_path.write_text(json.dumps(overlay, indent=2) + '\n')
    template['version'] += '+idle-48-axis-reassignments-v1'
    template['idle_axis_overlay'] = dict(schema='replica-local-idle-axes/1', path='IDLE-PAIR-OVERLAY.json',
        frame_path='IDLE-REMAINDER-FRAMES.json.gz', groups=n, changed_children=len(edits),
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path))
    for child in template['idle_children']:
        edit = edits.get((child['replica'], child['port'], child['child']))
        if edit:
            child['rank'] = edit[0]
    template_raw, frames_raw = canonical(template), canonical(new_frames)
    (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(portable_gzip(template_raw))
    (out / 'IDLE-REMAINDER-FRAMES.json.gz').write_bytes(portable_gzip(frames_raw))
    h = read(hosted / 'HOSTED.json')
    h.update(status='CANDIDATE_%d_IDLE_AXIS_REASSIGNMENTS' % n, template_sha256=hashlib.sha256(template_raw).hexdigest(),
        global_profile=overlay['profile'], rank_mass=sum(int(k) * v for k, v in overlay['profile'].items()),
        maxchild=max(profile), idle_remainder_frames_sha256=hashlib.sha256(frames_raw).hexdigest(),
        idle_pair_overlay_sha256=sha(overlay_path))
    (out / 'HOSTED.json').write_text(json.dumps(h, indent=2) + '\n')
    print('PASS_IDLE_OVERLAY groups=%d profile=%s' % (n, json.dumps(overlay['profile'])))


if __name__ == '__main__':
    main()
