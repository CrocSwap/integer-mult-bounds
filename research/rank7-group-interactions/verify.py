#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the complete five-group interaction domain of PR2979 stage one."""

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

from frames import (
    Invalid,
    build_edges,
    charge,
    difference,
    evaluate,
    frame,
    normalized,
    require,
    vertex,
)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def inputs():
    rows = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    result = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(path.stat().st_size <= 2_000_000, "bounded input size")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input SHA256")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "input Git blob")
        if path.suffix == ".gz":
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(8_000_001)
        require(len(raw) <= 8_000_000, "bounded decoded size")
        result[path.name] = json.loads(raw)
    require(len(result) == 3, "three live inputs")
    return result


def supports(names, edges):
    """Prove separation at register granularity, retaining all zero-rank edges."""
    registers = {}
    counts = Counter()
    trace = []
    for label, register, before, after in edges:
        flags = before[2] | after[2]
        require(flags.bit_count() <= 1, "cross-group charged edge")
        if flags:
            require(not registers.get(register, 0) & ~flags, "cross-group register")
            registers[register] = flags
            counts[flags] += 1
        trace.append([label, register, list(before), list(after)])
    groups = {}
    for index, name in enumerate(names):
        flag = 1 << index
        groups[name] = {
            "registers": sorted(r for r, f in registers.items() if f == flag),
            "dependent_edges": counts[flag],
        }
    return {
        "groups": groups,
        "affected_registers": len(registers),
        "dependent_edges": sum(counts.values()),
        "fixed_edges": len(edges) - sum(counts.values()),
        "cross_group_edges": 0,
        "cross_group_registers": 0,
        "all_edges_sha256": digest(trace),
    }


def add_profiles(base, deltas):
    result = Counter({int(r): n for r, n in base.items()})
    for delta in deltas:
        result.update({int(r): n for r, n in delta.items()})
    return normalized(result)


def require_additivity(profiles, inventories):
    for table in (profiles, inventories):
        deltas = [difference(table[1 << i], table[0]) for i in range(5)]
        for mask in range(32):
            expected = add_profiles(table[0], [deltas[i] for i in range(5) if mask & (1 << i)])
            require(table[mask] == expected, ("all-subset additive identity", mask))


def mobius(table):
    """Full Boolean finite differences, without using the separation claim."""
    values = [Counter({int(r): n for r, n in row.items()}) for row in table]
    for bit in range(5):
        for mask in range(32):
            if mask & (1 << bit):
                values[mask].subtract(values[mask ^ (1 << bit)])
    return [normalized(row) for row in values]


def rejection(action, expected):
    try:
        action()
    except Invalid as error:
        require(expected in str(error), ("unexpected rejection", expected, str(error)))
        return expected
    raise Invalid("mutant accepted: " + expected)


def synthetic_interaction():
    """All four paths are legal; equal rank mass hides a nonzero interaction."""
    start = vertex([])
    left = vertex([1, 2], 1, [1])
    right = vertex([1, 2, 4], 2, [1, 2])
    end = vertex([1, 2, 4])
    edges = [("one", 0, start, left), ("two", 0, left, right), ("end", 0, right, end)]
    profiles = [evaluate(edges, [], [], mask)[0] for mask in range(4)]
    cross = Counter()
    for mask, sign in ((0, 1), (1, -1), (2, -1), (3, 1)):
        cross.update({int(r): sign * n for r, n in profiles[mask].items()})
    require(normalized(cross) == {"1": 2, "2": -1}, "synthetic nonzero interaction")
    require(sum(r * n for r, n in cross.items()) == 0, "rank mass hides interaction")
    rejected = rejection(lambda: supports(["first", "second"], edges), "cross-group charged edge")
    return {"profiles": profiles, "mixed_difference": normalized(cross), "guard": rejected}


def controls(word, record, tables):
    results = {}
    bad = deepcopy(record)
    bad["frame_edits"][0]["gate"][3] *= -1
    results["stale_gate_preimage"] = rejection(lambda: build_edges(word, bad), "gate preimage")
    bad = deepcopy(record)
    bad["frame_edits"].append(deepcopy(bad["frame_edits"][0]))
    results["duplicate_edit"] = rejection(lambda: build_edges(word, bad), "unique gate edit")
    bad = deepcopy(record)
    bad["frame_edits"].pop()
    results["omitted_edit"] = rejection(lambda: build_edges(word, bad), "complete stage-one edit counts")
    bad = deepcopy(record)
    bad["helper_final_changes"]["249"]["old"] = [1]
    results["stale_endpoint"] = rejection(lambda: build_edges(word, bad), "endpoint preimage")
    bad = deepcopy(tables)
    bad[7]["1"] = bad[7].get("1", 0) + 1
    results["triple_only_corruption"] = rejection(
        lambda: require_additivity(bad, tables), "all-subset additive identity"
    )
    bad = deepcopy(tables)
    bad[31]["1"] += 1
    results["full_set_corruption"] = rejection(
        lambda: require_additivity(bad, tables), "all-subset additive identity"
    )
    results["synthetic_shared_register"] = synthetic_interaction()
    results["nonmonotone_path"] = rejection(
        lambda: charge(frame([1, 2]), frame([1]), "fixture"), "nonmonotone"
    )
    return results


def provider(word, record):
    names, edges, guards, widths = build_edges(word, record)
    separation = supports(names, edges)
    profiles, inventories = [], []
    for mask in range(32):
        paid, inventory = evaluate(edges, guards, widths, mask)
        profiles.append(paid)
        inventories.append(inventory)
    require(profiles[0] == word["report"]["local_profile"], "parent profile")
    require(inventories[0] == word["report"]["width_inventory"], "parent inventory")
    require(profiles[31] == record["declared_local_profile"], "full stage profile")
    require(inventories[31] == record["declared_width_inventory"], "full stage inventory")
    require_additivity(profiles, inventories)
    for table in (profiles, inventories):
        coefficients = mobius(table)
        require(all(not coefficients[m] for m in range(32) if m.bit_count() >= 2), "all higher interactions zero")
    return {
        "frame_edges_including_zero": len(edges),
        "warp_center_guards": len(guards),
        "helper_roles": len(widths),
        "separation": separation,
        "isolated_deltas": {
            name: {"profile": difference(profiles[1 << i], profiles[0]),
                   "inventory": difference(inventories[1 << i], inventories[0])}
            for i, name in enumerate(names)
        },
        "subsets": [
            {"mask": m, "groups": [n for i, n in enumerate(names) if m & (1 << i)],
             "profile": profiles[m], "inventory": inventories[m]}
            for m in range(32)
        ],
        "higher_mobius_coefficients_checked": 26,
        "higher_mobius_coefficients_nonzero": 0,
        "controls": controls(word, record, profiles),
    }


def run():
    data = inputs()
    record = data["STAGE1-FRAME-EDITS.json"]
    result = {
        "status": "PASS_RANK7_GROUP_INTERACTIONS",
        "scope": "PR2979 stage-one local frame profiles; no physical idle invoice or supplier admission",
        "providers": {},
    }
    for tag in ("base", "extra"):
        result["providers"][tag] = provider(data[f"PARENT-{tag}.json.gz"], record)
    require(result["providers"]["base"]["isolated_deltas"] == result["providers"]["extra"]["isolated_deltas"], "provider agreement")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit the recomputed receipt instead of comparing it")
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text()), "stored receipt mismatch")
        print("PASS_RANK7_GROUP_INTERACTIONS: 64 subsets; disjoint register supports; controls rejected")


if __name__ == "__main__":
    main()
