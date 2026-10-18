#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate norm-lattice enumeration, row-span ranks and maximal-clique check.

Does not import verify.py. Uses set-based pivoted Bron--Kerbosch, rather than
ordered bitset target-clique search. Same author/AI assistance as the package;
this is a second implementation, not independent human review.
"""
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

AUDITED_COMMIT = "ee8437bd9879272094e20c024cd34a53c4e84cd8"
REFERENCE_SHA256 = "181eddec639da62417f4176fe275d091e243766c5df69ebb35a19482b8155019"


def check(ok, message):
    if not ok:
        raise ValueError(message)


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def row_basis(rows):
    """Lowest-bit pivot basis, used before restricting the column support."""
    result = {}
    for row in rows:
        while row:
            pivot = row & -row
            if pivot not in result:
                result[pivot] = row
                break
            row ^= result[pivot]
    return list(result.values())


def maximal_cliques(neighbors):
    result = []

    def visit(current, candidates, excluded):
        if not candidates and not excluded:
            result.append(tuple(sorted(current)))
            return
        pivot = max(candidates | excluded,
                    key=lambda v: (len(candidates & neighbors[v]), -v))
        for vertex in sorted(candidates - neighbors[pivot]):
            visit(current | {vertex}, candidates & neighbors[vertex], excluded & neighbors[vertex])
            candidates.remove(vertex)
            excluded.add(vertex)

    visit(set(), set(range(len(neighbors))), set())
    return sorted(result)


def clique_counts_from_maximal(maximal):
    """Every finite clique is contained in a maximal clique; deduplicate deletions."""
    levels = {k: set() for k in range(1 + max(map(len, maximal)))}
    for clique in maximal:
        levels[len(clique)].add(clique)
    for size in range(max(levels), 0, -1):
        for clique in levels[size]:
            for i in range(size):
                levels[size - 1].add(clique[:i] + clique[i + 1:])
    return {str(k): len(value) for k, value in sorted(levels.items())}


def compare_reference(reference, sections):
    """Compare the named recomputed sections, including every per-atom hash."""
    for key, actual in sections.items():
        check(json.dumps(actual, sort_keys=True) == json.dumps(reference[key], sort_keys=True),
              "PR1236 semantic mismatch: " + key)


def read_reference(package):
    reference_bytes = (package / "reference" / "PR1236-CERTIFICATE.json").read_bytes()
    manifest = json.loads((package / "SOURCES.json").read_text())
    pin = manifest["audited_receipt"]
    check(pin["commit"] == AUDITED_COMMIT and pin["sha256"] == REFERENCE_SHA256,
          "PR1236 audit target was repinned")
    check(hashlib.sha256(reference_bytes).hexdigest() == REFERENCE_SHA256, "PR1236 receipt source pin")
    blob = b"blob " + str(len(reference_bytes)).encode() + b"\0" + reference_bytes
    check(hashlib.sha1(blob).hexdigest() == pin["git_blob"], "PR1236 receipt Git blob")
    return json.loads(reference_bytes)


def main():
    receipt = json.loads((Path(__file__).parent / "CERTIFICATE.json").read_text())
    # The doubled E8 lattice has uniform coordinate parity and sum divisible by
    # four. A norm-eight vector is automatically in this finite coordinate box.
    roots = []
    for row in product(range(-2, 3), repeat=8):
        if sum(x * x for x in row) != 8 or sum(row) % 4:
            continue
        if len({x % 2 for x in row}) != 1:
            continue
        if next(x for x in row if x) > 0:
            roots.append(row)
    roots.sort()
    check(len(roots) == 120, "norm-lattice root count")
    check(fingerprint(roots) == receipt["geometry"]["root_lines_sha256"], "root representatives")
    puncture = set()
    for start in (0, 2, 4, 6):
        for sign in (2, -2):
            row = [0] * 8
            row[start], row[start + 1] = 2, sign
            puncture.add(tuple(row))
    live = [r for r in roots if r not in puncture]
    check(len(live) == 112, "puncture count")
    gram = [[sum(x * y for x, y in zip(a, b)) for b in live] for a in live]
    even_neighbors = [{j for j in range(112) if j != i and gram[i][j] == 0}
                      for i in range(112)]
    odd_neighbors = [{j for j in range(112) if j != i and abs(gram[i][j]) == 4}
                     for i in range(112)]
    orthogonal = maximal_cliques(even_neighbors)
    check(max(map(len, orthogonal)) == 8, "orthogonal clique maximum")
    frames = [c for c in orthogonal if len(c) == 8]
    check(len(frames) == 1260, "independent frame count")
    check(fingerprint(frames) == receipt["geometry"]["frames_sha256"], "independent frame stream")
    incidence = [{f for f, frame in enumerate(frames) if i in frame} for i in range(112)]
    check({len(fs) for fs in incidence} == {90}, "independent incidence count")
    pair_hist = Counter()
    for i, j in combinations(range(112), 2):
        common = incidence[i] & incidence[j]
        check(bool(common) == (gram[i][j] == 0), "pair completion")
        pair_hist[len(common)] += 1
    check({str(k): v for k, v in pair_hist.items()} ==
          receipt["geometry"]["pair_frame_count_histogram"], "pair-frame census")
    nonorthogonal = maximal_cliques(odd_neighbors)
    histogram = Counter(map(len, nonorthogonal))
    check(max(histogram) == 8, "independent compatibility maximum")
    all_clique_counts = clique_counts_from_maximal(nonorthogonal)
    witness = receipt["compatibility"]["eight_clique_live_indices"]
    check(len(set(witness)) == 8 and all(j in odd_neighbors[i] for i, j in combinations(witness, 2)),
          "committed sharpness witness")

    label_rows = [sum(((gram[i][j] // 4 + 1) % 2) << j for j in range(112)) for i in range(112)]
    masks = []
    for root in roots:
        mask = sum(1 << i for i, row in enumerate(live) if sum(x * y for x, y in zip(root, row)))
        masks.extend((mask, mask & ~(1 << live.index(root)) if root in live else mask))
    # Taking the row span first and then restricting columns preserves the rank
    # of every submatrix. This avoids the primary checker's full-row elimination.
    bases = [row_basis(label_rows[i] for i in range(112) if mask >> i & 1) for mask in masks]
    rank_list = [len(row_basis(row & col_mask for row in basis))
                 for basis in bases for col_mask in masks]
    ranks = Counter(rank_list)
    check({str(k): v for k, v in ranks.items()} == receipt["atoms"]["pairing_rank_histogram"],
          "independent row-span pairing census")
    check(fingerprint(rank_list) == receipt["atoms"]["pairing_ranks_sha256"],
          "ordered per-atom rank stream")

    # Source binding added after discovery of concurrent PR1236. The geometry,
    # rank and maximal-clique algorithms above were written before reading it.
    reference = read_reference(Path(__file__).parent)
    check(reference["schema"] == 1 and reference["result"] == "SHARP_MASKED_ROOT_STAR_ASSEMBLY_FLOOR_64",
          "PR1236 schema/result identity")
    global_live = [roots.index(root) for root in live]
    global_frames = [tuple(global_live[i] for i in frame) for frame in frames]
    global_supports = [(i // 2, bool(i % 2), sum(1 << global_live[j] for j in range(112) if mask >> j & 1))
                       for i, mask in enumerate(masks)]
    missing = [{f for f, frame in enumerate(frames) if not any(mask >> i & 1 for i in frame)}
               for mask in masks]
    atom_rows, missed_hist, endpoint_hist = [], Counter(), Counter()
    for i in range(240):
        for j in range(240):
            beta = rank_list[240 * i + j]
            misses = len(missing[i] | missing[j])
            atom_rows.append((i, j, beta, misses))
            if beta == 7:
                missed_hist[misses] += 1
                endpoint_hist[len({i // 2, j // 2} & set(global_live))] += 1
    vectors = [[sum(x * y for x, y in zip(root, normal)) // 4 for root in live]
               for normal in sorted(puncture)]
    check(all(sum(vector[i] * vector[j] for vector in vectors) == gram[i][j] // 2
              for i in range(112) for j in range(112)), "independent coordinate identity")
    coordinate_masks = [sum(1 << i for i, value in enumerate(vector) if value) for vector in vectors]
    coordinate_costs = [len(row_basis(label_rows[i] & mask for i in range(112) if mask >> i & 1))
                        for mask in coordinate_masks]
    compare_reference(reference, {
        "model": {"root_lines": len(roots), "live_lines": len(live), "root_sha256": fingerprint(roots),
                  "punctured_frame_indices": sorted(roots.index(r) for r in puncture),
                  "field": "R or C, ordinary transpose", "support_masks_sha256": fingerprint(global_supports)},
        "frames": {"count": len(frames), "sha256": fingerprint(global_frames), "per_live_line": 90,
                   "orthogonal_pair_frame_multiplicities": {str(k): value for k, value in pair_hist.items() if k}},
        "atoms": {"ordered_support_pairs": len(atom_rows), "rank_histogram": {str(k): value for k, value in ranks.items()},
                  "sha256": fingerprint(atom_rows),
                  "beta7_missed_frame_histogram": {str(k): value for k, value in missed_hist.items()},
                  "beta7_live_endpoint_histogram": {str(k): value for k, value in endpoint_hist.items()}},
        "sharp_decoder": {"terms": len(vectors), "costs": coordinate_costs, "cost": sum(coordinate_costs),
                          "checked_all_pairs": len(live) ** 2, "support_sizes": [mask.bit_count() for mask in coordinate_masks]},
    })
    odd = reference["odd_graph"]
    check(odd["vertices"] == len(live) and odd["degrees"] == sorted({len(s) for s in odd_neighbors}),
          "PR1236 graph dimensions")
    check(odd["clique_census"] == all_clique_counts, "PR1236 full clique census from maximal closure")
    original_witness = odd["maximum_clique_indices"]
    check(len(set(original_witness)) == 8 and all(i in global_live for i in original_witness),
          "PR1236 witness membership")
    check(all(global_live.index(j) in odd_neighbors[global_live.index(i)]
              for i, j in combinations(original_witness, 2)), "PR1236 witness edges")
    check(odd["maximum_clique_roots"] == [list(roots[i]) for i in original_witness],
          "PR1236 witness root binding")
    # Exercise the pivot algorithm on an actual nine-clique: a false constant
    # upper-bound implementation would fail this positive adversarial fixture.
    complete_nine = [set(range(9)) - {i} for i in range(9)]
    check(maximal_cliques(complete_nine) == [tuple(range(9))], "K9 positive control")
    print("PASS_INDEPENDENT_ROOT_STAR_PREMISES")
    print("maximal compatibility cliques by size: " + json.dumps(dict(sorted(histogram.items()))))
    print("All 57600 pairing ranks and all 1260 frames agree; compatibility maximum 8.")
    print("PASS_PR1236_SOURCE_BOUND_AUDIT: geometry, frames, atoms, full clique census, witness and sharp decoder")


if __name__ == "__main__":
    main()
