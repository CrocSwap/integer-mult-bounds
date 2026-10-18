#!/usr/bin/env python3
"""Independent finite witness check; no predecessor verifier imports.
Yiyang with substantial OpenAI Codex assistance, Apache-2.0.
Separate AI implementation, not independent human review or a native replay.
"""
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent
PINS = {
    'b': '426bffd3ea874fd3f97ebcf731c43f1f576e8fba1dec8665294d7c1926df0389',
    'e': '735051e082013ded857ab03aa4dee1ee4eabc3aeced2cc7490dcc88aba96cad8',
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def span(vectors):
    result = {0}
    for v in vectors:
        need(isinstance(v, int) and 0 <= v < 512, 'invalid vector')
        if v not in result:
            result |= {x ^ v for x in result}
    return frozenset(result)


def join_sets(*spaces):
    return span(x for space in spaces for x in space)


def review(w):
    cut, host = 1202, 277
    need(all(rec[0] < cut for rec in w['warps']), 'post-cut warp')
    derivative = {100: Fraction(1)}
    support = {100}
    changes = []
    for section, seq, start in [('B', w['B'][cut:], cut), ('restore', w['restore'], 0)]:
        for i, g in enumerate(seq, start):
            need(g[0] in ('add', 'scale'), 'unsupported tail event')
            touched = g[1:3] if g[0] == 'add' else [g[1]]
            need(host not in touched, 'host used in inherited tail')
            old = derivative.copy()
            if g[0] == 'add':
                derivative[g[1]] = derivative.get(g[1], 0) + Fraction(g[3], g[4]) * derivative.get(g[2], 0)
            else:
                derivative[g[1]] = Fraction(g[2], g[3]) * derivative.get(g[1], 0)
            derivative = {q: a for q, a in derivative.items() if a}
            if derivative != old:
                changes.append((section, i))
            support.update(derivative)
    need(changes == [('B', 1428), ('B', 1429), ('B', 1430)], 'derivative change locations')
    need(support == {100, 67, 112, 169}, 'derivative support')
    need(derivative == {100: Fraction(1), 67: Fraction(-1, 2), 112: Fraction(-1, 2), 169: Fraction(-1, 2)}, 'final derivative')
    for section in ('A', 'B', 'precondition', 'compensation', 'cut', 'restore'):
        for g in w[section]:
            if g[0] == 'add':
                need(g[1] != g[2] and g[4] != 0, 'noninvertible ordinary shear')
            elif g[0] == 'scale':
                need(g[2] != 0 and g[3] != 0, 'noninvertible ordinary scale')
    need(all(112 <= g[1] < 224 and not 112 <= g[2] < 224 for g in w['cut']), 'centre cut not target shear')
    for rec in w['warps']:
        need(len(span(rec[2])) == 512, 'singular binary warp matrix')

    # Register-version inclusion graph. No predecessor lattice code is imported.
    v = w['report']['v']
    n = 2 * v + w['report']['R']
    empty = frozenset({0})
    nodes, previous, equalities, capture = [], [], [], {}
    for q in range(n):
        initial = span([w['ports'][q]]) if q < v else empty
        if str(q) in w['start_extra']:
            initial = span(w['start_extra'][str(q)])
        previous.append(len(nodes))
        nodes.append([[], initial])

    def gate(g):
        touched = g[1:3] if g[0] == 'add' else [g[1]]
        idx = len(nodes)
        nodes.append([[previous[q] for q in touched], empty])
        for q in touched:
            previous[q] = idx

    def fix(q, vectors):
        idx = previous[q]
        fixed = span(vectors)
        nodes[idx][1] = join_sets(nodes[idx][1], fixed)
        equalities.append((idx, fixed))

    def warp(q, entry, exit_):
        fix(q, entry)
        previous[q] = len(nodes)
        nodes.append([[], span(exit_)])

    for g in w['A']:
        if g[0] == 'warp':
            warp(g[1], g[3], g[4])
        else:
            gate(g)
    for q in range(v, 2 * v):
        fix(q, w.get('target_levels', {}).get(str(q - v), []))
    for q, vectors in zip(w['centers'], w['center_frames']):
        fix(q, vectors)
    by_position = {}
    for rec in w['warps']:
        by_position.setdefault(rec[0], []).append(rec)
    for i in range(len(w['B']) + 1):
        for rec in by_position.get(i, []):
            warp(rec[1], rec[3], rec[4])
        if i < len(w['B']):
            gate(w['B'][i])
        if i == 1201:
            capture['H'] = previous[host]
        if i == 1429:
            capture['U100'] = previous[100]
        if i == 1430:
            capture['U67'] = previous[67]
    for g in w['restore']:
        gate(g)
    values = []
    for parents, fixed in nodes:
        values.append(join_sets(fixed, *(values[p] for p in parents)))
    need(all(values[idx] <= fixed for idx, fixed in equalities), 'infeasible baseline equality')
    H = values[capture['H']]
    need(len(H) == 128 and 33 in H, 'host floor witness')
    for key, source, target, at in [('U100', 100, 112, 1429), ('U67', 67, 169, 1430)]:
        g = w['B'][at]
        need(g[0] == 'add' and g[1:3] == [target, source] and g[3] != 0, 'missing future target read')
        need(len(join_sets(H, values[capture[key]])) == 512, 'late join not full rank')
        need((33 & w['ports'][target - v]).bit_count() % 2 == 1, 'missing endpoint violation')
    return len(nodes)


def main():
    counts = []
    for label, digest in PINS.items():
        raw = (BASE / 'inputs' / f'hosted-{label}-473-277.json.gz').read_bytes()
        need(hashlib.sha256(raw).hexdigest() == digest, 'input pin mismatch')
        counts.append(review(json.loads(gzip.decompress(raw))))
    print('PASS_INDEPENDENT_STAGED_WITNESSES providers=2 nodes=' + ','.join(map(str, counts)) + ' derivative_changes=B1428,B1429,B1430 H_dimension=7 late_join_dimensions=9,9')


if __name__ == '__main__':
    main()
