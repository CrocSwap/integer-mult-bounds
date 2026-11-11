#!/usr/bin/env python3
"""Check the explicit Hall obstruction in the extremal 96-line complement.

Standard library only. No solver, predecessor execution, or file writes.
All contracts use exceptions and remain active under optimized Python.
"""

import ast
import hashlib
import itertools
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "p104-e8-rank8-closure" / "check.py"
SOURCE_SHA256 = "6c9c13133942d811449a76a3489886cd30a96eee38a041105f33a104453e8a00"
D24 = (0, 1, 2, 3, 12, 13, 14, 15, 24, 25, 34, 35,
       36, 37, 38, 39, 40, 41, 44, 45, 46, 47, 50, 51)
GAUGE = (4, 6, 8, 10, 56, 72, 88, 104)
WITNESS = (90, 92, 96, 106, 108, 112)
SUPPORTS = ((2, 5), (1, 5), (0, 5), (2, 4), (1, 4), (0, 4))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def e8_lines():
    """Doubled E8 coordinates, with the ordering of the pinned source."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((2, -2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            roots.append(tuple(row))
    roots.extend(row for row in itertools.product((1, -1), repeat=8)
                 if row.count(-1) % 2 == 0)
    require(len(roots) == 240, "root count")
    require(all(dot(row, row) == 8 for row in roots), "root norm")
    seen, lines = set(), []
    for row in roots:
        if row not in seen:
            seen.update((row, tuple(-x for x in row)))
            lines.append(row)
    require(len(lines) == 120, "line count")
    return lines


def read_deleted_set():
    require(SOURCE.stat().st_size <= 1_048_576, "source size bound")
    data = SOURCE.read_bytes()
    require(hashlib.sha256(data).hexdigest() == SOURCE_SHA256,
            "predecessor source hash")
    tree = ast.parse(data)
    values = [ast.literal_eval(node.value) for node in tree.body
              if isinstance(node, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == "D24"
                      for t in node.targets)]
    require(values == [list(D24)], "pinned D24 assignment")
    require(len(set(D24)) == 24 and set(D24) <= set(range(120)), "D24 domain")
    return set(range(120)) - set(D24)


def eight_cliques(no, vertices):
    """Enumerate increasing cliques by bounded iterative depth-first search."""
    require(len(no) == 120 and len(vertices) <= 120, "graph domain")
    neighbors = [sum(1 << j for j in vertices if no[i][j]) for i in range(120)]
    stack = [((), sum(1 << v for v in vertices))]
    result = []
    for _ in range(2_000_000):
        if not stack:
            return result
        clique, candidates = stack.pop()
        if len(clique) == 8:
            result.append(clique)
            require(len(result) <= 10_000, "clique storage bound")
            continue
        if len(clique) + candidates.bit_count() < 8:
            continue
        for _ in range(120):
            if not candidates:
                break
            bit = candidates & -candidates
            vertex = bit.bit_length() - 1
            candidates ^= bit
            stack.append((clique + (vertex,), candidates & neighbors[vertex]))
        require(len(stack) <= 960, "depth-first worklist bound")
    raise ValueError("clique enumeration exhausted its iteration bound")


def supports(gauge, no):
    return {t: tuple(i for i, c in enumerate(gauge) if not no[t][c])
            for t in range(120) if t not in gauge}


def components(edges):
    require(len(edges) <= 28, "edge domain")
    require(all(len(e) == 2 and 0 <= e[0] < e[1] < 8 for e in edges),
            "edge endpoints")
    parent = list(range(8))
    for a, b in edges:
        old, new = parent[b], parent[a]
        parent = [new if p == old else p for p in parent]
    return [(sum(p == root for p in parent),
             sum(parent[a] == root for a, _ in edges))
            for root in sorted(set(parent))]


def pseudoforest(edges):
    return all(e <= v for v, e in components(edges))


def endpoint_matching(edges):
    """Exhaust all at most 64 endpoint choices for the six-line fixture."""
    require(len(edges) <= 6, "matching enumeration domain")
    for choices in itertools.product(*edges):
        if len(set(choices)) == len(choices):
            return choices
    return None


def vectors_fit(vectors, no):
    vertices = tuple(vectors)
    require(len(vertices) <= 14, "fixture vector domain")
    require(all(len(row) == 8 for row in vectors.values()), "vector width")
    return (all(dot(vectors[t], vectors[t]) == 1 for t in vertices)
            and all(not no[s][t] or dot(vectors[s], vectors[t]) == 0
                    for s, t in itertools.combinations(vertices, 2)))


def check_fixture(no, live):
    require(set(GAUGE + WITNESS) <= live, "fixture inside S96")
    require(len(set(GAUGE + WITNESS)) == 14, "fixture distinct lines")
    require(all(no[s][t] for s, t in itertools.combinations(GAUGE, 2)),
            "gauge is a forced-zero clique")
    masks = supports(GAUGE, no)
    require(tuple(masks[t] for t in WITNESS) == SUPPORTS, "fixture support table")
    for s, t in itertools.combinations(WITNESS, 2):
        shared = set(masks[s]) & set(masks[t])
        require(len(shared) <= 1, "distinct pair supports")
        require(not shared or no[s][t], "shared-coordinate forced zero")
    vertices = set().union(*(set(edge) for edge in SUPPORTS))
    require(len(vertices) == 5 and len(SUPPORTS) == 6, "6k versus 5k")
    require(not pseudoforest(SUPPORTS), "Hall deficiency")
    require(endpoint_matching(SUPPORTS) is None, "scalar Hall deficiency")


def check_repairs(no):
    """All 64 pair-line subsets; construct exact integer patterns when feasible."""
    basis = [tuple(int(i == j) for i in range(8)) for j in range(8)]
    feasible = 0
    for mask in range(1 << 6):
        indices = [i for i in range(6) if mask >> i & 1]
        edges = [SUPPORTS[i] for i in indices]
        choice = endpoint_matching(edges)
        require((choice is not None) == pseudoforest(edges), "Hall control")
        require((choice is not None) == (mask != 63), "minimal obstruction")
        if choice is not None:
            vectors = {t: basis[i] for i, t in enumerate(GAUGE)}
            vectors.update({WITNESS[i]: basis[c]
                            for i, c in zip(indices, choice, strict=True)})
            require(vectors_fit(vectors, no), "integer repair pattern")
            feasible += 1
    require(feasible == 63, "repair subset count")
    vectors = {t: basis[i] for i, t in enumerate(GAUGE)}
    vectors[GAUGE[0]] = (0,) * 8
    require(not vectors_fit(vectors, no), "singular diagonal control")
    vectors[GAUGE[0]] = basis[1]
    require(not vectors_fit(vectors, no), "forced-zero violation control")
    return feasible


def is_k44(edges):
    if len(edges) != 16 or not all(e == 16 for _, e in components(edges)):
        return False
    adjacency = [set() for _ in range(8)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    if any(len(row) != 4 for row in adjacency):
        return False
    right = adjacency[0]
    left = set(range(8)) - right
    return (len(left) == len(right) == 4
            and all(adjacency[v] == right for v in left)
            and all(adjacency[v] == left for v in right))


def check_live_gauges(no, live):
    gauges = eight_cliques(no, live)
    require(len(gauges) == 192, "S96 eight-clique count")
    require(GAUGE in gauges, "explicit gauge enumerated")
    for gauge in gauges:
        masks = supports(gauge, no)
        require(Counter(map(len, masks.values())) == {2: 28, 5: 56, 6: 28},
                "outside-line support sizes")
        pairs = {t: edge for t, edge in masks.items() if len(edge) == 2}
        require(len(set(pairs.values())) == 28, "unique pair lines")
        edges = [edge for t, edge in pairs.items() if t in live]
        require(is_k44(edges), "S96 pair graph is K4,4")
        for s, t in itertools.combinations(pairs, 2):
            if set(pairs[s]) & set(pairs[t]):
                require(no[s][t], "pair-line star mask")
    require(not is_k44(edges[:-1]), "incomplete K4,4 control")
    return len(gauges)


def main():
    live = read_deleted_set()
    require(len(live) == 96, "live line count")
    lines = e8_lines()
    no = [[i != j and dot(lines[i], lines[j]) != 0 for j in range(120)]
          for i in range(120)]
    require(all(dot(lines[i], lines[j]) in (0, 4, -4)
                for i, j in itertools.combinations(range(120), 2)), "root pairs")
    check_fixture(no, live)
    print("fixture: K =", list(GAUGE), "pair lines =", list(WITNESS))
    print("supports:", list(SUPPORTS), "; Hall contradiction: 6k <= 5k")
    feasible = check_repairs(no)
    gauges = check_live_gauges(no, live)
    print("S96: 192 eight-cliques; every pair-line graph is K4,4")
    print("controls: 63 proper pair-line subsets have exact integer patterns;")
    print("singular diagonal, forced-zero violation and incomplete K4,4 rejected")
    print(f"PASS_E8_S96_HALL gauges={gauges} witness_lines=14 "
          f"repair_subsets={feasible} no_new_kappa")


if __name__ == "__main__":
    main()
