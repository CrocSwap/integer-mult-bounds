#!/usr/bin/env python3
"""Corrupt real replay inputs in disposable source mirrors and require rejection.

Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RELATIVE = PACKAGE.relative_to(ROOT)


def need(condition, label):
    if not condition:
        raise SystemExit("FAIL_STRATIFIED_BOUNDARIES: " + label)


def run(root, optimized=False):
    command = [sys.executable, "-I", "-B"]
    if optimized:
        command.append("-O")
    command.append(str(root / RELATIVE / "verify.py"))
    return subprocess.run(command, cwd=root, text=True, capture_output=True,
                          timeout=30, check=False)


def main():
    inputs = json.loads((PACKAGE / "VERIFY.json").read_text())["inputs"]
    with tempfile.TemporaryDirectory(prefix="stratified-owned-reserves-") as temp:
        mirror = Path(temp)
        package = mirror / RELATIVE
        shutil.copytree(PACKAGE, package)
        for name in inputs:
            target = mirror / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        for optimized in (False, True):
            good = run(mirror, optimized)
            need(good.returncode == 0 and "PASS_STRATIFIED_OWNED_RESERVES" in good.stdout,
                 "clean Git-free replay in both interpreter modes")

        expected_path = package / "RESULT.json"
        original = expected_path.read_bytes()
        receipt = json.loads(original)
        # Python's untyped object equality identifies True and 1.  This
        # mutation specifically checks the typed canonical-JSON comparison.
        receipt["schema"] = True
        expected_path.write_text(json.dumps(receipt))
        bad = run(mirror, True)
        need(bad.returncode != 0 and "complete typed result equality" in bad.stderr,
             "typed receipt corruption rejects under optimization")
        expected_path.write_bytes(original)

        source_path = mirror / inputs[0]
        source = source_path.read_bytes()
        source_path.write_bytes(source + b"\nsource drift control\n")
        bad = run(mirror)
        need(bad.returncode != 0 and "SHA " in bad.stderr, "source drift rejects")
        source_path.write_bytes(source)

        model_path = package / "stack_model.py"
        model = model_path.read_text()
        mutation = model.replace('(("B0", Fraction(4)),)', '(("B0", Fraction(1)),)', 1)
        need(mutation != model, "edge mutation applied")
        model_path.write_text(mutation)
        bad = run(mirror, True)
        need(bad.returncode != 0 and "selected graph symbolic unit example" in bad.stderr,
             "dropped radix-embedding inflation rejects under optimization")
        model_path.write_text(model)

        last = run(mirror)
        need(last.returncode == 0, "restoration after all mutations")
    print("PASS_STRATIFIED_BOUNDARIES clean_modes=2 rejecting_controls=3")


if __name__ == "__main__":
    main()
