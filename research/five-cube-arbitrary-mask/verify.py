#!/usr/bin/env python3
"""Exact finite premises for PROOF.md; not a proof by sampling. Apache-2.0.

Hanson Sun, with substantial OpenAI Codex assistance. No predecessor imports.
"""
import argparse
from collections import Counter
from functools import reduce
import hashlib
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import random
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 42
TARGET = 17  # diag(1,1,0), row-major bits of a 3 by 3 binary matrix.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank_q(matrix):
    """Exact integer elimination with gcd normalization; not modular rank."""
    a = [list(row) for row in matrix]
    if not a:
        return 0
    n, k = len(a[0]), 0
    require(all(len(row) == n for row in a), "ragged matrix")
    for j in range(n):
        pivot_row = next((i for i in range(k, len(a)) if a[i][j]), None)
        if pivot_row is None:
            continue
        a[k], a[pivot_row] = a[pivot_row], a[k]
        divisor = reduce(gcd, a[k][j:], 0)
        if divisor > 1:
            a[k][j:] = [v // divisor for v in a[k][j:]]
        pivot = a[k][j]
        for i in range(k + 1, len(a)):
            value = a[i][j]
            if not value:
                continue
            divisor = gcd(pivot, value)
            left, right = pivot // divisor, value // divisor
            row = [left * a[i][z] - right * a[k][z] for z in range(j + 1, n)]
            divisor = reduce(gcd, row, 0)
            if divisor > 1:
                row = [v // divisor for v in row]
            a[i][j:] = [0] + row
        k += 1
        if k == len(a):
            break
    return k


def rank_binary(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def dyad(a, b):
    return sum(((a >> i & 1) * (b >> j & 1)) << (3 * i + j)
               for i in range(3) for j in range(3))


def bilinear(u, state, v):
    return sum((u >> i & 1) * (state >> (3 * i + j) & 1) * (v >> j & 1)
               for i in range(3) for j in range(3)) % 2


def projection_rank(state, i, j):
    vectors = (1 | (i << 2), 2 | (j << 2))
    return rank_binary([sum(bilinear(u, state, v) << k for k, v in enumerate(vectors))
                        for u in vectors])


def cell_value(coefficient, parity, mask_bit):
    return ((coefficient >> parity & 1) ^ ((coefficient >> 2 & 1) * mask_bit))


def one_block_cost(a, b, i, j):
    return int(any(cell_value(a, p, h) for p, h in ((0, i), (1, j)))
               and any(cell_value(b, p, h) for p, h in ((0, i), (1, j))))


def check_potentials(potentials):
    require(len(potentials) == 5 and all(len(p) == 512 for p in potentials), "potential coverage")
    checked = 0
    for block, values in enumerate(potentials):
        require(values[0] == 0, "potential origin")
        require(values[TARGET] == (2 if block < 4 else 4), "potential target")
        for state in range(512):
            for a in range(1, 8):
                for b in range(1, 8):
                    cost = one_block_cost(a, b, block // 2, block % 2) if block < 4 else 2
                    require(abs(values[state ^ dyad(a, b)] - values[state]) <= cost,
                            "potential edge inequality")
                    checked += 1
    return checked


def primitives():
    potentials = [[projection_rank(s, i, j) for s in range(512)]
                  for i in range(2) for j in range(2)]
    potentials.append([2 * rank_binary([(s >> (3 * i)) & 7 for i in range(3)])
                       for s in range(512)])
    edges = check_potentials(potentials)
    # Q=[[3/5,-4/5],[4/5,3/5]], with every label scaled by five.
    vectors = [(5, 0), (0, 5), (3, 4), (-4, 3)]
    gram = [[sum(a * b for a, b in zip(x, y)) for y in vectors] for x in vectors]
    supports = [[2 * p + h for p in range(2) for h in range(2) if cell_value(c, p, h)]
                for c in range(1, 8)]
    ranks = [rank_q([[gram[x][y] for y in right] for x in left])
             for left in supports for right in supports]
    require(ranks == [2] * 49, "generic two-dimensional block")
    determinants = [vectors[i][0] * vectors[j][1] - vectors[i][1] * vectors[j][0]
                    for i, j in combinations(range(4), 2)]
    require(determinants == [25, 20, 15, -15, 20, 25], "generic pair independence")
    return {"potentials": potentials, "directed_edges": edges,
            "generic_pair_determinants_scaled": determinants, "generic_term_ranks": ranks}


def gram_cube():
    return [[2 * (4 - (x ^ y).bit_count()) * (2 - (x ^ y).bit_count())
             for y in range(32)] for x in range(32)]


def validate_gram(gram):
    require(len(gram) == 32 and all(len(row) == 32 for row in gram), "Gram shape")
    groups = [[x for x in range(32) if x.bit_count() % 2 == p] for p in range(2)]
    for group in groups:
        require(all(gram[x][y] == 16 * int(x == y) for x in group for y in group),
                "parity groups must be orthogonal bases")
    require(all(gram[x][y] == gram[y][x] for x in range(32) for y in range(32)), "Gram symmetry")
    cross = [[gram[x][y] for y in groups[1]] for x in groups[0]]
    require(all(sum(cross[i][k] * cross[j][k] for k in range(16)) == 256 * int(i == j)
                for i in range(16) for j in range(16)), "normalized cross matrix orthogonal")
    require(rank_q(gram) == 16, "rational full Gram rank")
    return groups


def mask_domain():
    coordinates = list(combinations(range(5), 3))[SEED % 10]
    masks = set()
    for truth_table in range(256):
        masks.add(sum(((truth_table >> sum(((x >> c) & 1) << j
                                           for j, c in enumerate(coordinates))) & 1) << x
                      for x in range(32)))
    for monomial in range(32):
        masks.add(sum(int(x & monomial == monomial) << x for x in range(32)))
    masks.add(sum((x.bit_count() % 2) << x for x in range(32)))
    masks.add(sum((1 - x.bit_count() % 2) << x for x in range(32)))
    rng = random.Random(SEED)
    masks.update(rng.getrandbits(32) for _ in range(42))
    return coordinates, sorted(masks)


def boolean_degree(mask):
    coefficients = [(mask >> x) & 1 for x in range(32)]
    for bit in range(5):
        for x in range(32):
            if x >> bit & 1:
                coefficients[x] ^= coefficients[x ^ (1 << bit)]
    return max((x.bit_count() for x, v in enumerate(coefficients) if v), default=-1)


def supports_for(mask):
    return [[x for x in range(32) if cell_value(c, x.bit_count() % 2, mask >> x & 1)]
            for c in range(8)]


def multiplicities(gram, groups, mask):
    cells = [[[x for x in groups[p] if (mask >> x & 1) == h] for h in range(2)] for p in range(2)]
    dimensions = [[len(cells[0][i]) - rank_q([[gram[x][y] for y in cells[1][1-j]]
                                            for x in cells[0][i]]) for j in range(2)]
                  for i in range(2)]
    generic = len(cells[0][0]) - sum(dimensions[0])
    require(all(v >= 0 for row in dimensions for v in row) and generic >= 0,
            "negative component multiplicity")
    require(sum(map(sum, dimensions)) + 2 * generic == 16, "component dimension total")
    return dimensions, generic


def predicted_rank(a, b, dimensions, generic):
    return 2 * generic + sum(dimensions[i][j] * one_block_cost(a, b, i, j)
                            for i in range(2) for j in range(2))


def valid_decoder(terms, supports):
    return all(sum(int(x in supports[a] and y in supports[b]) for a, b in terms) % 2
               == int(x.bit_count() % 2 == y.bit_count() % 2)
               for x in range(32) for y in range(32))


def check_pins():
    source = json.loads((HERE / "SOURCES.json").read_text())
    count = 0
    for record in source["files"]:
        if record["usage"] != "input":
            continue
        data = (ROOT / record["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == record["sha256"], "source SHA256 mismatch")
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == record["git_blob"], "source Git blob mismatch")
        count += 1
    return count


def controls(gram, primitive):
    names = []
    def rejects(name, operation):
        try:
            operation()
        except ValueError:
            names.append(name)
        else:
            raise ValueError("control accepted: " + name)
    supports = supports_for(0x80000000)
    rejects("omitted parity total", lambda: require(valid_decoder([(1, 1)], supports), "decoder identity"))
    rejects("wrong source factor", lambda: require(valid_decoder([(1, 1), (2, 1)], supports), "decoder identity"))
    bad = [row[:] for row in gram]
    bad[0][1] += 1
    bad[1][0] += 1
    rejects("nonorthogonal cross Gram", lambda: validate_gram(bad))
    mod_two_rows = [sum((value % 2) << j for j, value in enumerate(row)) for row in gram]
    rejects("wrong rank field", lambda: require(rank_binary(mod_two_rows) == rank_q(gram), "Q is not F2"))
    bad_potential = [p[:] for p in primitive["potentials"]]
    bad_potential[4][1] = 100
    rejects("forged potential edge", lambda: check_potentials(bad_potential))
    code = {tuple(cell_value(c, p, h) for p in range(2) for h in range(2)) for c in range(8)}
    rejects("nonaffine cell singleton", lambda: require((1, 0, 0, 0) in code, "outside common code"))
    require(rank_q([[25]]) == 1, "singleton boundary witness")
    rejects("degenerate angle priced as generic", lambda: require(rank_q([[1, 1], [1, 1]]) == 2,
                                                                 "nongeneric rotation"))
    require(rank_q(gram) == 16 and not valid_decoder([(3, 3)], supports), "all-ones decoder boundary")
    names.append("masked identity cannot replace all-pairs identity")
    ones = [[1] * 32 for _ in range(32)]
    require(valid_decoder([(1, 1), (2, 2)], supports), "changed-Gram decoder remains exact")
    require(sum(rank_q([[ones[x][y] for y in supports[b]] for x in supports[a]])
                for a, b in [(1, 1), (2, 2)]) == 2, "changed-Gram cost-two witness")
    rejects("changed Gram invalidates floor", lambda: validate_gram(ones))
    return names


def build():
    pins = check_pins()
    gram = gram_cube()
    groups = validate_gram(gram)
    primitive = primitives()
    coordinates, masks = mask_domain()
    fixtures = []
    degenerate = []
    for mask in masks:
        dimensions, generic = multiplicities(gram, groups, mask)
        supports = supports_for(mask)
        ranks = []
        for a in range(1, 8):
            for b in range(1, 8):
                actual = rank_q([[gram[x][y] for y in supports[b]] for x in supports[a]])
                require(actual == predicted_rank(a, b, dimensions, generic), "component rank formula")
                ranks.append(actual)
        require(2 * sum(map(sum, dimensions)) + 4 * generic == 32, "copy lower bound")
        require(valid_decoder([(1, 1), (2, 2)], supports), "parity witness all-pairs identity")
        require(ranks[0] + ranks[8] == 32, "attaining parity invoice")
        fixtures.append({"mask": f"{mask:08x}", "degree": boolean_degree(mask),
                         "intersections": dimensions, "generic_planes": generic, "ranks": ranks})
        evaluations = {((1 << (x.bit_count() % 2)) | ((mask >> x & 1) << 2)) for x in range(32)}
        if rank_binary(evaluations) == 2:
            patterns = sorted(evaluations)
            accepted = []
            for state in range(512):
                if not all(bilinear(u, state, v) == int(u == v) for u in patterns for v in patterns):
                    continue
                weighted = sum(dimensions[i][j] * primitive["potentials"][2*i+j][state]
                               for i in range(2) for j in range(2))
                require(generic == 0 and weighted == 32, "degenerate coefficient lift")
                accepted.append(state)
            require(len(accepted) == 32, "degenerate fiber size")
            degenerate.append({"mask": f"{mask:08x}", "states": accepted})
    negative = controls(gram, primitive)
    return {"schema_version": 1, "result": "sharp common-one-mask copy floor 32; no new kappa",
            "seed": SEED, "coordinates": list(coordinates),
            "proof_scope": "All Boolean masks and arbitrary finite term counts, by PROOF.md; fixtures are not exhaustive masks",
            "primitives": primitive, "fixtures": fixtures, "degenerate_lifts": degenerate,
            "degree_histogram": dict(sorted(Counter(str(f["degree"]) for f in fixtures).items())),
            "source_pins": pins, "controls": negative,
            "coverage": {"masks": len(fixtures), "ordered_rational_ranks": 49 * len(fixtures),
                         "binary_edge_inequalities": primitive["directed_edges"],
                         "witness_entries": 1024 * len(fixtures)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", type=Path, help="create a new receipt; never overwrite")
    args = parser.parse_args()
    receipt = build()
    if args.write_certificate:
        with args.write_certificate.open("x", encoding="utf-8") as stream:
            # Keep exact numeric tables on single lines for a reviewable diff.
            encoded = json.dumps(receipt, indent=2, sort_keys=True)
            encoded = re.sub(r"\[\n(?:\s+-?\d+,?\n)+\s*\]",
                             lambda m: json.dumps(json.loads(m.group(0))), encoded)
            stream.write(encoded + "\n")
    else:
        require(receipt == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
    count = receipt["coverage"]
    print(f"PASS_FIVE_CUBE_ARBITRARY_MASK masks={count['masks']} ranks={count['ordered_rational_ranks']} "
          f"edges={count['binary_edge_inequalities']} controls={len(receipt['controls'])} "
          f"pins={receipt['source_pins']} floor=32 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print("FAIL_FIVE_CUBE_ARBITRARY_MASK: " + str(error), file=sys.stderr)
        raise SystemExit(1)
