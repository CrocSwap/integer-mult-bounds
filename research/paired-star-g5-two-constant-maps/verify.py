#!/usr/bin/env python3
"""Two constant thin maps miss one g=5 paired-star word at q=1.

The fixed legal pair and the identity stage order are the named first step
from PR #7090. Checks raise SystemExit, so python -O does not strip them.
"""

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = 5
D = 2
MOD = 0x11B
I2 = ((1, 0), (0, 1))
Z2 = ((0, 0), (0, 0))
A = ((1, 0), (0, 0))
B = ((0, 1), (0, 0))
AP = ((0, 0), (0, 1))
POINTS = ((2, 3, 5, 6, 7), (6, 7, 11, 13, 14))
SEPARATING_GAPS = (1, 3, 5, 7, 9)

MUL = [0] * (256 * 256)
for _a in range(256):
    for _b in range(256):
        _p = 0
        _aa, _bb = _a, _b
        while _bb:
            if _bb & 1:
                _p ^= _aa
            _bb >>= 1
            _aa <<= 1
            if _aa & 0x100:
                _aa ^= MOD
        MUL[_a * 256 + _b] = _p
INV = [0] * 256
for _a in range(1, 256):
    for _b in range(1, 256):
        if MUL[_a * 256 + _b] == 1:
            INV[_a] = _b
            break


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def mul(a, b):
    return MUL[a * 256 + b]


def add2(left, right):
    return tuple(tuple(left[i][j] ^ right[i][j] for j in range(2)) for i in range(2))


def mul2(left, right):
    return tuple(
        tuple((left[i][0] & right[0][j]) ^ (left[i][1] & right[1][j]) for j in range(2))
        for i in range(2)
    )


def n_of(g):
    return D * (g + 1)


def zeros_exp(g):
    return tuple(0 for _ in range(g))


def unit_exp(stage, g):
    return tuple(1 if i == stage else 0 for i in range(g))


def eye_bits(n):
    return tuple(1 << i for i in range(n))


def embed_bits(blocks, n):
    rows = [0] * n
    for (bi, bj), block in blocks.items():
        for r in range(2):
            for c in range(2):
                if block[r][c]:
                    rows[bi * 2 + r] |= 1 << (bj * 2 + c)
    return tuple(rows)


def bits_add(left, right):
    return tuple(x ^ y for x, y in zip(left, right))


def bits_mul(left, right):
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


def bits_eq(left, right):
    return left == right


def rank_bits(rows):
    active = [row for row in rows if row]
    rank = 0
    while active:
        pivot = active[0]
        bit = pivot & -pivot
        rank += 1
        nxt = []
        for row in active[1:]:
            if row & bit:
                row ^= pivot
            if row:
                nxt.append(row)
        active = nxt
    return rank


def matrix_p(stage, matrix_a, matrix_b, g):
    mixed = add2(matrix_a, matrix_b)
    leaf = stage + 1
    return embed_bits(
        {(0, 0): mixed, (0, leaf): matrix_b, (leaf, 0): matrix_b, (leaf, leaf): mixed},
        n_of(g),
    )


def matrix_r(stage, matrix_a, g):
    leaf = stage + 1
    return embed_bits(
        {(0, 0): matrix_a, (0, leaf): matrix_a, (leaf, 0): matrix_a, (leaf, leaf): matrix_a},
        n_of(g),
    )


def matrix_e(stage, g):
    return embed_bits({(0, 0): I2, (stage + 1, stage + 1): I2}, n_of(g))


def matrix_t(stage, g):
    leaf = stage + 1
    return embed_bits(
        {(0, 0): I2, (0, leaf): I2, (leaf, 0): I2, (leaf, leaf): I2},
        n_of(g),
    )


def k_matrix(g):
    acc = eye_bits(n_of(g))
    for stage in range(g):
        acc = bits_add(acc, matrix_t(stage, g))
    return acc


def poly_add(left, right):
    out = dict(left)
    for exp, mat in right.items():
        prev = out.get(exp)
        if prev is None:
            if any(mat):
                out[exp] = mat
        else:
            summed = bits_add(prev, mat)
            if any(summed):
                out[exp] = summed
            else:
                del out[exp]
    return out


def poly_mul(left, right):
    out = {}
    for exp_l, mat_l in left.items():
        for exp_r, mat_r in right.items():
            exp = tuple(a + b for a, b in zip(exp_l, exp_r))
            prod = bits_mul(mat_l, mat_r)
            prev = out.get(exp)
            if prev is None:
                if any(prod):
                    out[exp] = prod
            else:
                summed = bits_add(prev, prod)
                if any(summed):
                    out[exp] = summed
                else:
                    del out[exp]
    return out


def word_mul(left, right):
    """Dual-number product. Each factor is (pure dict, e dict)."""
    pure = poly_mul(left[0], right[0])
    e_part = poly_add(poly_mul(left[0], right[1]), poly_mul(left[1], right[0]))
    return pure, e_part


def full_factor(proj, read, stage, g):
    """(I+(D+1)P)(I+e R) = (I+P)+D P + e D R when P R = R."""
    zero = zeros_exp(g)
    degree = unit_exp(stage, g)
    pure = {zero: bits_add(eye_bits(n_of(g)), proj), degree: proj}
    return pure, {degree: read}


def thin_factor(mat, g):
    return {zeros_exp(g): eye_bits(n_of(g))}, {zeros_exp(g): mat}


def stage_factor(stage, g):
    support = matrix_e(stage, g)
    zero = zeros_exp(g)
    degree = unit_exp(stage, g)
    return {zero: bits_add(eye_bits(n_of(g)), support), degree: support}, {}


def target_word(g):
    word = thin_factor(eye_bits(n_of(g)), g)
    for stage in range(g):
        word = word_mul(stage_factor(stage, g), word)
    return word


def eval_calls(calls, maps, g):
    """Chronological calls. maps[gap] is inserted before that many calls have been applied."""
    word = ({zeros_exp(g): eye_bits(n_of(g))}, {})
    placed = set()
    for index, (proj, read, stage) in enumerate(calls):
        mat = maps.get(index)
        if mat is not None:
            word = word_mul(thin_factor(mat, g), word)
            placed.add(index)
        word = word_mul(full_factor(proj, read, stage, g), word)
    if len(calls) in maps:
        word = word_mul(thin_factor(maps[len(calls)], g), word)
        placed.add(len(calls))
    require(placed == set(maps), 'a thin map was not placed')
    return word


def calls_from(assignments, order, g):
    calls = []
    for stage, half in order:
        matrix_a, matrix_b, complement = assignments[stage]
        block = matrix_a if half == 0 else complement
        calls.append((matrix_p(stage, block, matrix_b, g), matrix_r(stage, block, g), stage))
    return calls


def odd_pair():
    return (A, B, AP)


def diag_pair():
    return (A, Z2, AP)


def identity_order(g):
    return [(stage, half) for stage in range(g) for half in (0, 1)]


def sharp_maps(g):
    maps = {}
    for stage in range(0, g, 2):
        blocks = {}
        leaves = [stage] if stage + 1 == g else [stage, stage + 1]
        for leaf in leaves:
            block = leaf + 1
            blocks[(0, block)] = I2
            blocks[(block, 0)] = I2
        maps[2 * (stage + 1)] = embed_bits(blocks, n_of(g))
    return maps


def specialize(poly, values):
    n = None
    acc = None
    for exp, mat in poly.items():
        if n is None:
            n = len(mat)
            acc = tuple(tuple(0 for _ in range(n)) for _ in range(n))
        scale = 1
        for power, value in zip(exp, values):
            for _ in range(power):
                scale = mul(scale, value)
        if scale == 0:
            continue
        scaled = []
        for row in mat:
            out_row = [0] * n
            rest = row
            while rest:
                bit = rest & -rest
                out_row[bit.bit_length() - 1] = scale
                rest ^= bit
            scaled.append(out_row)
        acc = tuple(
            tuple(acc[i][j] ^ scaled[i][j] for j in range(n))
            for i in range(n)
        )
    require(acc is not None, 'empty polynomial')
    return acc


def gf_eye(n):
    return tuple(tuple(1 if i == j else 0 for j in range(n)) for i in range(n))


def gf_from_bits(rows, scalar=1):
    n = len(rows)
    out = [[0] * n for _ in range(n)]
    for i, row in enumerate(rows):
        rest = row
        while rest:
            bit = rest & -rest
            out[i][bit.bit_length() - 1] = scalar
            rest ^= bit
    return tuple(tuple(row) for row in out)


def gf_add(left, right):
    return tuple(tuple(a ^ b for a, b in zip(u, v)) for u, v in zip(left, right))


def gf_mul(left, right):
    n = len(left)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        li = left[i]
        oi = out[i]
        for k in range(n):
            aik = li[k]
            if not aik:
                continue
            base = aik * 256
            rk = right[k]
            for j in range(n):
                if rk[j]:
                    oi[j] ^= MUL[base + rk[j]]
    return tuple(tuple(row) for row in out)


def gf_gate(proj_bits, scalar):
    n = len(proj_bits)
    gate = [list(row) for row in gf_eye(n)]
    if scalar:
        for i, row in enumerate(proj_bits):
            rest = row
            while rest:
                bit = rest & -rest
                gate[i][bit.bit_length() - 1] ^= scalar
                rest ^= bit
    return tuple(tuple(row) for row in gate)


def prepare(calls, values, g):
    n = n_of(g)
    gates = []
    queries = []
    for proj, read, stage in calls:
        gates.append(gf_gate(proj, values[stage] ^ 1))
        queries.append(gf_from_bits(read, values[stage]))
    eye = gf_eye(n)
    right = eye
    rights = [eye]
    for gate in gates:
        right = gf_mul(gate, right)
        rights.append(right)
    target = gf_eye(n)
    for stage, value in enumerate(values):
        target = gf_mul(gf_gate(matrix_e(stage, g), value ^ 1), target)
    if rights[-1] != target:
        return None
    lefts = [None] * (len(gates) + 1)
    lefts[-1] = eye
    left = eye
    for index in range(len(gates) - 1, -1, -1):
        left = gf_mul(left, gates[index])
        lefts[index] = left
    error = tuple(tuple(0 for _ in range(n)) for _ in range(n))
    for index, query in enumerate(queries):
        error = gf_add(error, gf_mul(lefts[index + 1], gf_mul(query, rights[index])))
    return gf_add(target, error), lefts, rights


def eliminate(aug, unknowns):
    rows = len(aug)
    rank = 0
    row = 0
    for col in range(unknowns):
        pivot = next((i for i in range(row, rows) if aug[i][col]), None)
        if pivot is None:
            continue
        aug[row], aug[pivot] = aug[pivot], aug[row]
        inv_p = INV[aug[row][col]]
        if inv_p != 1:
            for j in range(col, unknowns + 1):
                aug[row][j] = MUL[aug[row][j] * 256 + inv_p]
        rowc = aug[row]
        for i in range(rows):
            factor = aug[i][col]
            if i != row and factor:
                rowi = aug[i]
                base = factor * 256
                for j in range(col, unknowns + 1):
                    rowi[j] ^= MUL[base + rowc[j]]
        row += 1
        rank += 1
    for i in range(rank, rows):
        if aug[i][unknowns]:
            return False, rank
    return True, rank


def gap_inconsistent(calls, values_list, g):
    """Every pair of gaps is inconsistent for Z2 = K + Z1."""
    preps = []
    for values in values_list:
        prepared = prepare(calls, values, g)
        require(prepared is not None, 'pure product missed at %s' % (values,))
        preps.append(prepared)
    n = n_of(g)
    unknowns = n * n
    kmat = gf_from_bits(k_matrix(g))
    gaps = len(preps[0][2])
    inconsistent = 0
    separating = 0
    for g1, g2 in itertools.combinations(range(gaps), 2):
        aug = []
        for need, lefts, rights in preps:
            l1, r1 = lefts[g1], rights[g1]
            l2, r2 = lefts[g2], rights[g2]
            rhs = gf_add(need, gf_mul(l2, gf_mul(kmat, r2)))
            rows = [[0] * (unknowns + 1) for _ in range(unknowns)]
            for a in range(n):
                for b_index in range(n):
                    col = a * n + b_index
                    r1b = r1[b_index]
                    r2b = r2[b_index]
                    for i in range(n):
                        c1 = l1[i][a]
                        c2 = l2[i][a]
                        if not c1 and not c2:
                            continue
                        b1 = c1 * 256
                        b2 = c2 * 256
                        for j in range(n):
                            coeff = 0
                            if c1 and r1b[j]:
                                coeff ^= MUL[b1 + r1b[j]]
                            if c2 and r2b[j]:
                                coeff ^= MUL[b2 + r2b[j]]
                            if coeff:
                                rows[i * n + j][col] = coeff
            for i in range(n):
                ri = rhs[i]
                for j in range(n):
                    rows[i * n + j][unknowns] = ri[j]
            aug.extend(rows)
        ok, _rank = eliminate(aug, unknowns)
        require(not ok, 'gap pair %s,%s admitted a constant solution' % (g1, g2))
        inconsistent += 1
        if g1 in SEPARATING_GAPS or g2 in SEPARATING_GAPS:
            separating += 1
    return inconsistent, separating


def legal_pair_checks():
    require(mul2(A, A) == A and mul2(AP, AP) == AP, 'halves are not idempotent')
    require(add2(A, AP) == I2, 'halves do not resolve I')
    require(add2(mul2(A, B), mul2(B, A)) == B, 'B is not a commutator fixpoint')
    # Rank-1 idempotent: image is one dimensional.
    require(A != Z2 and A != I2 and AP != Z2, 'halves are not rank one')
    for stage in range(G):
        for block, read_block in ((A, A), (AP, AP)):
            proj = matrix_p(stage, block, B, G)
            read = matrix_r(stage, read_block, G)
            require(bits_mul(proj, proj) == proj, 'local projector failed')
            require(bits_mul(proj, read) == read and bits_mul(read, proj) == read, 'P R = R failed')
    proj = matrix_p(0, A, B, G)
    other = matrix_p(0, AP, B, G)
    require(bits_mul(proj, other) == bits_mul(other, proj) == tuple(0 for _ in range(n_of(G))),
            'halves are not complementary')
    require(bits_add(proj, other) == matrix_e(0, G), 'halves do not sum to E')
    p0 = matrix_p(0, A, B, G)
    p1 = matrix_p(1, A, B, G)
    require(bits_mul(p0, p1) != bits_mul(p1, p0), 'stage projectors commute')


def lemma1():
    """(I+x P')(I+x P) = I+x E inside the g=5 space, both half orders."""
    g = G
    p = matrix_p(0, A, B, g)
    pp = matrix_p(0, AP, B, g)
    e = matrix_e(0, g)
    eye = eye_bits(n_of(g))
    degree = unit_exp(0, g)
    zero = zeros_exp(g)

    def gate(proj):
        return {zero: bits_add(eye, proj), degree: proj}

    def pack(constant, linear):
        out = {}
        if any(constant):
            out[zero] = constant
        if any(linear):
            out[degree] = linear
        return out

    target = pack(bits_add(eye, e), e)
    require(poly_mul(gate(pp), gate(p)) == target, 'P-then-P-prime missed I+x E')
    require(poly_mul(gate(p), gate(pp)) == target, 'P-prime-then-P missed I+x E')
    require(bits_add(matrix_r(0, A, g), matrix_r(0, AP, g)) == matrix_t(0, g),
            'queries do not sum to T')
    for left, right in itertools.combinations(range(g), 2):
        e_left = matrix_e(left, g)
        e_right = matrix_e(right, g)
        require(bits_mul(e_left, e_right) == bits_mul(e_right, e_left),
                'stage supports do not commute')


def two_stage_census():
    g = 2
    labels = [(0, 0), (0, 1), (1, 0), (1, 1)]
    pair = odd_pair()
    hits = []
    for perm in itertools.permutations(labels):
        calls = calls_from((pair, pair), perm, g)
        prepared = prepare(calls, (2, 3), g)
        if prepared is not None:
            hits.append(perm)
    adjacent = []
    for perm in itertools.permutations(labels):
        pos = {}
        for index, (stage, _half) in enumerate(perm):
            pos.setdefault(stage, []).append(index)
        if all(indexes[1] - indexes[0] == 1 for indexes in pos.values()):
            adjacent.append(perm)
    require(len(list(itertools.permutations(labels))) == 24, 'two-stage order count')
    require(len(adjacent) == 8, 'adjacent two-stage count %s' % len(adjacent))
    require(len(hits) == 8 and set(hits) == set(adjacent),
            'two-stage pure hits %s are not exactly the adjacent orders' % len(hits))
    sample = calls_from((pair, pair), adjacent[0], g)
    sample_pure, _sample_e = eval_calls(sample, {}, g)
    require(sample_pure == target_word(g)[0], 'an adjacent two-stage order missed the polynomial')
    # One explicit separated order fails as a polynomial, not only at one point.
    separated = [(0, 0), (1, 0), (0, 1), (1, 1)]
    calls = calls_from((pair, pair), separated, g)
    pure, _e = eval_calls(calls, {}, g)
    require(pure != target_word(g)[0], 'separated two-stage pure product matched')
    return len(hits)


def formula_lock(calls, g):
    """One probe thin map: the field formula matches the specialized polynomial."""
    values = POINTS[0][:g] if g == G else (2, 3, 5)[:g]
    probe = embed_bits({(0, 1): I2}, n_of(g))
    word = eval_calls(calls, {1: probe}, g)
    prepared = prepare(calls, values, g)
    require(prepared is not None, 'formula lock lost the pure endpoint')
    need, lefts, rights = prepared
    predicted = gf_add(need, gf_mul(lefts[1], gf_mul(gf_from_bits(probe), rights[1])))
    # need = target + full_sum, so target_e = full_sum + L Z R means
    # specialized e = (target + need) + L Z R = L Z R + full_sum.
    # predicted above is need + L Z R = target + full_sum + L Z R.
    # The specialized e coefficient should equal full_sum + L Z R = predicted + target,
    # because need = target + full_sum, so full_sum = need + target,
    # full_sum + LZR = need + target + LZR = predicted + target.
    target = specialize(target_word(g)[0], values)
    specialized_e = specialize(word[1], values)
    specialized_pure = specialize(word[0], values)
    require(specialized_pure == specialize(target_word(g)[0], values), 'pure specialization drifted')
    expect = gf_add(predicted, target)
    require(specialized_e == expect, 'gap formula drifted from the polynomial word')


def sharp_control(g, pair):
    order = identity_order(g)
    calls = calls_from((pair,) * g, order, g)
    maps = sharp_maps(g)
    word = eval_calls(calls, maps, g)
    target = target_word(g)
    require(word == target, 'sharp word missed the endpoint at g=%s' % g)
    ranks = [rank_bits(maps[gap]) for gap in sorted(maps)]
    # Drop the last map. The pure product is unchanged and the e coefficient moves.
    last = max(maps)
    broken = dict(maps)
    del broken[last]
    broken_word = eval_calls(calls, broken, g)
    require(broken_word[0] == target[0] and broken_word[1] != target[1],
            'deleting a sharp map still met the endpoint')
    return ranks


def g3_formula_accepts_control():
    g = 3
    calls = calls_from((odd_pair(),) * g, identity_order(g), g)
    maps = sharp_maps(g)
    require(eval_calls(calls, maps, g) == target_word(g), 'g=3 control missed the endpoint')
    values = (2, 3, 5)
    prepared = prepare(calls, values, g)
    require(prepared is not None, 'g=3 control lost the pure endpoint')
    need, lefts, rights = prepared
    gaps = sorted(maps)
    require(gaps == [2, 6], 'g=3 control gaps %s' % gaps)
    z1 = gf_from_bits(maps[gaps[0]])
    z2 = gf_from_bits(maps[gaps[1]])
    kmat = gf_from_bits(k_matrix(g))
    require(gf_add(z1, z2) == kmat, 'g=3 control maps do not sum to K')
    total = gf_mul(lefts[gaps[0]], gf_mul(z1, rights[gaps[0]]))
    total = gf_add(total, gf_mul(lefts[gaps[1]], gf_mul(z2, rights[gaps[1]])))
    require(total == need, 'g=3 control missed the two-gap formula')


def sigma_order():
    """Stage 0 uses the diagonal pair and is separated by stage 1's adjacent block."""
    order = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for stage in range(2, G):
        order.extend([(stage, 0), (stage, 1)])
    assignments = (diag_pair(), odd_pair(), odd_pair(), odd_pair(), odd_pair())
    return assignments, order


def selected_kappa():
    path = ROOT / 'certificates' / 'selected-result.json'
    record = json.loads(path.read_text(encoding='utf-8'))
    require(record['kappa'] == '363005817/100000000000', 'selected kappa changed')
    require(record['decimal'] == '0.00363005817', 'selected decimal changed')


def main():
    selected_kappa()
    legal_pair_checks()
    lemma1()
    two_hits = two_stage_census()
    # Identity order, one fixed nonzero pair: pure product matches, every two-gap
    # system is inconsistent, including every gap that separates a stage.
    calls = calls_from((odd_pair(),) * G, identity_order(G), G)
    pure, _e = eval_calls(calls, {}, G)
    require(pure == target_word(G)[0], 'identity order missed the pure endpoint')
    formula_lock(calls, G)
    inconsistent, separating = gap_inconsistent(calls, POINTS, G)
    require(inconsistent == 55, 'gap pair count %s' % inconsistent)
    require(separating == 40, 'separating gap-pair count %s' % separating)
    ranks = sharp_control(G, odd_pair())
    require(ranks == [4, 4, 4], 'sharp ranks %s' % ranks)
    g3_formula_accepts_control()
    # A foreign call between halves of this same pair misses the pure product.
    separated = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for stage in range(2, G):
        separated.extend([(stage, 0), (stage, 1)])
    foreign = calls_from((odd_pair(),) * G, separated, G)
    foreign_pure, _e = eval_calls(foreign, {}, G)
    require(foreign_pure != target_word(G)[0], 'foreign separation matched the pure endpoint')
    # D=1 makes a gate the identity, so the other stages drop out of the pure product.
    require(gf_gate(matrix_p(2, A, B, G), 0) == gf_eye(n_of(G)), 'a D=1 gate was not I')
    foreign_at_one = specialize(foreign_pure, (2, 3, 1, 1, 1))
    foreign_target = specialize(target_word(G)[0], (2, 3, 1, 1, 1))
    require(foreign_at_one != foreign_target, 'D=1 quotient of a separated word matched')
    # One mixed order whose pure product does match, and which separates stage 0
    # by a foreign block. Every two-gap system is inconsistent there too.
    assignments, order = sigma_order()
    diagonal_stage = matrix_p(0, A, Z2, G)
    nonzero_stage = matrix_p(1, A, B, G)
    require(bits_mul(diagonal_stage, nonzero_stage) != bits_mul(nonzero_stage, diagonal_stage),
            'mixed stage projectors commute')
    sigma = calls_from(assignments, order, G)
    sigma_pure, _e = eval_calls(sigma, {}, G)
    require(sigma_pure == target_word(G)[0], 'mixed separating order missed the pure endpoint')
    sigma_inconsistent, sigma_separating = gap_inconsistent(sigma, POINTS, G)
    require(sigma_inconsistent == 55 and sigma_separating == 40,
            'mixed gap counts %s %s' % (sigma_inconsistent, sigma_separating))
    # The opposite wrap, nonzero pair on the outside, misses the pure product.
    swapped = calls_from((odd_pair(), diag_pair(), diag_pair(), diag_pair(), diag_pair()), order, G)
    swapped_pure, _e = eval_calls(swapped, {}, G)
    require(swapped_pure != target_word(G)[0], 'swapped wrap matched the pure endpoint')
    print(json.dumps({
        'status': 'PASS_PAIRED_STAR_G5_TWO_CONSTANT_MAPS',
        'evidence_class': 'proof',
        'leaves': G,
        'ports': 1,
        'two_stage_orders': 24,
        'two_stage_pure_hits': two_hits,
        'identity_gap_pairs': inconsistent,
        'identity_separating_gap_pairs': separating,
        'mixed_gap_pairs': sigma_inconsistent,
        'sharp_ranks': ranks,
        'field_points': [list(point) for point in POINTS],
        'selected_kappa': '363005817/100000000000',
        'no_new_kappa': True,
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
