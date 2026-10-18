#!/usr/bin/env python3
"""Check every kernel call and complete PR917 replay, retaining all controls.

Sricharan Vagvala, substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fast_rows import accelerated, normal_row, sum_rows
from support import HERE, PREDECESSOR, canonical, check_pins, digest, fixture, load_module, predecessor, require


def verify():
    experiment, fast, verifier = predecessor()
    reference = load_module("ck917_reference", PREDECESSOR / "independent.py")
    programs = fixture(experiment)
    counts = {"normal_row": 0, "sum_rows": 0}
    streams = {}

    def checked_normal(terms, exponent):
        result = normal_row(terms, exponent)
        require(result == reference._normal_row(terms, exponent), "normalization differential failure")
        counts["normal_row"] += 1
        return result

    def checked_sum(left, right, sign):
        result = sum_rows(left, right, sign)
        require(result == reference._sum_rows(left, right, sign), "addition differential failure")
        counts["sum_rows"] += 1
        return result

    original = fast._normal_row, fast._sum_rows
    fast._normal_row, fast._sum_rows = checked_normal, checked_sum
    try:
        for name, program in programs.items():
            baseline = reference.replay(program)
            result = fast.replay(program)
            require(canonical(result) == canonical(baseline), "complete replay disagreement: " + name)
            reference.check_endpoint(baseline, name.rsplit("_", 1)[1])
            fast.check_endpoint(result, name.rsplit("_", 1)[1])
            streams[name] = {"primitive_count": len(program), "word_sha256": digest(program),
                             "complete_result_sha256": digest(result),
                             "input_columns": result["input_columns"],
                             "maximum_denominator_power": result["maximum_denominator_power"],
                             "positive_prefix": result["positive_prefix"]}
    finally:
        fast._normal_row, fast._sum_rows = original

    tests = load_module("ck_dyadic_tests", HERE / "test_fast_rows.py")
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    testing = unittest.TestResult()
    suite.run(testing)
    require(testing.wasSuccessful(), "kernel controls failed: " + repr(testing.errors + testing.failures))

    # This invokes the whole frozen verifier, including the separate Fraction
    # engine, reconstruction/census, native frame audit and its 10+25 controls.
    output = io.StringIO()
    with accelerated(fast), redirect_stdout(output):
        full = verifier.verify()
    require(canonical(full) == canonical(experiment.read(PREDECESSOR / "EXPECTED.json")),
            "full predecessor receipt changed")
    return {"status": "EXACT_CK_DYADIC_REPLAY_ACCELERATION_NO_NEW_KAPPA",
            "base_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
            "assignment_seed": 89, "live_source_count": len(check_pins()),
            "streams": streams, "total_primitive_count": sum(map(len, programs.values())),
            "every_kernel_return_compared": counts, "focused_test_groups": testing.testsRun,
            "signed_normalization_cases": 729, "signed_sum_cases": 328050,
            "independent_fraction_primitive_steps": 3000, "inherited_arithmetic_test_groups": 6,
            "full_predecessor_receipt_sha256": digest(full),
            "full_predecessor_stdout": output.getvalue().splitlines(),
            "retained_construction_controls": len(full["controls"]["rejected"]),
            "retained_native_controls": len(full["native"]["negative_controls_rejected"]),
            "scope": "Finite scalar replay and unchanged historical PR917 verification only; no selected cold replay, supplier change, kappa change or full multiplication proof"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true", help="write this package's deterministic RESULT.json")
    args = parser.parse_args()
    result = verify()
    path = HERE / "RESULT.json"
    if args.record:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical(result) == canonical(json.loads(path.read_text())), "RESULT.json changed")
    print("PASS_CK_DYADIC_REPLAY_FAST streams=4 primitives=374606 columns=725 controls=10+25 no_new_kappa")
