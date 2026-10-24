"""Optimized standalone replay and actual subprocess corruption controls.

Produced by Nick Petalas. Apache-2.0. All temporary outputs use TMPDIR.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def run(directory, *arguments):
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-W", "error", "-B",
         str(directory / "verify.py"), *arguments],
        cwd=directory.parent, capture_output=True, text=True, timeout=60, check=False)
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mutations(directory):
    for name in ("PROOF.md", "oracle.py", "verify.py", "test_package.py"):
        target = directory / name
        original = target.read_bytes()
        target.write_bytes(original + b"\n# deliberate corruption\n")
        try:
            result = run(directory)
            require(result.returncode != 0 and "receipt mismatch" in result.stderr,
                    "source corruption accepted: " + name)
        finally:
            target.write_bytes(original)
    target = directory / "RESULT.json"
    original = target.read_bytes()
    for replacement in (b'{"status": true}', original.replace(b'"schema_version": 1',
                                                             b'"schema_version": true'),
                        b'{"status": 0, "status": 0}'):
        target.write_bytes(replacement)
        try:
            require(run(directory).returncode != 0, "receipt corruption accepted")
        finally:
            target.write_bytes(original)


def behavioral_mutations(directory):
    changes = [
        ("verify.py", "return (2 ** (budget + 1) + 2) // 3",
         "return (3 * 2**budget + 3) // 4", "equality size"),
        ("verify.py", "ends_full = arity == 2 or (",
         "ends_full = arity in (2, 3) or (", "endpoint control"),
        ("verify.py", "count - 2 * cap", "count - cap", "leaf invariant"),
        ("oracle.py", "else 4", "else 3", "oracle lower bound"),
    ]
    for index, (name, old, new, reason) in enumerate(changes):
        target = directory / name
        original = target.read_text()
        require(original.count(old) == 1, "ambiguous mutation")
        target.write_text(original.replace(old, new))
        try:
            # --write bypasses receipt comparison: rejection must come from
            # actual scientific checks, rather than a changed source hash.
            output = directory.parent / ("mutant-" + str(index) + ".json")
            result = run(directory, "--write", str(output))
            require(result.returncode != 0 and reason in result.stderr,
                    "behavioral mutation escaped: " + name + ": " + result.stderr)
            require(not output.exists(), "failed science published a receipt")
        finally:
            target.write_text(original)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    scratch = Path(os.environ.get("TMPDIR", tempfile.gettempdir())).resolve()
    require(scratch.is_dir() and ROOT not in scratch.parents and scratch != ROOT,
            "temporary directory must be external")
    with tempfile.TemporaryDirectory(prefix="echo-controls-", dir=scratch) as temporary:
        directory = Path(temporary) / "package"
        directory.mkdir()
        for name in ("PROOF.md", "oracle.py", "verify.py", "test_package.py", "RESULT.json"):
            shutil.copyfile(ROOT / name, directory / name)
        success = run(directory)
        require(success.returncode == 0, success.stderr)
        require("PASS_DIRTY_ECHO_MAXIMAL_EQUALITY" in success.stdout, "missing pass")
        mutations(directory)
        behavioral_mutations(directory)
        output = Path(temporary) / "generated.json"
        generated = run(directory, "--write", str(output))
        require(generated.returncode == 0, generated.stderr)
        require(output.read_bytes() == (directory / "RESULT.json").read_bytes(),
                "standalone generated receipt differs")
        rejected = run(directory, "--write", str(output))
        require(rejected.returncode != 0 and "FileExistsError" in rejected.stderr,
                "exclusive output overwritten")
        require(output.read_bytes() == (directory / "RESULT.json").read_bytes(),
                "rejected write changed output")
    print(json.dumps(dict(status="PASS_DIRTY_ECHO_EQUALITY_CONTROLS",
                          source_corruptions=4, receipt_corruptions=3,
                          behavioral_mutations=4, standalone_optimized=True,
                          exclusive_output=True), sort_keys=True))


if __name__ == "__main__":
    main()
