# SPDX-License-Identifier: Apache-2.0
"""Rebuild the fixed P104 endpoint covers and their joint unit-step flags."""

import argparse
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p104-endpoint-geometric-budget/geometry.py"
WORD = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"
BASE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path):
    require(path.stat().st_size <= 2_000_000, "JSON size bound")
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


class SourceLoader(importlib.machinery.SourceFileLoader):
    """Compile authenticated source bytes without consulting bytecode caches."""

    def __init__(self, raw):
        super().__init__("p104_fixed_cover_geometry", str(ROOT / GEOMETRY))
        self.raw = raw

    def get_code(self, fullname):
        require(fullname == self.name, "fixed module name")
        return self.source_to_code(self.raw, self.path)


def inputs():
    records = read_json(PACKAGE / "SOURCES.json")["files"]
    require(len(records) <= 8, "source inventory bound")
    data = {}
    for row in records:
        if row["usage"] != "input":
            continue
        name = row["path"]
        require(
            name in {GEOMETRY, WORD, FIXTURE} and name not in data,
            "exact input inventory",
        )
        path = ROOT / name
        require(path.stat().st_size <= 2_000_000, "input size bound")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input SHA256")
        data[name] = raw
    require(set(data) == {GEOMETRY, WORD, FIXTURE}, "three authenticated inputs")
    loader = SourceLoader(data[GEOMETRY])
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return (
        module,
        json.loads(data[WORD], object_pairs_hook=unique),
        json.loads(data[FIXTURE], object_pairs_hook=unique),
    )


def endpoint_nodes(module, residuals):
    nodes, forms = {}, {}
    for orientation, (sets, normals) in residuals.items():
        require(len(sets) == len(normals) == 104, "104 endpoints per orientation")
        pairs = [
            module.plane_cover(points, normal)
            for points, normal in zip(sets, normals, strict=True)
        ]
        forms[orientation] = [[row["f"], row["g"]] for row in pairs]
        nodes[orientation] = [
            (i, normal, form)
            for i, normal in enumerate(normals)
            for form in forms[orientation][i]
        ]
    return nodes, forms


def compatibility(departure, arrival):
    require(len(departure) == len(arrival) == 208, "208 slots on each side")
    return [
        [
            j
            for j, (_, normal, form) in enumerate(arrival)
            if all(
                (v & w).bit_count() % 2 == 0
                for v in (label, second)
                for w in (normal, form)
            )
        ]
        for _, label, second in departure
    ]


def matching(graph):
    """Iterative augmenting paths, at most n searches of n left vertices."""
    n = len(graph)
    require(0 < n <= 208 and all(len(row) <= n for row in graph), "graph bound")
    require(
        all(type(v) is int and 0 <= v < n for row in graph for v in row),
        "graph vertex domain",
    )
    left, right = [-1] * n, [-1] * n
    for start in range(n):
        queue, seen, back, end = [start], {start}, {}, None
        for cursor in range(n):
            if cursor == len(queue):
                break
            u = queue[cursor]
            for v in graph[u]:
                if v in back:
                    continue
                back[v] = u
                if right[v] == -1:
                    end = v
                    break
                nxt = right[v]
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
            if end is not None:
                break
        require(end is not None, "no perfect matching for fixed covers")
        for _ in range(n):
            u = back[end]
            previous = left[u]
            left[u], right[end] = end, u
            if previous == -1:
                break
            end = previous
        else:
            raise ValueError("augmenting path bound exhausted")
    require(sorted(left) == list(range(n)), "perfect matching permutation")
    return left


def flag(module, departure, arrival):
    _, label, second = departure
    _, normal, form = arrival
    basis = [label, second]
    for dimension, space in (
        (
            7,
            [
                v
                for v in range(512)
                if not module.parity(v, normal) and not module.parity(v, form)
            ],
        ),
        (8, [v for v in range(512) if not module.parity(v, normal)]),
        (9, range(512)),
    ):
        for vector in space:
            if len(basis) == dimension:
                break
            if vector not in module.span(basis):
                basis.append(vector)
        require(len(basis) == dimension, "complete nested flag extension")
    return basis


def calculate():
    module, word, fixture = inputs()
    ports, paths, paid = module.reconstruct(word, fixture)
    require(paid == BASE, "original whole-channel histogram")
    nodes, forms = endpoint_nodes(module, module.residuals(ports, paths))
    departure, arrival = nodes["departure"], nodes["arrival"]
    graph = compatibility(departure, arrival)
    permutation = matching(graph)
    helpers = [
        {
            "source": departure[i][0],
            "departure_choice": i % 2,
            "target": arrival[j][0],
            "arrival_choice": j % 2,
            "basis": flag(module, departure[i], arrival[j]),
        }
        for i, j in enumerate(permutation)
    ]
    column_degrees = [sum(j in row for row in graph) for j in range(208)]
    return {
        "schema_version": 1,
        "forms": forms,
        "helpers": helpers,
        "graph": {
            "edges": sum(map(len, graph)),
            "left_degrees": list(map(len, graph)),
            "right_degrees": column_degrees,
        },
        "scope": "Joint endpoint flag compatibility only; no chronological circuit",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = calculate()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    require(
        json.dumps(result, sort_keys=True)
        == json.dumps(read_json(PACKAGE / "CERTIFICATE.json"), sort_keys=True),
        "typed certificate equality",
    )
    print("PASS_P104_JOINT_UNIT_FLAGS helpers=208 edges=2309 rank_one_steps=1872")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"FAIL_P104_JOINT_UNIT_FLAGS: {error}") from error
