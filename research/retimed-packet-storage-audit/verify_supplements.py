#!/usr/bin/env python3
"""Replay reviewed owner and byte supplements from the retained offline runtime."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ArithmeticError(why)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    source = HERE / "sources/pr8042"
    manifest = json.loads((HERE / "SOURCE-BINDINGS.json").read_text())
    need(manifest["commit"] == "dfd25d553a843a946ca0b94130a5ff8943e98fdd", "unexpected source commit")
    for name, pin in manifest["files"].items():
        path = Path(name)
        need(not path.is_absolute() and ".." not in path.parts, "invalid source path")
        data = (source / path).read_bytes()
        need(len(data) == pin["size"] and sha256(data).hexdigest() == pin["sha256"],
             "retained source changed: " + name)
    spec = spec_from_file_location("supplement_source_bootstrap", source / "bootstrap.py")
    bootstrap = module_from_spec(spec)
    spec.loader.exec_module(bootstrap)
    statuses = {}
    with TemporaryDirectory(prefix="supplement-replay-", dir=output) as scratch:
        scratch = Path(scratch)
        runtime = scratch / "runtime"
        runtime.mkdir()
        bootstrap.install(runtime)
        temp = scratch / "tmp"
        temp.mkdir()
        env = os.environ.copy()
        env["TMPDIR"] = str(temp)
        # The original byte driver writes in its own evidence directory. Run a
        # byte-identical temporary copy so committed evidence remains immutable.
        byte_work = scratch / "bytes"
        shutil.copytree(HERE / "bytes", byte_work, ignore=shutil.ignore_patterns("__pycache__"))
        jobs = [
            ("owner", [HERE / "census/verify_census.py", "--runtime", runtime,
                        "--output", output / "owner"], 240),
            ("owner-review", [HERE / "census/review/replay.py", "--runtime", runtime,
                               "--output", output / "owner-review"], 60),
            ("bytes", [byte_work / "verify.py", "--runtime", runtime], 180),
            ("byte-review", [HERE / "bytes/review/check.py", "--output", output / "byte-review.json"], 60),
        ]
        for label, argv, seconds in jobs:
            command = [sys.executable, "-B", *map(str, argv)]
            result = subprocess.run(command, check=True, capture_output=True, text=True,
                                    timeout=seconds, env=env)
            (output / (label + ".log")).write_text(result.stdout + result.stderr)
            print("PASS_SUPPLEMENT_" + label.upper().replace("-", "_"), flush=True)
        shutil.copytree(byte_work / "evidence", output / "bytes", dirs_exist_ok=True)
    paths = {"owner": output / "owner/RESULT.json",
             "owner-review": output / "owner-review/RESULT.json",
             "bytes": output / "bytes/RESULT.json", "byte-review": output / "byte-review.json"}
    expected = {"owner": "PASS_GAUSSIAN_OWNER_CENSUS",
                "owner-review": "PASS_INDEPENDENT_OWNER_CENSUS_REVIEW_CHECKS",
                "bytes": "PASS_RETIMED_LOCAL_BYTE_CENSUS",
                "byte-review": "PASS_INDEPENDENT_LOCAL_BYTE_REVIEW"}
    for label, path in paths.items():
        report = json.loads(path.read_text())
        need(report["status"] == expected[label], "unexpected supplement status: " + label)
        statuses[label] = {"status": report["status"], "sha256": sha256(path.read_bytes()).hexdigest()}
    report = {"status": "PASS_RETIMED_OWNER_AND_BYTE_SUPPLEMENTS",
              "source_commit": manifest["commit"], "seconds": time.monotonic() - started,
              "checks": statuses,
              "owner_proof_sha256": sha256((HERE / "census/OWNER-CENSUS.md").read_bytes()).hexdigest(),
              "byte_proof_sha256": sha256((HERE / "bytes/PROOF.md").read_bytes()).hexdigest(),
              "scope": "Source-local owner and byte theorems; universal mass, remaining-site/global tariff, control and movement obligations retained"}
    (output / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], flush=True)


if __name__ == "__main__":
    main()
