"""Replay the four frozen full-W component reviews in a private directory."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
LANES = Path("work/centre-encoding-campaign-20261014/lanes")
DIRTY = LANES / "portable-source-codes/dirty-record-hosting-20261015"
PHYSICAL = LANES / "residual-syndrome/physical-algebra"
JOBS = (
    ("composition", DIRTY / "algebra/composition-review/check_composition.py",
     DIRTY / "algebra/composition-review/CHECK.json", False),
    ("donors", LANES / "source-domain/two-cut-donor-review/review_donors.py",
     LANES / "source-domain/two-cut-donor-review/REVIEW.json", True),
    ("cleanup", PHYSICAL / "review-gauss/delayed-dirty-cleanup/check_review.py",
     PHYSICAL / "review-gauss/delayed-dirty-cleanup/CHECK.json", False),
    ("all-output", PHYSICAL / "review-gauss/all-output-dirt/check_review.py",
     PHYSICAL / "review-gauss/all-output-dirt/CHECK.json", False),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sources(manifest):
    for row in manifest["files"]:
        path = HERE / row["path"]
        if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            raise ValueError("Frozen source mismatch: " + row["path"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise ValueError("Use a new output directory")
    if HERE == out or HERE in out.parents:
        raise ValueError("Keep replay output outside the annex")
    if shutil.disk_usage(out.parent).free < 3 * 1024 ** 3:
        raise ValueError("At least three GiB of free space are required")
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    adaptation = json.loads((HERE / "ADAPTATIONS.json").read_text())["changes"][0]
    check_sources(manifest)
    if digest(HERE / adaptation["portable"]) != adaptation["portable_sha256"]:
        raise ValueError("Portable checker mismatch")
    out.mkdir()
    env = dict(os.environ)
    env.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               VECLIB_MAXIMUM_THREADS="1", MKL_NUM_THREADS="1")
    records = []
    for name, script, receipt, explicit_output in JOBS:
        stage = out / name
        shutil.copytree(HERE / "frozen", stage)
        if name == "composition":
            shutil.copyfile(HERE / adaptation["portable"], stage / script)
        command = [sys.executable, "-I", "-O", "-B", str(stage / script)]
        if explicit_output:
            command.extend(["--out", str(stage / receipt)])
        started = time.monotonic()
        with (out / (name + ".log")).open("w") as log:
            process = subprocess.run(command, cwd=stage, env=env,
                                     stdout=log, stderr=subprocess.STDOUT)
        if process.returncode:
            raise RuntimeError(name + " failed; read " + str(out / (name + ".log")))
        expected = HERE / "frozen" / receipt
        actual = stage / receipt
        if actual.read_bytes() != expected.read_bytes():
            raise ValueError(name + " receipt differs from the frozen receipt")
        shutil.copyfile(actual, out / (name + "-CHECK.json"))
        records.append({"name": name, "command": command,
                        "receipt_sha256": digest(actual),
                        "status": json.loads(actual.read_text())["status"],
                        "byte_identical_to_frozen_receipt": True,
                        "elapsed_seconds": round(time.monotonic() - started, 3)})
        check_sources(manifest)
        print("PASS_FULL_W_" + name.upper().replace("-", "_"), flush=True)
    result = {"status": "PASS_FULL_W_COMPONENT_ANNEX",
              "source_manifest_sha256": digest(HERE / "SOURCES.json"),
              "adaptations_sha256": digest(HERE / "ADAPTATIONS.json"),
              "source_files_unchanged": True,
              "checks": records,
              "scope": "Four component reviews; no complete supplier or kappa claim."}
    (out / "REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
