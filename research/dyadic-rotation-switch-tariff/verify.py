#!/usr/bin/env python3
"""Exact endpoint, tariff, and optimality corroboration; standard library only."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path

MAX_WIDTH = 12
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(h, c):
    require(type(h) is int and 1 <= h <= MAX_WIDTH, "width outside 1..12")
    require(type(c) is int and 0 <= c < (1 << h), "invalid offset")


def tariff(h, c):
    validate(h, c)
    total = 0
    for k in range(1, h + 1):
        modulus = 1 << k
        residue = c % modulus
        total += (1 << (h - k)) * min(residue, modulus - residue)
    return total


def layers(h, c):
    """Each tuple contains the lower endpoints of disjoint bit-i edges."""
    validate(h, c)
    result = []
    for i in range(h - 1, -1, -1):
        bit = 1 << i
        low_offset = c % bit
        edges = []
        for x in range(1 << h):
            carry = int((x % bit) + low_offset >= bit)
            if not (x & bit) and (((c >> i) & 1) ^ carry):
                edges.append(x)
        result.append((i, tuple(edges)))
    return tuple(result)


def execute(h, program):
    """Track token identities at positions, without using the carry formula."""
    require(type(h) is int and 1 <= h <= 8, "execution width outside 1..8")
    tokens = list(range(1 << h))
    for i, endpoints in program:
        bit = 1 << i
        for x in endpoints:
            tokens[x], tokens[x ^ bit] = tokens[x ^ bit], tokens[x]
    return tokens


def endpoint(h, c, tokens):
    n = 1 << h
    return all(tokens[(x + c) % n] == x for x in range(n))


def check_routes():
    cases = 0
    for h in range(1, 9):
        n = 1 << h
        for c in range(n):
            program = layers(h, c)
            require(endpoint(h, c, execute(h, program)), "wrong routed token")
            count = sum(len(edges) for _, edges in program)
            distance = sum((x ^ ((x + c) % n)).bit_count() for x in range(n))
            require(2 * count == distance, "not distance optimal")
            require(count == tariff(h, c), "wrong switch tariff")
            cases += 1
    return cases


def check_maxima():
    rows = []
    for h in range(1, MAX_WIDTH + 1):
        n = 1 << h
        values = [tariff(h, c) for c in range(n)]
        maximum = max(values)
        numerator = (3 * h + 1) * n - (-1) ** h
        require(numerator % 9 == 0, "nonintegral maximum")
        require(maximum == numerator // 9, "wrong maximum")
        a = (n - (-1) ** h) // 3
        maximizers = [c for c, value in enumerate(values) if value == maximum]
        require(maximizers == sorted({a, n - a}), "wrong equality cases")
        rows.append({"h": h, "maximum": maximum, "offsets": maximizers})
    return rows


def cube_distances(h):
    """Independent BFS over every token permutation, only for h <= 3."""
    require(1 <= h <= 3, "BFS width outside 1..3")
    n = 1 << h
    edges = [(x, x ^ (1 << i)) for x in range(n)
             for i in range(h) if not x & (1 << i)]
    identity = tuple(range(n))
    distances = {identity: 0}
    queue = deque([identity])
    capacity = {2: 2, 4: 24, 8: 40320}[n]
    # Connected edge transpositions generate S_n, with n! <= 40320 states.
    for _ in range(capacity):
        require(bool(queue), "BFS ended before its factorial bound")
        state = queue.popleft()
        for x, y in edges:
            successor = list(state)
            successor[x], successor[y] = successor[y], successor[x]
            key = tuple(successor)
            if key not in distances:
                require(len(distances) < capacity, "BFS capacity exceeded")
                distances[key] = distances[state] + 1
                queue.append(key)
    require(not queue and len(distances) == capacity, "incomplete BFS")
    for c in range(n):
        target = tuple((position - c) % n for position in range(n))
        require(distances[target] == tariff(h, c), "BFS optimum disagrees")
    return capacity


def check_controls():
    program = layers(3, 3)
    i, edges = program[0]
    damaged = ((i, edges[1:]),) + program[1:]
    require(not endpoint(3, 3, execute(3, damaged)), "omission control accepted")
    require(not endpoint(3, 3, execute(3, tuple(reversed(program)))),
            "order control accepted")
    invalid = [(0, 0), (13, 0), (3, -1), (3, 8), (True, 0), (3, False)]
    for h, c in invalid:
        try:
            tariff(h, c)
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    return 2 + len(invalid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write generated evidence outside checkout")
    args = parser.parse_args()
    report = {"claim_type": "scoped combinatorial proof with finite corroboration",
              "route_cases": check_routes(), "maxima": check_maxima(),
              "bfs_states": [cube_distances(h) for h in range(1, 4)],
              "controls": check_controls()}
    names = ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    report["source_sha256"] = {
        name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        args.receipt.write_text(output)
    print(output, end="")
    print("PASS_DYADIC_ROTATION_SWITCH_TARIFF")


if __name__ == "__main__":
    main()
