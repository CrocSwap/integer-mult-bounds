# SPDX-License-Identifier: Apache-2.0
"""Replay the frozen supplier using a fresh native-to-signed handoff."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
RECEIPTS = PACKAGE / "receipts"
CANDIDATE = "5ab1da9cae4ffb118ce79270108f879e50365c8adcb89d02d78158ffb0908d8c"


def read(path):
    return json.loads(path.read_bytes())


def require(condition, description):
    if not condition:
        raise ValueError(description)


def execute(script, *args):
    subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)], check=True)


def first_gate():
    old = PACKAGE / "sources/7647"
    with tempfile.TemporaryDirectory(prefix="croc-373-") as name:
        work = Path(name)
        execute(PACKAGE / "contact.py", "--source7644", old / "closure/pr7644",
                "--slice", old / "construction/gate.py", "--base7657", PACKAGE / "inputs/peer7657.json.gz",
                "--evidence7657", PACKAGE / "sources/7657/evidence", "--out", work)
        require(read(work / "GATE.json") == read(RECEIPTS / "GATE.json"), "exact first reads and directed charge bounds")
        raw = gzip.decompress((work / "candidate.json.gz").read_bytes())
        require(hashlib.sha256(raw).hexdigest() == CANDIDATE and
                raw == gzip.decompress((PACKAGE / "inputs/candidate.json.gz").read_bytes()), "frozen canonical word")
        historical = PACKAGE / "historical"
        reported = work / "historical.json"
        execute(historical / "compare.py", "--candidate", work / "candidate.json.gz",
                "--source7605", old / "closure/pr7644/retained/pr7605/data/word.json.gz",
                "--gate", work / "GATE.json", "--out", reported)
        require(read(reported) == read(historical / "RECEIPT.json"), "historic signed tariff and erasure distinction")
    print("PASS_COURIER_CONTACT_LOCAL_GATE", flush=True)


def replay_application(stage):
    # The registered driver is the same parent process for both commands.
    cookie = hashlib.sha256(f"{os.getuid()}/{os.getppid()}/{PACKAGE}".encode()).hexdigest()
    scratch = Path(tempfile.gettempdir()).resolve() / ("croc-373-courier-" + cookie)
    marker = scratch / "owner.json"
    identity = {"candidate": CANDIDATE, "package": str(PACKAGE)}
    app = PACKAGE / "application/check.py"
    args = ("--package", PACKAGE, "--work", scratch / "work")
    if stage == "native":
        scratch.mkdir(mode=0o700)
        with marker.open("x") as out:
            json.dump(identity, out)
        execute(app, "prepare", *args)
    else:
        info = scratch.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700,
                "owned native handoff directory")
        require(marker.is_file() and not marker.is_symlink() and read(marker) == identity,
                "matching native handoff")
    execute(app, stage, *args)
    work = scratch / "work"
    compare = [stage + "-science.json"]
    if stage == "signed":
        compare.extend(("DIRECTED-PRICE.json", "FINAL.json"))
    for name in compare:
        require(read(work / name) == read(RECEIPTS / name), "fresh signed or native evidence: " + name)
    if stage == "signed":
        measured = read(work / "signed-science.json")["price"]["after"]
        historical = read(PACKAGE / "historical/7612-invoice.json")
        require(measured["P"] == historical["paid"] and measured["T"] == historical["targets"],
                "all signed ranks equal to the published #7612 tariff")
        print(json.dumps(read(work / "FINAL.json"), sort_keys=True), flush=True)
        shutil.rmtree(scratch)
    print("PASS_COURIER_CONTACT_REGISTERED_" + stage.upper(), flush=True)


if __name__ == "__main__":
    require(__debug__ and sys.version_info[:2] == (3, 12), "CPython 3.12 with assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("gate", "native", "signed"))
    stage = parser.parse_args().stage
    if stage == "gate":
        first_gate()
    else:
        replay_application(stage)
