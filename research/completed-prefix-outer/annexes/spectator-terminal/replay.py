#!/usr/bin/env python3
"""Run the two frozen spectator terminal checks in private source copies."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve().parent
JOBS = [
    ("kernel", "lanes/coherent-port/check_spectator_terminal_product.py",
     "lanes/coherent-port/SPECTATOR-TERMINAL-PRODUCT.json",
     "PASS_SPECTATOR_TERMINAL_PRODUCT"),
    ("order", "lanes/schur-selection/spectator/review_terminal_product.py",
     "lanes/schur-selection/spectator/TERMINAL-PRODUCT-REVIEW.json",
     "PASS_INDEPENDENT_TERMINAL_PRODUCT_ORDER"),
]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        raw = (HERE / item["path"]).read_bytes()
        need(len(raw) == item["bytes"] and digest(raw) == item["sha256"],
             "Frozen source differs: " + item["path"])
    return manifest


def run_one(job, optimized, output):
    label, script, receipt, status = job
    mode = "optimized" if optimized else "normal"
    destination = output / mode / label
    destination.mkdir(parents=True)
    expected = (HERE / "frozen" / receipt).read_bytes()
    with tempfile.TemporaryDirectory(prefix="spectator-", dir=output) as temporary:
        workspace = Path(temporary) / "source"
        shutil.copytree(HERE / "frozen", workspace)
        result_path = workspace / receipt
        result_path.unlink()
        command = [sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
        command.append(str(workspace / script))
        environment = dict(os.environ)
        environment.update({name: "1" for name in [
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"]})
        started = time.monotonic()
        result = subprocess.run(command, cwd=workspace, env=environment,
                                capture_output=True, text=True, check=False)
        (destination / "stdout.txt").write_text(result.stdout + result.stderr)
        need(result.returncode == 0, label + " failed; see " + str(destination / "stdout.txt"))
        need(result_path.is_file(), label + " did not produce a new receipt")
        raw = result_path.read_bytes()
        need(raw == expected, label + " receipt differs from the frozen receipt")
        need(json.loads(raw)["status"] == status, label + " status differs")
        (destination / result_path.name).write_bytes(raw)
        return {"id": label, "mode": mode, "status": status,
                "seconds": round(time.monotonic() - started, 3),
                "fresh_receipt_created": True,
                "frozen_receipt_byte_equal": True, "receipt_sha256": digest(raw)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    output = args.out.resolve()
    need(not output.is_relative_to(HERE), "Output must be outside the annex")
    need(not output.exists(), "Output directory must not exist")
    need(shutil.disk_usage(output.parent).free >= 3 * 1024 ** 3, "Keep at least 3 GiB free")
    sources = verify_sources()
    output.mkdir()
    results = []
    for optimized in (False, True):
        for job in JOBS:
            print(("optimized" if optimized else "normal") + " " + job[0], flush=True)
            results.append(run_one(job, optimized, output))
    normal = {item["id"]: item["receipt_sha256"] for item in results if item["mode"] == "normal"}
    need(all(item["receipt_sha256"] == normal[item["id"]] for item in results), "Mode receipts differ")
    verify_sources()
    receipt = {
        "status": "PASS_SPECTATOR_TERMINAL_ANNEX",
        "source_files": len(sources["files"]),
        "source_manifest_sha256": digest((HERE / "SOURCES.json").read_bytes()),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "python": sys.version,
        "jobs": results,
        "normal_optimized_equal": True,
        "frozen_sources_unchanged": True,
        "scope": "Exact terminal kernels and independent formal product order. Complete portwise layer endpoints, native gather admission, the controller witness, full costs, precision, and recursive admission are not established by this replay."
    }
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    main()
