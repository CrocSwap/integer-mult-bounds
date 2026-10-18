#!/usr/bin/env python3
"""Check the witnesses by column replay and integer determinants."""

from fractions import Fraction
from functools import reduce
import gzip
from itertools import combinations, permutations
import json
from operator import xor
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def span(vectors):
    return {reduce(xor, group, 0) for size in range(len(vectors) + 1)
            for group in combinations(vectors, size)}


def determinant(matrix):
    size = len(matrix)
    total = 0
    for order in permutations(range(size)):
        sign = (-1) ** sum(order[i] > order[j] for i in range(size) for j in range(i + 1, size))
        value = sign
        for i, j in enumerate(order):
            value *= matrix[i][j]
        total += value
    return total


def minor_rank(matrix):
    for size in range(min(len(matrix), len(matrix[0])), 0, -1):
        for rows in combinations(range(len(matrix)), size):
            for columns in combinations(range(len(matrix[0])), size):
                if determinant([[matrix[i][j] for j in columns] for i in rows]):
                    return size
    return 0


def main():
    certificate = json.loads((ROOT / "CERTIFICATE.json").read_text())
    word = json.loads(gzip.decompress((ROOT / "inputs/SEVEN-SLOT-WORD.json.gz").read_bytes()))
    witnesses = certificate["factory"]["witnesses"]
    check(len(witnesses) == 192, "demand count")
    visits = {}
    for witness in witnesses:
        visits.setdefault((witness["phase"], witness["event"]), []).append(witness)
    stream = [(phase, index, event) for phase in ("A", "B") for index, event in enumerate(word[phase])]
    for column in range(112):
        values = [Fraction(0)] * 704
        values[column] = Fraction(1)
        for phase, index, event in stream:
            if event[0] == "add":
                target, source, numerator, denominator = event[1:5]
                values[target] += values[source] * Fraction(numerator, denominator)
            else:
                target, numerator, denominator = event[1:4]
                values[target] *= Fraction(numerator, denominator)
            for witness in visits.get((phase, index), []):
                expected = dict(witness["clean_row"]).get(column, "0")
                check(values[witness["register"]] == Fraction(expected), "column witness")
                check(span(witness["frame"]) == span(event[-1]), "event frame")
    frames = set()
    for witness in witnesses:
        labels = [word["ports"][i] for i, coefficient in witness["clean_row"] if Fraction(coefficient)]
        frame = frozenset(span(witness["frame"]))
        check(span(labels) == frame, "support hull")
        frames.add(frame)
    check(len(frames) == 168, "frame count")
    check(sum(len(frame) == 4 for frame in frames) == 24, "rank two count")
    check(sum(len(frame) == 8 for frame in frames) == 144, "rank three count")
    for first, second in combinations(frames, 2):
        check(not first <= second and not second <= first, "antichain")
    check(2 * len(frames) - 112 == certificate["factory"]["helper_lower_bound"] == 224,
          "register bound")
    cap_pairs = 0
    for key in ("whole_block_target_exclusion", "center_target_exclusion"):
        if key == "whole_block_target_exclusion":
            expected_frames = {frozenset(span(frame)) for register, frame in word["helper_final"].items()
                               if len(frame) == 4 and register not in word["start_extra"]}
        else:
            expected_frames = {frozenset(span(frame)) for frame in word["center_frames"]}
        check(len(certificate[key]) == 8 and
              {frozenset(span(record["frame"])) for record in certificate[key]} == expected_frames,
              "cap frame inventory")
        for record in certificate[key]:
            frame = span(record["frame"])
            check(len(record["odd_vectors_by_target"]) == 112, "cap target inventory")
            for port, vector in zip(word["ports"], record["odd_vectors_by_target"]):
                check(vector in frame and bin(vector & port).count("1") % 2 == 1, "cap witness")
                cap_pairs += 1
    check(cap_pairs == 1792, "cap coverage")
    split_ranks = 0
    for record in certificate["split_carriers"]:
        sources = record["sources"]
        labels = [word["ports"][i] for i in sources]
        matrix = [[word["root_lines"][j][i] for j in sources] for i in record["block"]]
        masks = {}
        for target, port in enumerate(word["ports"]):
            mask = sum(1 << i for i, label in enumerate(labels) if bin(label & port).count("1") % 2 == 0)
            masks.setdefault(mask, []).append(target)
        check(record["target_masks"] == [{"mask": m, "targets": masks[m]} for m in sorted(masks)],
              "mask inventory")
        pairs = [(m, 255 ^ m) for m in masks if m < (255 ^ m) and (255 ^ m) in masks]
        check(len(pairs) == 7, "partition coverage")
        check(len(record["two_cap_partitions"]) == 7 and
              {tuple(p["masks"]) for p in record["two_cap_partitions"]} == set(pairs),
              "partition inventory")
        for partition in record["two_cap_partitions"]:
            check(tuple(partition["masks"]) in pairs, "partition masks")
            for mask, expected in zip(partition["masks"], partition["ranks"]):
                restricted = [[row[j] for j in range(8) if mask >> j & 1] for row in matrix]
                check(minor_rank(restricted) == expected, "split determinant rank")
                split_ranks += 1
        escape = record["four_cap_escape"]
        check(len(set(escape["targets"])) == 4 and minor_rank(escape["rows"]) == 4, "escape rank")
        for row, target in zip(escape["rows"], escape["targets"]):
            support = [labels[i] for i, value in enumerate(row) if value]
            check(len(span(support)) == 8, "escape frame")
            check(all(bin(x & word["ports"][target]).count("1") % 2 == 0 for x in support),
                  "escape target")
        for pair in range(2):
            plus, minus = escape["rows"][2 * pair:2 * pair + 2]
            check([Fraction(x + y, 2) for x, y in zip(plus, minus)] == matrix[2 * pair], "escape sum")
            check([Fraction(x - y, 2) for x, y in zip(plus, minus)] == matrix[2 * pair + 1], "escape difference")
    check(split_ranks == 112, "split rank coverage")
    print("PASS_K8_ANTICHAIN_INDEPENDENT columns=112 values=192 antichain=168 split_ranks=112 cap_pairs=1792")


if __name__ == "__main__":
    main()
