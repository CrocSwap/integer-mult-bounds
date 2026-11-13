#!/usr/bin/env python3
"""All-rank binary dual-polar cut theorem: exact finite corroboration.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def domain(m, j):
    require(type(m) is int and 1 <= m <= 128, "checker rank must be 1..128")
    require(type(j) is int and 0 <= j <= m, "checker sector must be 0..rank")


def intersection(m, i):
    return (1 << i) - 1, (1 << i) - 1, (1 << (m + 1)) - (1 << (i + 1))


def theta(m, j):
    domain(m, j)
    return (1 << (m - j + 1)) - (1 << j) - 1


def polynomial(m, j):
    domain(m, j)
    coefficients = [1]
    factors = [1 << r for r in range(1, m - j + 1)]
    factors += [-(1 << r) for r in range(j)]
    for factor in factors:
        updated = [0] * (len(coefficients) + 1)
        for i, value in enumerate(coefficients):
            updated[i] += value
            updated[i + 1] += factor * value
        coefficients = updated
    return tuple(coefficients)


def check_coefficients(m, eigenvalue, coefficients):
    require(len(coefficients) == m + 1, "polynomial degree")
    require(coefficients[0] == 1, "constant coefficient")
    for i in range(m + 1):
        _, a_i, _ = intersection(m, i)
        left = eigenvalue * coefficients[i]
        right = a_i * coefficients[i]
        if i > 0:
            _, _, b_previous = intersection(m, i - 1)
            right += b_previous * coefficients[i - 1]
        if i < m:
            c_next, _, _ = intersection(m, i + 1)
            right += c_next * coefficients[i + 1]
        require(left == right, "distance eigenvalue recurrence")


def spectral_ratio(m, j):
    domain(m, j)
    require(j != 0, "constant sector has zero denominator")
    degree = 2 * ((1 << m) - 1)
    opposite = Fraction((-1) ** j, 1 << (j * (m - j + 1)))
    return (1 - opposite) / (1 - Fraction(theta(m, j), degree))


def algebra_checks():
    coefficient_rows = 0
    polynomials = 0
    for m in range(1, 49):
        for j in range(m + 1):
            coefficients = polynomial(m, j)
            check_coefficients(m, theta(m, j), coefficients)
            exponent = m * (m + 1) // 2 - j * (m - j + 1)
            require(coefficients[-1] == (-1) ** j * (1 << exponent), "top coefficient")
            coefficient_rows += m + 1
            polynomials += 1
    ratios = 0
    for m in range(1, 129):
        ceiling = Fraction((1 << m) - 1, 1 << (m - 1))
        require(all(theta(m, j) > theta(m, j + 1) for j in range(m)), "distinct roots")
        for j in range(1, m + 1):
            ratio = spectral_ratio(m, j)
            require(ratio <= ceiling, "spectral ceiling")
            require((ratio == ceiling) == (j == 1), "unique maximizing sector")
            ratios += 1
    return {"polynomials": polynomials, "coefficient_rows": coefficient_rows,
            "nonconstant_spectral_ratios": ratios}


def pairing(x, y, m):
    low = (1 << m) - 1
    return (((x & low) & (y >> m)).bit_count()
            + ((y & low) & (x >> m)).bit_count()) % 2


def lagrangians(m):
    require(type(m) is int and 1 <= m <= 3, "geometric fixture rank must be 1..3")
    layer = {(0,)}
    for dimension in range(m):
        updated = set()
        for space in sorted(layer):
            for vector in range(1, 1 << (2 * m)):
                if vector in space or any(pairing(vector, x, m) for x in space):
                    continue
                extended = tuple(sorted((*space, *(x ^ vector for x in space))))
                require(len(extended) == 1 << (dimension + 1), "span dimension")
                updated.add(extended)
        require(len(updated) <= 315, "bounded isotropic layer")
        layer = updated
    return tuple(sorted(layer))


def graph(spaces, m):
    size = len(spaces)
    distances = []
    for left in spaces:
        row = []
        for right in spaces:
            common = len(set(left).intersection(right))
            require(common > 0 and common & (common - 1) == 0, "intersection dimension")
            row.append(m - (common.bit_length() - 1))
        distances.append(tuple(row))
    masks = tuple(tuple(sum(1 << v for v in range(size) if distances[u][v] == i)
                        for u in range(size)) for i in range(m + 1))
    return tuple(distances), masks


def check_geometry(distances, masks, m):
    size = len(distances)
    degrees = [1]
    for i in range(1, m + 1):
        c_i, _, _ = intersection(m, i)
        _, _, b_previous = intersection(m, i - 1)
        quotient, remainder = divmod(degrees[-1] * b_previous, c_i)
        require(remainder == 0, "sphere integrality")
        degrees.append(quotient)
    require(sum(degrees) == size, "geometric vertex count")
    for u in range(size):
        require([mask[u].bit_count() for mask in masks] == degrees, "sphere sizes")
        for v in range(size):
            i = distances[u][v]
            counts = [0] * (m + 1)
            for w in range(size):
                if masks[1][v] >> w & 1:
                    counts[distances[u][w]] += 1
            expected = [0] * (m + 1)
            c_i, a_i, b_i = intersection(m, i)
            expected[i] = a_i
            if i > 0:
                expected[i - 1] = c_i
            if i < m:
                expected[i + 1] = b_i
            require(counts == expected, "literal geometric intersection array")
    require(degrees[-1] == 1 << (m * (m + 1) // 2), "opposite valency")
    return size * size


def exits(subset, neighbors):
    complement = ((1 << len(neighbors)) - 1) ^ subset
    return sum((row & complement).bit_count() for v, row in enumerate(neighbors)
               if subset >> v & 1)


def cut_ratio(subset, masks, m):
    edge_exits = exits(subset, masks[1])
    require(edge_exits > 0, "nontrivial connected cut")
    opposite_exits = exits(subset, masks[m])
    return Fraction(opposite_exits * masks[1][0].bit_count(),
                    edge_exits * masks[m][0].bit_count())


def geometric_checks():
    reports = []
    for m in range(1, 4):
        spaces = lagrangians(m)
        distances, masks = graph(spaces, m)
        cells = check_geometry(distances, masks, m)
        ceiling = Fraction((1 << m) - 1, 1 << (m - 1))
        point_cuts = 0
        for point in range(1, 1 << (2 * m)):
            subset = sum(1 << v for v, space in enumerate(spaces) if point in space)
            require(cut_ratio(subset, masks, m) == ceiling, "attaining point cut")
            point_cuts += 1
        all_cuts = 0
        attaining_cuts = 0
        if m <= 2:
            for subset in range(1, (1 << len(spaces)) - 1):
                ratio = cut_ratio(subset, masks, m)
                require(ratio <= ceiling, "literal Boolean-cut ceiling")
                attaining_cuts += ratio == ceiling
                all_cuts += 1
        reports.append({"rank": m, "vertices": len(spaces), "pair_cells": cells,
                        "point_cuts": point_cuts, "all_nontrivial_cuts": all_cuts,
                        "attaining_enumerated_cuts": attaining_cuts})
    return reports


def controls():
    rejected = 0
    for m, j, position in ((3, 1, 0), (4, 2, 1), (3, 2, 3)):
        changed = list(polynomial(m, j))
        changed[position] += 1
        try:
            check_coefficients(m, theta(m, j), changed)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("polynomial mutant survived")
    try:
        check_coefficients(4, theta(4, 1) + 1, polynomial(4, 1))
    except ValueError:
        rejected += 1
    else:
        raise ValueError("edge eigenvalue mutant survived")
    for m in (2, 3, 17, 128):
        false_ceiling = Fraction((1 << m) - 2, 1 << (m - 1))
        require(spectral_ratio(m, 1) > false_ceiling, "false smaller ceiling")
        rejected += 1
    invalid = ((0, 0), (129, 1), (3, -1), (3, 4), (True, 1), (3, False), (2.0, 1))
    for m, j in invalid:
        try:
            polynomial(m, j)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid checker input survived")
    require(rejected == 15, "complete control count")
    return rejected


def package_hashes():
    package = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.is_file() and not path.is_symlink(), "regular package file")
        require(path.stat().st_size <= 131072, "bounded package file")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    require(len(sys.argv) == 1, "no command-line arguments accepted")
    report = {"claim_type": "scoped written proof with exact finite corroboration",
              "algebra": algebra_checks(), "geometry": geometric_checks(),
              "rejecting_controls": controls(), "sha256": package_hashes()}
    print(json.dumps(report, sort_keys=True))
    print("PASS_BINARY_DUAL_POLAR_CUT_CEILING")


if __name__ == "__main__":
    main()
