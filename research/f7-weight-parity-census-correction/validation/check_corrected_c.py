#!/usr/bin/env python3
"""Compile corrected C, compare all small splits with raw-product brute.

Budgeted candidate leaf counts are deliberately NOT equated to all restored
leaf counts. All four budget modes must give the brute universal count.
"""
import argparse
import json
import subprocess
import tempfile
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from brute_validation import canonical, describe, brute


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def run(binary, split, directory, mode="both", extra=()):
    flags = {"both": [], "even": ["--no-odd-budget"],
             "odd": ["--no-even-budget"], "none": ["--no-budgets"]}[mode]
    hitfile, datafile = directory / "hits.txt", directory / "result.json"
    command = [str(binary), split, "--hits", str(hitfile), "--json",
               str(datafile), *flags, *extra]
    proc = subprocess.run(command, capture_output=True, text=True)
    data = json.loads(datafile.read_text()) if datafile.exists() else None
    words = hitfile.read_text().splitlines() if hitfile.exists() else []
    return proc, data, words


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-source", type=Path, default=HERE.parent / "engine" / "corrected_census.c")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir or Path(tempfile.mkdtemp(prefix="f7-validation-"))
    output_dir.mkdir(parents=True, exist_ok=True)
    source = args.engine_source.resolve()
    ground = {"method": "raw itertools.product, no pruning; direct XOR-set coverage",
              "cases": [brute(3, 6), brute(3, 8), brute(4, 8)]}
    records = []
    binaries = {}
    for case in ground["cases"]:
        n, length = case["n"], case["L"]
        binary = output_dir / f"corrected_n{n}_l{length}"
        compile_command = ["cc", "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror",
                           f"-DN={n}", f"-DL={length}", str(source), "-o", str(binary)]
        subprocess.run(compile_command, check=True, capture_output=True, text=True)
        binaries[n, length] = binary
        for split, expected in case["splits"].items():
            for mode in ("both", "even", "odd", "none"):
                with tempfile.TemporaryDirectory(prefix="cgate-", dir=output_dir) as temporary:
                    proc, data, words = run(binary, split, Path(temporary), mode)
                require(proc.returncode == 0, (n, length, split, mode, proc.stderr))
                require(data["complete"] and not data["aborted"], data)
                total = data["total"][0]
                require(total["hits"] == expected["universal"], (n, length, split, mode, total, expected))
                require(len(words) == len(set(words)) == total["hits"], (n, length, split, mode))
                for text in words:
                    word = tuple(map(int, text))
                    details = describe(word, n)
                    require(len(word) == length and canonical(word) == word, text)
                    require(details["restored"] and details["universal"], text)
                    require(",".join(map(str, details["groups"]["weight"]["split"])) == split, text)
                if mode == "none":
                    require(total["all_restored_leaves"] == expected["restored"], (n, length, split, total, expected))
                else:
                    require(total["all_restored_leaves"] is None, (n, length, split, mode))
                records.append({"n": n, "L": length, "split": split,
                                "mode": mode, "nodes": total["nodes"],
                                "candidate_restored_leaves": total["candidate_restored_leaves"],
                                "universal": total["hits"], "pass": True})
    safety = []
    binary = binaries[4, 8]
    for cap in (1, 10, 50):
        with tempfile.TemporaryDirectory(prefix="capgate-", dir=output_dir) as temporary:
            proc, data, words = run(binary, "4,4", Path(temporary), extra=("--cap", str(cap)))
        require(proc.returncode == 2 and data["aborted"] and not data["complete"], (cap, proc, data))
        require(data["total"][0]["nodes"] == cap, data)
        require(data["total"][0]["all_restored_leaves"] is None, data)
        safety.append({"check": "capped_run", "cap": cap, "returncode": proc.returncode,
                       "complete": data["complete"], "nodes": data["total"][0]["nodes"], "pass": True})
    invalid = [[], ["4,4"], ["4,4", "--hits", "/no/such/path/hits"],
               ["4,4", "--hits", "/tmp/unused-census-output", "00", "000"],
               ["4,4", "--hits", "/tmp/unused-census-output", "0124"],
               ["4,4", "--hits", "/tmp/unused-census-output", "0123:abc"],
               ["5,4", "--hits", "/tmp/unused-census-output"],
               ["4,4", "--hits", "/tmp/unused-census-output", "--cap", "-1"]]
    for arguments in invalid:
        proc = subprocess.run([str(binary), *arguments], capture_output=True, text=True)
        require(proc.returncode == 1, (arguments, proc))
        require("complete=true" not in proc.stdout, proc)
        safety.append({"check": "invalid_input", "arguments": arguments,
                       "returncode": proc.returncode, "pass": True})
    with tempfile.TemporaryDirectory(prefix="filegate-", dir=output_dir) as temporary:
        directory = Path(temporary)
        existing = directory / "hits.txt"
        existing.write_text("preserve me\n")
        proc = subprocess.run([str(binary), "4,4", "--hits", str(existing)],
                              capture_output=True, text=True)
        require(proc.returncode == 1 and existing.read_text() == "preserve me\n", proc)
        safety.append({"check": "existing_hits_file_not_overwritten", "returncode": proc.returncode, "pass": True})
    output = {"source": str(source), "method": ground["method"],
              "comparison": "all splits, universal counts; all restored leaves only when no budgets",
              "runs": records, "safety": safety, "pass": True}
    target = output_dir / "corrected_c_results.json"
    target.write_text(json.dumps(output, indent=2) + "\n")
    print(f"PASS: {len(records)} brute comparisons; {len(safety)} fail-closed checks; {target}")


if __name__ == "__main__":
    main()
