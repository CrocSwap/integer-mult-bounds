#!/usr/bin/env python3
"""Relocation, read-only replay and on-disk claim/source corruption controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix="four-transfer-check-") as directory:
        target = Path(directory) / "isolated-package"
        shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

        def run(expected_error=None):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py")],
                                    cwd=directory, text=True, capture_output=True, timeout=60)
            if expected_error is None:
                need(result.returncode == 0 and "PASS_FOUR_TRANSFER_OBSTRUCTION" in result.stdout,
                     "isolated replay failed: " + result.stderr)
            else:
                need(result.returncode != 0 and expected_error in result.stderr,
                     "corruption escaped or failed for the wrong reason: " + result.stderr)

        before = inventory(target)
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        run()
        need(inventory(target) == before, "normal replay mutated the isolated package")
        checks.append("isolated-optimized-read-only-replay")
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o644)

        def mutate(name, filename, edit, message):
            path = target / filename
            saved = path.read_bytes()
            path.write_bytes(edit(saved))
            try:
                run(message)
                checks.append(name)
            finally:
                path.write_bytes(saved)

        def json_edit(data, edit):
            obj = json.loads(data)
            edit(obj)
            return (json.dumps(obj) + "\n").encode()

        mutate("weakened-transfer-bound", "EXPECTED.json",
               lambda data: json_edit(data, lambda x: x.update(minimum_transfer_lower_bound_at_two_calls_per_operator=4)),
               "receipt mismatch")
        mutate("false-universal-coverage", "EXPECTED.json",
               lambda data: json_edit(data, lambda x: x.update(five_source_maximum_coverage_including_zero=32)),
               "receipt mismatch")
        mutate("altered-retained-predecessor", "references/PR943-CERTIFICATE.json",
               lambda data: data + b"\n", "retained source SHA256")
        mutate("altered-concurrent-source", "references/PR1438-README.md",
               lambda data: data + b"\n", "remote retained source SHA256")
        mutate("missing-source-inventory-entry", "SOURCES.json",
               lambda data: json_edit(data, lambda x: x["files"].pop()), "complete source inventory")
        mutate("duplicate-json-key", "EXPECTED.json",
               lambda data: b'{"status":"first","status":"second"}', "duplicate JSON key")
        mutate("nonfinite-json", "EXPECTED.json",
               lambda data: b'{"value":NaN}', "noninteger/nonfinite JSON number")
        need(inventory(target) == before, "corruption controls failed to restore source bytes")
    print("PASS_FOUR_TRANSFER_PACKAGE_CONTROLS", "checks=" + str(len(checks)))
    print(json.dumps(checks))


if __name__ == "__main__":
    main()
