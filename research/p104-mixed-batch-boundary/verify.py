#!/usr/bin/env python3
"""Replay a deposited result in a temporary directory and compare its complete JSON."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "pr7756"
SCRIPTS = HERE.parents[1] / "scripts"


def verify_source_files():
    manifest = json.loads((HERE / "PR7756-SOURCES.json").read_bytes())
    for row in manifest["files"]:
        data = (SOURCE / row["path"]).read_bytes()
        header = b"blob " + str(len(data)).encode("ascii") + b"\0"
        if (hashlib.sha256(data).hexdigest() != row["sha256"]
                or hashlib.sha1(header + data).hexdigest() != row["git_blob"]):
            raise ValueError("changed upstream source " + row["path"])


def replay(check, output):
    command = [sys.executable, "-I", "-B"]
    if check == "price":
        command += [str(HERE / "verify_price.py"), "--source", str(SOURCE), "--scripts", str(SCRIPTS)]
    elif check == "seam":
        command += [str(HERE / "verify_seam.py"), "--source", str(SOURCE)]
    else:
        command += [str(HERE / "qualify.py"), "--check", check, "--source", str(SOURCE),
                    "--scripts", str(SCRIPTS), "--price", str(HERE / "PRICE.json")]
    subprocess.run([*command, "--output", str(output)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=("price", "seam", "application", "expansion", "probe"))
    args = parser.parse_args()
    verify_source_files()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "receipt.json"
        replay(args.check, output)
        actual = json.loads(output.read_bytes())
        expected = json.loads((HERE / "evidence" / (args.check + ".json")).read_bytes())
        if actual != expected:
            raise ValueError("replay differs from the deposited " + args.check + " receipt")
    print("PASS_P104_BATCH_BOUNDARY", args.check)


if __name__ == "__main__":
    main()
