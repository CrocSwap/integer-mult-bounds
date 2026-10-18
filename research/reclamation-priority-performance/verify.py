"""One-command reproduction of the scoped priority-index contribution."""

import argparse
from pathlib import Path
import subprocess
import sys

from adapter import HERE, require, verify_sources


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=1)
    args = parser.parse_args()
    verify_sources()
    require(1 <= args.rounds <= 7, "Use one through seven rounds")
    require(not args.out.exists(), "Output must be a fresh directory")
    args.out.mkdir(parents=True)
    commands = [[sys.executable, "-B", str(HERE / "test_priority.py")]]
    for h in (23, 25):
        commands.append([sys.executable, "-B", str(HERE / "audit_index.py"),
                         "--h", str(h), "--out", str(args.out / f"audit-{h}")])
    commands.append([sys.executable, "-B", str(HERE / "benchmark.py"),
                     "--rounds", str(args.rounds), "--out", str(args.out / "benchmark")])
    for command in commands:
        subprocess.run(command, check=True)
    print("PASS_RECLAMATION_PRIORITY", flush=True)
