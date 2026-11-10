#!/usr/bin/env python3
"""Three F_2 thin maps meet total rank 6 on the three-leaf paired star.

The check multiplies one explicit word in F_2[D0, D1, D2, e] / (e^2).
Failures are raised, so python -O still fails closed. This is a witness,
not a census of other words.
"""

import sys

G = 3
N = 8
I2 = ((1, 0), (0, 1))


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


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


def bits_of(matrix):
    bits = 0
    for i in range(2):
        for j in range(2):
            if matrix[i][j]:
                bits |= 1 << (2 * i + j)
    return bits


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
            found.append((matrix_a, matrix_b, complement, first, second))
    return tuple(found)


def mon(exp):
    return exp[0] * 9 + exp[1] * 3 + exp[2]


def pmul(left, right):
    out = 0
    rest = right
    while rest:
        b = (rest & -rest).bit_length() - 1
        exp_b = (b // 9, (b // 3) % 3, b % 3)
        scan = left
        while scan:
            c = (scan & -scan).bit_length() - 1
            exp = (c // 9 + exp_b[0], (c // 3) % 3 + exp_b[1], c % 3 + exp_b[2])
            require(max(exp) <= 2, "polynomial degree exceeded (2, 2, 2)")
            out ^= 1 << mon(exp)
            scan ^= 1 << c
        rest ^= 1 << b
    return out


def eye():
    return tuple(tuple(1 if i == j else 0 for j in range(N)) for i in range(N))


def zero():
    return tuple(tuple(0 for _ in range(N)) for _ in range(N))


def matmul(left, right):
    out = [0] * N
    for i in range(N):
        row = [0] * N
        for k in range(N):
            if not left[i][k]:
                continue
            for j in range(N):
                if right[k][j]:
                    row[j] ^= pmul(left[i][k], right[k][j])
        out[i] = tuple(row)
    return tuple(out)


def add(left, right):
    return tuple(tuple(left[i][j] ^ right[i][j] for j in range(N)) for i in range(N))


def scale_rows(rows, poly):
    out = []
    for i in range(N):
        out.append(tuple(poly if (rows[i] >> j) & 1 else 0 for j in range(N)))
    return tuple(out)


def embed(cc, cl, lc, ll, leaf):
    rows = [0] * N
    for r in range(2):
        for c in range(2):
            if (cc >> (2 * r + c)) & 1:
                rows[r] |= 1 << c
            if (cl >> (2 * r + c)) & 1:
                rows[r] |= 1 << (2 * leaf + c)
            if (lc >> (2 * r + c)) & 1:
                rows[2 * leaf + r] |= 1 << c
            if (ll >> (2 * r + c)) & 1:
                rows[2 * leaf + r] |= 1 << (2 * leaf + c)
    return tuple(rows)


def projector_rows(matrix_a, matrix_b, leaf):
    mixed = add2(matrix_a, matrix_b)
    return embed(bits_of(mixed), bits_of(matrix_b), bits_of(matrix_b), bits_of(mixed), leaf)


def read_rows(matrix_a, leaf):
    bits = bits_of(matrix_a)
    return embed(bits, bits, bits, bits, leaf)


def support_rows(stage):
    rows = [0] * N
    rows[0] = 1
    rows[1] = 2
    leaf = stage + 1
    rows[2 * leaf] = 1 << (2 * leaf)
    rows[2 * leaf + 1] = 1 << (2 * leaf + 1)
    return tuple(rows)


def unit(stage):
    exp = [0, 0, 0]
    exp[stage] = 1
    return tuple(exp)


def scalar_x(stage):
    """x_j = 1 + D_j."""
    return 1 ^ (1 << mon(unit(stage)))


def scalar_d(stage):
    return 1 << mon(unit(stage))


def left_mul(pure, ecoeff, factor_pure, factor_e):
    return (
        matmul(factor_pure, pure),
        add(matmul(factor_pure, ecoeff), matmul(factor_e, pure)),
    )


def rank8(rows):
    active = [row for row in rows if row]
    rank = 0
    for col in range(N):
        mask = 1 << col
        pivot = next((i for i in range(rank, len(active)) if active[i] & mask), None)
        if pivot is None:
            continue
        active[rank], active[pivot] = active[pivot], active[rank]
        for i in range(len(active)):
            if i != rank and active[i] & mask:
                active[i] ^= active[rank]
        rank += 1
    return rank


def target():
    pure = eye()
    for stage in range(G):
        pure = matmul(add(eye(), scale_rows(support_rows(stage), scalar_x(stage))), pure)
    return pure


def evaluate(stage_res, order, thin):
    """Chronological order: the first call is the rightmost factor.

    Gap g sits before call g. Gap 6 sits after the last call. A full call is
    (I + x P)(I + e R) = I + x P + e D R, using P R = R and x = 1 + D.
    """
    pure = eye()
    ecoeff = zero()
    seen = [0, 0, 0]
    for gap, (stage, half) in enumerate(order):
        if any(thin[gap]):
            pure, ecoeff = left_mul(pure, ecoeff, eye(), scale_rows(thin[gap], 1))
        matrix_a, matrix_b, complement = stage_res[stage]
        factor_a = complement if half else matrix_a
        proj = projector_rows(factor_a, matrix_b, stage + 1)
        readm = read_rows(factor_a, stage + 1)
        factor_p = add(eye(), scale_rows(proj, scalar_x(stage)))
        factor_e = scale_rows(readm, scalar_d(stage))
        pure, ecoeff = left_mul(pure, ecoeff, factor_p, factor_e)
        seen[stage] += 1
    require(seen == [2, 2, 2], "a stage does not have exactly two full calls")
    if any(thin[6]):
        pure, ecoeff = left_mul(pure, ecoeff, eye(), scale_rows(thin[6], 1))
    return pure, ecoeff


def same(left, right):
    return left == right


def control_thin(stage):
    rows = [0] * N
    leaves = [stage] if stage + 1 == G else [stage, stage + 1]
    for leaf in leaves:
        block = leaf + 1
        for r in range(2):
            rows[r] |= 1 << (2 * block + r)
            rows[2 * block + r] |= 1 << r
    return tuple(rows)


# Explicit witness. Resolutions are (A bits, B bits). Call order is
# chronological, earliest first. Thin rows are bitmasks.
WITNESS_RES = ((1, 2), (1, 2), (3, 0))
WITNESS_ORDER = ((2, 0), (1, 0), (1, 1), (0, 0), (0, 1), (2, 1))
WITNESS_THIN = (
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0xD2, 0x00, 0x00, 0x00, 0x00, 0x03, 0x03, 0x00),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0x00, 0x2E, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0x86, 0x86, 0x00, 0x02, 0x00, 0x00, 0x02, 0x02),
    (0, 0, 0, 0, 0, 0, 0, 0),
)


def lookup(found, bits_a, bits_b):
    for matrix_a, matrix_b, complement, _first, _second in found:
        if bits_of(matrix_a) == bits_a and bits_of(matrix_b) == bits_b:
            return (matrix_a, matrix_b, complement)
    return None


def main():
    found = resolutions()
    require(len(found) == 12, "expected 12 orthogonal resolutions, found %d" % len(found))
    noncommuting = 0
    for left in found:
        for right in found:
            if mul2(left[0], right[0]) != mul2(right[0], left[0]):
                noncommuting += 1
    require(noncommuting == 96, "expected 96 noncommuting ordered A pairs, found %d" % noncommuting)

    stage_res = []
    for bits_a, bits_b in WITNESS_RES:
        triple = lookup(found, bits_a, bits_b)
        require(triple is not None, "witness resolution a=%d b=%d is not legal" % (bits_a, bits_b))
        stage_res.append(triple)
    require(
        mul2(stage_res[0][0], stage_res[2][0]) != mul2(stage_res[2][0], stage_res[0][0]),
        "the witness was expected to use noncommuting stage projectors",
    )

    goal = target()
    pure, ecoeff = evaluate(stage_res, WITNESS_ORDER, WITNESS_THIN)
    require(same(pure, goal), "witness pure product misses the target")
    require(same(ecoeff, goal), "witness e coefficient misses the target")
    ranks = tuple(rank8(rows) for rows in WITNESS_THIN)
    require(ranks == (0, 2, 0, 2, 0, 2, 0), "witness ranks are %s, expected 2+2+2" % (ranks,))
    require(sum(ranks) == 6, "witness rank sum is not 6")

    for gap in (1, 3, 5):
        deleted = [rows if index != gap else (0,) * N for index, rows in enumerate(WITNESS_THIN)]
        pure_d, ecoeff_d = evaluate(stage_res, WITNESS_ORDER, deleted)
        require(
            not (same(pure_d, goal) and same(ecoeff_d, goal)),
            "deleting gap %d still meets the endpoint" % gap,
        )

    corrupted = list(WITNESS_THIN)
    corrupted[1] = (WITNESS_THIN[1][0] ^ 1,) + WITNESS_THIN[1][1:]
    pure_c, ecoeff_c = evaluate(stage_res, WITNESS_ORDER, corrupted)
    require(
        not (same(pure_c, goal) and same(ecoeff_c, goal)),
        "flipping one witness bit still meets the endpoint",
    )

    diagonal = next(item for item in found if bits_of(item[1]) == 0)
    control_res = [(diagonal[0], diagonal[1], diagonal[2])] * 3
    control_order = tuple((stage, half) for stage in range(3) for half in range(2))
    control = [tuple(0 for _ in range(N)) for _ in range(7)]
    control[2] = control_thin(0)
    control[6] = control_thin(2)
    require((rank8(control[2]), rank8(control[6])) == (4, 4), "commuting control ranks are not 4+4")
    pure_k, ecoeff_k = evaluate(control_res, control_order, control)
    require(same(pure_k, goal) and same(ecoeff_k, goal), "commuting rank-8 control misses the endpoint")
    removed = list(control)
    removed[2] = tuple(0 for _ in range(N))
    pure_r, ecoeff_r = evaluate(control_res, control_order, removed)
    require(
        not (same(pure_r, goal) and same(ecoeff_r, goal)),
        "deleting the commuting control map still meets the endpoint",
    )

    print(
        "PASS_PAIRED_STAR_THREE_THIN_RANK ranks=2+2+2 sum=6 nonzero=3 "
        "resolutions=12 noncommuting_pairs=96 control=4+4"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
