#!/usr/bin/env python3
"""Exact local F2 circuit minimum and integer transfer check."""

from itertools import product
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
NAMES = ("a", "b", "h", "c")
INDEX = {name: i for i, name in enumerate(NAMES)}
PHYSICAL = (33, 38, 468, 77)
OLD = ((1, 0), (2, 0), (3, 0), (2, 1))
NEW = ((2, 1), (1, 0), (3, 0))
TARGET_ROWS = (0b0001, 0b0011, 0b0110, 0b1001)
OLD_INTEGER = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (2, 1, 1, 0),
    (1, 0, 0, 1),
)
NEW_INTEGER = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 1, 0),
    (1, 0, 0, 1),
)
DELTA = (
    (0, 0, 0, 0),
    (0, 0, 0, 0),
    (2, 0, 0, 0),
    (0, 0, 0, 0),
)
DISTINCT_MAPS = (1, 12, 97, 626)
TARGET_WORDS_BY_LENGTH = (0, 0, 0, 3)
SHORTEST_WORDS = (
    "h ^= b ; b ^= a ; c ^= a",
    "h ^= b ; c ^= a ; b ^= a",
    "c ^= a ; h ^= b ; b ^= a",
)
POSITIVE_CONTROL = ((1, 0), (3, 2))
POSITIVE_CONTROL_ROWS = (0b0001, 0b0011, 0b0100, 0b1100)
BAD_SOURCE_CONTROL = ((2, 0), (1, 0), (3, 0))
TWO_GATE_CONTROL = ((2, 1), (1, 0))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def f2_rows(word):
    rows = [1 << i for i in range(4)]
    for destination, source in word:
        rows[destination] ^= rows[source]
    return tuple(rows)


def integer_rows(word):
    rows = [[int(i == j) for j in range(4)] for i in range(4)]
    for destination, source in word:
        rows[destination] = [
            left + right for left, right in zip(rows[destination], rows[source])
        ]
    return tuple(tuple(row) for row in rows)


def run_boolean(word, value):
    state = list(value)
    for destination, source in word:
        state[destination] ^= state[source]
    return tuple(state)


def word_text(word):
    return " ; ".join(
        f"{NAMES[destination]} ^= {NAMES[source]}"
        for destination, source in word
    )


def named_word(value):
    require(isinstance(value, list), "word must be a JSON array")
    result = []
    for gate in value:
        require(isinstance(gate, list) and len(gate) == 2, "malformed gate")
        destination, source = gate
        require(destination in INDEX and source in INDEX, "unknown local register")
        require(destination != source, "self-add is outside the CNOT alphabet")
        result.append((INDEX[destination], INDEX[source]))
    return tuple(result)


def enumerate_cnot_words():
    operations = tuple(
        (destination, source)
        for destination in range(4)
        for source in range(4)
        if destination != source
    )
    distinct_counts = []
    target_words = []
    target_counts = []
    for length in range(4):
        maps = {}
        matches = []
        for word in product(operations, repeat=length):
            rows = f2_rows(word)
            maps[rows] = maps.get(rows, 0) + 1
            if rows == TARGET_ROWS:
                matches.append(word)
        distinct_counts.append(len(maps))
        target_counts.append(len(matches))
        target_words.append(matches)
    return tuple(distinct_counts), tuple(target_counts), tuple(target_words)


def expected_certificate():
    return {
        "minimum_adds": 3,
        "target_f2_rows": list(TARGET_ROWS),
        "old_integer_rows": [list(row) for row in OLD_INTEGER],
        "new_integer_rows": [list(row) for row in NEW_INTEGER],
        "old_minus_new": [list(row) for row in DELTA],
        "distinct_maps_by_length": list(DISTINCT_MAPS),
        "target_words_by_length": list(TARGET_WORDS_BY_LENGTH),
        "shortest_words": list(SHORTEST_WORDS),
        "boolean_inputs": 16,
        "positive_control_target_rows": list(POSITIVE_CONTROL_ROWS),
    }


def verify():
    source = json.loads((PACKAGE / "INPUT.json").read_text())
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text())
    predecessor = json.loads((PACKAGE / "PREDECESSORS.json").read_text())

    require(source["format"] == "r439-b509-local-minimality/1", "wrong input format")
    require(source["predecessor_pr"] == 1221, "wrong predecessor PR")
    require(source["predecessor_head"] == "6deda901721316fcb61c6e2a6dd6b537de183452",
            "predecessor head changed")
    require(tuple(source["register_order"]) == NAMES, "register order changed")
    require(tuple(source["physical_registers"]) == PHYSICAL, "physical labels changed")
    require(named_word(source["old_word"]) == OLD, "old source word changed")
    require(named_word(source["new_word"]) == NEW, "new witness word changed")
    require(source["boolean_endpoint"] == ["a", "b+a", "h+b", "c+a"],
            "endpoint statement changed")
    require(source["gate_contract"].startswith("one scalar ADD writes one destination"),
            "gate contract changed")
    require(predecessor["head"] == source["predecessor_head"],
            "predecessor manifest does not match the input pin")
    require(predecessor["pr"] == 1221 and predecessor["state_at_claim"] == "open",
            "predecessor metadata changed")
    concurrent = predecessor["concurrent_matrix_audit"]
    require(concurrent["pr"] == 1344
            and concurrent["head_at_overlap_refresh"]
            == "a42e525e9868970f3fa2d99dccca45f014aa0fd3",
            "concurrent matrix-audit pin changed")
    require("does not claim a circuit minimum" in concurrent["scope_added_here"],
            "overlap distinction changed")

    require(f2_rows(OLD) == TARGET_ROWS, "old word misses the target endpoint")
    require(f2_rows(NEW) == TARGET_ROWS, "new word misses the target endpoint")
    require(integer_rows(OLD) == OLD_INTEGER, "old integer transfer changed")
    require(integer_rows(NEW) == NEW_INTEGER, "new integer transfer changed")
    difference = tuple(
        tuple(left - right for left, right in zip(old_row, new_row))
        for old_row, new_row in zip(integer_rows(OLD), integer_rows(NEW))
    )
    require(difference == DELTA, "integer transfer difference changed")

    # Check the complete local truth table, including all dirty inputs.
    for value in product((0, 1), repeat=4):
        a, b, h, c = value
        target = (a, b ^ a, h ^ b, c ^ a)
        require(run_boolean(OLD, value) == target, "old word fails an input")
        require(run_boolean(NEW, value) == target, "new word fails an input")

    counts, target_counts, words = enumerate_cnot_words()
    require(counts == DISTINCT_MAPS, "distinct-map census changed")
    require(target_counts == TARGET_WORDS_BY_LENGTH, "target word count changed")
    require(tuple(map(word_text, words[3])) == SHORTEST_WORDS,
            "length-three realization census changed")
    require(len(NEW) == 3, "attaining word is not length three")

    # Failure controls: a wrong source and a two-gate prefix must miss the target.
    require(f2_rows(BAD_SOURCE_CONTROL) != TARGET_ROWS,
            "wrong-source negative control unexpectedly passes")
    require(f2_rows(TWO_GATE_CONTROL) != TARGET_ROWS,
            "two-gate negative control unexpectedly passes")
    require(f2_rows(POSITIVE_CONTROL) == POSITIVE_CONTROL_ROWS,
            "positive two-gate enumeration control failed")

    require(expected == expected_certificate(), "EXPECTED.json does not match replay")
    return {
        "minimum": 3,
        "length3_words": len(words[3]),
        "maps": counts,
        "boolean_inputs": 16,
        "integer_delta": difference,
    }


def main():
    result = verify()
    print(
        "PASS_R439_B509_LOCAL_MINIMALITY "
        f"minimum={result['minimum']} length3_words={result['length3_words']} "
        f"maps={','.join(map(str, result['maps']))} "
        f"boolean_inputs={result['boolean_inputs']} "
        "integer_delta=2e_h_e_a no_new_kappa"
    )


if __name__ == "__main__":
    main()
