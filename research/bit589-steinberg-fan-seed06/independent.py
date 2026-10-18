#!/usr/bin/env python3
"""Independent integer-rank / coefficient-kernel / majorization census.

No imports from verify.py, wlib, the tuner, or the frame optimizer.
Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""

from bisect import bisect_left, bisect_right
from functools import lru_cache
import gzip
import hashlib
from itertools import permutations, product
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer_basis(rows, width):
    """Fraction-free elimination; primitive integer rows avoid coefficient growth."""
    pivots = {}
    for input_row in rows:
        row = list(input_row)
        need(len(row) == width, "matrix width")
        for column in sorted(pivots):
            if row[column]:
                basis = pivots[column]
                a, b = basis[column], row[column]
                row = [a * x - b * y for x, y in zip(row, basis)]
                divisor = 0
                for x in row:
                    divisor = gcd(divisor, abs(x))
                if divisor:
                    row = [x // divisor for x in row]
        first = next((i for i, x in enumerate(row) if x), None)
        if first is not None:
            divisor = 0
            for x in row:
                divisor = gcd(divisor, abs(x))
            if row[first] < 0:
                divisor = -divisor
            pivots[first] = [x // divisor for x in row]
    return tuple(tuple(pivots[i]) for i in sorted(pivots))


def intersection_dimension(spaces):
    """Equate independent coefficients in each basis: dim intersection = nullity."""
    if not spaces:
        return 8
    offsets = [0]
    for space in spaces:
        offsets.append(offsets[-1] + len(space))
    width = offsets[-1]
    equations = []
    for i in range(1, len(spaces)):
        for coordinate in range(8):
            row = [0] * width
            for j, vector in enumerate(spaces[0]):
                row[j] = vector[coordinate]
            for j, vector in enumerate(spaces[i]):
                row[offsets[i] + j] = -vector[coordinate]
            equations.append(row)
    return width - len(integer_basis(equations, width))


def direct_map(gates, registers, bits):
    values = {r: (bits >> i) & 1 for i, r in enumerate(registers)}
    for target, source in gates:
        values[target] ^= values[source]
    return tuple(values[r] for r in registers)


def main(certificate_path):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    row = next(row for row in pins["files"] if row["path"] == WORD)
    payload = (ROOT / WORD).read_bytes()
    need(hashlib.sha256(payload).hexdigest() == row["sha256"], "independent source pin")
    word = json.loads(gzip.decompress(payload))
    certificate = json.loads(gzip.decompress(certificate_path.read_bytes()))
    frames = [integer_basis((word["lines"][r] for r in frame), 8) for frame in word["frames"]]
    dimensions = list(map(len, frames))

    @lru_cache(None)
    def join_rank(ids):
        return len(integer_basis((r for i in ids for r in frames[i]), 8))

    @lru_cache(None)
    def meet_rank(ids):
        return intersection_dimension([frames[i] for i in ids])

    operations = [(f, d, s) for f, d, sources in word["A"] for s in sources]
    initial = list(word["start"])
    for f, d, sources in word["D"]:
        for r in [d, *sources]:
            initial[r] = f
    touches = [[] for _ in initial]
    for i, (frame, target, source) in enumerate(operations):
        for r in (target, source):
            touches[r].append((i, frame))
    endpoints = list(word["final"])
    for phase in ("C", "B"):
        for f, d, sources in reversed(word[phase]):
            for r in [d, *sources]:
                endpoints[r] = f
    for r in word["ret"]:
        endpoints[r] = touches[r][-1][1] if touches[r] else initial[r]

    def boundary(index, registers):
        entry, following = {}, {}
        for r in registers:
            places = [i for i, _ in touches[r]]
            left = bisect_left(places, index)
            right = bisect_right(places, index + 1)
            entry[r] = touches[r][left - 1][1] if left else initial[r]
            following[r] = touches[r][right][1] if right < len(places) else endpoints[r]
        return entry, following

    def lengths(gates, ranks, registers, entry, following):
        parts = []
        for r in registers:
            path = [dimensions[entry[r]]]
            path.extend(rank for gate, rank in zip(gates, ranks) if r in gate)
            path.append(dimensions[following[r]])
            increments = [b - a for a, b in zip(path, path[1:])]
            need(min(increments) >= 0, "independent negative rank increment")
            parts.extend(x for x in increments if x)
        return parts

    seen_indices = []
    schedules_checked = 0
    for index, (first, second) in enumerate(zip(operations, operations[1:])):
        old = [(first[1], first[2]), (second[1], second[2])]
        registers = sorted(set(old[0] + old[1]))
        if len(registers) != 3 or not (first[1] == second[2] or first[2] == second[1]):
            continue
        # Derive the corrective gate and every valid order by all eight Boolean inputs.
        variants = []
        for correction in permutations(registers, 2):
            if correction in old:
                continue
            for order in permutations([*old, correction]):
                if all(direct_map(order, registers, value) == direct_map(old, registers, value)
                       for value in range(8)):
                    variants.append(order)
        need(len(variants) == 3 and len(set(variants)) == 3, "independent corrective orders")
        entry, following = boundary(index, registers)
        # Independently check an actual common rational boundary frame. Dimensions
        # alone would not establish that two subspaces are nested.
        need(first[0] == second[0], "pinned adjacent frames differ")
        common = first[0]
        for r in registers:
            need(join_rank(tuple(sorted({entry[r], common}))) == dimensions[common]
                 and join_rank(tuple(sorted({common, following[r]}))) == dimensions[following[r]],
                 "independent boundary containment")
        old_parts = lengths(old, [dimensions[first[0]], dimensions[second[0]]], registers, entry, following)
        record = certificate["windows"][len(seen_indices)]
        seen_indices.append(index)
        need(record["index"] == index and record["original"] == [list(first), list(second)], "window identity")
        need(record["entry"] == [list(p) for p in sorted(entry.items())]
             and record["following"] == [list(p) for p in sorted(following.items())], "window boundaries")
        need(record["baseline_histogram"] == [old_parts.count(r) for r in range(1, 9)], "old histogram")
        need({tuple(map(tuple, v["gates"])) for v in record["variants"]} == set(variants), "variant coverage")
        need(len(record["variants"]) == 3, "duplicate variant")
        for order in variants:
            item = next(v for v in record["variants"] if tuple(map(tuple, v["gates"])) == order)
            bounds = [join_rank(tuple(sorted({entry[r] for r in order[0]}))),
                      join_rank(tuple(sorted({entry[r] for r in registers}))),
                      meet_rank(tuple(sorted({following[r] for r in registers}))),
                      meet_rank(tuple(sorted({following[r] for r in order[2]})))]
            need(bounds == item["flag_dimensions"], "independent flag dimension")
            legal = [ranks for ranks in product(range(9), repeat=3)
                     if bounds[0] <= ranks[0] <= ranks[1] <= ranks[2] <= bounds[3]
                     and bounds[1] <= ranks[1] <= bounds[2]]
            need([tuple(s[:3]) for s in item["schedules"]] == legal, "rank domain missing or duplicated")
            for ranks, schedule in zip(legal, item["schedules"]):
                parts = lengths(order, ranks, registers, entry, following)
                need(sum(parts) == sum(old_parts), "independent mass")
                width = max(len(old_parts), len(parts))
                a = sorted(old_parts + [0] * (width - len(old_parts)), reverse=True)
                b = sorted(parts + [0] * (width - len(parts)), reverse=True)
                need(all(sum(a[:k]) >= sum(b[:k]) for k in range(1, width + 1)), "majorization failed")
                expected_slacks = [sum(min(r, cut) for r in parts) - sum(min(r, cut) for r in old_parts)
                                   for cut in range(1, 9)]
                need(schedule[3] == [parts.count(r) for r in range(1, 9)]
                     and schedule[4] == expected_slacks, "schedule histogram or slack mismatch")
                schedules_checked += 1
    need(len(seen_indices) == len(certificate["windows"]) == 316, "independent window coverage")
    need(schedules_checked == certificate["summary"]["rational_rank_schedules"] == 1671, "independent rank coverage")
    print("PASS_INDEPENDENT_INTEGER_KERNEL_MAJORIZATION pairs=316 orders=948 rank_schedules=1671")


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "CERTIFICATE.json.gz")
    except (ValueError, OSError, KeyError, IndexError) as error:
        raise SystemExit("FAIL_INDEPENDENT_STEINBERG_FAN: " + str(error)) from error
