"""Exact finite corroboration of the written all-field carrier theorem."""

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carrier as c


PACKAGE_FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
                 "VERIFY.json", "carrier.py", "verify.py")


def flatten(matrix):
    return [x for row in matrix for x in row]


def multiply(left, right):
    size = len(left)
    result = c.zero_matrix(size)
    for i in range(size):
        for k in range(size):
            if left[i][k]:
                for j in range(size):
                    result[i][j] += left[i][k] * right[k][j]
    return result


def check_field(f):
    q = f.size
    for x in range(q):
        for y in range(q):
            c.require(f.add[x][y] == f.add[y][x], "addition symmetry")
            c.require(f.mul[x][y] == f.mul[y][x], "multiplication symmetry")
            for z in range(q):
                c.require(f.add[f.add[x][y]][z] == f.add[x][f.add[y][z]],
                          "addition associativity")
                c.require(f.mul[f.mul[x][y]][z] == f.mul[x][f.mul[y][z]],
                          "multiplication associativity")
                c.require(f.mul[x][f.add[y][z]]
                          == f.add[f.mul[x][y]][f.mul[x][z]], "distributivity")
        c.require(f.add[x][0] == x and f.mul[x][1] == x
                  and f.add[x][f.neg[x]] == 0, "field identities")
    return q ** 3


def check_group(f, h, group, hybrid):
    lookup = {g: i for i, g in enumerate(group)}
    c.require(len({c.natural(f, g) for g in group}) == len(group),
              "natural group action is not faithful")
    for i, left in enumerate(group):
        for j, right in enumerate(group):
            result = c.compose(f, left, right)
            c.require(multiply(hybrid[i], hybrid[j]) == hybrid[lookup[result]],
                      "hybrid representation product")
            a, b = c.natural(f, left), c.natural(f, right)
            c.require(tuple(a[b[x]] for x in range(f.size))
                      == c.natural(f, result), "literal affine action product")
    return len(group) ** 2


def check_context(f, h, group, natural, aug, hybrid, modulus):
    count, order = len(group), len(h)
    expected = (count - order + 1, count - order, count)
    observed = tuple(c.rank([flatten(m) for m in bank], modulus)
                     for bank in (natural, aug, hybrid))
    c.require(observed == expected, "algebra span rank mismatch")
    recovered = 0
    for i, matrix in enumerate(hybrid):
        coefficients = [int(j == i) for j in range(count)]
        c.require(c.recover(f, h, matrix, modulus) == coefficients,
                  "basis coefficient reconstruction")
        recovered += 1
    for seed in range(12):
        coefficients = [(seed * i * i + i + seed // 3) % modulus
                        for i in range(count)]
        image = c.linear_combination(hybrid, coefficients, modulus)
        c.require(c.recover(f, h, image, modulus) == coefficients,
                  "mixed coefficient reconstruction")
        recovered += 1
    # Every stated kernel basis has all coefficients enumerated explicitly.
    for a in range(1, order):
        coefficients = [0] * count
        for b in range(f.size):
            coefficients[b] = -1
            coefficients[a * f.size + b] = 1
        c.require(not any(flatten(c.linear_combination(natural, coefficients,
                                                       modulus))),
                  "natural kernel basis is not null")
        c.require(any(flatten(c.linear_combination(hybrid, coefficients, modulus))),
                  "hybrid lost a natural kernel direction")
    return {"field": f.name, "subgroup_order": order, "characteristic": modulus,
            "regular_dimension": count, "carrier_dimension": len(hybrid[0]),
            "ranks_natural_augmentation_hybrid": list(observed),
            "coefficient_vectors_recovered": recovered,
            "kernel_basis_vectors": order - 1}


def rejects(function, expected):
    try:
        function()
    except ValueError as error:
        c.require(str(error) == expected, "unexpected rejection reason")
        return 1
    raise ValueError("missing rejection: " + expected)


def rational_lines(f, h, group, natural):
    """Separate uncompressed rational oracle for the affine line inverse."""
    for seed in range(4):
        coefficients = [Fraction(i * i - seed, seed + 1)
                        for i in range(len(group))]
        matrix = [[sum(coefficient * m[y][x]
                       for coefficient, m in zip(coefficients, natural))
                   for x in range(f.size)] for y in range(f.size)]
        sums = {a: sum(coefficients[i] for i, (t, _) in enumerate(group) if t == a)
                for a in h}
        total = sum(coefficients)
        for i, (a, b) in enumerate(group):
            line = sum(matrix[f.add[f.mul[a][x]][b]][x] for x in range(f.size))
            recovered = (line - total + sums[a]) / f.size
            c.require(recovered == coefficients[i], "rational line inverse")
    return 4 * len(group)


def controls():
    f, h = c.field("F3"), (1, 2)
    group = c.elements(f, h)
    bank = [c.matrices(f, h, g)[2] for g in group]
    # The excluded translation characteristic actually destroys this construction.
    modular_rank = c.rank([flatten(m) for m in bank], 3)
    c.require(modular_rank < len(group), "excluded characteristic control")
    total = 1
    total += rejects(lambda: c.field("F6"), "unsupported finite field")
    total += rejects(lambda: c.subgroup(f, 3), "invalid subgroup order")
    total += rejects(lambda: c.subgroup(f, True), "invalid subgroup order")
    total += rejects(lambda: c.recover(f, h, bank[0], 3),
                     "unsupported coefficient characteristic")
    total += rejects(lambda: c.recover(f, h, [[1]], 2),
                     "wrong carrier matrix shape")
    bad = [row[:] for row in bank[0]]
    bad[0][2] = 1
    total += rejects(lambda: c.recover(f, h, bad, 2), "mixed carrier blocks")
    bad = [row[:] for row in bank[0]]
    bad[2][3] = 1
    total += rejects(lambda: c.recover(f, h, bad, 2),
                     "matrix is outside the carrier algebra")
    total += rejects(lambda: c.linear_combination(bank, [1], 2),
                     "coefficient length mismatch")
    return total, modular_rank


def run():
    rows, group_pairs, field_triples, rational_coefficients = [], 0, 0, 0
    for name in c.SPECS:
        f = c.field(name)
        field_triples += check_field(f)
        for order in range(1, f.size):
            if (f.size - 1) % order:
                continue
            h = c.subgroup(f, order)
            group = c.elements(f, h)
            triples = [c.matrices(f, h, g) for g in group]
            natural, aug, hybrid = ([t[i] for t in triples] for i in range(3))
            group_pairs += check_group(f, h, group, hybrid)
            rational_coefficients += rational_lines(f, h, group, natural)
            for modulus in (2, 3, 5, 7):
                if modulus != f.prime:
                    rows.append(check_context(f, h, group, natural, aug,
                                              hybrid, modulus))
    control_count, excluded_rank = controls()
    package = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in PACKAGE_FILES}
    return {"status": "PASS_AFFINE_ALGEBRA_MINIMAL_CARRIER", "errors": 0,
            "contexts": len(rows), "group_product_pairs": group_pairs,
            "field_triples": field_triples, "controls": control_count,
            "rational_coefficients_recovered": rational_coefficients,
            "excluded_F3_S3_rank": excluded_rank, "results": rows,
            "package_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.receipt is not None:
        destination = args.receipt.resolve()
        checkout = Path(__file__).resolve().parents[2]
        c.require(not destination.is_relative_to(checkout),
                  "receipt must be outside the checkout")
    result = run()
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt is not None:
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    print(rendered, end="")
    print("PASS_AFFINE_ALGEBRA_MINIMAL_CARRIER")


if __name__ == "__main__":
    main()
