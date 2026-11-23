#!/usr/bin/env python3
"""Replay the complete ordinary data-byte join without modifying frozen receipts."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    records = []

    def run(label, argv, marker):
        remaining = 580 - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError("ordinary replay budget exhausted")
        completed = subprocess.run([sys.executable, *map(str, argv)],
                                   capture_output=True, text=True, check=True,
                                   timeout=min(120, remaining))
        (output / (label + ".log")).write_text(completed.stdout + completed.stderr)
        if marker not in completed.stdout:
            raise ValueError("missing successful marker for " + label)
        records.append({"label": label, "marker": marker})
        print("PASS_ORDINARY_" + label.upper().replace("-", "_"), flush=True)

    for label, flags in (("normal", ["-B"]), ("optimized", ["-O", "-B"])):
        run("composition-" + label,
            [*flags, HERE / "composition/check.py", "--output", output / ("composition-" + label + ".json")],
            "PASS_SOURCE_BOUND_ORDINARY_ANCESTOR_COMPOSITION")
        run("entry-history-" + label,
            [*flags, HERE / "composition/check_history.py", "--output", output / ("entry-history-" + label + ".json")],
            "PASS_NATIVE_ENTRY_HISTORY_BOUNDARY")
    local_hashes = []
    with TemporaryDirectory(prefix="ordinary-bytes-", dir=output) as temp:
        for label, flags in (("normal", ["-I", "-B"]), ("optimized", ["-I", "-O", "-B"])):
            work = Path(temp) / label
            shutil.copytree(HERE / "ordinary-local", work,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            run("local-" + label, [*flags, work / "check.py"], "PASS_UNIFORM_ORDINARY_LOCAL_BYTES")
            data = (work / "EVIDENCE.json").read_bytes()
            local_hashes.append(sha256(data).hexdigest())
            (output / ("local-" + label + ".json")).write_bytes(data)
            run("review-" + label,
                [*flags, HERE / "ordinary-local/review/check.py", "--package", HERE / "ordinary-local",
                 "--output", output / ("review-" + label + ".json")],
                "PASS_INDEPENDENT_ORDINARY_BYTE_ENVELOPES")
    if local_hashes[0] != local_hashes[1]:
        raise ValueError("ordinary author normal/optimized evidence differs")
    run("joined", ["-I", "-B", HERE / "check_joined.py", "--output", output / "joined.json"],
        "PASS_JOINED_ORDINARY_DATA_FILE_BOUND")
    receipt = {"status": "PASS_COMPLETE_ORDINARY_DATA_BYTE_JOIN", "commands": records,
               "local_normal_optimized_sha256": local_hashes[0],
               "seconds": round(time.monotonic() - started, 3),
               "scope": "Conditional source-bound ordinary data-file coefficient; frozen evidence unchanged"}
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    main()
