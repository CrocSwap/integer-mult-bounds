#!/usr/bin/env python3
"""Independent dense and combinatorial audit of phase-cell inverses.

Producer rounded local/boundary operations are compared with independent
rational inverses and Schur construction. No floating threshold is used.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from review_banded_inverse import inverse, matvec, multiply, norm


def rounded(x, bits):
    z = x*2**bits
    k = abs(z.numerator)//z.denominator
    return Q(k if z >= 0 else -k, 2**bits)


def outward(x, bits=160):
    z = x*2**bits
    return str(Q(-(-z.numerator//z.denominator), 2**bits))


def toeplitz(g):
    return [[g[abs(i-j)] for j in range(len(g))] for i in range(len(g))]


def gs_audit():
    entries = 0
    for n in range(1, 13):
        for sign in (-1, 1):
            g = [Q(1)]+[Q(sign**j, 2**(4*j*j)) if j <= 2 else Q(0)
                        for j in range(1, n)]
            a = toeplitz(g)
            ai = inverse(a)
            x = [row[0] for row in ai]
            z = [Q(0)]+list(reversed(x[1:]))
            lx = [[x[i-j] if i >= j else Q(0) for j in range(n)] for i in range(n)]
            lz = [[z[i-j] if i >= j else Q(0) for j in range(n)] for i in range(n)]
            xx = multiply(lx, list(map(list, zip(*lx))))
            zz = multiply(lz, list(map(list, zip(*lz))))
            for i in range(n):
                for j in range(n):
                    assert (xx[i][j]-zz[i][j])/x[0] == ai[i][j]
                    # Independent shift-displacement form of the GS identity.
                    previous = ai[i-1][j-1] if i and j else Q(0)
                    assert ai[i][j]-previous == (x[i]*x[j]-z[i]*z[j])/x[0]
                    entries += 1
    return dict(sizes_through=12, signs=(-1, 1), exact_GS_entries=entries,
                exact_shift_displacement_entries=entries)


def cell_census(max_s=160):
    records = ties = cells_checked = boundary_edges = 0
    for s in range(6, max_s+1):
        for difference in range(1, s//6+1):
            d = s//(3*difference)
            theta = Q(difference, s)
            if not (d >= 2 and Q(1, 4*d) < theta < Q(1, 2*d-1)):
                continue
            remainder, phase, cells = s, 0, []
            phases = []
            previous = None
            for j in range(s):
                direct = (2*difference*j+s)//(2*s)
                beta = Q(difference*j, s)-direct
                assert direct == phase and beta == Q(remainder-s, 2*s)
                assert -Q(1, 2) <= beta < Q(1, 2)
                ties += beta == -Q(1, 2)
                if phase != previous:
                    cells.append([])
                    previous = phase
                cells[-1].append(j)
                phases.append(phase)
                records += 1
                remainder += 2*difference
                if remainder >= 2*s:
                    remainder -= 2*s
                    phase += 1
            assert phase == difference and remainder == s
            assert len(cells) == difference+1
            assert all(d-2 <= len(cell) <= 4*d+1 for cell in cells)
            full = {s//difference, -(-s//difference)}
            assert all(len(cell) in full for cell in cells[1:-1])
            assert len(cells[0]) == -(-s//(2*difference))
            assert len(cells[-1]) == s//(2*difference)
            cells_checked += len(cells)
            for w in (1, 2):
                if min(map(len, cells)) <= 2*w:
                    continue
                boundary = [j for cell in cells for j in cell[:w]+cell[-w:]]
                order = {j: i for i, j in enumerate(boundary)}
                nb = len(boundary)
                assert nb == 2*w*(difference+1)
                for j in boundary:
                    for delta in list(range(-w, 0))+list(range(1, w+1)):
                        l = (j+delta) % s
                        if l in order:
                            distance = abs(order[j]-order[l])
                            assert min(distance, nb-distance) <= 2*w
                            boundary_edges += 1
                # Every interior elimination can fill only within its own
                # two adjacent boundary groups, a clique of size 2w.
                for cell in cells:
                    vertices = cell[:w]+cell[-w:]
                    for j in vertices:
                        for l in vertices:
                            distance = abs(order[j]-order[l])
                            assert min(distance, nb-distance) <= 2*w
                            boundary_edges += 1
    return dict(max_s=max_s, exact_generator_records=records, nearest_ties=ties,
                phase_cell_lengths_checked=cells_checked,
                cross_and_filled_boundary_edges_checked=boundary_edges,
                exceptional_endpoint_cells_checked=True)


def local_large_magnitude(bits):
    from downstream_phase_inverse import local_apply
    n = 20
    g = [Q(1)]+[Q(1, 2**(20*j*j)) if j <= 2 else Q(0) for j in range(1, n)]
    weights = [Q(1, 2**(14*min(i, n-1-i))) for i in range(n)]
    a = toeplitz(g)
    ai = inverse(a)
    x = [row[0] for row in ai]
    local = dict(weights=weights, x=x, bits=bits)
    h = [[weights[i]*a[i][j]/weights[j] for j in range(n)] for i in range(n)]
    hi = [[weights[i]*ai[i][j]/weights[j] for j in range(n)] for i in range(n)]
    assert multiply(h, hi) == [[Q(i == j) for j in range(n)] for i in range(n)]
    gap = min(h[i][i]-sum(abs(h[i][j]) for j in range(n) if i != j) for i in range(n))
    assert gap > Q(9, 10) and norm(hi) <= 1/gap
    probes = [[Q(i == j) for i in range(n)] for j in range(n)]
    probes += [[Q((i*11 % 17)-8, 8) for i in range(n)], [Q(1)]*n]
    error = Q(0)
    for rhs in probes:
        expected = matvec(hi, rhs)
        got = local_apply(local, rhs, rounded=True)
        error = max(error, max(abs(a-b) for a, b in zip(got, expected)))
    assert error < Q(1, 2**80)
    return dict(dimension=n, work_bits=bits, probes=len(probes),
                maximum_internal_reciprocal=str(1/min(weights)),
                internal_scale_power=126, true_inverse_norm_upper=outward(norm(hi)),
                complete_local_map_compared_to_dense=True,
                maximum_rounded_error_upper=outward(error))


def coupled_case(bits):
    from downstream_phase_inverse import local_apply, prepare_boundary
    from downstream_banded_inverse import apply
    cells, length, w = 3, 16, 2
    n = cells*length
    g = [Q(1)]+[Q(1, 2**(8*j*j)) if j <= w else Q(0) for j in range(1, length)]
    weights = [Q(1, 2**(4*min(i, length-1-i))) for i in range(length)]
    h = [[Q(i == j) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i//length == j//length:
                h[i][j] = weights[i % length]*g[abs(i-j)]/weights[j % length]
            elif min(abs(i-j), n-abs(i-j)) <= w:
                h[i][j] = Q(1, 64)
    near_gap = Q(1, 2**12)
    for i, j in [(0, n-1), (n-1, 0)]:
        rest = sum(abs(h[i][k]) for k in range(n) if k not in (i, j))
        h[i][j] = 1-near_gap-rest
    gap = min(h[i][i]-sum(abs(h[i][j]) for j in range(n) if i != j) for i in range(n))
    assert gap == near_gap
    boundary = [j for k in range(cells)
                for j in list(range(k*length, k*length+w))+list(range((k+1)*length-w, (k+1)*length))]
    interior = [j for j in range(n) if j not in boundary]
    hii = [[h[i][j] for j in interior] for i in interior]
    hbi = [[h[i][j] for j in interior] for i in boundary]
    hib = [[h[i][j] for j in boundary] for i in interior]
    hbb = [[h[i][j] for j in boundary] for i in boundary]
    ii = inverse(hii)
    correction = multiply(multiply(hbi, ii), hib)
    schur = [[hbb[i][j]-correction[i][j] for j in range(len(boundary))]
             for i in range(len(boundary))]
    sgap = min(schur[i][i]-sum(abs(schur[i][j]) for j in range(len(boundary)) if i != j)
               for i in range(len(boundary)))
    assert sgap >= gap and norm(schur) <= norm(h)
    for i in range(len(boundary)):
        for j in range(len(boundary)):
            distance = abs(i-j)
            if min(distance, len(boundary)-distance) > 2*w:
                assert schur[i][j] == 0
    locals_ = []
    for cell in range(cells):
        ids = list(range(cell*length+w, (cell+1)*length-w))
        gcell = toeplitz(g[:len(ids)])
        invcell = inverse(gcell)
        locals_.append(dict(ids=ids, weights=weights[w:-w],
                            x=[row[0] for row in invcell], bits=bits))
    table, metadata = prepare_boundary([[rounded(x, bits) for x in row] for row in schur], 2*w, bits)
    dense = inverse(h)
    maximum_error = maximum_residual = Q(0)
    probes = [[Q(i == j) for i in range(n)] for j in range(n)]
    probes += [[Q((-1)**i, 2) for i in range(n)], [Q(1, 2)]*n]
    for rhs in probes:
        first = [Q(0)]*n
        for local in locals_:
            got = local_apply(local, [rhs[i] for i in local['ids']], rounded=True)
            for i, value in zip(local['ids'], got):
                first[i] = value
        rb = [rounded(rhs[i]-sum(rounded(h[i][j], bits)*first[j] for j in interior), bits)
              for i in boundary]
        xb = apply(table, rb)
        actual = [Q(0)]*n
        for i, value in zip(boundary, xb):
            actual[i] = value
        for local in locals_:
            ri = [rounded(rhs[i]-sum(rounded(h[i][j], bits)*actual[j] for j in boundary), bits)
                  for i in local['ids']]
            got = local_apply(local, ri, rounded=True)
            for i, value in zip(local['ids'], got):
                actual[i] = value
        expected = matvec(dense, rhs)
        error = max(abs(a-b) for a, b in zip(actual, expected))
        residual = max(abs(a-b) for a, b in zip(matvec(h, actual), rhs))
        assert error <= residual/gap
        maximum_error = max(maximum_error, error)
        maximum_residual = max(maximum_residual, residual)
    assert maximum_error < Q(1, 2**64)
    return dict(dimension=n, phase_cells=cells, cell_length=length,
                interior_dimension=len(interior), boundary_dimension=len(boundary),
                boundary_halfwidth=2*w, gap=str(gap),
                Schur_gap_lower=outward(sgap), Schur_row_norm_upper=outward(norm(schur)),
                exact_dense_reference_inverse=True, all_basis_probes=len(probes)-2,
                extra_signed_probes=2, work_bits=bits,
                complete_two_local_passes_and_boundary_solve=True,
                maximum_error_upper=outward(maximum_error),
                maximum_residual_upper=outward(maximum_residual),
                rounded_boundary_metadata=metadata)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--bits', type=int, default=256)
    args = ap.parse_args()
    begin = time.monotonic()
    result = dict(gs=gs_audit(), cells=cell_census(),
                  large_internal_scale=local_large_magnitude(args.bits),
                  coupled_cyclic_schur=coupled_case(args.bits),
                  source_sha256={p.name: sha256(p.read_bytes()).hexdigest() for p in
                                 (Path(__file__), Path(__file__).with_name('downstream_phase_inverse.py'),
                                  Path(__file__).with_name('downstream_banded_inverse.py'),
                                  Path(__file__).with_name('review_banded_inverse.py'))},
                  wall_seconds=time.monotonic()-begin,
                  scope='Independent exact GS, cells, large-scale rounding and dense cyclic Schur calibration; all-size tape and analytic transfer separately derived')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
