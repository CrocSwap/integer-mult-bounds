#!/usr/bin/env python3
"""Independent exact check of the canonical typed-window fusion tariff."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COST = (0, 20, 16, 20)
WIDTH = 56
MAX_CHILDREN = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_blocks(blocks):
    require(1 <= len(blocks) <= MAX_CHILDREN, "child count outside 1..64")
    require(all(type(b) is int and 0 <= b < 3 for b in blocks), "invalid octet")
    return tuple(blocks)


def occurrences(blocks, octet):
    return [i for i, value in enumerate(blocks) if value == octet]


def gap_formula(blocks, literal=False):
    blocks = checked_blocks(blocks)
    total = 0
    for octet in range(3):
        positions = occurrences(blocks, octet)
        if positions:
            total += sum(COST[(a - b) % 4] for a, b in itertools.pairwise(positions))
            if literal:
                total += COST[-positions[0] % 4] + COST[(positions[-1] - len(blocks)) % 4]
    return total


def gap_dp(blocks, literal=False):
    """Four physical phases; independently minimize every permitted gap."""
    blocks = checked_blocks(blocks)
    total, infinity = 0, 1000000
    for octet in sorted(set(blocks)):
        candidates = []
        for required_phase in (0,) if literal else range(4):
            costs = [0, infinity, infinity, infinity]
            for position, block in enumerate(blocks):
                if block == octet:
                    costs = [v if p == required_phase else infinity for p, v in enumerate(costs)]
                advanced = [costs[(p - 1) % 4] for p in range(4)]
                if position + 1 == len(blocks):
                    costs = advanced
                else:
                    costs = [
                        min(advanced[q] + COST[(p - q) % 4] for q in range(4)) for p in range(4)
                    ]
            candidates.append(
                min(v + (COST[-p % 4] if literal else 0) for p, v in enumerate(costs))
            )
        total += min(candidates)
    return total


def fusion_saving(left, right):
    left, right = checked_blocks(left), checked_blocks(right)
    shared = set(left) & set(right)
    bridge = sum(
        COST[-(len(left) + right.index(b) - max(occurrences(left, b))) % 4] for b in shared
    )
    return 16 * len(shared) - 2 * bridge


def inverse(word):
    return [
        (kind, target, source, -sign if kind == "ADD" else 0)
        for kind, target, source, sign in reversed(word)
    ]


def cycle(phase, base):
    """PR1391's canonical words, transcribed without importing its emitter."""
    a, b, c, d = range(base, base + 4)
    one = [
        ("ADD", a, b, 1),
        ("ADD", b, a, -1),
        ("ADD", a, b, 1),
        ("ADD", c, a, 1),
        ("ADD", a, c, -1),
        ("ADD", c, a, 1),
        ("ADD", a, d, 1),
        ("ADD", d, a, -1),
        ("ADD", a, d, 1),
        ("NEG", b, None, 0),
    ]
    if phase == 0:
        return []
    if phase == 1:
        return one
    if phase == 3:
        return inverse(one)
    require(phase == 2, "invalid phase")
    return [
        (kind, target, source, sign)
        for x, y in ((a, c), (b, d))
        for kind, target, source, sign in (
            ("ADD", x, y, 1),
            ("ADD", y, x, -1),
            ("ADD", x, y, 1),
            ("NEG", y, None, 0),
        )
    ]


def octet_power(octet, phase):
    base = 32 + 8 * octet
    return cycle(phase, base) + cycle(phase, base + 4)


def rotated_row(row, phase):
    return 4 * (row // 4) + (row % 4 - phase) % 4


def schedule(blocks, literal=False, phase_indexed=False):
    blocks = checked_blocks(blocks)
    require(not (literal and phase_indexed), "literal phase-indexed mode is not supported")
    gaps = [dict() for _ in range(len(blocks))]
    sigma = {}
    for octet in sorted(set(blocks)):
        positions = occurrences(blocks, octet)
        sigma[octet] = 0 if literal or phase_indexed else -positions[0] % 4
        if not phase_indexed:
            for a, b in itertools.pairwise(positions):
                gaps[b - 1][octet] = (a - b) % 4
            if literal:
                if positions[0]:
                    gaps[positions[0] - 1][octet] = -positions[0] % 4
                gaps[-1][octet] = (positions[-1] - len(blocks)) % 4
    body, phases = [], [0, 0, 0]
    for i, octet in enumerate(blocks):
        for row in range(8):
            target = rotated_row(row, phases[octet]) if phase_indexed else row
            body.append(("ADD", target, 32 + 8 * octet + row, 1))
        for b in range(3):
            body.extend(octet_power(b, 1))
            phases[b] = (phases[b] + 1) % 4
        for b, power in sorted(gaps[i].items()):
            body.extend(octet_power(b, power))
            phases[b] = (phases[b] + power) % 4
    copy, erase = [], []
    for b, initial in sorted(sigma.items()):
        for row in range(8):
            copy.append(("ADD", 32 + 8 * b + row, 8 + 8 * b + rotated_row(row, initial), 1))
            erase.append(
                ("ADD", 32 + 8 * b + row, 8 + 8 * b + rotated_row(row, initial + phases[b]), -1)
            )
    return copy + body + erase + inverse(body)


def replay(word):
    require(len(word) <= 40000, "record capacity exceeded")
    # Column-by-column execution differs from the source's row interpreter.
    columns = []
    for column in range(WIDTH):
        values = [int(i == column) for i in range(WIDTH)]
        for kind, target, source, sign in word:
            require(type(target) is int and 0 <= target < WIDTH, "invalid target")
            if kind == "ADD":
                require(
                    type(source) is int and 0 <= source < WIDTH and source != target,
                    "invalid source",
                )
                require(sign in (-1, 1), "invalid sign")
                values[target] += sign * values[source]
            else:
                require(kind == "NEG" and source is None and sign == 0, "invalid opcode")
                values[target] = -values[target]
        columns.append(values)
    return columns


def check_map(word, blocks):
    columns = replay(word)
    for column, actual in enumerate(columns):
        expected = [int(i == column) for i in range(WIDTH)]
        for block in blocks:
            if 8 + 8 * block <= column < 16 + 8 * block:
                expected[column - 8 - 8 * block] += 1
        require(actual == expected, "dirty map mismatch at column " + str(column))
    return columns


def invoice(word, calls):
    adds = sum(g[0] == "ADD" for g in word)
    count = len(word)
    return {
        "primitives": count,
        "ADD": adds,
        "NEG": count - adds,
        "reads": count + adds,
        "writes": count,
        "dispatches": count,
        "instruction_fetches": count,
        "coefficient_fetches": count,
        "address_travel_row_steps": sum(
            2 * max(t, s if s is not None else t) for _, t, s, _ in word
        ),
        "descriptor_bits": 16 * count + 128 * calls,
        "data_storage_cells": 4088,
    }


def read_source():
    pins = json.loads((HERE / "EXTERNAL-SOURCE.json").read_text())
    raw = (HERE / "PR2595-RESULT.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pins["sha256"], "external receipt pin")
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if item["usage"] == "input":
            payload = (ROOT / item["path"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == item["sha256"], "source pin")
    return json.loads(raw)


def verify_formulas():
    require(
        all(COST[(u + v) % 4] <= COST[u] + COST[v] for u in range(4) for v in range(4)),
        "phase tariff subadditivity",
    )
    count = 0
    for length in range(1, 8):
        for blocks in itertools.product(range(3), repeat=length):
            for literal in (False, True):
                require(gap_formula(blocks, literal) == gap_dp(blocks, literal), "DP disagreement")
            count += 1
    short = [w for k in range(1, 5) for w in itertools.product(range(3), repeat=k)]
    for left in short:
        for right in short:
            direct = 16 * len(set(left) & set(right)) + 2 * (
                gap_formula(left) + gap_formula(right) - gap_formula(left + right)
            )
            require(fusion_saving(left, right) == direct, "fusion formula disagreement")
    return count, len(short) ** 2


def verify_programs(source):
    pivot = (0, 1, 2, 0, 1)
    cases = [
        ((0,), (1,), False, False, "legal_typed_pair"),
        ((0,), (1,), True, False, "legal_min_literal_pair"),
        (pivot, pivot, False, False, "pivot_separate5_typed_fixed"),
        (pivot, pivot, True, False, "pivot_separate5_min_literal"),
        (pivot, pivot, False, True, "pivot_separate5_typed_phase"),
    ]
    receipts = {}
    for left, right, literal, indexed, name in cases:
        first, second = schedule(left, literal, indexed), schedule(right, literal, indexed)
        check_map(first, left)
        check_map(second, right)
        complete = first + second
        check_map(complete, left + right)
        check_map(complete + inverse(complete), ())
        receipts[name] = invoice(complete, 2)
    for indexed, name in (
        (False, "pivot_joint10_typed_fixed"),
        (True, "pivot_joint10_typed_phase"),
    ):
        word = schedule(pivot + pivot, phase_indexed=indexed)
        check_map(word, pivot + pivot)
        check_map(word + inverse(word), ())
        receipts[name] = invoice(word, 1)
    for indexed, expected in ((False, 328), (True, 288)):
        minimal = schedule((0, 0), phase_indexed=indexed)
        check_map(minimal, (0, 0))
        require(len(minimal) == expected, "smallest shared-octet fixture")
    for name, receipt in receipts.items():
        section = "pivot_k5k10" if name.startswith("pivot_") else "k2_pair"
        require(receipt == source[section]["price"][name], "source invoice mismatch " + name)
    return receipts


def build_result():
    source = read_source()
    words, pairs = verify_formulas()
    receipts = verify_programs(source)
    pivot = (0, 1, 2, 0, 1)
    require(fusion_saving(pivot, pivot) == -56, "fixed-reader residual")
    require(gap_dp((0,) * MAX_CHILDREN) == gap_formula((0,) * MAX_CHILDREN), "capacity control")
    return {
        "words_checked": words,
        "ordered_pairs_checked": pairs,
        "fixed_reader_saving": -56,
        "phase_indexed_saving": 48,
        "smallest_shared_octet_fixed_saving": fusion_saving((0,), (0,)),
        "gap_cost_single": gap_formula(pivot),
        "gap_cost_fused": gap_formula(pivot + pivot),
        "receipts": receipts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit", action="store_true", help="print a new receipt without writing files"
    )
    args = parser.parse_args()
    result = build_result()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "stored receipt mismatch")
        print("PASS_TYPED_WINDOW_FUSION words=3279 pairs=14400 fixed=-56 phase_indexed=48")


if __name__ == "__main__":
    main()
