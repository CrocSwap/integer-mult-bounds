#!/usr/bin/env python3
"""Exercise the public replay boundary, including a Git-free read-only export."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from power import need
from verify import authenticate


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def invoke(root, *extra):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py"), *extra],
                          cwd=root, capture_output=True, text=True, timeout=90)


def main():
    authenticate(HERE)
    with tempfile.TemporaryDirectory(prefix="t74-evacuation-check-", dir=Path.cwd()) as directory:
        exported = Path(directory) / "export"
        shutil.copytree(HERE, exported, ignore=shutil.ignore_patterns("__pycache__"))
        before = hashes(exported)
        files = [p for p in exported.rglob("*") if p.is_file()]
        directories = [p for p in exported.rglob("*") if p.is_dir()] + [exported]
        try:
            for p in files:
                p.chmod(0o444)
            for p in directories:
                p.chmod(0o555)
            run = invoke(exported)
            need(run.returncode == 0 and "PASS_T74_EVACUATION_POWER_AUDIT" in run.stdout,
                 "read-only export replay: " + run.stderr[-1500:])
            need(hashes(exported) == before, "read-only export changed files")
        finally:
            for p in directories:
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)
        # The copy has no .git; the standalone verifier uses only retained bytes.
        need(not (exported / ".git").exists(), "export has Git metadata")
        target = exported / "sources" / "pr2575-fill.json.gz"
        raw = target.read_bytes()
        bad = bytearray(raw); bad[-1] ^= 1
        target.write_bytes(bad)
        try:
            authenticate(exported)
        except ValueError as error:
            need(str(error) == "source SHA256: pr2575-fill.json.gz", "source mutation reason")
        else:
            raise ValueError("source mutation accepted")
        target.write_bytes(raw)
        receipt = exported / "RESULT.json"
        original = receipt.read_bytes()
        changed = json.loads(original)
        changed["calls"] = float(changed["calls"])
        receipt.write_text(json.dumps(changed))
        run = invoke(exported)
        need(run.returncode != 0 and "committed receipt mismatch" in run.stderr, "typed receipt mutation accepted")
        receipt.write_bytes(original)
        run = invoke(exported, "--write-receipt", str(receipt))
        need(run.returncode != 0 and "FileExistsError" in run.stderr, "existing output overwritten")
        need(hashes(exported) == before, "integrity controls did not restore export")
    print("PASS_T74_EVACUATION_INTEGRITY controls=4 git_free_read_only=true")


if __name__ == "__main__":
    main()
