#!/usr/bin/env python3
"""Replay the complete six-call join and independent coordinate witnesses.

Nick Petalas, Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
FLAGS = ["-std=c++17", "-O3", "-Wall", "-Wextra", "-Wpedantic",
         "-Wconversion", "-Wshadow", "-Werror"]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a[b[i]] for i in range(12))


def group() -> tuple[list[list[int]], list[tuple[int, ...]]]:
    """Build the group from literal permutations, independently of native mul."""
    one = tuple(range(12))
    u = (1, 2, 3, 4, 5, 0, 7, 8, 9, 10, 11, 6)
    v = (6, 11, 10, 9, 8, 7, 3, 2, 1, 0, 5, 4)
    powers = [one]
    for _ in range(6):
        powers.append(compose(powers[-1], u))
    need(powers[6] == one and len(set(powers[:6])) == 6, "order of u")
    elements = powers[:6] + [compose(a, v) for a in powers[:6]]
    need(len(set(elements)) == 12, "literal group size")
    index = {a: i for i, a in enumerate(elements)}
    table = [[index[compose(a, b)] for b in elements] for a in elements]
    need(table[6][6] == 3 and table[table[6][1]][9] == 5, "dicyclic relations")
    words: list[tuple[int, ...] | None] = [None] * 12
    words[0] = ()
    for _ in range(11):
        for a in range(12):
            if words[a] is None:
                continue
            for g in (1, 6):
                b = table[a][g]
                candidate = words[a] + (g,)
                if words[b] is None or len(candidate) < len(words[b]):
                    words[b] = candidate
    need(all(w is not None for w in words), "positive reachability")
    return table, [tuple(w) for w in words if w is not None]


def literal_coordinate_checks(table: list[list[int]], words: list[tuple[int, ...]]) -> dict:
    """Execute full formal columns for all seven-call coordinate witnesses."""
    exact = omissions = 0
    histogram = [0] * 13
    for target in itertools.product(range(12), repeat=3):
        bill = sum(len(words[g]) for g in target)
        histogram[bill] += 1
        if bill != 7:
            continue
        calls = [(row, g) for row in range(3) for g in words[target[row]]]
        # A coordinate call multiplies that diagonal formal group coefficient.
        out = [0, 0, 0]
        for row, g in calls:
            out[row] = table[out[row]][g]
        need(tuple(out) == target, "seven-call formal endpoint")
        exact += 1
        for omitted in range(7):
            altered = [0, 0, 0]
            for i, (row, g) in enumerate(calls):
                if i != omitted:
                    altered[row] = table[altered[row]][g]
            need(tuple(altered) != target, "omitted-call control")
            omissions += 1
    # Independent convolution of the direct-distance counting polynomial.
    coefficients = [sum(len(w) == degree for w in words) for degree in range(5)]
    convolution = [0] * 13
    for a, b, c in itertools.product(range(5), repeat=3):
        convolution[a+b+c] += coefficients[a] * coefficients[b] * coefficients[c]
    need(histogram == convolution, "endpoint histogram")
    return {"direct_bill_histogram": histogram, "exact_seven_targets": exact,
            "omitted_call_rejections": omissions}


def compiler() -> str:
    executable = shutil.which(os.environ.get("CXX", "c++"))
    need(executable is not None, "C++17 compiler required; set CXX to its executable")
    return str(executable)


def compile_source(cxx: str, source: Path, binary: Path) -> None:
    subprocess.run([cxx, *FLAGS, str(source), "-o", str(binary)],
                   check=True, capture_output=True, text=True, timeout=120)


def native(cxx: str, directory: Path) -> dict:
    binary = directory / "search"
    compile_source(cxx, ROOT / "search.cpp", binary)
    result = subprocess.run([str(binary)], check=True, capture_output=True,
                            text=True, timeout=120)
    need(len(result.stdout) < 100000, "bounded native output")
    return json.loads(result.stdout)


def mutation_controls(cxx: str, directory: Path) -> int:
    original = (ROOT / "search.cpp").read_text()
    mutations = [
        ("depth <= 3", "depth <= 2", "raw triple missing"),
        ("needed[3*i+j] = shifts[w[j]][p.inverse[3*i+j]];",
         "needed[3*i+j] = shifts[w[j]][0];", "positive join missing"),
        ("return out;\n}\nvoid emit_word", "out[0] ^= 1; return out;\n}\nvoid emit_word",
         "positive endpoint"),
    ]
    for i, (old, new, diagnostic) in enumerate(mutations):
        need(old in original, "missing mutation anchor")
        source = directory / f"mutation-{i}.cpp"
        binary = directory / f"mutation-{i}"
        source.write_text(original.replace(old, new))
        compile_source(cxx, source, binary)
        run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=120)
        need(run.returncode != 0 and diagnostic in run.stderr,
             f"mutation {i} was not rejected for its intended reason: {run.stderr}")
    return len(mutations)


def source_hashes() -> dict[str, str]:
    paths = sorted(p for p in ROOT.iterdir() if p.is_file())
    need(len(paths) <= 12, "package file bound")
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controls", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    table, words = group()
    coordinate = literal_coordinate_checks(table, words)
    cxx = compiler()
    with tempfile.TemporaryDirectory(prefix="dic3-six-") as temporary:
        directory = Path(temporary)
        result = native(cxx, directory)
        controls = mutation_controls(cxx, directory) if args.controls else 0
    distances = [len(w) for w in words]
    need(result["multiplication"] == table, "independent literal group multiplication")
    need(result["distances"] == distances, "independent literal distances")
    need(result["hits"] == [], "a sharing word exists; report it and stop")
    need(len(result["new_states"]) == 4 and result["new_states"][0] == 1,
         "inventory depth contract")
    need(sum(result["new_states"]) == result["total_states"] <= 178809,
         "inventory cardinality contract")
    eligible = sum(coordinate["direct_bill_histogram"][7:])
    need(result["endpoint_count"] == eligible, "complete endpoint coverage")
    need(result["lookups"] == eligible * result["total_states"], "complete join coverage")
    receipt = {"result": result, "coordinate": coordinate,
               "semantic_mutations_rejected": controls, "sources_sha256": source_hashes()}
    encoded = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        destination = args.receipt.resolve()
        need(not destination.is_relative_to(ROOT), "receipts must stay outside the package")
        destination.write_text(encoded)
    print(encoded, end="")
    print("PASS_DICYCLIC_SIX_CALL_BOUNDARY")


if __name__ == "__main__":
    main()
