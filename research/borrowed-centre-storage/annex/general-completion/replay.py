#!/usr/bin/env python3
"""Replay the unchanged general-completion checker from local inputs."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    out = args.out.resolve()
    need(not out.exists(), "Output directory must not exist")
    need(out.parent.is_dir(), "Output parent directory must exist")
    need(root != out and root not in out.parents, "Output must be outside the annex")
    need(shutil.disk_usage(out.parent).free >= 3 * 1024**3, "At least 3 GiB must be free")
    manifest_path = root / "MANIFEST.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)

    def check_files():
        actual_paths = {str(path.relative_to(root)) for path in root.rglob("*")
                        if path.is_file()}
        need(actual_paths == set(manifest["files"]) | {"MANIFEST.json"},
             "Annex file set differs from the manifest")
        for relative, expected in manifest["files"].items():
            need(sha256((root / relative).read_bytes()).hexdigest() == expected,
                 "Annex file hash: " + relative)

    check_files()
    out.mkdir()
    review = (root / "frozen/work/centre-encoding-campaign-20261014/lanes"
              / "paired-package-review/upstream-followthrough-20261015/general-completion-review")
    command = [sys.executable, "-I", "-O", "-B", str(review / "check_extension.py"),
               "--repo", str(root / "frozen"), "--out", str(out)]
    started = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    (out / "checker.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (out / "checker.stderr.txt").write_text(result.stderr, encoding="utf-8")
    need(result.returncode == 0, "General completion checker failed; read the output logs")
    actual = (out / "CHECK.json").read_bytes()
    expected = (review / "CHECK.json").read_bytes()
    need(actual == expected, "Complete checker receipt differs from the frozen receipt")
    need(json.loads(actual)["status"] == "PASS_GENERAL_COMPLETION_EXTENSION",
         "Unexpected checker status")
    check_files()
    receipt = {
        "status": "PASS_BORROWED_CENTRE_GENERAL_COMPLETION_ANNEX",
        "command": command,
        "manifest_sha256": sha256(manifest_bytes).hexdigest(),
        "annex_files_checked": len(manifest["files"]),
        "checker_receipt_sha256": sha256(actual).hexdigest(),
        "complete_receipt_byte_match": True,
        "source_bytes_unchanged_after_run": True,
        "seconds": round(time.monotonic() - started, 6),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "execution": "One unchanged independent checker; Python standard library",
        "scope": "Algebraic completion and changed-output fields; no native-child bound",
        "checks_not_run": ["Native kernels or physical words", "Global controller",
                           "Finite precision and recursive storage", "Complete supplier invoice"],
        "kappa_improvement": False,
    }
    (out / "REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")
    print(receipt["status"])


if __name__ == "__main__":
    main()
