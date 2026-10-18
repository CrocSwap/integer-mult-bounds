#!/usr/bin/env python3
"""Independent structural check of STAR-MOVES.json.gz against the frozen #1094 replay.

Does not import analyze.py. For every move it re-derives, from the frozen idle
frames and DATA-PHASES recipes, the PR1252 commuting rule applied per axis:
a moved axis must be orthogonal (Z2 symplectic dot 0 as used by PR1252) to all
original leaf axes, every stage entry/exit X and Y, the terminal Y translation,
and the terminal translations of both centre and leaf. It then checks the
resulting axis sets, the group axis unions, the rank profile, the halving guard
and RESULT.json. Mutation controls must each be rejected.
"""
import argparse, tarfile, copy, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OWNER_MAP = ROOT / 'research/complex-t16-rare-pattern-exchanges/OWNERS.json.gz'


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


REPLAY_TAR = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBERS = ('hosted/IDLE-REMAINDER-FRAMES.json.gz', 'base/work/complex-nine-native/DATA-PHASES.json',
           'audit/OWNERS-AND-PROFILE.json')


def replay_inputs(root):
    """{member: raw bytes}; read from the committed selected replay unless a
    pre-extracted candidate/strict/global directory is given."""
    if root is not None:
        return {m: (Path(root) / m).read_bytes() for m in MEMBERS}
    with tarfile.open(REPLAY_TAR) as tar:
        return {m: tar.extractfile('candidate/strict/global/' + m).read() for m in MEMBERS}


def parse(name, raw):
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dot(a, b): return (a & b).bit_count() & 1


def gf2_rank(vs):
    piv = {}
    for x in vs:
        while x:
            b = x.bit_length() - 1
            if b in piv: x ^= piv[b]
            else: piv[b] = x; break
    return len(piv)


def check(moves, frames, recipes, roles, base_profile):
    old = {(r['replica'], r['port'], r['child']): r for r in frames}
    axes = {k: [int(v) for v in r['orthogonal_axes']] for k, r in old.items()}
    new = {k: list(v) for k, v in axes.items()}
    centres, leaves, moved_ids = set(), Counter(), set()
    for m in moves:
        rep, port = m['replica'], m['port']
        c, l = (rep, port, m['centre_child']), (rep, port, m['leaf_child'])
        assert c != l and c in old and l in old
        for k in (c, l):
            r = old[k]
            assert r['rank'] == 48 and r['hosted'] == 0 and r['pending_offset'] == 0
            assert k not in roles
        centres.add(c); leaves[l] += 1
        rec = recipes[port]
        fixed = ([int(s[q]) for s in rec['stage_alignment'] for q in ('entry_Y', 'exit_Y', 'entry_X', 'exit_X')]
                 + [int(rec['terminal_Y_translation'])]
                 + [int(rec['idle_children'][k[2]]['translation_after']) for k in (c, l)])
        mv = [int(v) for v in m['moved_axes']]
        assert 1 <= len(mv) <= 3
        for v in mv:
            assert v in axes[c] and (c, v) not in moved_ids
            moved_ids.add((c, v))
            assert all(dot(v, x) == 0 for x in axes[l] + fixed)
            new[c].remove(v); new[l].append(v)
    assert not (centres & set(leaves)) and max(leaves.values()) == 1  # disjoint stars
    groups = defaultdict(lambda: [Counter(), Counter()])
    for k in old:
        a = new[k]
        assert all(dot(x, y) == (i == j) for i, x in enumerate(a) for j, y in enumerate(a))
        assert gf2_rank(a) == len(a) and 1 <= len(a) <= 51
        groups[k[:2]][0].update(axes[k]); groups[k[:2]][1].update(a)
    assert all(u == v for u, v in groups.values())  # group axis multiset unchanged
    profile = Counter(base_profile)
    profile.subtract(len(axes[k]) for k in old); profile.update(len(new[k]) for k in old)
    profile = +profile
    assert 73 ** 2 > 2 * max(profile) ** 2
    return {str(r): n for r, n in sorted(profile.items())}, len(set(leaves)), len(centres)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--replay-root', type=Path,
                    help='Optional extracted candidate/strict/global of selected-replay.tar.gz')
    raw = replay_inputs(ap.parse_args().replay_root)
    result = json.loads((OUT / 'RESULT.json').read_text())
    overlay = read(OUT / 'STAR-MOVES.json.gz')
    for m in MEMBERS:
        assert result['inputs'][m] == hashlib.sha256(raw[m]).hexdigest(), m
    assert result['inputs'][str(OWNER_MAP.relative_to(ROOT))] == sha(OWNER_MAP)
    assert overlay['source_frames_sha256'] == result['inputs'][MEMBERS[0]]
    frames = parse(MEMBERS[0], raw[MEMBERS[0]])
    recipes = {x['port']: x for x in parse(MEMBERS[1], raw[MEMBERS[1]])['recipes']}
    roles = {(x['owner_replica'], x['port'], x['child']) for x in read(OWNER_MAP)}
    base = Counter({int(k): v for k, v in parse(MEMBERS[2], raw[MEMBERS[2]])['paid_profile'].items()})
    moves = overlay['moves']
    profile, n_leaves, n_centres = check(moves, frames, recipes, roles, base)
    assert profile == overlay['profile'] == result['profiles']['star_class_optimum']
    assert n_leaves == len(moves) == result['star_moves']

    # Mutation controls: each must be rejected.
    def first_noncommuting():
        m = moves[0]; rep, port = m['replica'], m['port']
        rows = {r['child']: r for r in frames if (r['replica'], r['port']) == (rep, port)}
        leaf = [int(v) for v in rows[m['leaf_child']]['orthogonal_axes']]
        for v in rows[m['centre_child']]['orthogonal_axes']:
            if any(dot(int(v), x) for x in leaf): return str(v)
    bad = first_noncommuting()
    controls = {}
    def mutate(name, fn):
        mm = copy.deepcopy(moves); fn(mm)
        try:
            check(mm, frames, recipes, roles, base)
        except (AssertionError, KeyError, ValueError):
            controls[name] = 'rejected'
        else:
            controls[name] = 'ACCEPTED'
    mutate('noncommuting_axis', lambda mm: mm[0]['moved_axes'].__setitem__(0, bad))
    by_centre = defaultdict(list)
    for i, m in enumerate(moves):
        by_centre[m['replica'], m['port'], m['centre_child']].append(i)
    i, j = next(v for v in by_centre.values() if len(v) >= 2)[:2]
    hosted_leaf = next((r['replica'], r['port'], r['child']) for r in frames if r['hosted'] > 0)
    mutate('axis_moved_twice', lambda mm: mm[j].__setitem__('moved_axes', list(mm[i]['moved_axes'])))
    mutate('leaf_reused', lambda mm: mm[j].__setitem__('leaf_child', mm[i]['leaf_child']))
    mutate('fourth_axis_rank52', lambda mm: (mm[i]['moved_axes'].append(mm[j]['moved_axes'].pop())))
    mutate('foreign_axis', lambda mm: mm[0]['moved_axes'].__setitem__(0, str(1 << 72 | 1)))
    mutate('hosted_leaf', lambda mm: mm[0].update(replica=hosted_leaf[0], port=hosted_leaf[1],
                                                  leaf_child=hosted_leaf[2]))
    mutate('centre_also_leaf', lambda mm: mm.append(dict(mm[i], centre_child=mm[i]['leaf_child'],
                                                         leaf_child=mm[i]['centre_child'])))
    assert all(v == 'rejected' for v in controls.values()), controls
    receipt = dict(status='PASS_INDEPENDENT_IDLE48_STAR_OVERLAY', moves=len(moves),
                   leaves=n_leaves, centres=n_centres, profile=profile, mutation_controls=controls,
                   checks=['per-axis PR1252 commuting rule', 'orthonormal resulting axis sets',
                           'group axis multisets unchanged', 'disjoint stars, leaves <= 51',
                           'no owner-map slots, no hosted/pending children', 'halving guard 73^2 > 2*51^2',
                           'profile equals RESULT.json star_class_optimum'],
                   not_checked=['serialized controller/owner audit', 'mixed-provider invoice',
                                'strict global assembly and its negative controls'])
    (OUT / 'STAR-AUDIT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 'moves=%d' % len(moves), 'controls=%d/%d rejected' % (
        sum(v == 'rejected' for v in controls.values()), len(controls)))


if __name__ == '__main__':
    main()
