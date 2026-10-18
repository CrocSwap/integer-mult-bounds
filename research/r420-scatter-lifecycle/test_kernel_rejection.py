#!/usr/bin/env python3
"""Confirm that a missing lifecycle proof is rejected after Lean compilation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    package = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=package.parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists():
        raise ValueError("output directory must not already exist")
    changed = output / "package"
    changed.mkdir(parents=True)
    for source in [*package.glob("*.lean"), package / "check.py", package / "MANIFEST.json"]:
        shutil.copyfile(source, changed / source.name)
    source = changed / "R420ScatterLifecycle.lean"
    text = source.read_text()
    original = ":=\n  BitCopyScatter.runWindows_eq_clear_direct temp windows windows_nonempty windows_well_formed s"
    if text.count(original) != 1:
        raise ValueError("expected exactly one lifecycle proof to replace")
    source.write_text(text.replace(original, ":= by sorry"))
    manifest_path = changed / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["modules"][-1]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    # Keep every statement and probe. Refreshing the source hash forces the
    # acceptance decision to depend on Lean's reachable axiom report.
    command = [sys.executable, str(changed / "check.py"), "--repo", str(args.repo.resolve()),
               "--lean", str(args.lean.resolve()), "--build-dir", str(output / "build")]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    (output / "checker.log").write_bytes(result.stdout)
    log = output / "build/R420ScatterLifecycle.log"
    expected = b"nonstandard axioms: CurrentMain.R420ScatterLifecycle.exact_lifecycle"
    if result.returncode == 0 or expected not in result.stdout or not log.exists() or "sorryAx" not in log.read_text():
        raise ValueError("missing-proof negative control did not reach the expected axiom rejection")
    summary = {"status": "PASS", "control": "exact_lifecycle proof replaced by sorry",
               "checker_exit": result.returncode, "rejection": expected.decode(),
               "lean_log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
    (output / "NEGATIVE_RESULT.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("PASS missing lifecycle proof rejected through sorryAx after compilation")


if __name__ == "__main__":
    main()
