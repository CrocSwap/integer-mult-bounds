# SPDX-License-Identifier: Apache-2.0
"""Necessary coefficient reachability for PR2981's fixed P104 helper flags."""

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"
FLAGS = "research/p104-joint-unit-flags/CERTIFICATE.json"
CREDIT = "research/p104-joint-unit-flags/README.md"
INPUTS = {WORD, FIXTURE, FLAGS, CREDIT}


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


def inputs():
    records = read_json(PACKAGE / "SOURCES.json")["files"]
    require(len(records) == 6, "six source records")
    data = {}
    for record in records:
        if record["usage"] != "input":
            continue
        name = record["path"]
        require(name in INPUTS and name not in data, "exact input inventory")
        path = ROOT / name
        require(path.stat().st_size <= 2_000_000, "input size bound")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == record["sha256"], "input SHA256")
        data[name] = raw
    require(set(data) == INPUTS, "four authenticated inputs")
    return [json.loads(data[name], object_pairs_hook=unique) for name in (WORD, FIXTURE, FLAGS)]


def span(basis):
    require(type(basis) is list and len(basis) <= 9, "basis size")
    points = {0}
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "binary vector")
        require(vector not in points, "basis independence")
        points |= {v ^ vector for v in points}
    return sum(1 << point for point in points)


def data_paths(word):
    paths = {f"{kind}{i}": [] for kind in "XY" for i in range(104)}
    for name in paths:
        paths[name].append(span(word["initial_frames"][name]))
    require(len(word["program"]) == 4058, "original event count")
    for event in word["program"]:
        if event[0] != "transport" or event[1] not in paths:
            continue
        _, name, before, after, rank = event
        old, new = span(before), span(after)
        require(paths[name][-1] == old and old != new and old & new == old,
                "strict nested data transport")
        require(rank == len(after) - len(before), "data transport rank")
        paths[name].append(new)
    for name, path in paths.items():
        require(len(path) <= 10 and path[-1] == span(word["final_frames"][name]),
                "complete data path")
    return paths


def ordered_roots(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *row) for row in product((-1, 1), repeat=7) if row.count(-1) % 2 == 0]
    puncture = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in puncture["F0"] + puncture["C"]}
    ports = sorted(set(roots) - removed)
    require(len(roots) == 120 and len(removed) == 16 and len(ports) == 104,
            "ordered P104 roots")
    return ports


def helper_graph(certificate, paths):
    rows = certificate["helpers"]
    require(type(rows) is list and len(rows) == 208, "208 fixed flags")
    edges, slots_x, slots_y = set(), set(), set()
    for row in rows:
        s, t, d, a = [row[k] for k in ("source", "target", "departure_choice", "arrival_choice")]
        require(all(type(v) is int for v in (s, t, d, a))
                and 0 <= s < 104 and 0 <= t < 104 and d in (0, 1) and a in (0, 1),
                "flag endpoint slots")
        require((s, d) not in slots_x and (t, a) not in slots_y, "slot bijections")
        slots_x.add((s, d))
        slots_y.add((t, a))
        basis = row["basis"]
        require(len(basis) == 9, "complete unit-step flag")
        chain = [span(basis[:k]) for k in range(10)]
        require(chain[1] == paths[f"X{s}"][0]
                and chain[8] == paths[f"Y{t}"][-1], "flag data endpoints")
        edges.update(zip(chain, chain[1:], strict=False))
    return edges


def propagate(paths, edges):
    """One topological pass of source bitsets, merging all equal-frame contacts."""
    nodes = {frame for path in paths.values() for frame in path}
    outgoing = {}
    for before, after in edges:
        require(before != after and before & after == before, "forward nested edge")
        nodes.update((before, after))
        outgoing.setdefault(before, set()).add(after)
    require(len(nodes) <= 4160 and len(edges) <= 1872, "fixed graph bounds")
    reach = dict.fromkeys(nodes, 0)
    for source in range(104):
        for frame in paths[f"X{source}"]:
            reach[frame] |= 1 << source
    for frame in sorted(nodes, key=int.bit_count):
        for after in outgoing.get(frame, ()):
            reach[after] |= reach[frame]
    outputs = []
    for target in range(104):
        mask = 0
        for frame in paths[f"Y{target}"]:
            mask |= reach[frame]
        outputs.append(mask)
    return reach, outputs


def cut_witness(source, target, paths, edges, reach, ports):
    closed = {frame for frame, mask in reach.items() if mask >> source & 1}
    require(set(paths[f"X{source}"]) <= closed, "cut contains every source snapshot")
    require(not set(paths[f"Y{target}"]) & closed, "cut separates every target frame")
    require(all(u not in closed or v in closed for u, v in edges), "forward-closed cut")
    gram4 = sum(a * b for a, b in zip(ports[source], ports[target], strict=True))
    require(source != target and gram4 in (-4, 4), "nonzero off-diagonal correction")
    return {"source": source, "target": target, "correction_numerator_over_8": -gram4,
            "source_root_doubled": list(ports[source]),
            "target_root_doubled": list(ports[target]),
            "reachable_frames_hex": [hex(frame) for frame in sorted(closed)]}


def compute(word, fixture, flags):
    paths, ports = data_paths(word), ordered_roots(fixture)
    edges = helper_graph(flags, paths)
    reach, outputs = propagate(paths, edges)
    required, missing, required_reachable = [], [], []
    for target in range(104):
        demand = []
        for source in range(104):
            gram4 = sum(a * b for a, b in zip(ports[target], ports[source], strict=True))
            label = paths[f"X{source}"][0].bit_length() - 1
            require(bool(paths[f"Y{target}"][-1] >> label & 1) == (gram4 % 8 == 4),
                    "root order and endpoint pairing binding")
            if gram4 != 8 * int(source == target):
                demand.append(source)
        required.append(demand)
        required_reachable.append([s for s in demand if outputs[target] >> s & 1])
        missing.extend([s, target] for s in demand if not (outputs[target] >> s & 1))
    require(sum(map(len, required)) == 4992 and missing, "nontrivial correction obstruction")
    source, target = missing[0]
    return {"schema_version": 1, "scope": "PR2981 fixed full flags; X-only monotone common-chart correction",
            "helpers": 208, "frame_nodes": len(reach), "helper_edges": len(edges),
            "required_pairs": sum(map(len, required)),
            "reachable_required_pairs": sum(map(len, required_reachable)),
            "missing_required_pairs": len(missing),
            "reachable_source_masks_hex": [hex(value) for value in outputs],
            "required_source_masks_hex": [hex(sum(1 << s for s in row)) for row in required],
            "missing_source_masks_hex": [hex(sum(1 << s for s in row if not (outputs[t] >> s & 1)))
                                         for t, row in enumerate(required)],
            "cut": cut_witness(source, target, paths, edges, reach, ports)}


def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(typed_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right, strict=True))
    return left == right


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a regenerated receipt")
    args = parser.parse_args()
    result = compute(*inputs())
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    require(typed_equal(result, read_json(PACKAGE / "RESULT.json")), "complete typed receipt equality")
    print(f"PASS_P104_FLAG_FLOW required={result['required_pairs']} "
          f"reachable={result['reachable_required_pairs']} missing={result['missing_required_pairs']}")


if __name__ == "__main__":
    main()
