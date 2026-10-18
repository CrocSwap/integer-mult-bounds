#!/usr/bin/env python3
"""Portable artifact-integrity controls for the QQ16 prefix certificate."""

import gzip
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
        raise ValueError(message)


def run(package, wanted):
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                            cwd=package.parents[1], text=True, capture_output=True, timeout=60)
    text = result.stdout + result.stderr
    need((result.returncode == 0) == (wanted == "PASS_QQ16_SHEAR_PREFIX_COST"), text)
    need(wanted in text, "missing expected result: " + wanted + "\n" + text)


def main():
    with tempfile.TemporaryDirectory(prefix="qq16-prefix-artifacts-") as temporary:
        export = Path(temporary)
        package = export / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        for entry in manifest["files"]:
            if entry["usage"] == "input":
                target = export / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / entry["path"], target)
        files = sorted(p for p in export.rglob("*") if p.is_file())
        before = {str(p.relative_to(export)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        directories = sorted([export] + [p for p in export.rglob("*") if p.is_dir()],
                             key=lambda p: len(p.parts), reverse=True)
        try:
            for p in files:
                p.chmod(0o444)
            for p in directories:
                p.chmod(0o555)
            run(package, "PASS_QQ16_SHEAR_PREFIX_COST")
            after = {str(p.relative_to(export)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in export.rglob("*") if p.is_file()}
            need(before == after, "read-only export changed or created files")
        finally:
            for p in directories:
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)

        source = export / "research/joint-query/certificate.json.gz"
        original = source.read_bytes()
        packet = json.loads(gzip.decompress(original))
        packet["native_line_recipes"]["inverse_21"]["label"] ^= 1
        source.write_bytes(gzip.compress(json.dumps(packet).encode(), mtime=0))
        run(package, "source pin:")
        source.write_bytes(original)

        receipt = package / "RESULT.json"
        original = receipt.read_bytes()
        data = json.loads(original)
        data["coverage"]["owned_scratch_fields"] = True  # Python True == 1 must not pass.
        receipt.write_text(json.dumps(data))
        run(package, "complete frozen receipt")
        receipt.write_bytes(original)

        prefix = package / "PREFIX.json"
        original = prefix.read_bytes()
        data = json.loads(original)
        data[0][2][1][1][3] = True  # Same arithmetic value, different artifact type.
        prefix.write_text(json.dumps(data))
        run(package, "complete frozen prefix instructions")
        prefix.write_bytes(original)
    print("PASS_QQ16_PREFIX_ARTIFACTS relocated_readonly_optimized=1 source_and_typed_artifact_rejections=3")


if __name__ == "__main__":
    main()
