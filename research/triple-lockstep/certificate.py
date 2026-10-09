#!/usr/bin/env python3
"""PR139 correction: retract invalid lockstep and pin sequential PR137.

The claimed rank-3r first-stage merge is NOT realizable by the submitted
shared-scratch schedule. Do not accept the hypothetical moment and kappa.
Re-run the original PR137 sequential cover calculation and the exact
three-core negative control, without changing its source closure.
"""
import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

if sys.flags.optimize:
    raise RuntimeError("Assertions must remain enabled")
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "research/cover-local-reuse"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(BASE))

def load_py(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def certificate():
    inherited = load_py("pinned_PR137_sequential_certificate",
                        BASE / "certificate.py")
    baseline = inherited.js(inherited.exact())
    saved = json.loads((BASE / "certificate.json").read_text())
    assert baseline == saved, "Frozen PR137 full certificate mismatch"

    pr137 = Q(206798116851, 500000000000000)
    pr138 = Q(51699582421, 125000000000000)
    retracted = Q(45019844704, 10**14)
    assert Q(saved["kappa"]) == pr137 < pr138 < retracted
    p = inherited.cover_profile()
    assert p["roles_per_cell"] == 91935
    assert p["rank_per_cell"] == 6612144
    assert p["deficit_per_cell"] == 7176
    assert p["maxchild"] == 66
    assert p["local_copies_per_cell"] == 9
    assert p["execution"].startswith("Three completed sequential cores")
    assert len(saved["assembly"]["strict_constraints"]) == 47
    assert len(saved["assembly"]["margins"]) == 7

    counterexample = load_py("PR139_shared_scratch_negative_control",
                             HERE / "lockstep_counterexample.py").run()
    assert counterexample["merged_frame_algebra_passes"]
    assert counterexample["sequential_target_errors"] == 0
    assert counterexample["lockstep_target_errors_per_core"] == [64, 64, 64]
    assert counterexample["lockstep_target_errors_total"] == 192
    return {
        "status": "RETRACTED: submitted three-core shared-stream lockstep is invalid",
        "retracted_kappa": str(retracted),
        "new_exponent_claimed": False,
        "retained_safe_schedule": "three fully completed consecutive cores per bank",
        "retained_conditional_PR137_kappa": str(pr137),
        "PR138_competitor_refined_kappa": str(pr138),
        "retained_PR137_profile": {
            "ambient_m": p["m"],
            "roles_per_three_vertex_cell": p["roles_per_cell"],
            "rank_mass": p["rank_per_cell"],
            "deficit": p["deficit_per_cell"],
            "maxchild": p["maxchild"],
            "local_copies_per_cell": p["local_copies_per_cell"]
        },
        "inherited_assembly_strict_constraints": 47,
        "inherited_assembly_margins": 7,
        "negative_control": counterexample,
        "remaining_research": (
            "Prove a genuinely different joint physical dirty-scratch "
            "implementation with independent live storage or paid cancellation "
            "before proposing any merged rank-3r child."
        ),
        "scope": (
            "Inherited PR137 result is conditional on its analytic/tape contracts. "
            "This checker validates an invalidity microexample, not a new theorem."
        )
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = certificate()
    contents = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(contents)
    else:
        print(contents)
    print("PASS: rejected PR139 lockstep and reproduced inherited sequential PR137",
          file=sys.stderr)

if __name__ == "__main__":
    main()
