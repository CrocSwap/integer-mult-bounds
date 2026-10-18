#!/usr/bin/env python3
"""Exact PR1006 normalization audit plus both unchanged T37 admission engines.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
This is a receipt-comparison audit, not a new supplier or exponent claim.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import runpy
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = "research/t37-slice-bitmaps"
R = runpy.run_path(str(HERE / "receipt.py"))
need, canonical, read = R["need"], R["canonical"], R["read_json"]


def check_sources(root):
    inventory = read(HERE / "SOURCES.json")
    checked = {}
    for row in inventory["files"]:
        if row["usage"] != "input":
            continue
        name = row["path"]
        relative = PurePosixPath(name)
        need(not relative.is_absolute() and ".." not in relative.parts, "source path")
        path = root / name
        need(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), "external source")
        actual = sha256(path.read_bytes()).hexdigest()
        need(actual == row["sha256"], "source pin: " + name)
        checked[name] = actual
    return checked


def fixtures(root):
    manifest = read(root / PREDECESSOR / "SOURCES.json")
    original = read(root / manifest["frozen_receipt"])
    expected = read(root / PREDECESSOR / "EXPECTED.json")["complete_receipt"]
    need(expected["input_sha256"] == manifest["logical_input_hashes"], "predecessor role hashes")
    return manifest, original, expected


def permutation_audit(legacy, manifest, original, expected):
    paths = R["historical_paths"]()
    roles = sorted(R["ROLES"])
    values = [expected["input_sha256"][role] for role in roles]
    need(len(set(values)) == len(roles) == 8, "eight distinct digest premise")
    baseline = canonical(expected)
    counts = dict(permutations=0, legacy_equal=0, strict_equal=0, strict_rejected=0)
    stream = sha256()
    for order in permutations(range(8)):
        changed = dict(original)
        changed["input_sha256"] = {paths[role]: values[index] for role, index in zip(roles, order)}
        legacy_equal = canonical(legacy(changed, manifest)) == baseline
        try:
            strict_equal = canonical(R["compare"](changed, paths, expected)) == baseline
        except ValueError as exc:
            need(str(exc).startswith("input digest for role: "), "unexpected permutation rejection")
            strict_equal = False
            counts["strict_rejected"] += 1
        identity = order == tuple(range(8))
        need(legacy_equal and strict_equal == identity, "permutation classification")
        counts["permutations"] += 1
        counts["legacy_equal"] += int(legacy_equal)
        counts["strict_equal"] += int(strict_equal)
        stream.update(bytes(order) + bytes([legacy_equal, strict_equal]))
    need(counts == dict(permutations=40320, legacy_equal=40320,
                       strict_equal=1, strict_rejected=40319), "complete permutation domain")
    counts["classification_sha256"] = stream.hexdigest()
    roles_to_swap = ("word.json.gz", "local-replay.json")
    changed = deepcopy(original)
    a, b = (paths[role] for role in roles_to_swap)
    changed["input_sha256"][a], changed["input_sha256"][b] = changed["input_sha256"][b], changed["input_sha256"][a]
    counts["smallest_witness"] = {
        "swapped_roles": list(roles_to_swap),
        "changed_fields": {path: {"before": original["input_sha256"][path],
                                   "after": changed["input_sha256"][path]} for path in (a, b)},
        "legacy_normalized_sha256": sha256(canonical(legacy(changed, manifest))).hexdigest(),
        "other_receipt_fields_unchanged": {k: v for k, v in changed.items() if k != "input_sha256"}
                                         == {k: v for k, v in original.items() if k != "input_sha256"},
    }
    return counts


def controls(original, expected):
    paths = R["historical_paths"]()
    accepted, rejected = [], []

    def reject(label, changed, bindings, message):
        try:
            R["compare"](changed, bindings, expected)
        except ValueError as exc:
            need(message in str(exc), label + ": wrong rejection: " + str(exc))
            rejected.append(label)
        else:
            raise ValueError("accepted control: " + label)

    layouts = {
        "historical": paths,
        "relocated POSIX": R["runtime_paths"](PurePosixPath("/relocated/repo"), PurePosixPath("/scratch/run/inputs")),
        "spaces and Unicode POSIX": R["runtime_paths"](PurePosixPath("/review space/repo-κ"), PurePosixPath("/scratch space/inputs-κ")),
        "Windows path labels": R["runtime_paths"](PureWindowsPath("C:/review/repo"), PureWindowsPath("D:/scratch/inputs")),
        "logical labels": {role: role for role in R["ROLES"]},
    }
    for label, bindings in layouts.items():
        value = deepcopy(original)
        value["input_sha256"] = {bindings[role]: expected["input_sha256"][role] for role in reversed(sorted(R["ROLES"]))}
        need(R["compare"](value, bindings, expected) == expected, "relocation: " + label)
        accepted.append(label)
    first, second = paths["word.json.gz"], paths["local-replay.json"]
    changed = deepcopy(original)
    changed["input_sha256"][first] = "0" * 64
    reject("wrong digest", changed, paths, "input digest for role")
    changed = deepcopy(original)
    changed["input_sha256"]["/unrelated/path/word.json.gz"] = changed["input_sha256"].pop(first)
    reject("same basename wrong root", changed, paths, "receipt path inventory")
    changed = deepcopy(original)
    changed["input_sha256"] = {"/unrelated/" + str(i): digest for i, digest in enumerate(changed["input_sha256"].values())}
    reject("all labels replaced", changed, paths, "receipt path inventory")
    changed = deepcopy(original)
    changed["input_sha256"].pop(first)
    reject("missing input", changed, paths, "receipt path inventory")
    changed = deepcopy(original)
    changed["input_sha256"]["/extra"] = changed["input_sha256"][first]
    reject("extra input", changed, paths, "receipt path inventory")
    ambiguous = dict(paths)
    ambiguous["word.json.gz"] = second
    reject("two roles one path", original, ambiguous, "ambiguous path binding")
    incomplete = dict(paths)
    incomplete.pop("word.json.gz")
    reject("missing binding role", original, incomplete, "binding role inventory")
    changed = deepcopy(original)
    changed["roles"] += 1
    reject("changed mathematical count", changed, paths, "complete receipt differs")
    changed = deepcopy(original)
    changed["controls_rejected"] = []
    reject("omitted controls", changed, paths, "complete receipt differs")
    changed = deepcopy(original)
    changed["new_proof_field"] = {"seconds": 1, "passed": False}
    reject("unfamiliar nested field retained", changed, paths, "complete receipt differs")
    changed = deepcopy(original)
    boolean = next(k for k, v in changed.items() if type(v) is bool)
    changed[boolean] = int(changed[boolean])
    reject("boolean changed to integer", changed, paths, "complete receipt differs")
    snapshot = canonical(original)
    normalized = R["normalize"](original, paths, expected["input_sha256"])
    normalized["controls_rejected"].clear()
    need(canonical(original) == snapshot, "normalization mutated caller's receipt")
    accepted.append("caller receipt not mutated")
    return {"accepted": accepted, "rejected": rejected}


def fresh_replays(root, output, expected):
    # Both complete original engines execute unchanged, one at a time.
    adapter = runpy.run_path(str(root / PREDECESSOR / "adapter.py"))
    results = {}
    for engine in ("reference", "bitmap"):
        print("fresh original T37 " + engine + " engine and role-bound receipt comparison", flush=True)
        destination = output / engine
        legacy_result, _ = adapter["run"](None, destination, engine, root)
        raw = read(destination / "receipt.json")
        paths = R["runtime_paths"](root.resolve(), (destination / "inputs").resolve())
        normalized = R["compare"](raw, paths, expected)
        need(canonical(normalized) == canonical(legacy_result), "fresh legacy/strict agreement")
        changed = deepcopy(raw)
        a, b = paths["word.json.gz"], paths["local-replay.json"]
        changed["input_sha256"][a], changed["input_sha256"][b] = changed["input_sha256"][b], changed["input_sha256"][a]
        try:
            R["compare"](changed, paths, expected)
        except ValueError as exc:
            need("input digest for role" in str(exc), "fresh mutation rejection reason")
        else:
            raise ValueError("fresh swapped receipt accepted")
        results[engine] = {
            "complete_receipt_sha256": sha256(canonical(normalized)).hexdigest(),
            "roles": normalized["roles"], "calls": normalized["calls"],
            "inherited_controls": len(normalized["controls_rejected"]) + len(normalized["omitted_edits_rejected"]),
            "swapped_receipt_rejected": True,
        }
    need(results["reference"] == results["bitmap"], "fresh engines differ")
    return results


def run(root, work, fresh=True):
    sources = check_sources(root)
    manifest, original, expected = fixtures(root)
    predecessor = runpy.run_path(str(root / PREDECESSOR / "common.py"))
    R["compare"](original, R["historical_paths"](), expected)
    return {
        "status": "PASS_T37_RECEIPT_ROLE_BINDING",
        "base_commit": read(HERE / "SOURCES.json")["base_commit"],
        "source_sha256": sources,
        "permutation_audit": permutation_audit(predecessor["normalize"], manifest, original, expected),
        "controls": controls(original, expected),
        "fresh_replays": fresh_replays(root, work, expected) if fresh else None,
        "scope": "Receipt role-binding audit and opt-in comparison. The predecessor independently pins and reads its inputs; no wrong owner result, new supplier, speedup, or kappa is established.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="retain fresh stage outputs in a new directory outside the checkout")
    parser.add_argument("--audit-only", action="store_true", help="omit fresh owner-stage replays; not the registered acceptance check")
    parser.add_argument("--write-result", action="store_true", help="explicitly regenerate this package's RESULT.json after a complete replay")
    args = parser.parse_args()
    need(not (args.audit_only and args.write_result), "partial audit cannot replace full result")
    root = args.source_root.resolve()
    if args.output:
        output = args.output.resolve()
        need(not output.exists() and not output.is_relative_to(root), "fresh output outside checkout required")
        output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="t37-receipt-role-binding-") as scratch:
        result = run(root, args.output.resolve() if args.output else Path(scratch), not args.audit_only)
    if args.write_result:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        expected = read(HERE / "RESULT.json")
        if args.audit_only:
            expected["fresh_replays"] = None
        need(canonical(result) == canonical(expected), "complete audit result changed")
    print(result["status"] + ("_AUDIT_ONLY" if args.audit_only else "") +
          ": 40320 legacy-equal permutations; 40319 rejected by role binding; " +
          ("fresh stages omitted" if args.audit_only else "both complete T37 engines agree"))


if __name__ == "__main__":
    main()
