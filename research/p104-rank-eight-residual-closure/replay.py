#!/usr/bin/env python3
"""Replay the retained #7363 source and its exact residual without Git or network."""

from argparse import ArgumentParser
from hashlib import sha256
from io import BytesIO
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PACKAGE = PurePosixPath("research/p104-rank-eight-fixed-paid-bank-bound")
SOURCE_SHA = "a7b02b2dab1f5de4b81566b3d04627f543c7cf1264491013aa887675a914f37d"
RESULT_SHA = "bd130ab860c7c605c47059d4a3e43852608acc2d31ffa7c9f80799b88600bc6e"


def check(data, expected):
    if sha256(data).hexdigest() != expected:
        raise ValueError("pinned SHA256 mismatch")
    return data


def extract(raw, dest):
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
        entries = archive.getmembers()
        seen = set()
        for entry in entries:
            path = PurePosixPath(entry.name)
            if (path in seen or path.is_absolute() or ".." in path.parts
                    or "\\" in entry.name or ":" in entry.name
                    or (not path.is_relative_to(PACKAGE)
                        and not (entry.isdir() and path in PACKAGE.parents))
                    or not (entry.isdir() or entry.isfile())):
                raise ValueError(f"unexpected retained source path: {entry.name}")
            seen.add(path)
        archive.extractall(dest, members=entries, filter="data")


def run(script, *args, timeout):
    subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                   check=True, timeout=timeout)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the full residual receipt to a new file")
    args = parser.parse_args()
    if not __debug__:
        parser.error("run with assertions enabled")
    raw = check((HERE / "predecessor.tar.gz").read_bytes(), SOURCE_SHA)
    try:
        check(raw[:-1] + bytes([raw[-1] ^ 1]), SOURCE_SHA)
    except ValueError:
        pass
    else:
        raise ValueError("changed source bundle accepted")
    with TemporaryDirectory(prefix="p104-rank-eight-residual-") as tmp:
        dest = Path(tmp)
        extract(raw, dest)
        source = dest / PACKAGE
        receipts, result = dest / "receipts", dest / "RESULT.json"
        run(source / "replay.py", "--output", receipts, timeout=90)
        run(HERE / "check_residual.py", "--source", source, "--receipts", receipts,
            "--out", result, timeout=75)
        data = check(result.read_bytes(), RESULT_SHA)
        if args.output:
            with args.output.open("xb") as out:
                out.write(data)
    print(f"PASS_P104_RANK_EIGHT_RESIDUAL_RECEIPT sha256={RESULT_SHA}")


if __name__ == "__main__":
    main()
