#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate proof-obligation checker; imports neither verify.py nor predecessor code.

Uses directly generated positive roots, squared-distance pairings, low-column
binary elimination, and pivoted maximal-clique enumeration. All cliques are
then recovered as subsets of maximal cliques, independently of the producer's
ordered-prefix census. Hanson Sun (@bbMisk), OpenAI Codex assisted.
"""

import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def indices(value):
    return [i for i in range(value.bit_length()) if value >> i & 1]


def low_rank(rows):
    rows = list(rows)
    rank = 0
    width = max(rows, default=0).bit_length()
    for col in range(width):
        pivot = next((r for r in range(rank, len(rows)) if rows[r] >> col & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(rank + 1, len(rows)):
            if rows[r] >> col & 1:
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def maximal_cliques(adjacency):
    """Bron-Kerbosch with a deterministic pivot; no requested size cutoff."""
    output = []

    def visit(chosen, possible, excluded):
        if not possible and not excluded:
            output.append(chosen)
            return
        union = possible | excluded
        pivot = max(indices(union), key=lambda v: (possible & adjacency[v]).bit_count())
        choices = possible & ~adjacency[pivot]
        while choices:
            bit = choices & -choices
            choices ^= bit
            vertex = bit.bit_length() - 1
            visit(chosen | bit, possible & adjacency[vertex], excluded & adjacency[vertex])
            possible ^= bit
            excluded |= bit

    visit(0, (1 << len(adjacency)) - 1, 0)
    return output


def verify(certificate):
    roots = []
    for a in range(8):
        for b in range(a + 1, 8):
            for sign in (-2, 2):
                vector = [0] * 8
                vector[a], vector[b] = 2, sign
                roots.append(tuple(vector))
    for tail in product((-1, 1), repeat=7):
        if sum(x == -1 for x in tail) % 2 == 0:
            roots.append((1,) + tail)
    roots.sort()
    check(len(set(roots)) == 120, "direct positive root generation")
    gram = []
    for x in roots:
        row = []
        for y in roots:
            distance = sum((a - b) ** 2 for a, b in zip(x, y))
            check(distance % 8 == 0, "root squared-distance integrality")
            row.append(2 - distance // 8)
        gram.append(row)
    puncture = [i for i, root in enumerate(roots) if any(root[2 * k] == 2 and abs(root[2 * k + 1]) == 2 and sum(v != 0 for v in root) == 2 for k in range(4))]
    live = [i for i in range(120) if i not in puncture]
    check(len(puncture) == 8 and len(live) == 112, "puncture inventory")
    position = {normal: i for i, normal in enumerate(live)}
    orth = [sum(1 << j for j, b in enumerate(live) if a != b and gram[a][b] == 0) for a in live]
    nonorth = [sum(1 << j for j, b in enumerate(live) if a != b and gram[a][b] != 0) for a in live]
    s9 = [sum((1 - abs(gram[a][b]) % 2) << j for j, b in enumerate(live)) for a in live]
    check(low_rank(s9) == 9, "binary model rank")

    orth_maximal = maximal_cliques(orth)
    check(max(m.bit_count() for m in orth_maximal) == 8, "orthogonal dimension")
    frames = sorted(tuple(indices(m)) for m in orth_maximal if m.bit_count() == 8)
    check(len(frames) == 1260, "independent complete frames")
    frame_sets = [set(frame) for frame in frames]
    containing = [{k for k, frame in enumerate(frame_sets) if i in frame} for i in range(112)]
    pair_hist = Counter(len(containing[i] & containing[j]) for i in range(112) for j in range(i + 1, 112) if orth[i] >> j & 1)
    check(min(pair_hist) > 0 and {len(x) for x in containing} == {90}, "orthogonal-pair completion")

    support_records = []
    support_indices = []
    miss_sets = []
    for a in range(120):
        for trimmed in (False, True):
            members = [i for i, b in enumerate(live) if gram[a][b] != 0 and not (trimmed and a == b)]
            support_records.append((a, trimmed, sum(1 << i for i in members)))
            support_indices.append(members)
            miss = {k for k, frame in enumerate(frame_sets) if frame.isdisjoint(members)}
            expected = containing[position[a]] if trimmed and a in position else set()
            check(miss == expected, "independent missing-frame support identity")
            miss_sets.append(miss)

    # Direct restricted matrices; deliberately does not use compressed support bases.
    table = []
    for members in support_indices:
        table.append([low_rank(s9[i] & mask for i in members) for _, _, mask in support_records])
    ranks = Counter(rank for row in table for rank in row)
    check(ranks == {7: 7616, 8: 37440, 9: 12544}, "independent atom prices")
    endpoints, hit_counts = Counter(), Counter()
    for i in range(240):
        for j in range(240):
            if table[i][j] == 7:
                live_trimmed = [a for a, trimmed, _ in (support_records[i], support_records[j]) if trimmed and a in position]
                check(live_trimmed, "missing live endpoint on rank-seven atom")
                check(containing[position[live_trimmed[0]]] <= miss_sets[i] | miss_sets[j], "rank-seven endpoint containment")
                endpoints[len(live_trimmed)] += 1
                hit_counts[1260 - len(miss_sets[i] | miss_sets[j])] += 1

    maximal = maximal_cliques(nonorth)
    check(max(m.bit_count() for m in maximal) == 8, "independent maximum clique")
    all_cliques = {0}
    for maximal_mask in maximal:
        subset = maximal_mask
        while subset:
            all_cliques.add(subset)
            subset = (subset - 1) & maximal_mask
    counts = Counter(m.bit_count() for m in all_cliques)
    check(len(all_cliques) == 482577, "independent clique coverage")
    witness = certificate["nonorthogonality"]["witness_live_indices"]
    check(len(witness) == len(set(witness)) == 8, "clique witness size")
    check(all(nonorth[i] >> j & 1 for i, j in combinations(witness, 2)), "clique witness edges")
    check(all(any(orth[v] >> i & 1 for i in witness) for v in range(112) if v not in witness), "all witness extensions")

    decoder = [[gram[a][b] for b in puncture] for a in live]
    check(all(sum(decoder[i][k] * decoder[j][k] for k in range(8)) == 2 * gram[a][b] for i, a in enumerate(live) for j, b in enumerate(live)), "independent all-pairs attainment")
    check([table[2 * b][2 * b] for b in puncture] == [8] * 8, "independent cost 64 attainment")

    model = certificate["model"]
    check(model == {"roots_sha256": sha(roots), "removed_global_indices": puncture, "live_global_indices": live, "binary_pairing_rank": 9, "supports_sha256": sha(support_records), "supports": 240}, "model receipt")
    check(certificate["frames"] == {"count": 1260, "sha256": sha(frames), "frames_per_line": 90, "orthogonal_pair_frame_count_histogram": {str(k): v for k, v in sorted(pair_hist.items())}}, "frame receipt")
    check(certificate["atoms"] == {"ordered_pairs": 57600, "rank_histogram": {str(k): v for k, v in sorted(ranks.items())}, "pair_rank_rows": ["".join(map(str, row)) for row in table], "pair_rank_encoding": "240 rows of 240 single-digit exact F2 ranks, support index 2*normal+trimmed", "rank7_live_trimmed_endpoint_count_histogram": {str(k): v for k, v in sorted(endpoints.items())}, "rank7_frame_hits_histogram": {str(k): v for k, v in sorted(hit_counts.items())}}, "atom receipt")
    check(certificate["nonorthogonality"] == {"clique_counts_including_empty": {str(k): v for k, v in sorted(counts.items())}, "complete_recursion_nodes": len(all_cliques), "maximum": 8, "witness_live_indices": witness, "witness_doubled_roots": [list(roots[live[i]]) for i in witness]}, "clique receipt")
    check(certificate["sharpness"] == {"coordinate_term_costs": [8] * 8, "all_pairs_checked": 12544, "decoder_sha256": sha(decoder), "cost": 64}, "attainment receipt")
    check(certificate["conclusion"]["minimum_copy_cost"] == 64 and certificate["conclusion"]["positive_terms_below_64"] == [8, 9], "conclusion receipt")

    manifest = json.loads((HERE / "SOURCES.json").read_text())
    check(len(manifest["dependencies"]) == 6, "source coverage")
    for source in manifest["dependencies"]:
        data = (HERE / source["path"]).read_bytes()
        check(hashlib.sha256(data).hexdigest() == source["sha256"], "source content binding")
        check(hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == source["git_blob"], "source Git binding")
        expected_commit = "ee8437bd9879272094e20c024cd34a53c4e84cd8" if source["path"] == "sources/pr1236-CERTIFICATE.json" else "8b10989e4e45f0f9ce41004d7898a21a32f87e11"
        check(source["source_commit"] == expected_commit, "source commit binding")
    check(certificate["source_manifest_sha256"] == sha(manifest), "source manifest binding")

    # PR1236 uses the same sorted positive roots but global (120-line) indices.
    # Re-encode our independently generated live-index data; import no PR code.
    audited = json.loads((HERE / "sources/pr1236-CERTIFICATE.json").read_text())
    global_supports = [(a, trimmed, sum(1 << live[i] for i in members)) for (a, trimmed, _), members in zip(support_records, support_indices)]
    global_frames = [tuple(live[i] for i in frame) for frame in frames]
    atom_rows = [(i, j, table[i][j], len(miss_sets[i] | miss_sets[j])) for i in range(240) for j in range(240)]
    check(audited["model"] == {"root_lines": 120, "live_lines": 112, "root_sha256": sha(roots), "punctured_frame_indices": puncture, "field": "R or C, ordinary transpose", "support_masks_sha256": sha(global_supports)}, "PR1236 model binding")
    check(audited["frames"] == {"count": 1260, "sha256": sha(global_frames), "per_live_line": 90, "orthogonal_pair_frame_multiplicities": {str(k): v for k, v in sorted(pair_hist.items())}}, "PR1236 complete frame binding")
    check(audited["atoms"] == {"ordered_support_pairs": 57600, "rank_histogram": {str(k): v for k, v in sorted(ranks.items())}, "sha256": sha(atom_rows), "beta7_missed_frame_histogram": {str(1260-k): v for k, v in hit_counts.items()}, "beta7_live_endpoint_histogram": {str(k): v for k, v in endpoints.items()}}, "PR1236 complete atom binding")
    audit_witness = audited["odd_graph"]["maximum_clique_indices"]
    check(len(audit_witness) == len(set(audit_witness)) == 8 and all(v in live for v in audit_witness), "PR1236 witness domain")
    check(all(gram[a][b] != 0 for a, b in combinations(audit_witness, 2)), "PR1236 witness pairings")
    check(audited["odd_graph"] == {"vertices": 112, "degrees": sorted({v.bit_count() for v in nonorth}), "clique_census": {str(k): v for k, v in sorted(counts.items())}, "maximum_clique_indices": audit_witness, "maximum_clique_roots": [list(roots[i]) for i in audit_witness]}, "PR1236 complete clique binding")
    check(audited["sharp_decoder"] == {"terms": 8, "costs": [8]*8, "cost": 64, "checked_all_pairs": 12544, "support_sizes": [sum(gram[a][b] != 0 for a in live) for b in puncture]}, "PR1236 attainment binding")
    check(audited["result"] == "SHARP_MASKED_ROOT_STAR_ASSEMBLY_FLOOR_64", "PR1236 result label")
    return {"maximal_nonorthogonal_cliques": len(maximal), "all_cliques": len(all_cliques), "pair_ranks_checked": 57600, "frames_checked": 1260, "copy_floor": 64, "pr1236_geometric_sections_matched": 5}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = verify(json.loads(args.certificate.read_text()))
    print("PASS_INDEPENDENT_ROOT_STAR_S46 " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        print("FAIL_INDEPENDENT_ROOT_STAR_S46:", error, file=sys.stderr)
        sys.exit(1)
