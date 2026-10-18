#!/usr/bin/env python3
"""Complete radius-four formal replay and all-pairs coset join; no new kappa."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # Deliberate local import; also works with python -I.
from algebra import (Algebra, SEED, formal_census, histogram, natural_census,
                     require, state_bytes, table_bytes)
from controls import check_controls


def independent(states, table, summary, work):
    compiler = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
    require(compiler is not None, "a C++17 compiler is required")
    executable = work / "independent"
    subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                    str(HERE / "independent.cpp"), "-o", str(executable)], check=True, timeout=120)
    state_path, table_path = work / "states.bin", work / "independent-table.bin"
    completed = subprocess.run([str(executable), str(state_path), str(table_path)],
                               text=True, capture_output=True, check=True, timeout=180)
    observed = json.loads(completed.stdout)
    require(observed == {k: v for k, v in summary.items() if k != "table_sha256"},
            "independent census counts differ")
    require(table_path.read_bytes() == table_bytes(table), "independent target table differs")
    require(state_path.stat().st_size == 85 * len(states), "independent state file is incomplete")
    digest = hashlib.sha256()
    with state_path.open("rb") as source:
        for state in sorted(states):
            expected = state_bytes(state, states[state])
            actual = source.read(85)
            require(actual == expected, "independent formal state or minimum distance differs")
            digest.update(actual)
        require(source.read(1) == b"", "unexpected trailing independent states")
    return {"all_states_and_distances_equal": True, "all_target_entries_equal": True,
            "state_encoding": "sorted four 168-bit coefficients, 21 little-endian bytes each, then distance byte",
            "state_sha256": digest.hexdigest(), "state_bytes": state_path.stat().st_size}


def verify(work):
    algebra = Algebra()
    states, formal, formal_summary = formal_census(algebra)
    print("CHECK formal census: all words through radius four", flush=True)
    comparison = independent(states, formal, formal_summary, work)
    del states
    print("CHECK independent C++ census: every formal state, distance and target entry agrees", flush=True)
    natural, natural_summary = natural_census(algebra)
    direct = [a + b for a in algebra.direct for b in algebra.direct]
    flat_formal = list(table_bytes(formal))
    require(flat_formal == [min(9, cost) for cost in direct], "a formal saving or coverage change was found")
    require(all(natural[a][b] <= formal[a][b] for a in range(168) for b in range(168)),
            "natural relaxation excludes a formal word")
    alias_counts = Counter()
    for a in range(168):
        for b in range(168):
            if natural[a][b] < formal[a][b]:
                alias_counts[(natural[a][b], algebra.direct[a] + algebra.direct[b])] += 1
    controls = check_controls(algebra, formal, natural)
    (work / "formal-targets.bin").write_bytes(table_bytes(formal))
    (work / "natural-targets.bin").write_bytes(table_bytes(natural))
    return {
        "schema_version": 1,
        "status": "PASS_SCOPED_FORMAL_GL3_TWO_REGISTER_CENSUS",
        "assignment_seed": SEED,
        "base_commit": "64039f1bd3b6a523b96083fd858ad040a75e3030",
        "model": "M_2(F2[GL_3(F2)]), six coordinate CNOTs, six scalar rank-one idempotents",
        "address_group_order": 168,
        "address_rows_encoding": "three 3-bit row masks packed low row first, matrices in increasing integer order",
        "address_matrices": algebra.group,
        "direct_cayley_layers": histogram(algebra.direct),
        "ordered_target_pairs": 168 * 168,
        "direct_pair_cost_histogram": histogram(direct),
        "formal": formal_summary,
        "natural": natural_summary,
        "independent": comparison,
        "completed_coverage": {
            "formal_word_lengths": list(range(9)),
            "formal_shorter_than_direct": 0,
            "exact_minimum_direct_cost_at_most_8": sum(cost <= 8 for cost in direct),
            "exact_minimum_direct_cost_at_most_9": sum(cost <= 9 for cost in direct),
            "remaining_direct_cost_10_to_12": sum(cost > 9 for cost in direct),
            "remaining_lower_bound": 9,
            "sentinel_9": "no formal word of length at most eight; not an assertion that minimum is nine",
        },
        "natural_aliases": [{"natural_minimum": n, "direct_cost": d, "target_pairs": count}
                            for (n, d), count in sorted(alias_counts.items())],
        "controls": controls,
        "scope": "Finite exact formal-word certificate for exactly two registers. No added-register, arbitrary-alphabet, physical supplier, selected frontier, or kappa claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, help="new or empty output directory outside the package")
    parser.add_argument("--emit-certificate", type=Path, help="write a newly generated certificate instead of comparing; refuses overwrite")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    try:
        if args.emit_certificate:
            require(not args.emit_certificate.exists(), "certificate output already exists")
        if args.work:
            require(not args.work.resolve().is_relative_to(HERE), "work directory must be outside the package")
            require(not args.work.exists() or not any(args.work.iterdir()), "work directory must be empty")
            args.work.mkdir(parents=True, exist_ok=True)
            report = verify(args.work)
        else:
            with tempfile.TemporaryDirectory(prefix="gl3-mixed-") as temporary:
                report = verify(Path(temporary))
        if args.emit_certificate:
            with args.emit_certificate.open("x") as output:
                json.dump(report, output, indent=2)
                output.write("\n")
            print("GENERATED_CERTIFICATE (not compared to the committed certificate)")
        else:
            require(report == json.loads(args.certificate.read_text()), "committed certificate differs from full replay")
        coverage = report["completed_coverage"]
        print(f"PASS_GL3_MIXED_TARGETS pairs={report['ordered_target_pairs']} "
              f"exact_minima={coverage['exact_minimum_direct_cost_at_most_9']} "
              f"unresolved={coverage['remaining_direct_cost_10_to_12']} "
              f"formal_states={report['formal']['states']} "
              f"natural_aliases={sum(row['target_pairs'] for row in report['natural_aliases'])} "
              f"controls={report['controls']['count']} no_new_kappa")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
