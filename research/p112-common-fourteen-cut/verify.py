#!/usr/bin/env python3
"""Reproduce the common-fourteen-cut P112 span bound without checkout writes."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

import geometry

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
FLAGS = (
    "-std=c++17",
    "-O3",
    "-mpopcnt",
    "-Wall",
    "-Wextra",
    "-Wpedantic",
    "-Wconversion",
    "-Wshadow",
    "-Werror",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.stat().st_size <= 2_000_000, f"JSON capacity exceeded: {path}")
    return json.loads(path.read_text())


def check_sources(root=ROOT, package=PACKAGE):
    sources = read_json(package / "SOURCES.json")
    hashes = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.stat().st_size <= 2_000_000, "source capacity exceeded")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], f"changed live input: {row['path']}")
        hashes[row["path"]] = digest
    for row in sources["upstream"]:
        path = package / row["local_path"]
        require(path.stat().st_size <= 100_000, "vendor capacity exceeded")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(
            digest == row["sha256"], f"changed retained source: {row['local_path']}"
        )
        hashes[row["local_path"]] = digest
    return hashes


def prepare_fixture(output, root=ROOT):
    data = root / "research/one-sided-six-multisets/data/data.txt"
    generators = root / "research/one-sided-six-multisets/data/gens.txt"
    text, coverage = geometry.fixture(data, generators)
    require(coverage["retained"] == 1144, "direction inventory changed")
    fixture = output / "fixture.txt"
    fixture.write_text(text)
    return (
        fixture,
        json.loads(json.dumps(coverage)),
        hashlib.sha256(text.encode()).hexdigest(),
    )


def run_command(argv, timeout, output, name):
    with (
        (output / f"{name}.stdout").open("w") as stdout,
        (output / f"{name}.stderr").open("w") as stderr,
    ):
        process = subprocess.run(
            argv,
            stdout=stdout,
            stderr=stderr,
            timeout=timeout,
            check=False,
        )
    require(
        process.returncode == 0, f"{name} failed, see {output / (name + '.stderr')}"
    )
    return (output / f"{name}.stdout").read_text()


def compile_census(output):
    executable = output / "census"
    compiler = os.environ.get("CXX", "g++")
    run_command(
        [compiler, *FLAGS, str(PACKAGE / "census.cpp"), "-o", str(executable)],
        60,
        output,
        "compile",
    )
    controls = run_command([str(executable), "--self-test"], 45, output, "controls")
    require(controls == "PASS_COMMON_CUT_CONTROLS\n", "incomplete native controls")
    return executable


def rational_rank(rows):
    require(len(rows) <= 9 and all(len(row) == 8 for row in rows), "rank-control shape")
    basis = {}
    for original in rows:
        row = list(map(Fraction, original))
        for pivot, old in sorted(basis.items()):
            factor = row[pivot]
            row = [x - factor * y for x, y in zip(row, old, strict=True)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [x / scale for x in row]
    return len(basis)


def check_rank_controls(text, directions):
    lines = text.splitlines()
    require(len(lines) == 96, "incomplete rational-rank controls")
    for i, line in enumerate(lines):
        fields = line.split()
        require(fields and fields[0] == "RANK", "invalid rank-control record")
        values = list(map(int, fields[1:]))
        require(len(values) >= 3 and values[:2] == [i, i % 10], "rank-control identity")
        ids, actual = values[2:-1], values[-1]
        require(
            len(ids) == i % 10 and all(0 <= d < 1144 for d in ids), "rank-control ids"
        )
        expected = min(6, rational_rank([directions[d] for d in ids]))
        require(actual == expected, "native rational rank disagrees with Fraction")


def parse_rows(text, start, length):
    lines = text.splitlines()
    require(len(lines) == length + 1, "incomplete census output")
    require(lines[-1] == f"PASS_COMMON_FOURTEEN {start} {length}", "missing completion")
    rows = []
    for i, line in enumerate(lines[:-1]):
        fields = line.split()
        require(len(fields) == 11 and fields[0] == "ROW", "invalid census row")
        values = list(map(int, fields[1:]))
        require(values[0] == start + i, "missing, duplicate or reordered orbit")
        require(all(value >= 0 for value in values), "negative census counter")
        require(
            values[1] < 776806 and values[2] <= 20 and values[3] <= 32,
            "invalid orbit identity",
        )
        require(
            values[4] <= 776806 and values[8] <= 262144 and values[9] <= 65536,
            "census resource bound exceeded",
        )
        rows.append(values)
    return rows


def check_receipt(actual, expected, start, length):
    require(expected["schema"] == "p112-common-fourteen-cut/v1", "receipt schema")
    require(len(expected["rows"]) == 160, "incomplete expected orbit inventory")
    require(
        [row[0] for row in expected["rows"]] == list(range(160)),
        "invalid expected orbit identities",
    )
    for key in ("schema", "input_sha256", "fixture_sha256", "coverage", "application"):
        require(actual[key] == expected[key], f"receipt mismatch: {key}")
    require(
        actual["rows"] == expected["rows"][start : start + length],
        "census differs from committed receipt",
    )


def application_check():
    """Independent arithmetic for the one original TWOSIDE caller."""
    profile = (2, 3, 4) + (6,) * 8
    caps = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
    minimum = (0, 53, 78, 92, 100, 106, 109)
    prefixes = [sum(caps[w] for w in profile[: 5 + level]) for level in range(1, 7)]
    require(prefixes == [74, 94, 114, 134, 154, 174], "TWOSIDE prefix capacities")
    require(
        all(prefixes[level - 1] >= minimum[level] for level in range(1, 7)),
        "profile fails original support filters",
    )
    excess = sum(w - 2 for w in profile)
    require(excess == 35 and excess < 36, "profile excess")
    basis = profile[:5]
    require(sum(caps[w] for w in basis) == 54, "old cardinality gate changed")
    require(
        basis == (2, 3, 4, 6, 6) and sum(caps[w] for w in basis[:3]) == 14,
        "two-six-flat/common-fourteen cover",
    )
    require(
        len(profile[5:]) == 6 and set(profile[5:]) == {6}, "nonbasis rank-six count"
    )
    return {
        "profile": profile,
        "basis": basis,
        "common_cut_cap": 14,
        "required_span": 6,
    }


def reproduce(output, part, record=None):
    hashes = check_sources()
    application = application_check()
    original = run_command(
        [sys.executable, "-B", str(PACKAGE / "vendor/bk2b.py")],
        60,
        output,
        "original-cells",
    )
    original_rows = [list(map(int, line.split())) for line in original.splitlines()]
    require(
        len(original_rows) == 24 and [6, 5, 174, 1] in original_rows,
        "original TWOSIDE cell control changed",
    )
    fixture, coverage, fixture_hash = prepare_fixture(output)
    executable = compile_census(output)
    rank_text = run_command(
        [str(executable), "--rank-controls", str(fixture)],
        15,
        output,
        "rank-controls",
    )
    directions, _ = geometry.direction_catalogue()
    check_rank_controls(rank_text, directions)
    start, length = (0, 160) if part is None else (part * 80, 80)
    rows = []
    # Two independently complete ranges keep the registered commands bounded.
    for offset in range(start, start + length, 80):
        text = run_command(
            [str(executable), str(fixture), str(offset), "80"],
            500,
            output,
            f"scan-{offset}",
        )
        rows.extend(parse_rows(text, offset, 80))
    result = {
        "schema": "p112-common-fourteen-cut/v1",
        "input_sha256": hashes,
        "fixture_sha256": fixture_hash,
        "coverage": coverage,
        "application": json.loads(json.dumps(application)),
        "rows": rows,
    }
    if record is not None:
        require(part is None, "recording requires the complete 160-orbit run")
        record.write_text(json.dumps(result, indent=2) + "\n")
    else:
        check_receipt(result, read_json(PACKAGE / "RESULT.json"), start, length)
    print(f"PASS_P112_COMMON_FOURTEEN_CUT orbits={start}..{start + length - 1} span<=5")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--part", type=int, choices=(0, 1))
    parser.add_argument(
        "--record", type=Path, help="write a full fresh receipt outside the checkout"
    )
    args = parser.parse_args()
    if args.record:
        require(
            not args.record.resolve().is_relative_to(ROOT), "record must be external"
        )
    if args.output_dir:
        output = args.output_dir.resolve()
        require(not output.is_relative_to(ROOT), "output directory must be external")
        output.mkdir(parents=True, exist_ok=True)
        reproduce(output, args.part, args.record)
    else:
        with tempfile.TemporaryDirectory(prefix="p112-common-fourteen-") as temporary:
            reproduce(Path(temporary), args.part, args.record)


if __name__ == "__main__":
    main()
