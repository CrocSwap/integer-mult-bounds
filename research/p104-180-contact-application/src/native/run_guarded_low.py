#!/usr/bin/env python3
"""Arm a scoped low-family run and retain its ledger gate and resource receipts."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time

from build_low import C_RAW, SOURCE_RAW, require, sha, write_json


HERE = Path(__file__).resolve().parent
CLAIM = "https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19698656"
RUNNERS = {"core": "build_low.py", "native": "verify_low_native.py"}
EVENTS = {"core": "p7636-180-lowering-core-running", "native": "p7636-180-lowering-native-running"}
ADDRESS_LIMIT = 2_684_354_560


def now():
    return datetime.now(timezone.utc).isoformat()


def file_hash(path):
    return sha(path.read_bytes()) if path.is_file() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=RUNNERS)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--materialized", type=Path)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--wall", type=int, required=True)
    args = parser.parse_args()
    require(0 < args.wall <= 1200 and args.cpu in os.sched_getaffinity(0), "invalid resource limit")
    require(args.stage == "core" or args.materialized is not None, "native needs the built matched pair")
    require(not args.authorization.exists() and not args.out.exists(), "run requires fresh gate and output paths")
    args.log.mkdir(exist_ok=False)
    runner = HERE / RUNNERS[args.stage]
    command = ["/usr/bin/time", "-v", "-o", str(args.log / "time.txt"), "timeout", "-k", "8s", f"{args.wall}s",
               "prlimit", f"--as={ADDRESS_LIMIT}", f"--cpu={args.wall}", "taskset", "-c", str(args.cpu),
               "python3.12", "-B", str(runner), "--inputs", str(args.inputs), "--out", str(args.out),
               "--authorization", str(args.authorization)]
    if args.materialized is not None:
        command += ["--materialized", str(args.materialized)]
    files = [runner, HERE / "build_low.py", *sorted((HERE / "engines").glob("*.py"))]
    code = {str(path.relative_to(HERE)): file_hash(path) for path in files}
    write_json(args.log / "START.json", {"stage": args.stage, "armed_at": now(), "public_claim": CLAIM,
               "source_raw_sha256": SOURCE_RAW, "raw_combined_sha256": C_RAW, "expected_event": EVENTS[args.stage],
               "wall_limit_seconds": args.wall, "address_space_bytes": ADDRESS_LIMIT, "cpu_affinity": [args.cpu],
               "code": code, "entrypoint": RUNNERS[args.stage], "argv": command})
    deadline = time.monotonic() + 240
    while not args.authorization.is_file():
        if time.monotonic() >= deadline:
            write_json(args.log / "launch.json", {"stage": args.stage, "exit": 124, "ended_at": now(),
                       "disposition": "ledger authorization wait expired before execution"})
            return 124
        time.sleep(0.2)
    auth = json.loads(args.authorization.read_bytes())
    require(auth.get("source_raw_sha256") == SOURCE_RAW and auth.get("raw_combined_sha256") == C_RAW
            and auth.get("public_claim") == CLAIM and auth.get("running_event") == EVENTS[args.stage]
            and auth.get("receipt_id"), "ledger gate scope or receipt")
    require(all(file_hash(HERE / path) == value for path, value in code.items()), "code changed while armed")
    started = now()
    with (args.log / "stdout.txt").open("xb") as out, (args.log / "stderr.txt").open("xb") as err:
        completed = subprocess.run(command, stdout=out, stderr=err, check=False)
    require(all(file_hash(HERE / path) == value for path, value in code.items()), "code changed while running")
    result_name = "BINDING.json" if args.stage == "core" else "RESULT.json"
    result_path = args.out / result_name
    result = json.loads(result_path.read_bytes()) if completed.returncode == 0 else {}
    record = {"stage": args.stage, "run_id": EVENTS[args.stage], "exit": completed.returncode,
              "started_at": started, "ended_at": now(), "source_raw_sha256": SOURCE_RAW,
              "running_event": auth["running_event"], "receipt_id": auth["receipt_id"],
              "authorization_sha256": file_hash(args.authorization), "launcher_sha256": file_hash(Path(__file__)),
              "adapter_sha256": file_hash(runner), "physical_sha256": file_hash(HERE / "engines/physical.py"),
              "walsh_sha256": file_hash(HERE / "engines/walsh.py"),
              "start_sha256": file_hash(args.log / "START.json"), "native_result_sha256": file_hash(result_path),
              "stdout_sha256": file_hash(args.log / "stdout.txt"), "stderr_sha256": file_hash(args.log / "stderr.txt"),
              "time_sha256": file_hash(args.log / "time.txt")}
    if result:
        record["candidate_raw_sha256"] = result["candidate"]["raw_sha256"]
        record["candidate_canonical_sha256"] = result["candidate"]["canonical_sha256"]
        record["status"] = result["status"]
    write_json(args.log / "launch.json", record)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
