#!/usr/bin/env python3
"""Exact finite corroboration of the Hurwitz budget/success theorem."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
BOUND_FILES = (
    "README.md", "PROOF.md", "verify.py", "TASK.json", "SOURCES.json", "VERIFY.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def maximum_success(pairs, width, budget):
    require(type(pairs) is int and pairs >= 1, "positive pair count required")
    require(type(width) is int and width >= 0, "nonnegative width required")
    require(type(budget) is int and budget >= 0, "nonnegative budget required")
    missing = max(0, pairs * width - budget // 2)
    return Fraction(1, 1 << missing)


def decode_partial_parities(inputs, width, kept):
    pairs = len(inputs) // 2
    require(len(inputs) == 2 * pairs and pairs >= 1, "paired inputs required")
    require(0 <= kept <= pairs * width, "invalid transmitted coordinate count")
    payload = []
    for coordinate in range(kept):
        pair, bit = divmod(coordinate, width)
        payload.append(((inputs[2 * pair] ^ inputs[2 * pair + 1]) >> bit) & 1)
    outputs = []
    for port in range(2 * pairs):
        value = inputs[port ^ 1]
        for bit in range(width):
            coordinate = (port // 2) * width + bit
            if coordinate < kept:
                value ^= payload[coordinate] << bit
        outputs.append(value)
    return tuple(outputs)


def witness_census():
    cases = inputs_checked = 0
    rows = []
    for pairs in range(1, 6):
        for width in range(4):
            bits = 2 * pairs * width
            if bits > 12:
                continue
            for budget in range(2 * pairs * width + 3):
                kept = min(pairs * width, budget // 2)
                successes = 0
                for word in range(1 << bits):
                    inputs = tuple((word >> (port * width)) & ((1 << width) - 1)
                                   for port in range(2 * pairs))
                    successes += decode_partial_parities(inputs, width, kept) == inputs
                require(Fraction(successes, 1 << bits) ==
                        maximum_success(pairs, width, budget), "attaining code failed")
                require(2 * kept <= budget, "attaining code exceeds budget")
                rows.append([pairs, width, budget, successes, 1 << bits])
                inputs_checked += 1 << bits
                cases += 1
    return {"cases": cases, "input_tuples": inputs_checked,
            "rows_sha256": hashlib.sha256(json.dumps(rows).encode()).hexdigest()}


def conflict_graph():
    """An edge forbids two inputs succeeding with the same broadcast bit."""
    adjacency = []
    for left in range(16):
        neighbors = 0
        for right in range(16):
            conflict = any(((left >> (port ^ 1)) & 1) ==
                           ((right >> (port ^ 1)) & 1) and
                           ((left >> port) & 1) != ((right >> port) & 1)
                           for port in range(4))
            neighbors |= int(conflict) << right
        adjacency.append(neighbors)
    return adjacency


def optimal_success_sets(adjacency):
    """Exhaust every induced graph by a nonrecursive independent-set DP."""
    sizes = [0] * (1 << 16)
    sets = [0] * (1 << 16)
    for mask in range(1, 1 << 16):
        vertex_bit = mask & -mask
        vertex = vertex_bit.bit_length() - 1
        rest = mask ^ vertex_bit
        allowed = rest & ~adjacency[vertex]
        if sizes[rest] >= 1 + sizes[allowed]:
            sizes[mask], sets[mask] = sizes[rest], sets[rest]
        else:
            sizes[mask], sets[mask] = 1 + sizes[allowed], vertex_bit | sets[allowed]
    return sizes, sets


def decoder_for_sets(zero_set, one_set):
    lookup = [[-1] * 4 for _ in range(4)]
    for broadcast, success_set in enumerate((zero_set, one_set)):
        for word in range(16):
            if not (success_set >> word) & 1:
                continue
            for port in range(4):
                observation = 2 * broadcast + ((word >> (port ^ 1)) & 1)
                bit = (word >> port) & 1
                old = lookup[port][observation]
                require(old in (-1, bit), "successful inputs have conflicting decodes")
                lookup[port][observation] = bit
    return [[max(0, bit) for bit in row] for row in lookup]


def boolean_broadcast_census():
    adjacency = conflict_graph()
    sizes, sets = optimal_success_sets(adjacency)
    all_inputs = (1 << 16) - 1
    require(sizes[all_inputs] == 4, "zero-message optimal success count changed")
    histogram = Counter()
    for truth_table in range(1 << 16):
        zero_inputs = all_inputs ^ truth_table
        predicted = sizes[zero_inputs] + sizes[truth_table]
        lookup = decoder_for_sets(sets[zero_inputs], sets[truth_table])
        actual = 0
        for word in range(16):
            broadcast = (truth_table >> word) & 1
            actual += all(lookup[port][2 * broadcast + ((word >> (port ^ 1)) & 1)]
                          == ((word >> port) & 1) for port in range(4))
        require(actual == predicted, "independent decoder optimum not attained")
        require(Fraction(actual, 16) <= maximum_success(2, 1, 2),
                "one-bit broadcast exceeds theorem")
        histogram[actual] += 1
    require(sum(histogram.values()) == 65536, "incomplete encoder census")
    require(max(histogram) == 8, "sharp broadcast success count changed")
    return {"boolean_encoders": 65536, "literal_input_tuples": 65536 * 16,
            "induced_graphs": 65536,
            "optimal_success_histogram": {str(k): v for k, v in sorted(histogram.items())}}


def rejection_controls():
    rejected = 0
    for arguments in ((0, 1, 1), (1, -1, 1), (1, 1, -1), (True, 1, 1)):
        try:
            maximum_success(*arguments)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid theorem parameters accepted")
    require(maximum_success(5, 1, 9) == Fraction(1, 2), "odd budget rounded upward")
    require(maximum_success(5, 1, 0) == Fraction(1, 32), "mate guesses treated as independent")
    require(decode_partial_parities((0, 1), 1, 0) != (0, 1), "missing bit undetected")
    require(decode_partial_parities((0, 1), 1, 1) == (0, 1), "positive code rejected")
    try:
        decoder_for_sets((1 << 0) | (1 << 1), 0)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("conflicting successful inputs accepted")
    require(all(decode_partial_parities((x, x), 1, 0) == (x, x) for x in range(2)),
            "correlated-input boundary example failed")
    require(Fraction(1, 1) > maximum_success(1, 1, 0), "boundary example is vacuous")
    return {"rejected_invalid_cases": rejected, "odd_budget": "1/2",
            "zero_budget_ten_ports": "1/32", "correlated_boundary": "1"}


def result():
    hashes = {}
    for name in BOUND_FILES:
        payload = (PACKAGE / name).read_bytes()
        require(len(payload) <= 1024 * 1024, "package input exceeds byte limit")
        hashes[name] = hashlib.sha256(payload).hexdigest()
    return {"schema": "hurwitz-budget-success/1", "claim_type": "scoped proof",
            "source_sha256": hashes, "witness_census": witness_census(),
            "boolean_broadcast_census": boolean_broadcast_census(),
            "controls": rejection_controls(), "new_kappa": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write generated receipt to a new external file")
    args = parser.parse_args()
    if args.write:
        require(not args.write.resolve().is_relative_to(PACKAGE),
                "generated replay output must be outside the package")
    actual = result()
    if args.write:
        with args.write.open("x", encoding="utf-8") as output:
            output.write(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        require(actual == expected, "receipt mismatch")
    print("PASS_HURWITZ_BUDGET_SUCCESS " + json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
