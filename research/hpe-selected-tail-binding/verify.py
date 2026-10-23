#!/usr/bin/env python3
"""Check the selected HPE pair slice against the Lean literals and premise."""

import argparse
import ast
import copy
import gzip
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RECORD = Path("certificates/selected-result.json")
SOURCE = Path("research/community-frontier1094-audit/SELECTED-SOURCE.json")
WORD = Path("research/gauge44-slots-t16/evidence/local/CANONICAL-WORD.json.gz")
ADAPTERS = Path("research/gauge44-slots-t16/evidence/local/RESIDUAL-ADAPTERS.json")
LEAN = Path("research/hyperplane-end-lean/HyperplaneEnd/Exact.lean")
TAIL_LEAN = Path("research/hyperplane-end-lean/HyperplaneEnd/Tail.lean")
MAIN_LEAN = Path("research/hyperplane-end-lean/HyperplaneEnd/Main.lean")
LABELS_LEAN = Path("research/hyperplane-end-lean/HyperplaneEnd/Labels.lean")
INSTANCE_CHECKER = Path("research/hyperplane-end-lean/code/check_hpe_pairs.py")
FIELDS = ("quadratic_rows", "linear_Z4", "matrix_rows", "offset", "phase")
EXPECTED_COUNTS = {"pair1": 12, "pair2": 12, "pair3": 10}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    return {row["path"]: row["sha256"] for row in sources["files"] if row["usage"] == "input"}


def exact_pairs(lean_text):
    result = {}
    names = {}
    for n in (1, 2, 3):
        match = re.search(r"def pair%d : Pair := (.*?)\n\n" % n, lean_text, re.S)
        require(match is not None, f"Lean literal pair{n} is absent")
        data = ast.literal_eval(match[1].replace("⟨", "[").replace("⟩", "]"))
        entrance, terminal, left, right = data
        key = (tuple(entrance), tuple(terminal))
        require(key not in result, "Lean pair literals are not distinct")
        result[key] = {
            "left": dict(zip(FIELDS, left, strict=True)),
            "right": dict(zip(FIELDS, right, strict=True)),
        }
        names[key] = f"pair{n}"
    require(len(result) == 3, "Expected exactly three Lean pair literals")
    return result, names


def inspect_word(word, adapters, pairs, pair_names, *, controls=False):
    tail = word.get("tail")
    require(isinstance(tail, list) and len(tail) == 94, "Selected tail inventory changed")
    op_counts = {op: sum(gate[0] == op for gate in tail) for op in ("add", "scale")}
    require(op_counts == {"add": 78, "scale": 16}, f"Selected tail operation counts changed: {op_counts}")
    frames = word["frames"]
    starts = word["start"]
    finals = word["final"]
    matched = []
    counts = {"pair1": 0, "pair2": 0, "pair3": 0}
    for gate_index, gate in enumerate(tail):
        require(isinstance(gate, list) and len(gate) in (5, 6), f"Malformed tail record {gate_index}")
        require(gate[0] in ("add", "scale"), f"Unknown tail operation at record {gate_index}")
        if gate[0] == "scale":
            continue
        require(len(gate) == 6, f"Malformed add tail record {gate_index}")
        _, helper, partner, _, _, terminal = gate
        require(isinstance(helper, int) and isinstance(partner, int), f"Bad register index at tail {gate_index}")
        entrance = starts[helper]
        key = (tuple(frames[entrance]), tuple(frames[terminal]))
        if key not in pairs:
            continue
        matched.append((gate_index, gate, key, entrance, terminal))
        counts[pair_names[key]] += 1

    require(len(matched) == sum(EXPECTED_COUNTS.values()), "Selected Lean-pair slice changed")
    require(counts == EXPECTED_COUNTS, f"Unexpected per-pair coverage: {counts}")
    helpers = [gate[1] for _, gate, _, _, _ in matched]
    require(len(set(helpers)) == len(helpers), "A selected helper has multiple matching tail records")

    for gate_index, gate, key, entrance, terminal in matched:
        helper, partner = gate[1], gate[2]
        require(gate[0] == "add" and gate[3:5] == [-1, 1], f"Selected tail {gate_index} is not h -= p")
        require(helper != partner, f"Selected tail {gate_index} has a self-partner")
        require(finals[helper] == terminal, f"Selected tail {gate_index} has the wrong final frame")
        recipe_key = f"{entrance}:{terminal}"
        recipe = adapters["recipes"].get(recipe_key)
        require(recipe is not None, f"Missing adapter recipe {recipe_key}")
        require(recipe["rank"] == 7, f"Wrong adapter rank for {recipe_key}")
        require(recipe["left"] == pairs[key]["left"], f"Left adapter differs from Lean pair at {recipe_key}")
        require(recipe["right"] == pairs[key]["right"], f"Right adapter differs from Lean pair at {recipe_key}")

    report = {
        "total_tail_records": len(tail),
        "operation_counts": op_counts,
        "lean_pair_tail_records": len(matched),
        "distinct_helpers": len(set(helpers)),
        "pair_counts": counts,
        "other_tail_records": len(tail) - len(matched),
        "self_partner_records": 0,
        "exact_recipe_records": len(matched),
    }

    if controls:
        first_index = matched[0][0]
        mutation = copy.deepcopy(word)
        mutation["tail"][first_index][2] = mutation["tail"][first_index][1]
        try:
            inspect_word(mutation, adapters, pairs, pair_names, controls=False)
        except ValueError:
            report["self_partner_mutation_rejected"] = True
        else:
            raise ValueError("Self-partner mutation was accepted")

        mutation = copy.deepcopy(word)
        old_terminal = mutation["tail"][first_index][-1]
        candidate = (old_terminal + 1) % len(frames)
        require(candidate != finals[mutation["tail"][first_index][1]], "No distinct frame for terminal control")
        mutation["tail"][first_index][-1] = candidate
        try:
            inspect_word(mutation, adapters, pairs, pair_names, controls=False)
        except ValueError:
            report["wrong_terminal_mutation_rejected"] = True
        else:
            raise ValueError("Wrong-terminal mutation was accepted")
    return report


def run():
    pins = input_pins()
    for path, expected in pins.items():
        actual = digest(ROOT / path)
        require(actual == expected, f"Pinned source changed: {path}")

    record_raw = (ROOT / RECORD).read_bytes()
    record = json.loads(record_raw)
    require(record["source_manifest"] == SOURCE.as_posix(), "Selected record uses a different source manifest")
    require(record["kappa"] == "836330098538459/500000000000000000", "Selected kappa changed")
    manifest = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
    require(WORD.as_posix() in manifest["files"], "Selected word is absent from the source manifest")
    require(ADAPTERS.as_posix() in manifest["files"], "Selected adapters are absent from the source manifest")
    require(hashlib.sha256((ROOT / WORD).read_bytes()).hexdigest() == manifest["files"][WORD.as_posix()],
            "Selected word is not the manifest-bound byte stream")
    require(hashlib.sha256((ROOT / ADAPTERS).read_bytes()).hexdigest() == manifest["files"][ADAPTERS.as_posix()],
            "Selected adapters are not manifest-bound")
    require(record["proof_supplements"].get(LEAN.as_posix()) == digest(ROOT / LEAN),
            "Lean pair source is not a selected proof supplement")
    require("research/gauge44-slots-t16" in manifest["package_roots"],
            "Selected word package root is absent from the selected source manifest")

    tail_text = (ROOT / TAIL_LEAN).read_text(encoding="utf-8")
    main_text = (ROOT / MAIN_LEAN).read_text(encoding="utf-8")
    labels_text = (ROOT / LABELS_LEAN).read_text(encoding="utf-8")
    checker_text = (ROOT / INSTANCE_CHECKER).read_text(encoding="utf-8")
    require("theorem hpe_labels" in tail_text and "(hp : h ≠ p)" in tail_text,
            "Pinned hpe_labels declaration no longer states the distinct-register premise")
    require("theorem hpe_word" in main_text and "(hp : h ≠ p)" in main_text,
            "Pinned hpe_word declaration no longer requires distinct registers")
    require("inductive XLab" in labels_text,
            "Pinned extended-label definition is absent")
    require("op, h, p, q, U = g[0], g[1], g[2], g[3], g[-1]" in checker_text
            and "h == p" in checker_text,
            "Pinned HPE instance checker no longer records the serialized h/p field layout")

    lean_text = (ROOT / LEAN).read_text(encoding="utf-8")
    pairs, pair_names = exact_pairs(lean_text)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    adapters = json.loads((ROOT / ADAPTERS).read_bytes())
    report = inspect_word(word, adapters, pairs, pair_names, controls=True)
    report.update({
        "status": "PASS_SELECTED_HPE_DISTINCT_PARTNERS",
        "selected_record_sha256": hashlib.sha256(record_raw).hexdigest(),
        "selected_source_manifest_sha256": digest(ROOT / SOURCE),
        "word_sha256": digest(ROOT / WORD),
        "adapters_sha256": digest(ROOT / ADAPTERS),
        "lean_sha256": digest(ROOT / LEAN),
        "tail_lean_sha256": digest(ROOT / TAIL_LEAN),
        "main_lean_sha256": digest(ROOT / MAIN_LEAN),
        "labels_lean_sha256": digest(ROOT / LABELS_LEAN),
        "instance_checker_sha256": digest(ROOT / INSTANCE_CHECKER),
        "scope": "Data-level check of 34 selected tail records whose entrance/terminal frame rows match the three Lean literals; other 60 records, serializer-to-Lean correspondence, and full theorem hypotheses are outside scope.",
    })
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true", help="Write the deterministic RESULT.json receipt")
    args = parser.parse_args()
    report = run()
    receipt = HERE / "RESULT.json"
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        receipt.write_text(encoded, encoding="utf-8")
    else:
        require(receipt.is_file(), "Missing RESULT.json; use --write-result once after review")
        require(receipt.read_text(encoding="utf-8") == encoded, "RESULT.json differs from replay")
    print(f"{report['status']} total_tail={report['total_tail_records']} matched={report['lean_pair_tail_records']} counts={report['pair_counts']} controls=2")


if __name__ == "__main__":
    main()
