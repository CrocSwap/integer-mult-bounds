#!/usr/bin/env python3
"""Relocated optimized CLI checks and four corruption controls. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(root, script, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(root / script), *map(str, args)],
                          cwd=root.parent, capture_output=True, text=True, timeout=30)


def main():
    with tempfile.TemporaryDirectory(prefix="reader-cuts-") as tmp:
        copy = Path(tmp) / "package"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("__pycache__"))
        result = run(copy, "verify.py")
        need(result.returncode == 0 and "PASS_READER_RESTORATION_CUTS" in result.stdout, result.stderr)
        result = run(copy, "verify.py", "--json")
        need(result.returncode == 0 and json.loads(result.stdout) == json.loads((copy / "CERTIFICATE.json").read_text()),
             "relocated canonical regeneration")
        result = run(copy, "planner.py", copy / "fixture.json")
        need(result.returncode == 0 and json.loads(result.stdout)["cost"] == 1, "public planner CLI")
        mutations = [
            ("CERTIFICATE.json", lambda s: s.replace('"cost": 1', '"cost": 2', 1), "saved certificate mismatch"),
            ("sources/pr1155/verify.py", lambda s: s + "\n# changed source\n", "source hash"),
            ("fixture.json", lambda s: s.replace('"reader": [-1]', '"reader": [1]', 1), "five-child construction"),
            ("planner.py", lambda s: s.replace('"cost": cost, "cuts"', '"cost": cost + 1, "cuts"', 1),
             "planner disagrees"),
        ]
        for path, change, message in mutations:
            file = copy / path
            original = file.read_text()
            altered = change(original)
            need(altered != original, "mutation did not change input")
            file.write_text(altered)
            result = run(copy, "verify.py")
            file.write_text(original)
            need(result.returncode != 0 and message in result.stderr, "mutation not rejected: " + path)
        invalid = copy / "bad-input.json"
        invalid.write_text('{"children": [], "prices": [1], "ignored": true}')
        result = run(copy, "planner.py", invalid)
        need(result.returncode != 0 and "unknown input fields" in result.stderr, "unknown CLI field accepted")
    print("PASS_READER_CUT_PACKAGE relocation=PASS regeneration=PASS corruptions=4 cli_controls=1")


if __name__ == "__main__":
    main()
