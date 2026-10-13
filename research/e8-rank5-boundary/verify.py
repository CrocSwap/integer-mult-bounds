#!/usr/bin/env python3
"""Exact first rank-five E8 puncture boundary; Python 3.10+, stdlib only.

Philipp (@mightyOil), with substantial OpenAI Codex assistance. Apache-2.0.
Self-contained; imports no predecessor implementation. See README.md for scope.
"""

import argparse
from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONNECTION = [5, 4, 3, 1, 2, 0, 3, 2, 4, 3, 1, 5, 4, 3, 2, 0]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def binary_basis(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return list(pivots.values())


def rational_rank(rows):
    """Integer row operations, dividing content to keep entries small."""
    pivots = {}
    for source in rows:
        row = list(source)
        for p, old in sorted(pivots.items()):
            if row[p]:
                a, b = row[p], old[p]
                row = [b * x - a * y for x, y in zip(row, old)]
                common = gcd(*row)
                if common:
                    row = [x // common for x in row]
        nonzero = next((i for i, x in enumerate(row) if x), None)
        if nonzero is not None:
            pivots[nonzero] = row
        if len(pivots) == 8:
            break
    return len(pivots)


def inverse(matrix):
    n = len(matrix)
    a = [[Fraction(x) for x in row] +
         [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if a[i][j])
        a[j], a[pivot] = a[pivot], a[j]
        divisor = a[j][j]
        a[j] = [x / divisor for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [x - factor * y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def geometry(fault=None):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            roots.append(tuple(r))
    roots.extend((1,) + signs for signs in product((-1, 1), repeat=7)
                 if sum(s < 0 for s in signs) % 2 == 0)
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        r = [0] * 8
        r[i], r[i + 1] = -2, 2
        simple.append(tuple(r))
    if fault == "root":
        roots[0] = (3,) + roots[0][1:]
    require(len(set(roots)) == 120 and all(dot(r, r) == 8 for r in roots),
            "root geometry")
    require(all(dot(x, y) % 4 == 0 for x in roots for y in roots), "Gram integrality")
    inv = inverse(simple)
    supports = []
    for r in roots:
        coefficients = [sum(r[i] * inv[i][j] for i in range(8)) for j in range(8)]
        require(all(c.denominator == 1 for c in coefficients), "simple integrality")
        require(all(c >= 0 for c in coefficients) or all(c <= 0 for c in coefficients),
                "simple positivity")
        supports.append(sum(1 << j for j, c in enumerate(coefficients) if c))
    rows = [sum(((1 + dot(x, y) // 4) % 2) << i for i, y in enumerate(roots))
            for x in roots]
    if fault == "decoder":
        rows[0] ^= 1
    basis = binary_basis(rows)
    require(len(basis) == 9, "binary dimension")
    code = [0]
    for row in basis:
        code += [x ^ row for x in code]
    code.sort()
    require(Counter(x.bit_count() for x in code[1:]) == {56: 255, 64: 255, 120: 1},
            "reader weights")
    lookup = {r: i for i, r in enumerate(roots)}
    lookup.update({tuple(-v for v in r): i for i, r in enumerate(roots)})
    permutations = []
    for a in simple:
        perm = [lookup[tuple(x - dot(r, a) // 4 * y for x, y in zip(r, a))]
                for r in roots]
        require(sorted(perm) == list(range(120)), "reflection permutation")
        require({transport(x, perm) for x in code} == set(code), "reader equivariance")
        permutations.append(perm)
    return roots, supports, code, permutations


def transport(mask, permutation):
    return sum(1 << permutation[i] for i in indices(mask))


def analyze_puncture(roots, code, puncture):
    weights = {word: rational_rank(roots[i] for i in indices(word & ~puncture))
               for word in code[1:]}
    live_rank = len(binary_basis(word & ~puncture for word in code[1:]))
    require(live_rank == 9, "live binary dimension")
    threshold_ranks = [len(binary_basis(word for word, w in weights.items() if w <= k))
                       for k in range(8)]
    chosen, basis_cost = [], 0
    for word in sorted(weights, key=lambda word: (weights[word], word)):
        if len(binary_basis(chosen + [word])) > len(chosen):
            chosen.append(word)
            basis_cost += weights[word]
        if len(chosen) == 9:
            break
    require(basis_cost == sum(9 - r for r in threshold_ranks), "basis cost identity")
    return ({"deleted_root_indices": list(indices(puncture)),
             "reader_rank_histogram": {str(k): v for k, v in sorted(Counter(weights.values()).items())},
             "cheap_rank_by_threshold": threshold_ranks, "star_cost": basis_cost},
            weights, chosen)


def price_basis(readers, weights):
    require(len(readers) == 9 and len(binary_basis(readers)) == 9,
            "decoder basis does not span nine dimensions")
    return sum(weights[r] for r in readers)


def census(fault=None):
    roots, supports, code, permutations = geometry(fault)
    minima, equalities = [], []
    for dimension in range(8):
        best = 120
        for subset in combinations(range(8), dimension):
            simple_mask = sum(1 << i for i in subset)
            flat = sum(1 << i for i, support in enumerate(supports) if not support & ~simple_mask)
            if fault == "flat" and dimension == 5:
                flat |= 1 << next(i for i in range(120) if not flat >> i & 1)
            require(rational_rank(roots[i] for i in indices(flat)) == dimension, "flat dimension")
            for word in code[1:]:
                deleted = word & ~flat
                count = deleted.bit_count()
                best = min(best, count)
                if dimension == 5 and count == 36:
                    require(rational_rank(roots[i] for i in indices(word & flat)) == 5,
                            "equality reader dimension")
                    equalities.append({"simple_indices": list(subset),
                                       "reader_root_indices": list(indices(word)),
                                       "deleted_root_indices": list(indices(deleted))})
        minima.append(best)
    require(minima == [56, 55, 53, 50, 44, 36, 26, 1], "rank-loss thresholds")
    require(len(equalities) == 2, "equality count")
    punctures = sorted({sum(1 << i for i in e["deleted_root_indices"]) for e in equalities})
    records, witnesses, restored = [], [], 0
    for p in punctures:
        record, weights, chosen = analyze_puncture(roots, code, p)
        require(record["reader_rank_histogram"] == {"5": 1, "7": 42, "8": 468}, "reader rank histogram")
        require(record["cheap_rank_by_threshold"] == [0, 0, 0, 0, 0, 1, 1, 8], "cheap span ranks")
        require(record["star_cost"] == 62, "star cost")
        require(price_basis(chosen, weights) == 62, "explicit basis invoice")
        special = next(word for word, cost in weights.items() if cost == 5)
        for i in indices(p):
            require(rational_rank(roots[j] for j in indices((special & ~p) | (1 << i))) == 6,
                    "single-port restoration")
            restored += 1
        records.append(record)
        witnesses.append({"deleted_root_indices": list(indices(p)),
                          "basis_reader_root_indices": [list(indices(c)) for c in chosen],
                          "basis_reader_ranks": [weights[c] for c in chosen]})
    # The explicit path uses the order of the two standard-flat equality rows.
    first, second = [sum(1 << i for i in e["deleted_root_indices"]) for e in equalities]
    moved = first
    for generator in CONNECTION:
        moved = transport(moved, permutations[generator])
    require(moved == second, "conjugacy word")
    seen, queue = {first}, deque([first])
    while queue:
        p = queue.popleft()
        for perm in permutations:
            image = transport(p, perm)
            if image not in seen:
                seen.add(image)
                queue.append(image)
        require(len(seen) <= 7560, "orbit exceeds certificate")
    require(len(seen) == 7560 and second in seen, "closed equality orbit")
    require(all(p.bit_count() == 36 for p in seen), "orbit puncture sizes")
    require(Fraction(54, 84) > Fraction(63, 111), "generic ratio exclusion")
    require(Fraction(62, 84) > Fraction(63, 111), "equality ratio exclusion")
    summary = {"binary_dimension": 9,
               "reader_weight_histogram": {"56": 255, "64": 255, "120": 1},
               "flat_count": 56, "pairs_tested": 56 * 511, "minimum_deletions": 36,
               "equality_pairs": sorted(equalities, key=lambda e: (e["simple_indices"], e["reader_root_indices"])),
               "punctures": sorted(records, key=lambda e: e["deleted_root_indices"])}
    return {"schema": "e8-rank5-boundary-v1", "independent_summary": summary,
            "rank_loss_thresholds": minima, "all_flat_reader_pairs": 255 * 511,
            "equality_orbit_size": len(seen), "conjugacy_generators": CONNECTION,
            "orbit_sha256": sha256(b"".join(p.to_bytes(15, "big") for p in sorted(seen))).hexdigest(),
            "basis_witnesses": witnesses, "single_port_restoration_controls": restored,
            "generic_ratio_lower_bound": "9/14", "equality_ratio": "31/42",
            "comparison_ratio": "21/37"}


def check_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for relative, pin in manifest["files"].items():
        require(sha256((HERE / relative).read_bytes()).hexdigest() == pin["sha256"],
                "predecessor source hash: " + relative)
    return {path: pin["sha256"] for path, pin in manifest["files"].items()}


def negative_controls():
    controls = []
    for fault, message in [("root", "root geometry"), ("decoder", "binary dimension"),
                           ("flat", "flat dimension")]:
        try:
            census(fault)
        except ValueError as error:
            require(message in str(error), "wrong rejection for " + fault)
            controls.append(fault)
        else:
            raise ValueError("accepted corruption: " + fault)
    # Nine DISTINCT cheap readers appear to cost 61, but span only eight
    # binary dimensions. The ninth, rank-eight reader cannot be omitted.
    roots, _, code, _ = geometry()
    puncture = int("ffffcfc3f03f00", 16)
    _, weights, chosen = analyze_puncture(roots, code, puncture)
    cheap = [reader for reader in chosen if weights[reader] <= 7]
    cheap.append(next(reader for reader in code[1:]
                      if weights[reader] == 7 and reader not in cheap))
    require(len(set(cheap)) == 9 and sum(weights[r] for r in cheap) == 61,
            "cost-61 control setup")
    try:
        price_basis(cheap, weights)
    except ValueError as error:
        require("does not span nine" in str(error), "wrong cheap-basis rejection")
    else:
        raise ValueError("accepted cost-61 nondecoder")
    controls.append("distinct-cost-61-nonspanning-readers")
    # Rank must be rational: in characteristic two these doubled roots can vanish.
    require(rational_rank([(2, 0), (0, 2)]) == 2 and
            len(binary_basis([0, 0])) == 0, "wrong-characteristic control")
    controls.append("wrong-characteristic")
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--write", type=Path, help="write a fresh receipt instead of comparing one")
    args = parser.parse_args()
    result = census()
    result["predecessor_sources"] = check_sources()
    result["negative_controls"] = negative_controls()
    if args.write is not None:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(args.check.read_text()) == result, "certificate mismatch")
    print("PASS_E8_RANK5_BOUNDARY: 28616 rank-five pairs; 2 representatives; "
          "7560 conjugate punctures; cost 62; 72 restorations; 5 negative controls; no new kappa")


if __name__ == "__main__":
    main()
