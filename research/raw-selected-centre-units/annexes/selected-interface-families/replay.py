#!/usr/bin/env python3
"""Replay the six frozen checks for the selected-interface families."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
BRIDGE = "lanes/bridge-review-20261017/"
INDEPENDENT = "lanes/independent-review-20261017/"
LIVE = "lanes/new-native-recipes-20261017/forward-eight-review-20261018/"
CASES = [
    ("structured", BRIDGE + "structured-centres-review-20261018/check_review.py", "fixed",
     {"REVIEW.json": BRIDGE + "structured-centres-review-20261018/REVIEW.json"}),
    ("minor-endpoints", BRIDGE + "structured-centres-review-20261018/check_interfaces.py", "fixed",
     {"INTERFACES.json": BRIDGE + "structured-centres-review-20261018/INTERFACES.json"}),
    ("signed-pivots", BRIDGE + "signed-centres-review-20261018/check_signed_pivots.py", "fixed",
     {"SIGNED-PIVOTS.json": BRIDGE + "signed-centres-review-20261018/SIGNED-PIVOTS.json"}),
    ("raw-words", INDEPENDENT + "check_new_raw.py", "file",
     {"REVIEW.json": INDEPENDENT + "NEW-RAW-REVIEW-FINAL.json"}),
    ("signed-words", INDEPENDENT + "check_new_signed.py", "file",
     {"REVIEW.json": INDEPENDENT + "NEW-SIGNED-REVIEW.json"}),
    ("live-eight", LIVE + "check.py", "directory",
     {"REVIEW.json": LIVE + "final-normal/REVIEW.json",
      "INPUTS.json": LIVE + "final-normal/INPUTS.json"}),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sources(manifest):
    for entry in manifest["files"]:
        path = HERE / entry["path"]
        raw = path.read_bytes()
        if len(raw) != entry["bytes"] or hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError("Source changed: " + entry["path"])
        if "decompressed_sha256" in entry:
            if hashlib.sha256(gzip.decompress(raw)).hexdigest() != entry["decompressed_sha256"]:
                raise ValueError("Compressed payload changed: " + entry["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    if output.is_relative_to(HERE):
        raise ValueError("The output directory must be outside the annex")
    if output.exists():
        raise ValueError("The output directory must be new")
    if shutil.disk_usage(HERE).free < 3 * 1024**3:
        raise ValueError("At least 3 GiB free space is required")
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    check_sources(manifest)
    output.mkdir(parents=True)
    results = []
    for mode, flags in (("normal", []), ("optimized", ["-O"])):
        scratch = output / ("source-" + mode)
        shutil.copytree(HERE / "frozen", scratch)
        for name, script, kind, expected_files in CASES:
            target = output / name / mode
            target.parent.mkdir(parents=True, exist_ok=True)
            command = [sys.executable, "-I", *flags, "-B", str(scratch / script)]
            if kind == "file":
                target.mkdir()
                command.extend(("--out", str(target / "REVIEW.json")))
            elif kind == "directory":
                command.extend(("--out", str(target)))
            print("RUN " + name + " " + mode, flush=True)
            result = subprocess.run(command, cwd=scratch, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, check=False)
            target.mkdir(exist_ok=True)
            (target / "stdout.log").write_text(result.stdout)
            if result.returncode:
                raise RuntimeError(name + " failed; read " + str(target / "stdout.log"))
            files = []
            for filename, original in expected_files.items():
                actual = scratch / original if kind == "fixed" else target / filename
                expected = HERE / "frozen" / original
                if actual.read_bytes() != expected.read_bytes():
                    raise ValueError(name + " differs from the frozen " + filename)
                if kind == "fixed":
                    shutil.copyfile(actual, target / filename)
                files.append({"name": filename, "sha256": digest(actual),
                              "matches_frozen_bytes": True})
            results.append({"check": name, "mode": mode, "files": files})
            print("PASS " + name + " " + mode, flush=True)
        shutil.rmtree(scratch)
    check_sources(manifest)
    receipt = {
        "status": "PASS_SELECTED_INTERFACE_FAMILIES_ANNEX",
        "checks": results,
        "source_files_checked": len(manifest["files"]),
        "sources_sha256": digest(HERE / "SOURCES.json"),
        "runner_sha256": digest(Path(__file__)),
        "source_files_unchanged": True,
        "original_scripts_unchanged": True,
        "main_package_suite_run": False,
        "retained_core_phase_suite_rerun": False,
        "producer_emission_rerun": False,
    }
    (output / "REPLAY.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
