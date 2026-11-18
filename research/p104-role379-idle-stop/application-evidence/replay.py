#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Prepare the frozen #7658 word and run optional Linux application checks."""

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import resource
import runpy
import signal
import subprocess
import sys
import tempfile
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
CANDIDATE = "f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669"
SOURCE = "fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6"
NATIVE = HERE / "native-replay"
RESOURCES = HERE / "resource-replay"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, pin=None):
    data = path.read_bytes()
    require(pin is None or sha(data) == pin, f"SHA-256 mismatch for {path.name}")
    return data


def core_candidate(args):
    core = runpy.run_path(str(args.core.resolve() / "verify.py"))
    work = args.out.resolve()
    work.mkdir(exist_ok=False)
    path, raw, transport = core["run_mutation"](
        7658, work, args.core.resolve() / "evidence/pr7658", core["pinned_sources"]()
    )
    require(raw == CANDIDATE, "unexpected #7658 candidate")
    print(json.dumps({"word": str(path), "raw_sha256": raw, "gzip_sha256": transport}))


def unpack_native(destination):
    origins = json.loads(read(HERE / "SOURCE-INPUTS.json"))
    pins = origins["native_archive_members"]
    with ZipFile(NATIVE / "predecessor-pairs.zip") as archive:
        require(sorted(archive.namelist()) == sorted(pins), "unexpected predecessor archive entries")
        for name, pin in pins.items():
            path = PurePosixPath(name)
            require(not path.is_absolute() and ".." not in path.parts and path.as_posix() == name,
                    "invalid archive member path")
            info = archive.getinfo(name)
            require(info.file_size == pin["bytes"], f"archive size for {name}")
            data = archive.read(info)
            require(sha(data) == pin["sha256"], f"archive pin for {name}")
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(data)


def native_application(args):
    core_parent = args.core.resolve() / "retained/pr7658"
    candidate = args.candidate.resolve()
    raw = read(candidate)
    require(sha(gzip.decompress(raw)) == CANDIDATE, "unexpected #7658 candidate")
    available = sorted(os.sched_getaffinity(0))
    cpus = args.cpus if args.cpus else available[:2]
    require(len(cpus) in (1, 2) and len(set(cpus)) == len(cpus) and set(cpus) <= set(available),
            "choose one or two available Linux CPUs")
    with tempfile.TemporaryDirectory(prefix="role379-prior-pairs-") as directory:
        prior = Path(directory)
        unpack_native(prior)
        subprocess.run(
            [
                "bash", str(NATIVE / "run_guarded.sh"), str(args.out.resolve()),
                str(args.wall), ",".join(map(str, cpus)), "offline-reviewer",
                "--pr", "7658", "--source", str(core_parent / "data/word.json.gz"),
                "--candidate", str(candidate), "--candidate-gzip", sha(raw),
                "--candidate-raw", CANDIDATE, "--engine", str(core_parent / "check.py"),
                "--prior-engine", str(prior / "phase-check.py"),
                "--prior-word", str(prior / "repair-word.json.gz"),
                "--prior-receipts", str(prior / "pairs"), "--workers", str(len(cpus)),
            ],
            check=True,
        )


def resource_application(args):
    stage = runpy.run_path(str(RESOURCES / "preflight.py"))
    run = stage[args.stage]
    path = args.word.resolve()
    pin = dict(stage["WORDS"]["7658-b" if args.case == "candidate" else "7658"], path=path)
    packed = read(path)
    expected = CANDIDATE if args.case == "candidate" else SOURCE
    require(sha(gzip.decompress(packed)) == expected, "unexpected resource word")
    # The core's decoded candidate is deterministic across supported compressors.
    if args.case == "candidate":
        pin["gzip_sha256"] = sha(packed)
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    engines = RESOURCES / "engines"
    vendor = engines / "vendor"
    for name, digest in stage["SOURCE_PINS"].items():
        read(engines / name, digest)
    run.__globals__.update(RESOURCES=engines, VENDOR=vendor, ACTIVE_OUT=out)
    cpu, wall = (20, 30) if args.stage == "quick" else (180, 205)
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
    signal.alarm(wall)
    try:
        if args.stage == "quick":
            run(pin, 225)
        else:
            run(pin, cpu, wall)
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(required=True)
    build = sub.add_parser("candidate", help="rebuild the core #7658 word and price")
    build.add_argument("--core", required=True, type=Path)
    build.add_argument("--out", required=True, type=Path)
    build.set_defaults(run=core_candidate)
    native = sub.add_parser("native", help="replay the matched finite native application")
    native.add_argument("--core", required=True, type=Path)
    native.add_argument("--candidate", required=True, type=Path)
    native.add_argument("--out", required=True, type=Path)
    native.add_argument("--cpus", type=int, nargs="+")
    native.add_argument("--wall", type=int, default=1104)
    native.set_defaults(run=native_application)
    app = sub.add_parser("resource", help="replay the grid or ordinary and scalar counts")
    app.add_argument("--case", choices=("source", "candidate"), required=True)
    app.add_argument("--stage", choices=("quick", "grid"), required=True)
    app.add_argument("--word", required=True, type=Path)
    app.add_argument("--out", required=True, type=Path)
    app.set_defaults(run=resource_application)
    args = parser.parse_args()
    require(sys.version_info[:2] == (3, 12) and __debug__, "use Python 3.12 without -O")
    runpy.run_path(str(HERE / "check.py"))["check_custody"]()
    args.run(args)


if __name__ == "__main__":
    main()
