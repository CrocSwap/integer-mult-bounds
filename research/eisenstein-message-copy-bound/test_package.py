#!/usr/bin/env python3
"""Relocation, certificate tampering, input tampering and output-preservation QA."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def main():
    with tempfile.TemporaryDirectory(prefix="eisenstein-message-qa-") as tmp:
        root = Path(tmp) / "relocated"
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((HERE / "SOURCES.json").read_text())["files"]
        for item in sources:
            target = root / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item["path"], target)

        def run(*args):
            return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *map(str, args)], cwd=tmp, capture_output=True, text=True)

        receipt = Path(tmp) / "replayed.json"
        result = run("--output", receipt)
        require(result.returncode == 0, "relocated replay failed: " + result.stderr)
        require(receipt.read_bytes() == (package / "certificate.json").read_bytes(), "regenerated receipt bytes differ")
        old = receipt.read_bytes()
        result = run("--output", receipt)
        require(result.returncode != 0 and "FileExistsError" in result.stderr and receipt.read_bytes() == old, "existing output was overwritten")

        certificate = package / "certificate.json"
        original = certificate.read_bytes()
        corrupted = json.loads(original)
        corrupted["bound"]["equal_width_floor"] = "23b"
        certificate.write_text(json.dumps(corrupted))
        missing = Path(tmp) / "must-not-exist.json"
        result = run("--output", missing)
        require(result.returncode != 0 and "certificate differs" in result.stderr and not missing.exists(), "tampered certificate accepted or output written")
        certificate.write_bytes(original)

        source = root / sources[0]["path"]
        source.write_bytes(source.read_bytes() + b"\nmodified source\n")
        result = run("--output", missing)
        require(result.returncode != 0 and "source hash mismatch" in result.stderr and not missing.exists(), "tampered source accepted or output written")
    print("PASS_MESSAGE_PACKAGE: relocated isolated optimized replay; exact receipt; existing output preserved; certificate and source mutations rejected")


if __name__ == "__main__":
    main()
