"""Replay source-intake behavior and the focused overlap regression suite.

Produced by Nick Petalas. Apache-2.0.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Write fresh evidence; refuse overwrite")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    command = [sys.executable, "-I", "-W", "error", "-B"]
    if sys.flags.optimize:
        command.append("-O")
    command.extend(["-m", "unittest", "discover", "-s", "tests",
                    "-p", "test_research_overlap_*.py", "-q"])
    started = time.perf_counter()
    result = subprocess.run(command, cwd=root, text=True, capture_output=True,
                            timeout=90, check=True)
    elapsed = time.perf_counter() - started
    print(result.stdout + result.stderr, end="")
    if args.write is not None:
        inputs = ["scripts/find_overlap.py", "scripts/research_package.py",
                  *sorted(str(path.relative_to(root)) for path in
                          (root / "tests").glob("test_research_overlap_*.py"))]
        evidence = {"claim_type": "workflow tooling with behavioral regression evidence",
                    "created_utc": datetime.now(timezone.utc).isoformat(),
                    "python": sys.version, "platform": platform.platform(),
                    "command": command, "seconds": elapsed, "exit_code": result.returncode,
                    "output": result.stdout + result.stderr,
                    "sha256": {name: sha256((root / name).read_bytes()).hexdigest() for name in inputs}}
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print("PASS_SOURCE_REFERENCE_INTAKE")


if __name__ == "__main__":
    main()
