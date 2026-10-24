#!/usr/bin/env python3
"""Exact antipodal spinor LP optimum; produced by Nick Petalas, Apache-2.0."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations
import json
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def krawtchouk(k, distance):
    return sum((-1) ** j * comb(distance, j) * comb(16 - distance, k - j)
               for j in range(max(0, k + distance - 16), min(k, distance) + 1))


def polynomial_coefficients(distance):
    coefficients = [1] + [0] * 16
    for step in range(16):
        sign = -1 if step < distance else 1
        for degree in range(step + 1, 0, -1):
            coefficients[degree] += sign * coefficients[degree - 1]
    return coefficients


def distribution(x, y, z):
    return [F(1), F(0), x, F(0), F(0), F(0), y, F(0), z,
            F(0), y, F(0), F(0), F(0), x, F(0), F(1)]


def transforms(values):
    return [sum(values[i] * krawtchouk(k, i) for i in range(17))
            for k in range(17)]


def validate(values):
    require(len(values) == 17, "distribution length")
    require(values[0] == values[16] == 1, "antipodal normalization")
    allowed = {0, 2, 6, 8, 10, 14, 16}
    for i in range(17):
        require(values[i] >= 0, "negative distance count")
        require(i in allowed or values[i] == 0, "forbidden distance")
        require(values[i] == values[16 - i], "antipodal symmetry")
    result = transforms(values)
    require(all(value >= 0 for value in result), "negative transform")
    return result


def determinant(matrix):
    result = 0
    for order in permutations(range(3)):
        inversions = sum(order[i] > order[j]
                         for i in range(3) for j in range(i + 1, 3))
        product = (-1) ** inversions
        for row in range(3):
            product *= matrix[row][order[row]]
        result += product
    return result


def check_certificate():
    for distance in range(17):
        coefficients = polynomial_coefficients(distance)
        require(coefficients == [krawtchouk(k, distance) for k in range(17)],
                "independent polynomial coefficients")
    optimum = F(18432, 29)
    point = distribution(F(750, 29), F(2002, 29), F(12870, 29))
    expected = [F(0)] * 17
    expected[0] = expected[16] = optimum
    expected[4] = expected[12] = F(931840, 29)
    require(validate(point) == expected, "exact primal transforms")
    require(sum(point) == optimum, "primal objective")
    weights = (F(25, 116), F(1, 116), F(1, 58))
    degrees = (2, 6, 8)
    # Compare every coefficient of the affine identity, not just the optimizer.
    probes = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    for probe in probes:
        values = distribution(*map(F, probe))
        result = transforms(values)
        gap = sum(weights[j] * result[degrees[j]] for j in range(3))
        require(optimum - sum(values) == gap, "affine dual gap identity")
    rows = [[128, 0, -8], [0, 128, -56], [-1716, -180, 70]]
    require(determinant(rows) == -1900544, "unique active-constraint solution")
    require(all(weight > 0 for weight in weights), "strict dual support")
    return point, expected


def check_literal_code():
    code = (0, 3, 65532, 65535)
    values = [F(0)] * 17
    for left in code:
        for right in code:
            values[(left ^ right).bit_count()] += F(1, len(code))
    validate(values)
    require(values == distribution(F(1), F(0), F(0)), "four-word code")
    return values


def check_rejections(point):
    mutants = []
    changed = point.copy()
    changed[2] += 1
    mutants.append(changed)
    changed = point.copy()
    changed[8] += 1
    mutants.append(changed)
    changed = point.copy()
    changed[16] = 0
    mutants.append(changed)
    changed = point.copy()
    changed[4] = changed[12] = 1
    mutants.append(changed)
    changed = point.copy()
    changed[2] = changed[14] = -1
    mutants.append(changed)
    for changed in mutants:
        rejected = False
        try:
            validate(changed)
        except ValueError:
            rejected = True
        require(rejected, "invalid distribution accepted")
    return len(mutants)


def main():
    point, result = check_certificate()
    check_literal_code()
    controls = check_rejections(point)
    root = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = root / name
        require(path.stat().st_size <= 1024 * 1024, "receipt file capacity")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"files": hashes, "optimizer": list(map(str, point)),
                      "transforms": list(map(str, result)), "controls": controls},
                     sort_keys=True))
    print("PASS_ANTIPODAL_SPINOR_LP_OPTIMUM optimum=18432/29 unique=1 "
          f"transforms=17 controls={controls} no_new_kappa")


if __name__ == "__main__":
    main()
