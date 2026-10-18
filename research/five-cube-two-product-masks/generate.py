#!/usr/bin/env python3
"""Exact certificate generator; the separate verifier does not import this file.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import base64
from collections import Counter
from functools import reduce
from heapq import heappop, heappush
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path

SIZE = 1 << 16
TARGET = (1 << 0) | (1 << 1) | (1 << 4)
NAMES = ("opposed", "disjoint", "aligned")  # seed 44 % 3 selects opposed first


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rational_rank(matrix):
    """Integer row operations and gcd normalization; exact over Q."""
    a = [row[:] for row in matrix]
    n = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(n, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[n], a[pivot] = a[pivot], a[n]
        p = a[n][col]
        for i in range(n + 1, len(a)):
            q = a[i][col]
            if q:
                row = [p * x - q * y for x, y in zip(a[i], a[n])]
                divisor = reduce(gcd, row)
                a[i] = [x // divisor for x in row] if divisor else row
        n += 1
        if n == len(a):
            break
    return n


def model(name):
    basis = []
    for x in range(32):
        b = [(x >> i) & 1 for i in range(5)]
        h = b[0] * b[1]
        k = b[2] * b[3] if name == "disjoint" else (b[1] ^ (name == "opposed")) * b[2]
        basis.append([1, x.bit_count() % 2, h, k])
    forms = [[sum(v * ((a >> i) & 1) for i, v in enumerate(row)) % 2
              for row in basis] for a in range(16)]
    gram = [[2 * (4 - (x ^ y).bit_count()) * (2 - (x ^ y).bit_count())
             for y in range(32)] for x in range(32)]
    edges = []
    for a, b in product(range(1, 16), repeat=2):
        delta = sum((((a >> i) & 1) * ((b >> j) & 1)) << (4 * i + j)
                    for i, j in product(range(4), repeat=2))
        weight = rational_rank([[gram[x][y] for y in range(32) if forms[b][y]]
                                for x in range(32) if forms[a][x]])
        edges.append((delta, weight, a, b))
    return forms, edges


def separating_functional(edges):
    basis = {}
    for delta, _, _, _ in edges:
        x = delta
        while x:
            bit = x.bit_length() - 1
            if bit in basis:
                x ^= basis[bit]
            else:
                basis[bit] = x
                break
    x = TARGET
    while x:
        bit = x.bit_length() - 1
        if bit not in basis:
            break
        x ^= basis[bit]
    if not x:
        return None, len(basis)
    for z in range(1, SIZE):
        if (z & TARGET).bit_count() % 2 and all((z & v).bit_count() % 2 == 0 for v in basis.values()):
            return z, len(basis)
    raise ValueError("missing separation witness")


def shortest_certificate(edges, cap):
    allowed = [e for e in edges if e[1] <= cap]
    separator, dimension = separating_functional(allowed)
    if separator is not None:
        return {"cap": cap, "optimum": None, "span_dimension": dimension,
                "separating_functional": separator}
    infinity = 10**9
    dist = [infinity] * SIZE
    dist[0] = 0
    queue = [(0, 0)]
    previous = {}
    while queue:
        value, state = heappop(queue)
        if value != dist[state]:
            continue
        if state == TARGET:
            break
        for delta, weight, a, b in allowed:
            nxt = state ^ delta
            proposed = value + weight
            if proposed < dist[nxt]:
                dist[nxt] = proposed
                previous[nxt] = (state, a, b)
                heappush(queue, (proposed, nxt))
    optimum = dist[TARGET]
    require(optimum < 256, "potential encoding overflow or unreachable target")
    # Dijkstra has settled every state at distance < optimum. Clamping the
    # others to optimum is therefore the exact truncated distance potential.
    potential = bytes(min(d, optimum) for d in dist)
    word = []
    state = TARGET
    while state:
        state, a, b = previous[state]
        word.append([a, b])
    word.reverse()
    return {"cap": cap, "optimum": optimum, "span_dimension": dimension,
            "potential_u8_base64": base64.b64encode(potential).decode("ascii"),
            "attaining_word": word}


def labelled_domain():
    records = []
    for first, second in combinations(list(combinations(range(5), 2)), 2):
        for signs in product(range(2), repeat=4):
            shared = set(first) & set(second)
            if not shared:
                name = "disjoint"
                axes = [*first, *second]
                flips = list(signs)
            else:
                common = next(iter(shared))
                left = next(i for i in first if i != common)
                right = next(i for i in second if i != common)
                left_signs = dict(zip(first, signs[:2]))
                right_signs = dict(zip(second, signs[2:]))
                name = "aligned" if left_signs[common] == right_signs[common] else "opposed"
                axes = [left, common, right]
                flips = [left_signs[left], left_signs[common], right_signs[right]]
            axes.extend(i for i in range(5) if i not in axes)
            flips.extend([0] * (5 - len(flips)))
            records.append({"first": list(first), "second": list(second),
                            "literal_flips": list(signs), "orbit": name,
                            "transport_axes": axes, "transport_flips": flips})
    return records


def generate():
    output = {"schema_version": 1, "assignment_seed": 44,
              "state_bits": 16, "target_state": TARGET,
              "domain": labelled_domain(), "orbits": []}
    for name in NAMES:
        forms, edges = model(name)
        caps = sorted({0, *(e[1] for e in edges)})
        records = [shortest_certificate(edges, cap) for cap in caps]
        lookup = {r["cap"]: r["optimum"] for r in records}
        table = [lookup[max(c for c in caps if c <= cap)] for cap in range(17)]
        orbit = {"name": name,
                                 "basis_masks": [sum(forms[a][x] << x for x in range(32)) for a in (1, 2, 4, 8)],
                                 "term_ranks": [e[1] for e in edges],
                                 "rank_histogram": dict(sorted(Counter(e[1] for e in edges).items())),
                                 "optimum_by_cap_0_to_16": table,
                                 "certificates": records}
        if name == "opposed":
            orbit["one_mask_subcodes_at_cap14"] = []
            for quotient in (4, 8, 12):
                coefficients = {1, 2, 3, quotient, quotient ^ 1, quotient ^ 2, quotient ^ 3}
                restricted = [e for e in edges if e[2] in coefficients and e[3] in coefficients]
                record = shortest_certificate(restricted, 14)
                record["quotient_generator"] = quotient
                orbit["one_mask_subcodes_at_cap14"].append(record)
        output["orbits"].append(orbit)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New certificate path; existing outputs are never replaced")
    args = parser.parse_args()
    # Exclusive creation refuses to replace an existing certificate.
    with args.output.open("x", encoding="utf-8") as stream:
        result = generate()
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    for orbit in result["orbits"]:
        print(orbit["name"], orbit["optimum_by_cap_0_to_16"])
    print("GENERATED_TWO_PRODUCT_MASK_CERTIFICATE (requires independent verification)")


if __name__ == "__main__":
    main()
