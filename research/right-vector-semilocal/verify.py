#!/usr/bin/env python3
"""Construct semilocal three-factor words on finite matrix-block fixtures.

Produced by Nick Petalas. Apache-2.0.
This checks this package's new construction, not a predecessor's census.
"""

from hashlib import sha256
import json
from pathlib import Path


ONE = 9  # I_2 in row-major binary coordinates.
SHARP = (8, 2, 4, 1)  # The 4x4 permutation exchanging coordinates 0 and 3.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_product(a, b):
    """Multiply two 2x2 binary matrices encoded in four bits."""
    return sum(
        (sum(((a >> (2*i+k)) & 1) * ((b >> (2*k+j)) & 1)
             for k in range(2)) % 2) << (2*i+j)
        for i in range(2) for j in range(2)
    )


def tables():
    """R=M_2(F_2[e]/e^2): low nibble is residue, high is e coefficient."""
    base = tuple(tuple(binary_product(a, b) for b in range(16))
                 for a in range(16))
    inverse = [-1] * 256
    for a in range(16):
        for b in range(16):
            if base[a][b] == base[b][a] == ONE:
                for radical in range(16):
                    inverse[a | (radical << 4)] = (
                        b | (base[base[b][radical]][b] << 4))
    multiplication = tuple(tuple(
        base[x & 15][y & 15]
        | ((base[x & 15][y >> 4] ^ base[x >> 4][y & 15]) << 4)
        for y in range(256)) for x in range(256))
    for x in range(256):
        if inverse[x] >= 0:
            require(multiplication[x][inverse[x]] == ONE
                    and multiplication[inverse[x]][x] == ONE, "unit inverse")
    return multiplication, tuple(inverse)


def product(a, b, mul):
    return (
        mul[a[0]][b[0]] ^ mul[a[1]][b[2]],
        mul[a[0]][b[1]] ^ mul[a[1]][b[3]],
        mul[a[2]][b[0]] ^ mul[a[3]][b[2]],
        mul[a[2]][b[1]] ^ mul[a[3]][b[3]],
    )


def factors(target, mul, inverse):
    """Use the residue completion f and the actual lifted pivot inverse."""
    a, b, c, d = target
    for f in range(16):
        pivot = a ^ mul[b][f]
        if inverse[pivot] >= 0:
            lower = mul[c ^ mul[d][f]][inverse[pivot]]
            last = d ^ mul[lower][b]
            require(inverse[last] >= 0, "Schur remainder must be a unit")
            return ((ONE, 0, lower, ONE), (ONE, b, 0, last),
                    (pivot, 0, f, ONE))
    raise ValueError("no unit completion in the residue algebra")


def flatten(matrix):
    """Independent faithful action on eight binary coordinates, x0 then e*x1."""
    rows = [0] * 8
    for i in range(4):
        for j in range(4):
            block = matrix[2*(i//2) + j//2]
            offset = 2*(i % 2) + j % 2
            residue = (block >> offset) & 1
            radical = (block >> (4+offset)) & 1
            rows[i] |= residue << j
            rows[i+4] |= (radical << j) | (residue << (j+4))
    return tuple(rows)


def compose_rows(a, b):
    rows = [0] * 8
    for i in range(8):
        for j in range(8):
            if (a[i] >> j) & 1:
                rows[i] ^= b[j]
    return tuple(rows)


def check_word(target, word, mul):
    f1, f2, f3 = word
    require(f1[0:2] == (ONE, 0) and f1[3] == ONE, "first e1 factor")
    require(f2[0] == ONE and f2[2] == 0, "middle e2 factor")
    require(f3[1] == 0 and f3[3] == ONE, "last e1 factor")
    require(product(product(f1, f2, mul), f3, mul) == target, "block endpoint")
    independent = compose_rows(compose_rows(flatten(f1), flatten(f2)), flatten(f3))
    require(independent == flatten(target), "all eight binary basis columns")


def invertible_rows(code):
    rows = [(code >> (4*i)) & 15 for i in range(4)]
    pivot = 0
    for col in range(4):
        found = next((i for i in range(pivot, 4) if (rows[i] >> col) & 1), None)
        if found is not None:
            rows[pivot], rows[found] = rows[found], rows[pivot]
            for i in range(4):
                if i != pivot and (rows[i] >> col) & 1:
                    rows[i] ^= rows[pivot]
            pivot += 1
    return pivot == 4


def blocks(code):
    out = [0] * 4
    for i in range(4):
        for j in range(4):
            bit = (code >> (4*i+j)) & 1
            out[2*(i//2)+j//2] |= bit << (2*(i % 2)+j % 2)
    return tuple(out)


def unit_pivots(target, inverse):
    """All nine common nonzero F2 rows/columns from the cited criterion."""
    count = 0
    for row in range(1, 4):
        for column in range(1, 4):
            entry = 0
            for i in range(2):
                for j in range(2):
                    if ((row >> i) & 1) and ((column >> j) & 1):
                        entry ^= target[2*i+j]
            count += inverse[entry] >= 0
    return count


def residue_census(mul, inverse):
    count = 0
    digest = sha256()
    for code in range(1 << 16):
        if invertible_rows(code):
            target = blocks(code)
            word = factors(target, mul, inverse)
            check_word(target, word, mul)
            digest.update(bytes(target + sum(word, ())))
            count += 1
    require(count == 20160, "complete GL4(F2) enumeration")
    return {"targets": count, "word_sha256": digest.hexdigest()}


def radical_census(mul, inverse):
    count = 0
    digest = sha256()
    for code in range(1 << 16):
        target = tuple(SHARP[i] | (((code >> (4*i)) & 15) << 4)
                       for i in range(4))
        require(unit_pivots(target, inverse) == 0, "cost-three lift lower bound")
        word = factors(target, mul, inverse)
        check_word(target, word, mul)
        digest.update(bytes(target + sum(word, ())))
        count += 1
    require(count == 65536, "every radical lift of the fixed sharp target")
    return {"targets": count, "exact_cost_three": count,
            "word_sha256": digest.hexdigest()}


def shared_local_control(mul, inverse):
    """Tiny numeric overlap with #4601/#4613; not a replay of their engines."""
    scalars = (0, ONE, ONE << 4, ONE | (ONE << 4))
    charts = tuple(tuple(ONE if (code >> i) & 1 else 0 for i in range(4))
                   for code in range(16)
                   if inverse[code] >= 0)
    require(len(charts) == 6, "common GL2(F2) charts")
    histogram = [0] * 4
    for code in range(256):
        coefficients = tuple((code >> (2*i)) & 3 for i in range(4))
        a, b, c, d = tuple(x & 1 for x in coefficients)
        if (a*d) ^ (b*c) != 1:
            continue
        target = tuple(scalars[x] for x in coefficients)
        delta = 2
        for chart in charts:
            n = product(target, chart, mul)
            col1, col2 = (n[0] ^ ONE, n[2]), (n[1], n[3] ^ ONE)
            rank = 0 if col1 == col2 == (0, 0) else (
                1 if col1 == (0, 0) or col2 == (0, 0) or col1 == col2 else 2)
            delta = min(delta, rank)
        cost = delta if delta <= 1 else (2 if unit_pivots(target, inverse) else 3)
        histogram[cost] += 1
    require(histogram == [6, 54, 36, 0], "shared binary dual-number count")
    return {"targets": sum(histogram), "cost_histogram": histogram}


def odd_characteristic_control():
    """The displayed identity, with genuine subtraction, in M2(F3)."""
    def mm(a, b):
        return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2)) % 3
                     for i in range(2) for j in range(2))

    def add(a, b, sign=1):
        return tuple((a[i]+sign*b[i]) % 3 for i in range(4))

    def block_mm(a, b):
        return tuple(add(mm(a[2*i], b[j]), mm(a[2*i+1], b[2+j]))
                     for i in range(2) for j in range(2))

    zero, one = (0, 0, 0, 0), (1, 0, 0, 1)
    a, b, c, d = (0, 0, 0, 1), (0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 0, 0)
    f = c
    pivot = add(a, mm(b, f), -1)
    pivot_inverse = (2, 0, 0, 1)
    require(mm(pivot, pivot_inverse) == one, "ternary inverse")
    lower = mm(add(c, mm(d, f), -1), pivot_inverse)
    last = add(d, mm(lower, b), -1)
    word = ((one, zero, lower, one), (one, b, zero, last), (pivot, zero, f, one))
    require(block_mm(block_mm(word[0], word[1]), word[2]) == (a, b, c, d),
            "odd-characteristic endpoint")
    wrong = (add(a, mm(b, f)), zero, f, one)
    require(block_mm(block_mm(word[0], word[1]), wrong) != (a, b, c, d),
            "wrong-sign control must differ")


def controls(mul, inverse):
    require(not any(inverse[SHARP[0] ^ mul[SHARP[1]][f]] >= 0
                    for f in (0, ONE)), "base-field-only completion must fail")
    word = factors(SHARP, mul, inverse)
    order_target = (1, 6, 6, 0)
    order_word = factors(order_target, mul, inverse)
    require(product(product(order_word[2], order_word[1], mul), order_word[0], mul)
            != order_target,
            "reversed word must differ")
    require(product(word[0], word[1], mul) != SHARP, "dropped factor must differ")
    lifted = tuple(SHARP[i] ^ (ONE << 4) for i in range(4))
    lifted_word = factors(lifted, mul, inverse)
    require(product(product(word[0], word[1], mul), word[2], mul) != lifted,
            "residue word cannot stand in for the lift")
    f = lifted_word[2][2]
    pivot = lifted_word[2][0]
    wrong_lower = mul[lifted[2] ^ mul[lifted[3]][f]][inverse[pivot & 15]]
    wrong_word = ((ONE, 0, wrong_lower, ONE),
                  (ONE, lifted[1], 0, lifted[3] ^ mul[wrong_lower][lifted[1]]),
                  lifted_word[2])
    require(product(product(wrong_word[0], wrong_word[1], mul), wrong_word[2], mul)
            != lifted, "uncorrected residue inverse must differ")
    try:
        factors((0, 0, 0, 0), mul, inverse)
    except ValueError as exc:
        require(str(exc) == "no unit completion in the residue algebra", "failure reason")
    else:
        raise ValueError("singular target must be rejected by this construction")
    odd_characteristic_control()
    return 7


def source_hashes():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    manifest = json.loads((package / "SOURCES.json").read_text())
    require(len(manifest["files"]) == 4, "source inventory size")
    for row in manifest["files"]:
        if row["usage"] == "input":
            require(sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source bytes: " + row["path"])
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    return {name: sha256((package / name).read_bytes()).hexdigest() for name in names}


def main():
    hashes = source_hashes()
    mul, inverse = tables()
    result = {"residue": residue_census(mul, inverse),
              "radical": radical_census(mul, inverse),
              "shared_local_control": shared_local_control(mul, inverse),
              "negative_controls": controls(mul, inverse), "files": hashes}
    receipt = sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print("PASS_RIGHT_VECTOR_SEMILOCAL", json.dumps(result, sort_keys=True),
          "receipt=" + receipt, "no_new_kappa")


if __name__ == "__main__":
    main()
