#!/usr/bin/env python3
"""Independent path-join audit of PR4992; no predecessor code imports.

Mihir Srivastava with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MASKS = (15, 23, 27, 29, 30, 31)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical(cycle):
    """Root stays zero; identify just the two traversal directions."""
    return min(cycle, (0,) + cycle[:0:-1])


def half_paths(n, length):
    endpoints = defaultdict(list)
    stack = [((0,), 1)]
    while stack:
        path, used = stack.pop()
        if len(path) == length + 1:
            endpoints[path[-1]].append((path, used))
            continue
        for coordinate in range(n):
            neighbor = path[-1] ^ (1 << coordinate)
            if not used & (1 << neighbor):
                stack.append((path + (neighbor,), used | (1 << neighbor)))
    return endpoints


def joined_cycles(n, length):
    require(n >= 2 and length % 2 == 0 and 4 <= length <= 2**n, "domain")
    for endpoint, paths in sorted(half_paths(n, length // 2).items()):
        shared = 1 | (1 << endpoint)
        for (left, left_used), (right, right_used) in combinations(paths, 2):
            if left_used & right_used == shared:
                yield canonical(left + right[-2:0:-1])


def literal_cycles(n, length):
    """Small independent oracle: all n**length words, without prefix pruning."""
    cycles = set()
    for word in product(range(n), repeat=length):
        points, state = [], 0
        for coordinate in word:
            points.append(state)
            state ^= 1 << coordinate
        if state == 0 and len(set(points)) == length:
            cycles.add(canonical(tuple(points)))
    return cycles


def validate_cycle(points, n=5, length=12):
    require(len(points) == length and points[0] == 0, "length/root")
    require(all(type(x) is int and 0 <= x < 2**n for x in points), "vertex")
    require(len(set(points)) == length, "simplicity")
    require(all((x ^ y).bit_count() == 1
                for x, y in zip(points, points[1:] + points[:1])), "edge/closure")


def support_bits(points):
    support = 0
    for x, y in combinations(points, 2):
        support |= 1 << (x ^ y)
    return support


def split_excess(points, mask):
    classes = (tuple(x for x in points if (x & mask).bit_count() % 2 == bit)
               for bit in (0, 1))
    sizes, value = [], 0
    for group in classes:
        sizes.append(len(group))
        value += len(group) * (len(group) - 1) // 2 - support_bits(group).bit_count()
    return tuple(sorted(sizes, reverse=True)), value


def check_target(points, mask, cap=11):
    validate_cycle(points)
    require(support_bits(points) == (1 << 32) - 2, "universality")
    require(type(mask) is int and mask in MASKS, "mask")
    split, value = split_excess(points, mask)
    require(split in ((6, 6), (7, 5)), "split")
    require(value <= cap, "cap")
    return value


def word_points(word):
    state, result = 0, []
    for character in word:
        result.append(state)
        state ^= 1 << int(character)
    require(state == 0, "word closure")
    return tuple(result)


def expect_rejection(action, reason):
    try:
        action()
    except ValueError as error:
        require(str(error) == reason, "wrong rejection")
        return
    raise ValueError("missed rejection: " + reason)


def controls():
    w4 = word_points("012343234031")
    w5 = word_points("012343103432")
    require(check_target(w4, 23) == check_target(w5, 31) == 11, "sharp witnesses")
    expect_rejection(lambda: check_target(w4, 23, 10), "cap")
    expect_rejection(lambda: check_target(w4, 1), "mask")
    expect_rejection(lambda: validate_cycle(w4[:-1]), "length/root")
    expect_rejection(lambda: validate_cycle(w4[:-1] + (w4[1],)), "simplicity")
    expect_rejection(lambda: validate_cycle(w4[:-1] + (14,)), "edge/closure")
    expect_rejection(lambda: validate_cycle((False,) + w4[1:]), "vertex")
    nonuniversal = word_points("010201030203")
    validate_cycle(nonuniversal)
    expect_rejection(lambda: check_target(nonuniversal, 23), "universality")
    set_only = (0, 3, 5, 9, 16, 19, 21, 25, 1, 14, 17, 30)
    require(support_bits(set_only) == (1 << 32) - 2, "universal set control")
    require(split_excess(set_only, 15) == ((8, 4), 18), "set-only excess")
    expect_rejection(lambda: check_target(set_only, 15), "edge/closure")
    require(split_excess(w4, 1)[1] == 21, "low-weight boundary")
    return {"semantic_rejections": 8, "sharp_witnesses": 2,
            "set_only_excess": 18, "low_weight_excess": 21}


def calibrate():
    report = []
    for n, length in ((2, 4), (3, 4), (3, 6), (3, 8), (4, 6), (4, 8)):
        joined = list(joined_cycles(n, length))
        literal = literal_cycles(n, length)
        require(len(joined) == len(set(joined)), "duplicate joined cycle")
        require(set(joined) == literal, "literal-word calibration")
        for cycle in joined:
            validate_cycle(cycle, n, length)
        report.append({"n": n, "length": length, "cycles": len(joined),
                       "literal_words": n**length})
    return report


def full_audit():
    counts = Counter()
    histogram = Counter()
    maxima = {str(mask): -1 for mask in MASKS}
    cycle_hash = sha256()
    for cycle in joined_cycles(5, 12):
        validate_cycle(cycle)
        counts["all_cycles"] += 1
        labels = 0
        for x, y in zip(cycle, cycle[1:] + cycle[:1]):
            labels |= x ^ y
        if labels == 31:
            counts["all_five_labels"] += 1
        if support_bits(cycle) != (1 << 32) - 2:
            continue
        counts["universal_cycles"] += 1
        cycle_hash.update(bytes(cycle))
        for mask in MASKS:
            split, value = split_excess(cycle, mask)
            require(split in ((6, 6), (7, 5)), "universal split")
            require(value <= 11, "universal cap")
            histogram[(mask.bit_count(), split, value)] += 1
            maxima[str(mask)] = max(maxima[str(mask)], value)
            counts["functional_checks"] += 1
    return {**dict(counts), "maxima_by_mask": maxima,
            "universal_cycle_stream_sha256": cycle_hash.hexdigest(),
            "histogram": [{"weight": weight, "split": list(split),
                           "excess": excess, "count": count}
                          for (weight, split, excess), count in sorted(histogram.items())]}


def source_bindings():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    verified = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            actual = sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(actual == row["sha256"], "source drift: " + row["path"])
            verified[row["path"]] = actual
    return verified


def compare_predecessor(actual):
    # Comparison only, after the complete independent census; no search decisions.
    old = json.loads((ROOT / "research/f7-five-label-pruning-proof/RESULT.json").read_text(
        encoding="utf-8"))["walks"]
    for new_key, old_key in (("all_cycles", "canonical_closed"),
                             ("all_five_labels", "all_five_labels"),
                             ("universal_cycles", "universal"),
                             ("functional_checks", "functional_checks")):
        require(actual[new_key] == 60 * old[old_key], "predecessor count: " + new_key)
    expected = [dict(row, count=60 * row["count"]) for row in old["histogram"]]
    require(actual["histogram"] == expected, "predecessor histogram")
    require(actual["maxima_by_mask"] == old["maxima_by_mask"], "predecessor maxima")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    pins = source_bindings()
    checks = controls()
    calibration = calibrate()
    audit = full_audit()
    compare_predecessor(audit)
    receipt = {"schema": "f7-sharp-cap-independent-audit/v1", "controls": checks,
               "calibration": calibration, "audit": audit, "source_sha256": pins,
               "package_sha256": {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
                                  for name in ("README.md", "verify.py", "test_mutations.py",
                                               "SOURCES.json", "TASK.json", "VERIFY.json")}}
    if args.emit_receipt:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        require(json_bytes(receipt) == json_bytes(expected), "receipt mismatch")
        print("PASS_F7_SHARP_CAP_INDEPENDENT_AUDIT "
              f"cycles={audit['all_cycles']} universal={audit['universal_cycles']} cap=11")


if __name__ == "__main__":
    main()
