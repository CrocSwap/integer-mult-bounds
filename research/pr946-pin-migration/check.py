#!/usr/bin/env python3
"""One-command inventory, adversarial controls and full historical replay."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    if sys.flags.optimize:
        raise SystemExit("Full historical replay requires assertion-enabled Python")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch-parent", type=Path, default=Path.cwd(),
                        help="Existing writable parent for disposable closures (default: current directory)")
    parser.add_argument("--check-proposal", action="store_true",
                        help="Also compare fetched PR946 Git blobs with the 165-file frozen inventory")
    args = parser.parse_args()
    for flags in ([], ["-O"]):
        subprocess.run([sys.executable, "-I", "-B", *flags, str(HERE / "test_inventory.py")], check=True)
    subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"),
                    *(["--check-proposal"] if args.check_proposal else [])], check=True)
    run = subprocess.run([sys.executable, "-I", "-B", str(HERE / "replay.py"),
                          "--scratch-parent", str(args.scratch_parent.resolve())],
                         check=True, capture_output=True, text=True, encoding="utf-8")
    replay = json.loads(run.stdout)
    if replay["status"] != "PASS_PR946_PIN_MIGRATION_REPLAY":
        raise ValueError("Unexpected replay status")
    if run.stderr:
        print(run.stderr, end="", file=sys.stderr)
    print("PASS_PR946_PIN_MIGRATION json_files=10707 proposal_files=165 "
          "old_references=561 single_file_rejections=8 full_audits=2 "
          "coefficients_per_audit=6760000 kappa=unchanged")


if __name__ == "__main__":
    main()
