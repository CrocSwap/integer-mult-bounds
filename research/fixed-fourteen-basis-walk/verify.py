#!/usr/bin/env python3
"""Exact fixed-set routing and arbitrary-dirty paired-readout checks."""

import argparse
import hashlib
import json
from pathlib import Path


POINTS = (0, 1, 2, 3, 4, 5, 6, 8, 16, 24, 32, 40, 48, 63)
CYCLE = (0, 16, 48, 32, 40, 8, 24, 63, 5, 4, 6, 2, 3, 1, 0)
SOURCE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cycle_steps(cycle):
    require(len(cycle) == 15, "fourteen edges required")
    require(cycle[0] == cycle[-1] == 0, "cycle must close at zero")
    require(tuple(sorted(cycle[:-1])) == POINTS, "wrong prefix set")
    return tuple(a ^ b for a, b in zip(cycle, cycle[1:]))


def tour_optimum(cap):
    """Held--Karp on the 14 terminals, with a fixed zero start."""
    require(cap in (3, 4, 6), "unsupported bounded arity")
    count = len(POINTS) - 1
    infinity = 1000  # Every fourteen-edge six-bit tour costs at most 84.
    costs = [[infinity] * count for _ in range(1 << count)]
    for j in range(count):
        weight = POINTS[j + 1].bit_count()
        if weight <= cap:
            costs[1 << j][j] = weight
    finite_states = 0
    for mask in range(1, 1 << count):
        for j in range(count):
            cost = costs[mask][j]
            if cost == infinity:
                continue
            finite_states += 1
            for k in range(count):
                bit = 1 << k
                weight = (POINTS[j + 1] ^ POINTS[k + 1]).bit_count()
                if mask & bit == 0 and weight <= cap:
                    costs[mask | bit][k] = min(costs[mask | bit][k], cost + weight)
    answers = [costs[-1][j] + POINTS[j + 1].bit_count()
               for j in range(count) if POINTS[j + 1].bit_count() <= cap
               and costs[-1][j] != infinity]
    return {"cost": min(answers) if answers else None, "finite_states": finite_states}


def query_word(cycle):
    steps = cycle_steps(cycle)
    reads = [[] for _ in POINTS]
    pairs = []
    for target in range(1, 64):
        pair = next((i, j) for i in range(14) for j in range(i + 1, 14)
                    if cycle[i] ^ cycle[j] == target)
        pairs.append(pair)
        for boundary in pair:
            reads[boundary].append(("A", target))
    word = []
    for boundary, step in enumerate(steps):
        word.extend(reads[boundary])
        word.append(("B", step))
    require(len(word) == 140, "incorrect complete query count")
    return tuple(word), pairs


def formal_endpoint(word):
    """Bit 0 is A_i(z_initial), bits 1..6 are A_i B_j(x_j)."""
    root = 1
    outputs = [1 << 7] * 64  # Each row's own independent initial value.
    for kind, mask in word:
        require(kind in ("A", "B") and 1 <= mask < 64, "invalid query")
        if kind == "B":
            root ^= mask << 1
        else:
            outputs[mask] ^= root
    return root == 1 and all(outputs[m] == (1 << 7) ^ (m << 1)
                             for m in range(1, 64))


def matrix_rows(seed, dimension):
    return tuple(((seed * (i + 1) * 7 + i * i + 3) ^ (seed >> i))
                 & ((1 << dimension) - 1) for i in range(dimension))


def apply_map(rows, value):
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(rows))


def dense_replay(word):
    cases = 0
    for dimension in (1, 2, 3):
        source_maps = tuple(matrix_rows(j + 1, dimension) for j in range(6))
        target_maps = tuple(matrix_rows(j + 11, dimension) for j in range(64))
        # 70 independent rows: six sources, one connector, 63 dirty targets.
        for basis in range(70 * dimension):
            initial = [0] * 70
            initial[basis // dimension] = 1 << (basis % dimension)
            expected = initial.copy()
            for mask in range(1, 64):
                value = 0
                for j in range(6):
                    if mask & (1 << j):
                        value ^= apply_map(source_maps[j], initial[j])
                expected[6 + mask] ^= apply_map(target_maps[mask], value)
            actual = initial.copy()
            for inverse, direction in enumerate((word, tuple(reversed(word)))):
                for kind, mask in direction:
                    if kind == "B":
                        for j in range(6):
                            if mask & (1 << j):
                                actual[6] ^= apply_map(source_maps[j], actual[j])
                    else:
                        actual[6 + mask] ^= apply_map(target_maps[mask], actual[6])
                require(actual == (initial if inverse else expected),
                        "dense forward/inverse endpoint mismatch")
                cases += 1
    return cases


def controls(word):
    rejected = 0
    for index in range(len(word)):
        require(not formal_endpoint(word[:index] + word[index + 1:]),
                "omitted query accepted")
        rejected += 1
    for index, (kind, mask) in enumerate(word):
        if kind == "B":
            for bit in range(6):
                if mask & (1 << bit):
                    reduced = mask ^ (1 << bit)
                    mutant = (word[:index] + ((kind, reduced),) + word[index + 1:]
                              if reduced else word[:index] + word[index + 1:])
                    require(not formal_endpoint(mutant), "unpaid source component accepted")
                    rejected += 1
    for bad in (CYCLE[:-1], (1,) + CYCLE[1:], CYCLE[:2] + (16,) + CYCLE[3:]):
        try:
            cycle_steps(bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid cycle accepted")
    return rejected


def certificate():
    steps = cycle_steps(CYCLE)
    weights = tuple(step.bit_count() for step in steps)
    distances = tuple((63 ^ p).bit_count() for p in POINTS if p != 63)
    require(min(distances) == 4, "isolated-point lower bound changed")
    require(sum(weights) == 12 + 2 * min(distances) == 20, "sharp cost bound failed")
    require(max(weights) == 4, "sharp arity witness failed")
    counts = [sum(bool(step & (1 << j)) for step in steps) for j in range(6)]
    require(all(count > 0 and count % 2 == 0 for count in counts), "source restoration failed")
    dp = {str(cap): tour_optimum(cap) for cap in (3, 4, 6)}
    require([dp[str(cap)]["cost"] for cap in (3, 4, 6)] == [None, 20, 20],
            "independent routing optimum disagrees")
    word, pairs = query_word(CYCLE)
    require(formal_endpoint(word), "free-symbol endpoint failed")
    require(formal_endpoint(tuple(reversed(word))), "free-symbol inverse failed")
    return {
        "claim_type": "scoped proof with exact finite corroboration",
        "points": POINTS, "cycle": CYCLE, "steps": steps, "weights": weights,
        "source_occurrences": counts, "maximum_arity": 4,
        "source_applications": 20, "root_queries": 140, "map_applications": 146,
        "held_karp": dp, "readout_boundary_pairs": pairs,
        "dense_forward_inverse_cases": dense_replay(word),
        "rejected_controls": controls(word),
        "source_sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                          for name in SOURCE_FILES},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a generated receipt")
    args = parser.parse_args()
    result = certificate()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.loads(json.dumps(result)) == expected, "receipt or source hashes changed")
        print("PASS_FIXED_FOURTEEN_BASIS_WALK arity=4 source_apps=20 "
              "root_queries=140 map_apps=146 dense_cases="
              + str(result["dense_forward_inverse_cases"]) + " controls="
              + str(result["rejected_controls"]))


if __name__ == "__main__":
    main()
