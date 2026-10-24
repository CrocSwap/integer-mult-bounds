#!/usr/bin/env python3
"""Standalone exact corroboration. Produced by Nick Petalas; Apache-2.0."""
import argparse
from fractions import Fraction
import hashlib
from heapq import heappop, heappush
from itertools import combinations, product
import json
from pathlib import Path
import sys

# Script-local imports also work under -I and in a Git-free export.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tour import checked_tour_cost, circuit, execute, minimum_cost, tour_events


def check(condition, message):
    if not condition:
        raise ValueError(message)


def distance(a, b, weights):
    return sum(weight for i, weight in enumerate(weights) if ((a ^ b) >> i) & 1)


def permutation_oracle(weights):
    """Held-Karp over pair masks, independent of the claimed formula/order."""
    check(2 <= len(weights) <= 5, "oracle source bound")
    masks = tuple((1 << i) | (1 << j) for i, j in combinations(range(len(weights)), 2))
    size = len(masks)
    table = {(1 << i, i): distance(0, mask, weights) for i, mask in enumerate(masks)}
    for seen in range(1, 1 << size):
        for last in range(size):
            previous = table.get((seen, last))
            if previous is None:
                continue
            for nxt in range(size):
                if (seen >> nxt) & 1:
                    continue
                key = (seen | (1 << nxt), nxt)
                cost = previous + distance(masks[last], masks[nxt], weights)
                if key not in table or cost < table[key]:
                    table[key] = cost
    return min(table[(1 << size) - 1, last] + distance(mask, 0, weights)
               for last, mask in enumerate(masks))


def cube_oracle(weights):
    """Dijkstra on (actual anchor mask, masks seen), including off-layer states."""
    n = len(weights)
    check(2 <= n <= 4, "cube oracle source bound")
    required = tuple((1 << i) | (1 << j) for i, j in combinations(range(n), 2))
    marked = {mask: 1 << i for i, mask in enumerate(required)}
    done = (1 << len(required)) - 1
    queue = [(0, 0, 0)]
    best = {(0, 0): 0}
    maximum_pops = 1 + n * (1 << n) * (1 << len(required))
    for _ in range(maximum_pops):
        check(bool(queue), "shortest-path queue unexpectedly exhausted")
        cost, mask, seen = heappop(queue)
        if best.get((mask, seen)) != cost:
            continue
        if mask == 0 and seen == done:
            return cost
        for i in range(n):
            nxt = mask ^ (1 << i)
            key = (nxt, seen | marked.get(nxt, 0))
            candidate = cost + weights[i]
            if key not in best or candidate < best[key]:
                best[key] = candidate
                heappush(queue, (candidate, *key))
    raise ValueError("Dijkstra exceeded its finite edge-relaxation bound")


def weighted_checks():
    counts = {"permutation_oracles": 0, "literal_cube_oracles": 0, "large_tours": 0}
    for n in range(2, 5):
        for weights in product(range(1, 4), repeat=n):
            predicted = minimum_cost(weights)
            check(permutation_oracle(weights) == predicted, "permutation minimum disagrees")
            check(cube_oracle(weights) == predicted, "arbitrary-mask minimum disagrees")
            check(checked_tour_cost(weights, tour_events(weights)) == predicted, "tour bill")
            counts["permutation_oracles"] += 1
            counts["literal_cube_oracles"] += 1
    for weights in [(1, 1, 1, 1, 1), (9, 2, 7, 1, 3), (1, 3, 2, 5, 4),
                    (Fraction(1, 3), Fraction(7, 2), Fraction(2, 5), Fraction(1, 7), 2)]:
        check(permutation_oracle(weights) == minimum_cost(weights), "five-source oracle")
        counts["permutation_oracles"] += 1
    for n in range(2, 65):
        families = [tuple(1 for _ in range(n)), tuple(range(1, n + 1)),
                    tuple(Fraction(1 + (7 * i) % 13, 1 + i % 5) for i in range(n))]
        for weights in families:
            events = tour_events(weights)
            check(checked_tour_cost(weights, events) == minimum_cost(weights), "large bill")
            check(sum(kind == "toggle" for kind, _ in events) == n * (n - 1) + 2,
                  "wrong complete toggle count")
            counts["large_tours"] += 1
    return counts


def reference(rows, n, copies):
    """Requested simultaneous boundary, using the original input rows only."""
    expected = list(rows)
    for p, (i, j) in enumerate(combinations(range(n), 2)):
        for k in range(copies):
            target = n + 1 + p * copies + k
            expected[target] ^= rows[0] ^ rows[i + 1] ^ rows[j + 1]
    return tuple(expected)


def circuit_checks():
    counts = {"basis_columns": 0, "complete_dirty_states": 0, "wide_dirty_states": 0}
    for n in range(2, 9):
        for copies in range(1, 4):
            weights = tuple(1 + (3 * i) % 7 for i in range(n))
            gates, size = circuit(weights, copies)
            for column in range(size):
                rows = tuple(int(i == column) for i in range(size))
                result = execute(gates, rows)
                check(result == reference(rows, n, copies), "full boundary column")
                check(execute(tuple(reversed(gates)), result) == rows, "inverse column")
                counts["basis_columns"] += 1
            for seed in range(8):
                rows = tuple(((i + 11) * (seed + 37) * 0x123456789ABCDEF) % (1 << 73)
                             for i in range(size))
                check(execute(gates, rows) == reference(rows, n, copies), "wide dirty boundary")
                counts["wide_dirty_states"] += 1
    for n, copies in [(2, 2), (3, 2), (4, 2)]:
        gates, size = circuit((1,) * n, copies)
        for bits in range(1 << size):
            rows = tuple((bits >> i) & 1 for i in range(size))
            check(execute(gates, rows) == reference(rows, n, copies), "exhaustive dirty boundary")
            counts["complete_dirty_states"] += 1
    gates, _ = circuit((1, 1, 1, 1), 2)
    check(len(gates) == 26, "four-source invoice")
    direct = tuple((5 + 2 * p + k, source)
                   for p, (i, j) in enumerate(combinations(range(4), 2))
                   for k in range(2) for source in (0, i + 1, j + 1))
    check(len(direct) == 36, "direct invoice")
    for column in range(17):
        rows = tuple(int(i == column) for i in range(17))
        check(execute(direct, rows) == reference(rows, 4, 2), "direct baseline boundary")
    check(minimum_cost((7, 3, 2, 1)) == 34, "weighted example")
    return counts


def rejection_checks():
    cases = [lambda: minimum_cost((1,)), lambda: minimum_cost((1,) * 65),
             lambda: minimum_cost((1, 0)), lambda: minimum_cost((1, -1)),
             lambda: minimum_cost((True, 1)), lambda: minimum_cost((1.0, 1)),
             lambda: minimum_cost("12"), lambda: circuit((1, 1), True),
             lambda: circuit((1, 1), 0), lambda: circuit((1, 1), 9),
             lambda: execute(((0, 0),), (1, 0)),
             lambda: execute(((2, 0),), (1, 0)),
             lambda: execute(((0, 1),), (True, 0))]
    for case in cases:
        try:
            case()
        except ValueError:
            continue
        raise ValueError("invalid-input control did not reject")
    events = tour_events((7, 3, 2, 1))
    mutants = [events[:-1], tuple(event for event in events if event != ("visit", 3)),
               (("visit", 3),) + events, (("toggle", 4),) + events]
    for mutant in mutants:
        try:
            checked_tour_cost((7, 3, 2, 1), mutant)
        except ValueError:
            continue
        raise ValueError("corrupted-tour control did not reject")
    gates, size = circuit((1, 1, 1, 1), 2)
    for mutant in [gates[:-1], gates[1:], tuple(g for g in gates if g != (5, 0))]:
        check(any(execute(mutant, tuple(int(i == c) for i in range(size)))
                  != reference(tuple(int(i == c) for i in range(size)), 4, 2)
                  for c in range(size)), "faulty circuit escaped the boundary oracle")
    # Reversed price priority is a legal tour but strictly worse for these prices.
    bad = tour_events((1, 2, 3, 7))
    check(checked_tour_cost((7, 3, 2, 1), bad) > minimum_cost((7, 3, 2, 1)),
          "price-order control")
    return {"invalid_inputs": len(cases), "tour_corruptions": len(mutants),
            "circuit_corruptions": 3, "suboptimal_price_order": 1}


def run():
    result = {"status": "PASS_WEIGHTED_PAIR_MASK_TOUR", "claim_type": "scoped proof with finite corroboration",
              **weighted_checks(), **circuit_checks(), **rejection_checks(),
              "unit_example": {"sources": 4, "targets_per_pair": 2, "transition_adds": 14,
                               "target_adds": 12, "complete_adds": 26, "direct_adds": 36},
              "weighted_example_cost": "34"}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new source-bound receipt after success")
    args = parser.parse_args()
    result = run()
    if args.receipt is not None:
        root = Path(__file__).resolve().parent
        names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json",
                 "tour.py", "verify.py")
        hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                  for name in names}
        receipt = {"schema": "weighted-pair-mask-tour/1", "files_sha256": hashes, "result": result}
        with args.receipt.open("x", encoding="utf-8") as output:
            output.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
