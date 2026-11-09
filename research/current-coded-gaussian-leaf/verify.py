"""Bounded complete current-leaf replay; no network or uncontrolled child jobs.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from leaf_sources import authenticate, need
from check_leaf import run_case
from check_controls import run_controls


def source_custody():
    dependencies = json.loads((HERE / "DEPENDENCIES.json").read_text())["files"]
    tree = json.loads((HERE / "BINDING-SOURCE-TREE.json").read_text())
    need(tree["commit"] == "5629e7772d1720d6727465e328a45694f8620538"
         and tree["truncated"] is False, "exact published complete binding tree")
    known = {row["path"]: row["git_blob"] for row in tree["top_files"] + tree["vendor_files"]}
    count = 0
    for row in dependencies:
        if row["path"].startswith("vendor/binding/"):
            relative = row["path"][len("vendor/binding/"):]
            need(known.get(relative) == row["git_blob"], "published binding source equality: " + relative)
            count += 1
    return dict(retained_files=authenticate(), published_binding_files=count)


def main():
    parser = ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="write the exact new receipt before freeze")
    args = parser.parse_args()
    custody = source_custody()
    cases = dict(
        single=run_case(f=1, K=2, rho=0),
        spaced=run_case(f=2, K=2, rho=1),
        inverse=run_case(f=3, K=1, inverse=True),
        multiple=run_case(f=2, K=1, rows=3, outer=2, r=3),
    )
    parity, state = run_case(f=1, fault="parity", return_state=True)
    cases["parity"] = parity
    cases["retry"] = run_case(f=1, reuse=state)
    cases["overflow"] = run_case(f=1, h=3, r=1, fault="overflow")
    cases["cutoff"] = run_case(f=2, fault="cutoff")
    large, state = run_case(f=2, after=3, return_state=True)
    small = run_case(f=1, reuse=state)
    fresh = run_case(f=1)
    need(small["physical_actions"] == fresh["physical_actions"], "no old backing rescan on a small call")
    need(small["retained_cells"] >= fresh["retained_cells"], "retained historical backing charged")
    cases.update(reuse_large=large, reuse_small=small, fresh_small=fresh)
    controls = run_controls()
    result = dict(schema_version=1, source=custody, cases=cases, controls=controls,
                  total_case_records=sum(row["records"] for row in cases.values()),
                  total_case_physical_actions=sum(row["physical_actions"] for row in cases.values()),
                  fixed_work_ports=349, no_new_kappa=True,
                  selected_assumptions_retained=["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"])
    receipt = HERE / "RESULT.json"
    if args.emit:
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(receipt.read_text())
        # JSON's arrays intentionally encode fixed tuple/list source records.
        # Compare canonical JSON rather than Python tuple/list identities; this
        # also distinguishes bools from ints, unlike raw Python equality.
        need(json.dumps(result, sort_keys=True, separators=(",", ":"))
             == json.dumps(expected, sort_keys=True, separators=(",", ":")),
             "complete exact frozen current-leaf receipt")
    print("PASS_CURRENT_CODED_GAUSSIAN_LEAF " + json.dumps({
        "cases": len(cases), "records": result["total_case_records"],
        "physical_actions": result["total_case_physical_actions"], "fixed_work_ports": 349,
        "source_files": custody["retained_files"], "named_arithmetic_controls": 2,
        "cutoff_control": 1, "other_rejected_controls": controls["rejected_controls"],
        "ordinary_supplier_calls": 0}, sort_keys=True))
    print("PASS_CURRENT_LEAF_CONTROLS")


if __name__ == "__main__":
    main()
