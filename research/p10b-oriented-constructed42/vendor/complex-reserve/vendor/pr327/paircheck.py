#!/usr/bin/env python3
"""paircheck.py: standalone re-check of the compensated reuse pairs of a written aligned tree.

Reads only the written word (cache/{graph,frames,selection}.json, references/paired-cube/physical/{frames,pairs}.json)
and re-verifies the pairs independently of the code that chose them and of aligned_word.py:
  kinds:      the donor is an ungauged, non-root role with operations; the recipient is a selected (rank h-4) gauge;
              pairs are one-to-one and every selected gauge is paired (no live external gauge);
  chronology: early pair (deadline None): the donor's last operation in phase 1, the recipient's first after the cut;
              late pair: deadline = the recipient's first operation (phase 2), the donor's last operation strictly
              before it in the executed order (phase 1, then phase 2 in index order), i.e. the donor is dead before the
              recipient's old-value read;
  frames:     the donor's last physical frame lies inside the recipient's gauge frame;
  parity:     no pair is erasable by PR #184's --purify-source-donors (donor last frame of rank <= 3 inside a cube
              parity 3-space inside the recipient gauge).
Five mutation controls must each be rejected for the condition they break (every violated condition is listed):
a late recipient given an unused donor still alive at its read; an unused donor with legal timing whose last frame
lies outside the gauge (frame containment alone); a duplicated pair; an unpaired gauge; an unused donor with legal
timing whose last frame is parity-erasable (erasability alone).
Prepared by DreamingOfClouds with Anthropic Claude assistance (Apache-2.0); uses the rebuilt tree's
scripts/paired_cube/frames.py only for basis/perp/containment.
usage: paircheck.py --root PR202_TREE WORD_TREE [WORD_TREE ...]      (prints one JSON line per word tree)"""
import argparse
import json
import sys
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')


def check(tree, mutate=None):
    from paired_cube.frames import basis, perp, contained
    tree = Path(tree)
    rd = lambda p: json.loads((tree / p).read_text())
    g, w, word = rd('cache/graph.json'), rd('cache/frames.json'), rd('cache/selection.json')
    moved = rd('references/paired-cube/physical/frames.json')['frames']
    pairs = rd('references/paired-cube/physical/pairs.json')['pairs']
    h, v = g['h'], g['v']
    ops = word['ops']
    frames = [perp(tuple(w['annihilators'][x]), h) for _, _, x in ops]
    for i, F in moved:
        frames[i] = tuple(F)
    pset = set(word['phase1'])
    order = sorted(pset) + [i for i in range(len(ops)) if i not in pset]
    pos = {i: k for k, i in enumerate(order)}
    role_ops = {}
    for i in order:
        a, b, _ = ops[i]
        role_ops.setdefault(a, []).append(i)
        role_ops.setdefault(b, []).append(i)
    gauge = {z['role']: perp(tuple(z['annihilator']), h) for z in word['selected']}
    assert all(z['rank'] == h - 4 for z in word['selected']), 'non rank-(h-4) gauge kept'
    roots = set(word['rootroles'])
    parity = []
    for cube in range(v // 8):
        for bit in range(2):
            parity.append(basis(tuple(g['inputs'][8 * cube + j] for j in range(8) if j.bit_count() % 2 == bit)))
    erasable_pair = lambda U, V: len(U) <= 3 and any(contained(U, S) and contained(S, V) for S in parity)
    if mutate is not None:
        pairs = mutate([list(p) for p in pairs], dict(frames=frames, pos=pos, role_ops=role_ops, gauge=gauge, roots=roots,
                                                       pset=pset, contained=contained, erasable=erasable_pair))
    bad = []
    donors, recips = set(), set()
    late = early = erasable = 0
    for d, b, t in pairs:
        if d in donors or b in recips:
            bad.append(('not one-to-one', d, b))
        donors.add(d)
        recips.add(b)
        if d in gauge or d in roots or d not in role_ops:
            bad.append(('donor kind', d))
        if b not in gauge:
            bad.append(('recipient kind', b))
            continue
        last, first = role_ops[d][-1], role_ops[b][0]
        if t is None:
            early += 1
            if not (last in pset and first not in pset):
                bad.append(('early chronology', d, b))
        else:
            late += 1
            if not (t == first and t not in pset and pos[last] < pos[t]):
                bad.append(('late chronology', d, b, t))
        if not contained(frames[last], gauge[b]):
            bad.append(('donor frame outside gauge', d, b))
        if erasable_pair(frames[last], gauge[b]):
            erasable += 1
    unpaired = set(gauge) - recips
    if unpaired:
        bad.append(('live external gauges', len(unpaired)))
    return dict(pairs=len(pairs), early=early, late=late, gauges=len(gauge), erasable=erasable,
                violations=len(bad), kinds=sorted({x[0] for x in bad}), first_violations=bad[:5],
                status='PASS' if not bad and not erasable else 'FAIL')


def controls(tree):
    """five mutations; each must be rejected for the condition it breaks (all violated conditions are listed)"""
    def free_donors(pairs, c):
        used = {p[0] for p in pairs}
        return [(d, ops[-1]) for d, ops in sorted(c['role_ops'].items()) if d not in used and d not in c['gauge'] and d not in c['roots']]

    def legal_timing(last, b, t, c):
        first = c['role_ops'][b][0]
        return last in c['pset'] if t is None else (t == first and c['pos'][last] < c['pos'][t])

    def swap(pairs, c, *wants):
        # replace the donor of some pair by an unused donor chosen by the first satisfiable predicate
        # want(last frame, gauge, last op, recipient, deadline)
        free = free_donors(pairs, c)
        for want in wants:
            for k, (d, b, t) in enumerate(pairs):
                for d2, last in free:
                    if want(c['frames'][last], c['gauge'][b], last, b, t):
                        pairs[k] = [d2, b, t]
                        return pairs
        raise RuntimeError('no control instance')

    def late_before_death(pairs, c):
        # a late recipient gets an unused donor that is still alive at the recipient's read; a donor whose frame also
        # fits the gauge is preferred (none exists on the committed words, so the frame check fires as well)
        alive = lambda U, V, last, b, t: t is not None and c['pos'][last] > c['pos'][t]
        return swap(pairs, c, lambda U, V, last, b, t: alive(U, V, last, b, t) and c['contained'](U, V) and not c['erasable'](U, V),
                    alive)

    def frame_outside(pairs, c):
        # an unused donor with legal timing whose last frame is outside the recipient's gauge
        return swap(pairs, c, lambda U, V, last, b, t: legal_timing(last, b, t, c) and not c['contained'](U, V))

    def duplicate(pairs, c):
        pairs.append(list(pairs[0]))
        return pairs

    def drop(pairs, c):
        return pairs[1:]

    def erasable(pairs, c):
        # an unused donor with legal timing whose last frame (rank <= 3) lies in a cube parity 3-space inside the gauge
        return swap(pairs, c, lambda U, V, last, b, t: legal_timing(last, b, t, c) and c['erasable'](U, V))
    out = {}
    for name, f, intended in [('late_read_before_donor_death', late_before_death, 'late chronology'),
                              ('donor_frame_outside_gauge', frame_outside, 'donor frame outside gauge'),
                              ('duplicate_pair', duplicate, 'not one-to-one'), ('unpaired_gauge', drop, 'live external gauges'),
                              ('parity_erasable_donor', erasable, 'erasable')]:
        try:
            r = check(tree, f)
        except RuntimeError as e:
            out[name] = 'no instance: %s' % e
            continue
        found = r['kinds'] + (['erasable'] if r['erasable'] else [])
        out[name] = ('REJECTED (%s)' if intended in found else 'ACCEPTED (control failed: %s)') % ', '.join(found)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True, help='the rebuilt PR #202 tree (scripts/paired_cube/frames.py)')
    ap.add_argument('trees', type=Path, nargs='+')
    a = ap.parse_args()
    sys.path.insert(0, str(a.root / 'scripts'))
    for t in a.trees:
        print(json.dumps(dict(check(t), controls=controls(t))), flush=True)


if __name__ == '__main__':
    main()
