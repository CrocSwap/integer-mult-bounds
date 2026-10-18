#!/usr/bin/env python3
"""Behavioral controls, including all four encoded commutation obligations.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def snapshot(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file()}


def command(folder, script, ok, marker):
    env = dict(os.environ, PYTHONOPTIMIZE="2", PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run([sys.executable, "-I", "-O", "-B", str(folder / script)],
                          cwd=folder.parent, env=env, capture_output=True, text=True, timeout=120)
    require((proc.returncode == 0) == ok, "wrong exit: " + proc.stdout + proc.stderr)
    require(marker in proc.stdout + proc.stderr, "wrong failure or marker: " + proc.stderr)


def main():
    v = runpy.run_path(str(HERE / "verify.py"))
    # Each missing crossing condition has a witness satisfying the other three.
    semantic = 0
    for left in range(2):
        for right in range(2):
            first = ((0, 1), (1, 0))
            second = [(0, 2), (2, 0)]
            x, z = second[right]
            second[right] = (x ^ (1 if left == 0 else 0), z ^ (1 if left == 1 else 0))
            enc = [first, second]
            pairings = {(a, b): v["symp"](enc[0][a], enc[1][b])
                        for a in range(2) for b in range(2)}
            require([key for key, value in pairings.items() if value] == [(left, right)],
                    "control does not isolate exactly one relation")
            require(all(v["symp"](a, b) == 1 for a, b in enc), "self relation lost")
            require(not v["check_encoding"]((0, 1, 0, 1), enc, 2), "missing-relation mutant accepted")
            semantic += 1
    # An unweighted substitution would accept four dimensions for this block case.
    width, _ = v["weighted_assignment"]((2, 0, 1), (1, 2, 1))
    require(width == 3 and v["brute_chain"]((2, 0, 1), (1, 1, 1)) == 2,
            "weighted-versus-unweighted boundary")
    semantic += 1

    with tempfile.TemporaryDirectory(prefix="encoded bank controls ") as tmp:
        root = Path(tmp)
        folder = root / "package without git"
        shutil.copytree(HERE, folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        before = snapshot(folder)
        for p in folder.rglob("*"):
            if p.is_file():
                p.chmod(0o444)
        command(folder, "verify.py", True, "PASS_ENCODED_PHASE_BANK")
        command(folder, "independent.py", True, "PASS_INDEPENDENT_ENCODED_BANK_MATRICES")
        require(snapshot(folder) == before, "ordinary replay changed files")
        # Restore permissions only on this disposable copy before mutation tests.
        for p in folder.rglob("*"):
            if p.is_file():
                p.chmod(0o644)
        source = folder / "references" / "PR2859-README.md"
        old = source.read_bytes()
        source.write_bytes(old + b"\nchanged reference\n")
        command(folder, "verify.py", False, "reference SHA256")
        source.write_bytes(old)
        result = folder / "RESULT.json"
        old = result.read_bytes()
        data = json.loads(old)
        data["no_new_kappa"] = 1  # Python == would confuse this with True.
        result.write_text(json.dumps(data))
        command(folder, "verify.py", False, "receipt mismatch")
        result.write_bytes(old)
        result = folder / "MATRICES.json"
        old = result.read_bytes()
        data = json.loads(old)
        data["coefficients"] -= 1
        result.write_text(json.dumps(data))
        command(folder, "independent.py", False, "independent receipt mismatch")
        result.write_bytes(old)
        require(snapshot(folder) == before, "restored controls differ")
    print("PASS_ENCODED_BANK_PACKAGE_CONTROLS semantic=5 corruption=3 optimized_git_free_read_only=true")


if __name__ == "__main__":
    main()
