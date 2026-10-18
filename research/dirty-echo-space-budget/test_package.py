"""Check isolated relocation and fail-closed source/certificate handling."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(package, cwd, failure=None, arguments=()):
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *arguments],
        cwd=cwd, capture_output=True, text=True, timeout=120,
    )
    if failure is None:
        if result.returncode != 0 or "PASS_DIRTY_ECHO_SPACE_BUDGET:" not in result.stdout:
            raise RuntimeError("relocated replay failed: " + result.stderr)
    elif result.returncode == 0 or failure not in result.stderr:
        raise RuntimeError("expected rejection missing: " + str(failure) + "\n" + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="dirty-echo-space-budget-") as directory:
        parent = Path(directory)
        package = parent / "standalone package with spaces"
        shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        run(package, parent)

        source = package / "vendor" / "pr673" / "echo.py"
        original_source = source.read_bytes()
        source.write_bytes(original_source + b"\n")
        run(package, parent, "source hash mismatch")
        source.write_bytes(original_source)

        manifest = package / "SOURCES.json"
        original_manifest = manifest.read_bytes()
        changed = json.loads(original_manifest)
        changed["files"].pop()
        manifest.write_text(json.dumps(changed))
        run(package, parent, "source inventory is incomplete")
        changed = json.loads(original_manifest)
        changed["files"][0]["source_commit"] = "0" * 40
        manifest.write_text(json.dumps(changed))
        run(package, parent, "source provenance changed")
        manifest.write_bytes(original_manifest)

        expected = package / "EXPECTED.json"
        original_expected = expected.read_bytes()
        changed = json.loads(original_expected)
        changed["main_witnesses"][0]["minimum_calls"] -= 1
        expected.write_text(json.dumps(changed))
        run(package, parent, "recomputed certificate differs")
        for invalid_count in (True, 1.0):
            changed = json.loads(original_expected)
            changed["costs_by_budget"][0][0] = invalid_count
            expected.write_text(json.dumps(changed))
            run(package, parent, "recomputed certificate differs")
        expected.write_bytes(original_expected)
        run(package, parent, "FileExistsError", ("--write", str(expected)))
        if expected.read_bytes() != original_expected:
            raise RuntimeError("--write replaced an existing certificate")
    print("PASS_DIRTY_ECHO_PACKAGE: relocated replay and 7 artifact rejection controls")


if __name__ == "__main__":
    main()
