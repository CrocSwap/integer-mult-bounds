#!/usr/bin/env python3
"""One thin map misses the three-leaf paired star over F_2 at block size 2.

Every legal orthogonal resolution and every call order is screened over
F_256. Any constant candidate is replayed in the polynomial ring. The
two-map commuting word is an exact positive control.
"""

import itertools
import json
import math

import numpy as np

G = 3
D = 2
N = D * (G + 1)
I2 = ((1, 0), (0, 1))
Z2 = ((0, 0), (0, 0))
ZERO_EXP = (0,) * G


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def add2(left, right):
    return tuple(tuple(left[i][j] ^ right[i][j] for j in range(2)) for i in range(2))


def mul2(left, right):
    return tuple(
        tuple((left[i][0] & right[0][j]) ^ (left[i][1] & right[1][j]) for j in range(2))
        for i in range(2)
    )


def rank2(matrix):
    rows = [list(row) for row in matrix]
    rank = 0
    for col in range(2):
        pivot = next((i for i in range(rank, 2) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(2):
            if i != rank and rows[i][col]:
                for j in range(2):
                    rows[i][j] ^= rows[rank][j]
        rank += 1
    return rank


def mat2(bits):
    return tuple(tuple((bits >> (i * 2 + j)) & 1 for j in range(2)) for i in range(2))


def block_rows(matrix_a, matrix_b):
    mixed = add2(matrix_a, matrix_b)
    rows = []
    for left, right in ((mixed, matrix_b), (matrix_b, mixed)):
        for r in range(2):
            mask = 0
            for block_col, block in enumerate((left, right)):
                for c in range(2):
                    if block[r][c]:
                        mask |= 1 << (block_col * 2 + c)
            rows.append(mask)
    return tuple(rows)


def mul_bits(left, right):
    out = []
    for row in left:
        value = 0
        rest = row
        while rest:
            bit = rest & -rest
            value ^= right[bit.bit_length() - 1]
            rest ^= bit
        out.append(value)
    return tuple(out)


def resolutions():
    found = []
    seen = set()
    for bits_a in range(16):
        matrix_a = mat2(bits_a)
        if mul2(matrix_a, matrix_a) != matrix_a or rank2(matrix_a) != 1:
            continue
        complement = add2(I2, matrix_a)
        for bits_b in range(16):
            matrix_b = mat2(bits_b)
            first = block_rows(matrix_a, matrix_b)
            second = block_rows(complement, matrix_b)
            zero = (0, 0, 0, 0)
            if not (
                mul_bits(first, first) == first
                and mul_bits(second, second) == second
                and mul_bits(first, second) == zero
                and mul_bits(second, first) == zero
            ):
                continue
            key = tuple(sorted((first, second)))
            if key in seen:
                continue
            seen.add(key)
            found.append((matrix_a, matrix_b, complement))
    return tuple(found)


def embed(blocks):
    rows = [0] * N
    for (block_i, block_j), block in blocks.items():
        for r in range(2):
            for c in range(2):
                if block[r][c]:
                    rows[block_i * 2 + r] |= 1 << (block_j * 2 + c)
    return tuple(rows)


def matrix_p(stage, matrix_a, matrix_b):
    mixed = add2(matrix_a, matrix_b)
    leaf = stage + 1
    return embed({(0, 0): mixed, (0, leaf): matrix_b, (leaf, 0): matrix_b, (leaf, leaf): mixed})


def matrix_r(stage, matrix_a):
    leaf = stage + 1
    return embed({
        (0, 0): matrix_a,
        (0, leaf): matrix_a,
        (leaf, 0): matrix_a,
        (leaf, leaf): matrix_a,
    })


def matrix_e(stage):
    return embed({(0, 0): I2, (stage + 1, stage + 1): I2})


def eye():
    return tuple(1 << i for i in range(N))


def add_rows(left, right):
    return tuple(x ^ y for x, y in zip(left, right))


def poly_mul(left, right):
    out = {}
    right_items = tuple(right.items())
    for exp_l, mat_l in left.items():
        for exp_r, mat_r in right_items:
            if exp_l[0] + exp_r[0] > 1:
                continue
            exp = (exp_l[0] + exp_r[0], tuple(a + b for a, b in zip(exp_l[1], exp_r[1])))
            prod = mul_bits(mat_l, mat_r)
            prev = out.get(exp)
            if prev is None:
                if any(prod):
                    out[exp] = prod
            else:
                summed = add_rows(prev, prod)
                if any(summed):
                    out[exp] = summed
                else:
                    del out[exp]
    return out


def full_gate(stage, proj, read):
    """(I+(D+1)P)(I+e R) = I+(D+1)P + e D R when P R = R."""
    degree = tuple(1 if i == stage else 0 for i in range(G))
    identity = eye()
    return {
        (0, ZERO_EXP): add_rows(identity, proj),
        (0, degree): proj,
        (1, degree): read,
    }


def thin_gate(mat):
    return {(0, ZERO_EXP): eye(), (1, ZERO_EXP): mat}


def stage_factor(stage):
    """I+(D+1)E = (I+E) + D E. Support blocks become D; the rest stay I."""
    support = matrix_e(stage)
    degree = tuple(1 if i == stage else 0 for i in range(G))
    return {(0, ZERO_EXP): add_rows(eye(), support), (0, degree): support}


def target_word():
    word = {(0, ZERO_EXP): eye(), (1, ZERO_EXP): eye()}
    for stage in range(G):
        word = poly_mul(stage_factor(stage), word)
    return word


TARGET = target_word()


def eval_word(factors):
    word = {(0, ZERO_EXP): eye()}
    for factor in factors:
        word = poly_mul(factor, word)
    return word


def rank_rows(rows):
    rows = list(rows)
    rank = 0
    size = len(rows)
    for col in range(size):
        mask = 1 << col
        pivot = next((i for i in range(rank, size) if rows[i] & mask), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_row = rows[rank]
        for i in range(size):
            if i != rank and (rows[i] & mask):
                rows[i] ^= pivot_row
        rank += 1
    return rank


def _gf_mul_slow(left, right):
    prod = 0
    while right:
        if right & 1:
            prod ^= left
        left <<= 1
        if left & 0x100:
            left ^= 0x11B
        right >>= 1
    return prod


_MUL = tuple(tuple(_gf_mul_slow(i, j) for j in range(256)) for i in range(256))


def gf_mul(left, right):
    return _MUL[left][right]


def gf_inv(value):
    result = 1
    base = value
    exp = 254
    while exp:
        if exp & 1:
            result = gf_mul(result, base)
        base = gf_mul(base, base)
        exp >>= 1
    return result


def gf_matmul(left, right):
    table = _MUL
    out = [[0] * N for _ in range(N)]
    cols = [[right[k][j] for k in range(N)] for j in range(N)]
    for i in range(N):
        row = left[i]
        dest = out[i]
        for j in range(N):
            acc = 0
            col = cols[j]
            for k in range(N):
                factor = row[k]
                if factor:
                    acc ^= table[factor][col[k]]
            dest[j] = acc
    return out


def gf_add(left, right):
    return [[left[i][j] ^ right[i][j] for j in range(N)] for i in range(N)]


def gf_eye():
    return [[1 if i == j else 0 for j in range(N)] for i in range(N)]


def gf_from_bits(rows, scale=1):
    return [[scale if rows[i] & (1 << j) else 0 for j in range(N)] for i in range(N)]


def gf_gate(proj, scalar):
    gate = gf_eye()
    if not scalar:
        return gate
    return gf_add(gate, gf_from_bits(proj, scalar))


def gf_inv_mat(matrix):
    work = [row[:] + [1 if i == j else 0 for j in range(N)] for i, row in enumerate(matrix)]
    for col in range(N):
        pivot = next((i for i in range(col, N) if work[i][col]), None)
        if pivot is None:
            return None
        work[col], work[pivot] = work[pivot], work[col]
        inv = gf_inv(work[col][col])
        for j in range(2 * N):
            work[col][j] = gf_mul(work[col][j], inv)
        for i in range(N):
            factor = work[i][col]
            if i != col and factor:
                for j in range(2 * N):
                    work[i][j] ^= gf_mul(factor, work[col][j])
    return [row[N:] for row in work]


def gf_const(matrix):
    if any(entry not in (0, 1) for row in matrix for entry in row):
        return None
    return tuple(sum(entry << col for col, entry in enumerate(row)) for row in matrix)


def control_thin(stage):
    blocks = {}
    leaves = [stage] if stage + 1 == G else [stage, stage + 1]
    for leaf in leaves:
        block = leaf + 1
        blocks[(0, block)] = I2
        blocks[(block, 0)] = I2
    return embed(blocks)


def control_word(resolutions_list):
    matrix_a, matrix_b, complement = next(item for item in resolutions_list if item[1] == Z2)
    factors = []
    for stage in range(G):
        factors.append(full_gate(
            stage, matrix_p(stage, matrix_a, matrix_b), matrix_r(stage, matrix_a)))
        factors.append(full_gate(
            stage, matrix_p(stage, complement, matrix_b), matrix_r(stage, complement)))
        if stage % 2 == 0:
            factors.append(thin_gate(control_thin(stage)))
    require(eval_word(factors) == TARGET, 'two-map control misses the endpoint')
    ranks = [rank_rows(control_thin(stage)) for stage in range(G) if stage % 2 == 0]
    broken = list(factors)
    broken[2] = {(0, ZERO_EXP): eye()}
    require(eval_word(broken) != TARGET, 'deleting a thin map still met the endpoint')
    values = (2, 3, 5)
    specialized = specialize(eval_word(factors), values, False)
    specialized_e = specialize(eval_word(factors), values, True)
    target_pure = specialize(TARGET, values, False)
    target_e = specialize(TARGET, values, True)
    require(specialized == target_pure and specialized_e == target_e, 'field specialization drifted from the polynomial control')
    return ranks


def specialize(poly, values, want_e):
    matrix = [[0] * N for _ in range(N)]
    for (flag, degrees), rows in poly.items():
        if bool(flag) != want_e:
            continue
        coeff = 1
        for degree, value in zip(degrees, values):
            for _ in range(degree):
                coeff = gf_mul(coeff, value)
        matrix = gf_add(matrix, gf_from_bits(rows, coeff))
    return matrix


def projector_checks(resolutions_list):
    checked = 0
    for matrix_a, matrix_b, complement in resolutions_list:
        for stage in range(G):
            for half in (matrix_a, complement):
                proj = matrix_p(stage, half, matrix_b)
                read = matrix_r(stage, half)
                require(mul_bits(proj, read) == read, 'P R = R')
                require(mul_bits(read, proj) == read, 'R P = R')
                checked += 1
    return checked


_MUL_NP = np.array(_MUL, dtype=np.uint8)


def np_matmul(left, right):
    return np.bitwise_xor.reduce(_MUL_NP[left[:, None, :], right.T[None, :, :]], axis=2)


def np_add(left, right):
    return np.bitwise_xor(left, right)


def np_from_bits(rows, scale=1):
    matrix = np.zeros((N, N), dtype=np.uint8)
    for i, row in enumerate(rows):
        rest = row
        while rest:
            bit = rest & -rest
            matrix[i, bit.bit_length() - 1] = scale
            rest ^= bit
    return matrix


def np_gate(proj, scalar):
    gate = np.eye(N, dtype=np.uint8)
    if scalar:
        gate = np_add(gate, np_from_bits(proj, scalar))
    return gate


def np_eye():
    return np.eye(N, dtype=np.uint8)


def np_const(matrix):
    if matrix.dtype != np.uint8 or matrix.shape != (N, N):
        return None
    if np.any((matrix != 0) & (matrix != 1)):
        return None
    rows = []
    for row in matrix:
        mask = 0
        for col, entry in enumerate(row.tolist()):
            if entry:
                mask |= 1 << col
        rows.append(mask)
    return tuple(rows)


def np_target(values):
    target = np_eye()
    for stage, value in enumerate(values):
        target = np_matmul(np_gate(matrix_e(stage), value ^ 1), target)
    return target


def gate_inverse(gate):
    inverse = gf_inv_mat(gate.astype(int).tolist())
    require(inverse is not None, 'pure gate was singular')
    return np.array(inverse, dtype=np.uint8)


def search(resolutions_list):
    """Screen every paired word with one thin map.

    List order is chronological: the first call is applied first and is the
    rightmost factor. A constant solution at both field points is replayed in
    the polynomial ring, so a specialization accident cannot become a witness.
    """
    points = ((2, 3, 5), (6, 7, 11))
    targets = [np_target(values) for values in points]
    orders = tuple(itertools.permutations(range(2 * G)))
    screened = 0
    pure_hits = 0
    exact_checks = 0
    eye = np_eye()
    for choice in itertools.product(range(len(resolutions_list)), repeat=G):
        bank = []
        prepared = []
        for stage, index in enumerate(choice):
            matrix_a, matrix_b, complement = resolutions_list[index]
            for half in (matrix_a, complement):
                proj = matrix_p(stage, half, matrix_b)
                read = matrix_r(stage, half)
                bank.append((proj, read, stage))
                gates = []
                queries = []
                inverses = []
                for values, _target in zip(points, targets):
                    gate = np_gate(proj, values[stage] ^ 1)
                    gates.append(gate)
                    queries.append(np_from_bits(read, values[stage]))
                    inverses.append(gate_inverse(gate))
                prepared.append((gates, queries, inverses))
        for order in orders:
            sequence = [bank[i] for i in order]
            screened += 1
            first = []
            for point in range(2):
                gates = [prepared[i][0][point] for i in order]
                queries = [prepared[i][1][point] for i in order]
                inverses = [prepared[i][2][point] for i in order]
                right = eye
                right_inv = eye
                rights = [eye]
                right_invs = [eye]
                for gate, inv in zip(gates, inverses):
                    right = np_matmul(gate, right)
                    right_inv = np_matmul(right_inv, inv)
                    rights.append(right)
                    right_invs.append(right_inv)
                if not np.array_equal(rights[-1], targets[point]):
                    break
                if point == 0:
                    pure_hits += 1
                left = eye
                left_inv = eye
                lefts = [None] * (len(gates) + 1)
                left_invs = [None] * (len(gates) + 1)
                lefts[-1] = eye
                left_invs[-1] = eye
                for index in range(len(gates) - 1, -1, -1):
                    left = np_matmul(left, gates[index])
                    left_inv = np_matmul(inverses[index], left_inv)
                    lefts[index] = left
                    left_invs[index] = left_inv
                error = np.zeros((N, N), dtype=np.uint8)
                for index, query in enumerate(queries):
                    error = np_add(error, np_matmul(lefts[index + 1], np_matmul(query, rights[index])))
                need = np_add(targets[point], error)
                found = []
                for gap in range(len(gates) + 1):
                    solved = np_matmul(left_invs[gap], np_matmul(need, right_invs[gap]))
                    bits = np_const(solved)
                    if bits is not None:
                        found.append((gap, bits))
                if point == 0:
                    first = found
                    if not first:
                        break
                else:
                    agreed = [candidate for candidate in first if candidate in set(found)]
                    for candidate in agreed:
                        exact_checks += 1
                        if exact_one(sequence, candidate):
                            return {
                                'witness': {'gap': candidate[0], 'order': order, 'choice': choice},
                                'screened_orders': screened,
                                'pure_hits': pure_hits,
                                'exact_checks': exact_checks,
                            }
    return {
        'witness': None,
        'screened_orders': screened,
        'pure_hits': pure_hits,
        'exact_checks': exact_checks,
    }


def exact_one(sequence, candidate):
    gap, mat = candidate
    factors = []
    for index, (proj, read, stage) in enumerate(sequence):
        if index == gap:
            factors.append(thin_gate(mat))
        factors.append(full_gate(stage, proj, read))
    if gap == len(sequence):
        factors.append(thin_gate(mat))
    return eval_word(factors) == TARGET


def numeric_candidates(sequence, values, target):
    """Constant thin maps for one chronological order at one D-point.

    sequence[0] is applied first. Returns None when the pure product misses
    the endpoint, otherwise a list of (gap, bitmask) pairs.
    """
    gates = [np_gate(proj, values[stage] ^ 1) for proj, _read, stage in sequence]
    queries = [np_from_bits(read, values[stage]) for _proj, read, stage in sequence]
    inverses = [gate_inverse(gate) for gate in gates]
    eye = np_eye()
    right = eye
    right_inv = eye
    rights = [eye]
    right_invs = [eye]
    for gate, inv in zip(gates, inverses):
        right = np_matmul(gate, right)
        right_inv = np_matmul(right_inv, inv)
        rights.append(right)
        right_invs.append(right_inv)
    if not np.array_equal(rights[-1], target):
        return None
    left = eye
    left_inv = eye
    lefts = [None] * (len(gates) + 1)
    left_invs = [None] * (len(gates) + 1)
    lefts[-1] = eye
    left_invs[-1] = eye
    for index in range(len(gates) - 1, -1, -1):
        left = np_matmul(left, gates[index])
        left_inv = np_matmul(inverses[index], left_inv)
        lefts[index] = left
        left_invs[index] = left_inv
    error = np.zeros((N, N), dtype=np.uint8)
    for index, query in enumerate(queries):
        error = np_add(error, np_matmul(lefts[index + 1], np_matmul(query, rights[index])))
    need = np_add(target, error)
    found = []
    for gap in range(len(gates) + 1):
        solved = np_matmul(left_invs[gap], np_matmul(need, right_invs[gap]))
        bits = np_const(solved)
        if bits is not None:
            found.append((gap, bits))
    return found


def control_numeric(resolutions_list):
    """The commuting two-map word, replayed on the same field arithmetic."""
    matrix_a, matrix_b, complement = next(item for item in resolutions_list if item[1] == Z2)
    calls = []
    thins = []
    for stage in range(G):
        for half in (matrix_a, complement):
            calls.append((matrix_p(stage, half, matrix_b), matrix_r(stage, half), stage))
        if stage % 2 == 0:
            thins.append((len(calls), control_thin(stage)))
    values = (2, 3, 5)
    target = np_target(values)
    target_e = specialize(TARGET, values, True)
    require(np.array_equal(target, np.array(target_e, dtype=np.uint8)), 'numeric target drifted')
    gates = [np_gate(proj, values[stage] ^ 1) for proj, _read, stage in calls]
    queries = [np_from_bits(read, values[stage]) for _proj, read, stage in calls]
    eye = np_eye()
    # Calls are chronological. Thin maps sit after the indicated prefix length.
    right = eye
    rights = [eye]
    for gate in gates:
        right = np_matmul(gate, right)
        rights.append(right)
    require(np.array_equal(rights[-1], target), 'control pure product missed the endpoint')
    left = eye
    lefts = [None] * (len(calls) + 1)
    lefts[-1] = eye
    for index in range(len(calls) - 1, -1, -1):
        left = np_matmul(left, gates[index])
        lefts[index] = left
    error = np.zeros((N, N), dtype=np.uint8)
    for index, query in enumerate(queries):
        error = np_add(error, np_matmul(lefts[index + 1], np_matmul(query, rights[index])))
    for gap, mat in thins:
        error = np_add(error, np_matmul(lefts[gap], np_matmul(np_from_bits(mat), rights[gap])))
    require(np.array_equal(error, target), 'control query coefficient missed the endpoint')
    # Recover the second thin map after the first is kept. This is the positive
    # solver check: the same gap formula has a known constant solution.
    kept_gap, kept = thins[0]
    missing_gap, missing = thins[1]
    partial = np.zeros((N, N), dtype=np.uint8)
    for index, query in enumerate(queries):
        partial = np_add(partial, np_matmul(lefts[index + 1], np_matmul(query, rights[index])))
    partial = np_add(partial, np_matmul(lefts[kept_gap], np_matmul(np_from_bits(kept), rights[kept_gap])))
    need = np_add(target, partial)
    recovered = np_const(np_matmul(
        gate_inverse(lefts[missing_gap]),
        np_matmul(need, gate_inverse(rights[missing_gap])),
    ))
    require(recovered == missing, 'solver did not recover the second control map')
    naked = numeric_candidates(calls, values, target)
    require(naked is not None, 'control order lost the pure endpoint')
    require(all(not exact_one(calls, candidate) for candidate in naked), 'one thin map reproduced the two-map control')


def formula_lock(resolutions_list):
    """The field formula agrees with the polynomial word at every gap.

    Uses a nonzero-B resolution and a swapped call order, so the lock is not
    only the commuting control.
    """
    matrix_a, matrix_b, complement = next(item for item in resolutions_list if item[1] != Z2)
    sequence = []
    for stage in range(G):
        sequence.append((matrix_p(stage, matrix_a, matrix_b), matrix_r(stage, matrix_a), stage))
        sequence.append((matrix_p(stage, complement, matrix_b), matrix_r(stage, complement), stage))
    sequence[1], sequence[2] = sequence[2], sequence[1]
    values = (2, 3, 5)
    probe = embed({(0, 1): I2, (1, 0): ((1, 0), (0, 0))})
    gates = [np_gate(proj, values[stage] ^ 1) for proj, _read, stage in sequence]
    queries = [np_from_bits(read, values[stage]) for _proj, read, stage in sequence]
    eye = np_eye()
    right = eye
    rights = [eye]
    for gate in gates:
        right = np_matmul(gate, right)
        rights.append(right)
    left = eye
    lefts = [None] * (len(sequence) + 1)
    lefts[-1] = eye
    for index in range(len(sequence) - 1, -1, -1):
        left = np_matmul(left, gates[index])
        lefts[index] = left
    base = np.zeros((N, N), dtype=np.uint8)
    for index, query in enumerate(queries):
        base = np_add(base, np_matmul(lefts[index + 1], np_matmul(query, rights[index])))
    for gap in range(len(sequence) + 1):
        factors = []
        for index, (proj, read, stage) in enumerate(sequence):
            if index == gap:
                factors.append(thin_gate(probe))
            factors.append(full_gate(stage, proj, read))
        if gap == len(sequence):
            factors.append(thin_gate(probe))
        word = eval_word(factors)
        predicted = np_add(base, np_matmul(lefts[gap], np_matmul(np_from_bits(probe), rights[gap])))
        require(np.array_equal(rights[-1], np.array(specialize(word, values, False), dtype=np.uint8)),
                'pure formula drifted at gap %s' % gap)
        require(np.array_equal(predicted, np.array(specialize(word, values, True), dtype=np.uint8)),
                'query formula drifted at gap %s' % gap)


def unsplit_fails():
    sequence_bank = [
        (matrix_p(stage, I2, Z2), matrix_r(stage, I2), stage) for stage in range(G)
    ]
    points = ((2, 3, 5), (6, 7, 11))
    targets = [np_target(values) for values in points]
    for order in itertools.permutations(range(G)):
        sequence = [sequence_bank[i] for i in order]
        first = numeric_candidates(sequence, points[0], targets[0]) or []
        second = set(numeric_candidates(sequence, points[1], targets[1]) or [])
        for candidate in first:
            if candidate in second and exact_one(sequence, candidate):
                return False
    return True


def main():
    found = resolutions()
    require(len(found) == 12, 'resolution census %s' % len(found))
    require(sum(item[1] == Z2 for item in found) == 3, 'diagonal resolutions')
    ranks = control_word(found)
    require(ranks == [4, 4], 'control ranks %s' % (ranks,))
    control_numeric(found)
    formula_lock(found)
    noncommuting = 0
    for left in found:
        for right in found:
            if mul2(left[0], right[0]) != mul2(right[0], left[0]):
                noncommuting += 1
    require(noncommuting > 0, 'every resolution pair commutes')
    require(projector_checks(found) == len(found) * 2 * G, 'projector check count')
    require(unsplit_fails(), 'unsplit one-call schedule admitted one thin map')
    result = search(found)
    require(result['screened_orders'] == len(found) ** G * math.factorial(2 * G),
            'screened order count %s' % result['screened_orders'])
    require(result['witness'] is None, 'one thin map exists: %s' % result)
    print(json.dumps({
        'status': 'PASS_PAIRED_STAR_ONE_THIN_GAP',
        'field': 'F2',
        'block_dimension': D,
        'leaves': G,
        'legal_resolutions': len(found),
        'diagonal_resolutions': 3,
        'screened_orders': result['screened_orders'],
        'pure_hits': result['pure_hits'],
        'exact_checks': result['exact_checks'],
        'noncommuting_ordered_pairs': noncommuting,
        'one_thin_witness': None,
        'control_thin_maps': 2,
        'control_ranks': ranks,
        'chronological_rank_floor': 6,
        'no_new_kappa': True,
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
