#!/usr/bin/env python3
"""Replay the pinned response package in a new output directory."""

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
MODEL = "lanes/oblique-native-20261017/signed-metric-reciprocal-20261020"
REVIEW = "lanes/independent-review-20261017"
CALLER = "lanes/cover-algebra/reciprocal-selected-baseline-20261020"


def digest(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return sha256(raw).hexdigest()


def verify_sources(manifest):
    for name, record in manifest["frozen_files"].items():
        path = HERE / "frozen" / name
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != record["sha256"]:
            raise ValueError("Frozen source changed: " + name)
        if path.suffix == ".gz" and digest(path) != record["decompressed_sha256"]:
            raise ValueError("Frozen payload changed: " + name)


def tasks():
    return [
        ("rank-two", "root/check_reciprocal_rank_two_20261020.py", [],
         [("root/RECIPROCAL-RANK-TWO-20261020.json", "root/RECIPROCAL-RANK-TWO-20261020.json")]),
        ("rank-two-review", REVIEW + "/reciprocal-rank-two-review-20261020/check_review.py", [],
         [(REVIEW + "/reciprocal-rank-two-review-20261020/CHECKS.json",
           REVIEW + "/reciprocal-rank-two-review-20261020/CHECKS.json")]),
        ("family", MODEL + "/check_family.py", ["--out", "results/family"],
         [("results/family/CHECKS.json", MODEL + "/family-normal/CHECKS.json")]),
        ("model", MODEL + "/check_model.py", ["--out", "results/model"],
         [("results/model/CHECKS.json", MODEL + "/model-normal-v2/CHECKS.json"),
          ("results/model/RESPONSE.json.gz", MODEL + "/model-normal-v2/RESPONSE.json.gz")]),
        ("native", MODEL + "/emit_native.py", ["--out", "results/native"],
         [("results/native/CHECKS.json", MODEL + "/native-normal/CHECKS.json"),
          ("results/native/NATIVE.json.gz", MODEL + "/native-normal/NATIVE.json.gz")]),
        ("native-review", REVIEW + "/signed-metric-native-review-20261020/check_review.py",
         ["--out", "results/native-review.json"],
         [("results/native-review.json", REVIEW + "/signed-metric-native-review-20261020/FINAL-CHECKS.json")]),
        ("coalesced", MODEL + "/emit_coalesced.py", ["--out", "results/coalesced"],
         [("results/coalesced/CHECKS.json", MODEL + "/coalesced-normal/CHECKS.json"),
          ("results/coalesced/NATIVE.json.gz", MODEL + "/coalesced-normal/NATIVE.json.gz")]),
        ("ordered-caller", CALLER + "/check_reciprocal_caller.py", ["--out", "results/caller.json"],
         [("results/caller.json", CALLER + "/CHECKS.json")]),
        ("conditional-clean-reflection", CALLER + "/check_clean_reflection.py",
         ["--out", "results/clean-reflection.json"],
         [("results/clean-reflection.json", CALLER + "/CLEAN-CHECKS.json")]),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    verify_sources(manifest)
    reports = []
    for mode, flags in (("normal", []), ("optimized", ["-O"])):
        work = output / mode
        shutil.copytree(HERE / "frozen", work)
        (work / "results").mkdir()
        for name, script, arguments, comparisons in tasks():
            command = [sys.executable, "-I", "-B", *flags, str(work / script), *arguments]
            start = time.monotonic()
            with (work / "results" / (name + ".log")).open("w") as log:
                subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT, check=True)
            compared = {}
            for produced, expected in comparisons:
                actual_hash = digest(work / produced)
                expected_hash = digest(HERE / "frozen" / expected)
                if actual_hash != expected_hash:
                    raise ValueError("Replay differs from frozen payload: " + mode + "/" + produced)
                compared[produced] = actual_hash
            reports.append({"mode": mode, "check": name,
                            "command": ["python3", "-I", "-B", *flags, script, *arguments],
                            "payloads": compared,
                            "elapsed_seconds": round(time.monotonic() - start, 3)})
            print("PASS " + mode + " " + name, flush=True)
    verify_sources(manifest)
    receipt = {
        "status": "PASS_RECIPROCAL_NATIVE_RESPONSES",
        "python": sys.version, "platform": platform.platform(),
        "replay_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_manifest_sha256": sha256((HERE / "SOURCES.json").read_bytes()).hexdigest(),
        "frozen_source_count": len(manifest["frozen_files"]), "runs": reports,
        "comparison": "Exact receipt bytes and decompressed gzip payload bytes.",
        "scope": "Response proof checks, local native words, and conditional caller algebra. No complete supplier replay.",
    }
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    main()
