#!/usr/bin/env python3
"""Exact finite checks for the eight-owner lattice theorem. Apache-2.0."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OWNERS = (5, 33, 49, 53, 62, 65, 97, 108)
TWICE_INVERSE = (
    (1, 0, 0, 0, 0, 0, 1, 0),
    (3, -1, -3, 2, 2, -2, 1, 2),
    (0, 1, 0, 0, 0, 0, 0, 1),
    (0, 0, 1, 0, 0, 0, 0, -1),
    (0, 0, 0, 0, 0, 1, -1, 0),
    (-2, 1, 1, 0, -2, 1, -1, 0),
    (-1, -1, 2, 0, 0, 1, 0, -1),
    (-1, 0, 1, 0, 0, 1, 0, -1),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vector(values, length, label):
    require(isinstance(values, (list, tuple)) and len(values) == length,
            label + " has the wrong length")
    require(all(type(x) is int and x.bit_length() <= 4096 for x in values),
            label + " requires integers of at most 4096 bits")
    return tuple(values)


def matvec(matrix, values):
    return tuple(sum(a * b for a, b in zip(row, values, strict=True))
                 for row in matrix)


def multiply(left, right):
    return tuple(matvec(tuple(zip(*right, strict=True)), row) for row in left)


def nearest_away(numerator, denominator=52):
    value = (2 * abs(numerator) + denominator) // (2 * denominator)
    return value if numerator >= 0 else -value


def forward(matrix, z):
    z = vector(z, 112, "input")
    quotients = tuple(nearest_away(x) for x in matvec(tuple(zip(*matrix)), z))
    return tuple(x - t for x, t in zip(z, matvec(matrix, quotients), strict=True))


def recover(matrix, y, residues):
    y = vector(y, 112, "output")
    residues = vector(residues, 8, "residues")
    require(all(0 <= r < 32 for r in residues), "residue outside [0,32)")
    rhs = tuple(r - y[i] for i, r in zip(OWNERS, residues, strict=True))
    doubled = matvec(TWICE_INVERSE, rhs)
    require(all(x % 2 == 0 for x in doubled), "odd doubled quotient residue")
    mode_residues = tuple((x // 2) % 16 for x in doubled)
    projected = matvec(tuple(zip(*matrix)), y)
    q = []
    for s, r in zip(projected, mode_residues, strict=True):
        lower = -((26 + s) // 4)
        upper = (26 - s) // 4
        candidate = lower + (r - lower) % 16
        require(candidate <= upper, "no quotient in residual interval")
        require(nearest_away(s + 56 * candidate) == candidate,
                "quotient violates the half-tie rule")
        q.append(candidate)
    z = tuple(a + b for a, b in zip(y, matvec(matrix, q), strict=True))
    require(all(z[i] % 32 == r for i, r in zip(OWNERS, residues, strict=True)),
            "reconstructed owner residue differs")
    require(forward(matrix, z) == y, "reconstructed forward value differs")
    return z


def rational_inverse(matrix):
    work = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(8)]
            for i, row in enumerate(matrix)]
    determinant = Fraction(1)
    for j in range(8):
        pivot = next((i for i in range(j, 8) if work[i][j]), None)
        require(pivot is not None, "singular selected rows")
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            determinant = -determinant
        scale = work[j][j]
        determinant *= scale
        work[j] = [x / scale for x in work[j]]
        for i in range(8):
            if i != j:
                scale = work[i][j]
                work[i] = [x - scale * y for x, y in zip(work[i], work[j], strict=True)]
    return determinant, tuple(tuple(row[8:]) for row in work)


def certificate(matrix, owners=OWNERS, twice_inverse=TWICE_INVERSE):
    selected = tuple(matrix[i] for i in owners)
    twice_identity = tuple(tuple(2 * (i == j) for j in range(8)) for i in range(8))
    require(multiply(selected, twice_inverse) == twice_identity, "A H differs from 2I")
    require(multiply(twice_inverse, selected) == twice_identity, "H A differs from 2I")
    return selected


def load_matrix():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    live = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(live) == 3, "unexpected source inventory")
    for row in live:
        path = ROOT / row["path"]
        require(path.stat().st_size <= 2_000_000, "source exceeds resource bound")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "pinned input differs: " + row["path"])
    fixture = ROOT / "research/precision-state-frontier/FIXTURE.json"
    columns = json.loads(fixture.read_text())["mode_columns"]
    require(len(columns) == 8 and all(len(row) == 112 for row in columns),
            "wrong source dimensions")
    matrix = tuple(vector(row, 8, "matrix row") for row in zip(*columns, strict=True))
    require(all(sum(x * x for x in row) == 4 for row in matrix), "wrong row norm")
    gram = multiply(tuple(zip(*matrix)), matrix)
    require(gram == tuple(tuple(56 * (i == j) for j in range(8)) for i in range(8)),
            "wrong source Gram matrix")
    return matrix


def check_scalar_intervals():
    checked = 0
    for s in range(-208, 209):
        lower, upper = -((26 + s) // 4), (26 - s) // 4
        candidates = [q for q in range(lower, upper + 1)
                      if nearest_away(s + 56 * q) == q]
        require(len(candidates) <= 13, "scalar fiber exceeds thirteen")
        require(len({q % 16 for q in candidates}) == len(candidates),
                "sixteen-residue decoding is ambiguous")
        checked += upper - lower + 1
    return checked


def check_roundtrips(matrix):
    count = 0
    for i in range(112):
        for value in (-32, -16, -1, 1, 16, 32):
            z = tuple(value if j == i else 0 for j in range(112))
            y = forward(matrix, z)
            require(recover(matrix, y, tuple(z[k] % 32 for k in OWNERS)) == z,
                    "basis roundtrip failed")
            count += 1
    for i in OWNERS:
        for value in range(32):
            z = tuple(value if j == i else 0 for j in range(112))
            require(recover(matrix, forward(matrix, z), tuple(z[k] % 32 for k in OWNERS)) == z,
                    "residue roundtrip failed")
            count += 1
    rng = random.Random(5444)
    for bits in range(0, 257, 16):
        for _ in range(8):
            z = tuple(rng.randrange(-(1 << bits), 1 << bits) for _ in range(112))
            require(recover(matrix, forward(matrix, z), tuple(z[k] % 32 for k in OWNERS)) == z,
                    "large integer roundtrip failed")
            count += 1
    for _ in range(64):
        z = tuple(rng.randrange(-10**6, 10**6) * (32 if i in OWNERS else 1)
                  for i in range(112))
        require(recover(matrix, forward(matrix, z), (0,) * 8) == z,
                "sparse sublattice roundtrip failed")
        count += 1
    return count


def expect_rejection(call, fragment):
    try:
        call()
    except ValueError as error:
        require(fragment in str(error), "rejected for an unexpected reason")
    else:
        raise ValueError("invalid fixture was accepted: " + fragment)


def check_controls(matrix):
    zero = (0,) * 112
    expect_rejection(lambda: recover(matrix, zero, (1,) + (0,) * 7), "odd doubled")
    expect_rejection(lambda: recover(matrix, zero, (6,) + (0,) * 7), "no quotient")
    expect_rejection(lambda: recover(matrix, zero, (10,) + (0,) * 7), "owner residue differs")
    expect_rejection(lambda: recover(matrix, (26,) + zero[1:], (0,) * 8), "half-tie rule")
    expect_rejection(lambda: recover(matrix, zero, (0,) * 7), "wrong length")
    expect_rejection(lambda: recover(matrix, zero, (32,) + (0,) * 7), "outside")
    expect_rejection(lambda: recover(matrix, zero, (False,) + (0,) * 7), "requires integers")
    expect_rejection(lambda: recover(matrix, zero[:-1], (0,) * 8), "wrong length")
    expect_rejection(lambda: forward(matrix, (1 << 4096,) + zero[1:]), "4096 bits")
    expect_rejection(lambda: certificate(matrix, (6,) + OWNERS[1:]), "A H differs")
    corrupt = ((2,) + TWICE_INVERSE[0][1:],) + TWICE_INVERSE[1:]
    expect_rejection(lambda: certificate(matrix, twice_inverse=corrupt), "A H differs")
    require(nearest_away(26) == 1 and nearest_away(-26) == -1,
            "half ties must round away from zero")
    require(round(Fraction(26, 52)) != nearest_away(26), "tie-even control disappeared")
    return 11


def check_threshold(matrix):
    sums = matvec(matrix, (1,) * 8)
    left, right = tuple(48 * x for x in sums), tuple(56 * x for x in sums)
    require(left != right, "collision inputs coincide")
    require(all(x % 16 == 0 for x in left + right), "four-bit collision leaves lattice")
    expected = tuple(-4 * x for x in sums)
    require(forward(matrix, left) == forward(matrix, right) == expected,
            "four-bit collision fails")
    require(any(left[i] % 32 != right[i] % 32 for i in OWNERS),
            "five-bit residues fail to separate the collision")
    unit = (1,) + (0,) * 111
    require(0 not in OWNERS and all(unit[i] % 32 == 0 for i in OWNERS),
            "strict domain witness leaves sparse lattice")
    require(any(x % 32 for x in unit), "strict domain witness is uniform")
    require(recover(matrix, forward(matrix, unit), (0,) * 8) == unit,
            "strict domain witness fails recovery")
    return {"left": left, "right": right, "output": expected}


def main():
    matrix = load_matrix()
    selected = certificate(matrix)
    determinant, inverse = rational_inverse(selected)
    require(determinant == -16, "wrong selected determinant")
    require(tuple(tuple(2 * x for x in row) for row in inverse) == TWICE_INVERSE,
            "rational inversion differs from the integer certificate")
    combinations = multiply(matrix, inverse)
    require(all(x.denominator == 1 for row in combinations for x in row),
            "selected rows do not span the integer row lattice")
    threshold = check_threshold(matrix)
    report = {"status": "PASS_EIGHT_OWNER_INJECTIVITY", "claim_type": "scoped proof with finite corroboration",
              "owners_zero_based": OWNERS, "selected_determinant": int(determinant),
              "residue_bits": 40, "sharp_equal_bits_per_selected_owner": 5,
              "scalar_candidates_checked": check_scalar_intervals(),
              "literal_roundtrips": check_roundtrips(matrix),
              "rejection_controls": check_controls(matrix),
              "four_bit_collision": threshold,
              "package_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                 for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")}}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
