#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent set-span census for the frozen P104 correction paths.

No candidate executable is imported. Python allocates bounded sets during this
finite calculation: 208 paths, 4058 events, 512 binary labels and 10816 pairs.
"""

import hashlib
import json
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "research" / "p104-native-channel" / "inputs"
PINS = {
    "LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
}
# source bypass, target bypass, union, forced demand count, for cuts 1 through 7.
EXPECTED = (
    (336, 0, 336, 4656),
    (336, 0, 336, 4656),
    (252, 92, 320, 4672),
    (168, 168, 312, 4680),
    (92, 252, 320, 4672),
    (0, 336, 336, 4656),
    (0, 336, 336, 4656),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    path = INPUT / name
    need(path.stat().st_size <= 250000, "input byte capacity")
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[name], "pinned input hash")
    return json.loads(raw)


def span(basis):
    need(isinstance(basis, list) and len(basis) <= 9, "frame capacity")
    result = {0}
    for value in basis:
        need(type(value) is int and 0 < value < 512, "binary label")
        result |= {other ^ value for other in tuple(result)}
    return frozenset(result)


def frozen_paths(witness):
    paths = {name: [span(witness["initial_frames"][name])]
             for prefix in ("X", "Y") for name in (f"{prefix}{i}" for i in range(104))}
    program = witness["program"]
    need(len(program) == 4058, "core event capacity")
    for event in program:
        if event[0] == "add":
            need(not event[1].startswith("X"), "original sources are immutable")
            need(not event[2].startswith("Y"), "original targets have no feedback")
        if event[0] != "transport" or event[1] not in paths:
            continue
        before, after = span(event[2]), span(event[3])
        path = paths[event[1]]
        need(path[-1] == before and before < after, "nested original path")
        path.append(after)
    for name, path in paths.items():
        need(path[-1] == span(witness["final_frames"][name]), "terminal binding")
        need(len(path) <= 10, "path length capacity")
    return paths


def correction_pairs(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.add(tuple(root))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    need(len(roots) == 120, "E8 root-line count")
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in puncture["F0"] + puncture["C"]}
    need(len(removed) == 16 and removed <= roots, "P104 puncture")
    ports = sorted(roots - removed)
    demands = {(s, t) for s in range(104) for t in range(104)
               if 8 * int(s == t) != sum(ports[s][i] * ports[t][i] for i in range(8))}
    need(len(demands) == 4992, "correction support count")
    return demands


def odd_functional(labels):
    candidates = [q for q in range(1, 512)
                  if all((q & value).bit_count() % 2 == 1 for value in labels)]
    need(len(candidates) == 1, "unique affine parity functional")
    return candidates[0]


def label_checks(paths, demands):
    source = [paths[f"X{s}"][0] for s in range(104)]
    target = [paths[f"Y{t}"][-1] for t in range(104)]
    need(all(len(line) == 2 for line in source), "initial source lines")
    need(all(len(hyperplane) == 256 for hyperplane in target), "target hyperplanes")
    need(len(set(source)) == len(set(target)) == 104, "distinct source and target labels")
    normals = []
    for hyperplane in target:
        choices = [n for n in range(1, 512)
                   if all((n & value).bit_count() % 2 == 0 for value in hyperplane)]
        need(len(choices) == 1, "unique target normal")
        normals.append(choices[0])
    labels = [next(iter(line - {0})) for line in source]
    source_parity, normal_parity = odd_functional(labels), odd_functional(normals)
    need(all(source[s] <= target[t] for s, t in demands), "demand incidence")
    return source_parity, normal_parity, normals


def census(paths, demands):
    rows = []
    for cut in range(1, 8):
        source_bypass, target_bypass = set(), set()
        for s, t in demands:
            source_path, target_path = paths[f"X{s}"], paths[f"Y{t}"]
            if any(len(frame) > 2**cut and frame <= target_path[-1]
                   for frame in source_path):
                source_bypass.add((s, t))
            if any(len(frame) <= 2**cut and source_path[0] <= frame
                   for frame in target_path):
                target_bypass.add((s, t))
        union = source_bypass | target_bypass
        rows.append((len(source_bypass), len(target_bypass), len(union), len(demands - union)))
    return tuple(rows)


def main():
    witness, fixture = load("LOWRANK-WITNESS.json"), load("P104-FIXTURE.json")
    paths = frozen_paths(witness)
    demands = correction_pairs(fixture)
    _, parity, normals = label_checks(paths, demands)
    rows = census(paths, demands)
    need(rows == EXPECTED, "independent per-cut bypass census")
    # These controls distinguish the relevant mathematical predicates directly.
    need(rows[2][3] != rows[3][3], "wrong-cut control")
    need(len(demands) - rows[3][0] != rows[3][3], "omitted target-bypass control")
    need(len(demands) - rows[3][1] != rows[3][3], "omitted source-bypass control")
    changed = normals.copy()
    changed[0] ^= parity & -parity
    need(not all((parity & n).bit_count() % 2 == 1 for n in changed), "normal-parity control")
    need((4680 - 482 + 62) // 63 == 67, "mixed-shape corollary")
    print("PASS_P104_INDEPENDENT_CROSSING_CAPACITY forced_cut4=4680 controls=4")


if __name__ == "__main__":
    main()
