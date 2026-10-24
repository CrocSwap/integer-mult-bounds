#!/usr/bin/env python3
"""Replay the unchanged terminal and finite rank checks in fresh copies."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
JOBS = (
    ("terminal", "lanes/independent-review-20261017/common-terminal-review-20261018/check_terminal.py",
     "PASS_INDEPENDENT_COMMON_COVER_TERMINAL"),
    ("rank_limit", "lanes/encoded-controller/cover-line-terminal-limit-20261018/check_limit.py",
     "PASS_COVER_ONLY_TERMINAL_RANK"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify_sources():
    entries = json.loads((ROOT / "SOURCES.json").read_bytes())["files"]
    for entry in entries:
        require(sha((ROOT / entry["path"]).read_bytes()) == entry["sha256"],
                "Source changed: " + entry["path"])
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    output = parser.parse_args().out.resolve()
    require(not output.exists(), "Use a new output directory")
    require(shutil.disk_usage(ROOT).free >= 3 * 2**30, "At least 3 GiB free is required")
    entries = verify_sources()
    output.mkdir(parents=True)
    reports = []
    for name, relative, expected_status in JOBS:
        for mode in ("normal", "optimized"):
            run = output / name / mode
            source = run / "source"
            shutil.copytree(ROOT / "frozen", source)
            command = [sys.executable, "-I", "-B"] + (["-O"] if mode == "optimized" else [])
            command.append(str(source / relative))
            print("RUN", name, mode, flush=True)
            start = time.monotonic()
            with (run / "stdout.log").open("w") as log:
                result = subprocess.run(command, cwd=source, stdout=log, stderr=subprocess.STDOUT)
            require(result.returncode == 0, "Check failed: " + str(run / "stdout.log"))
            receipt_path = Path(relative).parent / "CHECKS.json"
            actual = (source / receipt_path).read_bytes()
            frozen = (ROOT / "frozen" / receipt_path).read_bytes()
            require(actual == frozen, "Fresh receipt differs from frozen receipt")
            require(json.loads(actual)["status"] == expected_status, "Unexpected check status")
            if mode == "optimized":
                require(actual == (output / name / "normal/CHECKS.json").read_bytes(),
                        "Normal and optimized receipts differ")
            for entry in entries:
                require(sha((source / entry["campaign_path"]).read_bytes()) == entry["sha256"],
                        "Copied source changed: " + entry["campaign_path"])
            (run / "CHECKS.json").write_bytes(actual)
            shutil.rmtree(source)
            reports.append({"check": name, "mode": mode, "status": expected_status,
                            "seconds": round(time.monotonic() - start, 3),
                            "receipt_sha256": sha(actual), "equal_frozen_bytes": True})
            print("PASS", name, mode, flush=True)
    require(verify_sources() == entries, "Source manifest changed")
    receipt = {"status": "PASS_COMMON_COVER_TERMINAL_ANNEX", "checks": reports,
               "source_count": len(entries), "sources_unchanged": True,
               "python": platform.python_version(), "platform": platform.platform(),
               "source_manifest_sha256": sha((ROOT / "SOURCES.json").read_bytes()),
               "runner_sha256": sha(Path(__file__).read_bytes()),
               "scope": "Exact common-cover terminal and finite controls for its standalone rank theorem. No complete path, owner, map-price, recursive, or precision replay."}
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
