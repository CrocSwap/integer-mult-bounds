#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite premises for the P112 root-star copy-cost floor of 64.

Hanson Sun, with substantial OpenAI Codex assistance. Predecessors are credited
in README.md and SOURCES.json. No predecessor code is imported. Normal replay
is read-only and uses only the standard library.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SEED = 41


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def f2_rank(rows):
    """Exact Gaussian elimination on integer-encoded rows."""
    pivots = {}
    for row in rows:
        require(type(row) is int and row >= 0, "invalid F2 row")
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def root_lines():
    """Sorted doubled-coordinate representatives, first nonzero positive."""
    roots = set()
    for a, b in combinations(range(8), 2):
        for s, t in product((-2, 2), repeat=2):
            row = [0] * 8
            row[a], row[b] = s, t
            roots.add(tuple(row))
    roots.update(row for row in product((-1, 1), repeat=8)
                 if sum(x == -1 for x in row) % 2 == 0)
    require(len(roots) == 240, "root enumeration")
    return tuple(sorted({max(row, tuple(-x for x in row)) for row in roots}))


def fixed_cliques(adjacency, size):
    """Each size-k clique has exactly one strictly increasing traversal."""
    answer = []

    def extend(prefix, candidates):
        if len(prefix) == size:
            answer.append(tuple(prefix))
            return
        while candidates:
            if len(prefix) + candidates.bit_count() < size:
                return
            vertex = (candidates & -candidates).bit_length() - 1
            candidates &= ~(1 << vertex)
            extend(prefix + [vertex], candidates & adjacency[vertex])

    extend([], (1 << len(adjacency)) - 1)
    return tuple(answer)


def find_clique(adjacency, size):
    """Exhaustive target-size decision; the only bound is candidate cardinality."""
    nodes = Counter()

    def extend(prefix, candidates):
        nodes[len(prefix)] += 1
        if len(prefix) == size:
            return tuple(prefix)
        while candidates:
            if len(prefix) + candidates.bit_count() < size:
                break
            vertex = (candidates & -candidates).bit_length() - 1
            candidates &= ~(1 << vertex)
            found = extend(prefix + [vertex], candidates & adjacency[vertex])
            if found is not None:
                return found
        return None

    witness = extend([], (1 << len(adjacency)) - 1)
    return witness, {str(k): v for k, v in sorted(nodes.items())}


@dataclass(frozen=True)
class Geometry:
    lines: tuple
    gram: tuple
    removed: tuple
    live: tuple
    label_rows: tuple
    frames: tuple
    incidence: tuple


def validate_frames(gram, live, frames):
    require(len(frames) == 1260 and len(set(frames)) == 1260,
            "frame count or duplicate frame")
    incidence = [0] * len(live)
    for f, frame in enumerate(frames):
        require(len(frame) == 8 and tuple(sorted(set(frame))) == frame,
                "frame must have eight distinct ordered vertices")
        require(all(0 <= i < len(live) for i in frame), "frame vertex range")
        require(all(gram[live[i]][live[j]] == 0 for i, j in combinations(frame, 2)),
                "nonorthogonal frame")
        for i in frame:
            incidence[i] |= 1 << f
    require({mask.bit_count() for mask in incidence} == {90}, "line/frame incidence")
    for i, j in combinations(range(len(live)), 2):
        require(bool(incidence[i] & incidence[j]) == (gram[live[i]][live[j]] == 0),
                "orthogonal-pair completion")
    return tuple(incidence)


def geometry():
    lines = root_lines()
    require(len(lines) == 120 and len(set(lines)) == 120, "root-line count")
    dots = [[sum(x * y for x, y in zip(a, b)) for b in lines] for a in lines]
    require(all(dots[i][i] == 8 for i in range(120)), "root norms")
    require(all(x % 4 == 0 for row in dots for x in row), "Gram integrality")
    gram = tuple(tuple(x // 4 for x in row) for row in dots)
    removed = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            removed.append(lines.index(tuple(row)))
    removed = tuple(sorted(removed))
    require(all(gram[a][b] == 0 for a, b in combinations(removed, 2)),
            "puncture is not an orthogonal frame")
    live = tuple(i for i in range(120) if i not in removed)
    label_rows = tuple(sum(((gram[a][b] + 1) % 2) << j for j, b in enumerate(live))
                       for a in live)
    require(f2_rank(label_rows) == 9, "P112 label pairing rank")
    adjacency = tuple(sum(1 << j for j, b in enumerate(live)
                          if i != j and gram[a][b] == 0) for i, a in enumerate(live))
    frames = fixed_cliques(adjacency, 8)
    incidence = validate_frames(gram, live, frames)
    return Geometry(lines, gram, removed, live, label_rows, frames, incidence)


def supports_and_misses(g):
    positions = {line: i for i, line in enumerate(g.live)}
    frame_masks = tuple(sum(1 << i for i in frame) for frame in g.frames)
    supports, misses = [], []
    for normal in range(120):
        full = sum(1 << i for i, line in enumerate(g.live) if g.gram[line][normal])
        for trimmed in (False, True):
            mask = full
            if trimmed and normal in positions:
                mask &= ~(1 << positions[normal])
            supports.append((normal, trimmed, mask))
            misses.append(sum(1 << f for f, frame in enumerate(frame_masks)
                              if not mask & frame))
    validate_star_misses(g, supports, misses)
    return tuple(supports), tuple(misses)


def validate_star_misses(g, supports, misses):
    require(len(supports) == len(misses) == 240, "support inventory")
    positions = {line: i for i, line in enumerate(g.live)}
    for (normal, trimmed, _), missing in zip(supports, misses):
        expected = g.incidence[positions[normal]] if trimmed and normal in positions else 0
        require(missing == expected, "star missed-frame formula")


def pairing_rank(g, row_mask, col_mask):
    return f2_rank(g.label_rows[i] & col_mask for i in bits(row_mask))


def validate_cheap_atom(g, left, right, missing):
    positions = {line: i for i, line in enumerate(g.live)}
    normals = tuple(sorted({a for a, trimmed, _ in (left, right)
                            if trimmed and a in positions}))
    require(normals, "rank-seven atom has no live trimmed normal")
    require(all(g.incidence[positions[a]] & missing == g.incidence[positions[a]]
                for a in normals), "cheap atom omits a required missed frame")
    return normals


def atom_census(g, supports, misses):
    histogram, cheap_misses, rows = Counter(), Counter(), []
    for i, left in enumerate(supports):
        for j, right in enumerate(supports):
            a, trim_a, mask_a = left
            b, trim_b, mask_b = right
            beta = pairing_rank(g, mask_a, mask_b)
            full_a = not trim_a and a not in g.removed
            full_b = not trim_b and b not in g.removed
            predicted = (9 if full_a and full_b else 8 if full_a or full_b
                         else 8 - (g.gram[a][b] % 2))
            require(beta == predicted, "pairing-rank classification")
            histogram[beta] += 1
            missing = misses[i] | misses[j]
            normals = ()
            if beta == 7:
                normals = validate_cheap_atom(g, left, right, missing)
                cheap_misses[missing.bit_count()] += 1
            rows.append((i, j, beta, missing, normals))
    require(histogram == {7: 7616, 8: 37440, 9: 12544}, "atom rank histogram")
    require(cheap_misses == {90: 1792, 180: 5824}, "cheap atom missed-frame counts")
    return histogram, cheap_misses, rows


def compatibility_graph(g):
    graph = []
    for i, a in enumerate(g.live):
        row = 0
        for j, b in enumerate(g.live):
            compatible = i != j and not (g.incidence[i] & g.incidence[j])
            require(compatible == (i != j and abs(g.gram[a][b]) == 1),
                    "compatibility graph/Gram disagreement")
            if compatible:
                row |= 1 << j
        graph.append(row)
    return tuple(graph)


def coordinate_vectors(g):
    return tuple(tuple(g.gram[line][normal] for line in g.live) for normal in g.removed)


def verify_coordinate_decomposition(g, vectors):
    require(all(len(v) == len(g.live) for v in vectors), "coordinate vector width")
    require(all(sum(v[i] * v[j] for v in vectors) == 2 * g.gram[a][b]
                for i, a in enumerate(g.live) for j, b in enumerate(g.live)),
            "coordinate decoder identity")
    masks = [sum(1 << i for i, value in enumerate(v) if value) for v in vectors]
    costs = [pairing_rank(g, mask, mask) for mask in masks]
    require(costs == [8] * 8, "coordinate decoder invoice")
    return costs


def compute_receipt():
    g = geometry()
    supports, misses = supports_and_misses(g)
    histogram, cheap_misses, atoms = atom_census(g, supports, misses)
    graph = compatibility_graph(g)
    # Seed 41 chooses a traversal order; coverage remains the complete graph.
    order = tuple(range(SEED, 112)) + tuple(range(SEED))
    permuted = tuple(sum(1 << j for j, b in enumerate(order) if graph[a] >> b & 1)
                     for a in order)
    nine, nodes = find_clique(permuted, 9)
    require(nine is None, "nine compatible live normals found")
    eight, _ = find_clique(permuted, 8)
    require(eight is not None, "missing sharp eight-clique witness")
    witness = tuple(sorted(order[i] for i in eight))
    require(all(graph[a] >> b & 1 for a, b in combinations(witness, 2)),
            "invalid eight-clique witness")
    costs = verify_coordinate_decomposition(g, coordinate_vectors(g))
    pair_counts = Counter((g.incidence[i] & g.incidence[j]).bit_count()
                          for i, j in combinations(range(112), 2))
    even_entries = sum(row.bit_count() for row in g.label_rows)
    require(even_entries == 6720, "masked entry count")
    return {
        "schema_version": 1, "status": "PASS_MASKED_ROOT_STAR_FLOOR_64",
        "assignment_seed": SEED,
        "geometry": {
            "root_lines": 120, "live_lines": 112, "frame_count": len(g.frames),
            "frames_per_live_line": 90, "masked_entries": even_entries,
            "zero_price_singleton_positions": 112 ** 2 - even_entries,
            "pair_frame_count_histogram": {str(k): v for k, v in sorted(pair_counts.items())},
            "removed_line_indices": g.removed,
            "root_lines_sha256": digest(g.lines), "frames_sha256": digest(g.frames),
        },
        "atoms": {
            "support_entries": len(supports), "distinct_supports": len({s[2] for s in supports}),
            "ordered_pairs": len(atoms),
            "pairing_rank_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "rank_seven_missed_frames": {str(k): v for k, v in sorted(cheap_misses.items())},
            "pairing_ranks_sha256": digest([row[2] for row in atoms]),
            "table_sha256": digest(atoms),
        },
        "compatibility": {
            "graph_sha256": digest(graph), "vertices": 112,
            "edges": sum(row.bit_count() for row in graph) // 2,
            "maximum_clique": 8, "eight_clique_live_indices": witness,
            "eight_clique_doubled_roots": tuple(g.lines[g.live[i]] for i in witness),
            "exhaustive_nine_clique_search_nodes_by_depth": nodes,
        },
        "invoice": {
            "minimum_allowed_atom_cost": 7,
            "only_sub64_case_with_more_than_eight_terms": {"terms": 9, "cost_per_term": 7, "total": 63},
            "nine_term_case_excluded": True,
            "sharp_copy_cost": sum(costs), "coordinate_term_costs": costs,
        },
    }


def check_receipt(actual, expected):
    require(canonical(actual) == canonical(expected), "certificate mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", type=Path, help="write a newly computed certificate")
    group.add_argument("--check", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    try:
        actual = compute_receipt()
        if args.write:
            args.write.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
        else:
            check_receipt(actual, json.loads(args.check.read_text()))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("FAIL_MASKED_ROOT_STAR_FLOOR_64: " + str(exc), file=sys.stderr)
        return 1
    print(actual["status"])
    print("57600 atoms; 1260 frames; compatibility clique number 8; sharp copy cost 64")
    print("Scoped finite support obstruction; no supplier or kappa change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
