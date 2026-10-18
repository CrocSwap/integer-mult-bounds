# SPDX-License-Identifier: Apache-2.0
"""Bounded source authentication and inherited native compiler execution."""

import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

from lower import require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
NATIVE = "research/two-sided-helper-extraction/vendor/fastnative/vendor/native/new/code/borrow"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    require(path.is_file() and path.stat().st_size <= 8_000_000, "bounded file")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(8_000_001)
    require(len(raw) <= 8_000_000, "bounded payload")
    return json.loads(raw)


def authenticate(package=PACKAGE, root=ROOT):
    frozen = read(package / "VENDOR.json")["files"]
    expected = {
        "vendor/WORD-base.json.gz",
        "vendor/WORD-extra.json.gz",
        "vendor/CREDITS.md",
        "vendor/NOTICE",
    }
    require(
        len(frozen) == 4 and {x["path"] for x in frozen} == expected,
        "complete frozen inventory",
    )
    live = [x for x in read(package / "SOURCES.json")["files"] if x["usage"] == "input"]
    require(
        len(live) == 2
        and {x["path"] for x in live}
        == {NATIVE + "/bw_emit.py", NATIVE + "/bw_transport.py"},
        "complete native inventory",
    )
    for directory, records in ((package, frozen), (root, live)):
        for record in records:
            path = directory / record["path"]
            require(
                path.resolve().is_relative_to(directory.resolve()), "contained source"
            )
            require(
                path.is_file() and path.stat().st_size <= 8_000_000, "bounded source"
            )
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                "source hash: " + record["path"],
            )
    return 6


def compile_word(word, work):
    require(not work.exists(), "fresh compiler workspace")
    work.mkdir()
    payload = canonical(word)
    require(
        (work / "WORD.json").write_bytes(payload) == len(payload), "complete word write"
    )
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPYCACHEPREFIX=str(work / "bytecode"),
    )
    for name in ("PYTHONOPTIMIZE", "PYTHONPATH"):
        env.pop(name, None)
    for name, arguments in (
        ("bw_transport.py", [work / "WORD.json", work / "native"]),
        ("bw_emit.py", [work / "native"]),
    ):
        with (work / (name + ".log")).open("w", encoding="utf-8") as log:
            subprocess.run(
                [
                    sys.executable,
                    "-W",
                    "error",
                    "-B",
                    str(ROOT / NATIVE / name),
                    *map(str, arguments),
                ],
                cwd=work,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=90,
            )
    return read(work / "native/LOCAL-PROGRAMS.json.gz"), read(
        work / "native/LOCAL-CHECKS.json"
    )
