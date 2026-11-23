"""Restore floration's pinned word, then install the eta-lift ordinary recipe."""

import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE / "parent8088"
SOURCE = "06691302af526a488f3dee0298035f86b6e69c51"
PIN_SHA = "93c5ea20bbc6497a461ac6d2a8f69770b927c2d67eb991c57da2e9f8a3e8f5e6"
ORDINARY = (8192, 106000, 1681001)
GAUSSIAN = 85406


def digest(data):
    return hashlib.sha256(data).hexdigest()


def replace_pinned(path, before, text, replacement):
    data = path.read_bytes()
    if digest(data) != before or data.count(text) != 1:
        raise ValueError(
            "Candidate patch does not match its authenticated source: " + path.name
        )
    path.write_bytes(data.replace(text, replacement))


def build(tree):
    if not __debug__:
        raise RuntimeError("Use Python with assertions enabled")
    source = (HERE / "SOURCE8088.json").read_bytes()
    if digest(source) != PIN_SHA:
        raise ValueError("Unexpected #8088 source record")
    pins = json.loads(source)
    assert pins["commit"] == SOURCE
    for name, expected in pins["files"].items():
        data = (PARENT / name).read_bytes()
        git_blob = hashlib.sha1(
            b"blob " + str(len(data)).encode() + b"\0" + data
        ).hexdigest()
        if digest(data) != expected["sha256"] or git_blob != expected["git_blob"]:
            raise ValueError("Unexpected #8088 input: " + name)
    tree = Path(tree).resolve()
    tree.mkdir(parents=True, exist_ok=True)
    if any(tree.iterdir()):
        raise ValueError("Use a new empty installation directory")
    peer = runpy.run_path(str(PARENT / "verify.py"))["restore"](tree)
    runpy.run_path(str(PARENT / "prepare.py"))["materialize"](peer)
    for name in ("check_stage_seam.py", "check_cutoff.py", "check_ordinary_floor.py"):
        (peer / name).write_bytes((PARENT / name).read_bytes())
    runtime = tree / "runtime"
    subprocess.run([sys.executable, "-IB", peer / "bootstrap.py", runtime], check=True)
    replace_pinned(
        runtime / "installations.py",
        "cb93c268fca5a8051381018845907df2dca64083c58cfa27f1a1528a4e7d5c26",
        b'TERMINAL = Profile((62186, 986008, 1048575), 66037, Q(".003899574328473"))',
        b"TERMINAL = Profile((8192, 106000, 1681001), 85406, Q(39, 10000), eta=Q(1, 256))",
    )
    replace_pinned(
        runtime / "raw_binary_stage.py",
        "8020d33828233e7016700849a507a8cee78db8a17a33b6063b737313ea05b07f",
        b"level_floor=4474",
        b"level_floor=18960",
    )
    return peer, runtime


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    params = parser.parse_args()
    peer, runtime = build(params.destination)
    print(
        "PASS_PINNED_TARGET_INSTALLATION",
        digest((runtime / "installations.py").read_bytes()),
    )
