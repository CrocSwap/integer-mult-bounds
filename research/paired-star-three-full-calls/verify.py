#!/usr/bin/env python3
"""Three or more full calls miss the g=3, d=2, F_2 paired-star pure endpoint.

Every T-commuting projector on a stage block is enumerated from the 16-by-16
commutant. Ordered pairs and ordered triples are multiplied in F_2[x] and
compared with I+xE. Longer call lists are excluded by a determinant valuation
that is checked on every projector. Failures raise SystemExit, so python -O
still fails closed.
"""

from __future__ import annotations

I2 = ((1, 0), (0, 1))
Z2 = ((0, 0), (0, 0))
EYE4 = (1, 2, 4, 8)


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def add2(left, right):
    return tuple(tuple(left[r][c] ^ right[r][c] for c in range(2)) for r in range(2))


def mul2(left, right):
    return tuple(
        tuple((left[r][0] & right[0][c]) ^ (left[r][1] & right[1][c]) for c in range(2))
        for r in range(2)
    )


def mat2(bits):
    return tuple(tuple((bits >> (2 * r + c)) & 1 for c in range(2)) for r in range(2))


def bits2(matrix):
    value = 0
    for r in range(2):
        for c in range(2):
            if matrix[r][c]:
                value |= 1 << (2 * r + c)
    return value


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


def trace2(matrix):
    return matrix[0][0] ^ matrix[1][1]


def det2_scalar(matrix):
    return (matrix[0][0] & matrix[1][1]) ^ (matrix[0][1] & matrix[1][0])


def pmul(left, right):
    out = 0
    while left:
        bit = left & -left
        out ^= right << (bit.bit_length() - 1)
        left ^= bit
    return out


def valuation(poly):
    """(1+x)-adic valuation in F_2[x]. The zero polynomial is rejected."""
    if poly == 0:
        fail("zero polynomial has no finite valuation")
    value = 0
    while poly.bit_count() % 2 == 0:
        quotient = 0
        previous = 0
        for index in range(poly.bit_length()):
            coefficient = (poly >> index) & 1
            current = coefficient ^ previous
            if current:
                quotient |= 1 << index
            previous = current
        if previous != 0:
            fail("polynomial was not divisible by 1+x")
        poly = quotient
        value += 1
        if value > 32:
            fail("valuation did not terminate")
    return value


def pack_projector(matrix_a, matrix_b):
    mixed = add2(matrix_a, matrix_b)
    blocks = ((mixed, matrix_b), (matrix_b, mixed))
    rows = []
    for block_row in range(2):
        for r in range(2):
            mask = 0
            for block_col in range(2):
                block = blocks[block_row][block_col]
                for c in range(2):
                    if block[r][c]:
                        mask |= 1 << (2 * block_col + c)
            rows.append(mask)
    return tuple(rows)


def mul_bits(left, right):
    rows = []
    for row in left:
        value = 0
        rest = row
        while rest:
            bit = rest & -rest
            value ^= right[bit.bit_length() - 1]
            rest ^= bit
        rows.append(value)
    return tuple(rows)


def add_bits(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def gate4(projector):
    rows = []
    for i in range(4):
        row = []
        for j in range(4):
            poly = 1 if i == j else 0
            if (projector[i] >> j) & 1:
                poly ^= 1 << 1
            row.append(poly)
        rows.append(tuple(row))
    return tuple(rows)


def mul4(left, right):
    out = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for k in range(4):
            factor = left[i][k]
            if not factor:
                continue
            for j in range(4):
                out[i][j] ^= pmul(factor, right[k][j])
    return tuple(tuple(row) for row in out)


def det4(matrix):
    # In characteristic two every permutation has sign +1.
    total = 0
    for perm in (
        (0, 1, 2, 3),
        (0, 1, 3, 2),
        (0, 2, 1, 3),
        (0, 2, 3, 1),
        (0, 3, 1, 2),
        (0, 3, 2, 1),
        (1, 0, 2, 3),
        (1, 0, 3, 2),
        (1, 2, 0, 3),
        (1, 2, 3, 0),
        (1, 3, 0, 2),
        (1, 3, 2, 0),
        (2, 0, 1, 3),
        (2, 0, 3, 1),
        (2, 1, 0, 3),
        (2, 1, 3, 0),
        (2, 3, 0, 1),
        (2, 3, 1, 0),
        (3, 0, 1, 2),
        (3, 0, 2, 1),
        (3, 1, 0, 2),
        (3, 1, 2, 0),
        (3, 2, 0, 1),
        (3, 2, 1, 0),
    ):
        prod = 1
        for row, col in enumerate(perm):
            prod = pmul(prod, matrix[row][col])
            if prod == 0:
                break
        total ^= prod
    return total


def closed_block_det(matrix_a):
    """det(I+xP) = det(I+xA)^2 for a T-commuting projector."""
    trace = trace2(matrix_a)
    det = det2_scalar(matrix_a)
    det_a = 1 ^ ((trace & 1) << 1) ^ ((det & 1) << 2)
    return pmul(det_a, det_a)


def projectors():
    found = []
    for bits_a in range(16):
        matrix_a = mat2(bits_a)
        if mul2(matrix_a, matrix_a) != matrix_a:
            continue
        for bits_b in range(16):
            matrix_b = mat2(bits_b)
            if add2(mul2(matrix_a, matrix_b), mul2(matrix_b, matrix_a)) != matrix_b:
                continue
            projector = pack_projector(matrix_a, matrix_b)
            require(mul_bits(projector, projector) == projector, "commutant element is not idempotent")
            found.append(
                {
                    "rank": rank2(matrix_a),
                    "a": matrix_a,
                    "b": matrix_b,
                    "rows": projector,
                    "gate": gate4(projector),
                }
            )
    return tuple(found)


def embed(rows, stage):
    leaf = stage + 1
    coords = (0, 1, 2 * leaf, 2 * leaf + 1)
    out = [0] * 8
    for i in range(4):
        for j in range(4):
            if (rows[i] >> j) & 1:
                out[coords[i]] |= 1 << coords[j]
    return tuple(out)


def check_embedding(calls):
    for stage in range(3):
        for call in calls:
            if call["rank"] == 0:
                continue
            embedded = embed(call["rows"], stage)
            coords = (0, 1, 2 * (stage + 1), 2 * (stage + 1) + 1)
            order = coords + tuple(i for i in range(8) if i not in coords)
            for local_row, global_row in enumerate(order[:4]):
                for local_col, global_col in enumerate(order[:4]):
                    bit = (embedded[global_row] >> global_col) & 1
                    require(bit == ((call["rows"][local_row] >> local_col) & 1), "stage embedding moved the block")
            for global_row in order[4:]:
                require(embedded[global_row] == 0, "projector leaves its stage block")
            for global_row in order[:4]:
                for global_col in order[4:]:
                    require(((embedded[global_row] >> global_col) & 1) == 0, "projector has a cross-leaf column")


def support_e(stage):
    rows = [0] * 8
    rows[0] = 1
    rows[1] = 2
    leaf = 2 * (stage + 1)
    rows[leaf] = 1 << leaf
    rows[leaf + 1] = 1 << (leaf + 1)
    return tuple(rows)


def bivariate_gate(bit_rows, variable):
    one = {(0, 0): 1}
    monomial = {(1, 0): 1} if variable == 0 else {(0, 1): 1}
    matrix = []
    for i in range(8):
        row = []
        for j in range(8):
            poly = dict(one) if i == j else {}
            if (bit_rows[i] >> j) & 1:
                poly = add_poly(poly, monomial)
            row.append(poly)
        matrix.append(tuple(row))
    return tuple(matrix)


def add_poly(left, right):
    out = dict(left)
    for key in right:
        if key in out:
            del out[key]
        else:
            out[key] = 1
    return out


def mul_poly(left, right):
    out = {}
    for i, j in left:
        for k, ell in right:
            key = (i + k, j + ell)
            if key in out:
                del out[key]
            else:
                out[key] = 1
    return out


def mul8(left, right):
    out = []
    for i in range(8):
        row = []
        for j in range(8):
            acc = {}
            for k in range(8):
                factor = left[i][k]
                if factor:
                    acc = add_poly(acc, mul_poly(factor, right[k][j]))
            row.append(acc)
        out.append(tuple(row))
    return tuple(out)


def main():
    require(det4(gate4(EYE4)) == (1 << 4) ^ 1, "det(I+xI) must be (1+x)^4")
    require(valuation(1) == 0, "val(1)")
    require(valuation(0b11) == 1, "val(1+x)")
    require(valuation(0b101) == 2, "val(1+x^2)")
    require(valuation(0b10001) == 4, "val(1+x^4)")
    # Char-2 Leibniz has no signs: det[[0,1],[1,0]] = 1.
    swap = ((0, 1), (1, 0))
    require((swap[0][0] & swap[1][1]) ^ (swap[0][1] & swap[1][0]) == 1, "char-2 det sign")

    calls = projectors()
    require(len(calls) == 26, "commutant projector count")
    by_rank = {0: 0, 1: 0, 2: 0}
    for call in calls:
        by_rank[call["rank"]] += 1
        determinant = det4(call["gate"])
        call["det"] = determinant
        closed = closed_block_det(call["a"])
        require(determinant == closed, "Leibniz determinant disagrees with the block formula")
        require(valuation(determinant) == 2 * call["rank"], "determinant valuation")
    require(by_rank == {0: 1, 1: 24, 2: 1}, "rank census")
    full = [call for call in calls if call["rank"] == 2]
    require(full[0]["a"] == I2 and full[0]["b"] == Z2, "the rank-2 projector is E")
    zero = [call for call in calls if call["rank"] == 0]
    require(zero[0]["rows"] == (0, 0, 0, 0), "the rank-0 projector is zero")
    require(zero[0]["gate"] == gate4((0, 0, 0, 0)), "a zero call is the constant identity")

    nonzero = [call for call in calls if call["rank"] > 0]
    require(len(nonzero) == 25, "nonzero projector count")
    min_valuation = min(valuation(det4(call["gate"])) for call in nonzero)
    require(min_valuation == 2, "every nonzero full call has valuation exactly 2 or the rank-2 call has 4")
    # The minimum is 2; the rank-2 call is larger. Both are at least 2.
    require(all(valuation(det4(call["gate"])) >= 2 for call in nonzero), "valuation lower bound")
    target = gate4(EYE4)
    target_valuation = valuation(det4(target))
    require(target_valuation == 4, "target valuation")

    check_embedding(calls)
    for stage in range(3):
        embedded_e = embed(full[0]["rows"], stage)
        require(embedded_e == support_e(stage), "E embedding")

    pair_hits = 0
    complementary = 0
    different_b_seen = False
    for left in nonzero:
        for right in nonzero:
            product = mul4(left["gate"], right["gate"])
            if product == target:
                pair_hits += 1
                same = (
                    left["rank"] == 1
                    and right["rank"] == 1
                    and add2(left["a"], right["a"]) == I2
                    and left["b"] == right["b"]
                )
                require(same, "a resolving pair is not a complementary same-B pair")
                complementary += 1
            elif (
                left["rank"] == 1
                and right["rank"] == 1
                and add2(left["a"], right["a"]) == I2
                and left["b"] != right["b"]
            ):
                different_b_seen = True
    require(different_b_seen, "different-B complementary pairs were missing")
    require(pair_hits == 24 and complementary == 24, "ordered resolving pairs")

    # Independent orthogonality search, matching the predecessor's 12 resolutions.
    seen = set()
    for call in nonzero:
        if call["rank"] != 1:
            continue
        partner_a = add2(I2, call["a"])
        partner = next(
            other
            for other in nonzero
            if other["a"] == partner_a and other["b"] == call["b"]
        )
        product_zero = mul_bits(call["rows"], partner["rows"]) == (0, 0, 0, 0)
        reverse_zero = mul_bits(partner["rows"], call["rows"]) == (0, 0, 0, 0)
        summed = add_bits(call["rows"], partner["rows"]) == EYE4
        require(product_zero and reverse_zero and summed, "complementary pair is not an orthogonal resolution")
        seen.add(frozenset((call["rows"], partner["rows"])))
    require(len(seen) == 12, "unordered resolutions")

    triple_hits = 0
    screened = 0
    for left in nonzero:
        for middle in nonzero:
            partial = mul4(left["gate"], middle["gate"])
            for right in nonzero:
                screened += 1
                product = mul4(partial, right["gate"])
                require(
                    det4(product) == pmul(pmul(left["det"], middle["det"]), right["det"]),
                    "determinant failed to multiply on a triple",
                )
                if product == target:
                    triple_hits += 1
    require(screened == 25 ** 3 == 15625, "triple census domain")
    require(triple_hits == 0, "a triple met I+xE")

    # Length >= 4 is every tuple, not a sample: each factor contributes
    # valuation at least 2, and det is multiplicative.
    require(4 * 2 == 8 and 8 > target_valuation, "four calls exceed the target valuation")
    require(3 * 2 == 6 and 6 > target_valuation, "three calls exceed the target valuation")

    # Positive control: a grouped two-call word on two stages equals the
    # target factor, and inserting one more stage-0 call destroys it.
    resolution = next(iter(seen))
    first, second = tuple(resolution)
    stage0 = [bivariate_gate(embed(first, 0), 0), bivariate_gate(embed(second, 0), 0)]
    stage1_rows = next(iter(seen))
    third, fourth = tuple(stage1_rows)
    stage1 = [bivariate_gate(embed(third, 1), 1), bivariate_gate(embed(fourth, 1), 1)]
    grouped = stage0[0]
    for factor in (stage0[1], stage1[0], stage1[1]):
        grouped = mul8(factor, grouped)
    target_word = bivariate_gate(support_e(0), 0)
    target_word = mul8(bivariate_gate(support_e(1), 1), target_word)
    require(grouped == target_word, "grouped two-call control missed the pure target")
    extra = bivariate_gate(embed(nonzero[0]["rows"], 0), 0)
    # Rightmost factor is the first call. Insert the extra call on the right.
    broken = mul8(grouped, extra)
    require(broken != target_word, "an extra full call left the pure target unchanged")
    # The constant identity, which is the pure part of every thin map, does not
    # repair that mismatch.
    identity = bivariate_gate((0,) * 8, 0)
    require(mul8(identity, broken) == broken and broken != target_word, "thin pure part repaired a mismatch")

    # Corrupted-product control: flipping one entry of a real resolution
    # product must leave the endpoint.
    partner = next(
        other
        for other in nonzero
        if other["a"] == add2(I2, nonzero[0]["a"]) and other["b"] == nonzero[0]["b"] and other["rows"] != nonzero[0]["rows"]
    )
    good = mul4(nonzero[0]["gate"], partner["gate"])
    require(good == target, "control pair missed the endpoint")
    corrupted = [list(row) for row in good]
    corrupted[0][0] ^= 1
    require(tuple(tuple(row) for row in corrupted) != target, "corruption control did not move the product")

    print(
        "projectors=26 zero=1 rank1=24 rank2=1 "
        "pair_screened=625 pair_hits=24 resolutions=12 "
        "triple_screened=15625 triple_hits=0 "
        "min_nonzero_valuation=2 rank2_valuation=4 target_valuation=4 "
        "length_at_least_4=excluded_by_valuation embedding_stages=3"
    )
    print("PASS_PAIRED_STAR_THREE_FULL_CALLS")


if __name__ == "__main__":
    main()
