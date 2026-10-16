#!/usr/bin/env python3
"""Discover a short obstruction; this producer is not trusted by the verifier.

New implementation of the graph and path search, independent of PR288's code.
All sessions and physical edges use point-to-line orientation. Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path


def plus(a: int, b: int) -> int:
    return (a % 3 + b % 3) % 3 + 3 * ((a // 3 + b // 3) % 3)


def times(a: int, b: int) -> int:
    # Integer code a0 + 3*a1 represents a0 + a1*t, with t*t = -1.
    a0, a1, b0, b1 = a % 3, a // 3, b % 3, b // 3
    return (a0 * b0 - a1 * b1) % 3 + 3 * ((a0 * b1 + a1 * b0) % 3)


def candidate_edges() -> list[tuple[int, int]]:
    points = [(0, 0, 1)] + [(0, 1, a) for a in range(9)]
    points += [(1, a, b) for a in range(9) for b in range(9)]
    result = []
    for i, point in enumerate(points):
        for j, line in enumerate(points):
            value = 0
            for x, y in zip(point, line):
                value = plus(value, times(x, y))
            if value == 0:
                result.append((i, 91 + j))
    if len(result) != 910:
        raise ValueError("wrong PG(2,9) edge count")
    return result


def bfs(start: int, adjacency: list[list[int]]) -> tuple[list[int], list[int]]:
    distances = [-1] * 182
    parent = [-1] * 182
    distances[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if distances[v] < 0:
                distances[v] = distances[u] + 1
                parent[v] = u
                queue.append(v)
    return distances, parent


def from_root(parent: list[int], v: int) -> list[int]:
    path = [v]
    while parent[path[-1]] != -1:
        path.append(parent[path[-1]])
    return list(reversed(path))


def discover(instance_path: Path) -> dict:
    raw = instance_path.read_bytes()
    instance = json.loads(raw)
    edges = candidate_edges()
    removed = set(instance["removed_edges"])
    sessions = sorted(removed - set(instance["constant_zero_edges"]) - set(instance["dropped_edges"]))
    physical = [e for e in range(910) if e not in removed]
    if len(removed) != 175 or len(sessions) != 157 or len(physical) != 735:
        raise ValueError("wrong instance counts")
    adjacency: list[list[int]] = [[] for _ in range(182)]
    for e in physical:
        u, v = edges[e]
        adjacency[u].append(v)
        adjacency[v].append(u)
    for row in adjacency:
        row.sort()

    uses: dict[int, dict[int, tuple[int, list[int]]]] = {}
    for session in sessions:
        source, target = edges[session]
        ds, ps = bfs(source, adjacency)
        dt, pt = bfs(target, adjacency)
        if ds[target] != 5:
            raise ValueError(f"session {session} has distance {ds[target]}, expected 5")
        uses[session] = {}
        for e in physical:
            a, b = edges[e]
            for x, y, sign in ((a, b, 1), (b, a, -1)):
                if ds[x] >= 0 and dt[y] >= 0 and ds[x] + 1 + dt[y] == 5:
                    path = from_root(ps, x) + list(reversed(from_root(pt, y)))
                    if e in uses[session] and uses[session][e][0] != sign:
                        raise ValueError("one session uses an edge in both directions")
                    uses[session][e] = sign, path

    # A four-cycle is the smallest simple bipartite contradiction.
    # Search all ordered session pairs deterministically, without symmetry pruning.
    for offset, first in enumerate(sessions):
        for second in sessions[offset + 1:]:
            shared = sorted(uses[first].keys() & uses[second].keys())
            by_relation: dict[int, int] = {}
            for e in shared:
                relation = uses[first][e][0] * uses[second][e][0]
                by_relation.setdefault(relation, e)
            if 1 not in by_relation or -1 not in by_relation:
                continue
            same, opposite = by_relation[1], by_relation[-1]
            # Reuse a path when it witnesses both selected incidences. This
            # simplifies the human proof; it is not a mathematical assumption.
            for session in (first, second):
                for chosen in (same, opposite):
                    path = uses[session][chosen][1]
                    directed = set(zip(path, path[1:]))
                    if all(
                        (edges[e] if uses[session][e][0] == 1 else edges[e][::-1]) in directed
                        for e in (same, opposite)
                    ):
                        for e in (same, opposite):
                            uses[session][e] = uses[session][e][0], path
                        break
            nodes = [["session", first], ["edge", same], ["session", second], ["edge", opposite]]
            pairs = [(first, same), (second, same), (second, opposite), (first, opposite)]
            incidences = []
            for session, e in pairs:
                sign, path = uses[session][e]
                incidences.append({"path": path, "sign": sign})
            return {
                "schema": "pr288-negative-cycle-v1",
                "dimension": 5,
                "instance_sha256": hashlib.sha256(raw).hexdigest(),
                "cycle_nodes": nodes,
                "incidences": incidences,
            }
    raise RuntimeError("No four-cycle certificate found; this is not an existence verdict")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path, default=Path(__file__).with_name("instance.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("certificate.json"))
    args = parser.parse_args()
    certificate = discover(args.instance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PRODUCED_NOT_YET_VERIFIED", "cycle_nodes": certificate["cycle_nodes"], "path_count": len(certificate["incidences"])}, sort_keys=True))


if __name__ == "__main__":
    main()
