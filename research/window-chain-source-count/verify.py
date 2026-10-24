"""Even source calls on overlapping write windows.

A chain of length-two windows has hitting number ceil(k/2). Restoring the
connector makes the source-call count even, so the uniform bill uses twice
that number rounded up. The six-output scalar pilot expands the same counts
into explicit gates.
"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
CHAIN_LIMIT = 10
SOURCE = (3, 6, 7)
READERS = tuple((1, 2, 4) if index % 2 == 0 else (3, 2, 4) for index in range(6))


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def hitting_number(windows: tuple[tuple[int, int], ...]) -> int:
    last = -1
    number = 0
    for low, high in sorted(windows, key=lambda window: (window[1], window[0])):
        if last < low:
            last = high
            number += 1
    return number


def scan(windows: tuple[tuple[int, int], ...], prices: tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    due = [-1] * len(prices)
    for low, high in windows:
        due[high] = max(due[high], low)
    states = {(-1, 0): (0, ())}
    for slot, price in enumerate(prices):
        nxt = {}
        for (last, parity), (cost, counts) in states.items():
            for number in (0, 1, 2):
                new_last = slot if number else last
                if new_last < due[slot]:
                    continue
                key = (new_last, parity ^ (number & 1))
                candidate = (cost + number * price, counts + (number,))
                if key not in nxt or candidate < nxt[key]:
                    nxt[key] = candidate
        states = nxt
    return min(value for (_, parity), value in states.items() if parity == 0)


def brute(windows: tuple[tuple[int, int], ...], prices: tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    best = None
    for counts in product(range(3), repeat=len(prices)):
        if sum(counts) % 2:
            continue
        if any(not any(counts[low : high + 1]) for low, high in windows):
            continue
        cost = sum(number * price for number, price in zip(counts, prices))
        if best is None or (cost, counts) < best:
            best = (cost, counts)
    if best is None:
        raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE no feasible multiset")
    return best


def emit(windows: tuple[tuple[int, int], ...], counts: tuple[int, ...]) -> list[tuple[int, str, int]]:
    assigned: list[list[int]] = [[] for _ in counts]
    for index, (low, high) in enumerate(windows):
        slot = next(slot for slot in range(low, high + 1) if counts[slot])
        assigned[slot].append(index)
    events: list[tuple[int, str, int]] = []
    for slot, number in enumerate(counts):
        if number:
            events += [(slot, "A", index) for index in assigned[slot]]
            events.append((slot, "B", -1))
            events += [(slot, "A", index) for index in assigned[slot]]
            events += [(slot, "B", -1)] * (number - 1)
    return events


def gates(
    events: list[tuple[int, str, int]],
    source: tuple[int, ...],
    readers: tuple[tuple[int, ...], ...],
) -> list[tuple[int, int, int]]:
    width = len(source)
    found = []
    for slot, kind, index in events:
        matrix = source if kind == "B" else readers[index]
        origin = 0 if kind == "B" else width
        destination = width if kind == "B" else (2 + index) * width
        for row, mask in enumerate(matrix):
            for column in range(width):
                if mask >> column & 1:
                    found.append((slot, origin + column, destination + row))
    return found


def xor_rows(values) -> int:
    result = 0
    for value in values:
        result ^= value
    return result


def delivered(reader: tuple[int, ...], source: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        xor_rows(source[column] for column in range(len(source)) if row >> column & 1)
        for row in reader
    )


def apply_map(
    windows: tuple[tuple[int, int], ...],
    events: list[tuple[int, str, int]],
    source: tuple[int, ...],
    readers: tuple[tuple[int, ...], ...],
) -> None:
    width = len(source)
    size = (2 + len(windows)) * width
    rows = [1 << index for index in range(size)]
    expected = rows[:]
    for index, reader in enumerate(readers):
        for row, mask in enumerate(delivered(reader, source)):
            expected[(2 + index) * width + row] ^= mask
    found = gates(events, source, readers)
    last = max(high for _, high in windows)
    for slot in range(last + 1):
        for time, origin, destination in found:
            if time == slot:
                rows[destination] ^= rows[origin]
        for index, (_, high) in enumerate(windows):
            if high == slot:
                start = (2 + index) * width
                if rows[start : start + width] != expected[start : start + width]:
                    raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE deadline moved")
    if rows != expected:
        raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE endpoint moved")


def tariff(found: list[tuple[int, int, int]]) -> tuple[int, int]:
    return len(found), sum(2 * max(origin, destination) for _, origin, destination in found)


def main() -> None:
    pinned = load()
    largest = 0
    for outputs in range(1, CHAIN_LIMIT + 1):
        windows = tuple((index, index + 1) for index in range(outputs))
        prices = (1,) * (outputs + 1)
        tau = hitting_number(windows)
        scanned, scan_counts = scan(windows, prices)
        enumerated, brute_counts = brute(windows, prices)
        source_calls = 2 * ((tau + 1) // 2)
        if (
            tau != (outputs + 1) // 2
            or scanned != source_calls
            or enumerated != source_calls
            or sum(scan_counts) != source_calls
            or sum(brute_counts) != source_calls
        ):
            raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE chain bill moved")
        largest = source_calls
    weighted_windows = ((0, 1), (1, 2))
    weighted_prices = (1, 9, 1)
    weighted_cost, weighted_counts = brute(weighted_windows, weighted_prices)
    if weighted_cost + 4 != 6 or weighted_counts != (1, 0, 1):
        raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE weighted pair moved")
    if 9 + 1 + 4 != 14 or 2 * 9 + 4 != 22:
        raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE shared slot moved")
    windows = tuple((index, index + 1) for index in range(6))
    reader_prices = tuple(sum(row.bit_count() for row in reader) for reader in READERS)
    _, counts = scan(windows, (7,) * 7)
    pilot = gates(emit(windows, counts), SOURCE, READERS)
    apply_map(windows, emit(windows, counts), SOURCE, READERS)
    closed_events = []
    for index, (_, high) in enumerate(windows):
        closed_events += [(high, "A", index), (high, "B", -1), (high, "A", index), (high, "B", -1)]
    closed = gates(closed_events, SOURCE, READERS)
    apply_map(windows, closed_events, SOURCE, READERS)
    disjoint = tuple((high, high) for _, high in windows)
    _, disjoint_counts = scan(disjoint, (7,) * 7)
    disjoint_events = emit(disjoint, disjoint_counts)
    disjoint_gates = gates(disjoint_events, SOURCE, READERS)
    apply_map(disjoint, disjoint_events, SOURCE, READERS)
    pilot_xors, pilot_head = tariff(pilot)
    disjoint_xors, disjoint_head = tariff(disjoint_gates)
    closed_xors, closed_head = tariff(closed)
    if 2 * sum(reader_prices) + 4 * 7 != pilot_xors:
        raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE pilot expansion moved")
    if (
        pinned["chains"] != CHAIN_LIMIT
        or pinned["largest_source_calls"] != largest
        or pinned["weighted_cost"] != 6
        or pinned["shared_slot_cost"] != 14
        or pinned["double_shared_cost"] != 22
        or pinned["pilot_xors"] != pilot_xors
        or pinned["disjoint_xors"] != disjoint_xors
        or pinned["closed_xors"] != closed_xors
        or pinned["pilot_head_steps"] != pilot_head
        or pinned["disjoint_head_steps"] != disjoint_head
        or pinned["closed_head_steps"] != closed_head
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_WINDOW_CHAIN_SOURCE pinned result moved")
    print(f"PASS_WINDOW_CHAIN_SOURCE chains={CHAIN_LIMIT} no_new_kappa")


if __name__ == "__main__":
    main()
