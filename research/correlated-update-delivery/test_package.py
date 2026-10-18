#!/usr/bin/env python3
"""Focused file-integrity, optimized-execution and relocation checks. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_CORRELATED_UPDATE_PACKAGE " + message)


def execute(package, cwd, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *map(str, args)],
                          cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)


def main():
    with tempfile.TemporaryDirectory(prefix="correlated-delivery-") as temporary:
        root = Path(temporary) / "export"
        package = root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        inputs = [item for item in json.loads((PACKAGE / "SOURCES.json").read_text())["files"] if item["usage"] == "input"]
        for item in inputs:
            destination = root / item["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / item["path"], destination)
        empty = Path(temporary) / "unrelated"
        empty.mkdir()
        original = (package / "RESULT.json").read_bytes()
        positive = execute(package, empty)
        need(positive.returncode == 0 and "PASS_CORRELATED_UPDATE_DELIVERY" in positive.stdout, "optimized relocated replay: " + positive.stdout)
        need((package / "RESULT.json").read_bytes() == original, "normal replay rewrote receipt")
        source = root / inputs[0]["path"]
        retained = source.read_bytes()
        source.write_bytes(retained + b"\ncorruption\n")
        altered = execute(package, empty)
        need(altered.returncode != 0 and "source SHA256 drift" in altered.stdout, "source drift accepted")
        source.write_bytes(retained)
        receipt = json.loads(original)
        receipt["pilot"]["correlated"]["xor"] -= 1
        (package / "RESULT.json").write_text(json.dumps(receipt))
        altered = execute(package, empty)
        need(altered.returncode != 0 and "receipt mismatch" in altered.stdout, "undercharged receipt accepted")
        (package / "RESULT.json").write_bytes(original)
        occupied = Path(temporary) / "occupied.json"
        occupied.write_text("keep this exact data\n")
        refused = execute(package, empty, "--write-result", occupied)
        need(refused.returncode != 0 and occupied.read_text() == "keep this exact data\n", "occupied output overwritten")
        exported = Path(temporary) / "fresh.json"
        positive = execute(package, empty, "--write-result", exported)
        need(positive.returncode == 0 and json.loads(exported.read_text()) == json.loads(original), "nonportable regenerated payload")
    print("PASS_CORRELATED_UPDATE_PACKAGE controls=5 optimized_relocated_read_only")


if __name__ == "__main__":
    main()
