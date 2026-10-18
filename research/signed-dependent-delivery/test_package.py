#!/usr/bin/env python3
"""Portable replay and defect-sensitive evidence controls. Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def call(script, expected=0, contains=None):
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(script)],
                            text=True, capture_output=True, timeout=60)
    require((result.returncode == 0) == (expected == 0), "unexpected replay status: " + result.stderr)
    if contains:
        require(contains in result.stderr, "wrong failure: " + result.stderr)
    return result


def main():
    source_manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="signed-delivery-portable-") as temporary:
        export = Path(temporary)
        package = export / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for pin in source_manifest["files"]:
            if pin["usage"] == "input":
                target = export / pin["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / pin["path"], target)
        require(not (export / ".git").exists(), "portable export has Git metadata")
        before = hashes(export)
        for path in export.rglob("*"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        call(package / "verify.py")
        call(package / "independent.py")
        require(hashes(export) == before, "read-only replay changed export")
        for path in export.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        # Mutating a live scientific input must fail before mathematical replay.
        first = next(x for x in source_manifest["files"] if x["usage"] == "input")
        source = export / first["path"]
        original = source.read_bytes()
        source.write_bytes(original + b"\nsource-defect\n")
        call(package / "verify.py", expected=1, contains="source mismatch")
        source.write_bytes(original)
        # Exact payload comparison must reject both an undercharge and bool/int alias.
        receipt = package / "RESULT.json"
        original_receipt = receipt.read_bytes()
        value = json.loads(original_receipt)
        value["pilot"]["candidate"]["unit_adds"] -= 1
        receipt.write_text(json.dumps(value))
        call(package / "verify.py", expected=1, contains="complete result receipt mismatch")
        value = json.loads(original_receipt)
        value["schema_version"] = True
        receipt.write_text(json.dumps(value))
        call(package / "verify.py", expected=1, contains="complete result receipt mismatch")
        receipt.write_bytes(original_receipt)
    print("PASS_SIGNED_DELIVERY_PORTABILITY controls=4 optimized_read_only_git_free")


if __name__ == "__main__":
    main()
