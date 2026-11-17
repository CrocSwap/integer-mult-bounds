#!/usr/bin/env python3
"""Randomized sparse-host search: the generator for data/hosts.json.

For one row (an odd 8-clique F) and one scope (120 root lines, or the 104 P104
lines) a *host* is a Boolean function f on F_2^8 whose algebraic normal form (ANF)
reproduces the indicator of F on the scope. This script looks for hosts with few
monomials of degree >= 2 by information-set decoding over the 256 square-free
monomials:

  * the nine affine monomials are always pivoted first (they are free),
  * the other monomials are taken in a seeded random order,
  * the pivot solution with all free monomials zero is a host, and so is that
    solution with any one free monomial switched on,
  * the sparsest host over a fixed number of random orders is kept.

The outcome is an explicit upper bound for each row, checked afterwards by
verify.py on every scope point. It is not a minimum and carries no lower bound.

    python3 -B search.py --scope T120 --iterations 3000 --seed 20261110 \
        --write data/hosts_T120.json
    python3 -B search.py --scope P104 --iterations 3000 --seed 20261110 \
        --incumbent data/hosts_T120.json --write data/hosts_P104.json

The run is deterministic for fixed arguments (no clock, no threads).
"""

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verify as geo  # noqa: E402  (shares the chart and the host checker)

SIZE = geo.SIZE
GE2 = geo.GE2


def system_rows(scope, clique_set):
    """One row per scope point: monomial incidence bits, rhs bit at position SIZE."""
    rows = []
    for x in sorted(scope):
        row = 0
        for m in range(SIZE):
            if m & ~x == 0:
                row |= 1 << m
        if x in clique_set:
            row |= 1 << SIZE
        rows.append(row)
    return rows


AFFINE = [m for m in range(SIZE) if bin(m).count("1") <= 1]
HIGHER = [m for m in range(SIZE) if bin(m).count("1") >= 2]


def eliminate(rows, order):
    reduced = list(rows)
    used = [False] * len(reduced)
    pivot_row = {}
    for col in order:
        bit = 1 << col
        found = -1
        for i, row in enumerate(reduced):
            if not used[i] and row & bit:
                found = i
                break
        if found < 0:
            continue
        used[found] = True
        pivot = reduced[found]
        for j, row in enumerate(reduced):
            if j != found and row & bit:
                reduced[j] = row ^ pivot
        pivot_row[col] = found
        if len(pivot_row) == len(reduced):
            break
    for i, row in enumerate(reduced):
        geo.need(used[i] or not (row >> SIZE) & 1, "the host system is inconsistent")
    return reduced, pivot_row


def best_host(scope, clique_set, rng, iterations, incumbent=None):
    rows = system_rows(scope, clique_set)
    best_weight, best_anf = incumbent if incumbent else (10 ** 9, 0)
    for _ in range(iterations):
        order = AFFINE + rng.sample(HIGHER, len(HIGHER))
        reduced, pivot_row = eliminate(rows, order)
        solution = 0
        for col, i in pivot_row.items():
            if (reduced[i] >> SIZE) & 1:
                solution |= 1 << col
        weight = (solution & GE2).bit_count()
        if weight < best_weight:
            best_weight, best_anf = weight, solution
        # switch on one free monomial: it flips every pivot whose reduced row contains it
        flips = {}
        for col, i in pivot_row.items():
            row = reduced[i]
            for fc in HIGHER:
                if fc not in pivot_row and (row >> fc) & 1:
                    flips[fc] = flips.get(fc, 0) ^ (1 << col)
        for fc in HIGHER:
            if fc in pivot_row:
                continue
            candidate = solution ^ flips.get(fc, 0) ^ (1 << fc)
            weight = (candidate & GE2).bit_count()
            if weight < best_weight:
                best_weight, best_anf = weight, candidate
    return best_weight, best_anf


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("T120", "P104"), required=True)
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--rows", default="all", help="comma-separated row indices or 'all'")
    parser.add_argument("--write", default=None)
    parser.add_argument(
        "--incumbent", default=None,
        help="hosts file for a larger scope; its hosts also host on this scope and seed the search")
    args = parser.parse_args(argv)
    cartan, points, port_position, cliques = geo.load_geometry()
    lines = set(points)
    p104 = {points[port_position[p]] for c in cliques[:13] for p in c}
    scope = lines if args.scope == "T120" else p104
    count = 15 if args.scope == "T120" else 13
    rows = range(count) if args.rows == "all" else [int(r) for r in args.rows.split(",")]
    seeds = {}
    if args.incumbent:
        for entry in json.loads(Path(args.incumbent).read_text()):
            anf = 0
            for m in entry["monomials"]:
                anf ^= 1 << m
            seeds[entry["row"]] = (entry["charge"], anf)
    out = []
    for index in rows:
        clique = geo.Clique({points[port_position[p]] for p in cliques[index]})
        rng = random.Random("%d/%s/%d" % (args.seed, args.scope, index))
        weight, anf = best_host(scope, clique.set, rng, args.iterations, seeds.get(index))
        geo.check_host(anf, clique, scope)
        monomials = [m for m in range(SIZE) if (anf >> m) & 1]
        out.append({"scope": args.scope, "row": index, "charge": weight, "monomials": monomials})
        print("scope=%s row=%d charge=%d" % (args.scope, index, weight), flush=True)
    if args.write:
        Path(args.write).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
