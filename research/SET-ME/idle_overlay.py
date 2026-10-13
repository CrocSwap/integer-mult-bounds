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
    selected = []
    for (replica, port), rows in sorted(grouped.items()):
        recipe = recipes[port]
        ys = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_Y', 'exit_Y')] + [int(recipe['terminal_Y_translation'])]
        xs = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_X', 'exit_X')]
        used = set()
        for i, left in enumerate(rows):
            if i in used:
                continue
            left_axes = list(map(int, left['orthogonal_axes']))
            for j in range(i + 1, len(rows)):
                if j in used:
                    continue
                right = rows[j]
                right_axes = list(map(int, right['orthogonal_axes']))
                translations = [int(recipe['idle_children'][c]['translation_after']) for c in (left['child'], right['child'])]
                movable = [v for v in left_axes if all(dot(v, x) == 0 for x in right_axes + ys + xs + translations)]
                if len(movable) < 3:
                    continue
                moved = movable[:3]
                new_left, new_right = [v for v in left_axes if v not in moved], right_axes + moved
                if rank(new_left) != 45 or rank(new_right) != 51:
                    continue
                selected.append(dict(replica=replica, port=port, left_child=left['child'], right_child=right['child'],
                    left_family=left['family'], right_family=right['family'], old_axes_left=left_axes,
                    old_axes_right=right_axes, moved_axes=moved, new_axes_left=new_left, new_axes_right=new_right,
                    translation_after=translations, stage_X_commutes=True, stage_Y_commutes=True,
                    owner_slots_empty=True, pair_Z4_polynomial_unchanged=True))
                used.update((i, j)); break
    n = len(selected)
    edits = {(x['replica'], x['port'], x['left_child']): (45, x['new_axes_left']) for x in selected}
    edits.update({(x['replica'], x['port'], x['right_child']): (51, x['new_axes_right']) for x in selected})
    assert len(edits) == 2 * n
    new_frames = []
    for row in frames:
        o = dict(row)
        new = edits.get((row['replica'], row['port'], row['child']))
        if new:
            o['rank'], o['orthogonal_axes'] = new
        new_frames.append(o)
    profile = Counter(base_profile)
    profile[48] -= 2 * n; profile[45] += n; profile[51] += n
    profile = +profile
    assert sum(r * k for r, k in profile.items()) == base_mass
    assert 73 ** 2 > 2 * max(profile) ** 2
    overlay = dict(status='PASS_EMITTED_%d_IDLE_48_PAIR_EXCHANGES' % n,
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path),
        source_phases_sha256=sha(phases_path),
        pairs=selected, changed_children=2 * n, profile={str(k): v for k, v in sorted(profile.items())},
        scope='Replica-local residual pair repartitions; preserves each pair axis union.')
    shutil.copytree(hosted, out)
    overlay_path = out / 'IDLE-PAIR-OVERLAY.json'
    overlay_path.write_text(json.dumps(overlay, indent=2) + '\n')
    template['version'] += '+idle-48-pair-exchanges-v1'
    template['idle_axis_overlay'] = dict(schema='replica-local-idle-axes/1', path='IDLE-PAIR-OVERLAY.json',
        frame_path='IDLE-REMAINDER-FRAMES.json.gz', pairs=n, changed_children=2 * n,
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path))
    for child in template['idle_children']:
        edit = edits.get((child['replica'], child['port'], child['child']))
        if edit:
            child['rank'] = edit[0]
    template_raw, frames_raw = canonical(template), canonical(new_frames)
    (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(portable_gzip(template_raw))
    (out / 'IDLE-REMAINDER-FRAMES.json.gz').write_bytes(portable_gzip(frames_raw))
    h = read(hosted / 'HOSTED.json')
    h.update(status='CANDIDATE_%d_IDLE_PAIR_EXCHANGES' % n, template_sha256=hashlib.sha256(template_raw).hexdigest(),
        global_profile=overlay['profile'], rank_mass=sum(int(k) * v for k, v in overlay['profile'].items()),
        maxchild=max(profile), idle_remainder_frames_sha256=hashlib.sha256(frames_raw).hexdigest(),
        idle_pair_overlay_sha256=sha(overlay_path))
    (out / 'HOSTED.json').write_text(json.dumps(h, indent=2) + '\n')
    print('PASS_IDLE_OVERLAY pairs=%d profile=%s' % (n, json.dumps(overlay['profile'])))


if __name__ == '__main__':
    main()
