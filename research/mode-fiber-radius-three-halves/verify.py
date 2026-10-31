#!/usr/bin/env python3
"""Exact checks for the radius-3/2 mode-preserving rounder. Standard library only.

Checks every finite fact Theorem D uses: the block structure of the PR4933 mode
matrix, that the supports with 0 and 1^8 form the [8,4,4] code H8, that the
column sums are divisible by 8, the rainbow and straight matchings with their
pair identities, and the 16-case balancing table. It then runs the rounder on
fixed exact inputs and checks rejection controls.
Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rounder  # noqa: E402

ROOT = HERE.parents[1]
SOURCE = 'research/coded-native-caller/NORMALIZERS.json'
SOURCE_SHA256 = 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'
WITNESS_SUPPORT = (0, 7, 20, 111)
need = rounder.need


def read(path, limit=1 << 20):
    need(path.is_file() and not path.is_symlink() and path.stat().st_size <= limit, 'bounded regular file: %s' % path)
    return path.read_bytes()


def load_rows(raw):
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'source hash')
    cols = json.loads(raw)['mode_columns']
    need(type(cols) is list and len(cols) == 8 and all(len(c) == 112 for c in cols), 'mode shape')
    rows = [tuple(c[i] for c in cols) for i in range(112)]
    need(all(type(v) is int and v in (-1, 0, 1) for r in rows for v in r), 'signed entries')
    return rows


def check_structure(rows):
    need(len(set(rows)) == 112 and all(sum(map(abs, r)) == 4 for r in rows), 'distinct rows of weight four')
    gram = [[sum(r[a] * r[b] for r in rows) for b in range(8)] for a in range(8)]
    need(gram == [[56 * (a == b) for b in range(8)] for a in range(8)], 'M^T M = 56 I')
    blocks = rounder.blocks_of(rows)
    words = {rounder.word(s) for s in blocks}
    code = {(0,) * 8}
    for w in words:
        code |= {tuple(a ^ b for a, b in zip(w, x)) for x in code}
    need(code == words | {(0,) * 8, (1,) * 8} and len(code) == 16, 'supports, 0 and 1^8 form H8')
    need(all(tuple(1 - x for x in w) in words for w in words), 'complement of a support is a support')
    colsum = [sum(r[j] for r in rows) for j in range(8)]
    need(all(v % 8 == 0 for v in colsum), 'column sums divisible by 8')
    return blocks, colsum


def check_pairs(rows, pairs, block):
    ix, p, sign, free = block
    need(sorted(x for a, b, _ in pairs for x in (a, b)) == sorted(ix), 'pairs partition the block')
    for a, b, j in pairs:
        if j == p:
            v = [x + y for x, y in zip(rows[a], rows[b])]
            need(v == [2 * sign * (k == p) for k in range(8)], 'antipodal pair sums to 2 sigma e_p')
        else:
            v = [x - y for x, y in zip(rows[a], rows[b])]
            need(v == [2 * rows[a][j] * (k == j) for k in range(8)], 'flip pair differs by 2 e_j')


def check_matchings(rows, blocks):
    for s, block in blocks.items():
        rb = rounder.rainbow(rows, block)
        check_pairs(rows, rb, block)
        need(sorted(j for _, _, j in rb) == list(s), 'rainbow uses each coordinate once')
        for j in s:
            st = rounder.straight(rows, block, j)
            check_pairs(rows, st, block)
            need(all(d == j for _, _, d in st), 'straight matching in one direction')


def balancing_table(rows, blocks):
    """For every parity word h in H8, the planned pair counts n_j have parity h_j and cover |u_j| <= 4."""
    table = []
    words = {rounder.word(s) for s in blocks} | {(0,) * 8, (1,) * 8}
    for h in sorted(words):
        pairs, toggled = rounder.plan(rows, blocks, h)
        n = [sum(1 for pr in pairs if pr[2] == j) for j in range(8)]
        need(all(n[j] % 2 == h[j] and n[j] >= (3 if h[j] else 4) for j in range(8)), 'balancing covers h')
        table.append({'h': ''.join(map(str, h)), 'toggled': len(toggled), 'pairs_per_coordinate': n})
    need(len(table) == 16, 'sixteen parity classes')
    return table


def fixtures(rows, count=150, seed=20261031):
    """Exact y with M^T y in L: integer + rational vector projected onto ker M^T (M^T M = 56 I)."""
    rng = random.Random(seed)
    out = [[Q(1, 2) if i in WITNESS_SUPPORT else Q(0) for i in range(112)]]
    for k in range(count - 1):
        den = (2, 2, 4, 6, 7, 12, 30)[k % 7]
        v = [Q(rng.randint(-6 * den, 6 * den), den) for _ in range(112)]
        if k % 3:
            keep = set(rng.sample(range(112), rng.randint(2, 24)))
            v = [x if i in keep else Q(0) for i, x in enumerate(v)]
        mt = [sum(rows[i][j] * v[i] for i in range(112)) for j in range(8)]
        out.append([rng.randint(-4, 4) + v[i] - sum(rows[i][j] * mt[j] for j in range(8)) / 56
                    for i in range(112)])
    return out


def check_rounder(rows, blocks, ys):
    worst, toggles = Q(0), {}
    for y in ys:
        z, err, toggled = rounder.round_three_halves(rows, y, blocks)
        need(all(type(v) is int for v in z), 'integer output')
        worst = max(worst, err)
        toggles[len(toggled)] = toggles.get(len(toggled), 0) + 1
    need(set(toggles) == {0, 1, 2}, 'fixtures exercise all three parity cases')
    return worst, toggles


def rejects(fn):
    try:
        fn()
    except (ValueError, StopIteration):
        return True
    return False


def controls(rows, blocks, ys):
    out = []
    bad = list(rows)
    first = next(j for j in range(8) if bad[5][j])
    bad[5] = tuple(-x if k == first else x for k, x in enumerate(bad[5]))
    out.append(('flipped matrix entry', rejects(lambda: check_structure(bad))))
    s = min(blocks)
    rb = rounder.rainbow(rows, blocks[s])
    (a, b, j), rest = rb[0], rb[1:]
    out.append(('mislabelled pair direction',
                rejects(lambda: check_pairs(rows, [(a, b, (j + 1) % 8)] + rest, blocks[s]))))
    keep = rounder.plan
    rounder.plan = lambda r, bl, h: keep(r, bl, (1,) * 8)          # never toggle a block
    try:
        out.append(('parity toggle skipped', any(rejects(lambda y=y: rounder.round_three_halves(rows, y, blocks))
                                                 for y in ys[:40])))
    finally:
        rounder.plan = keep
    keepv = rounder.vertex
    rounder.vertex = lambda r, w: (list(w), [i for i in range(len(w)) if w[i].denominator != 1])
    try:
        out.append(('vertex step skipped', any(rejects(lambda y=y: rounder.round_three_halves(rows, y, blocks))
                                               for y in ys[1:20])))
    finally:
        rounder.vertex = keepv
    off = [Q(1, 2) if i == 0 else Q(0) for i in range(112)]
    out.append(('mode vector outside L', rejects(lambda: rounder.round_three_halves(rows, off, blocks))))
    claimed = Q(7, 5)
    out.append(('claimed radius 7/5', any(rounder.round_three_halves(rows, y, blocks)[1] > claimed for y in ys)))
    out.append(('source hash', rejects(lambda: load_rows(read(ROOT / SOURCE) + b' '))))
    failed = [name for name, ok in out if not ok]
    need(not failed, 'controls failed open: %s' % failed)
    return [name for name, _ in out]


def main():
    rows = load_rows(read(ROOT / SOURCE))
    blocks, colsum = check_structure(rows)
    check_matchings(rows, blocks)
    table = balancing_table(rows, blocks)
    ys = fixtures(rows)
    worst, toggles = check_rounder(rows, blocks, ys)
    names = controls(rows, blocks, ys)
    print(json.dumps({
        'column_sums': colsum,
        'blocks': len(blocks),
        'balancing_cases': len(table),
        'min_pairs_even_coordinate': min(n for t in table for n, c in zip(t['pairs_per_coordinate'], t['h']) if c == '0'),
        'min_pairs_odd_coordinate': min(n for t in table for n, c in zip(t['pairs_per_coordinate'], t['h']) if c == '1'),
        'rounder_runs': len(ys),
        'parity_cases_seen': {str(k): v for k, v in sorted(toggles.items())},
        'worst_error': '%d/%d' % (worst.numerator, worst.denominator),
        'controls_rejected': names,
    }, indent=1))
    print('PASS_MODE_FIBER_RADIUS_THREE_HALVES')


if __name__ == '__main__':
    main()
