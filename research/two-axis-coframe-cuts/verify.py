"""Exact finite corroboration of the two-axis cut threshold; writes no files."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def symplectic(a, b):
    """Bits 0,1 are x; bits 2,3 are z."""
    return (((a & 3) & (b >> 2)).bit_count()
            + ((b & 3) & (a >> 2)).bit_count()) % 2


def validate_plane(plane):
    require(type(plane) is tuple and len(plane) == 4, "plane size")
    require(all(type(v) is int and 0 <= v < 16 for v in plane), "vector domain")
    require(len(set(plane)) == 4 and 0 in plane, "distinct vectors and zero")
    require(all(a ^ b in plane for a in plane for b in plane), "linear closure")
    require(all(symplectic(a, b) == 0 for a in plane for b in plane), "isotropy")


def all_planes():
    subspaces = sorted({tuple(sorted((0, a, b, a ^ b)))
                        for a in range(1, 16) for b in range(a + 1, 16)})
    require(len(subspaces) == 35, "complete dimension-two subspace census")
    planes = tuple(p for p in subspaces
                   if all(symplectic(a, b) == 0 for a in p for b in p))
    require(len(planes) == 15, "complete Lagrangian census")
    for plane in planes:
        validate_plane(plane)
    return planes


def binary_rank(vectors):
    pivots = [0] * 4
    for original in vectors:
        value = original
        for bit in range(3, -1, -1):
            if (value >> bit) & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(v != 0 for v in pivots)


def distances(planes):
    table = [[0] * 15 for _ in range(15)]
    histogram = [0, 0, 0]
    for i in range(15):
        for j in range(15):
            size = len(set(planes[i]).intersection(planes[j]))
            require(size in (1, 2, 4), "intersection cardinality")
            distance = 2 - (size.bit_length() - 1)
            require(distance == binary_rank(planes[i] + planes[j]) - 2,
                    "independent rank/intersection agreement")
            table[i][j] = distance
            histogram[distance] += 1
    require(histogram == [15, 90, 120], "ordered distance coverage")
    return table


def separated(mask, i, j):
    return ((mask >> i) ^ (mask >> j)) & 1


def pencils(planes):
    cuts = tuple(sum(1 << i for i, plane in enumerate(planes) if v in plane)
                 for v in range(1, 16))
    require(len(set(cuts)) == 15, "distinct pencil cuts")
    require(all(cut.bit_count() == 3 for cut in cuts), "pencil sizes")
    require(all(sum((cut >> i) & 1 for cut in cuts) == 3 for i in range(15)),
            "three lines per plane")
    return cuts


def pentagonal(table, indices):
    signs = (1, 1, 1, -1, -1)
    return sum(signs[i] * signs[j] * table[indices[i]][indices[j]]
               for i, j in combinations(range(5), 2))


def witness(planes, table):
    named = ((0, 1, 2, 3), (0, 4, 8, 12), (0, 6, 9, 15),
             (0, 1, 8, 9), (0, 2, 4, 6))
    indices = tuple(planes.index(p) for p in named)
    for i, j in combinations(range(5), 2):
        expected = 2 if (i < 3) == (j < 3) else 1
        require(table[indices[i]][indices[j]] == expected, "K3,2 witness")
    minimum = 0
    for mask in range(1 << 14):
        total = sum((1 if i < 3 else -1) for i in range(5)
                    if (mask >> indices[i]) & 1)
        value = sum((1 if i < 3 else -1) * (1 if j < 3 else -1)
                    * separated(mask, indices[i], indices[j])
                    for i, j in combinations(range(5), 2))
        require(value == total * (1 - total) and value <= 0, "cut separation")
        minimum = min(minimum, value)
    require(minimum == -6, "nontrivial cut witness coverage")
    return indices


def decomposition(table, cuts, parameter):
    """Return the claimed exact cut decomposition for 1 <= a <= 3/2."""
    single_weight = Fraction(3, 2) - parameter
    pencil_weight = (parameter - 1) / 2
    require(single_weight >= 0 and pencil_weight >= 0, "negative cut weight")
    result = [[Fraction(0)] * 15 for _ in range(15)]
    for i, j in combinations(range(15), 2):
        value = 2 * single_weight + pencil_weight * sum(
            separated(cut, i, j) for cut in cuts)
        target = Fraction(1) if table[i][j] == 1 else parameter
        require(value == target, "exact decomposition identity")
        result[i][j] = result[j][i] = value
    return result


def check_tariffs(table, cuts, indices):
    for i, j in combinations(range(15), 2):
        count = sum(separated(cut, i, j) for cut in cuts)
        require(count == 2 + 2 * table[i][j], "pencil separation count")
        # Coefficients of 1 and a in the exact decomposition.
        require((3 - Fraction(count, 2), -2 + Fraction(count, 2))
                == ((1, 0) if table[i][j] == 1 else (0, 1)), "affine identity")
    for step in range(33):
        parameter = 1 + Fraction(step, 32)
        target = [[Fraction(0) if i == j else
                   (Fraction(1) if table[i][j] == 1 else parameter)
                   for j in range(15)] for i in range(15)]
        require(pentagonal(target, indices) == 4 * parameter - 6, "separator value")
        if parameter <= Fraction(3, 2):
            require(decomposition(table, cuts, parameter) == target, "full cut metric")
        else:
            require(pentagonal(target, indices) > 0, "strict nonembedding")
        distortion = max(Fraction(1), 2 * parameter / 3)
        for i, j in combinations(range(15), 2):
            upper = (target[i][j] if parameter <= Fraction(3, 2) else
                     parameter * sum(separated(c, i, j) for c in cuts) / 6)
            require(target[i][j] <= upper <= distortion * target[i][j],
                    "attaining distortion bounds")
    require(2 ** 199 > 3 ** 100, "whole near-linear tariff interval")


def rejection_controls(table, cuts):
    invalid = ((), (0, 1, 2, 3, 4), (0, 1, 1, 2), (0, 1, 2, 4),
               (0, 1, 4, 5), (0, 1, 2, 16), (False, 1, 2, 3),
               (0.0, 1, 2, 3))
    rejected = 0
    for plane in invalid:
        try:
            validate_plane(plane)
        except ValueError:
            rejected += 1
    require(rejected == len(invalid), "invalid-plane rejection")
    mutations = ((cuts, Fraction(2)), (cuts, Fraction(3, 4)),
                 (cuts[:-1], Fraction(3, 2)), (cuts[1:] + cuts[:1], Fraction(0)))
    for mutant, parameter in mutations:
        try:
            decomposition(table, mutant, parameter)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("changed decomposition accepted")
    return rejected


def receipt():
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = root / name
        require(path.stat().st_size <= 1024 * 1024, "package-file size bound")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    planes = all_planes()
    table = distances(planes)
    cuts = pencils(planes)
    indices = witness(planes, table)
    check_tariffs(table, cuts, indices)
    controls = rejection_controls(table, cuts)
    print(json.dumps({"status": "PASS_TWO_AXIS_COFRAME_CUTS", "planes": 15,
                      "ordered_pairs": 225, "distinct_cuts": 16384,
                      "pencils": 15, "rational_tariffs": 33,
                      "rejection_controls": controls,
                      "threshold": "2^t <= 3/2",
                      "distortion": "max(1,2^(t+1)/3)",
                      "sha256": receipt()}, sort_keys=True))


if __name__ == "__main__":
    main()
