#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact certificate for the P112 masked root-star assembly floor.

No predecessor code is imported. Coordinates are doubled E8 roots, with the
first nonzero coordinate positive, sorted lexicographically. All arithmetic is
integer/F2. Default replay is read-only; --write explicitly replaces the receipt.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"),
                                    sort_keys=True).encode()).hexdigest()


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask_of(values):
    return sum(1 << value for value in values)


def make_roots():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    for tail in product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            roots.append((1,) + tail)
    return tuple(sorted(roots))


def inner_products(roots):
    require(len(roots) == 120 and len(set(roots)) == 120, "120 distinct root lines")
    require(all(len(r) == 8 and sum(x*x for x in r) == 8 for r in roots),
            "doubled roots must have squared norm 8")
    result = []
    for r in roots:
        dots = [sum(x*y for x, y in zip(r, s)) for s in roots]
        require(all(dot % 4 == 0 for dot in dots), "integral root inner products")
        result.append(tuple(dot // 4 for dot in dots))
    require(all(result[i][j] in (-1, 0, 1) for i in range(120)
                for j in range(120) if i != j), "distinct root inner products")
    return tuple(result)


def coordinate_frame(roots):
    frame = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[i+1] = 2, 2 * sign
            frame.append(roots.index(tuple(root)))
    return tuple(sorted(frame))


def f2_rank(rows):
    pivots = {}
    for row in rows:
        require(isinstance(row, int) and row >= 0, "nonnegative F2 bit rows")
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def pairing_rank(label_rows, row_mask, column_mask):
    return f2_rank(label_rows[i] & column_mask for i in indices(row_mask))


def enumerate_cliques(adjacency, vertices):
    """Enumerate all cliques exactly once, retaining the complete size census."""
    counts = Counter()
    maximum = ()

    def visit(chosen, remaining):
        nonlocal maximum
        counts[len(chosen)] += 1
        if len(chosen) > len(maximum):
            maximum = chosen
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            vertex = bit.bit_length() - 1
            visit(chosen + (vertex,), remaining & adjacency[vertex])
    visit((), vertices)
    return counts, maximum


def enumerate_frames(adjacency, live):
    frames = []

    def visit(chosen, remaining):
        if len(chosen) == 8:
            frames.append(chosen)
            return
        if remaining.bit_count() < 8 - len(chosen):
            return
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            vertex = bit.bit_length() - 1
            visit(chosen + (vertex,), remaining & adjacency[vertex])
    visit((), live)
    return tuple(frames)


def frame_incidence(frames, live, ip):
    through = [0] * 120
    pair_counts = Counter()
    for number, frame in enumerate(frames):
        require(len(frame) == 8 and len(set(frame)) == 8, "eight distinct frame lines")
        require(all(ip[i][j] == 0 for i, j in combinations(frame, 2)),
                "frame lines must be orthogonal")
        for vertex in frame:
            through[vertex] |= 1 << number
        pair_counts.update(combinations(frame, 2))
    for i, j in combinations(indices(live), 2):
        if ip[i][j] == 0:
            require(pair_counts[i, j] > 0, "orthogonal live pair lacks a live frame")
    return through, pair_counts


def disjoint_misses(masks):
    used = 0
    for mask in masks:
        if used & mask:
            return False
        used |= mask
    return True


def reject(action, name):
    try:
        action()
    except VerificationError:
        return name
    raise VerificationError("negative control was accepted: " + name)


def compute_certificate():
    roots = make_roots()
    ip = inner_products(roots)
    puncture = coordinate_frame(roots)
    live = ((1 << 120) - 1) ^ mask_of(puncture)
    live_ids = tuple(indices(live))
    label_rows = tuple(mask_of(j for j in range(120) if (ip[i][j]+1) % 2)
                       for i in range(120))
    orth = tuple(mask_of(j for j in live_ids if i != j and ip[i][j] == 0)
                 for i in range(120))
    odd = tuple(mask_of(j for j in live_ids if i != j and ip[i][j] % 2)
                for i in range(120))
    frames = enumerate_frames(orth, live)
    require(len(frames) == 1260, "complete P112 frame census")
    frame_masks = tuple(mask_of(frame) for frame in frames)
    through, pair_counts = frame_incidence(frames, live, ip)
    require({through[i].bit_count() for i in live_ids} == {90}, "90 frames per live line")
    supports, misses = [], []
    for normal in range(120):
        for trimmed in (False, True):
            support = mask_of(i for i in live_ids if ip[i][normal] != 0
                              and not (trimmed and i == normal))
            missing = mask_of(k for k, frame in enumerate(frame_masks) if not support & frame)
            expected = through[normal] if trimmed and normal in live_ids else 0
            require(missing == expected, "star misses exactly the frames through its trimmed root")
            supports.append((normal, trimmed, support))
            misses.append(missing)

    ranks, cheap_misses, cheap_endpoints = Counter(), Counter(), Counter()
    atom_rows = []
    for a, (alpha, trim_a, rows) in enumerate(supports):
        for b, (beta, trim_b, cols) in enumerate(supports):
            rank = pairing_rank(label_rows, rows, cols)
            reduced_a = trim_a or alpha in puncture
            reduced_b = trim_b or beta in puncture
            expected_rank = (7 if ip[alpha][beta] % 2 else 8) if reduced_a and reduced_b else (
                8 if reduced_a or reduced_b else 9)
            require(rank == expected_rank, "root-star pairing rank classification")
            ranks[rank] += 1
            atom_rows.append((a, b, rank, (misses[a] | misses[b]).bit_count()))
            if rank == 7:
                endpoints = {v for v in (alpha, beta) if v in live_ids}
                require(endpoints, "cheap atom must have a live endpoint")
                missing = misses[a] | misses[b]
                require(all(missing & through[v] == through[v] for v in endpoints),
                        "cheap atom misses every frame through each live endpoint")
                cheap_misses[missing.bit_count()] += 1
                cheap_endpoints[len(endpoints)] += 1
    require(ranks == {7: 7616, 8: 37440, 9: 12544}, "complete 57,600 atom census")
    clique_counts, clique = enumerate_cliques(odd, live)
    require(len(clique) == 8 and max(clique_counts) == 8, "no nine pairwise-odd live roots")

    coordinate_supports = [mask_of(i for i in live_ids if ip[i][f]) for f in puncture]
    coordinate_costs = [pairing_rank(label_rows, support, support) for support in coordinate_supports]
    for i in live_ids:
        for j in live_ids:
            actual = sum(ip[i][f] * ip[j][f] for f in puncture)
            require(actual == 2 * ip[i][j], "sharp coordinate decoder on every pair")
    require(coordinate_costs == [8] * 8, "sharp decoder cost 64")
    controls = []
    broken_roots = list(roots)
    broken_roots[0] = tuple(2*x for x in broken_roots[0])
    controls.append(reject(lambda: inner_products(broken_roots), "wrong_root_norm"))
    controls.append(reject(lambda: require(f2_rank([3, 3]) == 2, "dependent F2 rows"),
                           "rank_counts_rows_instead_of_pivots"))
    wrong_labels = tuple(mask_of(j for j in range(120) if ip[i][j] % 2) for i in range(120))
    first_frame = frame_masks[0]
    require(pairing_rank(label_rows, first_frame, first_frame) == 1,
            "correct label pairing on a frame has rank one")
    controls.append(reject(lambda: require(pairing_rank(wrong_labels, first_frame, first_frame) == 1,
                                          "wrong label pairing on a frame"), "omit_pairing_plus_one"))
    pair = next(iter(pair_counts))
    deleted = tuple(frame for frame in frames if not set(pair) <= set(frame))
    controls.append(reject(lambda: frame_incidence(deleted, live, ip), "remove_all_extensions_of_pair"))
    controls.append(reject(lambda: require(disjoint_misses([through[pair[0]], through[pair[1]]]),
                                          "shared missing frame"), "orthogonal_endpoint_pair"))
    controls.append(reject(lambda: require(disjoint_misses([through[live_ids[0]]]*2),
                                          "duplicate missing frame"), "repeated_endpoint"))
    complete9 = tuple(((1 << 9)-1) ^ (1 << i) for i in range(9))
    controls.append(reject(lambda: require(max(enumerate_cliques(complete9, (1 << 9)-1)[0]) <= 8,
                                          "nine-clique fixture"), "injected_nine_clique"))
    controls.append(reject(lambda: require(all(sum(ip[i][f]**2 for f in puncture[:-1]) == 4
                                              for i in live_ids), "omitted decoder term"),
                           "omit_coordinate_term"))
    return {
        "schema": 1, "result": "SHARP_MASKED_ROOT_STAR_ASSEMBLY_FLOOR_64",
        "model": {"root_lines": 120, "live_lines": 112, "root_sha256": digest(roots),
                  "punctured_frame_indices": puncture, "field": "R or C, ordinary transpose",
                  "support_masks_sha256": digest(supports)},
        "frames": {"count": len(frames), "sha256": digest(frames), "per_live_line": 90,
                   "orthogonal_pair_frame_multiplicities": dict(sorted(Counter(pair_counts.values()).items()))},
        "atoms": {"ordered_support_pairs": len(atom_rows), "rank_histogram": dict(sorted(ranks.items())),
                  "sha256": digest(atom_rows), "beta7_missed_frame_histogram": dict(sorted(cheap_misses.items())),
                  "beta7_live_endpoint_histogram": dict(sorted(cheap_endpoints.items()))},
        "odd_graph": {"vertices": 112, "degrees": sorted({odd[i].bit_count() for i in live_ids}),
                      "clique_census": dict(sorted(clique_counts.items())),
                      "maximum_clique_indices": clique, "maximum_clique_roots": [roots[i] for i in clique]},
        "sharp_decoder": {"terms": 8, "costs": coordinate_costs, "cost": sum(coordinate_costs),
                          "checked_all_pairs": 112**2, "support_sizes": [s.bit_count() for s in coordinate_supports]},
        "assembly_cases": {"fewer_than_8_terms": "rank obstruction",
                           "8_terms_with_beta7": "a frame has at most 7 active terms",
                           "9_terms_below_64": "nine beta7 atoms require a forbidden nine-clique",
                           "at_least_10_terms": "cost at least 70"},
        "negative_controls": controls,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate CERTIFICATE.json")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args(argv)
    try:
        certificate = compute_certificate()
        encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        if args.write:
            args.certificate.write_text(encoded, encoding="utf-8")
        else:
            expected = json.loads(args.certificate.read_text(encoding="utf-8"))
            require(json.loads(encoded) == expected, "certificate differs from exact recomputation")
        print("PASS_MASKED_ROOT_STAR_ASSEMBLY_FLOOR_64 atoms=57600 frames=1260 max_odd_clique=8 controls=8")
        return 0
    except (VerificationError, OSError, ValueError) as error:
        print("FAIL_MASKED_ROOT_STAR_ASSEMBLY: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
