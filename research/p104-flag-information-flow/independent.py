# SPDX-License-Identifier: Apache-2.0
"""Per-source BFS with reduced binary bases; no producer/predecessor imports."""

import hashlib
import json
from collections import deque
from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
NAMES = ("research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
         "research/p104-native-channel/inputs/P104-FIXTURE.json",
         "research/p104-joint-unit-flags/CERTIFICATE.json",
         "research/p104-joint-unit-flags/README.md")


def check(ok, message):
    if not ok:
        raise ValueError(message)


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    check(path.stat().st_size <= 2_000_000, "bounded JSON")
    return json.loads(path.read_bytes(), object_pairs_hook=no_duplicates)


def authenticate():
    data = {}
    records = load(PACKAGE / "SOURCES.json")["files"]
    check(len(records) == 6, "source count")
    for record in records:
        if record["usage"] != "input":
            continue
        name = record["path"]
        check(name in NAMES and name not in data, "input inventory")
        path = ROOT / name
        check(path.stat().st_size <= 2_000_000, "bounded source")
        raw = path.read_bytes()
        check(hashlib.sha256(raw).hexdigest() == record["sha256"], "input SHA256")
        data[name] = raw
    check(set(data) == set(NAMES), "all four inputs")
    return [json.loads(data[name], object_pairs_hook=no_duplicates) for name in NAMES[:3]]


def reduced(basis):
    """Unique reduced row basis, with descending pivots, over F2."""
    check(type(basis) is list and len(basis) <= 9, "basis list")
    rows = {}
    for vector in basis:
        check(type(vector) is int and 0 < vector < 512, "vector range")
        value = vector
        for pivot in sorted(rows, reverse=True):
            if value >> pivot & 1:
                value ^= rows[pivot]
        check(value != 0, "dependent basis")
        pivot = value.bit_length() - 1
        for old in rows:
            if rows[old] >> pivot & 1:
                rows[old] ^= value
        rows[pivot] = value
    return tuple(rows[p] for p in sorted(rows, reverse=True))


def enumerate_space(basis):
    points = [0]
    for vector in basis:
        points += [v ^ vector for v in points]
    return points


def frames(word):
    paths = {f"{k}{i}": [reduced(word["initial_frames"][f"{k}{i}"])]
             for k in "XY" for i in range(104)}
    check(len(word["program"]) == 4058, "word size")
    for event in word["program"]:
        if event[0] == "transport" and event[1] in paths:
            _, name, before, after, rank = event
            a, b = reduced(before), reduced(after)
            check(a == paths[name][-1] and len(b) - len(a) == rank > 0,
                  "ordered data paths")
            check(set(enumerate_space(a)) < set(enumerate_space(b)), "data nesting")
            paths[name].append(b)
    check(all(path[-1] == reduced(word["final_frames"][name])
              for name, path in paths.items()), "final frames")
    return paths


def graph(flags):
    check(len(flags["helpers"]) == 208, "helper count")
    adjacency = {}
    for helper in flags["helpers"]:
        basis = helper["basis"]
        check(len(basis) == 9, "full flag")
        chain = [reduced(basis[:k]) for k in range(10)]
        for k in range(9):
            adjacency.setdefault(chain[k], set()).add(chain[k + 1])
    return adjacency


def bfs(adjacency, starts):
    reached, queue = set(starts), deque(starts)
    while queue:
        before = queue.popleft()
        for after in adjacency.get(before, ()):
            if after not in reached:
                reached.add(after)
                queue.append(after)
        check(len(reached) <= 4160, "BFS graph bound")
    return reached


def root_list(fixture):
    """Direct E8 doubled-lattice definition, independent of the root generator."""
    roots = []
    for row in product(range(-2, 3), repeat=8):
        if sum(v * v for v in row) != 8 or sum(row) % 4:
            continue
        if any(v % 2 != row[0] % 2 for v in row):
            continue
        if next(v for v in row if v) > 0:
            roots.append(row)
    puncture = fixture["section4_explicit_P104"]
    removed = set(map(tuple, puncture["F0"])) | set(map(tuple, puncture["C"]))
    check(len(roots) == 120 and len(removed) == 16, "E8 root inventory")
    return sorted(set(roots) - removed)


def compare_receipt(word, fixture, flags, receipt):
    paths, adjacency, ports = frames(word), graph(flags), root_list(fixture)
    reachable = [bfs(adjacency, paths[f"X{s}"]) for s in range(104)]
    nodes = {frame for chain in paths.values() for frame in chain}
    nodes.update(adjacency)
    nodes.update(v for values in adjacency.values() for v in values)
    available = [[s for s in range(104) if reachable[s].intersection(paths[f"Y{t}"])]
                 for t in range(104)]
    demands = [[s for s in range(104)
                if sum(ports[t][k] * ports[s][k] for k in range(8)) != 8 * int(s == t)]
               for t in range(104)]
    missing = [[s, t] for t in range(104) for s in demands[t] if s not in available[t]]
    s, t = missing[0]
    cut = reachable[s]
    check(not cut.intersection(paths[f"Y{t}"]), "cut separates target")
    check(all(v in cut for u in cut for v in adjacency.get(u, ())), "cut is closed")
    expected = {"schema_version": 1,
                "scope": "PR2981 fixed full flags; X-only monotone common-chart correction",
                "helpers": 208, "frame_nodes": len(nodes),
                "helper_edges": sum(map(len, adjacency.values())),
                "required_pairs": sum(map(len, demands)),
                "reachable_required_pairs": sum(len(set(d) & set(a)) for d, a in zip(demands, available, strict=True)),
                "missing_required_pairs": len(missing),
                "reachable_source_masks_hex": [hex(sum(1 << v for v in row)) for row in available],
                "required_source_masks_hex": [hex(sum(1 << v for v in row)) for row in demands],
                "missing_source_masks_hex": [hex(sum(1 << v for v in d if v not in a))
                                              for d, a in zip(demands, available, strict=True)],
                "cut": {"source": s, "target": t,
                        "source_root_doubled": list(ports[s]),
                        "target_root_doubled": list(ports[t]),
                        "correction_numerator_over_8": -sum(ports[s][k] * ports[t][k] for k in range(8)),
                        "reachable_frames_hex": [hex(m) for m in sorted(
                            sum(1 << v for v in enumerate_space(basis)) for basis in cut)]}}
    check(json.dumps(expected, sort_keys=True) == json.dumps(receipt, sort_keys=True),
          "independent full receipt equality")
    return expected


if __name__ == "__main__":
    result = compare_receipt(*authenticate(), load(PACKAGE / "RESULT.json"))
    print(f"PASS_P104_FLAG_FLOW_BFS required={result['required_pairs']} "
          f"reachable={result['reachable_required_pairs']} missing={result['missing_required_pairs']}")
