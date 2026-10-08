#!/usr/bin/env python3
"""Independent dense reference for rounded banded/Woodbury solves.

Construct cases whose true inverse norm attains 1/gap, rather than merely
having a small diagonal-dominance gap. Compare the producer's rounded
banded application to independent dense rational Gauss-Jordan inversion.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time


def norm(a):
    return max((sum(map(abs, row), Q(0)) for row in a), default=Q(0))


def multiply(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def inverse(a):
    n = len(a)
    rows = [row[:]+[Q(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        v = rows[j][j]
        rows[j] = [x/v for x in rows[j]]
        for i in range(n):
            if i != j:
                v = rows[i][j]
                rows[i] = [x-v*y for x, y in zip(rows[i], rows[j])]
    assert all(rows[i][:n] == [Q(i == j) for j in range(n)] for i in range(n))
    return [row[n:] for row in rows]


def matvec(a, x):
    return [sum((v*w for v, w in zip(row, x)), Q(0)) for row in a]


def check_schur(a, gap):
    """Full dense Schur updates, independently of the band iteration bounds."""
    n = len(a)
    s = [row[:] for row in a]
    initial = norm(a)
    lower_pivot = Q(2)
    rows_checked = 0
    for k in range(n):
        for i in range(k, n):
            current = abs(s[i][i])-sum((abs(s[i][j]) for j in range(k, n) if j != i), Q(0))
            assert current >= gap
            assert sum((abs(s[i][j]) for j in range(k, n)), Q(0)) <= initial
            rows_checked += 1
        pivot = s[k][k]
        assert abs(pivot) >= gap
        lower_pivot = min(lower_pivot, abs(pivot))
        for i in range(k+1, n):
            ratio = s[i][k]/pivot
            for j in range(k+1, n):
                s[i][j] -= ratio*s[k][j]
            s[i][k] = Q(0)
    return dict(full_schur_rows=rows_checked, minimum_pivot=str(lower_pivot))


def nearest_bounds(max_s=48):
    comparisons, ties = 0, 0
    for s in range(2, max_s+1):
        for t in range(s+1, 2*s):
            rho, theta = Q(t, s), Q(t-s, s)
            beta = [rho*j-(rho*j+Q(1, 2)).numerator//(rho*j+Q(1, 2)).denominator
                    for j in range(s)]
            for j, b in enumerate(beta):
                ties += b == -Q(1, 2)
                for delta in [-2*s-1, -s, -3, -2, -1, 1, 2, 3, s, 2*s+1]:
                    phi = (rho*delta+b)**2-beta[(j+delta) % s]**2
                    assert phi >= rho*rho*delta*delta-rho*abs(delta)
                    if abs(delta) == 1:
                        assert phi >= 1+2*theta+2*delta*b
                    comparisons += 1
    return dict(ground_sizes_through=max_s, exact_exponent_comparisons=comparisons,
                nearest_rounding_ties=ties, periodic_aliases_included=True)


def cases():
    gap, n = Q(1, 2**20), 24
    for name, w in [('cyclic_positive_laplacian', 3), ('cyclic_negative_laplacian', 1),
                    ('wrapped_positive_pairs', 1), ('signed_random', 2)]:
        h = [[Q(i == j) for j in range(n)] for i in range(n)]
        if name == 'wrapped_positive_pairs':
            pairs = [(0, n-1)]+[(i, i+1) for i in range(1, n-1, 2)]
            for i, j in pairs:
                h[i][j] = h[j][i] = 1-gap
        else:
            deltas = [-3, -1, 1, 3] if w == 3 else list(range(-w, 0))+list(range(1, w+1))
            rng = random.Random(109)
            for i in range(n):
                for delta in deltas:
                    sign = -1 if name == 'cyclic_negative_laplacian' else (
                        rng.choice([-1, 1]) if name == 'signed_random' else 1)
                    h[i][(i+delta) % n] = sign*(1-gap)/len(deltas)
        yield name, h, w, gap


def audit_case(name, h, w, gap, bits):
    from downstream_banded_inverse import prepare, apply
    n = len(h)
    actual_gap = min(abs(h[i][i])-sum((abs(h[i][j]) for j in range(n) if j != i), Q(0)) for i in range(n))
    assert actual_gap == gap
    dense = inverse(h)
    identity = multiply(h, dense)
    assert identity == [[Q(i == j) for j in range(n)] for i in range(n)]
    exact_norm = norm(dense)
    assert exact_norm <= 1/gap
    if name != 'signed_random':
        assert exact_norm == 1/gap
    tables, metadata = prepare(h, w, bits)
    a = [[value if abs(i-j) <= w else Q(0) for j, value in enumerate(row)]
         for i, row in enumerate(h)]
    assert multiply(tables['exact_low'], tables['exact_high']) == a
    schur = check_schur(a, gap)
    Ai = inverse(a)
    assert norm(Ai) <= 1/gap
    assert norm(inverse(tables['exact_low'])) <= 2/gap
    assert norm(inverse(tables['exact_high'])) <= (1+2*w/gap)/gap
    border = list(range(w))+list(range(n-w, n))
    selector = [[Q(i == j) for j in border] for i in range(n)]
    assert multiply(Ai, selector) == tables['exact_z']
    wrapped = multiply(selector, tables['v'])
    assert [[a[i][j]+wrapped[i][j] for j in range(n)] for i in range(n)] == h
    # Woodbury orientation checked directly against the independently dense inverse.
    correction = multiply(multiply(multiply(tables['exact_z'], tables['exact_ki']), tables['v']), Ai)
    woodbury = [[Ai[i][j]-correction[i][j] for j in range(n)] for i in range(n)]
    assert woodbury == dense
    probes = [[Q((-1)**i, 2) for i in range(n)], [Q(1, 2)]*n]
    probes += [[Q(i == j) for i in range(n)] for j in range(n)]
    maximum_error, maximum_residual, maximum_output = Q(0), Q(0), Q(0)
    for rhs in probes:
        expected = matvec(dense, rhs)
        got = apply(tables, rhs)
        error = max(map(abs, [x-y for x, y in zip(got, expected)]))
        residual = max(map(abs, [x-y for x, y in zip(matvec(h, got), rhs)]))
        assert error <= residual/gap
        assert error < Q(1, 2**32)
        # Deliberately loose bound covering factor reciprocals and large correction.
        assert error < Q(2**30*n**4, 2**bits*gap**4)
        maximum_error = max(maximum_error, error)
        maximum_residual = max(maximum_residual, residual)
        maximum_output = max(maximum_output, max(map(abs, got)))
    if name != 'signed_random':
        assert maximum_output >= Q(1, 3*gap)
    def outward(x, precision=128):
        scaled = x*2**precision
        return str(Q(-(-scaled.numerator//scaled.denominator), 2**precision))
    return dict(case=name, dimension=n, half_bandwidth=w, gap=str(gap),
                work_fractional_bits=bits, dense_exact_inverse_norm=str(exact_norm),
                worst_case_inverse_norm_attained=name != 'signed_random', probes=len(probes),
                all_factor_product_entries_checked=n*n, dense_Woodbury_identity=True,
                schur=schur, border_inverse_norm_upper=metadata['border_inverse_norm_upper'],
                maximum_rounded_error_upper=outward(maximum_error),
                maximum_rounded_residual_upper=outward(maximum_residual),
                maximum_output_magnitude_upper=outward(maximum_output))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bits', type=int, default=96)
    ap.add_argument('--skip-nearest', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    begin = time.monotonic()
    result = dict(nearest={} if args.skip_nearest else nearest_bounds(),
                  cases=[audit_case(name, h, w, gap, args.bits) for name, h, w, gap in cases()],
                  code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  producer_sha256=sha256(Path(__file__).with_name('downstream_banded_inverse.py').read_bytes()).hexdigest(),
                  wall_seconds=time.monotonic()-begin,
                  scope='Independent exact finite exponent/factorization/conditioning/rounding checks, separate from the full asymptotic tape proof')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
