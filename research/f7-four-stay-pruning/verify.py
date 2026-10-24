#!/usr/bin/env python3
"""Exact corroboration of the length-ten codimension-one excess theorem."""

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path


MASKS = (7, 11, 13, 14, 15)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cycle_states(word):
    require(len(word) == 10, "the word must have length ten")
    require(all(type(j) is int and 0 <= j < 4 for j in word), "invalid label")
    states = []
    q = 0
    for label in word:
        require(q not in states, "the cycle must be simple")
        states.append(q)
        q ^= 1 << label
    require(q == 0, "the cycle must restore every coordinate")
    return tuple(states)


def pair_sums(cell):
    return {x ^ y for x, y in combinations(cell, 2)}


def statistics(states, mask):
    require(type(mask) is int and 1 <= mask < 16, "invalid functional")
    require(len(states) == len(set(states)) == 10, "ten distinct states required")
    require(all(type(x) is int and 0 <= x < 16 for x in states), "invalid state")
    cells = tuple(tuple(x for x in states if (x & mask).bit_count() % 2 == p)
                  for p in (0, 1))
    supports = tuple(pair_sums(cell) for cell in cells)
    slots = sum(len(cell) * (len(cell) - 1) // 2 for cell in cells)
    excess = slots - sum(len(support) for support in supports)
    return cells, supports, excess


def matching_check(states, mask):
    """Check the degree identity and matching premise, without assuming balance."""
    colors = tuple((x & mask).bit_count() % 2 for x in states)
    internal = [0, 0]
    endpoints = set()
    for i in range(10):
        j = (i + 1) % 10
        if colors[i] == colors[j]:
            require(i not in endpoints and j not in endpoints, "not a matching")
            endpoints.update((i, j))
            internal[colors[i]] += 1
    s = colors.count(0)
    t = 10 - s
    require(s - t == internal[0] - internal[1], "degree identity failed")
    require(2 * internal[0] <= s and 2 * internal[1] <= t, "matching capacity")
    require(max(s, t) <= 2 * min(s, t), "matching balance failed")


def exact_walks():
    """At most 4**9 prefixes; restoration uniquely determines the last edge."""
    for prefix in product(range(4), repeat=9):
        states = []
        q = 0
        for label in prefix:
            if q in states:
                break
            states.append(q)
            q ^= 1 << label
        else:
            if q not in states and q.bit_count() == 1:
                yield prefix + (q.bit_length() - 1,)


def walk_corroboration():
    maxima = {mask: -1 for mask in MASKS}
    witnesses = {}
    histogram = {mask: {} for mask in MASKS}
    count = 0
    for word in exact_walks():
        states = cycle_states(word)
        count += 1
        for mask in MASKS:
            matching_check(states, mask)
            cells, supports, excess = statistics(states, mask)
            split = tuple(sorted(map(len, cells)))
            require(split in ((4, 6), (5, 5)), "unexpected split")
            if mask == 15:
                require(split == (5, 5) and excess == 6, "parity endpoint")
            require(excess <= 11, "sharp cap failed")
            key = str(excess)
            histogram[mask][key] = histogram[mask].get(key, 0) + 1
            if excess > maxima[mask]:
                maxima[mask] = excess
                witnesses[mask] = "".join(map(str, word))
            if split == (4, 6):
                small = 0 if len(cells[0]) == 4 else 1
                require((excess == 11) == (len(supports[small]) == 3),
                        "equality characterization failed")
    require(count == 2640, "incomplete walk enumeration")
    require(maxima == {7: 11, 11: 11, 13: 11, 14: 11, 15: 6}, "maxima failed")
    return {"labeled_cycles": count, "functional_checks": count * len(MASKS),
            "maxima": {str(mask): maxima[mask] for mask in MASKS},
            "witnesses": {str(mask): witnesses[mask] for mask in MASKS},
            "histogram": {str(mask): histogram[mask] for mask in MASKS}}


def subset_envelope():
    """Independent set-level envelope; this does not enumerate walks."""
    checked = 0
    equalities = 0
    for states in combinations(range(16), 10):
        for mask in MASKS:
            # Count ordered nonzero differences directly, independently of pair_sums.
            cells = [[x for x in states if (x & mask).bit_count() % 2 == p]
                     for p in (0, 1)]
            sizes = sorted(map(len, cells))
            if sizes not in ([4, 6], [5, 5]):
                continue
            excess = 0
            for cell in cells:
                support = {x ^ y for x in cell for y in cell if x != y}
                excess += len(cell) * (len(cell) - 1) // 2 - len(support)
                if len(cell) >= 5:
                    require(len(support) == 7, "large-set lemma failed")
                if len(cell) == 4:
                    affine_plane = 0
                    for x in cell:
                        affine_plane ^= x
                    require((len(support) == 3) == (affine_plane == 0),
                            "affine-plane equality failed")
            require(excess <= 11, "set envelope failed")
            if sizes == [5, 5]:
                require(excess == 6, "balanced set value failed")
            checked += 1
            equalities += excess == 11
    require(checked > 0 and equalities > 0, "empty set corroboration")
    return {"admitted_set_functional_pairs": checked, "equalities": equalities}


def controls():
    for word in ((0,) * 10, tuple(map(int, "0102301022")),
                 (0, 1, 0, 2, 3, 0, 1, 0, 2, 4),
                 (False, 1, 0, 2, 3, 0, 1, 0, 2, 3)):
        try:
            cycle_states(word)
        except ValueError:
            pass
        else:
            raise ValueError("invalid word was accepted")
    sharp = cycle_states(tuple(map(int, "0102301023")))
    require(statistics(sharp, 7)[2] == 11, "cap-ten mutation not detected")
    require(len({x ^ y for x in sharp for y in sharp}) == 16,
            "sharp witness must be universal")
    for mask in (0, 16, True):
        try:
            statistics(sharp, mask)
        except ValueError:
            pass
        else:
            raise ValueError("invalid functional was accepted")
    low = cycle_states(tuple(map(int, "0102131213")))
    require(statistics(low, 1)[2] == 21 > 13, "weight restriction control")
    require(len({x ^ y for x in low for y in low}) == 16, "control universality")
    return 9


def receipt():
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        path = root / name
        require(path.stat().st_size <= 1_048_576, "oversize package source")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"schema": "f7-four-stay-pruning/v1", "claim_type": "scoped proof",
            "source_sha256": hashes, "walks": walk_corroboration(),
            "sets": subset_envelope(), "controls": controls()}


def root_outside_package(path):
    checkout = Path(__file__).resolve().parents[2]
    return not path.resolve().is_relative_to(checkout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a fresh external JSON receipt")
    parser.add_argument("--check-receipt", type=Path, help="compare with a prior receipt")
    args = parser.parse_args()
    result = receipt()
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.check_receipt is not None:
        require(args.check_receipt.stat().st_size <= 1_048_576, "oversize receipt")
        supplied = json.loads(args.check_receipt.read_text(encoding="utf-8"))
        require(json.dumps(supplied, sort_keys=True, indent=2) + "\n" == payload,
                "receipt does not match this replay and its source hashes")
    if args.output is not None:
        require(root_outside_package(args.output), "receipt must be outside the checkout")
        with args.output.open("x", encoding="utf-8") as stream:
            written = stream.write(payload)
            require(written == len(payload), "incomplete receipt write")
    print("PASS_F7_FOUR_STAY_PRUNING labeled_cycles=2640 functional_checks=13200 "
          "max_weight3=11 max_weight4=6 substituted_budget=13 controls=9")
    print(payload, end="")


if __name__ == "__main__":
    main()
