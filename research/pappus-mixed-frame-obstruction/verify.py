"""New mixed-Pappus obstruction and boundary witnesses.

Produced by Nick Petalas. Apache-2.0. The integer fixture is mathematical
data from Sagar Thakrar's PR2274; no predecessor implementation is imported.
"""

import hashlib
import itertools
import json
from pathlib import Path


POINTS = (
    (0, 0, 1), (1, 0, 1), (1, 0, -1),
    (0, 1, 1), (15, -1, -1), (15, 1, 1),
    (0, 1, -14), (15, 1, -14), (15, -1, 14),
)
LINES = (
    (0, 1, 0), (0, 1, -1), (0, 14, 1),
    (1, 15, 0), (1, -15, 0), (1, 1, -1),
    (1, -14, -1), (1, -1, 1), (1, 14, 1),
)
ODD_POINTS = (
    (0, 0, 1), (1, 0, 1), (-1, 0, 1),
    (0, 1, 0), (1, 1, 0), (-1, 1, 0),
    (0, 1, 1), (-1, 1, 1), (1, 1, 1),
)
ODD_LINES = (
    (0, 1, 0), (0, 0, 1), (0, 1, -1),
    (1, -1, 0), (1, 1, 0), (1, 0, -1),
    (1, 1, -1), (1, 0, 1), (1, -1, 1),
)
RELAXED_POINTS = (
    (0, 0, 1), (1, 0, 1), (2, 0, 1),
    (0, 1, 1), (1, 1, 1), (3, 1, 1),
    (0, 1, 2), (1, 2, 1), (1, 1, 0),
)
RELAXED_LINES = (
    (0, 1, 0), (0, 1, 1), (1, 1, 3),
    (1, 1, 0), (1, 3, 0), (1, 1, 1),
    (1, 2, 1), (1, 2, 2), (1, 3, 2),
)
FIELDS = (2, 3, 4, 5, 7, 8, 16)
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer_dot(left, right):
    return sum(left[j] * right[j] for j in range(3))


def add(q, left, right):
    return left ^ right if q in (4, 8, 16) else (left + right) % q


def negative(q, value):
    return value if q in (4, 8, 16) else -value % q


def multiply(q, left, right):
    if q not in (4, 8, 16):
        return left * right % q
    modulus = {4: 7, 8: 11, 16: 19}[q]
    result = 0
    for _ in range(q.bit_length() - 1):
        if right & 1:
            result ^= left
        right >>= 1
        left <<= 1
        if left & q:
            left ^= modulus
    require(0 <= result < q, "field multiplication range")
    return result


def field_dot(q, left, right):
    result = 0
    for j in range(3):
        result = add(q, result, multiply(q, left[j], right[j]))
    return result


def incidence(points, lines):
    return tuple(tuple(integer_dot(p, line) == 0 for line in lines) for p in points)


def valid_vectors(vectors, q):
    return len(vectors) == 9 and all(
        len(v) == 3 and any(v) and all(type(x) is int and 0 <= x < q for x in v)
        for v in vectors
    )


def realization(q, points, lines, relax_pap=False):
    require(q in FIELDS, "unsupported field")
    if not valid_vectors(points, q) or not valid_vectors(lines, q):
        return False
    for rows, support, is_line in ((points, POINTS, False), (lines, LINES, True)):
        for i, row in enumerate(rows):
            for j in range(3):
                relaxed = relax_pap and is_line and i == 2 and j == 0
                if row[j] and not support[i][j] and not relaxed:
                    return False
    target = incidence(POINTS, LINES)
    return all(
        (field_dot(q, points[i], lines[j]) == 0) == target[i][j]
        for i in range(9) for j in range(9)
    )


def check_field(q):
    require(q in FIELDS, "unsupported field")
    nonzero = range(1, q)
    for x, y, z in itertools.product(range(q), repeat=3):
        require(add(q, x, y) == add(q, y, x), "addition commutativity")
        require(add(q, add(q, x, y), z) == add(q, x, add(q, y, z)), "addition associativity")
        require(multiply(q, x, y) == multiply(q, y, x), "multiplication commutativity")
        require(multiply(q, multiply(q, x, y), z) == multiply(q, x, multiply(q, y, z)),
                "multiplication associativity")
        require(multiply(q, x, add(q, y, z)) == add(q, multiply(q, x, y), multiply(q, x, z)),
                "distributivity")
    for x in range(q):
        require(add(q, x, 0) == x and add(q, x, negative(q, x)) == 0, "additive identity/inverse")
        require(multiply(q, x, 1) == x, "multiplicative identity")
    for x in nonzero:
        require(sum(multiply(q, x, y) == 1 for y in nonzero) == 1, "unique field inverse")


def check_normalized_core(q):
    """Enumerate the new three-parameter core, not predecessor field searches."""
    tested = constrained = accepted = 0
    for a, c, d in itertools.product(range(1, q), range(q), range(q)):
        tested += 1
        a1 = (a, 0, 1)
        c0, c1 = (0, 1, 1), (d, 1, 1)
        l12 = (1, negative(q, d), negative(q, a))
        l20 = (1, 0, negative(q, c))
        e0 = field_dot(q, c0, l12)
        e1 = field_dot(q, c1, l20)
        pairing = field_dot(q, a1, l20)
        twice_a = add(q, a, a)
        require(pairing == add(q, add(q, twice_a, e0), e1), "literal core identity")
        if e0 == 0 and e1 == 0:
            constrained += 1
            accepted += pairing != 0
    require(constrained == q - 1, "two incidence equations")
    expected = 0 if q in (2, 4, 8, 16) else q - 1
    require(accepted == expected, "characteristic obstruction")
    return {"q": q, "triples": tested, "incidence_solutions": constrained,
            "nonincident_solutions": accepted}


def check_odd_witness():
    target = incidence(POINTS, LINES)
    require(len(set(target)) == 9 and len(set(zip(*target))) == 9, "distinct incidence signatures")
    require(incidence(ODD_POINTS, ODD_LINES) == target, "odd incidence witness")
    for rows, support in ((ODD_POINTS, POINTS), (ODD_LINES, LINES)):
        require(all(any(row) for row in rows), "nonzero odd vectors")
        require(all(not row[j] or support[i][j] for i, row in enumerate(rows) for j in range(3)),
                "odd support witness")
    products = [integer_dot(p, line) for p in ODD_POINTS for line in ODD_LINES]
    require({abs(x) for x in products if x} == {1, 2}, "all-odd characteristic certificate")
    require(products.count(0) == 27, "fixture incidence count")
    for q in (3, 5, 7):
        points = tuple(tuple(x % q for x in row) for row in ODD_POINTS)
        lines = tuple(tuple(x % q for x in row) for row in ODD_LINES)
        require(realization(q, points, lines), "finite odd witness")
    return {"zero_pairings": 27, "nonzero_pairings": 54, "nonzero_absolute_values": [1, 2]}


def check_controls():
    require(not realization(4, RELAXED_POINTS, RELAXED_LINES), "original support must reject")
    require(realization(4, RELAXED_POINTS, RELAXED_LINES, relax_pap=True), "one-zero relaxation witness")
    bad = list(RELAXED_LINES)
    bad[3] = RELAXED_LINES[4]
    require(not realization(4, RELAXED_POINTS, tuple(bad), relax_pap=True), "incidence mutation")
    zero = list(RELAXED_POINTS)
    zero[0] = (0, 0, 0)
    require(not realization(4, tuple(zero), RELAXED_LINES, relax_pap=True), "zero point mutation")
    # Dropping A1.L20 != 0 admits a=c=d=1 in characteristic two.
    require(field_dot(2, (0, 1, 1), (1, 1, 1)) == 0, "relaxed first incidence")
    require(field_dot(2, (1, 1, 1), (1, 0, 1)) == 0, "relaxed second incidence")
    require(field_dot(2, (1, 0, 1), (1, 0, 1)) == 0, "required nonincidence is essential")
    return {"one_coordinate_relaxation": "GF4", "rejection_controls": 3,
            "nonincidence_removal": "core feasible over GF2"}


def receipt(results):
    directory = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        with (directory / name).open("rb") as source:
            data = source.read(1024 * 1024 + 1)
        require(len(data) <= 1024 * 1024, "receipt file capacity")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return {"schema": "pappus-mixed-frame-obstruction/v1", "checks": results, "sha256": hashes}


def main():
    # Coefficients of (a,c,d): N - 2a - e0 - e1 = 0, with e0=-(a+d).
    n, twice, e0, e1 = (1, -1, 0), (2, 0, 0), (-1, 0, -1), (0, -1, 1)
    require(tuple(n[j] - twice[j] - e0[j] - e1[j] for j in range(3)) == (0, 0, 0),
            "integer polynomial identity")
    for q in FIELDS:
        check_field(q)
    cores = [check_normalized_core(q) for q in FIELDS]
    results = {"core": cores, "odd_witness": check_odd_witness(), "controls": check_controls()}
    print("PASS_PAPPUS_MIXED_FRAME_OBSTRUCTION")
    print(json.dumps(receipt(results), sort_keys=True))


if __name__ == "__main__":
    main()
