#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite premises for the P112 masked root-star cost floor.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
See README.md for the written argument, scope and predecessor credit.
No predecessor executable is imported. Python 3.10+, standard library.
"""

import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def model():
    # Twice the usual norm-two roots; choose the first nonzero coordinate positive.
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            v = [0] * 8
            v[i], v[j] = 2, 2 * sign
            roots.add(tuple(v))
    for tail in product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            roots.add((1,) + tail)
    roots = sorted(roots)
    require(len(roots) == 120, "root-line count")
    gram = []
    for r in roots:
        row = []
        for s in roots:
            q, rem = divmod(sum(x * y for x, y in zip(r, s)), 4)
            require(rem == 0, "nonintegral root pairing")
            row.append(q)
        gram.append(row)
    puncture = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            v = [0] * 8
            v[i], v[i + 1] = 2, 2 * sign
            puncture.append(roots.index(tuple(v)))
    puncture.sort()
    live = [i for i in range(120) if i not in puncture]
    require(all(gram[i][i] == 2 for i in range(120)), "root norms")
    require(all(gram[i][j] == 0 for i, j in combinations(puncture, 2)), "punctured frame")
    return roots, gram, puncture, live


def clique_census(adjacency, vertices, collect_size=None):
    """Enumerate *all* cliques, with no depth cutoff; visit each in increasing order."""
    counts = Counter()
    witness = []
    collected = []

    def visit(chosen, candidates):
        nonlocal witness
        counts[len(chosen)] += 1
        if len(chosen) > len(witness):
            witness = chosen
        if len(chosen) == collect_size:
            collected.append(chosen)
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            v = bit.bit_length() - 1
            visit(chosen + [v], candidates & adjacency[v])

    visit([], sum(1 << i for i in vertices))
    return counts, witness, collected


def check_decoder(gram, live, left, right):
    return all(sum(d[i] * t[j] for d, t in zip(left, right)) == 2 * gram[i][j]
               for i in live for j in live)


def compute():
    roots, gram, puncture, live = model()
    label_rows = [sum(((g + 1) % 2) << j for j, g in enumerate(row)) for row in gram]
    require(rank2(label_rows) == 9, "label rank")
    orth = {i: sum(1 << j for j in live if i != j and gram[i][j] == 0) for i in live}
    nonorth = {i: sum(1 << j for j in live if i != j and gram[i][j] != 0) for i in live}
    _, _, frames = clique_census(orth, live, 8)
    require(len(frames) == 1260, "frame census")
    frame_masks = [sum(1 << i for i in f) for f in frames]
    appearances = Counter(i for f in frames for i in f)
    extensions = Counter(pair for f in frames for pair in combinations(f, 2))
    require(set(appearances.values()) == {90}, "every live normal must lie in a frame")
    require(set(extensions) == {(i, j) for i, j in combinations(live, 2) if gram[i][j] == 0},
            "an orthogonal pair has no live-frame extension")

    supports = []
    zeros = []
    for normal in range(120):
        untrimmed = sum(1 << i for i in live if gram[i][normal] != 0)
        for trimmed in (False, True):
            support = untrimmed & ~(1 << normal) if trimmed else untrimmed
            supports.append((normal, trimmed, support))
            zero = [k for k, fm in enumerate(frame_masks) if not support & fm]
            expected = [k for k, f in enumerate(frames) if trimmed and normal in f]
            require(zero == expected, "star/frame annihilation classification")
            zeros.append(zero)

    ranks = []
    rank_hist = Counter()
    cheap_types = Counter()
    for a, ta, sa in supports:
        for b, tb, sb in supports:
            beta = rank2(label_rows[i] & sb for i in bits(sa))
            ranks.append(beta)
            rank_hist[beta] += 1
            predicted = (abs(gram[a][b]) == 1 and (ta or a in puncture)
                         and (tb or b in puncture))
            require((beta == 7) == predicted, "rank-seven classification")
            if beta == 7:
                live_normals = [v for v in (a, b) if v in live]
                require(live_normals, "cheap atom without a live trimmed normal")
                cheap_types[len(live_normals)] += 1
    require(dict(rank_hist) == {7: 7616, 8: 37440, 9: 12544}, "atom rank census")

    counts, clique, _ = clique_census(nonorth, live)
    require(max(counts) == 8, "nine pairwise nonorthogonal live normals exist")
    require(all(gram[i][j] != 0 for i, j in combinations(clique, 2)), "clique witness")

    coordinate = [[gram[i][f] for i in range(120)] for f in puncture]
    require(check_decoder(gram, live, coordinate, coordinate), "coordinate decoder identity")
    coordinate_costs = []
    for d in coordinate:
        support = sum(1 << i for i in live if d[i])
        coordinate_costs.append(rank2(label_rows[i] & support for i in bits(support)))
    require(coordinate_costs == [8] * 8, "cost-64 attaining decoder")

    # Failure controls address mathematical boundaries, rather than code formatting.
    controls = []
    damaged = [row[:] for row in coordinate]
    k, i = next((k, i) for k, row in enumerate(damaged) for i in live if row[i])
    damaged[k][i] += 1
    require(not check_decoder(gram, live, damaged, coordinate), "coefficient mutation escaped")
    controls.append("changed_coordinate_coefficient_rejected")
    require(not check_decoder(gram, live, [], []), "zero decoder escaped diagonal constraint")
    controls.append("zero_decoder_rejected_by_diagonal")
    full9 = {i: ((1 << 9) - 1) ^ (1 << i) for i in range(9)}
    nine_counts, nine, _ = clique_census(full9, list(range(9)))
    require(len(nine) == 9 and nine_counts[9] == 1, "clique search silently stops at eight")
    controls.append("synthetic_K9_detected_without_depth_cutoff")
    first = live[0]
    singleton = 1 << first
    require(singleton not in {s for _, _, s in supports}
            and rank2([label_rows[first] & singleton]) == 1, "outside-family boundary")
    controls.append("rank_one_singleton_outside_star_family")
    repeated_frame = next(f for f in frames if first in f)
    require(not (sum(1 << i for i in live if gram[i][first] and i != first)
                 & sum(1 << i for i in repeated_frame)), "repeated normal not annihilated")
    controls.append("repeated_normal_has_shared_zero_frame")
    pair = min(extensions)
    shared = next(f for f in frames if all(i in f for i in pair))
    require(all(not any(gram[i][a] for i in shared if i != a) for a in pair),
            "orthogonal normals not annihilated")
    controls.append("orthogonal_normals_have_shared_zero_frame")
    odd_pair = next((i, j) for i in live for j in live if gram[i][j] % 2)
    require(rank2([label_rows[odd_pair[0]] & (1 << odd_pair[1])]) == 0
            and not any(all(i in f for i in odd_pair) for f in frames), "free odd repair hits frame")
    controls.append("free_odd_entry_patch_vanishes_on_every_frame")

    return {
        "schema": "masked-star-frame-compatibility-v1",
        "scope": "P112; exact C(alpha)/N(alpha) supports; ordinary complex transpose; arbitrary finite term count",
        "lines": 120, "live_lines": 112, "label_rank": 9,
        "roots_sha256": digest(roots), "puncture": puncture,
        "frames": len(frames), "frames_sha256": digest(frames),
        "frames_per_line": 90,
        "orthogonal_pair_extension_histogram": dict(sorted(Counter(extensions.values()).items())),
        "ordered_support_pairs": len(ranks), "support_labels": len(supports),
        "distinct_supports": len({s for _, _, s in supports}),
        "rank_histogram": dict(sorted(rank_hist.items())), "ranks_sha256": digest(ranks),
        "rank7_live_normal_count_histogram": dict(sorted(cheap_types.items())),
        "star_zero_frames_sha256": digest(zeros),
        "nonorthogonal_clique_counts": dict(sorted(counts.items())),
        "maximum_nonorthogonal_clique": len(clique), "maximum_clique_witness": clique,
        "maximum_clique_root_vectors": [roots[i] for i in clique],
        "coordinate_decoder_costs": coordinate_costs, "coordinate_decoder_entries": len(live) ** 2,
        "cost_floor": 64, "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the package certificate")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    try:
        actual = json.loads(json.dumps(compute()))
        if args.write:
            args.certificate.write_text(json.dumps(actual, indent=2) + "\n")
        else:
            require(json.loads(args.certificate.read_text()) == actual,
                    "certificate differs from exact recomputation")
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL_MASKED_STAR_FRAME_COMPATIBILITY: {error}", file=sys.stderr)
        return 1
    print("PASS_MASKED_STAR_FRAME_COMPATIBILITY atoms=57600 frames=1260 max_clique=8 cost_floor=64 controls=7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
