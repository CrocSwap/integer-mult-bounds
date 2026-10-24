#!/usr/bin/env python3
"""Run the exact package checks in sequence. Keep all source files unchanged."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT / "frozen"
NATIVE = "lanes/new-native-recipes-20261017/"
BRIDGE = "lanes/bridge-review-20261017/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_sources():
    entries = json.loads((ROOT / "SOURCE-MANIFEST.json").read_bytes())["immutable_inputs"]
    for entry in entries:
        data = (ROOT / entry["path"]).read_bytes()
        require(digest(data) == entry["sha256"], "Source changed: " + entry["path"])
        if "decompressed_sha256" in entry:
            require(digest(gzip.decompress(data)) == entry["decompressed_sha256"],
                    "Payload changed: " + entry["path"])
    return len(entries)


def worker():
    script, output, *arguments = sys.argv[2:]
    allowed = (ROOT, Path(output).resolve(), Path(sys.base_prefix).resolve())
    opened = set()
    def audit(event, arguments):
        if event != "open" or not isinstance(arguments[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(arguments[0])).resolve()
        require(path == Path(os.devnull) or any(path.is_relative_to(base) for base in allowed),
                "File access outside the package, output, or Python runtime: " + str(path))
        if path.is_relative_to(ROOT):
            opened.add(path.relative_to(ROOT).as_posix())
    sys.addaudithook(audit)
    sys.argv = [script, *arguments]
    runpy.run_path(script, run_name="__main__")
    (Path(output) / "FILE-ACCESS.json").write_text(json.dumps(sorted(opened), indent=2) + "\n")


def jobs():
    return [
        ("unitary_footprint", FROZEN / "lanes/independent-review-20261017/unitary-footprint-review-20261020/check_review.py", "--out", "result.json", [],
         {"result.json": "lanes/independent-review-20261017/unitary-footprint-review-20261020/REVIEW-NORMAL.json"}),
        ("unitary_native", FROZEN / (NATIVE + "unitary-clean-24-review-20261020/check.py"), "--out", "result", [
            "--source-freeze", "95fa9e61ddf860f3305fff398996077b6ecc164c011d37b60f6db0e459719fc5",
            "--payload-sha256", "472935ba574b78c6ec1fd6f02fc1c0c29d37b53f73ec55b8583904bd5d5af245"],
         {"result/REVIEW.json": NATIVE + "unitary-clean-24-review-20261020/normal-final/REVIEW.json",
          "result/INPUTS.json": NATIVE + "unitary-clean-24-review-20261020/normal-final/INPUTS.json"}),
        ("signed_metric", FROZEN / (BRIDGE + "signed-metric-review-20261020/check_review.py"), "--output", "result", [],
         {"result/REVIEW-CHECKS.json": BRIDGE + "signed-metric-review-20261020/normal/REVIEW-CHECKS.json"}),
        ("signed_native", ROOT / "portable/check_signed_clean.py", "--out", "result", [],
         {"result/REVIEW.json": NATIVE + "signed-clean-native-review-20261020/normal-final/REVIEW.json",
          "result/INPUTS.json": NATIVE + "signed-clean-native-review-20261020/normal-final/INPUTS.json"}),
        ("signed_family", FROZEN / "root/check_signed_metric_family.py", "--out", "result.json", [],
         {"result.json": "root/signed-metric-family-normal.json"}),
        ("signed_family_review", FROZEN / (BRIDGE + "signed-family-review-20261020/check_family_review.py"), "--output", "result.json", [],
         {"result.json": BRIDGE + "signed-family-review-20261020/normal.json"}),
        ("rational_grid", FROZEN / (NATIVE + "rational-packing-grid-review-20261020/check.py"), "--out", "result", [],
         {"result/REVIEW.json": NATIVE + "rational-packing-grid-review-20261020/normal-final/REVIEW.json",
          "result/INPUTS.json": NATIVE + "rational-packing-grid-review-20261020/normal-final/INPUTS.json"}),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    require(not output.exists(), "Use a new output directory")
    require(shutil.disk_usage(ROOT).free >= 3 * 1024**3, "At least 3 GiB of free disk space is required")
    count = verify_sources()
    output.mkdir(parents=True)
    reports = []
    for name, script, flag, result, extra, expected in jobs():
        for mode in ("normal", "optimized"):
            directory = output / name / mode
            directory.mkdir(parents=True)
            command = [sys.executable, "-I", "-B"] + (["-O"] if mode == "optimized" else [])
            command += [str(ROOT / "replay.py"), "--worker", str(script), str(directory), flag, str(directory / result), *extra]
            print("RUN", name, mode, flush=True)
            started = time.monotonic()
            with (directory / "stdout.log").open("w") as log:
                completed = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            require(completed.returncode == 0, "Check failed. Read " + str(directory / "stdout.log"))
            matches = {}
            for relative, frozen in expected.items():
                actual = (directory / relative).read_bytes()
                require(actual == (FROZEN / frozen).read_bytes(), "Frozen receipt mismatch: " + name + "/" + relative)
                if mode == "optimized":
                    require(actual == (output / name / "normal" / relative).read_bytes(), "Normal and optimized receipts differ")
                matches[relative] = digest(actual)
            reports.append({"check": name, "mode": mode, "seconds": round(time.monotonic()-started, 3),
                            "receipts_equal_frozen": matches, "file_access_confined": True})
            print("PASS", name, mode, flush=True)
    require(verify_sources() == count, "Source count changed")
    receipt = {"status": "PASS_CENTRE_METRIC_ENCODERS", "immutable_inputs": count,
               "checks": reports, "normal_optimized_equal": True, "frozen_sources_unchanged": True,
               "python": platform.python_version(), "platform": platform.platform(),
               "replay_sha256": digest(Path(__file__).read_bytes()),
               "portable_signed_checker_sha256": digest((ROOT / "portable/check_signed_clean.py").read_bytes()),
               "source_manifest_sha256": digest((ROOT / "SOURCE-MANIFEST.json").read_bytes()),
               "scope": "Exact local proofs, matrices, scalar words, native words, phases, invoices, and grid checks. No recursive supplier or kappa claim."}
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker()
    else:
        main()
