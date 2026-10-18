#!/usr/bin/env python3
"""Exact finite premises for README's quantified proof, not a theorem prover.

Hanson Sun / bbMisk, substantial OpenAI Codex assistance. Apache-2.0.
Geometry: Mihir Srivastava / PR845, following DreamingOfClouds / PR717.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import combinations, permutations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {'research/p112-single-lift/geometry.py',
          'research/complex-frame-pair-decoders/PROOF.md'}
PAIR = (2, 4)
STRATA = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))
ALL = (1 << 112) - 1


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(obj):
    data = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def check_sources(sources):
    rows = [r for r in sources['files'] if r['usage'] == 'input']
    need(len(rows) == len(INPUTS) and {r['path'] for r in rows} == INPUTS,
         'complete input inventory')
    for row in rows:
        need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
             == row['sha256'], 'source digest')


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return list(pivots.values())


def rank(rows):
    return len(basis(rows))


def indices(mask):
    return [i for i in range(112) if mask >> i & 1]


def support(values):
    return sum(bool(v) << i for i, v in enumerate(values))


def cost(pairing, left, right):
    return rank(pairing[i] & right for i in indices(left))


def canonical(row):
    return max(tuple(row), tuple(-v for v in row))


def model():
    spec = importlib.util.spec_from_file_location(
        'source_geometry', ROOT / 'research/p112-single-lift/geometry.py')
    geo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geo)
    data = geo.build()
    geo.check_geometry(data)
    order = sorted(range(112), key=lambda i: canonical(data['roots'][i]))
    roots, x, pairing = [], [], []
    for i in order:
        r = data['roots'][i]
        sign = 1 if tuple(r) == canonical(r) else -1
        roots.append(list(canonical(r)))
        x.append([sign * v for v in data['X'][i]])
        pairing.append(sum(((data['duals'][i] & data['labels'][j]).bit_count() % 2)
                           << k for k, j in enumerate(order)))
    check_geometry(roots, x, pairing)
    return roots, x, pairing


def check_geometry(roots, x, pairing):
    need(len(roots) == len(x) == len(pairing) == 112, 'geometry size')
    need(rank(pairing) == 9, 'ambient pairing rank nine')
    for i in range(112):
        need(set(x[i]) <= {-1, 0, 1}, 'coordinate alphabet')
        for j in range(112):
            gram4 = sum(a * b for a, b in zip(roots[i], roots[j]))
            need(gram4 % 4 == 0, 'integral Gram')
            need(sum(a * b for a, b in zip(x[i], x[j])) == gram4 // 2,
                 'coordinate Gram identity')
            need((pairing[i] >> j & 1) == (1 + gram4 // 4) % 2,
                 'pairing bound to Euclidean Gram')


def common_odd(pairing, subset):
    covered = 0
    for i in indices(subset):
        covered |= pairing[i]
    return ALL ^ covered


def strata(x, pair=PAIR):
    return [support(a * row[pair[0]] + b * row[pair[1]] for row in x)
            for a, b in STRATA]


def characters(pairing):
    values = [0]
    for b in basis(pairing):
        values += [v ^ b for v in values]
    return sorted(values)


def check_character_space(pairing, values):
    need(len(values) == len(set(values)) == 512 and 0 in values,
         'complete 512-character space')
    need(rank(values) == 9 and all(v in values for v in pairing),
         'character space equals full pairing row space')


def census(pairing, supports, values):
    check_character_space(pairing, values)
    records, hist = [], Counter()
    for i, s in enumerate(supports):
        for char in values:
            cut = s & char
            if not cut:
                continue
            neighbors = common_odd(pairing, cut)
            need(neighbors.bit_count() <= 1, 'cut has at most one common odd neighbor')
            records.append([i, format(char, 'x'), format(cut, 'x'),
                            format(neighbors, 'x')])
            hist[(i, cut.bit_count(), neighbors.bit_count())] += 1
    need(len(records) == 2553, 'complete nonempty cut inventory')
    base = [[cost(pairing, s, t) for t in supports] for s in supports]
    need(min(map(min, base)) == 8, 'baseline pairing floor eight')
    return {'records': records,
            'histogram': [list(k) + [v] for k, v in sorted(hist.items())],
            'nonempty_cuts': len(records), 'empty_cuts': 5 * 512 - len(records),
            'support_sizes': [s.bit_count() for s in supports],
            'support_spans': [rank(pairing[i] for i in indices(s)) for s in supports],
            'baseline_pairings': base}


def orbit_maps(x):
    lookup = {canonical(row): i for i, row in enumerate(x)}
    need(len(lookup) == 112, 'distinct coordinate root lines')
    maps = {}
    for perm in permutations(range(8)):
        target = tuple(sorted((perm[PAIR[0]], perm[PAIR[1]])))
        if target in maps:
            continue
        row_map, signs = [], []
        for row in x:
            moved = [0] * 8
            for k in range(8):
                moved[perm[k]] = row[k]
            j = lookup.get(canonical(moved))
            if j is None:
                break
            row_map.append(j)
            signs.append(1 if moved == x[j] else -1)
        if len(row_map) == 112:
            maps[target] = {'pair': list(target), 'permutation': list(perm),
                            'row_map': row_map, 'signs': signs}
        if len(maps) == 28:
            break
    return [maps[p] for p in sorted(maps)]


def check_maps(x, pairing, maps):
    need(len(maps) == 28 and {tuple(m['pair']) for m in maps}
         == set(combinations(range(8), 2)), 'complete 28-pair orbit')
    for m in maps:
        perm, rows, signs = m['permutation'], m['row_map'], m['signs']
        need(sorted(perm) == list(range(8)) and sorted(rows) == list(range(112)),
             'coordinate and root permutations')
        need(sorted([perm[PAIR[0]], perm[PAIR[1]]]) == m['pair'], 'pair image')
        for i in range(112):
            need(signs[i] in (-1, 1) and all(
                x[i][k] == signs[i] * x[rows[i]][perm[k]] for k in range(8)),
                'signed coordinate image')
            for j in range(112):
                need((pairing[i] >> j & 1) == (pairing[rows[i]] >> rows[j] & 1),
                     'binary pairing preserved by orbit map')


# Gaussian rationals. Complex coefficients are never reduced modulo two.
def q(a=0, b=0):
    return F(a), F(b)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def inv(a):
    norm = a[0] ** 2 + a[1] ** 2
    need(norm != 0, 'invertible scalar')
    return a[0] / norm, -a[1] / norm


def total(values):
    out = q()
    for value in values:
        out = add(out, value)
    return out


def inverse(m):
    a = [row[:] + [q(i == j) for j in range(3)] for i, row in enumerate(m)]
    for j in range(3):
        pivot = next((i for i in range(j, 3) if a[i][j] != q()), None)
        need(pivot is not None, 'invertible mixing matrix')
        a[pivot], a[j] = a[j], a[pivot]
        scale = inv(a[j][j])
        a[j] = [mul(v, scale) for v in a[j]]
        for i in range(3):
            if i != j:
                scale = a[i][j]
                a[i] = [add(v, neg(mul(scale, w))) for v, w in zip(a[i], a[j])]
    return [row[3:] for row in a]


def check_rectangle(pairing, u, v):
    su = support(z != q() for z in u)
    sv = support(z != q() for z in v)
    need(su.bit_count() >= 2 and sv.bit_count() >= 2, 'two indices on each side')
    need(cost(pairing, su, sv) == 0, 'free rectangle')
    return su, sv


def factors(x, u, v, m, wrong_transpose=False):
    mi = inverse(m)
    left = [[q(row[PAIR[0]]), q(row[PAIR[1]]), u[i]] for i, row in enumerate(x)]
    right = [[q(row[PAIR[0]]), q(row[PAIR[1]]), v[i]] for i, row in enumerate(x)]
    d = [[total(mul(row[k], m[k][j]) for k in range(3)) for j in range(3)]
         for row in left]
    t = [[total(mul(row[k], mi[k][j] if wrong_transpose else mi[j][k])
                for k in range(3)) for j in range(3)] for row in right]
    return d, t


def validate_identity(x, u, v, d, t, conjugate=False, constrained=False,
                      pairing=None):
    for i in range(112):
        for j in range(112):
            if constrained and not (pairing[i] >> j & 1):
                continue
            actual = total(mul(d[i][k], (t[j][k][0], -t[j][k][1])
                               if conjugate else t[j][k]) for k in range(3))
            expected = q(sum(x[i][k] * x[j][k] for k in PAIR))
            if not constrained:
                expected = add(expected, mul(u[i], v[j]))
            need(actual == expected, 'exact ordinary-transpose decoder identity')


def rejection(fn, fragment):
    try:
        fn()
    except ValueError as exc:
        need(fragment in str(exc), 'unexpected rejection: ' + str(exc))
        return fragment
    raise ValueError('negative control accepted: ' + fragment)


def fixtures(x, pairing):
    zero, one, imag = q(), q(1), q(0, 1)
    ident = [[q(i == j) for j in range(3)] for i in range(3)]
    shear = [[one, zero, zero], [zero, one, zero], [q(-1), zero, one]]
    dense = [[one, one, one], [zero, one, imag], [one, zero, one]]
    triangle = [[one, q(1, 1), zero], [zero, one, imag], [zero, zero, one]]
    v_mask = (1 << 42) | (1 << 43)
    u_mask = common_odd(pairing, v_mask)
    u = [q(x[i][PAIR[0]]) if u_mask >> i & 1 else zero for i in range(112)]
    varied = [q(1 + (i + 42) % 3, (-1, 1)[i % 2]) if u_mask >> i & 1 else zero
              for i in range(112)]
    v = [imag if i == 42 else one if i == 43 else zero for i in range(112)]
    wide_v_mask = common_odd(pairing, sum(1 << i for i in indices(u_mask)[:4]))
    narrow_u = [q(1, i % 2) if i in indices(u_mask)[:4] else zero for i in range(112)]
    wide_v = [q(1, -(i % 2)) if wide_v_mask >> i & 1 else zero for i in range(112)]
    maximal_pair = next((a, b) for a, b in combinations(range(112), 2)
                        if common_odd(pairing, (1 << a) | (1 << b)).bit_count() == 26)
    maximal_rows = common_odd(pairing, sum(1 << j for j in maximal_pair))
    maximal_u = [q(1, i % 2) if maximal_rows >> i & 1 else zero for i in range(112)]
    maximal_v = [one if i == maximal_pair[0] else imag if i == maximal_pair[1] else zero
                 for i in range(112)]
    cases = [('sharp identity with nonzero correction', varied, v, ident),
             ('coupled cancellation and compensation', u, v, shear),
             ('dense nonreal factor change', varied, v, dense),
             ('triangular complex factor change', varied, v, triangle),
             ('four-row wide rectangle', narrow_u, wide_v, dense),
             ('transposed rectangle', v, varied, dense),
             ('maximal 26-row free rectangle', maximal_u, maximal_v, dense)]
    result, controls = [], []
    for name, uu, vv, m in cases:
        su, sv = check_rectangle(pairing, uu, vv)
        d, t = factors(x, uu, vv, m)
        validate_identity(x, uu, vv, d, t)
        costs = [cost(pairing, support(row[k] != zero for row in d),
                      support(row[k] != zero for row in t)) for k in range(3)]
        need(sum(r >= 8 for r in costs) >= 2, 'two charged rank-eight terms')
        result.append({'name': name, 'rows': indices(su), 'columns': indices(sv),
                       'replacement_ranks': costs, 'whole_copy_cost': 48 + sum(costs),
                       'identity_entries': 112 * 112})
    need(result[0]['replacement_ranks'] == [8, 8, 0], 'sharp COPY64 fixture')
    d, t = factors(x, varied, v, dense)
    controls.append(rejection(lambda: validate_identity(x, varied, v, d, t, True),
                              'ordinary-transpose'))
    wd, wt = factors(x, varied, v, dense, True)
    controls.append(rejection(lambda: validate_identity(x, varied, v, wd, wt),
                              'ordinary-transpose'))
    d, t = factors(x, u, v, shear)
    for row in d:
        row[2] = zero
    controls.append(rejection(lambda: validate_identity(x, u, v, d, t,
                              constrained=True, pairing=pairing), 'ordinary-transpose'))
    controls.append(rejection(lambda: inverse([[one] * 3 for _ in range(3)]),
                              'invertible mixing matrix'))
    bad_v = v[:]
    witness = next(i for i, z in enumerate(varied) if z != zero)
    bad_v[witness] = one  # B_ii=1, so this is a constrained entry.
    controls.append(rejection(lambda: check_rectangle(pairing, varied, bad_v),
                              'free rectangle'))
    controls.append(rejection(lambda: check_rectangle(pairing, varied,
                              [one if i == 42 else zero for i in range(112)]),
                              'two indices on each side'))
    return result, controls


def run():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    check_sources(sources)
    roots, x, pairing = model()
    supports, values = strata(x), characters(pairing)
    finite = census(pairing, supports, values)
    maps = orbit_maps(x)
    check_maps(x, pairing, maps)
    examples, controls = fixtures(x, pairing)
    changed = deepcopy(sources)
    changed['files'] = [r for r in changed['files'] if r['path'] != sorted(INPUTS)[0]]
    controls.append(rejection(lambda: check_sources(changed), 'input inventory'))
    changed = deepcopy(sources)
    next(r for r in changed['files'] if r['usage'] == 'input')['sha256'] = '0' * 64
    controls.append(rejection(lambda: check_sources(changed), 'source digest'))
    controls.append(rejection(lambda: check_character_space(pairing, values[:-1]),
                              '512-character'))
    controls.append(rejection(lambda: check_maps(x, pairing, maps[:-1]), '28-pair'))
    bad_pairing = pairing[:]
    bad_pairing[0], bad_pairing[1] = bad_pairing[1], bad_pairing[0]
    controls.append(rejection(lambda: check_geometry(roots, x, bad_pairing),
                              'Euclidean Gram'))
    # Removing the second anchor breaks the span lemma, not necessarily the
    # COPY theorem: singleton cases need their own coupled-factor argument.
    boundary = supports[0] & (ALL ^ pairing[42])
    before = rank(pairing[i] for i in indices(supports[0]))
    after = rank(pairing[i] for i in indices(supports[0] & ~boundary))
    need((before, after) == (8, 7), 'singleton boundary really loses span')
    controls.append(rejection(lambda: need(after == before, 'singleton erasure preserves span'),
                              'singleton erasure'))
    return {'status': 'PASS_P112_MULTILINE_FREE_RECTANGLES_S42',
            'base_commit': sources['base_commit'], 'assignment_seed': 42,
            'representative_pair': list(PAIR), 'strata': [list(v) for v in STRATA],
            'geometry_sha256': digest({'roots': roots, 'X': x, 'B': pairing}),
            'character_space_sha256': digest([format(v, 'x') for v in values]),
            'character_census': finite, 'coordinate_orbit': maps,
            'fixtures': examples, 'negative_controls': controls,
            'singleton_scope_control': {'column': 42, 'deleted': indices(boundary),
                                        'before': before, 'after': after},
            'scope': 'Nonzero free rectangles with >=2 indices on each side; two original modes mixed by arbitrary GL(3,C); separate COPY objective only.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', type=Path)
    ap.add_argument('--check', type=Path, default=HERE / 'CERTIFICATE.json')
    args = ap.parse_args()
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads(args.check.read_text()), 'complete certificate mismatch')
    print(result['status'], 'cuts=2553 pairs=28 fixtures=7 entries=87808',
          'controls=' + str(len(result['negative_controls'])), 'copy_floor=64')


if __name__ == '__main__':
    main()
