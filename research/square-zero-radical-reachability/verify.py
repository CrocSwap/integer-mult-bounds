"""Exact binary checks for the square-zero radical reachability theorem.

Only the standard library is used. All scientific checks survive -O.
The literal alphabet enumeration does not use the common-zero criterion.
"""

import hashlib
import itertools
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_DIM = 3
LINES = ((1, 0), (0, 1), (1, 1))
FREE = tuple((a, b, c, d) for a, b, c, d in itertools.product(range(2), repeat=4)
             if a * d ^ b * c)
IDENTITY = (1, 0, 0, 1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ring_table(dim):
    """Element bit 0 is scalar; remaining bits encode the square-zero ideal."""
    require(type(dim) is int and 0 <= dim <= MAX_DIM, "dimension outside bound")
    size = 1 << (dim + 1)
    return tuple(tuple(((b if a & 1 else 0) ^ (a if b & 1 else 0)
                        ^ (a & b & 1)) for b in range(size)) for a in range(size))


def multiply(a, b, table):
    return (table[a[0]][b[0]] ^ table[a[1]][b[2]],
            table[a[0]][b[1]] ^ table[a[1]][b[3]],
            table[a[2]][b[0]] ^ table[a[3]][b[2]],
            table[a[2]][b[1]] ^ table[a[3]][b[3]])


def residue(a):
    return tuple(x & 1 for x in a)


def common_zero(a):
    """Return a base-field row/column witness, or None."""
    for phi, v in itertools.product(LINES, repeat=2):
        value = ((a[0] if phi[0] and v[0] else 0)
                 ^ (a[1] if phi[0] and v[1] else 0)
                 ^ (a[2] if phi[1] and v[0] else 0)
                 ^ (a[3] if phi[1] and v[1] else 0))
        if value == 0:
            return phi, v
    return None


def inverse(a):
    require(a in FREE, "inverse requires a binary free map")
    return (a[3], a[1], a[2], a[0])


def triangular_word(a, witness, table):
    """Return G^-1, C1, C2, H^-1 in algebraic product order."""
    phi, v = witness
    g = next(g for g in FREE if g[:2] == phi)
    h = next(h for h in FREE if (h[1], h[3]) == v)
    n = multiply(multiply(g, a, table), h, table)
    require(n[1] == 0, "common-zero chart")
    c1 = (n[0], 0, n[2], 1)
    c2 = (1, 0, 0, n[3])
    return inverse(g), c1, c2, inverse(h)


def product(word, table):
    require(0 <= len(word) <= 4, "word outside replay bound")
    acc = IDENTITY
    for factor in word:
        acc = multiply(acc, factor, table)
    return acc


def paid_factors(size):
    require(2 <= size <= 16 and size & (size - 1) == 0, "ring size bound")
    return tuple(sorted({(1 ^ (a if y[0] else 0), a if y[1] else 0,
                          b if y[0] else 0, 1 ^ (b if y[1] else 0))
                         for a, b in itertools.product(range(size), repeat=2)
                         for y in LINES}))


def literal_two_factor_radicals(table):
    """Enumerate Q1 Q2 S without using any pivot or common-zero test."""
    factors = paid_factors(len(table))
    binary = ring_table(0)
    groups = {}
    for factor in factors:
        groups.setdefault(residue(factor), []).append(factor)
    targets = set()
    pairs = 0
    for r1, r2 in itertools.product(groups, repeat=2):
        if multiply(r1, r2, binary) != (0, 0, 0, 0):
            continue
        for q1, q2 in itertools.product(groups[r1], groups[r2]):
            middle = multiply(q1, q2, table)
            pairs += 1
            for free in FREE:
                targets.add(multiply(middle, free, table))
    require(all(residue(a) == (0, 0, 0, 0) for a in targets), "radical filter")
    return targets, pairs


def check_dimension(dim):
    table = ring_table(dim)
    literal, pairs = literal_two_factor_radicals(table)
    criterion = set()
    for a in itertools.product(range(0, len(table), 2), repeat=4):
        witness = common_zero(a)
        if witness is not None:
            criterion.add(a)
            require(product(triangular_word(a, witness, table), table) == a,
                    "attaining two-factor word")
    require(literal == criterion, "literal alphabet and criterion disagree")
    z = 1 << dim
    check_formula(z, len(literal), (-20, 42, -30, 9, 0))
    return {"dimension": dim, "total": z ** 4, "reachable": len(literal),
            "unreachable": z ** 4 - len(literal), "literal_pairs": pairs}


def check_formula(z, actual, coefficients):
    require(len(coefficients) == 5 and 1 <= z <= 8, "polynomial bounds")
    require(actual == sum(c * z ** i for i, c in enumerate(coefficients)),
            "binary all-dimension counting law")


def binary_rank(vectors):
    require(len(vectors) <= 9 and all(0 <= v < 16 for v in vectors), "rank bound")
    pivots = [0] * 4
    for value in vectors:
        for bit in range(3, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(p) for p in pivots)


def check_counting_arrangement():
    """Independent inclusion-exclusion over nine rank-one bilinear forms."""
    tensors = tuple((phi[0] * v[0] | phi[0] * v[1] << 1
                     | phi[1] * v[0] << 2 | phi[1] * v[1] << 3)
                    for phi, v in itertools.product(LINES, repeat=2))
    coefficients = [0] * 5
    for mask in range(1, 1 << 9):
        vectors = tuple(tensors[i] for i in range(9) if mask >> i & 1)
        coefficients[4 - binary_rank(vectors)] += (-1) ** (mask.bit_count() + 1)
    require(coefficients == [-20, 42, -30, 9, 0], "arrangement polynomial")
    return coefficients


def check_zero_transition():
    """Exhaust all first-zero transitions for dim J = 1."""
    table = ring_table(1)
    rank_one = tuple(a for a in itertools.product(range(2), repeat=4)
                     if a != (0, 0, 0, 0) and a not in FREE)
    checked = 0
    for p0 in rank_one:
        for q in paid_factors(4):
            if multiply(residue(q), p0, table) != (0, 0, 0, 0):
                continue
            for perturbation in itertools.product((0, 2), repeat=4):
                p = tuple(a ^ b for a, b in zip(p0, perturbation))
                result = multiply(q, p, table)
                require(common_zero(result) is not None, "first-zero invariant")
                checked += 1
    return checked


def check_controls(dimensions):
    table = ring_table(2)
    obstruction = (2, 4, 4, 6)
    require(common_zero(obstruction) is None, "irreducible pencil control")
    coefficients = ((1, 0, 0, 1), (0, 1, 1, 1))
    require(all(common_zero(a) is not None for a in coefficients),
            "componentwise charts would wrongly accept obstruction")
    witness = (2, 0, 4, 6)
    word = triangular_word(witness, common_zero(witness), table)
    require(product((word[0], word[2], word[1], word[3]), table) != witness,
            "reversed paid factors control")
    require(product((word[0], word[1], word[3]), table) != witness,
            "dropped paid factor control")
    try:
        check_formula(8, dimensions[3]["reachable"], (-19, 42, -30, 9, 0))
    except ValueError:
        pass
    else:
        raise ValueError("changed polynomial constant was accepted")
    try:
        ring_table(MAX_DIM + 1)
    except ValueError:
        pass
    else:
        raise ValueError("dimension exhaustion was accepted")
    return 6


def receipt(results):
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    paths = [PACKAGE / name for name in names]
    manifest = json.loads((PACKAGE / "VERIFY.json").read_text(encoding="utf-8"))
    paths.extend(ROOT / name for name in manifest["inputs"])
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in paths}
    return {"files": hashes, "results": results}


def main():
    dimensions = [check_dimension(d) for d in range(MAX_DIM + 1)]
    results = {"dimensions": dimensions,
               "arrangement": check_counting_arrangement(),
               "first_zero_transitions": check_zero_transition(),
               "controls": check_controls(dimensions)}
    print(json.dumps(receipt(results), sort_keys=True))
    print("PASS_SQUARE_ZERO_RADICAL_REACHABILITY dimensions=0..3 "
          "reachable=1,16,244,3004 unreachable=0,0,12,1092 no_new_kappa")


if __name__ == "__main__":
    main()
