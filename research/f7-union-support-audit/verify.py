#!/usr/bin/env python3
"""Fresh independent census checks. Nick Petalas. Apache-2.0."""
import argparse
import hashlib
import json
import runpy
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
# -I excludes the script directory. Only this package's explicit sibling is imported.
sys.path.insert(0, str(PACKAGE))
from oracle import admissible_splits, census, describe  # noqa: E402

FLAGS = ["-std=c++20", "-O3", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
         "-Wsign-conversion", "-Wshadow", "-Werror"]
CASES = [(2, 4), (2, 6), (3, 6), (3, 8), (4, 8), (4, 10), (5, 10), (5, 12)]
FULL_CASES = [(7, 20, 10, 10), (7, 20, 10, 9), (7, 20, 10, 8),
              (7, 20, 9, 9), (7, 20, 10, 7), (7, 18, 9, 9)]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def pins():
    source = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in source["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"], "changed input: " + row["path"])


def compile_engine(directory, compiler, source=None, sanitize=False):
    target = directory / "census"
    path = PACKAGE / "census.cpp"
    if source is not None:
        path = directory / "mutant.cpp"
        path.write_text(source)
    flags = FLAGS + (["-O1", "-fsanitize=undefined,bounds", "-fno-sanitize-recover=all"] if sanitize else [])
    subprocess.run([compiler, *flags, str(path), "-o", str(target)], check=True,
                   capture_output=True, text=True, timeout=60)
    return target


def run_engine(binary, args, directory, timeout=60):
    hits = directory / "hits.txt"
    proc = subprocess.run([str(binary), *map(str, args), str(hits)], check=False, capture_output=True,
                          text=True, timeout=timeout)
    require(proc.returncode in (0, 2), "engine error: " + proc.stderr)
    result = json.loads(proc.stdout)
    require(result["complete"] == (proc.returncode == 0), "exit/completeness mismatch")
    require(hits.stat().st_size <= 5_000_000, "oversize witness output")
    words = hits.read_text().splitlines()
    require(len(words) == len(set(words)) == result["hits"], "duplicate or missing witnesses")
    return result, set(words)


def compare_case(binary, directory, n, length):
    counts, expected, wrong_simple = census(n, length)
    rows = []
    limit = min(length // 2, 1 << (n - 1))
    for s in range(1, limit + 1):
        for t in range(1, limit + 1):
            wanted = expected.get((s, t), set())
            for mode in (0, 1):
                result, words = run_engine(binary, (n, length, s, t, mode, 0), directory)
                require(result["complete"] and words == wanted, f"oracle mismatch {n,length,s,t,mode}")
                if mode == 0:
                    require(result["candidate_leaves"] == counts.get((s, t), 0), "unpruned restored count")
            if wanted:
                digest = hashlib.sha256(("\n".join(sorted(wanted)) + "\n").encode()).hexdigest()
                rows.append({"split": [s, t], "hits": len(wanted), "words_sha256": digest})
    return {"n": n, "length": length, "restored": sum(counts.values()),
            "universal": sum(map(len, expected.values())), "hits_by_split": rows,
            "simple_universal_wrong_bit0_rejections": wrong_simple,
            "comparisons": 2 * limit * limit}


def fixtures():
    tiny = describe((0, 1, 0, 2, 1, 3, 2, 3), 4)
    require(tiny == {"path": [0, 1, 3, 2, 6, 4, 12, 8], "split": (4, 4),
                     "bit0_split": (6, 2), "coverage": 16, "wrong_excess": 8,
                     "weight_budget": 5, "simple": True}, "tiny counterexample")
    splits = admissible_splits(20)
    require(splits == [(9, 9), (10, 7), (10, 8), (10, 9), (10, 10)], "L20 split domain")
    require(admissible_splits(18) == [(9, 9)], "L18 split domain")
    upper = tuple(map(int, "010201030102010345464546"))
    require(describe(upper, 7)["coverage"] == 128, "L24 upper witness")
    return {"counterexample": tiny, "l20_splits": splits, "l24_upper_word": "".join(map(str, upper))}


def historical_control():
    # Authenticated audit subject only. The new engine and oracle never call it.
    path = ROOT / "research/universal-f7-singleton-seedb859517b/engine.py"
    subject = runpy.run_path(str(path))["cyclic_census"]
    word = (0, 1, 0, 2, 1, 3, 2, 3)
    unpruned = subject(4, 8, simple=True, prefix=word, max_nodes=100)
    faulty = subject(4, 8, budget=5, simple=True, prefix=word, max_nodes=100)
    require(unpruned["hits"] == 1 and unpruned["leaves"] == 1, "historical positive control")
    require(faulty["hits"] == 0 and faulty["leaves"] == 0, "historical wrong prune not reproduced")
    return {"without_budget": unpruned, "bit0_budget_5": faulty}


def failure_controls(binary, directory):
    for cap in (1, 7, 100):
        result, _ = run_engine(binary, (4, 8, 4, 4, 1, cap), directory)
        require(not result["complete"] and result["attempts"] == cap, "cap falsely accepted")
    bad = [(1, 8, 4, 4, 1, 0), (8, 20, 10, 10, 1, 0), (3, 7, 3, 3, 1, 0),
           (3, 22, 3, 3, 1, 0), (3, 8, 5, 3, 1, 0), (3, 8, 3, 3, 2, 0),
           (3, 8, 3, 3, 1, -1), (3, 8, 3, 3, 1, "1x")]
    for args in bad:
        proc = subprocess.run([str(binary), *map(str, args), str(directory / "bad-hits")],
                              check=False, capture_output=True, text=True, timeout=5)
        require(proc.returncode == 1 and not proc.stdout, "invalid input accepted")
    proc = subprocess.run([str(binary), "3", "8", "3", "3", "1", "0", str(directory)],
                          check=False, capture_output=True, text=True, timeout=5)
    require(proc.returncode == 1 and not proc.stdout, "unwritable output accepted")
    return 12


def mutant_controls(directory, compiler):
    original = (PACKAGE / "census.cpp").read_text()
    mutations = [
        ("depth % 2", "next.position & 1"),
        ("if (next.visited.contains(next.position)) return true;", "if (next.visited.contains(next.position)) return remaining == 0;"),
        ("node.same.size() + future_same < half - 1", "node.same.size() + future_same < half"),
        ("next_label[index] >= c.n", "next_label[index] >= c.n - 1"),
    ]
    _, expected, _ = census(3, 8)
    for index, (old, new) in enumerate(mutations):
        require(original.count(old) == 1, "ambiguous mutation")
        sub = directory / str(index)
        sub.mkdir()
        binary = compile_engine(sub, compiler, original.replace(old, new))
        detected = False
        for split, wanted in expected.items():
            try:
                result, words = run_engine(binary, (3, 8, *split, 1, 0), sub)
                detected |= not result["complete"] or words != wanted
            except RuntimeError as error:
                require(str(error).startswith("engine error:"), "unexpected mutant harness failure")
                detected = True
        require(detected, "surviving implementation mutant " + str(index))
    return len(mutations)


def quick(directory, compiler):
    binary = compile_engine(directory, compiler)
    checks = fixtures()
    historical = historical_control()
    rows = [compare_case(binary, directory, *case) for case in CASES]
    by_case = {(row["n"], row["length"]): row for row in rows}
    require(by_case[(2, 4)]["universal"] == 3 and by_case[(3, 6)]["universal"] == 10
            and by_case[(4, 8)]["universal"] == 26, "known positive controls")
    failures = failure_controls(binary, directory)
    mutants = mutant_controls(directory, compiler)
    sanitized = directory / "sanitized"
    sanitized.mkdir()
    binary = compile_engine(sanitized, compiler, sanitize=True)
    control = compare_case(binary, sanitized, 4, 10)
    require(control == by_case[(4, 10)], "sanitizer result mismatch")
    return {"fixtures": checks, "historical_control": historical,
            "small_domains": rows, "failure_controls": failures,
            "rejected_mutants": mutants, "sanitized_case": [4, 10]}


def full(directory, compiler):
    binary = compile_engine(directory, compiler)
    results = []
    deadline = time.monotonic() + 540
    for case in FULL_CASES:
        remaining = deadline - time.monotonic()
        require(remaining > 0, "full census budget exhausted")
        result, words = run_engine(binary, (*case, 1, 0), directory, timeout=remaining)
        require(result["complete"] and result["cap"] == 0 and result["hits"] == 0 and not words,
                "full exclusion failed")
        results.append(result)
    return {"cases": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="six uncapped seven-label traversals, at most 540 native seconds")
    parser.add_argument("--emit", action="store_true", help="print fresh receipt instead of comparing committed receipt")
    parser.add_argument("--compiler", default="c++")
    args = parser.parse_args()
    pins()
    with tempfile.TemporaryDirectory(prefix="f7-independent-") as temporary:
        work = Path(temporary)
        report = full(work, args.compiler) if args.full else quick(work, args.compiler)
    filename = "FULL.json" if args.full else "QUICK.json"
    # Normalize tuples to the JSON representation before the exact comparison.
    report = json.loads(json.dumps(report))
    if args.emit:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        require(report == json.loads((PACKAGE / filename).read_text()), "committed receipt mismatch")
        print("PASS_F7_INDEPENDENT_FULL" if args.full else "PASS_F7_INDEPENDENT_QUICK")


if __name__ == "__main__":
    main()
