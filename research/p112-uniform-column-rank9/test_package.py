#!/usr/bin/env python3
"""Read-only relocation and claim/source corruption checks. Apache-2.0."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix="uniform-column-controls-") as directory:
        target = Path(directory) / "relocated"
        shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        def run(error=None, script="verify.py"):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(target / script)],
                                    cwd=directory, capture_output=True, text=True, timeout=120)
            if error is None:
                need(result.returncode == 0 and "PASS_" in result.stdout, "relocated replay: " + result.stderr)
            else:
                need(result.returncode != 0 and error in result.stderr,
                     "corruption escaped or failed for wrong reason: " + result.stderr)
        before = inventory(target)
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        run()
        run(script="independent.py")
        need(inventory(target) == before, "read-only replay wrote package files")
        checks.append("both-optimized-read-only-relocated-checkers")
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o644)

        def mutate(name, filename, change, error):
            path = target / filename
            saved = path.read_bytes()
            path.write_bytes(change(saved))
            try:
                run(error)
                checks.append(name)
            finally:
                path.write_bytes(saved)
        def edit(data, change):
            obj = json.loads(data)
            change(obj)
            return (json.dumps(obj) + "\n").encode()
        mutate("false-COPY63-claim", "EXPECTED.json",
               lambda data: edit(data, lambda x: x.update(sharp_copy_floor=63)), "receipt mismatch")
        mutate("weakened-nine-mixed-bound", "EXPECTED.json",
               lambda data: edit(data, lambda x: x.update(sharp_nine_mixed_floor=64)), "receipt mismatch")
        mutate("omitted-puncture-coverage", "EXPECTED.json",
               lambda data: edit(data, lambda x: x["finite"]["exceptional_character_indices"].pop()),
               "receipt mismatch")
        mutate("retained-geometry-drift", "references/PR845-geometry.py",
               lambda data: data + b"\n", "retained source SHA256")
        mutate("predecessor-proof-drift", "references/PR1591-PROOF.md",
               lambda data: data + b"\n", "remote attribution SHA256")
        mutate("missing-source-inventory", "SOURCES.json",
               lambda data: edit(data, lambda x: x["files"].pop()), "source inventory")
        mutate("duplicate-receipt-key", "EXPECTED.json",
               lambda data: b'{"scope":1,"scope":2}', "duplicate JSON key")
        mutate("nonfinite-receipt", "EXPECTED.json",
               lambda data: b'{"value":NaN}', "noninteger/nonfinite JSON number")
        need(inventory(target) == before, "controls did not restore original bytes")
    print("PASS_UNIFORM_COLUMN_PACKAGE_CONTROLS", "checks=" + str(len(checks)))
    print(json.dumps(checks))


if __name__ == "__main__":
    main()
