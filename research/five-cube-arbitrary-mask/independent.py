#!/usr/bin/env python3
"""Separate Walsh/Fraction and literal binary-matrix replay; Apache-2.0.

Hanson Sun, with substantial OpenAI Codex assistance. This file imports no
primary-checker or predecessor implementation. This is not separate authorship.
"""
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import random
import sys

PACKAGE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def rational_rank(rows):
    a = [[Fraction(x) for x in row] for row in rows]
    if not a:
        return 0
    lead = 0
    for column in range(len(a[0])):
        found = [r for r in range(lead, len(a)) if a[r][column] != 0]
        if not found:
            continue
        a[lead], a[found[0]] = a[found[0]], a[lead]
        pivot = a[lead][column]
        a[lead] = [v / pivot for v in a[lead]]
        for r in range(lead + 1, len(a)):
            amount = a[r][column]
            if amount:
                a[r] = [v - amount * u for u, v in zip(a[lead], a[r])]
        lead += 1
        if lead == len(a):
            break
    return lead


def binary_rank(matrix):
    a = [row[:] for row in matrix]
    rank = 0
    if not a:
        return 0
    for column in range(len(a[0])):
        candidates = [i for i in range(rank, len(a)) if a[i][column]]
        if not candidates:
            continue
        a[rank], a[candidates[0]] = a[candidates[0]], a[rank]
        for i in range(len(a)):
            if i != rank and a[i][column]:
                a[i] = [(u + v) % 2 for u, v in zip(a[i], a[rank])]
        rank += 1
    return rank


def bits(value, width):
    return [int(c) for c in format(value, f"0{width}b")[::-1]]


def evaluate(coefficients, parity, h):
    return sum(x * y for x, y in zip(coefficients, (1 - parity, parity, h))) % 2


def domain():
    coords = tuple(combinations(range(5), 3))[42 % 10]
    tables = set()
    ports = [bits(x, 5) for x in range(32)]
    for values in product((0, 1), repeat=8):
        tables.add(sum(values[sum(port[c] * (2 ** i) for i, c in enumerate(coords))] * (2 ** x)
                       for x, port in enumerate(ports)))
    for subset in range(32):
        tables.add(sum(int(all(port[c] for c in range(5) if bits(subset, 5)[c])) * (2 ** x)
                       for x, port in enumerate(ports)))
    tables.add(sum((sum(port) % 2) * (2 ** x) for x, port in enumerate(ports)))
    tables.add(sum((1 - sum(port) % 2) * (2 ** x) for x, port in enumerate(ports)))
    generator = random.Random(42)
    for _ in range(42):
        tables.add(generator.getrandbits(32))
    return coords, sorted(tables)


def projection(matrix, i, j):
    rows = [[1, 0, i], [0, 1, j]]
    return [[sum(u[r] * matrix[r][s] * v[s] for r in range(3) for s in range(3)) % 2
             for v in rows] for u in rows]


def polynomial_degree(values):
    # Coefficient of x^S is the XOR of function values at all subsets of S.
    degree = -1
    for subset in range(32):
        coefficient = sum(values[t] for t in range(32) if (t | subset) == subset) % 2
        if coefficient:
            degree = max(degree, sum(bits(subset, 5)))
    return degree


def run():
    certificate = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for record in sources["files"]:
        if record["usage"] == "input":
            data = (PACKAGE.parents[1] / record["path"]).read_bytes()
            check(hashlib.sha256(data).hexdigest() == record["sha256"], "changed source")
    # Independent construction: all Walsh characters of degree at most two.
    ports = [bits(x, 5) for x in range(32)]
    monomials = [s for s in range(32) if sum(bits(s, 5)) <= 2]
    labels = [[(-1) ** sum(a * b for a, b in zip(port, bits(s, 5))) for s in monomials]
              for port in ports]
    gram = [[sum(u * v for u, v in zip(x, y)) for y in labels] for x in labels]
    parity = [sum(x) % 2 for x in ports]
    for x, y in product(range(32), repeat=2):
        common = sum(a == b for a, b in zip(ports[x], ports[y]))
        check(gram[x][y] == 2 * (common - 1) * (common - 3), "Walsh/quadratic Gram identity")
    check(rational_rank(gram) == 16, "Walsh Gram rank")
    for p in range(2):
        group = [i for i in range(32) if parity[i] == p]
        check(all(gram[x][y] == 16 * int(x == y) for x in group for y in group), "Walsh parity basis")

    coefficients = [bits(a, 3) for a in range(1, 8)]
    potentials = [[] for _ in range(5)]
    matrices = []
    for state in range(512):
        flat = bits(state, 9)
        matrix = [flat[3 * i:3 * i + 3] for i in range(3)]
        matrices.append(matrix)
        for i, j in product(range(2), repeat=2):
            potentials[2 * i + j].append(binary_rank(projection(matrix, i, j)))
        potentials[4].append(2 * binary_rank(matrix))
    check(potentials == certificate["primitives"]["potentials"], "potential table")
    edge_count = 0
    for a in coefficients:
        for b in coefficients:
            delta = sum(a[i] * b[j] * (2 ** (3 * i + j)) for i in range(3) for j in range(3))
            prices = []
            for i, j in product(range(2), repeat=2):
                va = [evaluate(a, 0, i), evaluate(a, 1, j)]
                vb = [evaluate(b, 0, i), evaluate(b, 1, j)]
                prices.append(binary_rank([[x * y for y in vb] for x in va]))
            prices.append(2)
            for state in range(512):
                for k, price in enumerate(prices):
                    check(abs(potentials[k][state ^ delta] - potentials[k][state]) <= price,
                          "edge exceeds rank price")
                    edge_count += 1
    check(edge_count == 125440 == certificate["coverage"]["binary_edge_inequalities"], "edge coverage")

    coords, masks = domain()
    check(list(coords) == certificate["coordinates"], "coordinate selection")
    check([f"{m:08x}" for m in masks] == [f["mask"] for f in certificate["fixtures"]], "mask coverage")
    rank_count = 0
    degenerate = []
    for mask, fixture in zip(masks, certificate["fixtures"]):
        values = bits(mask, 32)
        check(polynomial_degree(values) == fixture["degree"], "mask degree")
        cells = [[[x for x in range(32) if parity[x] == p and values[x] == h]
                  for h in range(2)] for p in range(2)]
        intersections = [[len(cells[0][i]) + len(cells[1][j])
                          - rational_rank([labels[x] for x in cells[0][i] + cells[1][j]])
                          for j in range(2)] for i in range(2)]
        remaining = 16 - sum(sum(row) for row in intersections)
        check(remaining >= 0 and remaining % 2 == 0, "intersection dimensions")
        generic = remaining // 2
        check(intersections == fixture["intersections"] and generic == fixture["generic_planes"],
              "component multiplicities")
        supports = [[x for x in range(32) if evaluate(a, parity[x], values[x])] for a in coefficients]
        actual_ranks = []
        for left in supports:
            for right in supports:
                actual_ranks.append(rational_rank([[gram[x][y] for y in right] for x in left]))
                rank_count += 1
        check(actual_ranks == fixture["ranks"], "Fraction pairing ranks")
        for x, y in product(range(32), repeat=2):
            check((int(x in supports[0] and y in supports[0])
                   + int(x in supports[1] and y in supports[1])) % 2 == int(parity[x] == parity[y]),
                  "full parity identity")
        check(actual_ranks[0] + actual_ranks[8] == 32, "attaining cost")
        evaluations = [[1 - parity[x], parity[x], values[x]] for x in range(32)]
        if binary_rank(evaluations) == 2:
            patterns = sorted(set(tuple(row) for row in evaluations))
            accepted = []
            for state, matrix in enumerate(matrices):
                image = [[sum(u[i] * matrix[i][j] * v[j] for i in range(3) for j in range(3)) % 2
                          for v in patterns] for u in patterns]
                if image != [[1, 0], [0, 1]]:
                    continue
                weighted = sum(intersections[i][j] * potentials[2 * i + j][state]
                               for i in range(2) for j in range(2))
                check(generic == 0 and weighted == 32, "degenerate coefficient lift")
                accepted.append(state)
            check(len(accepted) == 32, "degenerate fiber size")
            degenerate.append({"mask": f"{mask:08x}", "states": accepted})
    check(rank_count == certificate["coverage"]["ordered_rational_ranks"], "rank coverage")
    check(degenerate == certificate["degenerate_lifts"], "degenerate lift coverage")
    # Independent boundary checks, with literal matrices rather than rank formulas.
    check(binary_rank([[1, 0], [0, 1]]) == 2 and binary_rank([[1, 1], [1, 1]]) == 1,
          "all-pairs target cannot be replaced by one all-ones total")
    check(rational_rank([[1, 1], [1, 1]]) == 1, "endpoint angle is not generic")
    check(rational_rank([[1] * 16 for _ in range(16)]) * 2 == 2, "changed Gram boundary")
    print(f"PASS_INDEPENDENT_WALSH_FRACTION masks={len(masks)} ranks={rank_count} "
          f"edges={edge_count} degenerate_lifts={sum(len(x['states']) for x in degenerate)} floor=32 no_new_kappa")


if __name__ == "__main__":
    try:
        run()
    except (ValueError, OSError, KeyError) as error:
        print("FAIL_INDEPENDENT_WALSH_FRACTION: " + str(error), file=sys.stderr)
        raise SystemExit(1)
