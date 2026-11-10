#!/usr/bin/env python3
"""Verify the new record codec, produced by Nick Petalas. Apache-2.0."""

import argparse
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codec

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ("research/kappa-0023-productive-jobs/dependencies/"
          "kappa-next-regime/direct-decoder/sources/DATA-PHASES.json")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def expect_rejection(function, value):
    try:
        function(value)
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            need(digest == row["sha256"], "source bytes differ: " + row["path"])
            hashes[row["path"]] = digest
    return hashes


def independent_columns():
    count = 0
    for width in range(1, 4):
        for length in range(6):
            for rows in product(range(1 << width), repeat=length):
                counts = [sum((row >> i) & 1 for row in rows) for i in range(width)]
                expected = tuple(sum(((c >> b) & 1) << i for i, c in enumerate(counts))
                                 for b in range(2))
                need(codec.column_tag(list(rows), width) == expected, "bit-plane oracle differs")
                count += 1
    # The high bit must read the OLD low bit. This fixture distinguishes order.
    need(codec.column_tag([1, 1, 1], 1) == (1, 1), "three-row carry fixture")
    for width in (9, 73, 128, 256):
        rows = [(1 << width) - 1] * 129
        need(codec.column_tag(rows, width) == ((1 << width) - 1, 0), "capacity fixture")
    return count, 4


def check_complete_document(document):
    original = deepcopy(document)
    compact = codec.encode(document)
    need(document == original, "encoder mutated its input")
    restored = codec.decode(compact)
    need(restored == document, "complete metadata round trip differs")
    records = list(codec.events(compact))
    expected = [(rec["port"], i, child) for rec in document["recipes"]
                for i, child in enumerate(rec["idle_children"])]
    need(records == expected, "legacy consumer records differ")
    need(codec.encode(restored) == compact, "canonical encoding is not stable")
    removed = sum("translation_after" in child for rec in document["recipes"]
                  for child in rec["idle_children"])
    need(all("translation_after" not in child for rec in compact["payload"]["recipes"]
             for child in rec["idle_children"]), "a stored translation remains")
    before, after = len(codec.canonical(document)), len(codec.canonical(compact))
    need(after < before, "new representation does not reduce bytes")
    need((before, after, removed) == (814140, 763803, 2240),
         "published finite construction counts differ")
    return compact, {"recipes": len(document["recipes"]), "consumer_records": len(records),
                     "removed_translation_fields": removed, "canonical_source_bytes": before,
                     "canonical_encoded_bytes": after, "saved_bytes": before - after,
                     "original_canonical_sha256": compact["original_sha256"],
                     "encoded_sha256": hashlib.sha256(codec.canonical(compact)).hexdigest()}


def check_rejections(document, compact):
    changed = deepcopy(document)
    changed["recipes"][0]["idle_children"][0]["translation_after"] ^= 1
    expect_rejection(codec.encode, changed)
    changes = [deepcopy(compact) for _ in range(8)]
    changes[0]["schema"] = "unsupported"
    changes[1]["original_sha256"] = "0" * 64
    changes[2]["payload"]["recipes"][0]["idle_children"][0]["translation_after"] = 15
    changes[3]["payload"]["recipes"][0]["idle_children"][0]["orthogonal_axes"][0] = 0
    changes[4]["payload"]["recipes"][0]["idle_children"][0]["rank"] += 1
    changes[5]["payload"]["recipes"][0]["q"] = 1
    changes[6]["payload"]["recipes"][0]["stage_alignment"][1]["entry_X"] ^= 1
    changes[7]["payload"]["recipes"].reverse()
    for change in changes:
        expect_rejection(codec.decode, change)
    for raw in (b'{"m":73,"m":73}', b" " * (codec.MAX_BYTES + 1)):
        expect_rejection(codec.parse, raw)
    bad_rows = [([-1], 9), ([1 << 256], 256), ([0] * 130, 1), ([True], 1)]
    for rows, width in bad_rows:
        try:
            codec.column_tag(rows, width)
        except ValueError:
            continue
        raise ValueError("row boundary control was accepted")
    for axes in ([3], [1, 1], [1, 2]):
        try:
            codec.translation(axes, 11, 73)
        except ValueError:
            continue
        raise ValueError("incomplete or nonorthogonal frame was accepted")
    return 18


def run_cli(directory, operation, name):
    result = subprocess.run([sys.executable, "-I", "-W", "error", "-O", "-B",
                             str(HERE / "codec.py"), operation, str(directory / name)],
                            capture_output=True, timeout=30, check=False)
    return result


def check_cli(document, compact):
    with tempfile.TemporaryDirectory(prefix="derived-phase-codec-") as name:
        directory = Path(name)
        (directory / "source.json").write_bytes(codec.canonical(document))
        (directory / "compact.json").write_bytes(codec.canonical(compact))
        for operation, filename, expected in (
                ("encode", "source.json", codec.canonical(compact) + b"\n"),
                ("decode", "compact.json", codec.canonical(document) + b"\n"),
                ("events", "compact.json", b"".join(codec.canonical(event) + b"\n"
                                                   for event in codec.events(compact)))):
            result = run_cli(directory, operation, filename)
            need(result.returncode == 0 and not result.stderr and result.stdout == expected,
                 "actual CLI output differs: " + operation)
        (directory / "bad.json").write_bytes(b'{"schema":"bad"}')
        result = run_cli(directory, "decode", "bad.json")
        need(result.returncode == 2 and not result.stdout and result.stderr,
             "actual CLI did not reject before output")
    return 3, 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path,
                        help="place all temporary CLI files in this existing directory")
    args = parser.parse_args()
    if args.scratch:
        need(args.scratch.is_dir(), "scratch directory does not exist")
        tempfile.tempdir = str(args.scratch)
    sources = authenticate()
    document = codec.parse((ROOT / SOURCE).read_bytes())
    core, capacities = independent_columns()
    compact, result = check_complete_document(document)
    result["api_rejection_controls"] = check_rejections(document, compact)
    result["successful_cli_commands"], result["cli_rejection_controls"] = check_cli(document, compact)
    result["bit_plane_oracle_cases"] = core
    result["capacity_cases"] = capacities
    result["source_sha256"] = sources
    result["package_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps({"status": "PASS_DERIVED_PHASE_STREAM", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
