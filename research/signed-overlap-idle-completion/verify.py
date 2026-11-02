#!/usr/bin/env python3
"""Exact new completion certificates. Produced by Nick Petalas, Apache-2.0."""

import argparse
from fractions import Fraction
from hashlib import sha256
from heapq import heappop, heappush
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dual_checks():
    """All subsets for the extreme concave cardinality tariffs."""
    count = 0
    for hinge in range(1, 4):
        tariff = tuple(Fraction(min(k, hinge)) for k in range(4))
        a, _, c = tariff[1:]
        weights = ((c-a)/2, a, (c-a)/2)
        for bits in product((0, 1), repeat=3):
            if not any(bits):
                continue
            value = sum(w*x for w, x in zip(weights, bits, strict=True))
            for sign in (-1, 1):
                need(sign*value <= tariff[sum(bits)], "dual atom inequality")
                count += 1
        need(sum(w*d for w, d in zip(weights, (2, 4, 2), strict=True))
             == 2*c+2*a, "dual objective")
    return count


def inventory_balance(inventory, expected, tariff):
    need(len(inventory) <= 32, "inventory capacity")
    balance = [0, 0, 0]
    cost = Fraction(0)
    for sign, bits in inventory:
        need(sign in (-1, 1), "atom sign")
        need(len(bits) == 3 and all(x in (0, 1) for x in bits) and any(bits),
             "atom support")
        for i in range(3):
            balance[i] += sign*bits[i]
        cost += tariff[sum(bits)]
    need(tuple(balance) == expected, "wrong signed determinant balance")
    return cost


def shortest_inventory(target, tariff):
    """Independent bounded lattice search, not the all-length proof."""
    bound = 4
    states = tuple(product(range(-bound, bound+1), repeat=3))
    distances = dict.fromkeys(states, Fraction(1000))
    distances[(0, 0, 0)] = Fraction(0)
    queue = [(Fraction(0), (0, 0, 0))]
    atoms = tuple(b for b in product((0, 1), repeat=3) if any(b))
    settled = set()
    # Each vertex is expanded once and can cause at most 14 successful pushes.
    for _ in range(len(states)*15):
        if not queue:
            break
        distance, state = heappop(queue)
        if state in settled:
            continue
        settled.add(state)
        if state == target:
            return distance, len(settled)
        for bits in atoms:
            for sign in (-1, 1):
                nxt = tuple(x+sign*b for x, b in zip(state, bits, strict=True))
                if nxt not in distances:
                    continue
                candidate = distance + tariff[sum(bits)]
                if candidate < distances[nxt]:
                    distances[nxt] = candidate
                    heappush(queue, (candidate, nxt))
    raise ValueError("bounded shortest-path queue exhausted without target")


def check_transfers():
    ranks = [8, 8, 25, 25, 25, 25]
    checks = 0
    transfers = (((8, 25), (16, 17)),)*2 + (((16, 25), (17, 24)),)*2
    for old, new in transfers:
        need(sum(old) == sum(new) and old[0] < new[0] <= new[1] < old[1],
             "not a strict balancing transfer")
        for value in old:
            ranks.remove(value)
        ranks.extend(new)
        for hinge in range(1, 26):
            need(sum(min(x, hinge) for x in new)
                 >= sum(min(x, hinge) for x in old), "concave transfer")
            checks += 1
    need(sorted(ranks) == [17, 17, 17, 17, 24, 24], "final reward ranks")
    return checks


def rejects(function, *args):
    try:
        function(*args)
    except (ValueError, TypeError):
        return
    raise ValueError("negative control was accepted")


def verify():
    tariffs = ((0, 1, 1, 1), (0, 1, 2, 2), (0, 1, 2, 3),
               (0, 4, 6, 7), (0, 8, 11, 13))
    witness = [(1, (1, 1, 1))]*2 + [(1, (0, 1, 0))]*2
    finite = []
    for raw in tariffs:
        tariff = tuple(map(Fraction, raw))
        expected = 2*tariff[3] + 2*tariff[1]
        need(inventory_balance(witness, (2, 4, 2), tariff) == expected,
             "attaining inventory cost")
        for target, optimum in (((2, 4, 2), expected),
                                ((4, 4, 4), 4*tariff[3])):
            distance, settled = shortest_inventory(target, tariff)
            need(distance == optimum, "independent finite shortest path")
            finite.append({"tariff": list(raw), "target": list(target),
                           "optimum": str(distance), "settled": settled})
    tariff = tuple(map(Fraction, tariffs[-1]))
    rejects(inventory_balance, witness[:-1], (2, 4, 2), tariff)
    rejects(inventory_balance, [(-1, witness[0][1])]+witness[1:], (2, 4, 2), tariff)
    rejects(inventory_balance, [(1, (0, 0, 0))], (0, 0, 0), tariff)
    rejects(inventory_balance, [(2, (1, 1, 1))], (2, 2, 2), tariff)
    rejects(inventory_balance, [(1, (1, 2, 0))], (1, 2, 0), tariff)
    rejects(inventory_balance, witness*9, (18, 36, 18), tariff)
    targets = ((1, 1, 1),)*2 + ((1, 1, 0),)*2 + ((0, 1, 1),)*2
    degrees = tuple(sum(row[i] for row in targets) for i in range(3))
    need(tuple(x-2 for x in degrees) == (2, 4, 2), "native determinant debit")
    return {"status": "PASS_SIGNED_OVERLAP_IDLE_COMPLETION",
            "signed_dual_inequalities": dual_checks(),
            "concave_transfer_checks": check_transfers(),
            "finite_shortest_paths": finite, "rejecting_controls": 6,
            "scope": "Scoped proof and finite corroboration; determinant relaxation only."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    report = verify()
    report["source_sha256"] = {
        name: sha256((ROOT/name).read_bytes()).hexdigest()
        for name in ("verify.py", "PROOF.md", "README.md", "TASK.json",
                     "SOURCES.json", "VERIFY.json")}
    payload = json.dumps(report, indent=2, sort_keys=True)+"\n"
    if args.write_receipt:
        with args.write_receipt.open("x") as destination:
            need(destination.write(payload) == len(payload), "short receipt write")
    else:
        receipt = json.loads((ROOT/"RESULT.json").read_text())
        need(report == receipt, "receipt differs from current proof/source replay")
    print(payload, end="")


if __name__ == "__main__":
    main()
