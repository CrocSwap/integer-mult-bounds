#!/usr/bin/env python3
"""Source corruption, receipt corruption and relocated optimized replay.
Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(package, root, pins_only=False, failure=None):
    argv = [sys.executable, "-I", "-O", "-B", str(package / "verify.py"), "--source-root", str(root)]
    if pins_only:
        argv.append("--pins-only")
    result = subprocess.run(argv, cwd=root, text=True, capture_output=True, timeout=120)
    if failure is None:
        need(result.returncode == 0, result.stdout + result.stderr)
    else:
        need(result.returncode != 0 and failure in result.stderr,
             "expected fail-closed rejection: " + result.stdout + result.stderr)
    return result.stdout


def inventory(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pins = [pin for pin in sources["files"] if pin["usage"] == "input"]
    with tempfile.TemporaryDirectory(prefix="four-shear-export-") as directory:
        root = Path(directory)
        package = root / "relocated-checker"
        package.mkdir()
        for name in ("verify.py", "independent.py", "SOURCES.json", "EVIDENCE.json"):
            shutil.copyfile(HERE / name, package / name)
        for pin in pins:
            path = root / pin["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / pin["path"], path)
        run(package, root, pins_only=True)
        for pin in pins:
            path = root / pin["path"]
            original = path.read_bytes()
            path.write_bytes(original + b"\nsource-corruption-control\n")
            run(package, root, pins_only=True, failure="source pin mismatch")
            path.write_bytes(original)
        receipt = package / "EVIDENCE.json"
        original = receipt.read_bytes()
        altered = json.loads(original)
        altered["exceptional_census"]["target_successes"] = 1
        receipt.write_text(json.dumps(altered))
        run(package, root, failure="committed evidence differs")
        receipt.write_bytes(original)
        before = inventory(root)
        output = run(package, root)
        need("PASS_BIDIRECTIONAL_FOUR_SHEAR_RIGIDITY" in output, "missing real replay marker")
        need(inventory(root) == before, "relocated default replay modified inputs or outputs")
    print("PASS_FOUR_SHEAR_PACKAGE_CONTROLS source_mutations=5 receipt_mutations=1 relocated_optimized=true read_only=true")


if __name__ == "__main__":
    main()
