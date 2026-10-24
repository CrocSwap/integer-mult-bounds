#!/usr/bin/env python3
"""Replay the two unchanged rank checks in separate local copies."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


LANES = Path("work/centre-encoding-campaign-20261014/lanes")
JOBS = (
    ("pure-cycle", LANES / "bridge-review-20261017/pure-cycle-rank-review-20261018",
     "check_review.py", "REVIEW.json", "PASS_INDEPENDENT_PURE_CYCLE_RANK_BINDING"),
    ("rank9", LANES / "bridge-review-20261017/rank9-completion-review-20261020",
     "check_rank9.py", "CHECKS.json", "PASS_INDEPENDENT_RANK9_COMPLETION"),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    out = parser.parse_args().out.resolve()
    root = Path(__file__).resolve().parent
    need(not out.exists(), "Use a new output directory")
    need(out.parent.is_dir(), "The output parent directory must exist")
    need(root != out and root not in out.parents, "Output must be outside the annex")
    need(shutil.disk_usage(out.parent).free >= 3 * 2**30, "At least 3 GiB must be free")
    manifest_path = root / "ANNEX-MANIFEST.json"
    manifest_bytes = manifest_path.read_bytes()
    entries = json.loads(manifest_bytes)["files"]

    def verify_annex():
        actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
        need(actual == {e["path"] for e in entries} | {"ANNEX-MANIFEST.json"},
             "Annex file set differs from the manifest")
        for entry in entries:
            need(digest(root / entry["path"]) == entry["sha256"],
                 "Annex file changed: " + entry["path"])
        need(manifest_path.read_bytes() == manifest_bytes, "Annex manifest changed")

    verify_annex()
    sources = json.loads((root / "SOURCES.json").read_bytes())["files"]
    out.mkdir()
    reports = []
    for name, relative, checker, receipt_name, status in JOBS:
        for mode in ("normal", "optimized"):
            run = out / name / mode
            source = run / "source"
            shutil.copytree(root / "frozen", source)
            (source / relative / receipt_name).unlink()
            command = [sys.executable, "-I", "-B"]
            if mode == "optimized":
                command.append("-O")
            command.append(str(source / relative / checker))
            print("RUN", name, mode, flush=True)
            started = time.monotonic()
            with (run / "stdout.txt").open("w", encoding="utf-8") as log:
                result = subprocess.run(command, cwd=source, stdout=log,
                                        stderr=subprocess.STDOUT, check=False)
            need(result.returncode == 0, "Check failed: " + str(run / "stdout.txt"))
            actual = (source / relative / receipt_name).read_bytes()
            expected = (root / "frozen" / relative / receipt_name).read_bytes()
            need(actual == expected, "Complete receipt differs from its frozen bytes")
            need(json.loads(actual)["status"] == status, "Unexpected check status")
            if mode == "optimized":
                need(actual == (out / name / "normal" / receipt_name).read_bytes(),
                     "Normal and optimized receipts differ")
            for entry in sources:
                path = Path(entry["path"])
                if path.parts[0] == "frozen":
                    need(digest(source / path.relative_to("frozen")) == entry["sha256"],
                         "Runtime source changed: " + str(path))
            (run / receipt_name).write_bytes(actual)
            shutil.rmtree(source)
            reports.append({"check": name, "mode": mode, "status": status,
                            "receipt_sha256": sha256(actual).hexdigest(),
                            "complete_frozen_receipt_match": True,
                            "seconds": round(time.monotonic() - started, 6)})
            print("PASS", name, mode, flush=True)
    verify_annex()
    result = {"status": "PASS_ORDERED_RANK_COMPLETIONS_ANNEX", "checks": reports,
              "annex_manifest_sha256": sha256(manifest_bytes).hexdigest(),
              "source_manifest_sha256": digest(root / "SOURCES.json"),
              "sources_unchanged": True, "sequential_checks": True,
              "python": platform.python_version(), "source_files": len(sources),
              "scope": "Restricted pure-cycle rank bound and exact one-field rank-nine contraction",
              "kappa_improvement": False,
              "not_run": ["Producer dependency suites", "Recursive child implementations",
                          "Full-cover finite map prices", "Finite precision and recursive hosting",
                          "Complete supplier or kappa calculation"]}
    (out / "REPLAY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    main()
