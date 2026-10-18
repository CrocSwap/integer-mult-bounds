#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build the core-only Lean count lemma and reject four false variants."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def invoke(executable, filename):
    return subprocess.run([executable, "-j1", "-DwarningAsError=true", str(filename)],
                          capture_output=True, text=True, timeout=60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", default=shutil.which("lean"))
    args = parser.parse_args()
    if not args.lean:
        raise SystemExit("Lean 4.21.0 required; pass --lean PATH (no automatic installation)")
    version = subprocess.check_output([args.lean, "--version"], text=True, timeout=60).strip()
    if not version.startswith("Lean (version 4.21.0,"):
        raise SystemExit("Expected Lean 4.21.0, got " + version)
    result = invoke(args.lean, HERE / "CountFloor.lean")
    if result.returncode or "sorryAx" in result.stdout + result.stderr:
        raise SystemExit(result.stdout + result.stderr)
    for name in ("floor_of_counts", "rank_four_floor", "floor_of_term_prices"):
        expected = f"'P112CrossForm.{name}' depends on axioms: [propext, Quot.sound]"
        if expected not in result.stdout:
            raise SystemExit("Unexpected axiom audit: " + result.stdout)
    # Each missing-hypothesis variant is false, with a concrete witness in
    # CountFloor.lean. A failed proof here is a compiler control, not its proof.
    controls = [
        "example : 128 ≤ 64 := by decide\n",
        "example : 128 ≤ 0 := by decide\n",
        "example : (8 : Nat) * 8 ≥ 128 := by omega\n",
        "example : (7 : Nat) * 16 ≥ 128 := by omega\n",
    ]
    with tempfile.TemporaryDirectory(prefix="p112-count-controls-") as directory:
        for i, content in enumerate(controls):
            path = Path(directory) / f"False{i}.lean"
            path.write_text("import Lean\n" + content)
            failed = invoke(args.lean, path)
            if failed.returncode == 0 or "error:" not in failed.stdout:
                raise SystemExit("False theorem accepted or wrong failure: " + failed.stdout + failed.stderr)
    print(version)
    print(result.stdout.strip())
    print("PASS_LEAN_P112_COUNT_FLOOR theorems=3 concrete_counterexamples=4 rejected_proofs=4")


if __name__ == "__main__":
    main()
