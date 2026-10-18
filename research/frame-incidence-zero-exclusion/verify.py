#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the finite hypotheses of the frame-incidence zero-exclusion theorem.

Standard library only; no SAT solver, numerical algebra, downloads, or assert.
The universal field argument is in proof.md. This verifies its finite premises.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from math import isqrt
from pathlib import Path

PRIME = 1000003
PIVOT = (2, 5, 8, 9, 30, 41, 108, 117)
DELETED = (32, 45, 73, 78, 88)
COVERAGE_CONTROL = (3, 13, 14, 22, 23)


class VerificationError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def rank_mod(rows, prime=PRIME):
    """Exact modular Gaussian elimination; nonzero minors lift to characteristic 0."""
    basis = {}
    for row in rows:
        v = [x % prime for x in row]
        for j in sorted(basis):
            if v[j]:
                a, w = v[j], basis[j]
                v = [(x - a * y) % prime for x, y in zip(v, w)]
        j = next((j for j, x in enumerate(v) if x), None)
        if j is not None:
            inverse = pow(v[j], -1, prime)
            basis[j] = [(x * inverse) % prime for x in v]
    return len(basis)


class Model:
    def __init__(self):
        vectors = []
        for i, j in combinations(range(8), 2):
            for s in (-2, 2):
                v = [0] * 8
                v[i], v[j] = 2, s
                vectors.append(tuple(v))
        for signs in product((-1, 1), repeat=7):
            if signs.count(-1) % 2 == 0:
                vectors.append((1,) + signs)
        self.vectors = tuple(sorted(vectors))
        require(len(set(self.vectors)) == 120, 'root count')
        require(all(sum(x*x for x in v) == 8 for v in self.vectors), 'root norms')
        require(all(next(x for x in v if x) > 0 for v in self.vectors), 'root signs')
        dots = [[sum(x*y for x, y in zip(v, w)) for w in self.vectors]
                for v in self.vectors]
        require(all(x % 4 == 0 for row in dots for x in row), 'Gram integrality')
        self.g = [[x // 4 for x in row] for row in dots]
        require(all(self.g[i][j] in ((2,) if i == j else (-1, 0, 1))
                    for i in range(120) for j in range(120)), 'Gram values')
        f0 = []
        for a in range(4):
            for s in (-2, 2):
                v = [0] * 8
                v[2*a], v[2*a+1] = 2, s
                f0.append(self.vectors.index(tuple(v)))
        self.frame0 = tuple(sorted(f0))
        self.p112 = set(range(120)) - set(self.frame0)
        orth = [sum(1 << j for j in range(120) if i != j and self.g[i][j] == 0)
                for i in range(120)]
        frames = []

        def visit(prefix, candidates):
            if len(prefix) == 8:
                frames.append(tuple(prefix))
                return
            while candidates.bit_count() >= 8 - len(prefix):
                bit = candidates & -candidates
                candidates -= bit
                i = bit.bit_length() - 1
                visit(prefix + [i], candidates & orth[i])

        visit([], (1 << 120) - 1)
        self.frames = tuple(frames)
        require(len(self.frames) == len(set(self.frames)) == 2025, 'frame enumeration')
        require(self.frame0 == (0, 1, 6, 11, 20, 29, 106, 119), 'FRAME0 IDs')

    def geometry(self, pivot):
        require(tuple(sorted(set(pivot))) == pivot and len(pivot) == 8, 'pivot format')
        require(pivot in self.frames, 'pivot is not an E8 frame')
        supports, classes, blocks = {}, {}, {}
        for i in range(120):
            if i in pivot:
                continue
            t = tuple(k for k in pivot if self.g[i][k])
            require(len(t) == 4, 'nonpivot support size')
            supports[i] = t
            parity = sum(self.g[i][k] < 0 for k in t) % 2
            classes.setdefault((t, parity), []).append(i)
            blocks.setdefault(t, []).append(i)
        require(len(blocks) == 14 and len(classes) == 28, 'block/class counts')
        for t, indices in blocks.items():
            require(len(indices) == 8, 'block size')
            for k in t:
                others = [l for l in t if l != k]
                signs = {tuple(self.g[i][k] * self.g[i][l] for l in others) for i in indices}
                require(signs == set(product((-1, 1), repeat=3)), 'block sign cube')
        for (t, _), c in classes.items():
            require(len(c) == 4, 'class size')
            for i in c:
                for j in c:
                    require(sum(self.g[i][k]*self.g[j][k] for k in t)
                            == (4 if i == j else 0), 'class Hadamard identity')
        require(all(sum(set(s) <= set(t) for t in blocks) == 1
                    for s in combinations(pivot, 3)), 'Steiner triple condition')
        require(all(sum(set(s) <= set(t) for t in blocks) == 3
                    for s in combinations(pivot, 2)), 'Steiner pair condition')
        require(all(len(set(t) & set(u)) in (0, 2)
                    for t, u in combinations(blocks, 2)), 'block intersections')
        require(all(sum(self.g[i][k]*self.g[j][k] for k in pivot) == 2*self.g[i][j]
                    for i in range(120) for j in range(120)), 'pivot Gram expansion')
        return supports, classes, blocks


def pair_graph(model, live_frames, indices, k, l):
    """Edges come from complete frames meeting I_kl in exactly TWO lines."""
    require(bool(indices), 'G: empty pair vertex set')
    vertices = set(indices)
    edges = set()
    for s in live_frames:
        intersection = tuple(sorted(vertices.intersection(s)))
        if len(intersection) == 2:
            edges.add(intersection)
    adjacency = {i: set() for i in indices}
    for i, j in sorted(edges):
        require(model.g[i][k]*model.g[i][l] + model.g[j][k]*model.g[j][l] == 0,
                'G: inconsistent edge sign')
        adjacency[i].add(j)
        adjacency[j].add(i)
    seen = {min(indices)}
    todo = list(seen)
    while todo:
        for j in adjacency[todo.pop()] - seen:
            seen.add(j)
            todo.append(j)
    require(seen == vertices, f'G: disconnected frame-intersection graph {k,l}')
    return [k, l, len(indices), len(edges)]


def certify(model, pivot, live, frames_override=None):
    require(set(pivot) <= live <= set(range(120)), 'invalid live set / deleted pivot')
    supports, classes, blocks = model.geometry(pivot)
    live_frames = [s for s in model.frames if set(s) <= live]
    if frames_override is not None:
        require(all(s in live_frames for s in frames_override), 'invalid selected frame')
        live_frames = list(frames_override)
    nonpivot = sorted(live - set(pivot))
    g = model.g
    diagonal, graphs = [], []
    for s in live_frames:
        for k, l in combinations(pivot, 2):
            require(sum(g[i][k]*g[i][l] for i in s) == 0, 'frame off-diagonal identity')
        require(all(sum(g[i][k]**2 for i in s) == 4 for k in pivot), 'frame diagonal identity')
    for k in pivot:
        indices = [i for i in nonpivot if g[i][k]]
        others = [l for l in pivot if l != k]
        h = [[g[i][k]*g[i][l] for l in others] for i in indices]
        rows = sorted({tuple(int(i in s) for i in indices) for s in live_frames})
        require(all(sum(row[j]*h[j][c] for j in range(len(indices))) == 0
                    for row in rows for c in range(7)), 'D: exact kernel identity')
        h_rank, m_rank = rank_mod(h), rank_mod(rows)
        require(h_rank == 7, f'D: dependent canonical kernel at {k}')
        require(m_rank == len(indices)-7, f'D: incidence rank deficit at {k}')
        diagonal.append([k, len(indices), m_rank, h_rank, len(rows)])
    for k, l in combinations(pivot, 2):
        indices = [i for i in nonpivot if g[i][k] and g[i][l]]
        graphs.append(pair_graph(model, live_frames, indices, k, l))
    good, full, witnesses, profiles = [], [], [], []
    for t in sorted(blocks):
        cs = [tuple(i for i in classes[(t, p)] if i in live) for p in (0, 1)]
        profiles.append(sorted(map(len, cs)))
        if all(len(c) == 4 for c in cs):
            full.append(t)
        choices = [p for p in (0, 1) if len(cs[p]) == 4 and len(cs[1-p]) >= 1]
        if choices:
            p = choices[0]
            good.append(t)
            witnesses.append([list(t), list(cs[p]), cs[1-p][0]])
    covered = {p for t in good for p in combinations(t, 2)}
    missing = sorted(set(combinations(pivot, 2)) - covered)
    require(not missing, f'W: uncovered pivot pairs {missing}')
    full_covered = {p for t in full for p in combinations(t, 2)}
    return dict(
        deleted_from_p112=sorted(model.p112-live), pivot=list(pivot),
        live_count=len(live), live_frames=len(live_frames), diagonal_table=diagonal,
        pair_graph_table=graphs, witnessed_blocks=len(good), fully_live_blocks=len(full),
        witness_table=witnesses, class_size_profile=[list(k)+[v] for k,v in
            sorted(Counter(tuple(p) for p in profiles).items())],
        pairs_not_covered_by_fully_live_blocks=[list(p) for p in
            sorted(set(combinations(pivot, 2))-full_covered)],
        all_blocks_nonempty=all(any(i in live for i in indices) for indices in blocks.values()))


def check_factors(model, pivot, live, a, b):
    """Check the ORIGINAL factor equations, not Boolean patterns."""
    for f in pivot:
        target = [4*int(k == f) for k in pivot]
        require(a[f] == target and b[f] == target, 'factor pivot condition')
    for i in live:
        for p, f in enumerate(pivot):
            if model.g[i][f] == 0:
                require(a[i][p] == b[i][p] == 0, 'factor support condition')
        for j in live:
            if i == j or model.g[i][j] == 0:
                value = sum(x*y for x,y in zip(a[i],b[j]))
                require(value == (16 if i == j else 0), f'factor equation {i,j}')


def expect_failure(action, prefix):
    try:
        action()
    except VerificationError as error:
        require(str(error).startswith(prefix), f'wrong rejection: {error}')
        return str(error)
    raise VerificationError('negative control was accepted')


def controls(model, report):
    f, live, g = PIVOT, model.p112-set(DELETED), model.g
    d = {i: Q(i % 7+1, i % 5+2) for i in live}
    a = {i: [2*g[i][k]*d[i]/d[k] for k in f] for i in live}
    b = {i: [2*g[i][k]*d[k]/d[i] for k in f] for i in live}
    check_factors(model, f, live, a, b)
    for i in live:
        for j in live:
            require(sum(x*y for x,y in zip(a[i],b[j]))/4 == 2*g[i][j]*d[i]/d[j],
                    'exact gauge reconstruction')
    require(all(a[i][p]*b[i][p] == 4 for i in live-set(f)
                for p,k in enumerate(f) if g[i][k]), 'gauge product control')
    aa = {i: list(row) for i,row in a.items()}
    i = min(live-set(f))
    p = next(p for p,k in enumerate(f) if g[i][k])
    aa[i][p] = 0
    perturbation = expect_failure(lambda: check_factors(model,f,live,aa,b), 'factor equation')
    rank_rejection = expect_failure(lambda: certify(model,f,live,[f]), 'D:')
    k,l = f[:2]
    indices = [i for i in live-set(f) if g[i][k] and g[i][l]]
    graph_rejection = expect_failure(lambda: pair_graph(model,[f],indices,k,l), 'G:')
    coverage_rejection = expect_failure(
        lambda: certify(model,f,model.p112-set(COVERAGE_CONTROL)), 'W:')
    t, c, extra = report['witness_table'][0]
    small_live = set(f) | set(c)
    a0 = {i: [0]*8 for i in small_live}
    b0 = {i: [0]*8 for i in small_live}
    for i in f:
        a0[i][f.index(i)] = b0[i][f.index(i)] = 4
    for i,k in zip(c,t):
        a0[i][f.index(k)] = b0[i][f.index(k)] = 4
    check_factors(model,f,small_live,a0,b0)
    zero_count = sum(a0[i][f.index(k)] == 0 for i in c for k in t)
    require(zero_count == 12, 'local nongauge control lacks zeros')
    # Four possible exceptional rows in the delta branch. The fifth row
    # necessarily has diagonal 1/2 or -1/2, which is not an idempotent scalar.
    k, rest = t[0], t[1:]
    signs = {i: [g[i][k]*g[i][l] for l in rest] for i in c+[extra]}
    for exceptional in c:
        coefficients = [Q(x,4) for x in signs[exceptional]]
        w = {i: Q(1,4)+sum(x*y for x,y in zip(coefficients,signs[i]))
             for i in c+[extra]}
        require(all(w[i] == int(i == exceptional) for i in c), 'delta Fourier identity')
        require(w[extra] in (Q(1,2),Q(-1,2)) and w[extra]**2 != w[extra],
                '4+1 obstruction control')
    # Actual 13-line 4+1 boundary control, separate from the 12-line control.
    # These are fixed GLOBAL line labels, not positions or a selected witness.
    t13, c13, j13 = (2, 5, 30, 41), (22, 27, 34, 37), 23
    require(f == (2, 5, 8, 9, 30, 41, 108, 117), '13-line pivot convention')
    supports13, classes13, _ = model.geometry(f)
    require(tuple(classes13.get((t13, 1), ())) == c13
            and j13 in classes13.get((t13, 0), ()), '13-line class convention')
    require(all(supports13[i] == t13 for i in c13+(j13,)), '13-line support convention')
    require(all(g[i][j13] != 0 for i in c13), '13-line opposite-class orthogonality')
    live13 = set(f) | set(c13) | {j13}
    require(len(live13) == 13, '13-line live count')
    a13 = {i: [0]*8 for i in live13}
    for i in f:
        a13[i][f.index(i)] = 4
    for i,k in zip(c13,t13):
        a13[i][f.index(k)] = 4
    a13[j13][f.index(2)] = 4  # Pivot LABEL 2: the first coordinate in f.
    b13 = {i: list(row) for i,row in a13.items()}
    check_factors(model,f,live13,a13,b13)
    # This integer matrix is 4K. Its modular rank gives a characteristic-zero
    # lower bound; eight-column factorization gives the matching upper bound.
    order13 = sorted(live13)
    four_k13 = [[sum(x*y for x,y in zip(a13[i],b13[j])) for j in order13]
                for i in order13]
    rank13 = rank_mod(four_k13)
    require(rank13 == 8, '13-line rank lower bound')
    zeros_a13 = sum(a13[i][f.index(k)] == 0 for i in c13+(j13,) for k in t13)
    zeros_b13 = sum(b13[i][f.index(k)] == 0 for i in c13+(j13,) for k in t13)
    require(zeros_a13 == zeros_b13 == 15, '13-line nongauge support zeros')
    pi13 = {i: [[Q(a13[i][p]*b13[i][q],16) for q in range(8)]
                for p in range(8)] for i in live13}
    require(all(pi13[i][p][q] == 0 for i in live13
                for p in range(8) for q in range(8) if p != q),
            '13-line off-diagonal formula with all t=0')
    p13 = f.index(2)
    diagonal13 = [pi13[i][p13][p13] for i in c13]
    require(diagonal13 == [1,0,0,0], '13-line class diagonal projectors')
    coefficients13 = [sum(diagonal13[r]*g[i][2]*g[i][l]
                          for r,i in enumerate(c13))/4 for l in t13[1:]]
    require(coefficients13 == [Q(1,4),Q(1,4),Q(-1,4)], '13-line Hadamard coefficients')
    require(all(Q(1,4)+sum(x*g[i][2]*g[i][l] for x,l in zip(coefficients13,t13[1:]))
                == diagonal13[r] for r,i in enumerate(c13)), '13-line class interpolation')
    predicted13 = Q(1,4)+sum(x*g[j13][2]*g[j13][l]
                             for x,l in zip(coefficients13,t13[1:]))
    actual13 = pi13[j13][p13][p13]
    require(predicted13 == Q(-1,2) and actual13 == 1 and predicted13 != actual13,
            '13-line shared diagonal mismatch')
    return dict(
        exact_gauge_matrix_entries=len(live)**2,
        perturbed_factor_rejected=perturbation,
        deficient_frame_family_rejected=rank_rejection,
        disconnected_pair_graph_rejected=graph_rejection,
        coverage_control_deleted=list(COVERAGE_CONTROL),
        coverage_control_rejected=coverage_rejection,
        coverage_control_passed_D_and_G=True,
        local_actual_nongauge_live_count=len(small_live),
        local_actual_nongauge_zero_a_entries=zero_count,
        local_delta_branches_checked=4,
        local_4plus1_actual_nongauge=dict(
            pivot=list(f), block=list(t13), complete_minus_class=list(c13), extra_line=j13,
            live_count=len(live13), rank=rank13,
            diagonal_equations_checked=len(live13),
            ordered_orthogonal_zero_equations_checked=sum(
                i != j and g[i][j] == 0 for i in live13 for j in live13),
            zero_a_support_entries=zeros_a13, zero_b_support_entries=zeros_b13,
            distinguished_pivot_label=2, class_diagonals=list(map(str,diagonal13)),
            hadamard_coefficients=list(map(str,coefficients13)),
            predicted_extra_diagonal=str(predicted13), actual_extra_diagonal=str(actual13),
            off_diagonal_formula_all_t_zero=True))


def parse_ids(text):
    try:
        values = tuple(sorted(int(x) for x in text.split(',')))
    except ValueError as error:
        raise VerificationError('IDs must be comma-separated integers') from error
    require(len(values) == len(set(values)), 'duplicate IDs')
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true', help='regenerate certificate.json')
    parser.add_argument('--deleted', help='check one other five-set; no universal search')
    parser.add_argument('--pivot', help='eight pivot IDs for --deleted (default: fixture pivot)')
    args = parser.parse_args()
    require(PRIME > 2 and all(PRIME % d for d in range(2,isqrt(PRIME)+1)), 'modulus is not prime')
    model = Model()
    if args.deleted:
        deleted = parse_ids(args.deleted)
        pivot = parse_ids(args.pivot) if args.pivot else PIVOT
        require(len(deleted) == 5 and set(deleted) <= model.p112, 'need five P112 lines')
        report = certify(model,pivot,model.p112-set(deleted))
        print(json.dumps(report,indent=2))
        print('PASS_SELECTED_FINITE_HYPOTHESES; no all-five-set claim')
        return
    require(args.pivot is None, '--pivot requires --deleted')
    report = certify(model,PIVOT,model.p112-set(DELETED))
    require(any(model.g[i][j] != 0 for i,j in combinations(DELETED,2)),
            'fixture must not be frame-contained')
    require(report['all_blocks_nonempty'], 'gauge corollary nonempty-block premise')
    tests = controls(model,report)
    result = dict(schema='p107-frame-incidence-4plus1-v1', prime=PRIME,
                  frame0=list(model.frame0), report=report, controls=tests)
    path = Path(__file__).with_name('certificate.json')
    if args.write_certificate:
        path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:
        expected = json.loads(path.read_text(encoding='utf-8'))
        require(result == expected, 'certificate content mismatch')
    print('PASS_P107_FRAME_INCIDENCE_ZERO_EXCLUSION')
    print(f'Fixture: X={list(DELETED)}; F={list(PIVOT)}')
    print(f'120 roots; 2025 total frames; {report["live_frames"]} live frames; '
          '8 exact characteristic-zero rank certificates; 28 connected pair graphs.')
    print(f'{report["witnessed_blocks"]} witnessed 4+1 blocks cover all 28 pivot pairs; '
          f'{report["fully_live_blocks"]} fully live blocks alone do not.')
    print('Positive exact rational reconstruction: 11449 entries. '
          'Four rejection controls and four local delta-branch checks passed.')
    print('Actual nongauge controls: ONLY the restricted 12- and 13-line models, not P107.')
    print('13-line boundary: 15 support zeros per factor; predicted Pi_23(2,2)=-1/2, actual=1.')
    print('All-five-set coverage NOT checked. Universal implication: proof.md.')


if __name__ == '__main__':
    try:
        main()
    except (VerificationError, OSError, ValueError) as error:
        print(f'FAIL: {error}',file=sys.stderr)
        sys.exit(1)
