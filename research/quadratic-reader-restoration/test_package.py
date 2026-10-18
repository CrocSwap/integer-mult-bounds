#!/usr/bin/env python3
"""Standalone replay and real rejection controls. Apache-2.0.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(package, cwd, expected_success):
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                            cwd=cwd, text=True, capture_output=True, timeout=120)
    if expected_success:
        if result.returncode or "PASS_QUADRATIC_READER" not in result.stdout:
            raise ValueError("valid standalone replay failed: " + result.stdout + result.stderr)
        print(result.stdout.strip())
    elif result.returncode == 0 or "FAIL_QUADRATIC_READER" not in result.stderr:
        raise ValueError("corruption was not rejected: " + result.stdout + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="quadratic-reader-check-") as temporary:
        root = Path(temporary)
        package = root / "package"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        run(package, root, True)
        source = package / "context/pr1205-README.md"
        original = source.read_bytes()
        source.write_bytes(original + b"\ncorrupt source\n")
        run(package, root, False)
        source.write_bytes(original)
        context = package / "CONTEXT.json"
        original_context = context.read_text()
        changed = json.loads(original_context)
        changed["predecessor_heads"]["PR1205"] = "0" * 40
        context.write_text(json.dumps(changed))
        run(package, root, False)
        context.write_text(original_context)
        certificate = package / "CERTIFICATE.json"
        original_certificate = certificate.read_text()
        for corruption in ("unpaid_coefficients", "omitted_repair", "missing_census_case"):
            changed = json.loads(original_certificate)
            if corruption == "unpaid_coefficients":
                pilot = next(c for c in changed["cost_cases"] if c["arity"] == 8)
                pilot["costs"]["bilinear"]["constant_mul"] = 0
                pilot["costs"]["bilinear"]["scalar_operations"] -= 3
            elif corruption == "omitted_repair":
                changed["pilot"]["bilinear_word"] = [
                    gate for gate in changed["pilot"]["bilinear_word"] if gate[0] != "product"]
            else:
                changed["census"]["batches"] -= 1
            certificate.write_text(json.dumps(changed))
            run(package, root, False)
        certificate.write_text(original_certificate)
        print("PASS_QUADRATIC_READER_PACKAGE relocation=1 corruptions=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
