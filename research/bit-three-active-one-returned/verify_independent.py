#!/usr/bin/env python3
"""Replay the independent front end against a complete primary build."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

if not __debug__:
    raise SystemExit("Run this verifier without -O. Historical sources use assert.")
ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-build", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    primary, build = args.primary_build.resolve(), args.build.resolve()
    require(not build.exists(), "The build directory exists.")
    manifest = json.loads((ROOT / "SOURCE-MANIFEST.json").read_text())
    for item in manifest["files"]:
        require(hashlib.sha256((ROOT / item["package"]).read_bytes()).hexdigest()
                == item["sha256"], "Source hash: " + item["package"])
    receipt = json.loads((primary / "receipt.json").read_text())
    require(receipt["status"] == "PASS_COMPLETE_FINITE_CHECKS", "Primary status")
    for rank in [2, 3]:
        require(hashlib.sha256((primary / f"rank{rank}.bin").read_bytes()).hexdigest()
                == receipt["inputs"][str(rank)]["sha256"], "Primary input hash")
    shutil.copytree(ROOT / "independent-sources", build)
    base = build / "work/four-register"
    source, audit = base / "independent", base / "independent-audit"
    compiler = os.environ.get("CXX") or shutil.which("clang++") or shutil.which("g++")
    require(compiler is not None, "A C++17 compiler is required.")
    stages = []
    def run(label, command, output=None):
        print("Run:", " ".join(map(str, command)), flush=True)
        target = output or build / (label + ".stdout.log")
        with target.open("w") as out, (build / (label + ".stderr.log")).open("w") as err:
            subprocess.run(list(map(str, command)), cwd=build, check=True,
                           stdout=out, stderr=err)
        stages.append(label)
    run("catalogue", [sys.executable, "-E", "-B", source / "off_pattern_spaces.py"])
    run("independent-catalogue", [sys.executable, "-E", "-B", audit / "check_off_catalogue.py"])
    run("rank2-families", [sys.executable, "-E", "-B", base / "dirty_rank2.py"])
    levels = json.loads((source / "off-pattern-spaces.json").read_text())["levels"]
    with (audit / "rank2-pools.txt").open("w") as out:
        pools = levels[1]["representatives"]
        out.write(str(len(pools)) + "\n")
        for pool in pools:
            out.write(str(len(pool["projectors"])) + "\n")
            for x, y in pool["projectors"]:
                matrix = sum(y << (4 * i) for i in range(4) if x >> i & 1)
                out.write(f"{x} {y} {pool['space'].index(matrix & 0x7bde)}\n")
    for original, destination in [("pools.txt", "rank3-pools.txt"),
                                  ("multisets.jsonl", "rank3-multisets.jsonl"),
                                  ("orders.txt", "rank3-word-input.txt"),
                                  ("orders.jsonl", "rank3-parity-survivors.jsonl"),
                                  ("rank2.bin", "rank2-words.bin"),
                                  ("rank3.bin", "rank3-words.bin")]:
        shutil.copyfile(primary / original, source / destination)
    for name in ["check_rank3_multisets", "check_rank3_orders"]:
        run(name + "-compile", [compiler, "-O3", "-std=c++17", audit / (name + ".cpp"),
                                 "-o", audit / name])
    run("rank2-multisets", [audit / "check_rank3_multisets", audit / "rank2-pools.txt", "2"],
        audit / "rank2-multisets.jsonl")
    run("rank3-multisets", [audit / "check_rank3_multisets", source / "rank3-pools.txt"],
        audit / "rank3-multisets.jsonl")
    run("input-binding", [sys.executable, "-E", "-B", audit / "check_input_binding.py"])
    run("rank2-orders", [sys.executable, "-E", "-B", audit / "check_rank2_orders.py"])
    run("rank3-orders", [audit / "check_rank3_orders", source / "rank3-word-input.txt",
                         source / "rank3-words.bin"], audit / "RANK3-ORDERS-RESULT.json")
    shutil.copyfile(ROOT / "field101.cpp", base / "dirty_f101.cpp")
    run("polynomial-controls", [sys.executable, "-E", "-B", base / "dirty_f101_controls.py"])
    expected = json.loads((ROOT / "independent-receipt.json").read_text())
    reports = {name: json.loads((audit / name).read_text()) for name in
               ["OFF-CATALOGUE-RESULT.json", "INPUT-BINDING-RESULT.json",
                "RANK2-FRONT-END-RESULT.json", "RANK3-ORDERS-RESULT.json"]}
    old_reports = expected["independent_receipts"]
    for name, value in reports.items():
        require(value == old_reports[name], "Independent report: " + name)
    final = {"status": "PASS_INDEPENDENT_RETURNED_REGISTER_FRONT_END", "stages": stages,
             "reports": reports, "polynomial_controls": json.loads((base / "dirty-f101-controls.json").read_text()),
             "source_manifest_sha256": hashlib.sha256((ROOT / "SOURCE-MANIFEST.json").read_bytes()).hexdigest()}
    (build / "receipt.json").write_text(json.dumps(final, indent=2) + "\n")
    print(final["status"])


if __name__ == "__main__":
    main()
