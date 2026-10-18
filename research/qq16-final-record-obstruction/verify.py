#!/usr/bin/env python3
"""Read-only replay of the QQ16 final-record obstruction and independent oracle.

Apache-2.0. Substantial OpenAI Codex assistance; no human review claimed.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_module(name):
    spec = importlib.util.spec_from_file_location("qq16_final_" + name, PACKAGE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_inputs(root):
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = []
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = (root / row["path"]).resolve()
        need(path.is_relative_to(root.resolve()) and path.is_file(), "input path: " + row["path"])
        need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "input hash: " + row["path"])
        checked.append(row["path"])
    return checked


def compute(root=ROOT):
    inputs = check_inputs(root)
    primary = read_module("verify_core").report(root)
    independent = read_module("independent_moments").verify(root)
    algebra = read_module("independent_algebra").verify(root)
    left, right = primary["sources"], independent
    need(left["R_columns_sha256"] == right["R_columns_sha256"], "independent centre matrix")
    comparisons = {tuple(row["stages"]): row for row in right["pairs"]}
    for row in left["pair_checks"]:
        other = comparisons[tuple(row["stages"])]
        need(row["relative_routes_sha256"] == other["relative_route_sha256"], "independent relative owner routes")
        need(row["distinct_relative_routes"] == other["routes"] == 96, "independent route census")
        need(int(row["cross_gram_identity_trace"]) == other["cross_trace_per_owner"] == 1536, "independent full trace")
    need(left["triple_trace_per_owner"] == right["normalized_moment1_per_owner"] == "24", "first moment")
    need(left["triple_square_trace_per_owner"] == right["normalized_moment2_per_owner"] == "28", "second moment")
    need(left["stacked_rank_lower_per_owner"] == right["stack_rank_lower_per_owner"] == "144/7", "stacked rank bound")
    need(left["constrained_image_lower_per_owner"] == right["conditional_image_lower_per_owner"] == "32/7", "constrained image bound")
    need(left["selected_defect_lower_per_owner"] == "8/7", "selected defect bound")
    return {"schema_version": 1, "status": "PASS_QQ16_FINAL_RECORD_OBSTRUCTION",
            "input_paths_checked": inputs, "primary": primary, "independent_moments": independent,
            "independent_algebra": algebra,
            "proof_scope": "Actual regular owner action; ordinary-only bridge/terminal replica; fixed local maps through F2; all 64 named initial record coordinates granted free. No first-six-swap, supplier, native-cost or kappa claim."}


def verify_receipt(result):
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    need(expected == result, "complete canonical RESULT.json differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate the complete deterministic result")
    args = parser.parse_args()
    result = compute()
    if args.write:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        verify_receipt(result)
    print("PASS_QQ16_FINAL_RECORD_OBSTRUCTION actual_routes=1008 pairs=6 events=19 initial_records=64 defect>=ceil(8|G|/7) controls="
          + str(len(result["primary"]["rejected_controls"])) + " independent_oracles=PASS no_new_kappa")


if __name__ == "__main__":
    main()
