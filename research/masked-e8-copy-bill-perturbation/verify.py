#!/usr/bin/env python3
"""Exact scalar/support certificates for one fixed 93-line E8 puncture.

Standard library only. No network, imports from other packages, or file writes.
The JSON receipt binds the result to the five package files.
"""

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

DIM = 8
PORTS = 120
TARGET = (2, 2, 0, 0, 0, 0, 0, 0)
NORMAL = (1, -1, 2, 0, 0, 0, 0, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    need(len(left) == len(right) == DIM, "wrong vector dimension")
    return sum(a * b for a, b in zip(left, right))


def roots():
    """One sign representative of each root line, in lexicographic order."""
    vectors = []
    for i, j in itertools.combinations(range(DIM), 2):
        for sign in (1, -1):
            row = [0] * DIM
            row[i], row[j] = 2, 2 * sign
            vectors.append(tuple(row))
    for tail in itertools.product((1, -1), repeat=7):
        row = (1,) + tail
        if row.count(-1) % 2 == 0:
            vectors.append(row)
    lines = tuple(sorted(vectors))
    need(len(lines) == len(set(lines)) == PORTS, "wrong root-line inventory")
    need(all(dot(q, q) == 8 for q in lines), "wrong doubled-root norm")
    return lines


def binary_rank(rows, width=PORTS):
    """Bounded bit Gaussian elimination; no arithmetic rank heuristic."""
    need(0 <= width <= PORTS and len(rows) <= PORTS, "rank capacity exceeded")
    need(all(0 <= r < (1 << width) for r in rows), "invalid binary row")
    pivots = [0] * width
    result = 0
    for row in rows:
        for bit in range(width - 1, -1, -1):
            if row & (1 << bit):
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    result += 1
                    break
    return result


def column_rank(rows, width=PORTS):
    """Independent transpose-and-XOR span computation."""
    need(len(rows) <= PORTS and 0 <= width <= PORTS, "rank capacity exceeded")
    basis = []
    for col in range(width):
        vector = sum(((r >> col) & 1) << i for i, r in enumerate(rows))
        for previous in basis:
            vector = min(vector, vector ^ previous)
        if vector:
            basis.append(vector)
    return len(basis)


def pairing(lines):
    rows = []
    for left in lines:
        products = [dot(left, right) for right in lines]
        need(all(p % 4 == 0 for p in products), "nonintegral root product")
        rows.append(sum(int((p // 4) % 2 == 0) << j for j, p in enumerate(products)))
    need(binary_rank(rows) == column_rank(rows) == 9, "wrong full pairing rank")
    return rows


def restricted_rank(mask_rows, sources, targets):
    mask = sum(1 << j for j in targets)
    rows = [mask_rows[i] & mask for i in sources]
    result = binary_rank(rows)
    need(result == column_rank(rows), "the binary rank implementations disagree")
    return result


def puncture(lines):
    target = lines.index(TARGET)
    orthogonal = [i for i, q in enumerate(lines) if dot(q, TARGET) == 0]
    deleted = [i for i in orthogonal if dot(lines[i], NORMAL) != 0]
    live = [i for i in range(PORTS) if i not in deleted]
    need(len(orthogonal) == 63 and len(deleted) == 27 and len(live) == 93,
         "wrong fixed puncture")
    neighbourhood = [i for i in live if i == target or dot(lines[i], TARGET) == 0]
    need(all(dot(lines[i], NORMAL) == 0 for i in neighbourhood), "normal violates mask")
    need(sum(dot(lines[i], NORMAL) != 0 for i in live) == 56,
         "wrong nonzero error-column support")
    return target, deleted, live


def coordinate_factors(lines, live, target, scalar, normal=NORMAL):
    left = [[Fraction(x, 2) for x in lines[i]] for i in live]
    right = [[Fraction(x) for x in lines[i]] for i in live]
    position = live.index(target)
    right[position] = [x + scalar * y for x, y in zip(right[position], normal)]
    return left, right


def error_counts(lines, live, left, right):
    masked = 0
    unmasked = 0
    columns = set()
    for a, i in enumerate(live):
        for b, j in enumerate(live):
            actual = sum(x * y for x, y in zip(left[a], right[b]))
            expected = Fraction(dot(lines[i], lines[j]), 2)
            if actual != expected:
                if i == j or dot(lines[i], lines[j]) == 0:
                    masked += 1
                else:
                    unmasked += 1
                columns.add(j)
    return masked, unmasked, sorted(columns)


def coordinate_certificate(lines, mask_rows, live, target):
    exceptional = sorted({Fraction(-a, b) for a, b in zip(TARGET, NORMAL) if b})
    need(exceptional == [Fraction(-2), Fraction(0), Fraction(2)], "wrong support breakpoints")
    results = []
    patterns = set()
    for scalar in (Fraction(-2), Fraction(0), Fraction(2), Fraction(1)):
        left, right = coordinate_factors(lines, live, target, scalar)
        pattern = tuple(k for k, value in enumerate(right[live.index(target)]) if value)
        patterns.add(pattern)
        ranks = []
        for k in range(DIM):
            sources = [i for a, i in enumerate(live) if left[a][k]]
            targets = [i for a, i in enumerate(live) if right[a][k]]
            ranks.append(restricted_rank(mask_rows, sources, targets))
        need(ranks == [9] * DIM, "coordinate perturbation changed the COPY bill")
        errors = error_counts(lines, live, left, right)
        expected_errors = (0, 0, []) if scalar == 0 else (0, 56, [target])
        need(errors == expected_errors, "coordinate identity/error support failed")
        results.append({"scalar": str(scalar), "target_support": list(pattern),
                        "ranks": ranks, "masked_errors": errors[0],
                        "unmasked_errors": errors[1]})
    need(len(patterns) == 4, "not every scalar support class was checked")
    return results


def root_direction_certificate(lines, mask_rows, live, target):
    histogram = Counter()
    critical = []
    entries = []
    for direction in lines:
        targets = [i for i in live if dot(lines[i], direction) != 0]
        without = [i for i in targets if i != target]
        full_rank = restricted_rank(mask_rows, range(PORTS), targets)
        removed_rank = restricted_rank(mask_rows, range(PORTS), without)
        need(0 <= full_rank - removed_rank <= 1, "one-column rank bound failed")
        histogram[(full_rank, removed_rank)] += 1
        entry = {"direction": list(direction), "support_size": len(targets),
                 "rank": full_rank, "rank_without_target": removed_rank}
        entries.append(entry)
        if full_rank != removed_rank:
            slope = dot(NORMAL, direction)
            cancellation = str(Fraction(-dot(TARGET, direction), slope)) if slope else None
            critical.append({**entry, "cancellation_scalar": cancellation})
    expected = {TARGET: None, (2, 0, 2, 0, 0, 0, 0, 0): "-2/3",
                (0, 2, -2, 0, 0, 0, 0, 0): "2/3"}
    actual = {tuple(row["direction"]): row["cancellation_scalar"] for row in critical}
    need(actual == expected, "wrong critical root-direction classification")
    need(histogram == {(8, 8): 27, (9, 8): 3, (9, 9): 90}, "wrong root-direction spectrum")
    return {"spectrum": [{"ranks": list(k), "count": v} for k, v in sorted(histogram.items())],
            "critical": critical, "directions": entries}


def controls(lines, mask_rows, live, target):
    """Small exhaustive rank controls and wrong-perturbation rejection."""
    for encoded in range(1 << 9):
        rows = [(encoded >> (3 * i)) & 7 for i in range(3)]
        need(binary_rank(rows, 3) == column_rank(rows, 3), "3x3 rank control failed")
        for removed in range(3):
            shorter = [r & ~(1 << removed) for r in rows]
            need(binary_rank(shorter, 3) == column_rank(shorter, 3),
                 "3x3 deletion rank implementations disagree")
            need(0 <= binary_rank(rows, 3) - binary_rank(shorter, 3) <= 1,
                 "3x3 column-deletion control failed")
    for rows, width in (([8], 3), ([0] * 121, 1), ([-1], 1)):
        try:
            binary_rank(rows, width)
        except ValueError:
            pass
        else:
            raise ValueError("invalid binary matrix accepted")
    left, right = coordinate_factors(lines, live, target, Fraction(1), TARGET)
    need(error_counts(lines, live, left, right)[0] > 0, "diagonal mutation was not rejected")
    # Rank loss on all rows is not enough to promise loss after restriction.
    exceptional = lines.index((2, 0, 2, 0, 0, 0, 0, 0))
    targets = [i for i in live if dot(lines[i], lines[exceptional])]
    need(restricted_rank(mask_rows, [], targets) ==
         restricted_rank(mask_rows, [], [i for i in targets if i != target]) == 0,
         "empty-row no-saving control failed")
    return {"binary_matrices": 512, "column_deletions": 1536,
            "invalid_inputs_rejected": 3, "wrong_normal_rejected": True,
            "restriction_need_not_save": True}


def main():
    lines = roots()
    mask_rows = pairing(lines)
    target, deleted, live = puncture(lines)
    coordinate = coordinate_certificate(lines, mask_rows, live, target)
    directions = root_direction_certificate(lines, mask_rows, live, target)
    checks = controls(lines, mask_rows, live, target)
    package = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {"claim_type": "scoped proof supported by finite certificates",
               "package_sha256": hashes, "target": list(TARGET), "normal": list(NORMAL),
               "deleted_lines": [list(lines[i]) for i in deleted], "live_lines": len(live),
               "coordinate": coordinate, "root_directions": directions, "controls": checks}
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("PASS_MASKED_E8_COPY_BILL_PERTURBATION coordinate=72 support_classes=4 "
          "root_directions=120 critical=3 possible_saving_scalars=-2/3,2/3 max_root_basis_saving=1")


if __name__ == "__main__":
    main()
