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
    # Per replica/port group (<=4 completely idle rank-48 children): donors give disjoint triples of axes to
    # receivers (each receiver gets exactly one triple -> rank 51 = guard maximum). Value is convex in the number of
    # receivers served by one donor (strict-priced marginal gains per group at the #1218+pairs profile).
    # G[r]: strict-priced mass-compensated kappa weight of one idle child of rank r relative to rank 48 (selection heuristic only; any valid selection is audited)
    G = {int(k): v for k, v in {"36": -2.4520183911866953e-09, "39": -1.9171680322068257e-09, "42": -1.3276966099980976e-09, "45": -6.875123312271499e-10, "48": 0.0, "51": 7.318804853566615e-10}.items()}
    VALUE = {k: G[48 - 3 * k] + k * G[51] for k in (1, 2, 3)}
    from itertools import product
    selected = []  # one entry per donor: {replica,port,donor,receivers:[{child,moved_axes}],...}
    for (replica, port), rows in sorted(grouped.items()):
        recipe = recipes[port]
        ys = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_Y', 'exit_Y')] + [int(recipe['terminal_Y_translation'])]
        xs = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_X', 'exit_X')]
        m = len(rows)
        ax = [list(map(int, r['orthogonal_axes'])) for r in rows]
        mov = {}
        for i in range(m):
            for j in range(m):
                if i != j:
                    tr = [int(recipe['idle_children'][c]['translation_after']) for c in (rows[i]['child'], rows[j]['child'])]
                    mov[i, j] = [v for v in ax[i] if all(dot(v, x) == 0 for x in ax[j] + ys + xs + tr)]
        best = (0.0, None)
        # assignment[j] = donor index feeding receiver j, or -1
        for assign in product(range(-1, m), repeat=m):
            if any(assign[j] == j for j in range(m)):
                continue
            donors = set(d for d in assign if d >= 0)
            if any(assign[d] >= 0 for d in donors):
                continue  # a donor cannot also receive
            serve = {d: [j for j in range(m) if assign[j] == d] for d in donors}
            value = sum(VALUE[len(v)] for v in serve.values())
            if value <= best[0]:
                continue
            plan = {}
            ok = True
            for d, rs in serve.items():
                used_axes = set()
                for j in sorted(rs, key=lambda j: len(mov[d, j])):
                    pick = [v for v in mov[d, j] if v not in used_axes][:3]
                    if len(pick) < 3 or rank(ax[j] + pick) != 51:
                        ok = False; break
                    used_axes.update(pick); plan[d, j] = pick
                if not ok:
                    break
            if ok:
                best = (value, plan)
        if best[1]:
            plan = best[1]
            donors = sorted({d for d, j in plan})
            for d in donors:
                recv = [(j, plan[d, j]) for j in range(m) if (d, j) in plan]
                gone = {v for _, mv in recv for v in mv}
                selected.append(dict(replica=replica, port=port, donor_child=rows[d]['child'], donor_family=rows[d]['family'],
                    old_axes_donor=ax[d], new_axes_donor=[v for v in ax[d] if v not in gone],
                    receivers=[dict(child=rows[j]['child'], family=rows[j]['family'], old_axes=ax[j],
                                    moved_axes=mv, new_axes=ax[j] + mv) for j, mv in recv]))
    edits = {}
    for x in selected:
        r = 48 - 3 * len(x['receivers'])
        assert rank(x['new_axes_donor']) == r
        edits[x['replica'], x['port'], x['donor_child']] = (r, x['new_axes_donor'])
        for y in x['receivers']:
            edits[x['replica'], x['port'], y['child']] = (51, y['new_axes'])
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
    overlay = dict(status='PASS_EMITTED_%d_IDLE_48_DONOR_EXCHANGES' % n,
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path),
        source_phases_sha256=sha(phases_path),
        donors=selected, changed_children=len(edits), profile={str(k): v for k, v in sorted(profile.items())},
        scope='Replica-local residual pair repartitions; preserves each pair axis union.')
    shutil.copytree(hosted, out)
    overlay_path = out / 'IDLE-PAIR-OVERLAY.json'
    overlay_path.write_text(json.dumps(overlay, indent=2) + '\n')
    template['version'] += '+idle-48-donor-exchanges-v1'
    template['idle_axis_overlay'] = dict(schema='replica-local-idle-axes/1', path='IDLE-PAIR-OVERLAY.json',
        frame_path='IDLE-REMAINDER-FRAMES.json.gz', donors=n, changed_children=len(edits),
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path))
    for child in template['idle_children']:
        edit = edits.get((child['replica'], child['port'], child['child']))
        if edit:
            child['rank'] = edit[0]
    template_raw, frames_raw = canonical(template), canonical(new_frames)
    (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(portable_gzip(template_raw))
    (out / 'IDLE-REMAINDER-FRAMES.json.gz').write_bytes(portable_gzip(frames_raw))
    h = read(hosted / 'HOSTED.json')
    h.update(status='CANDIDATE_%d_IDLE_DONOR_EXCHANGES' % n, template_sha256=hashlib.sha256(template_raw).hexdigest(),
        global_profile=overlay['profile'], rank_mass=sum(int(k) * v for k, v in overlay['profile'].items()),
        maxchild=max(profile), idle_remainder_frames_sha256=hashlib.sha256(frames_raw).hexdigest(),
        idle_pair_overlay_sha256=sha(overlay_path))
    (out / 'HOSTED.json').write_text(json.dumps(h, indent=2) + '\n')
    print('PASS_IDLE_OVERLAY donors=%d profile=%s' % (n, json.dumps(overlay['profile'])))


if __name__ == '__main__':
    main()
