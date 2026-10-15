#!/usr/bin/env python3
"""Run the normal verifier, then the unchanged upstream native cohort checkers.

Usage: python native.py --out /tmp/r420-forest-native --boost /path/to/boost
Requires a C++17 compiler and genuine Boost headers. Every subprocess has a
180-second limit and the whole run has a 20-minute deadline. Logs, records,
candidate artifacts, and executables are written only under --out.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from construct import canonical_payload, SOURCE_PATH


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / "e8-bit-carrier-skeleton"
BIT = PACKAGE / "code/bit"
CHECKERS = BIT / "checkers"
PAID_HISTOGRAM = [[1, 1320], [2, 1440], [4, 60], [5, 120], [8, 9]]
LEG_PASS = "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE"
FIVE_PASS = "PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"
BRIDGE_PASS = "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Runner:
    def __init__(self, out: Path):
        self.out = out
        self.deadline = time.monotonic() + 1200
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")

    def run(self, name: str, command: list, *, required: bool = True) -> dict:
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, "native verification exceeded its 20-minute deadline")
        began = time.monotonic()
        try:
            result = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", env=self.env,
                                    timeout=min(180, remaining), check=False)
        except subprocess.TimeoutExpired as error:
            (self.out / (name + ".log")).write_text(str(error) + "\n", encoding="utf-8")
            raise RuntimeError(f"{name} timed out; see {self.out / (name + '.log')}") from error
        log = self.out / (name + ".log")
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        receipt = {"exit": result.returncode, "seconds": round(time.monotonic() - began, 6),
                   "log": log.name, "stderr": result.stderr.strip()}
        require(not required or result.returncode == 0,
                f"{name} failed ({result.returncode}); see {log}: {result.stderr[-1000:]}")
        print(f"{name}: exit {result.returncode}", flush=True)
        return receipt


def compile_checkers(runner: Runner, cxx: str, boost: Path) -> dict[str, Path]:
    require((boost / "boost/multiprecision/cpp_int.hpp").is_file(), "genuine Boost headers missing")
    bindir = runner.out / "bin"
    bindir.mkdir(exist_ok=True)
    common = [cxx, "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9",
              "-I" + str(PACKAGE / "portable-include"), "-I" + str(CHECKERS), "-I" + str(boost)]
    jobs = [("legality", "legality_h.cpp", []),
            ("columns_h", "columns_h.cpp", ["-DVPORTS=120", "-DRHELP=420"]),
            ("columns_k4", "columns_k.cpp", ["-DVPORTS=120", "-DRHELP=420", "-DKPAIRS=4"]),
            ("columns_k5", "columns_k.cpp", ["-DVPORTS=120", "-DRHELP=420", "-DKPAIRS=5"])]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(runner.run, "compile-" + name,
                               common + extra + [CHECKERS / source, "-o", bindir / name])
                   for name, source, extra in jobs]
        for future in futures:
            future.result()
    return {name: bindir / name for name, _, _ in jobs}


def check_word(runner: Runner, binaries: dict[str, Path], name: str, word: Path) -> dict:
    root = runner.out / name
    root.mkdir(exist_ok=True)
    records, cin, cout = (root / sub for sub in ("records", "cin", "cout"))
    python = [sys.executable, "-I", "-B"]
    runner.run(name + "-export", python + [BIT / "export_records.py", word, records])
    runner.run(name + "-stage", python + [BIT / "regression/stage_cohort.py", records, records, cin, cout])
    runner.run(name + "-legality", [binaries["legality"], cin, cout, cout / "legality.json"])
    legality = read_json(cout / "legality.json")
    require(legality["status"] == LEG_PASS and legality["copies"] == legality["erasures"] == 9,
            name + ": unexpected legality receipt")
    require(legality["rank_mass"] == 5112 and legality["paid_histogram"] == PAID_HISTOGRAM,
            name + ": paid profile changed")
    checked = {}
    for binary, stages, columns, bridges in [("columns_h", 5, 900, 6),
                                              ("columns_k4", 9, 1380, 18),
                                              ("columns_k5", 11, 1620, 24)]:
        receipt_path = cout / (binary + ".json")
        receipt_path.unlink(missing_ok=True)
        run = runner.run(name + "-" + binary,
                         [binaries[binary], cout / "COHORT249-RECORDS.bin", receipt_path], required=False)
        if run["exit"] == 0:
            receipt = read_json(receipt_path)
            require(receipt["status"] == (FIVE_PASS if stages == 5 else BRIDGE_PASS), "column status")
            require(receipt["formal_columns_checked"] == columns and len(receipt["stages"]) == stages,
                    "formal column or stage count")
            require(receipt["bridge_additions"] == bridges * 120 and
                    len(receipt["negative_controls"]) == bridges and
                    all(control["rejected"] for control in receipt["negative_controls"]), "bridge controls")
            require(receipt["local_raw_H"] == PAID_HISTOGRAM and
                    int(receipt["payload_prefix_upper"]) < 2 ** 104, "profile or fixed prefix cap")
            run["receipt"] = receipt
        checked[binary] = run
    runner.run(name + "-gram", python + [CHECKERS / "gram_frames.py", records,
                                          "--gram", "e8ham", "--h", "8", "--positive"])
    return {"legality": legality, "columns": checked, "gram_passed": True}


def corruption_control(runner: Runner, binaries: dict[str, Path]) -> dict:
    """Delete one target-to-target D ADD; all frame and COPY events stay intact."""
    source = runner.out / "candidate/cout"
    mutant = runner.out / "candidate-mutant"
    mutant.mkdir(exist_ok=True)
    for path in source.iterdir():
        if path.is_file() and path.suffix != ".json":
            shutil.copyfile(path, mutant / path.name)
        elif path.name in ("COHORT249-FRAMES.json", "COHORT249-INITIAL.json", "COHORT249-SELECTION.json"):
            shutil.copyfile(path, mutant / path.name)
    raw = (source / "COHORT249-RECORDS.bin").read_bytes()
    require(len(raw) % 24 == 0, "record alignment")
    rows = list(struct.iter_unpack("<6i", raw))
    sites = [i for i, row in enumerate(rows) if row[0] == 1 and row[5] == 1
             and 120 <= row[1] < 240 and 120 <= row[2] < 240]
    require(bool(sites), "candidate has no target unpreparation ADD")
    index = sites[-1]
    (mutant / "COHORT249-RECORDS.bin").write_bytes(raw[:24 * index] + raw[24 * (index + 1):])
    runner.run("mutant-legality", [binaries["legality"], runner.out / "candidate/cin", mutant,
                                    mutant / "legality.json"])
    require(read_json(mutant / "legality.json")["status"] == LEG_PASS, "mutant legality")
    results = {}
    for binary in ("columns_h", "columns_k4", "columns_k5"):
        run = runner.run("mutant-" + binary,
                         [binaries[binary], mutant / "COHORT249-RECORDS.bin", mutant / (binary + ".json")],
                         required=False)
        run["endpoint_rejected"] = (run["exit"] != 0 and
                                    "local defining-decoder full formal column" in run["stderr"])
        results[binary] = run
    return {"mutation": "delete final target-to-target D unpreparation ADD",
            "deleted_record_index": index, "deleted_record": rows[index],
            "legality_passed": True, "columns": results,
            "all_endpoint_rejected": all(result["endpoint_rejected"] for result in results.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--boost", type=Path, required=True)
    parser.add_argument("--cxx", default=os.environ.get("CXX", "c++"))
    parser.add_argument("--candidate", type=Path,
                        help="candidate path (default: package data/word.json.gz)")
    parser.add_argument("--recipe", type=Path, help="recipe for --candidate; both options are required together")
    parser.add_argument("--expect-prefix-rejection", action="store_true",
                        help="require the independently valid unconstrained candidate to fail the fixed 104-bit cap")
    args = parser.parse_args()
    out = args.out.resolve()
    require(not out.is_relative_to(HERE.parents[1]), "--out must be outside the repository")
    out.mkdir(parents=True, exist_ok=True)
    (out / "NATIVE-RESULTS.json").unlink(missing_ok=True)
    runner = Runner(out)
    require((args.candidate is None) == (args.recipe is None),
            "--candidate and --recipe must be provided together")
    input_word = args.candidate or HERE / "data/word.json.gz"
    input_recipe = args.recipe or HERE / "data/recipe.json"
    opener = gzip.open if input_word.suffix == ".gz" else open
    with opener(input_word, "rt", encoding="utf-8") as stream:
        candidate = json.load(stream)
    recipe = read_json(input_recipe)
    candidate_path, recipe_path = out / "candidate.json.gz", out / "recipe.json"
    candidate_path.write_bytes(gzip.compress(canonical_payload(candidate), mtime=0))
    write_json(recipe_path, recipe)
    verifier_command = [sys.executable, "-B", HERE / "verify.py", "--source", SOURCE_PATH,
                        "--candidate", candidate_path, "--recipe", recipe_path,
                        "--json", out / "VERIFY.json"]
    if args.expect_prefix_rejection:
        verifier_command.append("--expect-prefix-rejection")
    runner.run("normal-verifier", verifier_command)
    binaries = compile_checkers(runner, args.cxx, args.boost.resolve())
    baseline = check_word(runner, binaries, "baseline", SOURCE_PATH)
    candidate_result = check_word(runner, binaries, "candidate", candidate_path)
    baseline_passed = all(run["exit"] == 0 for run in baseline["columns"].values())
    if args.expect_prefix_rejection:
        prefix = read_json(out / "VERIFY.json")["positive_prefix"]["candidate"]
        control = {"not_run": "The fixed prefix check rejects before the endpoint audit can run."}
        passed = (baseline_passed and prefix["payload_bits"] == 106 and
                  not prefix["below_2_pow_104"] and
                  all(run["exit"] != 0 and run["stderr"] == "payloadfiniteprefix2^104"
                      for run in candidate_result["columns"].values()))
        status = "PASS_EXPECTED_UNCONSTRAINED_PREFIX_REJECTION" if passed else "NATIVE_CHECK_REJECTED"
    else:
        control = corruption_control(runner, binaries)
        passed = (baseline_passed and all(run["exit"] == 0 for run in candidate_result["columns"].values())
                  and control["all_endpoint_rejected"])
        status = "PASS_UNCHANGED_NATIVE_COHORT_CHECKERS" if passed else "NATIVE_CHECK_REJECTED"
    source_files = [BIT / "export_records.py", BIT / "regression/stage_cohort.py"] + [
        CHECKERS / name for name in ("legality_h.cpp", "columns_h.cpp", "columns_k.cpp", "gram_frames.py")]
    receipt = {"status": status,
               "candidate_canonical_sha256": hashlib.sha256(canonical_payload(candidate)).hexdigest(),
               "checker_source_sha256": {str(path.relative_to(PACKAGE)): hashlib.sha256(path.read_bytes()).hexdigest()
                                         for path in source_files},
               "configuration": "HDIM=8 NCOPY=9 VPORTS=120 RHELP=420; columns_h, KPAIRS=4,5",
               "fixed_payload_cap": "payload < 2^104; unchanged upstream checker",
               "baseline": baseline, "candidate": candidate_result, "candidate_corruption_control": control,
               "scope": "Concrete native legality, finite F2 columns, bridge controls, Gram witnesses and "
                        "positive-prefix bound only. All-size forest theorem, global routing and outer pricing "
                        "are separate; no improved asymptotic constant is claimed."}
    write_json(out / "NATIVE-RESULTS.json", receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(out / "NATIVE-RESULTS.json")}))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
