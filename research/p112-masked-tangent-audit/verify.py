#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact full-Jacobian certificate for the P112 masked decoder component.

Python 3.10+, standard library only. No predecessor code is imported.
A modular nonzero minor proves a characteristic-zero rank LOWER bound;
explicit integer kernel vectors independently supply its UPPER bound.
"""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIME = 101


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def model():
    lines = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            lines.add(tuple(row))
    for tail in itertools.product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            lines.add((1,) + tail)
    frame = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.append(tuple(row))
    require(len(lines) == 120 and set(frame) <= lines, 'root/frame census')
    roots = sorted(lines - set(frame))
    require(all(dot(r, f) % 4 == 0 for r in roots for f in frame), 'integer coordinates')
    y = [tuple(dot(r, f) // 4 for f in frame) for r in roots]
    gram = [[dot(a, b) for b in y] for a in y]
    require(len(y) == 112 and len(set(y)) == 112, 'live census')
    require(all(gram[i][i] == 4 for i in range(112)), 'diagonal normalization')
    require({gram[i][j] for i in range(112) for j in range(112) if i != j} == {-2, 0, 2}, 'off-diagonal values')
    require(all(sum(r[a] * r[b] for r in y) == 56 * (a == b)
                for a in range(8) for b in range(8)), 'left inverse Y^T/56')
    require(all(2 * gram[i][j] == dot(roots[i], roots[j])
                for i in range(112) for j in range(112)), 'K = 2 true-root Gram')
    return roots, frame, y, gram


def jacobian(y, gram):
    """Variables are all U entries, then all V entries; equations are ordered."""
    n = len(y)
    rows, pairs = [], []
    for i in range(n):
        for j in range(n):
            if i != j and gram[i][j] != 0:
                continue
            row = {8 * i + k: v for k, v in enumerate(y[j]) if v}
            row.update({8 * n + 8 * j + k: v for k, v in enumerate(y[i]) if v})
            rows.append(row)
            pairs.append([i, j])
    return rows, pairs


def rank_mod(rows, prime=PRIME):
    """Sparse ordinary Gaussian elimination; return original row/column pivots."""
    basis, pivots = {}, []
    for index, original in enumerate(rows):
        row = {k: v % prime for k, v in original.items() if v % prime}
        while row:
            col = min(row)
            value = row[col]
            if col not in basis:
                inv = pow(value, -1, prime)
                basis[col] = {k: v * inv % prime for k, v in row.items()}
                pivots.append([index, col])
                break
            for k, v in basis[col].items():
                entry = (row.get(k, 0) - value * v) % prime
                if entry:
                    row[k] = entry
                elif k in row:
                    del row[k]
    return pivots


def orbit_generators(y):
    n = len(y)
    generators = []
    for a in range(8):
        for b in range(8):
            # H=E_ab: U=YH, V=-YH^T.
            g = {8 * i + b: r[a] for i, r in enumerate(y) if r[a]}
            g.update({8 * n + 8 * i + a: -r[b] for i, r in enumerate(y) if r[b]})
            generators.append(g)
    for i, r in enumerate(y):
        g = {8 * i + k: v for k, v in enumerate(r) if v}
        g.update({8 * n + 8 * i + k: -v for k, v in enumerate(r) if v})
        generators.append(g)
    return generators


def residuals(rows, vector):
    return [sum(v * vector.get(k, 0) for k, v in row.items()) for row in rows]


def f2rank(rows):
    basis = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit not in basis:
                basis[bit] = row
                break
            row ^= basis[bit]
    return len(basis)


def costs(d, t, gram):
    values = []
    for k in range(8):
        cols = [j for j in range(112) if t[j][k]]
        rows = [sum(((gram[i][j] // 2 + 1) % 2) << j for j in cols)
                for i in range(112) if d[i][k]]
        values.append(f2rank(rows))
    return values


def source_check():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    require(set(manifest['local_files']) == {
        'research/complex-frame-pair-decoders/PROOF.md',
        'research/complex-decoder-field-extension-seed44/PROOF.md',
    }, 'source inventory changed')
    for name, digest in manifest['local_files'].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                'source bytes changed: ' + name)
    return manifest['local_files']


def calculate():
    sources = source_check()
    roots, frame, y, gram = model()
    rows, pairs = jacobian(y, gram)
    require(len(rows) == 6720, 'complete directed mask census')
    pivots = rank_mod(rows)
    require(len(pivots) == 1617, 'Jacobian lower rank')
    generators = orbit_generators(y)
    require(len(generators) == 176, 'orbit generator count')
    require(all(not any(residuals(rows, g)) for g in generators), 'integer kernel identities')
    kernel_pivots = rank_mod(generators)
    require(len(kernel_pivots) == 175, 'kernel lower dimension')
    require(len(pivots) + len(kernel_pivots) == 1792, 'exact characteristic-zero rank sandwich')
    # The selected columns/rows themselves form a nonzero 1617-square minor.
    columns = {c for _, c in pivots}
    minor = [{c: v for c, v in rows[r].items() if c in columns} for r, _ in pivots]
    require(len(rank_mod(minor)) == 1617, 'explicit nonzero modular minor')
    adjacency = [[j for j in range(112) if i != j and gram[i][j]] for i in range(112)]
    tree, seen, queue = [], {0}, [0]
    for i in queue:
        for j in adjacency[i]:
            if j not in seen:
                seen.add(j)
                queue.append(j)
                tree.append([i, j])
    require(len(seen) == 112 and all(len(a) == 52 for a in adjacency), 'connected odd graph')
    # A rational path in the orbit changes odd entries, leaving every mask entry fixed.
    scales = [Fraction(2)] + [Fraction(1)] * 111
    d = [[scales[i] * v for v in r] for i, r in enumerate(y)]
    t = [[v / scales[i] for v in r] for i, r in enumerate(y)]
    product = [[dot(a, b) for b in t] for a in d]
    require(all(product[i][j] == gram[i][j] for i, j in pairs), 'row-scaled positive fixture')
    require(any(product[i][j] != gram[i][j] for i in range(112) for j in range(112)), 'not all-pairs control')
    for factor in (d, t):
        # Multiply by 2 to clear the only possible denominator.
        combined = [{k: y[i][k] for k in range(8)} |
                    {8 + k: int(2 * factor[i][k]) for k in range(8)} for i in range(112)]
        require(len(rank_mod(combined)) == 9, 'both factors leave root code')
    require(costs(y, y, gram) == costs(d, t, gram) == [8] * 8, 'support-preserving COPY costs')
    # Reconstruct normalized row scales from the product and the stored odd tree.
    recovered = {0: Fraction(1)}
    for i, j in tree:
        recovered[j] = recovered[i] * gram[i][j] / product[i][j]
    require(all(recovered[i] == scales[i] / scales[0] for i in range(112)), 'tree scale recovery')
    # Basis changes can alter supports, so do not equate gauge with support preservation.
    gd = [list(r) for r in y]
    gt = [list(r) for r in y]
    for i in range(112):
        gd[i][1] += y[i][0]
        gt[i][0] -= y[i][1]
    require(all(dot(gd[i], gt[j]) == gram[i][j] for i in range(112) for j in range(112)), 'all-pairs shear fixture')
    require(any(bool(gd[i][k]) != bool(y[i][k]) for i in range(112) for k in range(8)), 'basis change alters supports')
    # Meaningful semantic failures, without relying on Python assertions.
    single = {k: v for k, v in enumerate(y[0]) if v}  # U_0=Y_0, V=0
    errors = residuals(rows, single)
    require(errors[pairs.index([0, 0])] == 4, 'diagonal mutation detected')
    require(all(not e for e, (i, j) in zip(errors, pairs) if i != j), 'diagonals are essential')
    wrong_gauge = dict(generators[0])
    for k in list(wrong_gauge):
        if k >= 896:
            wrong_gauge[k] *= -1
    require(any(residuals(rows, wrong_gauge)), 'wrong inverse-transpose sign rejected')
    require(dot(d[0], d[0]) != gram[0][0], 'nonreciprocal scaling rejected')
    require(any(dot(gd[i], y[j]) != gram[i][j] for i, j in pairs), 'unpaired basis shear rejected')
    # Exact Gaussian-integer phase distinguishes transpose from conjugate transpose.
    phase_d = [[(0, v) if i == 0 else (v, 0) for v in r] for i, r in enumerate(y)]
    phase_t = [[(0, -v) if i == 0 else (v, 0) for v in r] for i, r in enumerate(y)]
    def gaussian_dot(a, b):
        return (sum(ar * br - ai * bi for (ar, ai), (br, bi) in zip(a, b)),
                sum(ar * bi + ai * br for (ar, ai), (br, bi) in zip(a, b)))
    require(all(gaussian_dot(phase_d[i], phase_t[j]) == (gram[i][j], 0)
                for i, j in pairs), 'complex bilinear phase fixture')
    conjugated = [(re, -im) for re, im in phase_t[0]]
    require(gaussian_dot(phase_d[0], conjugated) == (-4, 0), 'conjugate transpose rejected')
    # A 112-term completion shows the eight-term scope cannot be dropped.
    i, j = 0, adjacency[0][0]
    changed = [row[:] for row in gram]
    changed[i][j] += 1
    require(all(changed[a][b] == gram[a][b] for a, b in pairs), 'overcomplete mask fixture')
    require(changed[i][j] * changed[j][i] != 4, 'overcomplete fixture outside orbit')
    require(len(rank_mod([dict(enumerate(r)) for r in changed])) == 9, 'overcomplete product rank nine')
    return {
        'schema': 'p112-masked-component-v1',
        'roots_doubled': roots, 'frame_doubled': frame,
        'coordinates_sha256': hashlib.sha256(json.dumps(y, separators=(',', ':')).encode()).hexdigest(),
        'mask_equations': len(rows), 'variables': 1792,
        'prime': PRIME, 'jacobian_rank': len(pivots), 'jacobian_minor_pivots': pivots,
        'orbit_generators': len(generators), 'kernel_rank': len(kernel_pivots),
        'kernel_pivots': kernel_pivots, 'odd_edges': sum(map(len, adjacency)) // 2,
        'odd_spanning_tree': tree, 'coordinate_term_costs': costs(y, y, gram),
        'shear_term_costs': costs(gd, gt, gram),
        'controls': ['non_all_pairs_orbit', 'both_factors_outside_root_code',
                     'diagonal_essential', 'wrong_gauge_sign', 'nonreciprocal_scaling',
                     'unpaired_shear', 'basis_changes_support', 'rank_nine_mask_completion',
                     'conjugate_transpose'],
        'sources': sources,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate deterministic CERTIFICATE.json')
    args = parser.parse_args()
    result = calculate()
    payload = json.dumps(result, indent=2) + '\n'
    path = HERE / 'CERTIFICATE.json'
    if args.write:
        path.write_text(payload)
    else:
        require(path.read_text() == payload, 'certificate differs from exact recomputation')
    print('PASS_P112_MASKED_COMPONENT rank=1617 nullity=175 mask=6720 odd_edges=2912 controls=9')


if __name__ == '__main__':
    main()
