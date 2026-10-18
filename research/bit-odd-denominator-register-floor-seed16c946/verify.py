#!/usr/bin/env python3
"""Exact formal replay and controls for the odd-denominator auxiliary bound."""
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ZERO_EXP = (0,) * 9


def need(condition, message):
    if not condition:
        raise ValueError(message)


def matrix_zero(n):
    return (0,) * n


def matrix_identity(n):
    return tuple(1 << i for i in range(n))


def matrix_xor(a, b):
    need(len(a) == len(b), 'matrix XOR shape')
    return tuple(x ^ y for x, y in zip(a, b))


def matrix_is_zero(a):
    return all(row == 0 for row in a)


def matrix_mul(a, b, ncols=None):
    """Multiply binary matrices represented by row bitmasks."""
    if not b:
        return ()
    if ncols is None:
        ncols = len(b)
    out = []
    for row in a:
        value = 0
        for j in range(len(b)):
            if (row >> j) & 1:
                value ^= b[j]
        out.append(value & ((1 << ncols) - 1))
    return tuple(out)


def gf2_rank(rows, ncols):
    work = [int(row) & ((1 << ncols) - 1) for row in rows]
    rank = 0
    for col in range(ncols):
        pivot = next((i for i in range(rank, len(work)) if (work[i] >> col) & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(len(work)):
            if i != rank and ((work[i] >> col) & 1):
                work[i] ^= work[rank]
        rank += 1
        if rank == len(work):
            break
    return rank


def outer_bits(x, y, n):
    return tuple(((1 << n) - 1 if (x >> i) & 1 else 0) &
                 sum(1 << j for j in range(n) if (y >> j) & 1)
                 for i in range(n))


def binary_projectors(n):
    out = []
    for x in range(1, 1 << n):
        for y in range(1, 1 << n):
            if (x & y).bit_count() & 1:
                out.append(outer_bits(x, y, n))
    return out


def is_idempotent(nmat, n):
    return matrix_mul(nmat, nmat, n) == nmat


def exponent(matrix):
    return tuple(int(value) for row in matrix for value in row)


def exponent_add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def polynomial_multiply(left, right):
    out = {}
    for ea, ma in left.items():
        for eb, mb in right.items():
            e = exponent_add(ea, eb)
            term = matrix_mul(ma, mb, len(mb))
            value = matrix_xor(out.get(e, matrix_zero(len(term))), term)
            if matrix_is_zero(value):
                out.pop(e, None)
            else:
                out[e] = value
    return out


def diagonal_projector(n, role):
    return tuple((1 << role) if i == role else 0 for i in range(n))


def rank_one_over_q(matrix):
    rows, cols = len(matrix), len(matrix[0])
    pivot = None
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j]:
                pivot = (i, j)
                break
        if pivot:
            break
    if pivot is None:
        return False
    i0, j0 = pivot
    for i in range(rows):
        for j in range(cols):
            if (matrix[i][j] * matrix[i0][j0] !=
                    matrix[i][j0] * matrix[i0][j]):
                return False
    return True


def det3_mod2(matrix):
    a = [[int(x) & 1 for x in row] for row in matrix]
    signless = 0
    for p in ((0, 1, 2), (0, 2, 1), (1, 0, 2),
              (1, 2, 0), (2, 0, 1), (2, 1, 0)):
        term = a[0][p[0]] & a[1][p[1]] & a[2][p[2]]
        signless ^= term
    return signless


def target_rank_sum(targets):
    return sum(gf2_rank(tuple(sum((int(value) & 1) << j
                                   for j, value in enumerate(row))
                               for row in matrix), len(matrix[0]))
               for matrix in targets)


def block_diagonal_rows(targets):
    m = len(targets[0])
    w = len(targets)
    rows = [0] * (m * w)
    for role, matrix in enumerate(targets):
        for i in range(m):
            row = 0
            for j in range(m):
                if int(matrix[i][j]) & 1:
                    row |= 1 << (role * m + j)
            rows[role * m + i] = row
    return tuple(rows)


def address_column_frame(matrix, col):
    return tuple(tuple(matrix[i][col] if j == col else 0
                       for j in range(len(matrix)))
                 for i in range(len(matrix)))


def build_calls(targets, nregisters):
    calls = []
    for role, matrix in enumerate(targets):
        for col in range(len(matrix)):
            frame = address_column_frame(matrix, col)
            need(rank_one_over_q(frame), 'column frame is not rank one')
            calls.append((diagonal_projector(nregisters, role), exponent(frame)))
    return calls


def factor_polynomial(projector, frame, nregisters):
    identity = matrix_identity(nregisters)
    constant = matrix_xor(identity, projector)
    return {ZERO_EXP: constant, frame: projector}


def replay(calls, targets, nregisters):
    poly = {ZERO_EXP: matrix_identity(nregisters)}
    for projector, frame in calls:
        need(len(projector) == nregisters, 'projector register dimension')
        need(is_idempotent(projector, nregisters), 'projector is not idempotent')
        need(gf2_rank(projector, nregisters) == 1, 'projector is not rank one')
        need(any(frame), 'zero address frame is not a paid call')
        factor = factor_polynomial(projector, frame, nregisters)
        poly = polynomial_multiply(poly, factor)
    expected = {}
    zero = matrix_zero(nregisters)
    for role in range(nregisters):
        if role < len(targets):
            e = exponent(targets[role])
        else:
            e = ZERO_EXP
        diagonal = diagonal_projector(nregisters, role)
        expected[e] = matrix_xor(expected.get(e, matrix_zero(nregisters)), diagonal)
        if matrix_is_zero(expected[e]):
            expected.pop(e)
    return poly == expected, poly, expected


def xor_frame(a, b):
    return tuple(tuple(int(x) ^ int(y) for x, y in zip(rx, ry))
                 for rx, ry in zip(a, b))


def encode_odd_lattice(matrix, q):
    need(q > 0 and q % 2 == 1, 'denominator must be positive and odd')
    out = []
    for row in matrix:
        values = []
        for value in row:
            scaled = Fraction(value) * q
            need(scaled.denominator == 1, 'matrix is outside the common lattice')
            values.append(scaled.numerator & 1)
        out.append(tuple(values))
    return tuple(out)


def kron_rows(a, b):
    """Kronecker matrix rows, with address row/column nested inside roles."""
    n, m = len(a), len(b)
    out = []
    for i in range(n):
        for u in range(m):
            row = 0
            for j in range(n):
                if (a[i] >> j) & 1:
                    for v in range(m):
                        if (b[u] >> v) & 1:
                            row |= 1 << (j * m + v)
            out.append(row)
    return tuple(out)


def check_pins():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for item in sources['files']:
        data = (ROOT / item['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item['sha256'],
             'pinned source changed: ' + item['path'])


def build_receipt():
    c1 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    c2 = ((1, 0, 0), (1, 1, 0), (0, 0, 1))
    c3 = ((1, 0, 0), (0, 1, 0), (0, 1, 1))
    targets = (c1, c2, c3)
    need(all(det3_mod2(matrix) == 1 for matrix in targets),
         'positive targets must be invertible modulo two')
    data_rank = target_rank_sum(targets)
    need(data_rank == 9 and gf2_rank(block_diagonal_rows(targets), 9) == 9,
         'data target degree-one block rank')

    # The odd-denominator homomorphism preserves sums, including a nonintegral
    # lattice example with common denominator three.
    a = ((Fraction(1, 3), 0, 0), (0, 0, 0), (0, 0, 0))
    b = ((0, 0, 0), (0, Fraction(2, 3), 0), (0, 0, 0))
    ab = tuple(tuple(a[i][j] + b[i][j] for j in range(3)) for i in range(3))
    need(encode_odd_lattice(ab, 3) == tuple(tuple(x ^ y for x, y in zip(ra, rb))
                                            for ra, rb in zip(encode_odd_lattice(a, 3),
                                                               encode_odd_lattice(b, 3))),
         'odd-lattice map is not additive')

    # Every rank-one F2 idempotent in dimensions 3 through 6 is included in a
    # finite support control; the proof covers every n by rank factorization.
    projector_counts = {}
    address = ((1, 0, 0), (1, 0, 0), (0, 0, 0))
    address_rows = tuple(sum((int(value) & 1) << j for j, value in enumerate(row))
                         for row in address)
    for n in (3, 4, 5, 6):
        projectors = binary_projectors(n)
        need(all(gf2_rank(p, n) == 1 and is_idempotent(p, n) for p in projectors),
             'binary rank-one idempotent family')
        for p in projectors:
            k = kron_rows(p, address_rows)
            need(gf2_rank(k, n * 3) <= 1, 'rank-one Kronecker contribution')
        projector_counts[str(n)] = len(projectors)

    # One explicit pair of free mixer matrices preserves rank one around every
    # idempotent; the general proof allows arbitrary invertible prefix/suffixes.
    n = 4
    left = (0b0011, 0b0010, 0b0100, 0b1000)
    right = matrix_identity(n)
    need(gf2_rank(left, n) == n and gf2_rank(right, n) == n,
         'free mixer controls are invertible')
    for p in binary_projectors(n):
        bmat = matrix_mul(matrix_mul(left, p, n), right, n)
        need(gf2_rank(bmat, n) == 1, 'free mixer rank preservation')

    programs = {}
    reference_calls = None
    for nregisters in (3, 4, 6):
        calls = build_calls(targets, nregisters)
        ok, product, expected = replay(calls, targets, nregisters)
        need(ok, 'exact column-decomposition program, n=' + str(nregisters))
        programs[str(nregisters)] = {
            'calls': len(calls),
            'polynomial_support_terms': len(product),
            'endpoint_terms': len(expected),
        }
        if nregisters == 4:
            reference_calls = calls

    need(reference_calls is not None, 'four-register positive control missing')
    deleted_ok, _, _ = replay(reference_calls[:-1], targets, 4)
    need(not deleted_ok, 'deleted-call control was accepted')

    changed = list(reference_calls)
    nmat, frame = changed[0]
    changed[0] = (nmat, tuple(2 * x for x in frame))
    changed_ok, _, _ = replay(changed, targets, 4)
    need(not changed_ok, 'valid rank-one frame mutation was accepted')

    wrong_targets = (c1, ((1, 1, 0), (1, 1, 0), (0, 0, 1)), c3)
    changed_endpoint_ok, _, _ = replay(reference_calls, wrong_targets, 4)
    need(not changed_endpoint_ok, 'perturbed endpoint control was accepted')

    even_det = ((1, 0, 0), (0, 1, 0), (0, 0, 2))
    even_targets = (c1, c2, even_det)
    even_sum = target_rank_sum(even_targets)
    need(det3_mod2(even_det) == 0 and even_sum == 8,
         'even-determinant boundary should lower the mod-two rank sum')
    even_calls = build_calls(even_targets, 4)
    even_ok, _, _ = replay(even_calls, even_targets, 4)
    need(even_ok, 'even-determinant direct endpoint control')

    # A half-integral entry cannot be cleared by a common odd denominator.
    half = ((Fraction(1, 2), 0, 0), (0, 0, 0), (0, 0, 0))
    try:
        encode_odd_lattice(half, 1)
    except ValueError:
        even_denominator_rejected = True
    else:
        even_denominator_rejected = False
    need(even_denominator_rejected, 'even-denominator scope guard')

    return {
        'status': 'PASS_ODD_DENOMINATOR_AUXILIARY_CALL_FLOOR',
        'model': 'formal F2[q^-1 M3(Z)], q odd; arbitrary rank-one idempotent register projectors and free interleaved GL mixing',
        'cycle_seed': '16c9467a282673c96099aae5db2415a9',
        'base_commit': '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2',
        'selected_record_sha256': '10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32',
        'data_roles': 3,
        'address_dimension': 3,
        'auxiliary_counts_checked': [0, 1, 3],
        'data_target_ranks_mod2': [3, 3, 3],
        'uniform_call_lower_bound': data_rank,
        'positive_call_count': 9,
        'projector_counts_checked': projector_counts,
        'positive_programs': programs,
        'even_determinant_boundary_rank_sum': even_sum,
        'controls': {
            'odd_lattice_additivity': True,
            'all_sampled_idempotents_rank_one': True,
            'free_mixer_rank_preservation': True,
            'deleted_call_rejected': True,
            'valid_rank_one_frame_mutation_rejected': True,
            'perturbed_endpoint_rejected': True,
            'even_determinant_boundary_is_rank_eight': True,
            'half_integral_frame_outside_scope': True,
        },
        'scope': 'Tight mW lower bound for odd-denominator frames and cleared targets invertible modulo two, arbitrary auxiliary count. Even-denominator frames and physical supplier costs are not covered.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    check_pins()
    result = build_receipt()
    text = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.write:
        destination = args.write if args.write.is_absolute() else ROOT / args.write
        with destination.open('x', encoding='utf-8') as handle:
            handle.write(text)
    else:
        expected_path = HERE / 'RESULT.json'
        expected = json.loads(expected_path.read_text())
        need(result == expected, 'recomputed exact receipt differs from RESULT.json')
    print(text, end='')
    print('PASS_ODD_DENOMINATOR_AUXILIARY_CALL_FLOOR')


if __name__ == '__main__':
    main()
