"""Exact finite corroboration of the new CRT placement theorem.

The all-size theorem is in PROOF.md. No predecessor executable is imported.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


MAX_AXES = 1 << 16


def need(condition, message):
    if not condition:
        raise ValueError(message)


def domain(d, ell, k):
    need(type(d) is int and 2 <= d <= MAX_AXES, "axis count range")
    need(d & (d - 1) == 0, "dyadic axis count")
    need(type(ell) is int and 2 <= ell <= MAX_AXES, "width range")
    need(type(k) is int and 0 <= k <= d, "long-axis count")


def extrema(d, ell, k):
    """Sharp active-row extrema; integer arithmetic and no logarithm rounding."""
    domain(d, ell, k)
    height = d.bit_length() - 1
    right_max = sum(min(k, d >> j) for j in range(1, height + 1))
    base = (2 * ell - 3) * (d - 1)
    return base + 2 * max(0, k - 1), base + 2 * right_max


def placements(d, k):
    domain(d, 2, k)
    height = d.bit_length() - 1
    high = []
    for i in range(k):
        value, reversed_bits = i, 0
        for _ in range(height):
            reversed_bits = 2 * reversed_bits + (value & 1)
            value >>= 1
        high.append(d - 1 - reversed_bits)
    need(len(set(high)) == k, "distinct extremizing leaves")
    return tuple(range(k)), tuple(high)


def tree_statistics(marks):
    """Build the occupied tree bottom up, without the scheduler predicate."""
    d = len(marks)
    domain(d, 2, 0)
    need(all(type(x) is bool for x in marks), "Boolean marks")
    occupied = tuple(marks)
    right, branch, right_only = 0, 0, 0
    for _ in range(d.bit_length() - 1):
        parents = []
        for a in range(0, len(occupied), 2):
            left, child = occupied[a], occupied[a + 1]
            right += child
            branch += left and child
            right_only += child and not left
            parents.append(left or child)
        occupied = tuple(parents)
    return right, branch, right_only


def literal_schedule(widths, ell, reverse=False):
    """Independent direct row/node loops implementing the declared interface."""
    d = len(widths)
    domain(d, ell, 0)
    need(all(type(w) is int and w in (ell - 1, ell) for w in widths),
         "declared widths")
    need(type(reverse) is bool, "direction flag")
    need((2 * ell - 1) * (d - 1) <= 1000, "literal command capacity")
    commands = []
    for level in range(1, d.bit_length()):
        size = 1 << level
        for row in range(2 * ell - 1):
            for start in range(0, d, size):
                active = False
                for i in range(start + size // 2, start + size):
                    if widths[i] == ell or row not in (ell - 1, ell):
                        active = True
                if active:
                    commands.append((level, start, row))
    return tuple(reversed(commands)) if reverse else tuple(commands)


def exhaustive_placements():
    placement_cases, schedule_cases, active_commands = 0, 0, 0
    for d in (2, 4, 8, 16):
        minima, maxima = [None] * (d + 1), [None] * (d + 1)
        for marks in product((False, True), repeat=d):
            k = sum(marks)
            right, branches, right_only = tree_statistics(marks)
            need(branches == max(0, k - 1), "occupied branch identity")
            need(right == branches + right_only, "right-only identity")
            minima[k] = right if minima[k] is None else min(minima[k], right)
            maxima[k] = right if maxima[k] is None else max(maxima[k], right)
            for ell in (2, 3, 5):
                widths = tuple(ell if x else ell - 1 for x in marks)
                actual = len(literal_schedule(widths, ell))
                expected = (2 * ell - 3) * (d - 1) + 2 * right
                need(actual == expected, "literal activity count")
                low, high = extrema(d, ell, k)
                need(low <= actual <= high, "extremal bound")
                active_commands += actual
                schedule_cases += 1
            placement_cases += 1
        for k in range(d + 1):
            low, high = extrema(d, 2, k)
            need(low == d - 1 + 2 * minima[k], "enumerated minimum")
            need(high == d - 1 + 2 * maxima[k], "enumerated maximum")
    return placement_cases, schedule_cases, active_commands


def constructive_cases():
    cases, level_cases = 0, 0
    for height in range(1, 11):
        d = 1 << height
        for k in range(d + 1):
            low, high = placements(d, k)
            for selected, expected in ((low, max(0, k - 1)),
                                       (high, sum(min(k, d >> j)
                                                  for j in range(1, height + 1)))):
                mark_set = set(selected)
                marks = tuple(i in mark_set for i in range(d))
                need(tree_statistics(marks)[0] == expected,
                     "explicit extremizer")
            for level in range(1, height + 1):
                # Count distinct blocks hit by a marked right-half leaf.
                hit = {x >> level for x in high if x & (1 << (level - 1))}
                need(len(hit) == min(k, d >> level), "simultaneous level maximum")
                level_cases += 1
            t = k.bit_length() - 1
            closed = 0 if k == 0 else (height - t - 1) * k + (1 << (t + 1)) - 1
            need(extrema(d, 2, k)[1] == d - 1 + 2 * closed,
                 "closed form")
            cases += 1
    return cases, level_cases


def boundary_and_controls():
    controls = 0
    invalid = ((True, 2, 0), (1, 2, 0), (3, 2, 0),
               (MAX_AXES + 1, 2, 0), (4, True, 1), (4, 1, 1),
               (4, MAX_AXES + 1, 1), (4, 2, True), (4, 2, -1), (4, 2, 5))
    for args in invalid:
        try:
            extrema(*args)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid domain accepted")
    for marks in ((0, 1), (False, False, False)):
        try:
            tree_statistics(marks)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid marks accepted")
    need(extrema(MAX_AXES, MAX_AXES, 0)[0] ==
         (2 * MAX_AXES - 3) * (MAX_AXES - 1), "maximum arithmetic domain")
    for d in (2, 4, 8, 16):
        widths = (2,) * d
        forward = literal_schedule(widths, 2)
        need(literal_schedule(widths, 2, True) == tuple(reversed(forward)),
             "reverse command order")
        need(len(forward) == 3 * (d - 1), "all-long boundary")
        need(len(literal_schedule((1,) * d, 2)) == d - 1,
             "all-short boundary")
    return controls


def main():
    placements_count, schedules, commands = exhaustive_placements()
    constructors, levels = constructive_cases()
    controls = boundary_and_controls()
    example = extrema(16, 3, 4)
    need(example == (51, 67), "displayed example")
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest()
              for name in files}
    receipt = {"status": "PASS_CRT_ACTIVE_ROW_EXTREMA",
               "placement_cases": placements_count, "literal_schedules": schedules,
               "literal_active_commands": commands, "constructive_cases": constructors,
               "constructive_level_cases": levels, "rejection_controls": controls,
               "example_active_extrema": example, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
