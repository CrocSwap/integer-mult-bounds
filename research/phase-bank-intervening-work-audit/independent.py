#!/usr/bin/env python3
"""Independent exact Gaussian-rational matrix audit of intervening data work.

No predecessor model or primary checker imports. Matrix indices put the data
bits below the bank bits. Products act right to left on column vectors.
Finite evidence only; the all-parameter claim requires the written proof.
Prepared by kumagi with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from itertools import product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def g(real=0, imag=0):
    return Fraction(real), Fraction(imag)


ZERO, ONE = g(), g(1)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def sign(exponent):
    return g(-1 if exponent % 2 else 1)


def zero(n):
    return [[ZERO for _ in range(n)] for _ in range(n)]


def identity(n):
    out = zero(n)
    for j in range(n):
        out[j][j] = ONE
    return out


def multiply(a, b):
    n = len(a)
    require(len(b) == n, "square matrices of equal size")
    out = zero(n)
    for row, mid, column in product(range(n), repeat=3):
        if a[row][mid] != ZERO and b[mid][column] != ZERO:
            out[row][column] = add(out[row][column], times(a[row][mid], b[mid][column]))
    return out


def scale(matrix, coefficient):
    return [[times(coefficient, value) for value in row] for row in matrix]


def plus(a, b):
    return [[add(x, y) for x, y in zip(arow, brow)] for arow, brow in zip(a, b)]


def chain(*matrices):
    out = identity(len(matrices[0]))
    for matrix in matrices:
        out = multiply(out, matrix)
    return out


def pauli(r, a, b):
    """X^b Z^a, directly from its basis action."""
    out = zero(1 << r)
    for column in range(1 << r):
        out[column ^ b][column] = sign((a & column).bit_count())
    return out


def controlled(labels, r):
    nd, nb = len(labels), 1 << r
    out = zero(nd * nb)
    for d, (a, b) in enumerate(labels):
        for c in range(nb):
            out[d + nd * (c ^ b)][d + nd * c] = sign((a & c).bit_count())
    return out


def lift(data, nb):
    nd = len(data)
    out = zero(nd * nb)
    for e, d, c in product(range(nd), range(nd), range(nb)):
        out[e + nd * c][d + nd * c] = data[e][d]
    return out


def factor_data(matrix, nd, nb):
    candidate = [[matrix[e][d] for d in range(nd)] for e in range(nd)]
    return candidate if lift(candidate, nb) == matrix else None


def edge_formula(data, incoming, outgoing, r):
    nd, nb = len(data), 1 << r
    out = zero(nd * nb)
    for e, d, c in product(range(nd), range(nd), range(nb)):
        a, b = incoming[d]
        ap, bp = outgoing[e]
        exponent = (ap & b).bit_count() + ((a ^ ap) & c).bit_count()
        out[e + nd * (c ^ b ^ bp)][d + nd * c] = times(data[e][d], sign(exponent))
    return out


def audit_edges():
    blocks = columns = omitted_phase_failures = 0
    for r in (1, 2):
        for a, b, ap, bp in product(range(1 << r), repeat=4):
            actual = multiply(pauli(r, ap, bp), pauli(r, a, b))
            bare = pauli(r, a ^ ap, b ^ bp)
            expected = scale(bare, sign((ap & b).bit_count()))
            require(actual == expected, "edge Pauli product")
            scalar = actual[0][0]
            require((actual == scale(identity(1 << r), scalar)) == (a == ap and b == bp),
                    "a nonzero edge is scalar exactly when both labels match")
            if (ap & b).bit_count() % 2:
                require(actual != bare, "omitted commutation phase must fail")
                omitted_phase_failures += 1
            blocks += 1
            columns += 1 << r
    return blocks, columns, omitted_phase_failures


def audit_data_matrices():
    cases = columns = rejected = transported = 0
    dense = [[g(Fraction(e + 1, d + 1), (-1) ** (e + d))
              for d in range(4)] for e in range(4)]
    block = [[dense[e][d] if e // 2 == d // 2 else ZERO
              for d in range(4)] for e in range(4)]
    cross = [row[:] for row in block]
    cross[0][2] = g(1, 1)
    diagonal = [[dense[e][d] if e == d else ZERO for d in range(4)] for e in range(4)]
    permutation = (2, 3, 0, 1)
    permuted = [block[permutation[e]][:] for e in range(4)]
    for r in (1, 2):
        unique = [(0, 0), (0, 1), (1, 0), (1, 1)] if r == 1 else [(0, 0), (1, 2), (2, 3), (3, 1)]
        repeated = [unique[0], unique[0], unique[-1], unique[-1]]
        moved = [repeated[permutation[e]] for e in range(4)]
        fixtures = (
            (zero(4), unique, list(reversed(unique)), True),
            (diagonal, unique, unique, True),
            (dense, [unique[-1]] * 4, [unique[-1]] * 4, True),
            (dense, unique, unique, False),
            (block, repeated, repeated, True),
            (cross, repeated, repeated, False),
            (permuted, repeated, moved, True),
            (permuted, repeated, repeated, False),
        )
        for data, incoming, outgoing, admissible in fixtures:
            actual = chain(controlled(outgoing, r), lift(data, 1 << r), controlled(incoming, r))
            require(actual == edge_formula(data, incoming, outgoing, r), "full edge formula")
            support_matches = all(data[e][d] == ZERO or incoming[d] == outgoing[e]
                                  for e, d in product(range(4), repeat=2))
            factored = factor_data(actual, 4, 1 << r)
            require(support_matches == admissible == (factored is not None), "support iff tensor factor")
            if admissible:
                expected = [[times(data[e][d], sign((incoming[d][0] & incoming[d][1]).bit_count()))
                             for d in range(4)] for e in range(4)]
                require(factored == expected, "admitted data operator is U D_ab")
                transported += incoming != outgoing and data != zero(4)
            else:
                rejected += 1
            cases += 1
            columns += 4 * (1 << r)
    return cases, columns, rejected, transported


def physical_gate(axis, entries):
    out = zero(8)
    for column in range(8):
        bit = (column >> axis) & 1
        for target in (0, 1):
            row = (column & ~(1 << axis)) | (target << axis)
            out[row][column] = entries[target][bit]
    return out


def differences(a, b):
    return [column for column in range(len(a))
            if any(arow[column] != brow[column] for arow, brow in zip(a, b))]


def audit_physical():
    # Two normalized data Hadamards combine into rational entries +/-1/2.
    fourier_data = [[times(g(Fraction(1, 2)), sign((e & d).bit_count()))
                     for d in range(4)] for e in range(4)]
    fourier = lift(fourier_data, 2)
    labels = [(d & 1, (d >> 1) & 1) for d in range(4)]
    producer = chain(fourier, controlled(labels, 1), fourier)
    require(multiply(fourier, fourier) == identity(8), "normalized data Fourier involution")
    closed = zero(8)
    for column, row in product(range(8), repeat=2):
        x, y, c = column & 1, (column >> 1) & 1, column >> 2
        xp, yp, cp = row & 1, (row >> 1) & 1, row >> 2
        if xp == x ^ c:
            closed[row][column] = times(g(Fraction(1, 2)), sign((cp ^ c) * (yp ^ y)))
    require(producer == closed, "closed physical kernel of accumulator_word(1, half=True)")
    alpha, beta = g(Fraction(1, 2), Fraction(1, 2)), g(Fraction(1, 2), Fraction(-1, 2))
    c_x = physical_gate(0, [[alpha, beta], [beta, alpha]])
    s_x = physical_gate(0, [[ONE, ZERO], [ZERO, g(0, 1)]])
    z_x = physical_gate(0, [[ONE, ZERO], [ZERO, g(-1)]])
    x_x = physical_gate(0, [[ZERO, ONE], [ONE, ZERO]])
    x_y = physical_gate(1, [[ZERO, ONE], [ONE, ZERO]])
    z_c = physical_gate(2, [[ONE, ZERO], [ZERO, g(-1)]])
    q_data = [[times(g(Fraction(1, 2)), sign(((e ^ d) & 1) * (((e ^ d) >> 1) & 1)))
               for d in range(4)] for e in range(4)]
    q_xy = lift(q_data, 2)
    require(multiply(producer, producer) == q_xy, "uninterrupted accumulator closure")
    for name, data in (("C_x", c_x), ("Q_xy", q_xy), ("X_x", x_x)):
        require(chain(producer, data, producer) == multiply(data, q_xy), "safe physical " + name)
    z_actual = chain(producer, z_x, producer)
    s_actual = chain(producer, s_x, producer)
    mismatch = {}
    for name, actual, data in (("S_x", s_actual, s_x), ("Z_x", z_actual, z_x)):
        bad = differences(actual, multiply(data, q_xy))
        require(bad == list(range(8)), "unsafe interleaving must fail on all eight physical inputs")
        require(factor_data(actual, 4, 2) is None, "unsafe endpoint admits no data-only V")
        mismatch[name] = {"all_columns": len(bad), "dirty_bank_columns": sum(j >= 4 for j in bad)}
    require(z_actual == chain(z_x, q_xy, x_y, z_c), "exact Z_x residual X_y Z_c")
    residual = plus(scale(identity(8), alpha), scale(chain(z_x, x_y, z_c), beta))
    require(s_actual == multiply(residual, q_xy), "exact S_x residual")
    twisted_s, twisted_z = zero(8), zero(8)
    for column in range(8):
        parity = (column & 1) ^ (column >> 2)
        twisted_s[column][column] = g(0, 1) if parity else ONE
        twisted_z[column][column] = sign(parity)
    require(s_actual == multiply(q_xy, twisted_s), "S_x residual in physical input coordinates")
    require(z_actual == multiply(q_xy, twisted_z), "Z_x residual in physical input coordinates")
    repaired = chain(producer, z_c, z_x, producer)
    require(repaired == multiply(z_x, q_xy), "bank Z before consumer repairs Z_x")
    misplaced = chain(z_c, producer, z_x, producer)
    require(misplaced == chain(z_x, q_xy, x_y), "late bank Z leaves X_y")
    require(differences(misplaced, multiply(z_x, q_xy)) == list(range(8)), "reject misplaced repair")
    return {
        "dimension": 8,
        "safe_cases": 3,
        "safe_basis_columns": 24,
        "unsafe_cases": mismatch,
        "residual_identities": 4,
        "nonfactorable_endpoints": 2,
        "repaired_basis_columns": 8,
        "repaired_dirty_bank_columns": 4,
        "misplaced_repair_rejected_columns": 8,
    }


def check_all():
    blocks, edge_columns, phase_failures = audit_edges()
    cases, data_columns, rejected, transported = audit_data_matrices()
    return {
        "status": "PASS_INDEPENDENT_EXACT_MATRIX_AUDIT",
        "arithmetic": "Gaussian rational pairs of fractions.Fraction",
        "edge_blocks": blocks,
        "edge_bank_columns": edge_columns,
        "data_matrix_cases": cases,
        "data_matrix_basis_columns": data_columns,
        "nonfactorable_data_cases": rejected,
        "nonzero_transported_label_cases": transported,
        "omitted_commutation_phase_rejections": phase_failures,
        "physical": audit_physical(),
    }


if __name__ == "__main__":
    print(json.dumps(check_all(), sort_keys=True))
