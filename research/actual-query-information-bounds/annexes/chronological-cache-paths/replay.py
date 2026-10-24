"""Replay one support appendix in fresh source copies."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    config = json.loads((package/"TASK.json").read_text())
    manifest = json.loads((package/"SOURCES.json").read_text())

    def verify():
        for rel, record in manifest["frozen_files"].items():
            path = package/"frozen"/rel
            if digest(path) != record["sha256"] or path.stat().st_size != record["bytes"]:
                raise ValueError("Frozen source differs: "+rel)

    verify()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    runs = []
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
    for mode in ("normal", "optimized"):
        workspace = output/mode
        shutil.copytree(package/"frozen", workspace)
        (workspace/"results").mkdir(exist_ok=True)
        script = (package if config["location"] == "package" else workspace)/config["script"]
        command = [sys.executable, "-I", "-B"]
        if mode == "optimized":
            command.append("-O")
        command.append(str(script))
        command.extend(v.format(workspace=str(workspace)) for v in config["arguments"])
        start = time.monotonic()
        result = subprocess.run(command, cwd=workspace, env=env,
                                capture_output=True, text=True)
        (output/(mode+".log")).write_text(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError("Child failed: "+mode)
        receipt = workspace/config["receipt"]
        if receipt.read_bytes() != (package/config["expected"]).read_bytes():
            raise ValueError("Receipt bytes differ: "+mode)
        runs.append({"mode": mode, "command": command, "exit_code": 0,
                     "receipt_sha256": digest(receipt),
                     "elapsed_seconds": round(time.monotonic()-start, 3)})
        print("PASS", mode, config["id"], flush=True)
    verify()
    receipt = {"status": "PASS_SCOPED_SUPPORT_PROOF_REPLAY", "appendix": config["id"],
               "runs": runs, "source_manifest_sha256": digest(package/"SOURCES.json"),
               "runner_sha256": digest(Path(__file__)),
               "comparison": "Both complete receipt files match exact bytes.",
               "scope": config["scope"]}
    (output/"REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
