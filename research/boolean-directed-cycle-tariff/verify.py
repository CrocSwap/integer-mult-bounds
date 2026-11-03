#!/usr/bin/env python3
"""Exact Boolean triple cycle tariff. Produced by Nick Petalas. Apache-2.0."""

from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


TARGET = (3, 5, 6)
CYCLE = ((1, 0), (2, 1), (0, 2))
FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def column_step(state, gate):
    i, j, coefficient = gate
    need(0 <= i < 3 and 0 <= j < 3 and i != j, "invalid directed edge")
    need(1 <= coefficient <= 7, "invalid nonzero Boolean coefficient")
    result = list(state)
    result[i] ^= coefficient & state[j]
    return tuple(result)


def column_graph(root):
    start = tuple(7 if i == root else 0 for i in range(3))
    distance = {start: 0}
    queue = deque([start])
    gates = tuple((i, j, a) for i, j in CYCLE for a in range(1, 8))
    for _ in range(343):
        if not queue:
            break
        state = queue.popleft()
        for gate in gates:
            result = column_step(state, gate)
            if result not in distance:
                need(len(distance) < 343, "column-state capacity exceeded")
                distance[result] = distance[state] + 1
                queue.append(result)
    need(not queue and len(distance) == 343, "incomplete nonzero-column graph")
    for state in distance:
        for gate in gates:
            result = column_step(state, gate)
            need(abs(distance[result] - distance[state]) <= 1, "distance edge")
    need(distance[TARGET] == 4, "cycle column distance is not four")
    return dict(sorted(Counter(distance.values()).items()))


def scalar_column_obstruction(root):
    """Enumerate the columns reachable by every word of length <=3."""
    start = tuple(1 << root for _ in range(3))
    goal = (3, 5, 6)  # Each bit-coordinate column, encoded by destination bits.
    frontier = {start}
    counts = [1]
    for _ in range(3):
        next_frontier = set()
        for columns in frontier:
            for destination, source in CYCLE:
                for chosen in range(1, 8):
                    changed = []
                    for coordinate, column in enumerate(columns):
                        active = (chosen >> coordinate) & (column >> source) & 1
                        changed.append(column ^ (active << destination))
                    next_frontier.add(tuple(changed))
        need(goal not in next_frontier, "a three-step column word exists")
        frontier = next_frontier
        counts.append(len(frontier))
    return counts


def suffix(root):
    following, last = (root + 1) % 3, (root + 2) % 3
    return ((following, root, TARGET[last]), (last, following, 7),
            (following, root, TARGET[root]), (root, last, 7 ^ TARGET[root]))


def program(root):
    tail = suffix(root)
    return tuple(reversed(tail)) + ((root, 3, 7),) + tail


def literal(state, word):
    """Bit-list arithmetic, separate from the packed column transition."""
    rows = [[(value >> bit) & 1 for bit in range(3)] for value in state]
    for destination, source, coefficient in word:
        need(0 <= destination < 3 and 0 <= source < 4, "invalid row")
        need(destination != source and 1 <= coefficient <= 7, "invalid gate")
        for bit in range(3):
            if (coefficient >> bit) & 1:
                rows[destination][bit] = (rows[destination][bit] + rows[source][bit]) % 2
    return tuple(sum(value << bit for bit, value in enumerate(row)) for row in rows)


def expected(state):
    return tuple(state[i] ^ (TARGET[i] & state[3]) for i in range(3)) + (state[3],)


def endpoint(word):
    for column in range(4):
        for bit in range(3):
            state = tuple(1 << bit if i == column else 0 for i in range(4))
            if literal(state, word) != expected(state):
                return False
    return True


def check_words():
    scalar_cases = 0
    for root in range(3):
        word = program(root)
        need(len(word) == 9 and endpoint(word), "formal arbitrary-dirt endpoint")
        need(sum(j == 3 for _, j, _ in word) == 1, "insertion count")
        need(all(j == 3 or (i, j) in CYCLE for i, j, _ in word), "off-cycle gate")
        for state in product(range(8), repeat=4):
            result = literal(state, word)
            need(result == expected(state), "literal scalar endpoint")
            need(literal(result, tuple(reversed(word))) == state, "literal inverse")
            scalar_cases += 1
    return scalar_cases


def tariff(insertion_prices, cycle_price, reverse_prices):
    need(len(insertion_prices) == 3 and len(reverse_prices) == 3, "three prices required")
    need(cycle_price > 0, "cycle price must be positive")
    need(min(insertion_prices) >= 8 * cycle_price, "insertion prices outside cone")
    need(min(reverse_prices) >= 8 * cycle_price, "reverse prices outside cone")
    return min(insertion_prices) + 8 * cycle_price


def check_prices():
    cases = 0
    for denominator in (1, 3, 7):
        c = Fraction(1, denominator)
        for mu in ((8, 8, 8), (100, 100, 100), (9, 20, 30), (31, 8, 19)):
            prices = tuple(x * c for x in mu)
            reverse = (8 * c, 100 * c, 12 * c)
            optimum = tariff(prices, c, reverse)
            root = min(range(3), key=lambda i: prices[i])
            bill = sum(prices[i] if j == 3 else c for i, j, _ in program(root))
            need(bill == optimum, "attaining word tariff")
            need(2 * min(prices) >= optimum, "multi-insertion bound")
            need(min(prices) + min(reverse) >= optimum, "reverse-edge bound")
            cases += 1
    need(tariff((100, 100, 100), 1, (100, 100, 100)) == 108, "concrete tariff")
    return cases


def check_controls():
    word = program(0)
    for index in range(9):
        need(not endpoint(word[:index] + word[index + 1:]), "omitted-gate mutant")
    for index, (i, j, a) in enumerate(word):
        mutant = word[:index] + ((i, j, a ^ 1),) + word[index + 1:]
        if a ^ 1:
            need(not endpoint(mutant), "coefficient mutant")
    for root in range(3):
        need(not endpoint(((root, 3, 7),) + suffix(root)), "missing dirt preparation")
    invalid = (((7, 8, 8), 1, (8, 8, 8)), ((8, 8, 8), 1, (8, 7, 8)),
               ((8, 8, 8), 0, (8, 8, 8)), ((8, 8), 1, (8, 8, 8)))
    for prices, c, reverse in invalid:
        try:
            tariff(prices, c, reverse)
        except ValueError:
            continue
        raise ValueError("invalid tariff boundary accepted")
    return 9 + sum((a ^ 1) != 0 for _, _, a in word) + 3 + len(invalid)


def main():
    layers = [column_graph(root) for root in range(3)]
    short = [scalar_column_obstruction(root) for root in range(3)]
    cases = check_words()
    prices = check_prices()
    controls = check_controls()
    folder = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        content = (folder / name).read_bytes()
        need(len(content) <= 131072, "package file capacity exceeded")
        hashes[name] = sha256(content).hexdigest()
    print(json.dumps({"status": "PASS_BOOLEAN_DIRECTED_CYCLE_TARIFF",
                      "claim_type": "scoped proof with exact finite corroboration",
                      "column_states_per_root": 343, "minimum_suffix_adds": [4] * 3,
                      "distance_layers": layers, "short_word_frontiers": short,
                      "literal_forward_inverse_inputs": cases,
                      "price_fixtures": prices, "rejection_controls": controls,
                      "concrete_optimum": 108, "direct_insertion_bill": 300,
                      "word_root_zero": program(0), "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
