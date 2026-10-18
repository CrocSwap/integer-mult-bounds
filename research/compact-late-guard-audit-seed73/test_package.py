#!/usr/bin/env python3
"""Subprocess corruption controls and a read-only minimal relocated replay.

Hanson Sun / bbMisk, substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RELATIVE = PACKAGE.relative_to(ROOT)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def populate(root):
    target = root / RELATIVE
    shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for source in sources["files"]:
        if source["usage"] == "input":
            destination = root / source["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source["path"], destination)
    return target


def run(root, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B",
                           str(root / RELATIVE / "verify.py"), *map(str, args)],
                          cwd=root.parent, text=True, capture_output=True, timeout=120)


def reject(root, expected, *args):
    result = run(root, *args)
    need(result.returncode != 0 and "FAIL_COMPACT_LATE_GUARD" in result.stderr
         and expected in result.stderr,
         "fault was not rejected for the specified reason: " + expected + "\n" +
         result.stdout + result.stderr)


def change(path, old, new):
    data = path.read_text()
    need(data.count(old) == 1, "mutation target is not unique")
    path.write_text(data.replace(old, new))


def main():
    started = time.monotonic()
    faults = []
    with tempfile.TemporaryDirectory(prefix="compact late guard package ") as directory:
        base = Path(directory)
        clean = base / "minimal read only export"
        populate(clean)
        # No Git metadata, selected frontier, or undeclared import files exist.
        files = sorted(p for p in clean.rglob("*") if p.is_file())
        dirs = sorted((p for p in clean.rglob("*") if p.is_dir()), reverse=True)
        before = {str(p.relative_to(clean)): p.read_bytes() for p in files}
        try:
            for p in files:
                p.chmod(0o444)
            for p in dirs:
                p.chmod(0o555)
            clean.chmod(0o555)
            positive = run(clean)
            need(positive.returncode == 0 and "PASS_COMPACT_LATE_TWO_PASS_GUARD" in positive.stdout,
                 "minimal relocated replay failed\n" + positive.stdout + positive.stderr)
            after = {str(p.relative_to(clean)): p.read_bytes()
                     for p in clean.rglob("*") if p.is_file()}
            need(before == after, "read-only replay changed its source closure")
            print(positive.stdout.strip())
        finally:
            clean.chmod(0o755)
            for p in dirs:
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)

        def fixture(name):
            root = base / name
            return root, populate(root)

        root, package = fixture("source drift")
        source = root / "scripts/audit_compact_controls.py"
        source.write_text(source.read_text() + "\n# fault injection\n")
        reject(root, "source drift", "--check-inputs")
        faults.append("source drift")

        root, package = fixture("missing receipt")
        (package / "EXPECTED.json").unlink()
        reject(root, "expected receipt missing")
        need(not (package / "EXPECTED.json").exists(), "missing receipt silently regenerated")
        faults.append("missing receipt")

        root, package = fixture("corrupted receipt")
        receipt = json.loads((package / "EXPECTED.json").read_text())
        receipt["admitted"] += 1
        (package / "EXPECTED.json").write_text(json.dumps(receipt))
        reject(root, "expected receipt mismatch")
        faults.append("corrupted receipt")

        root, package = fixture("first call only")
        change(package / "verify.py", "active = self.parity[u] | c", "active = self.parity[u]")
        reject(root, "first_guard_only counterexample")
        faults.append("first-call-only guard")

        root, package = fixture("missing source carry guard")
        change(package / "verify.py", "if not self.nonsaturated[t] or not self.source_ok(c, u):",
               "if not self.nonsaturated[t]:")
        reject(root, "two-pass contract equivalence")
        faults.append("missing source carry guard")

        root, package = fixture("omitted highest xor")
        change(package / "verify.py", 'completed = dict(actual, y=actual["y"] ^ top)',
               "completed = dict(actual)")
        reject(root, "completed highest-bit endpoint")
        faults.append("omitted highest XOR")

        root, package = fixture("occupied output")
        output = root / "preserve.json"
        output.write_bytes(b"pre-existing result\n")
        reject(root, "receipt destination already exists", "--write", output)
        need(output.read_bytes() == b"pre-existing result\n", "existing receipt overwritten")
        faults.append("occupied output")

    print("PASS_COMPACT_LATE_GUARD_PACKAGE relocated_isolated_optimized=PASS faults=" + str(len(faults)))
    print("Package checks:", ", ".join(faults))
    print("Elapsed seconds:", round(time.monotonic() - started, 3))


if __name__ == "__main__":
    main()
