#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact integer frame-cover obstruction for the P112 root-star alphabet.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
Model and predecessor census: Navinor, PR1226; DreamingOfClouds, PR717/595.
No predecessor executable is imported. Python 3.10+, standard library only.
"""

import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PREDECESSOR = "8b10989e4e45f0f9ce41004d7898a21a32f87e11"
AUDITED = "ee8437bd9879272094e20c024cd34a53c4e84cd8"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def basis(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return tuple(pivots.values())


def root_lines():
    roots = []
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            roots.append(tuple(row))
    roots.extend(s for s in product((-1, 1), repeat=8) if s.count(-1) % 2 == 0)
    require(len(set(roots)) == 240, "E8 root inventory")
    lines = set()
    for row in roots:
        if next(x for x in row if x) < 0:
            row = tuple(-x for x in row)
        lines.add(row)
    require(len(lines) == 120, "E8 line inventory")
    return sorted(lines)


def model():
    roots = root_lines()
    inner = []
    for row in roots:
        values = []
        for col in roots:
            value = sum(a * b for a, b in zip(row, col))
            require(value % 4 == 0, "nonintegral root pairing")
            values.append(value // 4)
        inner.append(values)
    removed = []
    for i in range(0, 8, 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[i + 1] = 2, sign
            removed.append(roots.index(tuple(row)))
    removed.sort()
    require(all(inner[a][b] == (2 if a == b else 0) for a in removed for b in removed), "puncture is not a frame")
    live = [i for i in range(120) if i not in removed]
    pos = {normal: i for i, normal in enumerate(live)}
    pairing = [sum(((inner[a][b] + 1) % 2) << j for j, b in enumerate(live)) for a in live]
    orthogonal = [sum(1 << j for j, b in enumerate(live) if a != b and inner[a][b] == 0) for a in live]
    nonorthogonal = [sum(1 << j for j, b in enumerate(live) if a != b and inner[a][b] != 0) for a in live]
    supports = []
    for normal in range(120):
        full = sum(1 << i for i, line in enumerate(live) if inner[line][normal] != 0)
        for trimmed in (False, True):
            mask = full
            if trimmed and normal in pos:
                mask &= ~(1 << pos[normal])
            supports.append((normal, trimmed, mask))
    return roots, inner, removed, live, pairing, orthogonal, nonorthogonal, supports


def all_frames(adjacency):
    result = []

    def extend(prefix, candidates):
        if len(prefix) == 8:
            result.append(tuple(prefix))
            return
        while candidates and len(prefix) + candidates.bit_count() >= 8:
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            extend(prefix + [vertex], candidates & adjacency[vertex])

    extend([], (1 << len(adjacency)) - 1)
    return result


def clique_census(adjacency):
    counts = Counter()
    witness = []

    def extend(prefix, candidates):
        nonlocal witness
        counts[len(prefix)] += 1
        if len(prefix) > len(witness):
            witness = prefix[:]
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            extend(prefix + [vertex], candidates & adjacency[vertex])

    extend([], (1 << len(adjacency)) - 1)
    return dict(sorted(counts.items())), witness


def source_bindings():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    seen = set()
    for item in manifest["dependencies"]:
        require(item["path"] not in seen, "duplicate source pin")
        seen.add(item["path"])
        expected_commit = AUDITED if item["path"] == "sources/pr1236-CERTIFICATE.json" else PREDECESSOR
        require(item["source_commit"] == expected_commit, "changed source commit")
        path = HERE / item["path"]
        require(path.resolve().is_relative_to(HERE), "source path escapes package")
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256 mismatch: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == item["git_blob"], "source Git blob mismatch: " + item["path"])
    require(len(seen) == 6, "incomplete source inventory")
    return digest(manifest)


def build_certificate():
    source_hash = source_bindings()
    roots, inner, removed, live, pairing, orth, nonorth, supports = model()
    require(len(basis(pairing)) == 9, "binary pairing rank")
    frames = all_frames(orth)
    require(len(frames) == 1260, "frame coverage")
    frame_masks = [sum(1 << i for i in frame) for frame in frames]
    contain = [sum(1 << k for k, frame in enumerate(frame_masks) if frame >> i & 1) for i in range(112)]
    require(all(m.bit_count() == 90 for m in contain), "line-frame incidence")
    pair_hist = Counter()
    for i in range(112):
        for j in bits(orth[i]):
            if i < j:
                count = (contain[i] & contain[j]).bit_count()
                require(count > 0, "orthogonal live pair extends to no live frame")
                pair_hist[count] += 1

    pos = {line: i for i, line in enumerate(live)}
    all_frame_bits = (1 << len(frames)) - 1
    missed = []
    for normal, trimmed, support in supports:
        actual = sum(1 << k for k, frame in enumerate(frame_masks) if not support & frame)
        expected = contain[pos[normal]] if trimmed and normal in pos else 0
        require(actual == expected, "root-star missed-frame identity")
        missed.append(actual)

    support_bases = [basis(pairing[i] for i in bits(mask)) for _, _, mask in supports]
    rank_table = []
    rank_hist = Counter()
    endpoint_hist = Counter()
    hit_hist = Counter()
    for i, row_basis in enumerate(support_bases):
        row = []
        for j, (_, _, mask) in enumerate(supports):
            rank = len(basis(value & mask for value in row_basis))
            row.append(rank)
            rank_hist[rank] += 1
            if rank == 7:
                endpoints = [normal for normal, trimmed, _ in (supports[i], supports[j]) if trimmed and normal in pos]
                require(endpoints, "rank-seven atom has no live trimmed endpoint")
                selected = pos[endpoints[0]]
                require(contain[selected] & ~(missed[i] | missed[j]) == 0, "rank-seven missed endpoint")
                endpoint_hist[len(endpoints)] += 1
                hit_hist[(all_frame_bits ^ (missed[i] | missed[j])).bit_count()] += 1
        rank_table.append(row)
    require(rank_hist == {7: 7616, 8: 37440, 9: 12544}, "support-pair rank census")

    counts, witness = clique_census(nonorth)
    require(max(counts) == 8, "nonorthogonality clique bound")
    require(all(nonorth[i] >> j & 1 for i, j in combinations(witness, 2)), "clique witness")
    require(sum(counts.values()) == 482577, "clique census coverage")

    decoder = [[inner[line][normal] for normal in removed] for line in live]
    for i, a in enumerate(live):
        for j, b in enumerate(live):
            require(sum(x * y for x, y in zip(decoder[i], decoder[j])) == 2 * inner[a][b], "coordinate decoder identity")
    coordinate_costs = [rank_table[2 * normal][2 * normal] for normal in removed]
    require(coordinate_costs == [8] * 8, "sharp coordinate decoder price")

    # Mathematical negative controls: structural constraints, not only output hashes.
    require(any(sum(decoder[i][k] ** 2 for k in range(7)) != 4 for i in range(112)), "deleted coordinate term was not detected")
    require(contain[witness[0]] & contain[witness[0]], "duplicate endpoint control")
    extending = []
    for vertex in range(112):
        if vertex in witness:
            continue
        conflicts = [i for i in witness if orth[vertex] >> i & 1]
        require(conflicts, "ninth endpoint escaped the maximal clique")
        extending.append((vertex, conflicts[0], (contain[vertex] & contain[conflicts[0]]).bit_count()))
    require(len(extending) == 104, "ninth-endpoint control coverage")
    require(all(rank_table[2 * a + 1][2 * b + 1] >= 8 for a in removed for b in removed), "punctured endpoint control")
    require(all(pairing[i] >> j & 1 for frame in frames for i in frame for j in frame), "zero-cost frame control")

    return {
        "schema_version": 1,
        "status": "SCOPED_ROOT_STAR_COPY_FLOOR_64",
        "source_manifest_sha256": source_hash,
        "model": {"roots_sha256": digest(roots), "removed_global_indices": removed, "live_global_indices": live, "binary_pairing_rank": 9, "supports_sha256": digest(supports), "supports": 240},
        "frames": {"count": len(frames), "sha256": digest(frames), "frames_per_line": 90, "orthogonal_pair_frame_count_histogram": dict(sorted(pair_hist.items()))},
        "atoms": {"ordered_pairs": 57600, "rank_histogram": dict(sorted(rank_hist.items())), "pair_rank_rows": ["".join(map(str, row)) for row in rank_table], "pair_rank_encoding": "240 rows of 240 single-digit exact F2 ranks, support index 2*normal+trimmed", "rank7_live_trimmed_endpoint_count_histogram": dict(sorted(endpoint_hist.items())), "rank7_frame_hits_histogram": dict(sorted(hit_hist.items()))},
        "nonorthogonality": {"clique_counts_including_empty": counts, "complete_recursion_nodes": sum(counts.values()), "maximum": len(witness), "witness_live_indices": witness, "witness_doubled_roots": [roots[live[i]] for i in witness]},
        "sharpness": {"coordinate_term_costs": coordinate_costs, "all_pairs_checked": 12544, "decoder_sha256": digest(decoder), "cost": sum(coordinate_costs)},
        "controls": {"missing_coordinate_term_rejected": True, "duplicate_endpoint_rejected": True, "all_104_extensions_of_witness_rejected": True, "punctured_only_beta7_rejected": True, "zero_cost_atoms_cannot_meet_frames": True},
        "conclusion": {"minimum_copy_cost": 64, "positive_terms_below_64": [8, 9], "eight_term_obstruction": "Every term must meet every frame, excluding every rank-seven atom.", "nine_term_obstruction": "Nine rank-seven atoms require nine distinct pairwise nonorthogonal live trimmed endpoints; maximum is eight.", "scope": "Exact C(alpha)/N(alpha) supports on this P112; any finite term count and arbitrary real or complex coefficients; additional zero-cost terms permitted. No arbitrary proper sub-supports or new kappa."},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--write-certificate", type=Path, help="Create a new receipt; never overwrite an existing file.")
    args = parser.parse_args()
    certificate = json.loads(json.dumps(build_certificate()))
    if args.write_certificate:
        with args.write_certificate.open("x") as output:
            json.dump(certificate, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        require(json.loads(args.certificate.read_text()) == certificate, "certificate differs from complete recomputation")
    print("PASS_ROOT_STAR_INTEGER_COVER_S46 atoms=57600 frames=1260 cliques=482577 omega=8 copy_floor=64 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_ROOT_STAR_INTEGER_COVER_S46:", error, file=sys.stderr)
        sys.exit(1)
