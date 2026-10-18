#!/usr/bin/env python3
"""Exact bounded screens of the inherited 112-port Hamming geometry.

This neither constructs a new scalar supplier nor proves a universal ceiling.
It tests lossless binary dimension reduction, coordinate-center puncturing,
and the orthogonal-frame obstruction to a lower-rank fitting matrix.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json"


def binary_rank(vectors):
    basis = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def modular_rank(rows, prime=1000003):
    matrix = [[value % prime for value in row] for row in rows]
    rank = 0
    for column in range(8):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column], -1, prime)
        matrix[rank] = [value * inverse % prime for value in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            factor = matrix[i][column]
            if factor:
                matrix[i] = [(x - factor * y) % prime
                             for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank


def main():
    source = json.loads(SOURCE.read_text())
    indices = [i for i, root in enumerate(source["root_lines"])
               if sum(bool(value) for value in root) > 1]
    ports = [source["binary_ports"][i] for i in indices]
    roots = [source["root_lines"][i] for i in indices]
    assert len(ports) == 112 and all(port.bit_count() % 2 for port in ports)
    gram_rows = [sum(((a & b).bit_count() % 2) << j for j, b in enumerate(ports))
                 for a in ports]
    assert binary_rank(ports) == binary_rank(gram_rows) == 9
    center_ranks = [binary_rank([port for port, root in zip(ports, roots) if root[i]])
                    for i in range(8)]
    assert center_ranks == [8] * 8

    punctures = []
    possible_totals = []
    minimum_removals = [112] * 8
    for normal in range(1, 512):
        kept = [j for j, port in enumerate(ports) if (normal & port).bit_count() % 2 == 0]
        center_cost = sum(binary_rank([ports[j] for j in kept if roots[j][i]])
                          for i in range(8))
        punctures.append(dict(normal=normal, live=len(kept), coordinate_center_cost=center_cost,
                              deficit_per_replica=8 * len(kept) - 9 * center_cost))
        outside = [root for port, root in zip(ports, roots)
                   if (normal & port).bit_count() % 2]
        rank = modular_rank(outside)
        if rank < 8:
            zero_coordinates = [i for i in range(8) if all(root[i] == 0 for root in outside)]
            assert rank == 7 and len(zero_coordinates) == 1
            possible_totals.append(dict(normal=normal, coordinate=zero_coordinates[0],
                                        outside_rational_rank=7))
        for i in range(8):
            support = [j for j, root in enumerate(roots) if root[i]]
            retained_support = [j for j in kept if roots[j][i]]
            if binary_rank([ports[j] for j in retained_support]) < 8:
                minimum_removals[i] = min(minimum_removals[i],
                                          len(support) - len(retained_support))
    good = {row["normal"] for row in possible_totals}
    assert len(good) == 8 and not any(a ^ b in good for a in good for b in good if a != b)
    assert minimum_removals == [24] * 8

    full_ports = source["binary_ports"]
    full_roots = source["root_lines"]
    full_total_hyperplanes = []
    for normal in range(1, 512):
        outside = [root for port, root in zip(full_ports, full_roots)
                   if (normal & port).bit_count() % 2]
        if modular_rank(outside) < 8:
            full_total_hyperplanes.append(normal)
    assert len(full_ports) == 120 and not full_total_hyperplanes
    full_center_ranks = [binary_rank([port for port, root in zip(full_ports, full_roots)
                                     if root[i]]) for i in range(8)]
    assert full_center_ranks == [9] * 8

    neighbors = [sum(1 << j for j, other in enumerate(roots)
                     if i != j and sum(x * y for x, y in zip(root, other)) == 0)
                 for i, root in enumerate(roots)]
    frames = []

    def enumerate_frames(remaining, chosen):
        if len(chosen) == 8:
            frames.append(chosen)
            return
        if remaining.bit_count() < 8 - len(chosen):
            return
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            vertex = bit.bit_length() - 1
            enumerate_frames(remaining & neighbors[vertex], chosen + [vertex])

    enumerate_frames((1 << 112) - 1, [])
    degrees = Counter(vertex for frame in frames for vertex in frame)
    assert len(frames) == 1260 and set(degrees.values()) == {90}
    receipt = dict(
        status="PASS_EXACT_BOUNDED_GEOMETRY_SCREENS",
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        live_ports=112, binary_port_rank=9, binary_gram_rank=9,
        coordinate_center_ranks=center_ranks,
        binary_hyperplanes_checked=511,
        hyperplane_live_count_distribution=dict(sorted(Counter(r["live"] for r in punctures).items())),
        maximum_hyperplane_deficit_per_replica=max(r["deficit_per_replica"] for r in punctures),
        best_hyperplane_restrictions=[r for r in punctures if r["deficit_per_replica"] == 8],
        baseline_deficit_per_replica=320,
        hyperplanes_supporting_nonzero_coordinate_totals=possible_totals,
        proper_subspace_total_lower_bound=8,
        minimum_port_deletions_for_one_coordinate_center_rank_drop=minimum_removals,
        reverse_puncture_120=dict(coordinate_total_support_ranks=full_center_ranks,
                                 proper_hyperplanes_supporting_any_nonzero_coordinate_total=0,
                                 hyperplanes_checked=511,
                                 coordinate_center_rank_sum_lower_bound=72),
        orthogonal_eight_frames=len(frames), frames_per_port=90,
        frame_census_sha256=hashlib.sha256(json.dumps(frames, separators=(",", ":")).encode()).hexdigest(),
        rank_j_decoder_necessary_live_bound="v <= 14*j",
        rank_seven_decoder_necessary_deletions=14,
        rank_seven_rank_eight_centers_best_center_to_port_ratio="56/98 = 64/112",
        proof_scope="Dimension obstruction preserves the current binary Gram matrix. "
                    "Hyperplane screen retains the coordinate-total architecture. "
                    "A nonzero total supported in a proper binary subspace must lie "
                    "in one of the eight certified hyperplanes; their one-dimensional "
                    "rational annihilators are distinct, ruling out dimension <=7. "
                    "The frame count bounds any rank-j matrix with nonzero diagonal "
                    "and zeros on distinct orthogonal root pairs: each surviving "
                    "frame is a diagonal principal submatrix, and averaging its "
                    "size gives v/14 <= j. These are necessary conditions, not "
                    "construction, general compiler or arbitrary-frame ceilings.")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
