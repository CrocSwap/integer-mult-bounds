#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One fresh discovery process, inside the externally verified whole-job cgroup.

Per-process limits below are defense in depth; aggregate enforcement belongs
to the cgroup containing THIS supervisor, gate, compiler and all descendants.
"""
import time
START = time.monotonic()
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--freeze-sha", required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir()
    resource.setrlimit(resource.RLIMIT_AS, (64 * 2**20, 2**30))
    record = {"started_utc": datetime.now(timezone.utc).isoformat(),
              "total_wall_limit_seconds": 120, "total_cpu_limit_seconds": 120,
              "total_memory_limit_bytes": 2**30, "case_runs_requested": 1}
    child = None
    try:
        frozen_bytes = (ROOT / "FREEZE.json").read_bytes()
        if sha256(frozen_bytes).hexdigest() != args.freeze_sha:
            raise ValueError("externally pinned frozen digest")
        frozen = json.loads(frozen_bytes)
        for item in frozen["files"]:
            raw = (ROOT / item["path"]).read_bytes()
            if (len(raw), sha256(raw).hexdigest()) != (item["bytes"], item["sha256"]):
                raise ValueError("frozen input mismatch: " + item["path"])
        record["freeze_sha256"] = sha256((ROOT / "FREEZE.json").read_bytes()).hexdigest()

        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (960 * 2**20, 960 * 2**20))
            resource.setrlimit(resource.RLIMIT_CPU, (118, 119))
            resource.setrlimit(resource.RLIMIT_STACK, (32 * 2**20, 32 * 2**20))

        with (output / "STDOUT.txt").open("x") as out, (output / "STDERR.txt").open("x") as err:
            child = subprocess.Popen([sys.executable, "-I", "-B", str(ROOT / "gate.py"), "--out", str(output),
                                      "--freeze-sha", args.freeze_sha],
                stdout=out, stderr=err, cwd=ROOT, preexec_fn=limits, start_new_session=True)
            try:
                child.wait(timeout=max(.01, 119 - (time.monotonic() - START)))
            except subprocess.TimeoutExpired:
                record["supervisor_timeout"] = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=.25)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=.25)
            record["returncode"] = child.returncode
    except BaseException as error:
        record["supervisor_error"] = repr(error)
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=.25)
    finally:
        own, kids = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
        gate = json.loads((output / "RECEIPT.json").read_text()) if (output / "RECEIPT.json").exists() else {}
        if not gate:
            (output / "INCOMPLETE.json").write_text(json.dumps({"coverage":"unknown","nominee_admissible":False})+"\n")
        total_cpu = own.ru_utime+own.ru_stime+kids.ru_utime+kids.ru_stime
        total_rss = own.ru_maxrss + gate.get("conservative_sum_peak_rss_KiB", kids.ru_maxrss)
        record.update(elapsed_wall_seconds=time.monotonic()-START, combined_cpu_seconds=total_cpu,
                      conservative_sum_peak_rss_KiB=total_rss, child_gate_receipt=gate,
                      finished_utc=datetime.now(timezone.utc).isoformat())
        record["within_declared_budget"] = record["elapsed_wall_seconds"] <= 120 and total_cpu <= 120 and total_rss * 1024 <= 2**30
        record["nominee_available_for_assessment"] = (record.get("returncode") == 0 and
            record["within_declared_budget"] and (output / "NOMINEE.json").exists())
        (output / "RESOURCE.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(json.dumps(record, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
