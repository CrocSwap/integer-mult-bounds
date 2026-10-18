# SPDX-License-Identifier: Apache-2.0
"""Rebuild both frozen providers and certify scalar-reference envelopes."""

import argparse
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from audit import run as audit_streams
from lattice import analyze, digest, require

HERE = Path(__file__).resolve().parent
MAX_BYTES = 8_000_000


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "regular input")
    require(path.stat().st_size <= MAX_BYTES, "bounded input")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "bounded decoded input")
    return json.loads(raw)


def authenticate(package=HERE):
    records = read_json(package / "VENDOR.json")["files"]
    require(len(records) == 8, "complete source inventory")
    require(len({r["path"] for r in records}) == 8, "unique source paths")
    for row in records:
        path = package / row["path"]
        require(path.resolve().is_relative_to(package), "contained source path")
        require(path.is_file() and not path.is_symlink(), "regular source")
        require(path.stat().st_size <= MAX_BYTES, "bounded source")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "source hash: " + row["path"],
        )
    return len(records)


def compile_provider(provider, work):
    source = HERE / f"vendor/WORD-{provider}.json.gz"
    output = work / provider
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPYCACHEPREFIX=str(work / "bytecode"),
    )
    for key in ("PYTHONOPTIMIZE", "PYTHONPATH"):
        env.pop(key, None)
    for script, args in (
        ("bw_transport.py", [source, output]),
        ("bw_emit.py", [output]),
    ):
        command = [
            sys.executable,
            "-W",
            "error",
            "-B",
            str(HERE / "vendor/native" / script),
            *map(str, args),
        ]
        with (work / f"{provider}-{script}.log").open("x") as log:
            subprocess.run(
                command,
                cwd=work,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=90,
            )
    programs = read_json(output / "LOCAL-PROGRAMS.json.gz")
    checks = read_json(output / "LOCAL-CHECKS.json")
    require(set(programs) == {"forward", "backward"}, "two native orientations")
    for name, events in programs.items():
        require(checks[name]["sha256"] == digest(events), "native program hash")
        require(checks[name]["all_columns"] == 632, "all source columns")
        require(
            checks[name]["zero_buffers_returned_to_zero"] == 91, "all private buffers"
        )
    return programs


def run(work):
    pins = authenticate()
    result = {}
    for provider in ("base", "extra"):
        programs = compile_provider(provider, work)
        result[provider] = {
            name: analyze(events, backward=name == "backward")
            for name, events in programs.items()
        }
    return {
        "status": "PASS_RANK7_SCALAR_REFERENCE_LATTICE_NOT_PHYSICAL_ADMISSION",
        "frozen_files": pins,
        "providers": result,
        "independent_integer_audit": audit_streams(work),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.work:
        require(not args.work.exists(), "fresh work directory")
        require(
            not args.work.resolve().is_relative_to(HERE.parents[1]),
            "external work directory",
        )
        args.work.mkdir(parents=True)
        result = run(args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-scalar-lattice-") as directory:
            result = run(Path(directory))
    expected = HERE / "RESULT.json"
    if args.write:
        require(not expected.exists(), "preserve existing evidence")
        with expected.open("x") as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        require(read_json(expected) == result, "complete deterministic receipt")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
