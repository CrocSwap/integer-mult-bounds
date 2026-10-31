#!/usr/bin/env python3
"""Diagnostic profile of an unchanged, frozen h=25 side verification scope.

This is not complex_network.certificate(), a selected-frontier replay, a
construction search, or a performance qualification. Run only under the
parent's serial process-group guard. No compiler or third-party dependency.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import cProfile
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pstats
import sys
import time

BASE_MAIN = "de5ec2e7a6074068452f45b1a191b5c72832df4a"
PINS = {
    "complex_circuit.py": "d623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1",
    "complex_network.py": "0da395e67ac04fa213494e71012c1b19b544596d34cdce5a3b172b1fb6af5f1b",
}
ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_check():
    for name, expected in PINS.items():
        actual = hashlib.sha256((ROOT / "source" / name).read_bytes()).hexdigest()
        require(actual == expected, "Source digest changed: " + name)
    tree = ast.parse((ROOT / "source" / "complex_network.py").read_text())
    hs = [ast.literal_eval(node.value) for node in tree.body
          if isinstance(node, ast.Assign) and
          any(isinstance(target, ast.Name) and target.id == "H" for target in node.targets)]
    require(hs == [25], "The unchanged caller no longer freezes H=25")
    return hs[0]


def run_side(h, rank_calls, phases):
    def phase(name, action):
        start_wall = time.perf_counter()
        start_cpu = time.process_time()
        value = action()
        phases[name] = {"wall_seconds": time.perf_counter() - start_wall,
                        "cpu_seconds": time.process_time() - start_cpu}
        return value

    def load():
        spec = importlib.util.spec_from_file_location("_frozen_matrix_complex_circuit", ROOT / "source" / "complex_circuit.py")
        require(spec is not None and spec.loader is not None, "Cannot load frozen module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    module = phase("load", load)
    original_rank = module.rank

    def traced_rank(rows):
        frozen_rows = tuple(rows)
        result = original_rank(frozen_rows)
        require(type(result) is int, "Rank result changed its exact type")
        rank_calls.append((frozen_rows, result))
        return result

    module.rank = traced_rank
    circuit = phase("construction", lambda: module.ComplexSideCircuit(h))
    checks = phase("checks_initialization", lambda: module.Checks(circuit))
    code = phase("compile_roles", lambda: module.compile_roles(circuit))
    side_map = phase("verify_map", checks.verify_map)
    labels = phase("verify_labels", checks.verify_labels)
    roles = phase("verify_role_frames", lambda: module.verify_role_frames(circuit, checks, code))
    # These are exactly the complete finite side checks called, in this order,
    # by complex_network.certificate(). No mathematical parameters are varied.
    result = {"circuit": circuit.stats(), "side_map": side_map,
              "labels": labels, "role_frames": roles}
    return circuit, checks, code, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(sys.flags.optimize == 0, "This source uses assert; profile must run without -O")
    sys.dont_write_bytecode = True
    require(not args.output.exists(), "Refusing to overwrite diagnostic evidence")
    args.output.mkdir(parents=True)
    h = source_check()
    profile = cProfile.Profile()
    rank_calls = []
    phases = {}
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    circuit, checks, code, result = profile.runcall(run_side, h, rank_calls, phases)
    profile_cpu = time.process_time() - start_cpu
    profile_wall = time.perf_counter() - start_wall
    profile.dump_stats(str(args.output / "profile.pstats"))
    stats = pstats.Stats(profile)
    targeted = []
    all_source = []
    for (filename, line, name), (primitive, total, self_time, cumulative, callers) in stats.stats.items():
        if filename.endswith("complex_circuit.py"):
            row = {"name": name, "line": line, "primitive_calls": primitive,
                   "total_calls": total, "self_seconds": self_time,
                   "cumulative_seconds": cumulative}
            all_source.append(row)
            if name in {"rank", "echelon", "reduce", "dot", "complement_in", "nondegenerate"}:
                targeted.append(row)
    shape_counts = Counter((len(rows), max((x.bit_length() for x in rows), default=0))
                           for rows, _ in rank_calls)
    unique = {}
    for rows, rank in rank_calls:
        previous = unique.setdefault(rows, rank)
        require(previous == rank, "Identical rank matrices produced different outputs")
    # Preserve the ordered trace, exact rows and expected outputs. This frozen
    # corpus enables a later conversion-plus-native check without a new search.
    with (args.output / "rank-trace.jsonl").open("x", encoding="ascii") as output:
        for rows, rank in rank_calls:
            output.write(canonical({"rows": rows, "rank": rank}).decode("ascii") + "\n")
    rank_corpus = [{"rows": rows, "rank": rank} for rows, rank in sorted(unique.items())]
    (args.output / "rank-corpus.json").write_bytes(canonical(rank_corpus) + b"\n")
    # Basis dictionary insertion order, labels, pivots, role order and coefficient
    # numerators/denominators are all hashed without normalization of witnesses.
    witnesses = {
        "support": circuit.support,
        "args": circuit.args,
        "kind": circuit.kind,
        "active": sorted(circuit.active),
        "pieces": [(target, node, (coefficient.numerator, coefficient.denominator))
                   for target, node, coefficient in circuit.pieces],
        "labels": [(key, list(label.basis.items()), label.dim, label.key)
                   for key, label in checks.cache.items()],
        "code": {"roles": code["roles"], "gates": code["gates"],
                 "sources": list(code["sources"].items()),
                 "outputs": list(code["outputs"].items())},
    }
    receipt = {
        "status": "DIAGNOSTIC_COMPLETE_SIDE_SCOPE_ONLY",
        "base_main": BASE_MAIN,
        "sources": PINS,
        "unchanged_caller": "scripts/complex_network.py:certificate (side verification segment)",
        "h": h,
        "result": result,
        "result_sha256": digest(result),
        "exact_witness_sha256": digest(witnesses),
        "rank_trace_sha256": digest(rank_calls),
        "rank_call_count": len(rank_calls),
        "rank_distinct_matrix_count": len(unique),
        "rank_shape_counts": [{"rows": r, "columns": c, "calls": n}
                              for (r, c), n in sorted(shape_counts.items())],
        "profiled_complete_side_wall_seconds": profile_wall,
        "profiled_complete_side_cpu_seconds": profile_cpu,
        "profiled_phases": phases,
        "targeted_functions": sorted(targeted, key=lambda item: item["cumulative_seconds"], reverse=True),
        "all_source_functions": sorted(all_source, key=lambda item: item["self_seconds"], reverse=True),
        "environment": {"python": sys.version, "executable": sys.executable,
                        "platform": sys.platform, "pid": os.getpid()},
        "limitations": [
            "Profiled timings include cProfile and exact rank-trace instrumentation.",
            "Cumulative times are nested and must not be summed.",
            "No native code or candidate execution; no speedup established.",
            "The complete side verification segment is not the full complex-network certificate.",
            "No PR5864 workload is executed and no matrix time counts toward its improvement target.",
            "No new construction, parameter search, kappa admission or formal theorem verification.",
        ],
    }
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "h": h,
                      "wall_seconds": profile_wall, "cpu_seconds": profile_cpu,
                      "rank_calls": len(rank_calls), "rank_distinct_matrices": len(unique),
                      "result_sha256": receipt["result_sha256"],
                      "exact_witness_sha256": receipt["exact_witness_sha256"],
                      "targeted_functions": receipt["targeted_functions"]}, sort_keys=True))


if __name__ == "__main__":
    main()
