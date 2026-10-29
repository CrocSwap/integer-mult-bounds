#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact support screens for a bounded symmetric two-star P112 dictionary."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask(values):
    return sum(1 << i for i in values)


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def geometry():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, sign * 2
            roots.append(tuple(row))
    roots += [(1,) + tail for tail in product((-1, 1), repeat=7)
              if tail.count(-1) % 2 == 0]
    roots.sort()
    dots = [[sum(a * b for a, b in zip(x, y)) for y in roots] for x in roots]
    frame = mask(roots.index(tuple(2 if k == i else sign * 2 if k == i + 1 else 0
                                   for k in range(8)))
                 for i in range(0, 8, 2) for sign in (-1, 1))
    live = ((1 << 120) - 1) ^ frame
    pairing = [mask(j for j, value in enumerate(row) if (value // 4 + 1) % 2)
               for row in dots]
    adjacency = [mask(j for j, value in enumerate(row) if value == 0) & live
                 for row in dots]
    need(len(roots) == 120 and live.bit_count() == 112, "root/line counts")
    need(all(v % 4 == 0 for row in dots for v in row), "integral pairing")
    need(rank(pairing) == 9, "ambient binary rank")
    return roots, dots, live, pairing, adjacency


def cliques(adjacency, live, sizes):
    """Bounded depth-eight enumeration; sorted vertices avoid duplicate cliques."""
    result = []

    def visit(chosen, remaining, size):
        if size in sizes:
            result.append((chosen, size))
        if size == max(sizes):
            return
        for i in bits(remaining):
            remaining &= ~(1 << i)
            visit(chosen | (1 << i), remaining & adjacency[i], size + 1)

    visit(0, live, 0)
    return result


def dictionary(dots, live, pairing):
    stars = [mask(j for j, value in enumerate(row) if value) & live for row in dots]
    base = set(stars) | {s & ~(1 << i) for i, s in enumerate(stars)}
    supports = base | {s & t for s, t in combinations(base, 2)}
    supports.discard(0)
    rows = [(s, rank(pairing[i] & s for i in bits(s))) for s in sorted(supports)]
    need(len(base) == 232 and len(rows) == 16556, "complete support dictionary")
    return rows


def screen(selected, constraints):
    failures = []
    histogram = Counter()
    for clique, size in constraints:
        hits = sum(count for support, _, count in selected if support & clique)
        histogram[(size, hits)] += 1
        if hits < size:
            failures.append({"clique": hex(clique), "size": size, "hits": hits})
    return failures, {f"{size}:{hits}": count
                      for (size, hits), count in sorted(histogram.items())}


def validate_selection(proposal, atoms):
    available = dict(atoms)
    selected = []
    seen = set()
    for row in proposal:
        support, price, count = int(row["support"], 16), row["rank"], row["count"]
        need(support in available and support not in seen, "unknown/duplicate support")
        need(type(price) is int and price == available[support], "wrong actual COPY rank")
        need(type(count) is int and 0 < count <= 10, "invalid multiplicity")
        selected.append((support, price, count))
        seen.add(support)
    need(selected and sum(count for _, _, count in selected) <= 10, "term-count capacity")
    return selected


def controls(atoms, roots, live, pairing, constraints):
    available = dict(atoms)
    coordinate = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            normal = tuple(2 if k == i else sign * 2 if k == i + 1 else 0
                           for k in range(8))
            support = mask(j for j, root in enumerate(roots)
                           if live >> j & 1 and sum(a * b for a, b in zip(root, normal)))
            need(available[support] == 8, "coordinate positive-control price")
            coordinate.append((support, 8, 1))
    failures, _ = screen(coordinate, constraints)
    need(not failures, "coordinate decoder must pass every clique screen")
    failures, _ = screen(coordinate[:-1], constraints)
    need(failures, "omitting a coordinate must fail a clique screen")
    for support, price, _ in coordinate:
        span = {0}
        for i in bits(support):
            span |= {v ^ (pairing[i] & support) for v in span}
        need(len(span) == 1 << price, "independent row-span oracle")
    row = {"support": hex(coordinate[0][0]), "rank": 7, "count": 1}
    try:
        validate_selection([row], atoms)
    except ValueError as error:
        need(str(error) == "wrong actual COPY rank", "wrong-price rejection reason")
    else:
        raise ValueError("undercharged COPY mutation accepted")
    return {"coordinate_cost": 64, "coordinate_clique_violations": 0,
            "omitted_coordinate_rejected": True, "undercharged_rank_rejected": True,
            "independent_span_prices": 8}


def frame_census(atoms, constraints):
    frames = [clique for clique, size in constraints if size == 8]
    histogram = Counter((price, sum(bool(support & frame) for frame in frames))
                        for support, price in atoms)
    return {f"{price}:{hits}": count for (price, hits), count in sorted(histogram.items())}


def run(witness):
    roots, dots, live, pairing, adjacency = geometry()
    atoms = dictionary(dots, live, pairing)
    constraints = cliques(adjacency, live, set(range(1, 9)))
    need(Counter(size for _, size in constraints) ==
         {1: 112, 2: 3304, 3: 31024, 4: 94892, 5: 82656, 6: 39088, 7: 10592, 8: 1260},
         "complete proper-clique census")
    selected = []
    failures, histogram, cost = [], {}, None
    if witness["selected"]:
        selected = validate_selection(witness["selected"], atoms)
        failures, histogram = screen(selected, constraints)
        cost = sum(price * count for _, price, count in selected)
        need(cost <= 63, "proposal exceeds the declared strict-improvement budget")
        for support, price, _ in selected:
            span = {0}
            for i in bits(support):
                span |= {v ^ (pairing[i] & support) for v in span}
            need(len(span) == 1 << price, "independent selected-support price")
    dictionary_hash = hashlib.sha256("".join(f"{s:x}\t{r}\n" for s, r in atoms).encode()).hexdigest()
    return {"dictionary_sha256": dictionary_hash, "atoms": len(atoms),
            "rank_histogram": {str(r): count for r, count in sorted(Counter(r for _, r in atoms).items())},
            "cost": cost, "terms": sum(c for _, _, c in selected),
            "cliques": len(constraints), "violations": len(failures) if selected else None,
            "first_violations": failures[:16], "hit_histogram": histogram,
            "atom_frame_census": frame_census(atoms, constraints),
            "controls": controls(atoms, roots, live, pairing, constraints),
            "incumbent_present": bool(selected),
            "scope": "Necessary support conditions only; no coefficients, decoder, supplier or new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness", type=Path, default=HERE / "SEARCH.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(json.loads(args.witness.read_text()))
    need(result["violations"] in (None, 0), "candidate violates an orthogonal-clique rank constraint")
    if args.output:
        with args.output.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    elif args.witness == HERE / "SEARCH.json":
        need(result == json.loads((HERE / "RESULT.json").read_text()), "changed exact receipt")
    print(json.dumps({k: result[k] for k in ("atoms", "cost", "terms", "cliques", "violations")}))
    print("PASS_MASKED_TWO_STAR_CENSUS" if not result["incumbent_present"]
          else "PASS_MASKED_TWO_STAR_SUPPORT_SCREEN")


if __name__ == "__main__":
    main()
