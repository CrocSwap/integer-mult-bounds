#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""CLI corruption checks on disposable copies; never edit predecessor inputs."""
import hashlib
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


def hashes(directory):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.iterdir() if p.is_file()}


def run(directory, script, expected_error=None):
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(directory / script)],
                            capture_output=True, text=True, encoding="utf-8", timeout=45)
    if expected_error is None:
        need(result.returncode == 0, script + " positive failed: " + result.stderr)
    else:
        need(result.returncode != 0 and expected_error in result.stderr,
             script + " mutation did not fail as intended: " + result.stdout + result.stderr)


def main():
    before = hashes(HERE)
    # A sibling preserves repository-relative source lookup. The temporary
    # directory is created here, validated here, then cleaned by its owner.
    with tempfile.TemporaryDirectory(prefix=".p112-floor-test-", dir=HERE.parent) as name:
        sandbox = Path(name).resolve()
        need(sandbox.parent == HERE.parent.resolve() and sandbox != HERE,
             "temporary copy must be a new package sibling")
        for path in HERE.iterdir():
            if path.is_file():
                shutil.copy2(path, sandbox / path.name)
        copied = hashes(sandbox)
        run(sandbox, "verify.py")
        run(sandbox, "audit.py")
        need(hashes(sandbox) == copied, "positive default replay wrote files")

        result_path = sandbox / "RESULT.json"
        source_path = sandbox / "SOURCES.json"
        result_original, source_original = result_path.read_bytes(), source_path.read_bytes()
        result = json.loads(result_original)
        result["finite_premises"]["hyperplanes"][0]["minor_determinant"] += 1
        result_path.write_text(json.dumps(result), encoding="utf-8")
        run(sandbox, "verify.py", "complete typed RESULT.json mismatch")
        run(sandbox, "audit.py", "exact minor determinant")
        result_path.write_bytes(result_original)

        sources = json.loads(source_original)
        next(row for row in sources["files"] if row["usage"] == "input")["git_blob"] = "0" * 40
        source_path.write_text(json.dumps(sources), encoding="utf-8")
        run(sandbox, "verify.py", "Git blob mismatch")
        source_path.write_bytes(source_original)

        result = json.loads(result_original)
        result["rectangular_coupling_fixture"]["cost"] -= 1
        result_path.write_text(json.dumps(result), encoding="utf-8")
        run(sandbox, "verify.py", "complete typed RESULT.json mismatch")
        result_path.write_bytes(result_original)

        text = result_original.decode("utf-8")
        result_path.write_text('{"schema_version": 1,' + text[1:], encoding="utf-8")
        run(sandbox, "verify.py", "duplicate JSON key")
    need(hashes(HERE) == before, "package source bytes changed")
    print("PASS_P112_BATCH_PACKAGE positive_relocation=2 mutation_groups=4 rejected_runs=5 read_only=1")


if __name__ == "__main__":
    main()
