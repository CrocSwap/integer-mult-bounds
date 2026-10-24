#!/usr/bin/env python3
"""Replay the saved clean-register checks in a new directory."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

if not __debug__:
    raise SystemExit("Run this verifier without -O. Historical sources use assert.")
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def run(command, log):
    print("Run:", " ".join(map(str, command)), flush=True)
    with log.open("w") as output:
        subprocess.run(list(map(str, command)), check=True,
                       stdout=output, stderr=subprocess.STDOUT)


def check_alphabets(path):
    # This uses the dual-vector construction from the independent audit.
    bases = []
    for columns in itertools.combinations(range(1, 16), 4):
        dual = []
        for i in range(4):
            choices = [v for v in range(1, 16)
                       if all((v & c).bit_count() % 2 == int(i == j)
                              for j, c in enumerate(columns))]
            if len(choices) != 1:
                break
            dual.append(choices[0])
        if len(dual) == 4:
            bases.append(tuple(sorted(zip(columns, dual))))
    def permute(v, p):
        return sum(((v >> i) & 1) << p[i] for i in range(4))
    def canonical(basis):
        return min(tuple(sorted((permute(x, p + (3,)),
                                 permute(y, p + (3,))) for x, y in basis))
                   for p in itertools.permutations(range(3)))
    orbits = Counter(canonical(basis) for basis in bases)
    rows = [list(map(int, line.split())) for line in path.read_text().splitlines()]
    require(all(len(row) == 16 for row in rows), "Invalid alphabet row")
    alphabets = [tuple(zip(row[::2], row[1::2])) for row in rows]
    identity = tuple((1 << i, 1 << i) for i in range(4))
    require(len(bases) == 840 and len(orbits) == 166, "Basis count")
    require(all(row[:4] == identity for row in alphabets), "Coordinate basis")
    require(len(alphabets) == 166 and
            set(row[4:] for row in alphabets) == set(orbits), "Basis coverage")
    require(Counter(orbits.values()) == {1: 6, 3: 42, 6: 118}, "Orbit sizes")
    return {"unordered_bases": 840, "alphabets": 166,
            "orbit_sizes": dict(Counter(orbits.values()))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    build = args.build.resolve()
    require(not build.exists(), "The build directory exists.")
    manifest = read(ROOT / "SOURCE-MANIFEST.json")
    for item in manifest["files"]:
        require(hashlib.sha256((ROOT / item["package"]).read_bytes()).hexdigest()
                == item["sha256"], "Source hash: " + item["package"])
    build.mkdir(parents=True)
    shutil.copytree(ROOT / "sources", build / "sources")
    clean = build / "sources/four-register/independent/clean-zero"
    audit = build / "sources/four-register/independent-audit"
    basis = build / "sources/doubling-architecture/clean-ancilla"
    selected = build / "sources/doubling-architecture/rank-independent/clean-audit"
    compiler = os.environ.get("CXX") or shutil.which("clang++") or shutil.which("g++")
    require(compiler is not None, "A C++17 compiler is required.")
    for source, target in [(clean / "integer.cpp", clean / "integer"),
                           (clean / "field.cpp", clean / "field"),
                           (audit / "check_clean_zero_orders.cpp", audit / "orders"),
                           (basis / "two_bases.cpp", basis / "two_bases"),
                           (selected / "selected_words.cpp", selected / "selected_words")]:
        run([compiler, "-O3", "-std=c++17", source, "-o", target],
            build / (target.name + "-compile.log"))
    run([sys.executable, "-E", "-B", clean / "generate.py"], build / "clean-generate.log")
    expected = read(ROOT / "expected/clean-zero-result.json")
    require(hashlib.sha256((clean / "words.bin").read_bytes()).hexdigest()
            == expected["word_sha256"], "Clean word stream")
    run([audit / "orders", audit / "clean-zero-family-metadata.txt", clean / "words.bin"],
        build / "independent-orders.json")
    independent = read(build / "independent-orders.json")
    require(independent == expected["independent_front_end_audit"], "Independent orders")
    for engine in ["integer", "field"]:
        run([clean / engine, clean / "words.bin", clean / (engine + ".jsonl")],
            build / (engine + "-run.log"))
    for suffix in [".jsonl", ".jsonl.terminals.jsonl"]:
        require((clean / ("integer" + suffix)).read_bytes() ==
                (clean / ("field" + suffix)).read_bytes(), "Engine comparison: " + suffix)
    totals = json.loads((clean / "integer.jsonl").read_text().splitlines()[-1])
    require(totals == expected["engine_totals"], "Clean totals")
    require(len((clean / "integer.jsonl.terminals.jsonl").read_text().splitlines())
            == expected["terminal_word_count"], "Terminal word count")
    catalogue = check_alphabets(basis / "ALPHABETS.txt")
    results = []
    for index in range(166):
        output = build / f"basis-{index:03d}.json"
        run([basis / "two_bases", basis / "ALPHABETS.txt", index, output],
            build / f"basis-{index:03d}.log")
        results.append(read(output))
    full = {"alphabets": 166, "completed": len(results), "results": results,
            "states": [sum(row["states"][i] for row in results) for i in range(4)]}
    for key in ["searched_words", "terminals", "robust"]:
        full[key] = sum(row[key] for row in results)
    (build / "all-basis-summary.json").write_text(json.dumps(full, indent=2) + "\n")
    old = read(ROOT / "expected/all-basis-summary.json")
    require(full["completed"] == full["alphabets"] == 166, "Incomplete basis run")
    for key in ["searched_words", "states", "terminals", "robust"]:
        require(full[key] == old[key], "Basis total: " + key)
    for actual, expected_row in zip(full["results"], old["results"]):
        require(actual["complete"] and actual["robust"] == 0, "Incomplete alphabet")
        for key in expected_row:
            if key != "seconds":
                require(actual[key] == expected_row[key], "Alphabet field: " + key)
    fixed = read(ROOT / "expected/selected-comparison.json")["results"]
    words = [row["word"] for row in fixed]
    encoded = "".join(" ".join(str(n) for xy in word for n in xy) + "\n" for word in words)
    output = subprocess.run([str(selected / "selected_words")], input=encoded,
                            text=True, capture_output=True, check=True)
    field = [json.loads(line) for line in output.stdout.splitlines()]
    require(len(field) == len(words) == 48, "Selected word count")
    spec = importlib.util.spec_from_file_location("clean_search", basis / "search.py")
    exact = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exact)
    checks = []
    for i, word in enumerate(words):
        rational = exact.solve(word)
        require(len(rational["found"]) == field[i]["robust"] == 0, "Selected survivor")
        require(rational["stats"]["terminals"] == field[i]["terminals"], "Selected terminals")
        checks.append({"case": i, "word": word, "rational": rational["stats"], "field": field[i]})
        exact.d.rref.cache_clear()
        exact.d.rep.cache_clear()
        exact.d.add.cache_clear()
    (build / "selected-comparison.json").write_text(json.dumps(checks, indent=2) + "\n")
    receipt = {"status": "PASS_CLEAN_RESTRICTED_CLASSES", "clean_zero": totals,
               "independent_orders": independent, "basis_catalogue": catalogue,
               "all_basis": {key: full[key] for key in
                             ["alphabets", "completed", "searched_words", "states", "terminals", "robust"]},
               "selected_rational_field_words": len(checks),
               "source_manifest_sha256": hashlib.sha256((ROOT / "SOURCE-MANIFEST.json").read_bytes()).hexdigest(),
               "scope": "Restricted clean endpoint; frame spans five and six remain open."}
    (build / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], totals["words"], full["searched_words"], flush=True)


if __name__ == "__main__":
    main()
