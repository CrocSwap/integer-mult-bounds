"""Concrete finite serializer consumer; parent admission is required to execute.

Run in separate guarded processes for baseline and candidate. This module never
imports the complete scientific comparison or native backend. All output paths
must be fresh. It does not launch processes or measure itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType

import reference


_NAMES = ("result.json", "witness.json", "rank-trace.json")


def fixture(rows):
    """Small exact-schema input; this is not the complete H25 witness."""
    reference.require(type(rows) is int and rows in (0, 1, 1024, 1025, 2048),
                      "Unsupported finite fixture row count")
    return ({"ok": True, "number": 3}, {
        "support": list(range(rows)), "args": [None, (0, 1)], "kind": [None, "in"],
        "active": [1, 2], "pieces": [((0, 1, 2), 2, (1, 2))],
        "labels": [(1, [(2, 3), (0, 1)], 2, (1, 3))],
        "code": {"roles": 3, "gates": [(1, (0,), (1, 2))],
                 "sources": [((2, 1, 0), 1), ((0, 1, 2), 2)],
                 "outputs": [(1, 2), (0, 1)]},
    }, [((1, 2), 2), ((1, 2), 1), ((2,), 1)])


def finite_reference(values):
    """Same original code with separate finite EXPECTED, as in frozen controls."""
    result, witness, ranks = values
    expected = {
        "result_sha256": hashlib.sha256(reference.canonical(result)).hexdigest(),
        "exact_witness_sha256": hashlib.sha256(reference.canonical(witness)).hexdigest(),
        "rank_trace_sha256": hashlib.sha256(reference.canonical(ranks)).hexdigest(),
        "rank_call_count": len(ranks),
        "rank_distinct_matrix_count": len({rows for rows, _ in ranks}),
    }
    namespace = dict(reference.write_scientific.__globals__)
    namespace["EXPECTED"] = expected
    original = FunctionType(reference.write_scientific.__code__, namespace,
                            reference.write_scientific.__name__,
                            reference.write_scientific.__defaults__,
                            reference.write_scientific.__closure__)
    return original, expected


def run_component(mode, output_root, rows=2048):
    """One concrete arm; no runtime permission or source custody is inferred."""
    reference.require(mode in ("baseline", "candidate", "controls"), "Invalid component arm")
    reference.require(sys.flags.optimize in (0, 1), "Only normal and -O modes are declared")
    root = Path(output_root)
    reference.require(not root.exists(), "Refusing earlier component evidence")
    if mode == "controls":
        import serialization_controls
        spec_path = Path(__file__).resolve().parent / "CONTROL-SPEC.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        receipt = serialization_controls.run_controls(reference, root)
        reference.require(receipt["case_count"] == spec["count_per_mode"] == 70,
                          "Component controls did not retain exactly 70 cases")
        reference.require([row["case"] for row in receipt["cases"]] == spec["ordered_cases"],
                          "Component control order differs from frozen review")
        reference.require(receipt["optimization"] == sys.flags.optimize,
                          "Component control optimization mode differs")
        # Keep the exact original controls.json. Acceptance records are additive.
        (root / "component-control-acceptance.json").write_text(json.dumps({
            "status": "COMPONENT_CONTROL_ORDER_CHECKED",
            "case_count": 70, "optimization": sys.flags.optimize,
            "scope": "Finite component only; requires independent parent validation",
        }, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return receipt

    # Input creation and finite oracle derivation are common paid setup in both
    # arms. No previous artifact/receipt or successful PASS is read or reused.
    values = fixture(rows)
    original, expected = finite_reference(values)
    root.mkdir(parents=True)
    writer = original
    if mode == "candidate":
        import bounded_serialization
        writer = bounded_serialization.make_writer(
            original, reference.canonical, expected, reference.require,
            batch_bytes=1048576, batch_rows=1024, copy_bytes=1048576)
        reference.require(writer._h25_serialization_faults_enabled is False,
                          "Fault injection enabled in component candidate")
    scientific_receipt = writer(root, *values)
    if mode == "candidate":
        reference.require(writer.last_operation["status"] == "BOUNDED_SERIALIZATION_PASS",
                          "Finite component candidate did not use bounded writer")
    # Independent parent readback/comparison remains required. This finite local
    # readback is charged and supplies concrete receipts, not source authority.
    files = {}
    for name, key, size_key in zip(_NAMES,
            ("result_sha256", "exact_witness_sha256", "rank_trace_sha256"),
            ("result", "witness", "rank_trace")):
        raw = (root / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        reference.require(digest == expected[key] == scientific_receipt[key],
                          "Finite artifact digest differs: " + name)
        reference.require(len(raw) == scientific_receipt["serialized_bytes"][size_key],
                          "Finite artifact byte count differs: " + name)
        files[name] = {"bytes": len(raw), "sha256": digest}
    receipt = {
        "status": "FINITE_SERIALIZER_COMPONENT_RETURNED", "mode": mode,
        "optimization": sys.flags.optimize, "fixture_rows": rows,
        "scientific_receipt": scientific_receipt, "files": files,
        "candidate_operation": None if mode == "baseline" else writer.last_operation,
        "scope": "Finite serializer fixture only; no complete H25 or performance qualification",
    }
    (root / "component-receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2)
                                                + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("controls", "baseline", "candidate"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rows", type=int, choices=(0, 1, 1024, 1025, 2048), default=2048)
    args = parser.parse_args()
    receipt = run_component(args.mode, args.output, args.rows)
    print(json.dumps({"status": receipt["status"], "mode": args.mode,
                      "optimization": sys.flags.optimize}, sort_keys=True))


if __name__ == "__main__":
    main()
