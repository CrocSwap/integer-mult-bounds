#!/usr/bin/env python3
"""Replay the fixed-baseline spectral bound in a new output directory."""

from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve().parent
CAMPAIGN = Path("work/centre-encoding-campaign-20261014")
MANIFEST = HERE / "SOURCE-MANIFEST.json"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_inputs():
    records = json.loads(MANIFEST.read_text())["files"]
    for name, item in records.items():
        raw = (HERE / name).read_bytes()
        need(len(raw) == item["bytes"], "Source size: " + name)
        need(sha256(raw).hexdigest() == item["sha256"], "Source hash: " + name)
        if "decompressed_sha256" in item:
            need(sha256(gzip.decompress(raw)).hexdigest() == item["decompressed_sha256"],
                 "Source payload: " + name)
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--optimized", action="store_true")
    args = parser.parse_args()
    output = args.out.resolve()
    need(not output.exists(), "Use a new output directory")
    need(not output.is_relative_to(HERE), "Keep output outside the annex")
    output.parent.mkdir(parents=True, exist_ok=True)
    need(shutil.disk_usage(output.parent).free >= 3 * 1024**3 + 10 * 1024**2,
         "Keep at least 3 GiB free during replay")
    count = check_inputs()
    output.mkdir()
    started = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    report = {"schema": "fixed-baseline-spectral-replay-v1", "source_files": count,
              "source_manifest_sha256": sha256(MANIFEST.read_bytes()).hexdigest(),
              "replay_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "python": sys.version, "platform": platform.platform(),
              "optimized_reviewer": args.optimized, "stages": []}
    with tempfile.TemporaryDirectory(prefix="spectral-gap-", dir=output) as temporary:
        workspace = Path(temporary) / "workspace"
        shutil.copytree(HERE / "frozen", workspace)
        lanes = workspace / CAMPAIGN / "lanes"
        shutil.copyfile(HERE / "portable/review_spectral_bound.py",
                        lanes / "temporal-reuse/review_spectral_bound.py")
        stages = [
            ("producer", "schur-selection/check_spectral_bound.py",
             "schur-selection/SPECTRAL-BOUND.json", False),
            ("independent", "temporal-reuse/review_spectral_bound.py",
             "temporal-reuse/SPECTRAL-BOUND-REVIEW.json", args.optimized),
        ]
        for name, script, receipt, optimized in stages:
            need(shutil.disk_usage(output).free >= 3 * 1024**3, "Disk reserve")
            command = [sys.executable, "-I", "-B"]
            if optimized:
                command.append("-O")
            command.append(str(lanes / script))
            tick = time.monotonic()
            print("RUN " + name, flush=True)
            with (output / (name + ".log")).open("w") as stream:
                process = subprocess.run(command, cwd=workspace, env=env, stdout=stream,
                                         stderr=subprocess.STDOUT, check=False)
            need(process.returncode == 0, "Read " + str(output / (name + ".log")))
            actual = (lanes / receipt).read_bytes()
            expected = (HERE / "frozen" / CAMPAIGN / "lanes" / receipt).read_bytes()
            need(actual == expected, "Historical receipt bytes differ: " + name)
            result = json.loads(actual)
            (output / (name + ".json")).write_bytes(actual)
            report["stages"].append({"name": name, "status": result["status"],
                "command": command, "python_optimized": optimized,
                "receipt_bytes_equal": True, "receipt_sha256": sha256(actual).hexdigest(),
                "seconds": time.monotonic() - tick})
            print(result["status"], flush=True)
    check_inputs()
    report.update(status="PASS_FIXED_BASELINE_SPECTRAL_GAP", frozen_inputs_unchanged=True,
                  producer_assertions_enabled=True, seconds=time.monotonic() - started,
                  scope="Fixed A,T and retained selected baselines. Size27 remains open. No global minimum or kappa change.",
                  source_access="Two exact compressed archive members and their decoded payloads; no Git, network, or full archive access.")
    (output / "REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"], flush=True)


if __name__ == "__main__":
    main()
