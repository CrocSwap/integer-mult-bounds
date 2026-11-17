# SPDX-License-Identifier: Apache-2.0
"""Run the exact composition checks with a fresh native-to-signed handoff."""
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

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "closure" / "pr7644"
RECEIPTS = HERE / "receipts"
WORD = HERE / "inputs" / "combined.json.gz"


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def require(test, description):
    if not test:
        raise ValueError(description)


def execute(script, *args, isolated=True):
    flags = ["-I", "-B"] if isolated else ["-B"]
    subprocess.run([sys.executable, *flags, str(script), *map(str, args)], check=True)


def rows():
    with tempfile.TemporaryDirectory(prefix="croc-composition-rows-") as directory:
        work = Path(directory)
        for name in ("gate.py", "full_gate.py"):
            shutil.copyfile(HERE / "construction" / name, work / name)
        args = ["--inputs", HERE / "inputs", "--source7644", SOURCE,
                "--contact-check", HERE / "closure" / "contact_phase.py"]
        for stage in ("first", "full"):
            execute(work / "gate.py", stage, *args)
        require(read(work / "candidate.json.gz") == read(WORD), "regenerated literal word")
        require(read(work / "clock-map.json") == read(RECEIPTS / "clock-map.json"), "all event origins and clock shifts")
        require(read(work / "first-provenance.json.gz") == read(RECEIPTS / "first-provenance.json.gz"), "complete operand provenance")
        for filename, observations in (("first-receipt.json", ("provenance_sha256",)),
                                       ("full-receipt.json", ("gzip_sha256", "first_provenance_sha256"))):
            fresh, sealed = read(work / filename), read(RECEIPTS / filename)
            for key in observations:
                fresh.pop(key)
                sealed.pop(key)
            require(fresh == sealed, filename)
    print("PASS_COMPOSITION_LITERAL_OBSERVATIONS", flush=True)


def registered_work():
    # Both registered commands are owned by the same research_package.py process.
    # The native command reserves a new private directory and signed consumes it.
    identity = f"{os.getuid()}/{os.getppid()}/{HERE}"
    key = hashlib.sha256(identity.encode()).hexdigest()
    return Path(tempfile.gettempdir()).resolve() / ("croc-conditional-composition-" + key)


def compare_science(stage, output):
    fresh = read(output)
    expected = read(RECEIPTS / (stage + "-science.json"))
    require({key: fresh[key] for key in expected} == expected, stage + " scientific receipt")


def application(stage, scratch, keep):
    engine = HERE / "application" / "run.py"
    root = scratch / "run"
    args = ("--source", SOURCE, "--work", root)
    marker = scratch / ".composition-owner.json"
    identity = {"package": str(HERE), "word": hashlib.sha256(WORD.read_bytes()).hexdigest()}
    if stage == "native":
        scratch.mkdir(mode=0o700)
        with marker.open("x") as stream:
            json.dump(identity, stream)
        print("Application scratch", scratch, flush=True)
        execute(engine, "prepare", *args, "--word", WORD)
        execute(HERE / "application" / "peer_compare.py", *args, "--out", root / "PEER-7645.json")
        require(read(root / "PEER-7645.json") == read(RECEIPTS / "PEER-7645.json"), "directed comparison with #7645")
        execute(engine, "native", *args)
        require(read(root / "native-exit.json")["exit"] == 0, "fresh native stage")
        compare_science("native", root / "producer54/validation_native/NATIVE-RESULT.json")
        return
    info = scratch.lstat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid()
            and stat.S_IMODE(info.st_mode) == 0o700, "private native handoff ownership")
    require(marker.is_file() and not marker.is_symlink() and read(marker) == identity, "matching native scratch marker")
    execute(engine, "signed", *args)
    compare_science("signed", root / "producer54/validation_signed/RESULT.json")
    execute(HERE / "application" / "independent_bill.py", *args, "--out", root / "INDEPENDENT-BILLS.json")
    for name in ("FINAL.json", "DIRECTED-PRICE.json", "DIRECTED-CROSSING.json", "INDEPENDENT-BILLS.json"):
        require(read(root / name) == read(RECEIPTS / name), "fresh " + name)
    print(json.dumps(read(root / "FINAL.json"), sort_keys=True), flush=True)
    if not keep:
        shutil.rmtree(scratch)
    print("PASS_COMPOSITION_FRESH_COMPLETE_APPLICATION", flush=True)


if __name__ == "__main__":
    require(sys.version_info[:2] == (3, 12) and __debug__, "CPython 3.12 with assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("rows", "native", "signed"))
    parser.add_argument("--scratch", type=Path, help="fresh directory shared by native and signed")
    args = parser.parse_args()
    if args.stage == "rows":
        rows()
    else:
        application(args.stage, args.scratch.resolve() if args.scratch else registered_work(), args.scratch is not None)
