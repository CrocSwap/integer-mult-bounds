#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test complete replay, byte equality, relocation and missing/corrupted inputs."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(package, optimized=False, arguments=(), failure=None):
    flags = ["-I", "-B"] + (["-O"] if optimized else [])
    process = subprocess.run([sys.executable, *flags, str(package / "verify.py"), *map(str, arguments)],
                             cwd=package, capture_output=True, text=True)
    if failure is not None:
        require(process.returncode != 0 and failure in process.stderr,
                "packaging control was not rejected: " + failure)
        require("PASS_U8_B_SHEAR_REWRITE_SEED32" not in process.stdout, "failed input reported success")
    else:
        require(process.returncode == 0, "verifier failed: " + process.stderr)
        require(process.stdout.strip().startswith("PASS_U8_B_SHEAR_REWRITE_SEED32"), "success marker missing")


def main():
    expected = (HERE / "RESULT.json").read_bytes()
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        for optimized in (False, True):
            out = temporary / "RESULT.json"
            run(HERE, optimized, ["--write-result", out])
            require(out.read_bytes() == expected, "deterministic result bytes differ")

        # Only the package and its declared immutable archive are copied.
        relocated = temporary / "relocated"
        package = relocated / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        archive = relocated / pins["archive"]["path"]
        archive.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / pins["archive"]["path"], archive)
        for optimized in (False, True):
            out = temporary / "relocated-result.json"
            run(package, optimized, ["--write-result", out])
            require(out.read_bytes() == expected, "relocated result bytes differ")

        source_path = package / "SOURCES.json"
        original_sources = source_path.read_bytes()
        source_path.unlink()
        run(package, True, failure="SOURCES.json")
        source_path.write_bytes(original_sources)

        with archive.open("ab") as stream:
            stream.write(b"corrupted archive")
        run(package, True, failure="archive pin differs")
        shutil.copyfile(ROOT / pins["archive"]["path"], archive)

        bad_pins = json.loads(original_sources)
        bad_pins["members"]["native/local/CANONICAL-WORD.json.gz"] = "0" * 64
        source_path.write_text(json.dumps(bad_pins), encoding="utf-8")
        run(package, True, failure="member pin differs")
        source_path.write_bytes(original_sources)

        (package / "RESULT.json").write_bytes(expected + b"\n")
        run(package, True, failure="committed deterministic result differs")

    print("PASS_U8_B_SHEAR_PACKAGE deterministic_result=1")
    print("PASS_U8_B_SHEAR_PACKAGE_CLOSURE normal_and_optimized=PASS relocated=PASS controls=4")


if __name__ == "__main__":
    main()
