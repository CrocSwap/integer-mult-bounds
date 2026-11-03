#!/usr/bin/env python3
"""Check the new attaining lift; do not replay the predecessor lower bound."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PARENT = "341236425430103051216402"
LIFT = "374717236747275473071030571727164702"
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_word(text: str, dimension: int) -> tuple[int, ...]:
    require(type(dimension) is int and 1 <= dimension <= 8, "dimension outside 1..8")
    require(type(text) is str and 1 <= len(text) <= 64, "word length outside 1..64")
    require(all("0" <= a <= "7" for a in text), "invalid coordinate symbol")
    word = tuple(ord(a) - ord("0") for a in text)
    require(all(a < dimension for a in word), "coordinate outside dimension")
    return word


def prefix_path(word: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    require(1 <= len(word) <= 64, "unbounded path")
    require(all(type(a) is int and 0 <= a < 8 for a in word), "invalid path coordinate")
    prefixes = []
    current = 0
    for a in word:
        prefixes.append(current)
        current ^= 1 << a
    return tuple(prefixes), current


def interval_table(word: tuple[int, ...]) -> dict[int, tuple[int, int]]:
    """Accumulate each interval directly, without a prefix-pair implementation."""
    require(1 <= len(word) <= 64, "unbounded interval domain")
    require(all(type(a) is int and 0 <= a < 8 for a in word), "invalid interval coordinate")
    table = {0: (0, 0)}
    for start in range(len(word)):
        coefficients = [0] * 8
        for stop in range(start, len(word)):
            coefficients[word[stop]] = 1 - coefficients[word[stop]]
            mask = sum(coefficients[a] * (2 ** a) for a in range(8))
            if mask not in table:
                table[mask] = (start, stop + 1)
    return table


def certify(text: str) -> tuple[dict[str, object], dict[int, tuple[int, int]]]:
    word = parse_word(text, 8)
    require(len(word) == 36, "attaining word must have length 36")
    require(text.replace("7", "") == PARENT, "wrong literal projection")
    prefixes, final = prefix_path(word)
    require(final == 0, "word does not restore the accumulator")
    require(len(set(prefixes)) == 36, "lift is not a simple closed path")
    pair_differences = {a ^ b for a in prefixes for b in prefixes}
    require(pair_differences == set(range(256)), "prefix pairs miss a target")
    table = interval_table(word)
    require(set(table) == set(range(256)), "literal intervals miss a target")
    projected = {a & 127 for a in prefixes}
    parent_states, _ = prefix_path(parse_word(PARENT, 7))
    require(projected == set(parent_states), "wrong projected state set")
    require(word.count(7) == 12, "wrong number of new-coordinate calls")
    counts = [word.count(a) for a in range(8)]
    fibers = [sum(p in prefixes for p in (q, q + 128)) for q in sorted(projected)]
    require(fibers.count(2) == 12 and fibers.count(1) == 12, "wrong lift fibers")
    record = {"word": text, "parent": PARENT, "length": len(word),
              "coordinate_counts": counts, "distinct_states": len(set(prefixes)),
              "difference_masks": len(pair_differences), "interval_masks": len(table),
              "double_fibers": fibers.count(2), "single_fibers": fibers.count(1)}
    return record, table


def dirty_recovery(text: str, table: dict[int, tuple[int, int]]) -> int:
    """Execute literal scalar XORs on every source/dirty assignment."""
    word = parse_word(text, 8)
    require(set(table) == set(range(256)), "incomplete recovery table")
    checked = 0
    for inputs in range(512):
        sources = tuple((inputs >> a) & 1 for a in range(8))
        dirty = (inputs >> 8) & 1
        values = [dirty]
        for a in word:
            values.append(values[-1] ^ sources[a])
        require(values[-1] == dirty, "dirty accumulator was not restored")
        for mask in range(256):
            start, stop = table[mask]
            require(0 <= start <= stop <= len(word), "invalid recovery interval")
            expected = sum(sources[a] for a in range(8) if (mask >> a) & 1) % 2
            require(values[start] ^ values[stop] == expected, "incorrect dirty recovery")
            checked += 1
    return checked


def expect_bad_word(text: str, dimension: int) -> None:
    try:
        parse_word(text, dimension)
    except ValueError:
        return
    raise ValueError("malformed input was accepted")


def controls(table: dict[int, tuple[int, int]]) -> int:
    checked = 0
    for text, dimension in (("", 8), ("0" * 65, 8), ("8", 8),
                            ("-1", 8), ("7", 7), ("0", 0), ("0", 9)):
        expect_bad_word(text, dimension)
        checked += 1
    shortened = LIFT.replace("7", "", 1)
    _, final = prefix_path(parse_word(shortened, 8))
    require(final != 0, "one missing switch must break restoration")
    checked += 1
    without_two = LIFT.replace("7", "", 2)
    _, final = prefix_path(parse_word(without_two, 8))
    require(final == 0, "two missing switches should preserve restoration")
    require(len(interval_table(parse_word(without_two, 8))) < 256,
            "restoration alone must not imply universality")
    checked += 1
    require(len(interval_table(parse_word(PARENT, 8))) < 256,
            "projected universality must not imply lift universality")
    checked += 1
    require(128 in table and table[128][0] < table[128][1], "missing pure new coordinate")
    wrong = dict(table)
    wrong[128] = (0, 0)
    try:
        dirty_recovery(LIFT, wrong)
    except ValueError:
        pass
    else:
        raise ValueError("corrupt interval certificate was accepted")
    return checked + 1


def main() -> None:
    record, table = certify(LIFT)
    record["dirty_scalar_recoveries"] = dirty_recovery(LIFT, table)
    record["rejected_controls"] = controls(table)
    intervals = [[mask, *table[mask]] for mask in range(256)]
    record["interval_sha256"] = hashlib.sha256(json.dumps(intervals).encode()).hexdigest()
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = package / name
        require(path.is_file() and path.stat().st_size <= 1024 * 1024, "invalid package file")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {"schema": "fixed-projection-shortest-lift/1", "result": record,
               "optimality_dependency": "Nicholas Stone / PR5430, fixed-projection lower bound",
               "package_sha256": hashes}
    print(f"PASS_FIXED_PROJECTION_SHORTEST_LIFT length={record['length']} "
          f"differences={record['difference_masks']} "
          f"dirty_recoveries={record['dirty_scalar_recoveries']} "
          f"controls={record['rejected_controls']}")
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
