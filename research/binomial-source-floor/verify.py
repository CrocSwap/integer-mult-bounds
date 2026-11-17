#!/usr/bin/env python3
"""Check the new lower envelope without running predecessor executables."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement, product
import json
from math import prod
from pathlib import Path
import sys

from floor import height, need, source_floor


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def source_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            digest = sha256(raw).hexdigest()
            need(digest == row["sha256"], "changed input: " + row["path"])
            hashes[row["path"]] = digest
    need(len(hashes) == 2, "expected two cited source inputs")
    return hashes


def products(tokens, length):
    """Literal token words: multiplicities remain distinct positions."""
    need(len(tokens) <= 5 and 0 <= length <= 3, "literal word bound")
    return tuple(prod(word) for word in product(tokens, repeat=length))


def source_slots(targets, paid, cap):
    """Independent root/nonroot slots, without the telescope or binomial law."""
    low = min(targets)
    degree = height(low, cap)
    need(degree <= 3 and len(targets) <= 5 and len(paid) <= 5, "slot domain")
    need(max(paid) < low, "paid/target separation")
    total = len(targets) * sum(value <= cap for value in products(targets, degree))
    for depth in range(1, degree + 1):
        prefixes = products(paid, depth - 1)
        suffixes = products(targets, degree - depth)
        for prefix, rank, suffix, last in product(prefixes, paid, suffixes, targets):
            if prefix * rank * suffix <= cap < prefix * suffix * last:
                total += 1
    return total


def histogram_source(targets, paid, cap):
    """Independent product histograms for larger attaining examples."""
    degree = height(min(targets), cap)
    need(len(targets) <= 8 and len(paid) <= 8, "histogram token bound")
    need(max(paid) < min(targets), "histogram separation")
    target_powers, paid_powers = [Counter({1: 1})], [Counter({1: 1})]
    for _ in range(degree):
        for tokens, powers in ((targets, target_powers), (paid, paid_powers)):
            following = Counter()
            for value, count in powers[-1].items():
                for rank in tokens:
                    following[value * rank] += count
            powers.append(following)
    eligible = [
        sum(a * b for r, a in paid_powers[d].items()
            for k, b in target_powers[degree - d].items() if r * k <= cap)
        for d in range(degree + 1)
    ]
    w, q = len(targets), len(paid)
    return w * eligible[0] + sum(
        w * eligible[d] - q * eligible[d - 1] for d in range(1, degree + 1)
    )


def literal_checks():
    cases = strict = 0
    for low in (2, 3):
        for maximum in (low + 1, low + 2):
            for middle in range(low, maximum):
                targets = (low, middle, maximum)
                for q in (3, 4):
                    for paid in combinations_with_replacement(range(1, low), q):
                        for cap in range(1, low**4):
                            actual = source_slots(targets, paid, cap)
                            bound = source_floor(low, maximum, 3, q, 1, cap)
                            need(actual >= bound, "lower envelope failed")
                            if middle == low and set(paid) == {1}:
                                need(actual == bound, "collapsed inventory must attain")
                            strict += actual > bound
                            cases += 1
    return {"literal_inventories_and_caps": cases, "strict_comparisons": strict}


def attaining_checks():
    cases = 0
    for low in (2, 3, 4):
        for maximum in (low + 1, 2 * low + 1):
            for w in range(2, 6):
                for t in range(1, w):
                    for q in (w, w + 1):
                        targets = (low,) * (w - t) + (maximum,) * t
                        for degree in range(7):
                            caps = {low**degree, low**(degree + 1) - 1}
                            for cap in sorted(caps):
                                bound = source_floor(low, maximum, w, q, t, cap)
                                actual = histogram_source(targets, (1,) * q, cap)
                                need(actual == bound, "sharpness failed")
                                cases += 1
    return {"attaining_inventories_and_caps": cases}


def controls():
    need(source_floor(3, 8, 3, 5, 1, 26) == 29, "sharp first correction")
    need(source_slots((3, 7, 8), (1,) * 5, 26) == 35, "uncollapsed fixture")
    need(source_floor(3, 8, 3, 3, 1, 26) == 27, "Q=W boundary")
    need(source_floor(3, 8, 3, 5, 1, 8) == 9, "height-one slab")
    need(source_floor(3, 8, 3, 5, 1, 9) == 37, "new slab entry")
    need(source_floor(2, 3, 2, 3, 1, 3) == 4, "strict cutoff equality")
    # Q<W reverses the comparison: the collapsed inventory has 17 sources,
    # but this legal uncollapsed inventory has only 11.
    need(source_slots((2, 2, 4), (1,), 4) == 17, "collapsed Q<W control")
    need(source_slots((2, 3, 4), (1,), 4) == 11, "uncollapsed Q<W control")
    rejected = 0
    bad = ((3, 8, 3, 2, 1, 26), (3, 8, 3, 5, 0, 26),
           (3, 8, 3, 5, 3, 26), (3, 3, 3, 5, 1, 26),
           (3, 8, 3, 5, 1, 0), (3, 8, 3, 5, 1, 3**7),
           (True, 8, 3, 5, 1, 26), (3, 8, 9, 9, 1, 26))
    for args in bad:
        try:
            source_floor(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid summary accepted")
    return {"semantic_controls": 8, "domain_rejections": rejected}


def selected_application():
    """Use cited invoice constants; do not replay its scientific verifier."""
    raw = json.loads((ROOT / "research/joint-helper-lattice/RESULT.json").read_text())
    need(raw["productive_fields"] == 10928 and raw["paid_calls"] == 64620,
         "cited W0/Q0 constants changed")
    need(raw["targets"]["145"] == 224 and raw["strictification"]["power"] == 1024,
         "cited maximum multiplicity or power changed")
    need(raw["strictification"]["floor"] == 21
         and raw["strictification"]["cutoff"] == 20, "cited separation changed")
    v = 1024
    low, maximum, w, q0, t = 21**v, 145**v, 10928**v, 64620**v, 224**v
    need(low < maximum < low**2 and maximum**2 > low**3, "two-block threshold")
    need(q0 > w and 0 < t < w, "positive correction hypotheses")
    extra = (q0 - w) * t**2
    missing = sum(a * b for a, n in ((w - t, low), (t, maximum))
                  for b, m in ((w - t, low), (t, maximum)) if n * m >= low**3)
    need(missing == t**2, "first activation count")
    need(all(rank < low**3 for rank in (low, maximum)), "depth-one deficit")
    result = w**3 + extra
    return {"product_power": v, "first_strict_height": 2,
            "first_strict_floor_sha256": sha256(str(result).encode()).hexdigest(),
            "correction_bit_length": extra.bit_length(),
            "correction_sha256": sha256(str(extra).encode()).hexdigest()}


def run():
    hashes = source_inputs()
    result = {"schema_version": 1, "status": "PASS_BINOMIAL_SOURCE_FLOOR"}
    for check in (literal_checks, attaining_checks, controls, selected_application):
        result.update(check())
    need(source_inputs() == hashes, "input changed during verification")
    result["source_sha256"] = hashes
    result["package_sha256"] = {
        p.name: sha256(p.read_bytes()).hexdigest()
        for p in sorted(PACKAGE.iterdir()) if p.is_file() and p.suffix in (".py", ".md", ".json")
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a hash-bound receipt outside the checkout")
    args = parser.parse_args()
    if args.receipt:
        need(not args.receipt.resolve().is_relative_to(ROOT), "receipt must be outside checkout")
    sys.set_int_max_str_digits(100000)
    result = run()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.write_text(encoded)
    print(encoded, end="")
    print("PASS_BINOMIAL_SOURCE_FLOOR no_new_kappa")


if __name__ == "__main__":
    main()
