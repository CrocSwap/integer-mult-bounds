#!/usr/bin/env python3
"""Replay the frozen sign-metric checks in a new output directory."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REVIEW = "lanes/oblique-native-20261017/sign-metric-review-20261020"
UNIT_REVIEW = "lanes/oblique-native-20261017/sign-metric-unit-review-20261020"
CASES = [
    ("response24", "root/check_sign_metric_involutions_20261020.py", "--output",
     "root/sign-metric-normal-20261020", ("CHECKS.json", "RESPONSE.json")),
    ("review24", REVIEW + "/check_review.py", "--out",
     REVIEW + "/run-normal", ("CHECKS.json",)),
    ("reader24", REVIEW + "/check_reader_addendum.py", None,
     REVIEW, ("READER-CHECKS.json",)),
    ("capture32", "root/check_sign_metric_unit_capture_20261020.py", "--output",
     "root/sign-metric-unit-normal-20261020", ("CHECKS.json", "RESPONSE.json")),
    ("review32", UNIT_REVIEW + "/check_review.py", "--out",
     UNIT_REVIEW + "/run-normal", ("CHECKS.json",)),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sources(manifest):
    for entry in manifest["files"]:
        path = HERE / entry["path"]
        if path.stat().st_size != entry["bytes"] or digest(path) != entry["sha256"]:
            raise ValueError("Source changed: " + entry["path"])


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
        for name, script, option, expected_dir, names in CASES:
            target = output / name / mode
            target.mkdir(parents=True)
            command = [sys.executable, "-I", *flags, "-B", str(scratch / script)]
            if option:
                command.extend((option, str(target)))
            result = subprocess.run(command, cwd=scratch, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, check=False)
            (target / "stdout.log").write_text(result.stdout)
            if result.returncode:
                raise RuntimeError(name + " failed; read " + str(target / "stdout.log"))
            files = []
            for filename in names:
                actual = target / filename if option else scratch / expected_dir / filename
                expected = HERE / "frozen" / expected_dir / filename
                if actual.read_bytes() != expected.read_bytes():
                    raise ValueError(name + " differs from the frozen " + filename)
                if not option:
                    shutil.copyfile(actual, target / filename)
                files.append({"name": filename, "sha256": digest(actual),
                              "matches_frozen_bytes": True})
            results.append({"check": name, "mode": mode, "files": files})
            print("PASS " + name + " " + mode, flush=True)
        shutil.rmtree(scratch)
    check_sources(manifest)
    receipt = {
        "status": "PASS_SIGN_METRIC_CAPTURE_ANNEX",
        "checks": results,
        "source_files_checked": len(manifest["files"]),
        "sources_sha256": digest(HERE / "SOURCES.json"),
        "runner_sha256": digest(Path(__file__)),
        "source_files_unchanged": True,
        "original_scripts_unchanged": True,
        "native_word_or_invoice_checked": False,
        "main_encoder_suite_run": False,
    }
    (output / "REPLAY.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
