#!/usr/bin/env python3
"""Check the sharp five-label cap and its finite proof steps.

Prepared for Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from functools import lru_cache, reduce
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
W4 = tuple(map(int, "012343234031"))
W5 = tuple(map(int, "012343103432"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def differences(points):
    return {a ^ b for a, b in combinations(points, 2)}


def affine_rank(points):
    basis = {}
    for p in points:
        x = p ^ points[0]
        while x:
            bit = x.bit_length() - 1
            if bit not in basis:
                basis[bit] = x
                break
            x ^= basis[bit]
    return len(basis)


def support_checks():
    histograms = {}
    count = 0
    for size, allowed in ((5, {3: {7}, 4: {10}}),
                          (6, {3: {7}, 4: {12, 15}}),
                          (7, {3: {7}, 4: {13, 15}})):
        histogram = Counter()
        for points in combinations(range(16), size):
            rank = affine_rank(points)
            support = len(differences(points))
            require(rank in allowed and support in allowed[rank], "support lemma")
            histogram[support] += 1
            count += 1
        histograms[str(size)] = {str(k): v for k, v in sorted(histogram.items())}
    require(count == 23816, "support domain count")
    return {"subsets": count, "histograms": histograms}


def hamiltonian_cycle(points):
    """Search the literal cube graph, without the quotient or excess rules."""
    points = tuple(sorted(points))
    size = len(points)
    neighbors = [sum(1 << j for j, b in enumerate(points)
                     if (a ^ b).bit_count() == 1) for a in points]
    if any(mask.bit_count() < 2 for mask in neighbors):
        return False
    full = (1 << size) - 1

    @lru_cache(None)
    def visit(last, used):
        if used == full:
            return bool(neighbors[last] & 1)
        candidates = neighbors[last] & ~used
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            if visit(bit.bit_length() - 1, used | bit):
                return True
        return False

    return visit(0, 1)


def quotient_check(projected, minority):
    z = reduce(int.__xor__, projected)
    even = {x for x in range(16) if x.bit_count() % 2 == 0}
    require(z != 0 and z not in differences(projected), "missing direction")
    shifted = {x ^ z for x in projected}
    require(set(projected).isdisjoint(shifted) and set(projected) | shifted == even,
            "quotient partition")
    degrees = {u: sum((u ^ t).bit_count() == 1 for t in projected)
               for u in range(16) if u.bit_count() % 2}
    require(all(degrees[u] + degrees[u ^ z] == 4 for u in degrees), "degree sum")
    require({z, z ^ 16} <= differences(minority), "missing lifts not covered")
    levels = tuple(tuple(b & 15 for b in minority if b >> 4 == level)
                   for level in (0, 1))
    if tuple(map(len, levels)) != (2, 2):
        return "unequal_levels"
    same = next((level for level in (0, 1) if levels[level][0] ^ levels[level][1] == z), None)
    require(same is not None, "same-level missing lift")
    repeated = set(levels[0]) & set(levels[1])
    require(repeated, "repeated projection")
    require(any(u in levels[same] and u ^ z in levels[same] for u in repeated),
            "repeated projection lacks partner")
    # Test every alternating order and injective block assignment directly.
    for left in permutations(levels[0]):
        for right in permutations(levels[1]):
            cycle = (left[0], right[0], left[1], right[1])
            for blocks in permutations(projected):
                legal = all((blocks[i] ^ cycle[i]).bit_count() == 1 and
                            (blocks[i] ^ cycle[(i + 1) % 4]).bit_count() == 1
                            for i in range(4))
                require(not legal, "universal quotient cycle")
    return "balanced_levels"


def set_checks():
    even = tuple(x for x in range(16) if x.bit_count() % 2 == 0)
    odd_lifts = tuple(x for x in range(32) if (x & 15).bit_count() % 2)
    counts = Counter()
    control = None
    for projected in combinations(even, 4):
        majority = projected + tuple(t ^ 16 for t in projected)
        da = differences(majority)
        for minority in combinations(odd_lifts, 4):
            counts["set_pairs"] += 1
            points = majority + minority
            universal = len(differences(points)) == 31
            if not universal:
                if control is None and hamiltonian_cycle(points):
                    control = list(points)
                continue
            counts["universal_sets"] += 1
            require(len(da) == 13, "universal majority support")
            counts[quotient_check(projected, minority)] += 1
            require(not hamiltonian_cycle(points), "literal universal cube cycle")
            counts["literal_graph_rejections"] += 1
    require(counts["set_pairs"] == 127400 and counts["universal_sets"] == 13664,
            "set domain count")
    require(control is not None, "missing nonuniversal positive graph control")
    return {**dict(sorted(counts.items())), "nonuniversal_cycle_control": control}


def word_points(word):
    require(len(word) == 12, "length")
    require(all(type(label) is int and 0 <= label < 5 for label in word), "label")
    points = []
    state = 0
    for label in word:
        points.append(state)
        state ^= 1 << label
    require(state == 0, "restoration")
    require(len(set(points)) == 12, "simplicity")
    require(len(differences(points)) == 31, "universality")
    return tuple(points)


def excess(points, mask):
    classes = [tuple(x for x in points if (x & mask).bit_count() % 2 == bit)
               for bit in (0, 1)]
    return sum(len(c) * (len(c) - 1) // 2 - len(differences(c)) for c in classes)


def check_word(word, mask, cap=11):
    require(type(mask) is int and 0 < mask < 32 and mask.bit_count() >= 4, "mask")
    points = word_points(word)
    value = excess(points, mask)
    require(value <= cap, "cap")
    require(hamiltonian_cycle(points), "positive graph control")
    return value


def reject(action, reason):
    try:
        action()
    except ValueError as error:
        require(reason in str(error), "wrong rejection: " + str(error))
        return
    raise ValueError("accepted control: " + reason)


def controls():
    require(check_word(W4, 23) == check_word(W5, 31) == 11, "sharpness")
    for mask in (0, 1, 32, True):
        reject(lambda: check_word(W4, mask), "mask")
    for word, reason in ((W4[:-1], "length"), ((True,) + W4[1:], "label"),
                         ((5,) + W4[1:], "label"), (W4[:-1] + (0,), "restoration"),
                         ((0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 0, 0), "simplicity"),
                         (tuple(map(int, "010201030203")), "universality")):
        reject(lambda: word_points(word), reason)
    reject(lambda: check_word(W4, 23, 10), "cap")
    require(excess(word_points(W4), 1) == 21, "low-weight boundary")
    points = (0, 3, 5, 9, 16, 19, 21, 25, 1, 14, 17, 30)
    require(len(differences(points)) == 31 and excess(points, 15) == 18,
            "set-only boundary")
    require(not hamiltonian_cycle(points), "set-only graph boundary")
    reject(lambda: require(excess(points, 15) <= 11, "set-only cap"), "set-only cap")
    return {"semantic_rejections": 12, "weight_four_witness": W4,
            "weight_five_witness": W5, "sharp_value": 11,
            "low_weight_excess": 21, "set_only_excess": 18}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    actual = {"schema": "f7-five-label-sharp-cap/v1", "proved_cap": 11,
              "supports": support_checks(), "sets": set_checks(), "controls": controls(),
              "source_sha256": {f: sha256((PACKAGE / f).read_bytes()).hexdigest() for f in FILES}}
    if args.emit_receipt:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(canonical(actual) == canonical(stored), "receipt")
    for value in (10, True):
        changed = dict(actual, proved_cap=value)
        reject(lambda: require(canonical(changed) == canonical(stored), "receipt"), "receipt")
    print("PASS_F7_FIVE_LABEL_SHARP_CAP cap=11 support_sets=23816 "
          "set_pairs=127400 universal_graphs=13664")


if __name__ == "__main__":
    main()
