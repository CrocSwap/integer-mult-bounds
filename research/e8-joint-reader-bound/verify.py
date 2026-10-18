#!/usr/bin/env python3
"""Exact E8 joint-reader obstruction. Python 3.10+, standard library.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
Definitions and parabolic reduction follow Chi Zhao's PR631; see PROOF.md.
All checks remain active under python -O. No predecessor code is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def binary_basis(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return list(pivots.values())


def rational_rank(rows):
    pivots = {}
    for original in rows:
        row = list(original)
        for col, basis in sorted(pivots.items()):
            if row[col]:
                a, b = row[col], basis[col]
                row = [b * x - a * y for x, y in zip(row, basis)]
                common = gcd(*row)
                if common:
                    row = [x // common for x in row]
        col = next((i for i, x in enumerate(row) if x), None)
        if col is not None:
            pivots[col] = row
    return len(pivots)


def inverse(matrix):
    n = len(matrix)
    aug = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
           for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if aug[i][col])
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [x / scale for x in aug[col]]
        for i in range(n):
            if i != col:
                scale = aug[i][col]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[col])]
    return [row[n:] for row in aug]


def geometry():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.append(tuple(root))
    roots += [(1,) + signs for signs in product((-1, 1), repeat=7)
              if sum(x < 0 for x in signs) % 2 == 0]
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        root = [0] * 8
        root[i], root[i + 1] = -2, 2
        simple.append(tuple(root))
    require(len(set(roots)) == 120 and all(dot(r, r) == 8 for r in roots),
            "root geometry")
    inv = inverse(simple)
    supports = []
    for root in roots:
        coords = [sum(root[k] * inv[k][j] for k in range(8)) for j in range(8)]
        require(all(x.denominator == 1 for x in coords), "integral simple coordinates")
        require(all(x >= 0 for x in coords) or all(x <= 0 for x in coords),
                "common-sign simple coordinates")
        supports.append(sum(1 << j for j, x in enumerate(coords) if x))
    return roots, simple, supports


def decoder(roots, simple):
    require(all(dot(x, y) % 4 == 0 for x in roots for y in roots), "integral Gram")
    rows = [sum(((1 + dot(x, y) // 4) % 2) << i for i, y in enumerate(roots))
            for x in roots]
    basis = binary_basis(rows)
    require(len(basis) == 9, "reader code dimension")
    code = [0]
    for word in basis:
        code += [word ^ x for x in code]
    code = sorted(code)
    require(len(set(code)) == 512, "reader code size")
    histogram = Counter(x.bit_count() for x in code)
    require(histogram == {0: 1, 56: 255, 64: 255, 120: 1}, "reader code weights")
    root_index = {r: i for i, r in enumerate(roots)}
    root_index.update({tuple(-x for x in r): i for i, r in enumerate(roots)})
    code_set = set(code)
    for simple_root in simple:
        perm = [root_index[tuple(x - (dot(r, simple_root) // 4) * y
                                for x, y in zip(r, simple_root))] for r in roots]
        require(len(set(perm)) == 120, "reflection permutation")
        for word in code:
            image = sum(1 << perm[i] for i in range(120) if word >> i & 1)
            require(image in code_set, "Weyl reader-code invariance")
    return rows, code


def flat_census(roots, supports, code):
    maxima = [0] * 9
    thresholds = [120] * 9
    census = []
    witnesses = [None] * 9
    for subset in range(256):
        dimension = subset.bit_count()
        indices = [i for i, s in enumerate(supports) if not s & ~subset]
        flat = sum(1 << i for i in indices)
        require(rational_rank([roots[i] for i in indices]) == dimension, "flat dimension")
        distance, reader = min(((w & ~flat).bit_count(), w) for w in code[1:])
        maxima[dimension] = max(maxima[dimension], len(indices))
        if distance < thresholds[dimension]:
            thresholds[dimension] = distance
            witnesses[dimension] = {"simple_subset": subset, "reader": str(reader),
                                    "deleted_indices": [i for i in range(120)
                                                        if (reader & ~flat) >> i & 1]}
        census.append({"simple_subset": subset, "dimension": dimension,
                       "root_lines": len(indices), "minimum_deletions": distance})
    require(maxima == [0, 1, 3, 6, 12, 20, 36, 63, 120], "flat capacities")
    require(thresholds == [56, 55, 53, 50, 44, 36, 26, 1, 0], "reader thresholds")
    for d, witness in enumerate(witnesses):
        deleted = sum(1 << i for i in witness["deleted_indices"])
        reader = int(witness["reader"])
        require(rational_rank([r for i, r in enumerate(roots)
                               if (reader & ~deleted) >> i & 1]) == d, "sharp threshold witness")
    return maxima, thresholds, census, witnesses


def pair_bound(p, capacities, thresholds):
    require(0 <= p < 56, "puncture domain must retain all nine reader dimensions")
    candidates = [(a + 8 * b, a, b) for a in range(9) for b in range(a, 9)
                  if thresholds[a] <= p and thresholds[b] <= p
                  and capacities[a] + capacities[b] >= 84 - p]
    require(bool(candidates), "nonempty relaxation")
    return min(candidates)


def check_invoice(p, ranks, capacities, thresholds):
    require(0 <= p < 56, "puncture domain must retain all nine reader dimensions")
    require(len(ranks) == 9 and all(type(d) is int and 0 <= d <= 8 for d in ranks),
            "nine physical ranks required")
    require(all(thresholds[d] <= p for d in ranks), "single-reader threshold")
    require(all(capacities[a] + capacities[b] >= 84 - p for a, b in combinations(ranks, 2)),
            "joint-reader union constraint")


def negative_controls(capacities, thresholds):
    cases = [(36, [5] * 9, "joint-reader union constraint"),
             (43, [5, 5] + [6] * 7, "joint-reader union constraint"),
             (51, [4, 5] + [6] * 7, "joint-reader union constraint"),
             (35, [5] + [8] * 8, "single-reader threshold"),
             (55, [5] * 8, "nine physical ranks required"),
             (56, [0] + [8] * 8, "puncture domain")]
    names = []
    for p, ranks, expected in cases:
        try:
            check_invoice(p, ranks, capacities, thresholds)
        except ValueError as exc:
            require(expected in str(exc), "negative control wrong rejection")
            names.append({"punctures": p, "ranks": ranks, "rejected_by": expected})
        else:
            raise ValueError("negative control unexpectedly accepted")
    # These satisfy necessary inequalities; they are NOT constructed decoders.
    for p, ranks in [(44, [5] * 9), (52, [4] + [5] * 8)]:
        check_invoice(p, ranks, capacities, thresholds)
    return names


def source_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for entry in manifest["retained_sources"]:
        data = (HERE / entry["local_path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "source SHA256 mismatch")
        git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(git_blob == entry["git_blob"], "source Git blob mismatch")
    return {entry["local_path"]: entry["sha256"] for entry in manifest["retained_sources"]}


def build():
    pins = source_pins()
    roots, simple, supports = geometry()
    rows, code = decoder(roots, simple)
    capacities, thresholds, census, witnesses = flat_census(roots, supports, code)
    union_hist = Counter((a | b).bit_count() for a, b in combinations(code[1:], 2))
    require(min(union_hist) == 84, "two-reader minimum union")
    require(sum(union_hist.values()) == 130305, "complete distinct-reader pair census")
    pair_witness = next((a, b) for a, b in combinations(code[1:], 2) if (a | b).bit_count() == 84)
    bounds = []
    for p in range(56):
        cost, a, b = pair_bound(p, capacities, thresholds)
        # PR631 supplies the sharper bound for p<=8, replayed by the pinned
        # predecessor verifier and proved in its retained README.
        combined = max(cost, 72 - p) if p <= 8 else cost
        ratio = Fraction(combined, 120 - p)
        require(ratio >= Fraction(63, 111), "star ratio exclusion")
        require(ratio > Fraction(63, 111) or p == 9, "strictness away from nine punctures")
        bounds.append({"punctures": p, "relaxed_pair_cost": cost, "minimizing_ranks": [a] + [b] * 8,
                       "combined_lower_bound": combined, "ratio_lower_bound": str(ratio)})
    controls = negative_controls(capacities, thresholds)
    require(binary_basis([pair_witness[0], pair_witness[0]]) == [pair_witness[0]],
            "dependent pair boundary")
    require(pair_witness[0].bit_count() < 84, "distinct-pair hypothesis is necessary")
    # Verify the rank-loss stopping boundary explicitly.
    first_reader = next(w for w in code if w.bit_count() == 56)
    deleted_roots = [i for i in range(120) if first_reader >> i & 1]
    live_rows = [r & ~first_reader for r in rows]
    require(len(binary_basis(live_rows)) == 8, "56-puncture rank-loss boundary")
    independent_summary = {
        "flat_capacities": capacities,
        "single_reader_thresholds": thresholds,
        "reader_weight_histogram": {str(k): v for k, v in sorted(Counter(w.bit_count() for w in code).items())},
        "pair_union_minimum": 84,
        "rank_invoice_minima_36_through_55": [row["relaxed_pair_cost"] for row in bounds[36:]],
    }
    return {"schema": 1, "scope": "real E8 root-only star reader cost; no new kappa",
            "base_commit": "91a2094f2e022930069e8cfdc810a3ea1b81cd09", "assignment_seed": 46,
            "source_sha256": pins, "independent_summary": independent_summary,
            "single_reader_thresholds": thresholds, "flat_census": census,
            "threshold_witnesses": witnesses,
            "pair_union_histogram": {str(k): v for k, v in sorted(union_hist.items())},
            "minimum_pair_witness": [str(x) for x in pair_witness],
            "bounds": bounds, "negative_controls": controls,
            "rank_loss_boundary": {"punctures": deleted_roots, "live_label_rank": 8},
            "coverage": {"standard_flats": 256, "nonzero_readers": 511,
                         "distinct_reader_pairs": 130305, "puncture_budgets": 56,
                         "Weyl_generators": 8, "random_search": False},
            "theorem": "C_star(P)/(120-|P|) >= 63/111 for |P|<=55, with equality possible only at |P|=9"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a regenerated certificate after all checks pass")
    parser.add_argument("--check", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(encoded)
    else:
        require(json.loads(args.check.read_text()) == result, "certificate mismatch")
    print("PASS_E8_JOINT_READER: 256 flats; 511 readers; 130305 pairs; "
          "punctures 0..55; 6 rejection controls; no new kappa")


if __name__ == "__main__":
    main()
