#!/usr/bin/env python3
"""Opt-in xor-scatter-v1 boundary. Nick Petalas. Apache-2.0."""

import argparse
import gzip
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCHEMA = "xor-scatter-v1"
MAX_BYTES = 5 * 1024 * 1024
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, compressed=False):
    require(path.stat().st_size <= MAX_BYTES, "input exceeds 5 MiB")
    opener = gzip.open if compressed else open
    with opener(path, "rb") as stream:
        body = stream.read(MAX_BYTES + 1)
    require(len(body) <= MAX_BYTES, "input exceeds 5 MiB")
    return body


def normalize(word):
    """Validate the scatter boundary, then return a nonmutating parity normal form."""
    require(type(word) is dict, "word must be an object")
    v, helpers = word.get("v"), word.get("R")
    require(type(v) is int and 1 <= v <= 256, "v outside 1..256")
    require(type(helpers) is int and 0 <= helpers <= 4096, "R outside 0..4096")
    retained, rows = word.get("ret"), word.get("scatter")
    require(
        type(retained) is list and len(retained) <= 256,
        "ret must have at most 256 slots",
    )
    require(
        all(type(q) is int and 2 * v <= q < 2 * v + helpers for q in retained),
        "ret must contain helper registers",
    )
    require(type(rows) is list and len(rows) == v, "scatter must have v rows")
    normalized, total = [], 0
    for row in rows:
        require(type(row) is list and len(row) <= 4096, "row exceeds 4096 occurrences")
        total += len(row)
        require(total <= 65536, "scatter exceeds 65536 occurrences")
        parity = set()
        for slot in row:
            require(
                type(slot) is int and 0 <= slot < len(retained), "invalid scatter slot"
            )
            parity.symmetric_difference_update((slot,))
        normalized.append(sorted(parity))
    return {**word, "scatter": normalized}, total


def scripts(root):
    pins = json.loads(read_bounded(PACKAGE / "SOURCES.json"))["files"]
    require(len(pins) <= 16, "source inventory exceeds 16")
    result = {}
    for path in (CHECKER, EXPORTER):
        matches = [
            row for row in pins if row["path"] == path and row["usage"] == "input"
        ]
        require(len(matches) == 1, "missing or duplicate source pin: " + path)
        body = read_bounded(root / path)
        require(
            hashlib.sha256(body).hexdigest() == matches[0]["sha256"],
            "source pin: " + path,
        )
        result[path] = body
    return result


def delegate(body, word_path, directory, name, output=None):
    script = directory / name
    script.write_bytes(body)
    command = [sys.executable, "-I", "-B", str(script), str(word_path)]
    if output is not None:
        command.append(str(output))
    run = subprocess.run(command, capture_output=True, timeout=60, check=False)
    require(
        run.returncode == 0,
        name + " rejected: " + run.stderr[-2000:].decode(errors="replace"),
    )


def inspect_export(output, expected_terms, retained_count):
    require(
        sorted(p.name for p in output.iterdir()) == sorted(ARTIFACTS),
        "export inventory",
    )
    blobs = {name: read_bounded(output / name) for name in ARTIFACTS}
    raw = blobs["249-records.bin"]
    require(len(raw) % 24 == 0 and len(raw) <= 100000 * 24, "bounded aligned records")
    records = list(struct.iter_unpack("<6i", raw))
    scatter = sum(event[0] == 1 and event[5] == 3 for event in records)
    require(
        scatter == expected_terms, "emitted scatter invoice differs from normal form"
    )
    require(sum(event[0] == 2 for event in records) == retained_count, "COPY count")
    require(sum(event[0] == 3 for event in records) == retained_count, "ERASE count")
    return {
        "records": len(records),
        "scatter_adds": scatter,
        "copy_erase_pairs": retained_count,
        "sha256": {
            name: hashlib.sha256(body).hexdigest() for name, body in blobs.items()
        },
    }


def execute(mode, input_path, output=None, root=ROOT, scratch=None):
    require(mode in ("check", "export"), "unknown mode")
    require(
        (mode == "export") == (output is not None),
        "export needs output; check takes none",
    )
    if output is not None:
        require(
            not output.exists() and not output.is_symlink(), "output already exists"
        )
    raw = read_bounded(input_path, input_path.suffix == ".gz")
    normalized, occurrences = normalize(json.loads(raw))
    bodies = scripts(root)
    terms = sum(map(len, normalized["scatter"]))
    result = {
        "schema": SCHEMA,
        "input_occurrences": occurrences,
        "normalized_scatter_terms": terms,
    }
    with tempfile.TemporaryDirectory(prefix="xor-scatter-", dir=scratch) as temporary:
        directory = Path(temporary)
        snapshot = directory / "word.json.gz"
        snapshot.write_bytes(gzip.compress(json.dumps(normalized).encode(), mtime=0))
        delegate(bodies[CHECKER], snapshot, directory, "checker.py")
        if output is not None:
            staging = directory / "export"
            delegate(bodies[EXPORTER], snapshot, directory, "exporter.py", staging)
            result["export"] = inspect_export(staging, terms, len(normalized["ret"]))
            shutil.copytree(staging, output)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "export"))
    parser.add_argument("word", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--scratch", type=Path)
    args = parser.parse_args()
    try:
        result = execute(args.mode, args.word, args.output, scratch=args.scratch)
    except (ValueError, OSError, RecursionError, subprocess.TimeoutExpired) as error:
        print(f"REJECT {SCHEMA}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
