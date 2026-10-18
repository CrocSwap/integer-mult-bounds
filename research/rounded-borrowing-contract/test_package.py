#!/usr/bin/env python3
"""Run the checker from a read-only copy and check command failures."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def command(root, extra=()):
    env = dict(os.environ)
    env.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py"), *extra],
                          cwd=root.parent, env=env, text=True, capture_output=True,
                          timeout=180)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write validation metadata to a new path")
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError("validation path already exists")
    started = time.monotonic()
    controls = []
    with tempfile.TemporaryDirectory(prefix="rounded borrowing checks ") as temporary:
        folder = Path(temporary)
        relocated = folder / "read only package"
        shutil.copytree(ROOT, relocated, ignore=shutil.ignore_patterns("__pycache__"))
        try:
            for path in relocated.rglob("*"):
                path.chmod(0o555 if path.is_dir() else 0o444)
            relocated.chmod(0o555)
            receipt = folder / "fresh receipt.json"
            result = command(relocated, ("--output", str(receipt)))
            need(result.returncode == 0, "relocated command failed: " + result.stderr)
            need(json.loads(receipt.read_text()) == json.loads((ROOT / "EXPECTED.json").read_text()),
                 "relocated receipt differs")
            print(result.stdout, end="")
        finally:
            relocated.chmod(0o755)
            for path in relocated.rglob("*"):
                path.chmod(0o755 if path.is_dir() else 0o644)

        bad_source = folder / "changed source"
        shutil.copytree(ROOT, bad_source, ignore=shutil.ignore_patterns("__pycache__"))
        source = bad_source / "vendor/pr1057/borrow.py"
        source.write_bytes(source.read_bytes() + b"\n# Source fault for the command control.\n")
        result = command(bad_source)
        need(result.returncode != 0 and "source digest mismatch" in result.stderr,
             "changed source was not rejected by its digest guard")
        controls.append("changed_pinned_source_rejected")

        bad_residue = folder / "discarded residue"
        shutil.copytree(ROOT, bad_residue, ignore=shutil.ignore_patterns("__pycache__"))
        owner = bad_residue / "contracts.py"
        text = owner.read_text()
        original = "return nearest(residue + p * shift, q) - nearest(residue, q)"
        need(text.count(original) == 1, "residue mutation target is not unique")
        owner.write_text(text.replace(original, "return nearest(p * shift, q)"))
        result = command(bad_residue)
        need(result.returncode != 0 and "saved residue response failed" in result.stderr,
             "discarded residue did not fail at the response contract")
        controls.append("discarded_residue_rejected_at_response_contract")

        occupied = folder / "occupied receipt.json"
        original_bytes = b"keep this existing receipt\n"
        occupied.write_bytes(original_bytes)
        result = command(ROOT, ("--output", str(occupied)))
        need(result.returncode != 0 and "receipt path already exists" in result.stderr,
             "occupied output was not rejected")
        need(occupied.read_bytes() == original_bytes, "occupied output was changed")
        controls.append("occupied_output_rejected_without_change")

    metadata = {"status": "PASS", "command_controls": controls,
                "relocated_read_only_optimized_python": True,
                "python": sys.version, "seconds": round(time.monotonic() - started, 6)}
    if args.output:
        with args.output.open("x") as stream:
            json.dump(metadata, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(f"PASS_ROUNDED_BORROWING_PACKAGE controls={len(controls)} relocation=1")


if __name__ == "__main__":
    main()
