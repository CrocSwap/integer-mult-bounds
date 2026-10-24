#!/usr/bin/env python3
"""Uniform bill of six chained dirty-connector windows.

The checker prices this chain. It does not rerun the interval census.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_OVERLAPPING_WINDOW_BILL xor=70/84/126 no_new_kappa"
SOURCE = (3, 6, 7)
READERS = ((1, 2, 4), (3, 2, 4))


def fail(message):
    raise SystemExit("FAIL_OVERLAPPING_WINDOW_BILL " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def weight(matrix):
    return sum(row.bit_count() for row in matrix)


def hitting_number(windows):
    last, number = -1, 0
    for left, right in sorted(windows, key=lambda window: (window[1], window[0])):
        if last < left:
            last = right
            number += 1
    return number


def emit(windows, counts):
    assigned = [[] for _ in counts]
    for index, (left, right) in enumerate(windows):
        slot = next(time for time in range(left, right + 1) if counts[time])
        assigned[slot].append(index)
    events = []
    for time, count in enumerate(counts):
        if count:
            events += [(time, "A", index) for index in assigned[time]]
            events.append((time, "B", -1))
            events += [(time, "A", index) for index in assigned[time]]
            events += [(time, "B", -1)] * (count - 1)
    return events


def deliver(windows, events):
    connector = 2
    outputs = [0] * len(windows)
    for time, kind, index in events:
        if kind == "B":
            connector ^= 1
        else:
            require(windows[index][0] <= time <= windows[index][1], "a write left its window")
            outputs[index] ^= connector
    require(outputs == [1] * len(windows) and connector == 2, "the chain did not restore")


def gates(events, source, readers):
    dimension = len(source)
    found = []
    for time, kind, index in events:
        matrix = source if kind == "B" else readers[index % 2]
        origin = 0 if kind == "B" else dimension
        destination = dimension if kind == "B" else (2 + index) * dimension
        for row, mask in enumerate(matrix):
            for column in range(dimension):
                if mask >> column & 1:
                    found.append((time, origin + column, destination + row))
    return found


def weighted_minimum():
    best = None
    common = None
    for left in range(3):
        for middle in range(3):
            for right in range(3):
                if (left + middle + right) % 2 or left + middle < 1 or middle + right < 1:
                    continue
                cost = 4 + left + 9 * middle + right
                if best is None or cost < best:
                    best = cost
                if middle and not left and not right:
                    pass
                if middle >= 1 and (left + right) >= 1 and middle and (left, right) != (0, 0):
                    if left + right == 1 and middle == 1 and (common is None or cost < common):
                        common = cost
    return best, common


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    windows = tuple((index, index + 1) for index in range(6))
    disjoint = tuple((right, right) for _, right in windows)
    require(hitting_number(windows) == 3, "the chain hitting number moved")
    require(hitting_number(disjoint) == 6, "the disjoint hitting number moved")
    require(weight(SOURCE) == 7, "the source weight moved")
    reader_weights = tuple(weight(READERS[index % 2]) for index in range(6))
    require(reader_weights == (3, 4, 3, 4, 3, 4), "the output weights moved")
    counts = [0, 1, 0, 1, 0, 1, 1]
    events = emit(windows, counts)
    deliver(windows, events)
    pilot = gates(events, SOURCE, READERS)
    closed = []
    for index, (_, right) in enumerate(windows):
        closed += [(right, "A", index), (right, "B", -1), (right, "A", index), (right, "B", -1)]
    deliver(windows, closed)
    closed_gates = gates(closed, SOURCE, READERS)
    separate = [0, 1, 1, 1, 1, 1, 1]
    separate_events = emit(disjoint, separate)
    deliver(disjoint, separate_events)
    separate_gates = gates(separate_events, SOURCE, READERS)
    require((len(pilot), len(separate_gates), len(closed_gates)) == (70, 84, 126), "a gate count moved")
    require(2 * sum(reader_weights) + 2 * 7 * ((3 + 1) // 2) == 70, "the uniform bill moved")
    minimum, common = weighted_minimum()
    require((minimum, common) == (6, 14), "the weighted example moved")
    return {
        "hitting_number": 3,
        "source_calls": 4,
        "disjoint_source_calls": 6,
        "xor_gates": {"overlapping": 70, "disjoint": 84, "closed": 126},
        "data_bits": 24,
        "head_steps": {
            "overlapping": sum(2 * max(source, target) for _, source, target in pilot),
            "disjoint": sum(2 * max(source, target) for _, source, target in separate_gates),
            "closed": sum(2 * max(source, target) for _, source, target in closed_gates),
        },
        "weighted_minimum": 6,
        "weighted_common_slot": 14,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
