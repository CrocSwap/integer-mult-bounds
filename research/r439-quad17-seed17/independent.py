"""First-ADD BFS and exact inverse oracle; imports no discovery code.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
First-gate column subtraction is credited to the PR281 verification lineage.
"""
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
import json


def first_gate_bfs(matrix, limit=100_000):
    """Complete first-gate graph, with columns stored contiguously."""
    n = len(matrix)
    if n != 6 or any(len(row) != n for row in matrix):
        raise ValueError("expected a six-register map")
    if any(type(v) is not int or v < int(r == c)
           for r, row in enumerate(matrix) for c, v in enumerate(row)):
        raise ValueError("invalid positive matrix")
    if type(limit) is not int or limit < 1:
        raise ValueError("invalid state budget")
    initial = tuple(tuple(matrix[r][c] for r in range(n)) for c in range(n))
    identity = tuple(tuple(int(r == c) for r in range(n)) for c in range(n))
    distances, ways, todo = {initial: 0}, {initial: 1}, deque([initial])
    edges, adjacency = 0, {}
    while todo:
        columns = todo.popleft()
        adjacency[columns] = []
        for donor in range(n):
            for destination in range(n):
                if donor == destination:
                    continue
                residual = tuple(a-b for a, b in zip(columns[destination], columns[donor]))
                if any(v < int(r == destination) for r, v in enumerate(residual)):
                    continue
                child = columns[:destination]+(residual,)+columns[destination+1:]
                adjacency[columns].append((donor, destination, child))
                edges += 1
                depth = distances[columns]+1
                if child not in distances:
                    if len(distances) >= limit:
                        raise ValueError("incomplete independent BFS: state cap")
                    distances[child], ways[child] = depth, ways[columns]
                    todo.append(child)
                elif distances[child] == depth:
                    ways[child] += ways[columns]
    if identity not in distances:
        raise ValueError("no positive factorization in independent BFS")
    # Independently identify the shortest suffixes by increasing entry sum.
    # Multiplying a positive reverse product on the right adds column d to
    # column s. This is different from discovery's left row accumulation.
    remaining = {}
    for state in sorted(adjacency, key=lambda s: sum(map(sum, s))):
        remaining[state] = 0 if state == identity else min(
            (1+remaining[child] for _, _, child in adjacency[state]), default=10**9)
    if remaining[initial] != distances[identity]:
        raise ValueError("first-gate distance methods disagree")
    layer, visited_pairs = {(initial, identity): 1}, 1
    for _ in range(distances[identity]):
        following = defaultdict(int)
        for (state, growth), multiplicity in layer.items():
            for donor, destination, child in adjacency[state]:
                if remaining[child] != remaining[state]-1:
                    continue
                added = tuple(a+b for a, b in zip(growth[destination], growth[donor]))
                next_growth = growth[:destination]+(added,)+growth[destination+1:]
                following[child, next_growth] += multiplicity
        layer = dict(following)
        visited_pairs += len(layer)
        if visited_pairs > limit:
            raise ValueError("incomplete independent envelope census: state cap")
    if any(s != identity for s, _ in layer):
        raise ValueError("independent envelope endpoint is not identity")
    endpoints = sorted(
        ({"matrix": [columns[c][r] for r in range(n) for c in range(n)], "programs": count}
         for (_, columns), count in layer.items()), key=lambda e: e["matrix"])
    if sum(e["programs"] for e in endpoints) != ways[identity]:
        raise ValueError("independent envelope multiplicities disagree")
    encoded = json.dumps(endpoints, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return {"minimum": distances[identity], "shortest_programs": ways[identity],
            "states": len(distances), "edges": edges, "state_cap": limit,
            "reverse_paired_states": visited_pairs,
            "reverse_endpoints": len(endpoints),
            "reverse_census_sha256": hashlib.sha256(encoded).hexdigest(),
            "depth_histogram": dict(sorted(Counter(str(d) for d in distances.values()).items())),
            "exhausted": True}


def signed_map(gates, sign=1):
    n = 6
    out = [[int(r == c) for c in range(n)] for r in range(n)]
    for dst, src in gates:
        if type(dst) is not int or type(src) is not int or not (
                0 <= dst < n and 0 <= src < n and dst != src):
            raise ValueError("invalid ADD pair")
        for c in range(n):
            out[dst][c] += sign*out[src][c]
    return out


def inverse(matrix):
    n = len(matrix)
    rows = [[Fraction(v) for v in row]+[Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for pivot in range(n):
        donor = next((r for r in range(pivot, n) if rows[r][pivot]), None)
        if donor is None:
            raise ValueError("singular transfer")
        rows[pivot], rows[donor] = rows[donor], rows[pivot]
        scale = rows[pivot][pivot]
        rows[pivot] = [v/scale for v in rows[pivot]]
        for r in range(n):
            if r != pivot:
                scale = rows[r][pivot]
                rows[r] = [a-scale*b for a, b in zip(rows[r], rows[pivot])]
    out = [row[n:] for row in rows]
    if any(v.denominator != 1 for row in out for v in row):
        raise ValueError("nonintegral inverse")
    return [[int(v) for v in row] for row in out]


def product(left, right):
    n = len(left)
    return [[sum(left[r][k]*right[k][c] for k in range(n))
             for c in range(n)] for r in range(n)]


def inverse_envelope(transfer, backward):
    inv = inverse(transfer)
    lower = [[abs(v) for v in row] for row in inv]
    if any(b < a for x, y in zip(lower, backward) for a, b in zip(x, y)):
        raise ValueError("reverse envelope below absolute inverse")
    return inv, lower
