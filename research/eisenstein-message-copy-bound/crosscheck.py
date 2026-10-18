#!/usr/bin/env python3
"""Independent arithmetic check on the literal certificate's finite premises.

Imports neither geometry.py nor verify.py. Reconstructs bases from the original
root generators, then uses rank modulo 101 to certify every primal inequality.
This checks the certificate's arithmetic, not enumeration completeness or the
all-width transcript proof (those are established by the main replay/proof).
"""

from fractions import Fraction
import json
from pathlib import Path


def check(ok, message):
    if not ok:
        raise ValueError(message)


def indices(mask):
    return [i for i in range(40) if mask & (1 << i)]


def modular_rank(matrix, p=101):
    if not matrix:
        return 0
    a = [[x % p for x in row] for row in matrix]
    row = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(row, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        inverse = pow(a[row][col], -1, p)
        a[row] = [(x * inverse) % p for x in a[row]]
        for i in range(row + 1, len(a)):
            multiplier = a[i][col]
            a[i] = [(x - multiplier * y) % p for x, y in zip(a[i], a[row])]
        row += 1
        if row == len(a):
            break
    return row


def fraction_rank(matrix):
    if not matrix:
        return 0
    columns = [list(map(Fraction, column)) for column in zip(*matrix)]
    pivot = 0
    for coordinate in range(len(matrix)):
        target = next((j for j in range(pivot, len(columns)) if columns[j][coordinate]), None)
        if target is None:
            continue
        columns[pivot], columns[target] = columns[target], columns[pivot]
        scale = columns[pivot][coordinate]
        columns[pivot] = [x / scale for x in columns[pivot]]
        for j in range(pivot + 1, len(columns)):
            scale = columns[j][coordinate]
            columns[j] = [x - scale * y for x, y in zip(columns[j], columns[pivot])]
        pivot += 1
        if pivot == len(columns):
            break
    return pivot


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def main():
    receipt = json.loads((Path(__file__).resolve().parent / "certificate.json").read_text())
    reps = receipt["geometry"]["representatives"]
    g = receipt["geometry"]["rotation4"]
    lines = [[r, [dot(row, r) for row in g]] for r in reps]
    flats = receipt["certificate"]["flats"]
    # A full set of original integer generators avoids using primary RREF rows.
    bases = [[r for t in f["generators"] for r in lines[t]] for f in flats]
    for f, rows in zip(flats, bases):
        check(fraction_rank(rows) == 2 * f["rank"], "independent flat rank differs")
    cliques = [q for q in receipt["certificate"]["maximal_cliques"] if q.bit_count() == 7]
    check(len(cliques) == 2880, "wrong seven-clique count")
    for q in cliques:
        ids = indices(q)
        for i in ids:
            for j in ids:
                if i != j:
                    check(any(dot(x, y) for x in lines[i] for y in lines[j]), "non-clique in receipt")
    hit_masks = [sum(1 << k for k, q in enumerate(cliques) if q & f["mask"]) for f in flats]
    checked, fraction_cases = 0, 0
    for i, f in enumerate(flats):
        for j in range(i, len(flats)):
            numerator = 24 * (f["mask"] & flats[j]["mask"]).bit_count() + (hit_masks[i] & hit_masks[j]).bit_count()
            gram = [[dot(x, y) for y in bases[j]] for x in bases[i]]
            # Reduction mod p cannot increase rational rank. Rational rank is
            # even by J-invariance, so rounding an odd modular rank up to the
            # next even value is valid in Eisenstein rank units.
            lower = (modular_rank(gram) + 1) // 2
            check(numerator <= 960 * lower, "modular witness does not certify inequality")
            checked += 1
            if (f["rank"] == flats[j]["rank"] == 3 and numerator == 1920) or i == j == len(flats) - 1:
                exact = fraction_rank(gram)
                check(exact % 2 == 0 and exact // 2 == lower, "Fraction pairing rank differs")
                fraction_cases += 1
    check(checked == 298378 and fraction_cases == 241, "independent coverage changed")
    for t in range(40):
        check(Fraction(1, 40) + Fraction(sum(bool(q & 1 << t) for q in cliques), 960) == Fraction(11, 20), "nonuniform demand coefficient")
    # Finite derivative and inverse checks use a different Boolean expression
    # from the full network implementation.
    permutation = [z ^ (((z & 1) * ((z >> 1) & 1)) << 2) for z in range(8)]
    check(len(set(permutation)) == 8 and all(permutation[permutation[z]] == z for z in range(8)), "nonlinear inverse failed")
    check(permutation[0] ^ permutation[1] ^ permutation[2] ^ permutation[3] == 4, "map is affine")
    print("PASS_INDEPENDENT_MESSAGE_GEOMETRY: 298378 modular inequalities; 772 Fraction flat ranks; 241 Fraction pair ranks; demand weight 11/20")


if __name__ == "__main__":
    main()
