#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded composition checks; retains PR3018 geometry and interval checkers.

This is a finite allocation and moment receipt, not supplier/outer admission.
Managed Python storage is bounded by 666 calls, 271728 roles, 103 journal edits,
and two pinned words with fewer than 20000 gates each.
"""

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAIN = ROOT / "research/rank7-joint-endframes"
EXPECTED = {1: 1644352, 2: 470862, 3: 159472, 4: 71928,
            5: 13710, 8: 5328, 14: 1, 48: 28190}
DELTA = {1: 4, 3: 4, 5: -6, 14: 1}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    path = Path(path)
    data = path.read_bytes()
    need(len(data) <= 20_000_000, "compressed input limit")
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    need(len(data) <= 40_000_000, "decoded input limit")
    return json.loads(data)


def authenticate(root=ROOT, package=PACKAGE):
    """Authenticate live inputs and all vendor bytes before retained imports.

    Historical provenance rows belong to the registered package runner's check.
    """
    pins = [(root, row) for row in read(package / "SOURCES.json")["files"]
            if row.get("usage") == "input"]
    pins += [(package, row) for row in read(package / "VENDOR.json")]
    need(1 <= len(pins) <= 100, "source pin count")
    result = {}
    for base, row in pins:
        relative = Path(row["path"])
        need(not relative.is_absolute() and ".." not in relative.parts, "source path")
        actual = hashlib.sha256((base / relative).read_bytes()).hexdigest()
        need(actual == row["sha256"], "source drift: " + str(relative))
        result[str(relative)] = actual
    return result


def retained_checkers():
    authenticate()
    modules = []
    for name in ("geometry", "moment"):
        path = PACKAGE / "vendor/pr3018" / (name + ".py")
        spec = importlib.util.spec_from_file_location("composition_" + name, path)
        need(spec is not None and spec.loader is not None, "checker import")
        module = importlib.util.module_from_spec(spec)
        previous = sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        modules.append(module)
    return tuple(modules)


def apply_exchange(fill, journal):
    need(type(fill) is dict and type(fill.get("rows")) is list, "fill shape")
    need(len(fill["rows"]) == 271728, "complete role count")
    edits = journal.get("edits")
    need(type(edits) is list and len(edits) == 103, "103 journal edits")
    result, seen = copy.deepcopy(fill), set()
    for edit in edits:
        need(type(edit) is list and len(edit) == 3, "journal edit shape")
        index, old, new = edit
        need(type(index) is int and 0 <= index < 271728, "journal index")
        need(index not in seen, "duplicate journal edit")
        need(type(old) is list and type(new) is list, "journal row shape")
        need(len(old) == len(new) == 6, "journal row shape")
        need(all(type(x) is int for x in old + new), "integer journal row")
        need(fill["rows"][index] == old, "journal preimage")
        need(old[:2] == new[:2] and old != new, "journal helper identity")
        result["rows"][index] = new.copy()
        seen.add(index)
    need(sum(a != b for a, b in zip(fill["rows"], result["rows"], strict=True)) == 103,
         "literal changed row count")
    return result


def composed_fill():
    authenticate()
    return apply_exchange(read(MAIN / "allocation/FILL.json.gz"),
                          read(PACKAGE / "vendor/pr3018/EXCHANGE.json"))


def scalar_action(gates):
    """Exact three-register linear action, ignoring frame annotations only."""
    registers = {22: 0, 61: 1, 63: 2}
    matrix = [[Fraction(i == j) for j in range(3)] for i in range(3)]
    need(type(gates) is list and 1 <= len(gates) <= 3, "R1 gate count")
    for gate in gates:
        need(type(gate) is list and len(gate) == 6 and gate[0] == "add", "R1 add")
        _, target, source, numerator, denominator, _ = gate
        need(target in registers and source in registers, "R1 register")
        need(type(numerator) is int and type(denominator) is int and denominator != 0,
             "R1 rational scalar")
        target, source = registers[target], registers[source]
        scale = Fraction(numerator, denominator)
        matrix[target] = [a + scale * b for a, b in zip(matrix[target], matrix[source], strict=True)]
    return matrix


def cleanup(word):
    """Derive inverse-reverse cleanup, with one private slot per restored helper."""
    need(len(word["A"]) + len(word["B"]) + len(word["restore"]) < 20000,
         "word gate limit")
    restored = set(map(int, word["helper_final"]))
    need(len(restored) == 91, "91 private buffers")
    offset = 2 * word["report"]["v"] + word["report"]["R"]
    full = [1 << i for i in range(word["report"]["h"] - 1, -1, -1)]
    warps = {}
    for number, record in enumerate(word["warps"], 1):
        warps.setdefault(record[0], []).append(["warp", record[1], number])
    forward = word["A"][word["prelude_events"]:].copy()
    for position in range(len(word["B"]) + 1):
        forward.extend(warps.get(position, []))
        if position < len(word["B"]):
            forward.append(word["B"][position])
    forward.extend(word["restore"])
    result = []
    for gate in reversed(forward):
        if gate[0] != "warp" and 112 <= gate[1] < 224:
            continue
        target = gate[1] + offset if gate[1] in restored else gate[1]
        if gate[0] == "warp":
            result.append(["warp", target, -gate[2], full])
        elif gate[0] == "add":
            source = gate[2] + offset if gate[2] in restored else gate[2]
            result.append(["add", target, source, -gate[3], gate[4], full])
        else:
            need(gate[0] == "scale", "cleanup gate kind")
            result.append(["scale", target, gate[3], gate[2], full])
    return result


def check_word(old, new, edits):
    need(set(old) == set(new), "word keys")
    need(type(edits) is list and len(edits) == 1, "one R1 edit")
    edit = edits[0]
    need((edit["id"], edit["section"], edit["start"], edit["stop"]) ==
         ("R1", "restore", 178, 180), "R1 address")
    need(old["restore"][178:180] == edit["old"], "R1 preimage")
    need(scalar_action(edit["old"]) == scalar_action(edit["new"]), "R1 scalar identity")
    need(new["restore"] == old["restore"][:178] + edit["new"] + old["restore"][180:],
         "literal R1 restore sequence")
    need({key for key in old if old[key] != new[key]} == {"restore", "report", "cleanup"},
         "only declared word fields change")
    before, after = old["report"], new["report"]
    need(before["width_inventory"] == after["width_inventory"], "width inventory")
    need(before.keys() == after.keys(), "report fields")
    need(all(before[k] == after[k] for k in before if k != "local_profile"),
         "report invariant")
    delta = Counter({int(k): v for k, v in after["local_profile"].items()})
    delta.subtract({int(k): v for k, v in before["local_profile"].items()})
    need({k: v for k, v in delta.items() if v} == {1: -2, 2: 1}, "R1 profile delta")
    need(cleanup(old) == old["cleanup"] and cleanup(new) == new["cleanup"],
         "literal inverse cleanup with all private buffers")
    return {"edit": "R1", "private_buffers": 91, "scalar_identity": "exact 3x3 rational"}


def inputs():
    dispatch_rows = read(MAIN / "allocation/DISPATCH.json")
    need(type(dispatch_rows) is list and len(dispatch_rows) == 666, "dispatch rows")
    dispatch = {(s, o): p for s, o, p in dispatch_rows}
    need(len(dispatch) == 666, "duplicate dispatch")
    return (read(MAIN / "allocation/ORDER.json"), dispatch,
            read(MAIN / "allocation/vendor/PLAN.json.gz"),
            read(MAIN / "allocation/vendor/TEMPLATE.json.gz"),
            read(PACKAGE / "vendor/pr3015/allocation/PROVIDERS.json"))


def check_allocation(geometry, fill, data, buffers=91, claimed=EXPECTED):
    need(type(buffers) is int and buffers == 91, "91 private buffers")
    order, dispatch, plan, template, providers = data
    result = geometry.check(order, fill, dispatch, plan, template, providers, buffers)
    need(result["profile"] == claimed, "literal complete profile")
    need(result["physical"] == 66813 and result["rank_mass"] == 4816512,
         "complete physical and rank accounting")
    return result


def check_providers(providers):
    before = read(MAIN / "allocation/PROVIDERS.json")
    need(set(before) == set(providers) == {"extra", "gauge44"}, "provider identities")
    declared = read(PACKAGE / "vendor/pr3015/edits/EDITS.json")["declared"]
    for name in providers:
        need(providers[name]["widths"] == before[name]["widths"], "ordered helper widths")
        need(Counter(map(str, providers[name]["widths"])) ==
             Counter(declared["width_inventory"]), "literal width inventory")
        need(providers[name]["actual_paid_profile"] == declared["local_profile"],
             "provider profile agrees with word")


def moment_receipt(moment, baseline, profile):
    old_interval, new_interval = moment.root(baseline), moment.root(profile)
    gain = new_interval[0] - old_interval[1], new_interval[1] - old_interval[0]
    need(gain[0] > 0, "strict complete moment improvement")
    return {"baseline_root": list(map(str, old_interval)),
            "new_root": list(map(str, new_interval)), "gain": list(map(str, gain)),
            "sign_certificate": moment.sign_certificate()}


def run():
    pins = authenticate()
    geometry, moment = retained_checkers()
    data = inputs()
    check_providers(data[-1])
    edits = read(PACKAGE / "vendor/pr3015/edits/EDITS.json")["edits"]
    words = {}
    for variant in ("base", "extra"):
        words[variant] = check_word(read(MAIN / ("data/WORD-" + variant + ".json.gz")),
            read(PACKAGE / ("vendor/pr3015/edits/FINAL-WORD-" + variant + ".json.gz")),
            edits[variant])
    baseline = read(PACKAGE / "vendor/pr3015/CLAIM.json")
    baseline = {int(k): v for k, v in baseline["profile"].items()}
    original = read(MAIN / "allocation/FILL.json.gz")
    check_allocation(geometry, original, data, claimed=baseline)
    result = check_allocation(geometry, composed_fill(), data)
    delta = {rank: EXPECTED.get(rank, 0) - baseline.get(rank, 0)
             for rank in EXPECTED.keys() | baseline.keys()}
    need({k: v for k, v in delta.items() if v} == DELTA, "packing profile delta")
    result.pop("bin_pattern_histogram")
    result.update(moment_receipt(moment, baseline, EXPECTED))
    result.update({"status": "PASS_RESTORE_PACKING_COMPOSITION_FINITE",
        "journal_edits": 103, "packing_delta": DELTA, "words": words,
        "source_sha256": pins,
        "retained_checkers": "PR3018 geometry.py and moment.py, authenticated unchanged",
        "scope": "Finite allocation and conditional moment; supplier/outer admission not checked."})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(run(), sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
