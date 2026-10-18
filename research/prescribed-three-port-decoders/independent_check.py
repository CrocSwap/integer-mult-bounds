#!/usr/bin/env python3
"""Exact cut-code verification, independently of graph-partition enumeration.

Only the Python standard library is used.  Vertices 2i and 2i+1 are the
missing matched pair.  A cut is represented by n-1 vertex bits, fixing the
last vertex to zero.  We enumerate all rank-three subspaces of those bits
in reduced row echelon form, and minimize their union of edge supports.

If three prescribed coordinates have rank three in such a subspace,
deleting every other supported coordinate makes all three recoverable.
Conversely, any three decoders span one of the enumerated subspaces.
Thus this optimization is exact, without assuming a partition theorem.

Triple orbits are found by explicit group-generator traversal, rather
than a target-shape classification.  The proposed formula is consulted
only after the exact calculation, for p >= 3.  The p=2 case is reported as
boundary data.  Default p=2,3,4,5 takes roughly seconds to a minute.

Run: python independent_check.py
Regenerate explicitly: python independent_check.py --output independent-results.json
This is a separate Codex implementation, not independent human review.

Copyright 2026 woklerx. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. No physical supplier claim.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from itertools import combinations, product
import json
from pathlib import Path
import sys


def edges_for(p: int) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for u in range(2 * p) for v in range(u + 1, 2 * p)
                 if u // 2 != v // 2)


def rank(vectors: list[int] | tuple[int, ...]) -> int:
    basis: dict[int, int] = {}
    for vector in vectors:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = vector
                break
            vector ^= basis[pivot]
    return len(basis)


def triple_orbits(p: int, edges: tuple[tuple[int, int], ...]):
    """Cover every triple using generators of C2 wr S_p.

    Independent flips generate C2^p; adjacent pair swaps generate S_p.
    No motif classifier or graph-isomorphism package is used here.
    """
    n = 2 * p
    index = {edge: i for i, edge in enumerate(edges)}
    permutations = []
    for pair in range(p):
        permutation = list(range(n))
        a = 2 * pair
        permutation[a], permutation[a + 1] = permutation[a + 1], permutation[a]
        permutations.append(permutation)
    for pair in range(p - 1):
        permutation = list(range(n))
        a = 2 * pair
        for offset in (0, 1):
            permutation[a + offset], permutation[a + offset + 2] = (
                permutation[a + offset + 2], permutation[a + offset])
        permutations.append(permutation)
    actions = [tuple(index[tuple(sorted((permutation[u], permutation[v])))]
                     for u, v in edges) for permutation in permutations]
    unseen = set(combinations(range(len(edges)), 3))
    result = []
    while unseen:
        representative = min(unseen)
        unseen.remove(representative)
        queue = deque([representative])
        orbit_size = 0
        while queue:
            triple = queue.popleft()
            orbit_size += 1
            for action in actions:
                image = tuple(sorted(action[edge] for edge in triple))
                if image in unseen:
                    unseen.remove(image)
                    queue.append(image)
        result.append((representative, orbit_size))
    return result


def cut_subspaces(n: int):
    """Yield the vertex labels of every 3D cut subspace exactly once.

    The labels are columns of a 3 x (n-1) RREF generator matrix.
    Pivot columns are the three unit vectors; a nonpivot column has
    nonzero entries only in rows whose pivots lie to its left.
    """
    dimension = n - 1
    for pivots in combinations(range(dimension), 3):
        labels = [0] * n
        for row, column in enumerate(pivots):
            labels[column] = 1 << row
        free = [column for column in range(dimension) if column not in pivots]
        choices = [range(1 << sum(pivot < column for pivot in pivots))
                   for column in free]
        for entries in product(*choices):
            for column, value in zip(free, entries):
                labels[column] = value
            yield labels


def gaussian_binomial_rank3(dimension: int) -> int:
    return ((2 ** dimension - 1) * (2 ** dimension - 2) *
            (2 ** dimension - 4)) // ((8 - 1) * (8 - 2) * (8 - 4))


def targets_recoverable(n, edges, target_ids, retained_ids):
    """Fresh raw star-row elimination on the surviving input coordinates."""
    rows = [0] * n
    for coordinate, edge_id in enumerate(retained_ids):
        u, v = edges[edge_id]
        rows[u] |= 1 << coordinate
        rows[v] |= 1 << coordinate
    row_rank = rank(rows)
    positions = {edge_id: coordinate for coordinate, edge_id in enumerate(retained_ids)}
    return all(rank(rows + [1 << positions[target]]) == row_rank
               for target in target_ids)


def expected_formula(p, target_edges):
    """The conjectured/theorem value; never used by the optimizer."""
    degrees = Counter(vertex for edge in target_edges for vertex in edge)
    if len(degrees) == 3 and sorted(degrees.values()) == [2, 2, 2]:
        return None
    vertices = set(degrees)
    is_path = len(vertices) == 4 and sorted(degrees.values()) == [1, 1, 2, 2]
    is_two_pairs = len({vertex // 2 for vertex in vertices}) == 2
    return 6 * p - (11 if is_path and is_two_pairs else 12)


def verify(p: int):
    n = 2 * p
    edges = edges_for(p)
    orbits = triple_orbits(p, edges)
    records = []
    active = []
    for target_ids, orbit_size in orbits:
        target_edges = [list(edges[edge_id]) for edge_id in target_ids]
        # Edge functionals on the FULL cut space, not on a selected decoder.
        projection = [((1 << u) | (1 << v)) & ((1 << (n - 1)) - 1)
                      for u, v in target_edges]
        full_rank = rank(projection)
        record = {
            "target_edge_ids": list(target_ids),
            "target_edges": target_edges,
            "orbit_size": orbit_size,
            "full_cut_space_target_rank": full_rank,
            "minimum_deletions": None,
            "witness_vertex_labels": None,
        }
        records.append(record)
        if full_rank == 3:
            active.append(record)
    number_subspaces = 0
    best = [len(edges) + 1] * len(active)
    largest_best = max(best, default=-1)
    targets = [record["target_edges"] for record in active]
    for labels in cut_subspaces(n):
        number_subspaces += 1
        counts = [0] * 8
        for label in labels:
            counts[label] += 1
        # Support in the complete graph, minus the absent matching edges.
        support = (n * n - sum(count * count for count in counts)) // 2
        support -= sum(labels[u] != labels[u + 1] for u in range(0, n, 2))
        deletions = support - 3
        if deletions >= largest_best:
            continue
        changed = False
        for index, ((u, v), (w, x), (y, z)) in enumerate(targets):
            if deletions >= best[index]:
                continue
            a, b, c = labels[u] ^ labels[v], labels[w] ^ labels[x], labels[y] ^ labels[z]
            if a and b and c and a != b and a != c and b != c and (a ^ b ^ c):
                best[index] = deletions
                active[index]["minimum_deletions"] = deletions
                active[index]["witness_vertex_labels"] = labels.copy()
                changed = True
        if changed:
            largest_best = max(best, default=-1)
    assert number_subspaces == gaussian_binomial_rank3(n - 1)
    negative_controls = 0
    for record in records:
        labels = record["witness_vertex_labels"]
        if record["full_cut_space_target_rank"] == 3:
            assert labels is not None, "Full-rank projections must admit three decoders"
        if labels is not None:
            target_ids = set(record["target_edge_ids"])
            deleted = [i for i, (u, v) in enumerate(edges)
                       if labels[u] != labels[v] and i not in target_ids]
            retained = [i for i in range(len(edges)) if i not in deleted]
            assert len(deleted) == record["minimum_deletions"]
            assert targets_recoverable(n, edges, target_ids, retained)
            # Every single-edge restoration must invalidate a minimum witness.
            for restored in deleted:
                assert not targets_recoverable(n, edges, target_ids, sorted(retained + [restored]))
                negative_controls += 1
            record["witness_deleted_edges"] = [list(edges[i]) for i in deleted]
        if p >= 3:
            expected = expected_formula(p, record["target_edges"])
            record["formula_expected"] = expected
            assert record["minimum_deletions"] == expected, record
    histogram = Counter("impossible" if record["minimum_deletions"] is None
                        else str(record["minimum_deletions"])
                        for record in records for _ in range(record["orbit_size"]))
    total = len(edges) * (len(edges) - 1) * (len(edges) - 2) // 6
    assert sum(record["orbit_size"] for record in records) == total
    return {
        "p": p,
        "vertices": n,
        "input_edges": len(edges),
        "labelled_triples_covered": total,
        "target_orbits": len(records),
        "cut_subspaces_enumerated": number_subspaces,
        "minimum_deletion_histogram": dict(sorted(histogram.items())),
        "single_restoration_negative_controls": negative_controls,
        "formula_checked": p >= 3,
        "orbits": records,
    }


def main():
    if sys.flags.optimize:
        raise RuntimeError("Run without -O/-OO: this verifier requires enabled assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p", type=int, nargs="+", default=[2, 3, 4, 5])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path, help="explicitly generate a JSON certificate")
    mode.add_argument("--check", type=Path, help="verify a supplied JSON certificate; default is the sibling independent-results.json")
    args = parser.parse_args()
    if any(p < 2 or p > 5 for p in args.p):
        parser.error("this exhaustive verifier supports 2 <= p <= 5")
    output = {
        "schema": "prescribed-three-port-independent-cut-space-v1",
        "method": "all rank-three binary cut subspaces in RREF; generator BFS for target orbits",
        "arithmetic": "exact F2 integer bit masks",
        "results": [verify(p) for p in sorted(set(args.p))],
        "status": "passed",
    }
    encoded = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        certificate = args.check or Path(__file__).resolve().with_name("independent-results.json")
        if json.loads(certificate.read_text(encoding="utf-8")) != output:
            raise ValueError("independent certificate mismatch")
    results = output["results"]
    print("PASS_INDEPENDENT_CUT_SPACE"
          f" triples={sum(result['labelled_triples_covered'] for result in results)}"
          f" orbits={sum(result['target_orbits'] for result in results)}"
          f" subspaces={sum(result['cut_subspaces_enumerated'] for result in results)}"
          f" restoration_controls={sum(result['single_restoration_negative_controls'] for result in results)}")


if __name__ == "__main__":
    main()
