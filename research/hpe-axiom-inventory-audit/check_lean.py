#!/usr/bin/env python3
"""Reproduce the small syntax fixture with an explicit Lean 4.21.0 binary.

No Mathlib download or HPE build is involved. Apache-2.0; Hanson Sun with Codex.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--record", action="store_true", help="write new fixture evidence; refuse overwrite")
    args = parser.parse_args()
    lean = args.lean.resolve(strict=True)
    version = subprocess.check_output([str(lean), "--version"], text=True, timeout=30).strip()
    if not version.startswith("Lean (version 4.21.0,"):
        raise ValueError("the syntax fixture requires Lean 4.21.0")
    source = (HERE / "fixtures/ProbeSyntax.lean").read_bytes()
    with tempfile.TemporaryDirectory(prefix="hpe-lean-syntax-") as temporary:
        fixture = Path(temporary) / "ProbeSyntax.lean"
        fixture.write_bytes(source)
        process = subprocess.run([str(lean), str(fixture)], cwd=temporary,
                                 text=True, capture_output=True, timeout=60, check=True)
    if process.stderr:
        raise ValueError("unexpected Lean stderr: " + process.stderr)
    if args.record:
        metadata = {
            "scope": "Actual compiler output for three tiny syntax fixtures; no HPE theorem was compiled.",
            "version": version,
            "compiler_sha256": hashlib.sha256(lean.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "stdout_sha256": hashlib.sha256(process.stdout.encode()).hexdigest(),
            "command": ["lean-4.21.0", "ProbeSyntax.lean"],
            "exit_code": process.returncode,
        }
        with (HERE / "fixtures/lean421.txt").open("x", encoding="utf-8") as stream:
            stream.write(process.stdout)
        with (HERE / "fixtures/LEAN.json").open("x", encoding="utf-8") as stream:
            json.dump(metadata, stream, indent=2)
            stream.write("\n")
    elif process.stdout != (HERE / "fixtures/lean421.txt").read_text():
        raise ValueError("Lean fixture output differs")
    print("PASS_HPE_LEAN421_SYNTAX_FIXTURE probes=3 deliberately_forbidden_dependency=1 no_HPE_build")


if __name__ == "__main__":
    main()
