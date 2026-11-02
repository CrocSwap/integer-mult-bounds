#!/usr/bin/env python3
"""Exact finite evidence for fixed-weight tours. Produced by Nick Petalas.

Apache-2.0. Standard library only. Universal claims rest on PROOF.md.
"""

from collections import deque
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def domain(n, k, limit=12):
    require(type(n) is int and type(k) is int, "integer dimensions required")
    require(1 <= n <= limit and 0 <= k <= n, "dimension outside finite domain")


def tariff(n, k):
    domain(n, k)
    return 0 if k == 0 else 2 * comb(n, k) + 2 * k - 2


def gray_layer(n, k):
    domain(n, k)
    return tuple(i ^ (i >> 1) for i in range(1 << n)
                 if (i ^ (i >> 1)).bit_count() == k)


def layer_set(n, k):
    domain(n, k)
    return {sum(1 << j for j in positions)
            for positions in combinations(range(n), k)}


def expand_walk(n, k, listing):
    domain(n, k)
    require(len(listing) == comb(n, k), "wrong layer size")
    require(set(listing) == layer_set(n, k), "wrong layer masks")
    current = 0
    walk = [0]
    for target in (*listing, 0):
        difference = current ^ target
        for bit in range(n):
            if difference & (1 << bit):
                current ^= 1 << bit
                walk.append(current)
    return tuple(walk)


def check_walk(n, k, walk):
    domain(n, k)
    require(1 <= len(walk) <= n * (comb(n, k) + 1) + 1, "walk capacity")
    require(walk[0] == walk[-1] == 0, "anchor must return")
    require(all(type(x) is int and 0 <= x < (1 << n) for x in walk), "invalid mask")
    require(all((a ^ b).bit_count() == 1 for a, b in zip(walk, walk[1:])),
            "each step must toggle one source")
    require(layer_set(n, k) <= set(walk), "missing required mask")
    require(len(walk) - 1 == tariff(n, k), "nonoptimal transition count")


def shortest_cover(n, k):
    """BFS permits every cube step, arbitrary repeats and off-layer states."""
    domain(n, k, limit=5)
    goals = {mask: i for i, mask in enumerate(sorted(layer_set(n, k)))}
    complete = (1 << len(goals)) - 1
    initial = 1 << goals[0] if 0 in goals else 0
    queue = deque([(0, initial, 0)])
    seen = {(0, initial)}
    capacity = 1 << (n + len(goals))
    for _ in range(capacity):
        require(bool(queue), "covering walk must exist")
        position, visited, distance = queue.popleft()
        if position == 0 and visited == complete:
            return distance, len(seen)
        for bit in range(n):
            neighbor = position ^ (1 << bit)
            following = visited | (1 << goals[neighbor] if neighbor in goals else 0)
            state = (neighbor, following)
            if state not in seen:
                seen.add(state)
                queue.append((neighbor, following, distance + 1))
        require(len(seen) <= capacity, "BFS state capacity")
    raise ValueError("finite state space exhausted without a covering walk")


def compile_word(n, k, copies):
    domain(n, k, limit=8)
    require(type(copies) is int and 1 <= copies <= 3, "copy multiplicity")
    gates = []
    current = 0
    for index, mask in enumerate(gray_layer(n, k)):
        difference = current ^ mask
        for bit in range(n):
            if difference & (1 << bit):
                gates.append((0, bit + 1))
        current = mask
        for copy in range(copies):
            gates.append((n + 1 + index * copies + copy, 0))
    for bit in range(n):
        if current & (1 << bit):
            gates.append((0, bit + 1))
    return tuple(gates)


def apply_word(rows, gates):
    require(1 <= len(rows) <= 219 and len(gates) <= 356, "circuit capacity")
    result = list(rows)
    for destination, source in gates:
        require(type(destination) is int and type(source) is int,
                "integer row references required")
        require(0 <= destination < len(rows) and 0 <= source < len(rows),
                "row reference outside boundary")
        require(destination != source, "self ADD is outside the alphabet")
        result[destination] ^= result[source]
    return tuple(result)


def expected_rows(n, k, copies, rows):
    result = list(rows)
    for index, mask in enumerate(gray_layer(n, k)):
        parity = rows[0]
        for bit in range(n):
            if mask & (1 << bit):
                parity ^= rows[bit + 1]
        for copy in range(copies):
            target = n + 1 + index * copies + copy
            result[target] ^= parity
    return tuple(result)


def check_word(n, k, copies, gates):
    domain(n, k, limit=8)
    require(type(copies) is int and 1 <= copies <= 3, "copy multiplicity")
    count = n + 1 + copies * comb(n, k)
    require(len(gates) == copies * comb(n, k) + tariff(n, k), "full row invoice")
    writes = [0] * count
    for destination, source in gates:
        require((destination == 0 and 1 <= source <= n)
                or (n < destination < count and source == 0), "gate alphabet")
        writes[destination] += 1
    require(all(writes[row] == 1 for row in range(n + 1, count)),
            "each target must be written exactly once")
    basis = tuple(1 << row for row in range(count))
    require(apply_word(basis, gates) == expected_rows(n, k, copies, basis),
            "arbitrary-input coefficient map or source restoration")
    return count


def check_layers():
    cases = 0
    vertices = 0
    for n in range(1, 13):
        for k in range(n + 1):
            listing = gray_layer(n, k)
            require(len(listing) == len(set(listing)) == comb(n, k), "layer census")
            require(set(listing) == layer_set(n, k), "independent combination census")
            if k:
                require(listing[0] == (1 << k) - 1, "first Gray mask")
                require(listing[-1] == (1 << (n - 1)) + (1 << (k - 1)) - 1,
                        "last Gray mask")
                require(all((a ^ b).bit_count() == 2
                            for a, b in zip(listing, listing[1:])), "exchange adjacency")
            check_walk(n, k, expand_walk(n, k, listing))
            cases += 1
            vertices += len(listing)
    return {"layer_cases": cases, "required_masks": vertices}


def check_oracle():
    cases = []
    for n in range(1, 6):
        for k in range(n + 1):
            distance, states = shortest_cover(n, k)
            require(distance == tariff(n, k), "independent shortest-walk mismatch")
            cases.append({"n": n, "k": k, "distance": distance, "states": states})
    return cases


def check_circuits():
    cases = coefficients = dirty_cases = inverse_cases = 0
    for n in range(1, 9):
        for k in range(n + 1):
            for copies in range(1, 4):
                gates = compile_word(n, k, copies)
                count = check_word(n, k, copies, gates)
                cases += 1
                coefficients += count * count
                rows = tuple(((1 << 73) - 1) ^ (i * 0x13579BDF) for i in range(count))
                require(apply_word(rows, gates) == expected_rows(n, k, copies, rows),
                        "73-bit dirty rows")
                require(apply_word(apply_word(rows, gates), tuple(reversed(gates))) == rows,
                        "inverse must restore every input")
                dirty_cases += 1
                inverse_cases += 1
                if n <= 3 and copies == 1:
                    for bits in range(1 << count):
                        rows = tuple((bits >> i) & 1 for i in range(count))
                        require(apply_word(rows, gates) == expected_rows(n, k, copies, rows),
                                "exhaustive arbitrary dirty data")
                        dirty_cases += 1
    gates = compile_word(5, 3, 1)
    require(len(gates) == 34 and 4 * comb(5, 3) == 40, "attaining fixture")
    return {"circuit_cases": cases, "coefficient_positions": coefficients,
            "dirty_data_cases": dirty_cases, "inverse_cases": inverse_cases,
            "fixture": {"n": 5, "k": 3, "targets": 10, "transitions": 24,
                        "complete_row_adds": len(gates), "direct_row_adds": 40}}


def check_rejections():
    controls = 0
    for n, k in [(0, 0), (13, 2), (4, -1), (4, 5), (True, 1), (3, 1.0)]:
        try:
            gray_layer(n, k)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid dimensions accepted")
    walk = expand_walk(5, 3, gray_layer(5, 3))
    for changed in [walk[:-1], (0,), (*walk, 1, 0), (0, 32, 0)]:
        try:
            check_walk(5, 3, changed)
        except ValueError:
            controls += 1
        else:
            raise ValueError("bad covering walk accepted")
    gates = compile_word(5, 3, 1)
    changed_words = [gates[:-1], gates[1:], gates + ((0, 1), (0, 1)),
                     ((6, 1),) + gates[1:]]
    first = next(i for i, gate in enumerate(gates) if gate[0] == 0)
    alternate = 1 if gates[first][1] != 1 else 2
    changed_words.append(gates[:first] + ((0, alternate),) + gates[first + 1:])
    for changed in changed_words:
        try:
            check_word(5, 3, 1, changed)
        except ValueError:
            controls += 1
        else:
            raise ValueError("bad source restoration or target map accepted")
    for copies in [0, 4, True]:
        try:
            compile_word(5, 3, copies)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid multiplicity accepted")
    return controls


def source_hashes():
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as stream:
            payload = stream.read(131073)
        require(len(payload) <= 131072, "package file exceeds receipt capacity")
        hashes[name] = sha256(payload).hexdigest()
    return hashes


def main():
    result = {"claim_type": "scoped proof with finite corroboration",
              "layers": check_layers(), "shortest_walks": check_oracle(),
              "circuits": check_circuits(), "rejection_controls": check_rejections(),
              "sha256": source_hashes(),
              "status": "PASS_FIXED_WEIGHT_BORROWED_TOURS_NO_NEW_KAPPA"}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
