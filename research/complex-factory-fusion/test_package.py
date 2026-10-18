#!/usr/bin/env python3
"""Check relocation, source integrity and output preservation.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. The mathematical rejection controls are in verify.py.
"""
import json
import os
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


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="factory fusion ") as directory:
        checkout = Path(directory) / "minimal checkout"
        package = checkout / HERE.relative_to(ROOT)
        files = set(pins["files"])
        files.update(str(p.relative_to(ROOT)) for p in HERE.rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
        for name in files:
            target = checkout / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
        environment = os.environ.copy()
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
            environment[name] = "1"

        def run(extra=(), reason=None):
            result = subprocess.run(command + list(extra), cwd=directory,
                                    env=environment, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=300)
            if reason is None:
                need(result.returncode == 0 and "PASS_EXACT_COMPLEX_FACTORY_FUSION" in result.stdout,
                     "relocated check failed:\n" + result.stdout[-4000:])
            else:
                need(result.returncode != 0 and reason in result.stdout,
                     "wrong failure:\n" + result.stdout[-2000:])

        run()
        print("PASS minimal offline relocation with isolated optimized Python", flush=True)
        path = checkout / "research/complex-dyadic-lowering/lower.py"
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        run(reason="source pin:")
        path.write_bytes(original)
        path = package / "CIRCUIT.json"
        original = path.read_bytes()
        changed = json.loads(original)
        changed["levels"][0] = True
        path.write_text(json.dumps(changed))
        run(reason="noninteger certificate")
        path.write_bytes(original)
        receipt = Path(directory) / "existing receipt.json"
        receipt.write_bytes(b"user-owned result\n")
        run(["--write", str(receipt)], "receipt output already exists")
        need(receipt.read_bytes() == b"user-owned result\n", "receipt overwritten")
        occupied = Path(directory) / "existing artifacts"
        occupied.mkdir()
        marker = occupied / "retain.txt"
        marker.write_bytes(b"retain\n")
        run(["--out", str(occupied)], "artifact output already exists")
        need(list(occupied.iterdir()) == [marker] and marker.read_bytes() == b"retain\n",
             "artifact directory changed")
    print("PASS_FACTORY_FUSION_PACKAGE relocation=1 corruption=2 output_preservation=2")


if __name__ == "__main__":
    main()
