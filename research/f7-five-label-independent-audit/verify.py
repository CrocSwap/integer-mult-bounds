#!/usr/bin/env python3
"""Complete-word audit of PR4992; no predecessor code imports.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Candidates are generated from positions and perfect matchings, not cube walks.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import comb, factorial
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
MASKS = (15, 23, 27, 29, 30, 31)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matchings(items):
    """Every perfect matching once, paired by its smallest unused position."""
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for index, partner in enumerate(rest):
        for tail in matchings(rest[:index] + rest[index + 1:]):
            yield ((first, partner),) + tail


def candidates():
    """One representative per coordinate-permutation orbit, before tests."""
    for repeated in combinations(range(12), 4):
        remaining = tuple(p for p in range(12) if p not in repeated)
        for pairs in matchings(remaining):
            word = [0] * 12
            for label, pair in enumerate(pairs, start=1):
                for position in pair:
                    word[position] = label
            yield tuple(word)


def prefixes(word):
    require(len(word) == 12, "length")
    require(all(type(label) is int and 0 <= label < 5 for label in word), "label")
    point, states = 0, []
    for label in word:
        states.append(point)
        point ^= 1 << label
    require(point == 0, "restoration")
    return states


def support(points):
    return {x ^ y for x, y in combinations(points, 2)}


def universal(points):
    # Count ordered pair sums, including zero; no span surrogate.
    return {x ^ y for x in points for y in points} == set(range(32))


def measure(points, mask):
    classes = [[x for x in points if (x & mask).bit_count() % 2 == parity]
               for parity in (0, 1)]
    sizes = [len(part) for part in classes]
    supports = [len(support(part)) for part in classes]
    return (tuple(sorted(sizes, reverse=True)), tuple(supports),
            sum(comb(n, 2) for n in sizes) - sum(supports))


def check_target(word, mask=31, cap=11):
    require(mask in MASKS, "weight")
    points = prefixes(word)
    require(len(set(points)) == 12, "simplicity")
    require(universal(points), "universality")
    split, sizes, excess = measure(points, mask)
    require(split in ((6, 6), (7, 5)), "split")
    require(excess <= cap, "cap")
    return split, sizes, excess


def audit():
    counts, histograms = Counter(), {4: Counter(), 5: Counter()}
    all_words, universal_words, boundary = set(), [], None
    for word in candidates():
        require(word not in all_words, "duplicate candidate")
        all_words.add(word)
        counts["candidates"] += 1
        require(tuple(word.count(i) for i in range(5)) == (4, 2, 2, 2, 2), "multiplicity")
        points = prefixes(word)
        if len(set(points)) != 12:
            counts["nonsimple"] += 1
            continue
        counts["simple"] += 1
        if not universal(points):
            counts["simple_nonuniversal"] += 1
            if boundary is None:
                for mask in MASKS[:-1]:
                    if measure(points, mask)[0] == (8, 4):
                        boundary = {"word": "".join(map(str, word)), "mask": mask}
                        break
            continue
        counts["universal"] += 1
        universal_words.append("".join(map(str, word)))
        for mask in MASKS:
            split, sizes, excess = check_target(word, mask)
            histograms[mask.bit_count()][f"{split[0]},{split[1]}:X={excess}"] += 1
            even = [x for x in points if (x & mask).bit_count() % 2 == 0]
            odd = [x for x in points if (x & mask).bit_count() % 2 == 1]
            require(len(support(even) | support(odd)) == 15, "kernel coverage")
            require(sum(sizes) >= 19, "separate supports")
    expected_count = comb(12, 4) * factorial(8) // (2**4 * factorial(4))
    require(counts["candidates"] == expected_count == 51975, "domain count")
    require(counts["simple"] + counts["nonsimple"] == expected_count, "partition")
    require(boundary is not None, "missing nonuniversal boundary fixture")
    for weight in (4, 5):
        require(max(int(k.split("=")[1]) for k in histograms[weight]) == 11, "sharpness")
    return {
        "counts": dict(sorted(counts.items())),
        "histograms": {str(w): dict(sorted(h.items())) for w, h in histograms.items()},
        "candidates_sha256": sha256(("\n".join(sorted("".join(map(str, w)) for w in all_words)) + "\n").encode()).hexdigest(),
        "universal_words_sha256": sha256(("\n".join(sorted(universal_words)) + "\n").encode()).hexdigest(),
        "nonuniversal_84": boundary,
        "controls": controls(boundary),
    }


def controls(boundary):
    results = []

    def reject(name, call, reason):
        try:
            call()
        except ValueError as exc:
            require(str(exc) == reason, f"wrong rejection for {name}: {exc}")
        else:
            raise ValueError(f"accepted negative control: {name}")
        results.append(name)

    witness4 = tuple(map(int, "012343234031"))
    witness5 = tuple(map(int, "012343103432"))
    require(check_target(witness4, 23) == ((7, 5), (7, 13), 11), "literal weight-four witness")
    require(check_target(witness5, 31) == ((6, 6), (7, 12), 11), "literal weight-five witness")
    for witness, mask in ((witness4, 23), (witness5, 31)):
        original = measure(prefixes(witness), mask)
        for shift in range(32):
            shifted = [point ^ shift for point in prefixes(witness)]
            current = measure(shifted, mask)
            require(current[0] == original[0] and sorted(current[1]) == sorted(original[1])
                    and current[2] == original[2] and universal(shifted), "translation")
        for offset in range(12):
            rotated = witness[offset:] + witness[:offset]
            for orientation in (rotated, rotated[::-1]):
                require(check_target(orientation, mask)[2] == 11, "dihedral witness")
    results.extend(["translation_checks=64", "dihedral_checks=48"])
    reject("cap_ten", lambda: check_target(witness5, 31, 10), "cap")
    reject("wrong_length", lambda: check_target(witness5[:-1]), "length")
    reject("out_of_range_label", lambda: check_target((5,) + witness5[1:]), "label")
    reject("negative_label", lambda: check_target((-1,) + witness5[1:]), "label")
    reject("nonintegral_label", lambda: check_target((0.0,) + witness5[1:]), "label")
    reject("not_restored", lambda: check_target(witness5[:-1] + (0,)), "restoration")
    reject("nonsimple", lambda: check_target(tuple(map(int, "000011223344"))), "simplicity")
    reject("low_weight", lambda: check_target(witness5, 7), "weight")
    boundary_word = tuple(map(int, boundary["word"]))
    require(measure(prefixes(boundary_word), boundary["mask"])[0] == (8, 4), "boundary split")
    reject("nonuniversal_84", lambda: check_target(boundary_word, boundary["mask"]), "universality")
    require(2 * comb(6, 2) - 15 == 15 and measure(prefixes(witness5), 31)[2] == 11,
            "merged-support discriminant")
    results.append("merged_supports_distinguished")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    receipt = audit()
    if args.emit_receipt:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(receipt == expected, "receipt mismatch")
        print("PASS_F7_FIVE_LABEL_INDEPENDENT_AUDIT "
              f"candidates={receipt['counts']['candidates']} "
              f"universal={receipt['counts']['universal']} cap=11")


if __name__ == "__main__":
    main()
