"""Exact finite checks for the new two-addition charge-fiber theorem."""

from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement, permutations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(packet):
    u, b, w = packet
    if u:
        return (1, u * b % 3, u * w % 3)
    pivot = b or w
    if pivot:
        scale = 1 if pivot == 1 else 2
        return (0, scale * b % 3, scale * w % 3)
    return packet


def charges(state):
    return tuple(sorted((u * b % 3, u * w % 3) for u, b, w in state))


def passing(state):
    key = charges(state)
    return all(y == 0 for _, y in key) and sum(
        1 if x == 1 else -1 if x == 2 else 0 for x, _ in key
    ) in (1, -2)


def check_totals(before, after):
    old, new = charges(before), charges(after)
    require(sum(x for x, _ in old) % 3 == sum(x for x, _ in new) % 3,
            "scalar charge conservation")
    require(sum(y for _, y in old) % 3 == sum(y for _, y in new) % 3,
            "slope charge conservation")


def move(state, i, j, a):
    packets = list(state)
    ui, bi, wi = packets[i]
    uj, bj, wj = packets[j]
    packets[i] = normalize(((ui + a * uj) % 3, bi, wi))
    packets[j] = normalize((uj, (bj - a * bi) % 3, (wj - a * wi) % 3))
    result = tuple(sorted(packets))
    check_totals(state, result)
    return result


def neighbors(state):
    m = len(state)
    require(2 <= m <= 5, "finite fixture dimension")
    result = set()
    for i in range(m):
        for j in range(m):
            if i != j:
                for a in (1, 2):
                    result.add(move(state, i, j, a))
    return result


def check_fibers(states, levels):
    fibers = {}
    histogram = Counter()
    for state in states:
        key, cost = charges(state), levels.get(state, 3)
        if key in fibers:
            require(fibers[key] == cost, "two-addition charge fiber split")
        fibers[key] = cost
        histogram[cost] += 1
    return fibers, histogram


def finite_fibers(m):
    types = sorted({normalize(p) for p in product(range(3), repeat=3)})
    states = []
    for state in combinations_with_replacement(types, m):
        key = charges(state)
        if sum(x for x, _ in key) % 3 == 1 and sum(y for _, y in key) % 3 == 0:
            states.append(state)
    levels = {s: 0 for s in states if passing(s)}
    frontier = set(levels)
    for depth in (1, 2):
        next_frontier = set()
        for state in frontier:
            for nxt in neighbors(state):
                if nxt not in levels:
                    levels[nxt] = depth
                    next_frontier.add(nxt)
        frontier = next_frontier
    fibers, histogram = check_fibers(states, levels)
    require(set(levels).issubset(set(states)), "normalized family preservation")
    return {"m": m, "states": len(states), "charge_fibers": len(fibers),
            "truncated_costs": dict(sorted(histogram.items()))}


def local_scalar_envelopes():
    count = 0
    for xs in product(range(3), repeat=3):
        if xs.count(0) == 0:
            continue
        lift = sum(1 if x == 1 else -1 if x == 2 else 0 for x in xs)
        total = sum(xs) % 3
        canonical = 1 if total == 1 else -1 if total == 2 else 0
        require(abs(lift - canonical) <= 3, "three-vertex scalar envelope")
        count += 1
    for before in product(range(3), repeat=2):
        for after in product(range(3), repeat=2):
            if sum(before) % 3 != sum(after) % 3:
                continue
            old = sum(1 if x == 1 else -1 if x == 2 else 0 for x in before)
            new = sum(1 if x == 1 else -1 if x == 2 else 0 for x in after)
            require(abs(old - new) <= 3, "one-addition scalar envelope")
            count += 1
    return count


def literal_prefix_count(state):
    count = 0
    for order in permutations(range(len(state))):
        okay = True
        for a in range(3):
            for size in range(1, len(state)):
                minor = [[((i == j) - state[order[i]][0] * (
                    state[order[j]][1] + a * state[order[j]][2])) % 3
                    for j in range(size)] for i in range(size)]
                if determinant(minor) == 0:
                    okay = False
        count += okay
    return count


def determinant(matrix):
    size = len(matrix)
    require(1 <= size <= 4, "literal minor size")
    rows = [list(row) for row in matrix]
    value = 1
    for j in range(size):
        pivot = next((i for i in range(j, size) if rows[i][j]), None)
        if pivot is None:
            return 0
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            value = -value
        entry = rows[j][j]
        value = value * entry % 3
        inverse = 1 if entry == 1 else 2
        for i in range(j + 1, size):
            coefficient = rows[i][j] * inverse % 3
            for k in range(j, size):
                rows[i][k] = (rows[i][k] - coefficient * rows[j][k]) % 3
    return value % 3


def literal_moves():
    checked = 0
    for state in product(tuple(product(range(3), repeat=3)), repeat=2):
        canonical = tuple(normalize(p) for p in state)
        for i, j in ((0, 1), (1, 0)):
            for a in (1, 2):
                forward = [[int(r == c) for c in range(2)] for r in range(2)]
                inverse = [[int(r == c) for c in range(2)] for r in range(2)]
                forward[i][j], inverse[i][j] = a, -a % 3
                u, b, w = zip(*canonical)
                image = [sum(forward[r][c] * u[c] for c in range(2)) % 3
                         for r in range(2)]
                base = [sum(b[r] * inverse[r][c] for r in range(2)) % 3
                        for c in range(2)]
                slope = [sum(w[r] * inverse[r][c] for r in range(2)) % 3
                         for c in range(2)]
                actual = tuple(sorted(normalize(p) for p in zip(image, base, slope)))
                require(actual == move(canonical, i, j, a), "dense header action")
                checked += 1
    return checked


def controls():
    # Same charges, distinct dormant dual directions. Neither is erased.
    left = ((1, 0, 1), (1, 0, 2), (1, 1, 0), (0, 1, 0))
    right = ((1, 0, 1), (1, 0, 2), (1, 1, 0), (0, 0, 1))
    require(charges(left) == charges(right), "hidden-data fixture charges")
    require(left != right, "hidden-data fixture distinction")
    require(not passing(left) and not passing(right), "nonseparated control")
    require(passing(move(left, 0, 1, 2)), "legal one-addition positive control")
    require(passing(move(right, 0, 1, 2)), "hidden-data positive control")
    rejected = mutation_controls(left, right)
    checked = 0
    types = sorted({normalize(p) for p in product(range(3), repeat=3)})
    for state in product(types, repeat=2):
        key = charges(state)
        if sum(x for x, _ in key) % 3 == 1 and sum(y for _, y in key) % 3 == 0:
            require(bool(literal_prefix_count(state)) == passing(state), "literal proper minors")
            checked += 1
    return {"rejected": rejected, "literal_two_coordinate_families": checked}


def mutation_controls(left, right):
    rejected = 0
    try:
        check_fibers((left, right), {left: 1, right: 2})
    except ValueError as exc:
        require(str(exc) == "two-addition charge fiber split", "wrong fiber rejection")
        rejected += 1
    # This state passes in either coordinate order despite D=-2.
    negative = ((1, 2, 0), (1, 2, 0))
    try:
        require(bool(literal_prefix_count(negative)) is False,
                "deleted negative scalar endpoint")
    except ValueError as exc:
        require(str(exc) == "deleted negative scalar endpoint", "wrong endpoint rejection")
        rejected += 1
    # A plus sign in the inverse dual update breaks charge conservation.
    initial = ((1, 1, 1), (1, 0, 0))
    wrong_dual = ((2, 1, 1), (1, 1, 1))
    try:
        check_totals(initial, wrong_dual)
    except ValueError as exc:
        require(str(exc) == "scalar charge conservation", "wrong dual rejection")
        rejected += 1
    require(rejected == 3, "rejecting controls")
    return rejected


def main():
    rows = [finite_fibers(m) for m in range(2, 6)]
    report = {"status": "PASS_TERNARY_TWO_ADDITION_CHARGE_INVARIANCE",
              "fixtures": rows, "scalar_cases": local_scalar_envelopes(),
              "controls": controls(), "dense_actions": literal_moves(), "errors": 0,
              "sha256": {name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                         for name in ("verify.py", "PROOF.md")}}
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
