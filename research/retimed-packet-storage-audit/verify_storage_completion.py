#!/usr/bin/env python3
"""Replay the ordinary byte join and binary capacity antecedent in one budget."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def snapshot():
    return {p.relative_to(HERE).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in HERE.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    before = snapshot()
    started = time.monotonic()
    for label, driver, limit in (("ordinary", "verify_ordinary.py", 120),
                                 ("binary", "verify_binary.py", 240)):
        remaining = 280 - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError("storage completion replay budget exhausted")
        subprocess.run([sys.executable, "-B", str(HERE / driver), "--output", str(output / label)],
                       check=True, timeout=min(limit, remaining))
    if snapshot() != before:
        raise ValueError("storage completion replay changed frozen package files")
    receipt = {"status": "PASS_RETIMED_COMPLETE_ORDINARY_AND_BINARY_STORAGE",
               "seconds": round(time.monotonic() - started, 3),
               "package_files_unchanged": len(before),
               "scope": "Ordinary historical data-file bound with local binary capacity derived; physical, custody and outer contracts retained"}
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    main()
