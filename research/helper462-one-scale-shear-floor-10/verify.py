#!/usr/bin/env python3
"""One-scale zero-swap helper-462 words have at least 10 elementary shears.

The rank-drop census has depth at most 2, so a word of length 9 would need
exactly one rank-preserving shear, at a census matrix of rank 6, 7 or 8, whose
predecessor still has depth equal to that rank. Every rational coefficient of
every such shear is covered by a generic depth plus the rational roots of the
pencil's eliminant. That depth stays strictly below the rank. No new kappa.

Standard library only. Checks use an explicit failure function, so they stay
active under python -O.
"""

from fractions import Fraction
import json
from multiprocessing import Pool
import os
from pathlib import Path
import sys
import time

# Python -I omits the script directory. The package is one module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import shearcert
from shearcert import (
    apply_shear,
    batch_edges,
    certified_max_depth,
    depth_matrix,
    eye,
    rank_of,
    rat_roots,
)

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
N = 8
# Heavy scale rows first so four workers finish near the long pole, row 7.
SCALE_ORDER = (7, 5, 2, 6, 3, 0, 4, 1)

# Distinct matrices. PR #7055 counted rank-6 arrivals before identifying equal
# matrices: 37 arrivals on rows 0, 1, 2 and 4, and 4 arrivals on row 5. Those
# arrivals are the edge counts below.
EXPECTED = {
    0: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 20}, "edges": {8: 33, 7: 37},
        "max_depth": {8: 3, 7: 2, 6: 1}},
    1: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 20}, "edges": {8: 33, 7: 37},
        "max_depth": {8: 3, 7: 2, 6: 1}},
    2: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 20}, "edges": {8: 33, 7: 37},
        "max_depth": {8: 3, 7: 2, 6: 1}},
    3: {"depth": 1, "det": "21/8", "nodes": {8: 1, 7: 38}, "edges": {8: 38, 7: 0},
        "max_depth": {8: 2, 7: 1}},
    4: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 20}, "edges": {8: 33, 7: 37},
        "max_depth": {8: 3, 7: 2, 6: 1}},
    5: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 36, 6: 2}, "edges": {8: 36, 7: 4},
        "max_depth": {8: 3, 7: 2, 6: 1}},
    6: {"depth": 1, "det": "21/8", "nodes": {8: 1, 7: 38}, "edges": {8: 38, 7: 0},
        "max_depth": {8: 2, 7: 1}},
    7: {"depth": 1, "det": "19/4", "nodes": {8: 1, 7: 48}, "edges": {8: 48, 7: 0},
        "max_depth": {8: 2, 7: 1}},
}

TIGHT_WORD = (
    (0, 1, Fraction(-1)),
    (1, 0, Fraction(1, 2)),
    (2, 3, Fraction(1)),
    (3, 2, Fraction(2)),
    (4, 5, Fraction(1)),
    (5, 4, Fraction(3)),
    (6, 7, Fraction(3)),
    (7, 6, Fraction(3)),
)


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def difference(matrix):
    return [[matrix[i][j] - (1 if i == j else 0) for j in range(len(matrix))]
            for i in range(len(matrix))]


def determinant(matrix):
    work = [row[:] for row in matrix]
    size = len(work)
    det = Fraction(1)
    sign = 1
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        pivot_value = work[column][column]
        det *= pivot_value
        for row in range(column + 1, size):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for index in range(column, size):
                work[row][index] -= factor * work[column][index]
    return sign * det


def load_matcher():
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    return [[Fraction(entry) for entry in row] for row in data["matcher"]]


def scale_matrix(matcher, row):
    out = [entry[:] for entry in matcher]
    for col in range(N):
        out[row][col] /= Fraction(-16)
    return out


def census(matrix):
    """Every matrix reachable by left rank-drop peels, and the edge counts."""
    seen = set()
    unique = {8: [], 7: [], 6: []}
    nodes = {8: 0, 7: 0, 6: 0}
    edges = {8: 0, 7: 0}
    lowest = [None]

    def rec(current, rank):
        key = tuple(tuple(entry) for entry in current)
        if key in seen:
            return
        seen.add(key)
        nodes[rank] = nodes.get(rank, 0) + 1
        if rank in unique:
            unique[rank].append(current)
        lowest[0] = rank if lowest[0] is None else min(lowest[0], rank)
        steps = batch_edges(current)
        if steps:
            edges[rank] = edges.get(rank, 0) + len(steps)
        for target, source, coefficient in steps:
            child = shearcert.left_peel(current, target, source, coefficient)
            child_rank = rank_of(difference(child))
            if child_rank != rank - 1:
                raise SystemExit("FAIL: peel did not drop rank by 1")
            rec(child, child_rank)

    root_rank = rank_of(difference(matrix))
    rec(matrix, root_rank)
    tree_depth = root_rank - lowest[0]
    return nodes, edges, unique, tree_depth, root_rank


def one_scale(scale_row):
    for key in ("nodes", "maxdeg", "maxbits", "roots", "maxrootdeg"):
        shearcert.STATS[key] = 0
    matcher = load_matcher()
    matrix = scale_matrix(matcher, scale_row)
    gap_det = determinant(difference(matrix))
    nodes, edges, unique, tree_depth, root_rank = census(matrix)
    expected = EXPECTED[scale_row]
    if str(gap_det) != expected["det"] or tree_depth != expected["depth"] or root_rank != 8:
        raise SystemExit("FAIL: census header row %s det %s depth %s rank %s" % (
            scale_row, gap_det, tree_depth, root_rank))
    for rank, count in expected["nodes"].items():
        if nodes.get(rank, 0) != count:
            raise SystemExit("FAIL: node count row %s rank %s got %s want %s" % (
                scale_row, rank, nodes.get(rank, 0), count))
    for rank, count in expected["edges"].items():
        if edges.get(rank, 0) != count:
            raise SystemExit("FAIL: edge count row %s rank %s got %s want %s" % (
                scale_row, rank, edges.get(rank, 0), count))
    if any(rank < 6 and count for rank, count in nodes.items()):
        raise SystemExit("FAIL: rank-drop tree on row %s reaches rank below 6: %s" % (scale_row, nodes))
    maxima = {}
    for rank in (8, 7, 6):
        if not unique[rank]:
            continue
        best = -1
        for matrix_node in unique[rank]:
            for target in range(N):
                for source in range(N):
                    if target == source:
                        continue
                    depth, _place, _generic, _nroots, _stats = certified_max_depth(
                        matrix_node, target, source, rank_target=rank)
                    if depth >= rank:
                        raise SystemExit(
                            "FAIL: row %s rank %s shear %s<-%s preserves rank with depth %s"
                            % (scale_row, rank, target, source, depth))
                    if depth > best:
                        best = depth
        maxima[rank] = best
        if best != expected["max_depth"][rank]:
            raise SystemExit("FAIL: row %s rank %s max depth %s want %s" % (
                scale_row, rank, best, expected["max_depth"][rank]))
    if shearcert.STATS["maxdeg"] > 2:
        raise SystemExit("FAIL: row %s pencil degree %s" % (scale_row, shearcert.STATS["maxdeg"]))
    if shearcert.STATS["maxrootdeg"] != 8:
        raise SystemExit("FAIL: row %s root degree %s" % (scale_row, shearcert.STATS["maxrootdeg"]))
    print("ROW", scale_row, "depth", tree_depth, "max", maxima,
          "rootdeg", shearcert.STATS["maxrootdeg"], flush=True)
    return scale_row, maxima


def controls(matcher):
    need(rat_roots((1, -3, 2)) and set(rat_roots((1, -3, 2))) == {Fraction(1, 2), Fraction(1)},
         "quadratic roots of 1 - 3x + 2x^2")
    need(rat_roots((1, 0, 1)) == [], "x^2 + 1 has no rational root")
    need(determinant(matcher) == Fraction(-16), "pinned matcher determinant")
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "363005817/100000000000", "selected kappa moved")
    # Eight tight shears attain rank distance 8 and depth 8. The obstruction
    # below is not an artifact of the depth function.
    tight = eye(8)
    for target, source, coefficient in TIGHT_WORD:
        tight = apply_shear(tight, target, source, coefficient)
    need(rank_of(difference(tight)) == 8 and depth_matrix(tight, {}) == 8,
         "tight 8-shear control")
    # A 3x3 shear can raise depth by 2 while preserving rank. The same
    # predicate that accepts the helper census rejects this matrix.
    small = eye(3)
    for target, source, coefficient in ((0, 1, -2), (1, 0, -2), (0, 2, -2)):
        small = apply_shear(small, target, source, Fraction(coefficient))
    need(depth_matrix(small, {}) == 0 and rank_of(difference(small)) == 2,
         "3x3 depth-0 base")
    best, where, generic, _nroots, _stats = certified_max_depth(small, 0, 2)
    need(generic == 0 and best == 2 and where[1] == 2,
         "3x3 preserving shear must be seen to reach depth 2")


def main():
    t0 = time.time()
    matcher = load_matcher()
    controls(matcher)
    for row in range(N):
        block = scale_matrix(matcher, row)
        need(determinant(block) == 1, "scale block %s is not in SL(8)" % row)
        need(rank_of(difference(block)) == 8, "scale block %s rank" % row)
    workers = min(4, os.cpu_count() or 1)
    with Pool(workers) as pool:
        results = pool.map(one_scale, SCALE_ORDER)
    got = {row for row, _maxima in results}
    need(got == set(range(N)), "missing scale rows %s" % (set(range(N)) - got))
    print("PASS_HELPER462_ONE_SCALE_SHEAR_FLOOR_10 seconds", round(time.time() - t0, 2))


if __name__ == "__main__":
    main()
