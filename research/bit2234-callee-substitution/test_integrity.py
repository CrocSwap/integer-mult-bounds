#!/usr/bin/env python3
"""Public CLI positive relocation and source/receipt rejection controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def execute(directory, optimized=False):
    args = [sys.executable, "-I", "-B"]
    if optimized:
        args.append("-O")
    args.append(str(directory / "verify.py"))
    return subprocess.run(args, cwd=directory, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=90)


def main():
    # The system temporary directory is provided by the running environment.
    # No source file in the live package is ever changed by these controls.
    with tempfile.TemporaryDirectory(prefix="bit2234-callee-") as temporary:
        copy = Path(temporary) / "export"
        shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("__pycache__"))
        result = execute(copy)
        need(result.returncode == 0 and "PASS_BIT2234_CALLEE_SUBSTITUTION" in result.stdout,
             "relocated Git-free replay: " + result.stderr)
        source = copy / "sources/pr-2234/header_streams.py"
        original = source.read_bytes()
        source.write_bytes(original.replace(b"width-1", b"width+1", 1))
        result = execute(copy, True)
        need(result.returncode != 0 and "vendored source SHA256" in result.stderr,
             "source corruption must reject before executing code")
        source.write_bytes(original)
        receipt = copy / "RESULT.json"
        original_receipt = receipt.read_text()
        for key, change in [("adapter", lambda x: x.update(cases=x["cases"] + 1)),
                            ("adapter", lambda x: x.update(binary_calls=True)),
                            ("adapter", lambda x: x.update(cases=float(x["cases"])) )]:
            data = json.loads(original_receipt)
            change(data[key])
            receipt.write_text(json.dumps(data))
            result = execute(copy, True)
            need(result.returncode != 0 and "exact typed receipt comparison" in result.stderr,
                 "changed typed receipt must reject")
        receipt.write_text(original_receipt.replace('"source_files": 8', '"source_files": 8, "source_files": 8'))
        result = execute(copy)
        need(result.returncode != 0 and "duplicate JSON key" in result.stderr,
             "duplicate receipt key must reject")
    print("PASS_BIT2234_CALLEE_INTEGRITY relocated=1 source_faults=1 receipt_faults=4")


if __name__ == "__main__":
    main()
