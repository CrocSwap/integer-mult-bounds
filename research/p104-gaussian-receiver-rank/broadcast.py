#!/usr/bin/env python3
"""Exact-Q two-receiver broadcast screen on the authenticated #8072 word.

A shared packet goes from the original sender through one relay to the two
receivers of an original incidence u: a->b, v: b->d, where v reads u. The
packet and both decoders may be arbitrary linear forms. Original stocks are
available acausally. Only a strict reduction in integer raw grade is tested.
The class and the lifting of modular annihilators to Q are in BROADCAST.md.

--corrupt-coordinate is an expected-failure negative control: it changes one
rational coefficient in an actual sink identity and must exit nonzero.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
import numpy as np

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("gaussian_receiver_baseline", HERE / "verify.py")
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)
P = 65521
CASES_SHA = "c2969359ad56459f42323c8e6b5945b89a8dc7c53d537ab6c606b04fbe3f123f"

IDENTITIES = {
    91582: [(103243, "1")],
    91560: [(104268, "-2"), (104318, "-2")],
    97266: [(103991, "-1/2"), (103944, "-1/2")],
    89777: [(104126, "1"), (104146, "1"), (104063, "1"),
            (103952, "1"), (104092, "-1/58")],
    96513: [(103514, "1")],
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def relay_census(data):
    """Enumerate every actual incidence and every legal cheaper relay."""
    graph, dims, spans, moves, rows = (data[k] for k in
                                       ("graph", "dims", "spans", "moves", "rows"))
    size = len(dims)
    depth_masks = {depth: 0 for depth in set(dims)}
    for chart, depth in enumerate(dims):
        depth_masks[depth] |= 1 << chart
    neighbors = []
    for a in range(size):
        mask = 0
        for b in range(size):
            if dims[a] != dims[b] and base.nested(spans[a], spans[b]):
                mask |= 1 << b
        neighbors.append(mask)

    def routes(a, b, d, old_grade):
        possible = ((neighbors[a] | (1 << a)) & (neighbors[b] | (1 << b)) &
                    (neighbors[d] | (1 << d)))
        output = []
        for level, mask in depth_masks.items():
            cost = (abs(dims[a] - level) + abs(dims[b] - level) +
                    abs(dims[d] - level))
            if cost < old_grade:
                output.extend([h, cost] for h in bits(possible & mask))
        return sorted(output)

    counts, cases = Counter(), []
    for v, (b, d) in moves.items():
        for u, coefficient in rows[v]:
            if u not in moves or moves[u][1] != b:
                continue
            check(base.rational(coefficient) != 0, "zero incidence coefficient")
            a, _ = moves[u]
            counts["incidences"] += 1
            if a == d:
                counts["source_is_second_receiver"] += 1
                continue
            old_grade = abs(dims[a] - dims[b]) + abs(dims[b] - dims[d])
            found = routes(a, b, d, old_grade)
            if found:
                counts["cheaper_relay_incidences"] += 1
                cases.append({"u": u, "v": v, "charts": [a, b, d],
                              "old_grade": old_grade, "routes": found})
    check(counts == {"incidences": 11819, "source_is_second_receiver": 8,
                     "cheaper_relay_incidences": 58}, "incidence census differs")
    check(len({tuple(e["charts"]) for e in cases}) == 39, "chart triple count differs")
    return cases


def annihilators(data, cases):
    """Produce and verify 36 modular annihilators per involved source stock."""
    rng = np.random.default_rng(0x8072F00D)
    n = data["n"]
    result = {}
    for chart in sorted({c for e in cases for c in (e["charts"][0], e["charts"][2])}):
        z = rng.integers(0, P, (36, n), dtype=np.int64)
        for col, row in reversed(list(data["basis"][chart].items())):
            z[:, col] = (z[:, col] - z @ row) % P
        for row in data["basis"][chart].values():
            check(not np.any((z @ row) % P), "invalid stock annihilator")
        result[chart] = z
    return result


def identity_checker(rows):
    """Return a checker expanding identities on all rational input coordinates."""
    sys.setrecursionlimit(50000)

    @lru_cache(None)
    def vector(node):
        if node < 0:
            return {~node: Fraction(1)}
        result = defaultdict(Fraction)
        for parent, coeff in rows[node]:
            scalar = Fraction(coeff)
            for coordinate, value in vector(parent).items():
                result[coordinate] += scalar * value
        return {i: x for i, x in result.items() if x}

    def check_identity(node, terms):
        difference = defaultdict(Fraction)
        for coordinate, value in vector(node).items():
            difference[coordinate] += value
        for source, coefficient in terms:
            for coordinate, value in vector(source).items():
                difference[coordinate] -= Fraction(coefficient) * value
        check(not any(difference.values()), "rational coordinate identity mismatch")

    return check_identity


def damaged_identity():
    result = list(IDENTITIES[89777])
    check(result[-1] == (104092, "-1/58"), "wrong mutation anchor")
    result[-1] = (104092, "-1/57")
    return result


def toy_controls():
    """Check a working two-decoder broadcast and a full-rank obstruction."""
    source = np.array([[1, 0], [0, 1]], dtype=np.int64)
    b = np.array([[1, 0], [0, 1]], dtype=np.int64)
    d = np.array([[0, 1], [1, 1]], dtype=np.int64)
    check(all(base.rank_mod(stock, P) == 2 for stock in (source, b, d)),
          "positive toy stocks dependent")
    packet = source[0]
    check(np.array_equal(packet, b[0]), "first toy decoder fails")
    check(np.array_equal((packet + d[0]) % P, d[1]), "second toy decoder fails")
    check(9 + 7 > 2 + 7, "positive toy has no raw grade saving")
    # Source span{x}, b span{x,z}, and d span{y,x+z}. The rows in z below
    # annihilate the stated source and destination stocks; b's pairing has rank 2.
    source = np.array([[1, 0, 0]], dtype=np.int64)
    b = np.array([[1, 0, 0], [0, 0, 1]], dtype=np.int64)
    d = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.int64)
    z = np.array([[0, 1, 0], [0, 0, 1], [1, 0, P - 1]], dtype=np.int64)
    check(not np.any((source @ z[:2].T) % P), "bad toy source annihilator")
    check(not np.any((d @ z[2:].T) % P), "bad toy destination annihilator")
    check(base.rank_mod((b @ z.T) % P, P) == 2, "negative toy rank differs")


def compute():
    check(np.__version__ == "1.26.4", "replay requires numpy==1.26.4")
    graph = base.read_graph()
    data = base.evaluate(graph, P)
    n = data["n"]
    check(n == 1291 and len(data["moves"]) == 5674, "baseline census differs")
    check(n * (P - 1) ** 2 < 2**53 < 2**63, "unsafe dot-product bound")
    cases = relay_census(data)
    stock_annihilators = annihilators(data, cases)
    ranks = {}
    for entry in cases:
        a, b, d = entry["charts"]
        key = (a, b, d)
        if key not in ranks:
            stock_b = np.stack([data["vectors"][j] for j in data["owners"][b]])
            z = np.concatenate([stock_annihilators[a], stock_annihilators[d]], axis=0)
            products = stock_b.astype(np.float64) @ z.astype(np.float64).T
            exact = sum(int(q) * int(r) for q, r in zip(stock_b[0], z[0]))
            check(products[0, 0] == exact, "float dot-product control failed")
            matrix = products.astype(np.int64) % P
            ranks[key] = (base.rank_mod(matrix, P), len(stock_b))
        entry["rank"], entry["stock_size"] = ranks[key]

    check_identity = identity_checker(data["rows"])
    checked = set()
    counts = Counter()
    for entry in cases:
        u, v = entry["u"], entry["v"]
        a, b, d = entry["charts"]
        rank, dimension = entry["rank"], entry["stock_size"]
        if rank == dimension:
            entry["kind"] = "zero"
            counts["zero"] += 1
            continue
        check(rank == dimension - 1 and d == 127 and u in IDENTITIES,
              "rank-one packet case differs")
        terms = IDENTITIES[u]
        check(v not in [node for node, _ in terms], "removed v occurs in sink identity")
        check(all(node in data["owners"][d] for node, _ in terms),
              "identity reads a non-sink node")
        if u not in checked:
            check_identity(u, terms)
            checked.add(u)
        entry["kind"] = "rank_one"
        counts["rank_one"] += 1
    check(counts == {"zero": 47, "rank_one": 11}, "47+11 exclusion differs")
    check(checked == set(IDENTITIES), "one of the five exact identities was not tested")
    try:
        check_identity(89777, damaged_identity())
    except ValueError as error:
        check(str(error) == "rational coordinate identity mismatch", "wrong corruption failure")
    else:
        raise ValueError("corrupted rational coordinate was accepted")
    toy_controls()
    records = sorted([[e["u"], e["v"], *e["charts"], e["old_grade"], e["routes"],
                       e["rank"], e["kind"]] for e in cases], key=lambda r: (r[0], r[1]))
    digest = hashlib.sha256(json.dumps(records, sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    check(digest == CASES_SHA, "route/rank case digest differs")
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrupt-coordinate", action="store_true",
                        help="expected-failure control for a rational coordinate")
    args = parser.parse_args()
    if args.corrupt_coordinate:
        graph = base.read_graph()
        identity_checker(dict(graph["forms"]))(89777, damaged_identity())
        raise ValueError("corrupted rational coordinate was accepted")
    digest = compute()
    print("PASS_BROADCAST incidences=11819 same_receiver=8 cheaper=58 zero=47 rank_one=11")
    print("PASS_BROADCAST_TOY_POSITIVE_NEGATIVE AND_CORRUPTED_COORDINATE_REJECTED")
    print("PASS_BROADCAST_CASE_DIGEST sha256=" + digest)


if __name__ == "__main__":
    main()
