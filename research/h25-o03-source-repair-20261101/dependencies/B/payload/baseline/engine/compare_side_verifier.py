#!/usr/bin/env python3
"""One cold finite or complete side-verification run, under the parent's guard.

The baseline and candidate serialize identical complete result, structural/
label/role witness, and rank transcript artifacts. Candidate additionally pays
all C compilation/link/load and independent finite/binding/fallback controls.
No profile or warm-build reuse; no orchestration, retry, search or parallelism.
"""
from __future__ import annotations

import time
START_WALL = time.perf_counter()
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys

sys.dont_write_bytecode = True
from native_backend import (ROOT, SOURCE_SHA256, CALLER_SHA256, ComplementTrace, attach_trace,
                            bind, build_native, guard_module, load_source, require)
from finite_controls import run_controls
from profile_side_verifier import canonical, source_check

EXPECTED = {
    "result_sha256": "342e99212b12e518902ae9598613f5484113bacee8747c27a13b58a4b1d3986c",
    "exact_witness_sha256": "4b170c1dbfc33c7cb141a2284c6fd69eac7b6d100971d3e9ee625502b5893f82",
    "rank_trace_sha256": "85006ca332bbc57c2ba9fd06f61a0281d4cee600c9f3b449342379bf2aedec8f",
    "rank_call_count": 59959,
    "rank_distinct_matrix_count": 252,
}


def cpu_seconds():
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def scientific_run(module, phases):
    def phase(name, action):
        wall, cpu = time.perf_counter(), cpu_seconds()
        answer = action()
        phases[name] = {"wall_seconds": time.perf_counter() - wall,
                        "cpu_seconds_including_children": cpu_seconds() - cpu}
        return answer

    c = phase("construction", lambda: module.ComplexSideCircuit(25))
    checks = phase("checks_initialization", lambda: module.Checks(c))
    code = phase("compile_roles", lambda: module.compile_roles(c))
    side_map = phase("verify_map", checks.verify_map)
    labels = phase("verify_labels", checks.verify_labels)
    roles = phase("verify_role_frames", lambda: module.verify_role_frames(c, checks, code))
    result = {"circuit": c.stats(), "side_map": side_map, "labels": labels, "role_frames": roles}
    # This exactly matches profile_side_verifier.py's predeclared witness
    # representation. Preserve basis and code dict insertion order as lists.
    witness = {
        "support": c.support,
        "args": c.args,
        "kind": c.kind,
        "active": sorted(c.active),
        "pieces": [(target, node, (coefficient.numerator, coefficient.denominator))
                   for target, node, coefficient in c.pieces],
        "labels": [(key, list(label.basis.items()), label.dim, label.key)
                   for key, label in checks.cache.items()],
        "code": {"roles": code["roles"], "gates": code["gates"],
                 "sources": list(code["sources"].items()),
                 "outputs": list(code["outputs"].items())},
    }
    return result, witness


def write_scientific(output, result, witness, rank_calls):
    encoded_result = canonical(result)
    encoded_witness = canonical(witness)
    encoded_trace = canonical(rank_calls)
    receipt = {
        "result_sha256": hashlib.sha256(encoded_result).hexdigest(),
        "exact_witness_sha256": hashlib.sha256(encoded_witness).hexdigest(),
        "rank_trace_sha256": hashlib.sha256(encoded_trace).hexdigest(),
        "rank_call_count": len(rank_calls),
        "rank_distinct_matrix_count": len({rows for rows, _ in rank_calls}),
    }
    require(receipt == EXPECTED, "Complete output, ordered witness, or rank trace changed from the frozen profile")
    # Same exact bytes and serialization work in both arms; file hashes omit
    # a trailing newline exactly as the existing profile's digest did.
    (output / "result.json").write_bytes(encoded_result)
    (output / "witness.json").write_bytes(encoded_witness)
    (output / "rank-trace.json").write_bytes(encoded_trace)
    receipt["serialized_bytes"] = {"result": len(encoded_result), "witness": len(encoded_witness),
                                    "rank_trace": len(encoded_trace)}
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("finite", "baseline", "candidate"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-complement-sha256", help="Lock to the parent-recorded fresh v2 baseline complement stream")
    args = parser.parse_args()
    require(args.mode != "candidate" or args.expected_complement_sha256 is not None, "Candidate requires the fresh baseline complement SHA-256 before execution")
    require(args.expected_complement_sha256 is None or (args.mode != "finite" and len(args.expected_complement_sha256) == 64 and all(c in "0123456789abcdef" for c in args.expected_complement_sha256)), "Invalid or inapplicable expected complement SHA-256")
    require(not args.output.exists(), "Refusing to overwrite earlier run evidence")
    args.output.mkdir(parents=True)
    require(source_check() == 25, "Frozen H changed")
    if args.mode != "finite":
        require(sys.flags.optimize == 0, "Complete measurements require all unchanged source assertions")
    phases = {}
    controls = None
    native = None
    build = None
    if args.mode in ("finite", "candidate"):
        wall, cpu = time.perf_counter(), cpu_seconds()
        native, build = build_native(args.output / "cold-build")
        phases["cold_compile_link_load"] = {"wall_seconds": time.perf_counter() - wall,
                                              "cpu_seconds_including_children": cpu_seconds() - cpu}
        wall, cpu = time.perf_counter(), cpu_seconds()
        controls = run_controls(native)
        phases["all_finite_independent_binding_fallback_controls"] = {
            "wall_seconds": time.perf_counter() - wall,
            "cpu_seconds_including_children": cpu_seconds() - cpu,
        }
        (args.output / "finite-controls.json").write_text(json.dumps(controls, indent=2, sort_keys=True) + "\n")
    complete = None
    binding = None
    if args.mode != "finite":
        rank_calls = []
        wall, cpu = time.perf_counter(), cpu_seconds()
        module = load_source("_matrix_complete_" + args.mode)
        complement_trace = ComplementTrace(module.Label)
        if args.mode == "candidate":
            binding = bind(module, native, rank_calls, complement_trace)
        else:
            guard_module(module)
            attach_trace(module, rank_calls, complement_trace)
        phases["cold_source_load_guard_bind"] = {"wall_seconds": time.perf_counter() - wall,
                                                "cpu_seconds_including_children": cpu_seconds() - cpu}
        result, witness = scientific_run(module, phases)
        wall, cpu = time.perf_counter(), cpu_seconds()
        complete = write_scientific(args.output, result, witness, rank_calls)
        phases["same_complete_witness_trace_serialization"] = {
            "wall_seconds": time.perf_counter() - wall,
            "cpu_seconds_including_children": cpu_seconds() - cpu,
        }
        complete["result"] = result
        complete["complement_trace"] = complement_trace.receipt()
        require(complete["complement_trace"]["calls"] == 238685, "Complete ordered complement call coverage changed")
        if args.expected_complement_sha256 is not None:
            require(complete["complement_trace"]["sha256"] == args.expected_complement_sha256, "Complete complement stream differs from the fresh baseline")
        (args.output / "complement-transcript.json").write_text(json.dumps(complete["complement_trace"], indent=2, sort_keys=True) + "\n")
        if binding is not None:
            expected_calls = {"complement_native": 238685, "complement_fallback": 0,
                              "gram_native": 59959, "gram_fallback": 0}
            require(binding["counters"] == expected_calls, "Frozen complete native call coverage changed")
            complete["native_calls"] = dict(binding["counters"])
    source_files = ("native_gf2.c", "native_backend.py", "finite_controls.py",
                    "compare_side_verifier.py", "profile_side_verifier.py")
    sources = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_files}
    receipt = {
        "status": "FINITE_PASS" if args.mode == "finite" else "COMPLETE_SIDE_PASS",
        "mode": args.mode,
        "qualification_revision": 2,
        "expected_complement_sha256": args.expected_complement_sha256,
        "base_main": "de5ec2e7a6074068452f45b1a191b5c72832df4a",
        "frozen_sources": {"complex_circuit.py": SOURCE_SHA256, "complex_network.py": CALLER_SHA256},
        "engineering_sources": sources,
        "complete": complete,
        "controls": controls,
        "build": build,
        "phases": phases,
        "measured_wall_seconds_before_receipt_write": time.perf_counter() - START_WALL,
        "process_plus_compiler_cpu_seconds_before_receipt_write": cpu_seconds(),
        "environment": {"python": sys.version, "executable": sys.executable,
                        "platform": sys.platform, "optimization": sys.flags.optimize},
        "measurement_scope": "Cold entire process; parent guard outer wall/CPU is authoritative. Both arms write identical complete witness bytes. Candidate additionally compiles, links, loads and runs every finite/native/binding control.",
        "scientific_scope": "Frozen H=25 complex side verification only; no full network certificate, selected frontier, PR5864 gain, new construction, parameter search or kappa admission.",
    }
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "mode": args.mode,
                      "wall_seconds": receipt["measured_wall_seconds_before_receipt_write"],
                      "cpu_seconds_with_compiler": receipt["process_plus_compiler_cpu_seconds_before_receipt_write"],
                      "complete_hashes": None if complete is None else {key: complete[key] for key in EXPECTED},
                      "complement_trace": None if complete is None else complete["complement_trace"],
                      "controls": None if controls is None else controls["status"],
                      "phases": phases}, sort_keys=True))


if __name__ == "__main__":
    main()
