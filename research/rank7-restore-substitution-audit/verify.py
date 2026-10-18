# SPDX-License-Identifier: Apache-2.0
"""Code-disjoint rational substitution and finite-set frame audit of PR3042."""

import copy
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from frames import registers, require, trace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PARENT = ROOT / "research/rank7-joint-endframes"
EXPECTED_PARENT = {1: 2445, 2: 706, 3: 232, 4: 108, 5: 18, 8: 8}
EXPECTED_FINAL = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}


def read(path):
    raw = path.read_bytes()
    require(len(raw) <= 3_000_000, "bounded compressed/JSON input")
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    require(len(raw) <= 8_000_000, "bounded decoded input")
    return json.loads(raw)


def check_pins():
    sources = read(PACKAGE / "SOURCES.json")
    vendor = read(PACKAGE / "VENDOR.json")
    for inventory, base in ((sources["files"], ROOT), (vendor["files"], PACKAGE)):
        require(len(inventory) <= 32, "bounded source inventory")
        for record in inventory:
            if record.get("usage") == "provenance":
                continue
            path = base / record["path"]
            require(path.resolve().is_relative_to(base), "contained source path")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                    f"source digest: {record['path']}")
    for name, digest in vendor["unchanged_allocation"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                f"unchanged PR3042 allocation: {name}")
    return sources, vendor


def operator(gates, universe):
    """Sparse rational matrix on independent dirty input columns."""
    require(len(gates) <= 1000 and len(universe) <= 704, "bounded scalar operator")
    rows = {register: {register: Fraction(1)} for register in universe}
    for gate in gates:
        kind, target = gate[:2]
        require(kind in ("add", "scale"), "scalar substitution only")
        require(all(r in rows for r in registers(gate)), "operator registers")
        if kind == "scale":
            require(len(gate) == 5 and gate[3] != 0, "scale shape and denominator")
            factor = Fraction(gate[2], gate[3])
            require(factor != 0, "invertible scale")
            rows[target] = {r: factor * value for r, value in rows[target].items()}
        else:
            require(len(gate) == 6 and gate[4] != 0, "ADD shape and denominator")
            require(target != gate[2], "distinct ADD operands")
            factor = Fraction(gate[3], gate[4])
            row = rows[target].copy()
            for register, value in rows[gate[2]].items():
                row[register] = row.get(register, Fraction(0)) + factor * value
            rows[target] = {r: value for r, value in row.items() if value}
    return rows


def equal_operators(before, after):
    universe = sorted({r for gate in before + after for r in registers(gate)})
    require(operator(before, universe) == operator(after, universe),
            "rational dirty-state substitution differs")
    return len(universe)


def apply_hunks(parent, edits):
    require(len(edits) == 2, "two named literal edits")
    require([edit["id"] for edit in edits] == ["R1_E42", "R2_E7"], "edit identifiers")
    changed = copy.deepcopy(parent)
    previous_stop = -1
    for edit in edits:
        start, stop = edit["start"], edit["stop"]
        require(edit["section"] == "restore" and previous_stop < start < stop,
                "disjoint source-addressed restore hunks")
        require(parent["restore"][start:stop] == edit["old"], "literal preimage")
        equal_operators(edit["old"], edit["new"])
        previous_stop = stop
    for edit in reversed(edits):
        changed["restore"][edit["start"]:edit["stop"]] = copy.deepcopy(edit["new"])
    return changed


def expected_cleanup(word):
    """Inverse reverse, using an injective renaming for every restored helper."""
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    restored = set(map(int, word["helper_final"]))
    require(len(restored) == 91, "91 restored helpers")
    forward = list(word["A"][word["prelude_events"]:])
    warps = {}
    for index, record in enumerate(word["warps"], 1):
        warps.setdefault(record[0], []).append(["warp", record[1], index])
    for index in range(len(word["B"]) + 1):
        forward.extend(warps.get(index, []))
        if index < len(word["B"]):
            forward.append(word["B"][index])
    forward.extend(word["restore"])
    require(len(forward) <= 60000, "bounded cleanup body")
    cleanup = []
    for gate in reversed(forward):
        kind, target = gate[:2]
        if kind != "warp" and 112 <= target < 224:
            continue
        target = target + 704 if target in restored else target
        if kind == "warp":
            inverse = [kind, target, -gate[2], full]
        elif kind == "scale":
            inverse = [kind, target, gate[3], gate[2], full]
        else:
            source = gate[2] + 704 if gate[2] in restored else gate[2]
            inverse = [kind, target, source, -gate[3], gate[4], full]
        cleanup.append(inverse)
    return cleanup


def signed_delta(before, after):
    return {rank: after.get(rank, 0) - before.get(rank, 0)
            for rank in sorted(set(before) | set(after))
            if after.get(rank, 0) != before.get(rank, 0)}


def check_variant(parent, candidate, edits):
    rebuilt = apply_hunks(parent, edits)
    require(set(parent) == set(candidate), "same word sections")
    changed_sections = {key for key in parent if parent[key] != candidate[key]}
    require(changed_sections == {"restore", "cleanup", "report"}, "exact changed sections")
    require(rebuilt["restore"] == candidate["restore"], "literal final restore")
    equal_operators(parent["restore"], candidate["restore"])
    require(candidate["cleanup"] == expected_cleanup(candidate), "derived cleanup")
    buffers = {r for gate in candidate["cleanup"] for r in registers(gate) if r >= 704}
    require(buffers == {704 + int(r) for r in candidate["helper_final"]}, "private buffers")
    old, new = trace(parent), trace(candidate)
    require(old["profile"] == EXPECTED_PARENT and new["profile"] == EXPECTED_FINAL,
            "independently recounted local profiles")
    require(old["widths"] == new["widths"], "unchanged ordered helper widths")
    inventory = Counter(new["widths"])
    require(inventory == {4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213}, "inventory")
    require({int(r): n for r, n in candidate["report"]["width_inventory"].items()}
            == inventory, "reported inventory")
    require({int(r): n for r, n in candidate["report"]["local_profile"].items()}
            == new["profile"], "reported local profile")
    isolated = []
    for edit, expected_delta in zip(edits, ({1: -8, 2: 4}, {1: -4, 2: 2}), strict=True):
        alone = copy.deepcopy(parent)
        alone["restore"][edit["start"]:edit["stop"]] = edit["new"]
        alone_trace = trace(alone)
        require(signed_delta(old["profile"], alone_trace["profile"]) == expected_delta,
                "separate edit delta")
        skipped = [r for r in range(704)
                   if Counter(b - a for _, a, b in old["histories"][r])
                   != Counter(b - a for _, a, b in alone_trace["histories"][r])]
        require(skipped == ([22, 40, 54, 63] if edit["id"] == "R1_E42" else [5, 73]),
                "literal skipped-register attribution")
        isolated.append({"edit": edit["id"], "old_gates": len(edit["old"]),
                         "new_gates": len(edit["new"]), "delta": expected_delta,
                         "skipped_registers": skipped})
    changed = {}
    for register in range(704):
        before = Counter(b - a for _, a, b in old["histories"][register])
        after = Counter(b - a for _, a, b in new["histories"][register])
        if before != after:
            changed[register] = {"delta": signed_delta(before, after),
                                 "before": old["histories"][register],
                                 "after": new["histories"][register]}
    require(set(changed) == {5, 22, 40, 54, 63, 73}, "six changed register bills")
    require(all(item["delta"] == {1: -2, 2: 1} for item in changed.values()),
            "every skip replaces two rank-one children with one rank-two child")
    return {"edits": isolated, "changed_registers": changed, "private_buffers": len(buffers),
            "profile": new["profile"], "width_inventory": dict(sorted(inventory.items()))}


def whole_bill(parent_profile, candidate_profile):
    calls, replicas, live, private = 666, 74, 66304, 91
    delta = signed_delta(EXPECTED_PARENT, EXPECTED_FINAL)
    expected = {rank: count + calls * delta.get(rank, 0)
                for rank, count in parent_profile.items()}
    require(expected == candidate_profile, "complete profile, unchanged idle bill")
    mass = sum(rank * count for rank, count in candidate_profile.items())
    require(mass == replicas * 65088 == 4816512, "complete rank mass")
    require(live + 408 + 8 + private + 2 == 66813, "full physical stock")
    return {"calls": calls, "replicas": replicas, "profile": candidate_profile,
            "delta": signed_delta(parent_profile, candidate_profile), "rank_mass": mass,
            "physical_families": 66813, "private_buffers": private}


def audit():
    sources, vendor = check_pins()
    spec = read(PACKAGE / "vendor/EDITS.json")
    variants = {}
    for variant in ("base", "extra"):
        parent = read(PARENT / f"data/WORD-{variant}.json.gz")
        candidate = read(PACKAGE / f"vendor/FINAL-WORD-{variant}.json.gz")
        variants[variant] = check_variant(parent, candidate, spec["edits"][variant])
    before = {int(r): n for r, n in read(PARENT / "allocation/PROFILE.json").items()}
    after = {int(r): n for r, n in read(PACKAGE / "vendor/PROFILE.json").items()}
    return {"status": "PASS_RANK7_RESTORE_SUBSTITUTION_AUDIT", "variants": variants,
            "bill": whole_bill(before, after), "source_head": vendor["head"],
            "base_commit": sources["base_commit"],
            "scope": "Independent rational restore equality and frame/invoice delta. "
                     "Baseline owner legality and native/physical/all-size/outer "
                     "contracts remain premises."}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
