#!/usr/bin/env python3
"""Run the unchanged signed-family coefficient checks in fresh copies."""

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
FROZEN = HERE / "frozen"
CHECKS = [
    ("producer", "lanes/controller-followthrough-20261017/reciprocal-centres-20261018",
     "check_reciprocal_centres.py", "RECIPROCAL-CENTRES.json"),
    ("independent", "lanes/bridge-review-20261017/reciprocal-centres-review-20261020",
     "check_review.py", "REVIEW.json"),
]


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def check_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        data = (FROZEN / row["path"]).read_bytes()
        need(len(data) == row["bytes"] and digest(data) == row["sha256"], "Frozen source: " + row["path"])
        if "decompressed_sha256" in row:
            need(digest(gzip.decompress(data)) == row["decompressed_sha256"], "Frozen matrix payload")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    need(not out.is_relative_to(HERE), "Output must be outside the source annex")
    out.parent.mkdir(parents=True, exist_ok=True)
    need(shutil.disk_usage(out.parent).free >= 3 * 1024**3, "At least 3 GiB free disk space is required")
    out.mkdir(exist_ok=False)
    manifest = check_sources()
    results = []
    for name, relative, script, receipt in CHECKS:
        expected = (FROZEN / relative / receipt).read_bytes()
        for mode in ("normal", "optimized"):
            result = out / name / mode
            result.mkdir(parents=True)
            work = result / "campaign"
            shutil.copytree(FROZEN, work)
            command = [sys.executable, "-I", "-B"] + (["-O"] if mode == "optimized" else [])
            command.append(str(work / relative / script))
            start = time.monotonic()
            with (result / "stdout.log").open("w") as log:
                run = subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT, check=False)
            need(run.returncode == 0, "Failed " + name + " " + mode + "; read " + str(result / "stdout.log"))
            actual = (work / relative / receipt).read_bytes()
            need(actual == expected, "Exact frozen receipt comparison: " + name + " " + mode)
            (result / receipt).write_bytes(actual)
            results.append({"check": name, "mode": mode, "status": json.loads(actual)["status"],
                            "seconds": round(time.monotonic() - start, 3),
                            "receipt_sha256": digest(actual), "equal_frozen_bytes": True})
            shutil.rmtree(work)
            print(name + " " + mode + " PASS", flush=True)
    check_sources()
    report = {"status": "PASS_SIGNED_RANK_EIGHT_COEFFICIENT_ANNEX", "checks": results,
              "source_files": len(manifest["files"]), "frozen_sources_unchanged": True,
              "runner_sha256": digest(Path(__file__).read_bytes()),
              "source_manifest_sha256": digest((HERE / "SOURCES.json").read_bytes()),
              "python": platform.python_version(), "platform": platform.platform(),
              "child_processes_run_concurrently": 1,
              "comparison": "All four JSON receipts match exact frozen bytes. The source gzip file is immutable; its decompressed payload hash is also checked.",
              "scope": "The signed48 full-unit and two-principal-unit coefficient classification, its six-step ordinary gauge, and its fixed64 complement. No new native schedule, native phase replay, all-stage composition, precision, supplier invoice, or complete kappa claim."}
    (out / "REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
