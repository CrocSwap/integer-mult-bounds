#!/usr/bin/env python3
"""Check one complete C5 space slice, including continuous normal planes."""

import argparse
import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from itertools import combinations
from pathlib import Path

from geometry import dot, echelon, label, normals, orthogonality_systems, require, roots

PACKAGE = Path(__file__).resolve().parent
FLAGS = [
    "-std=c++17",
    "-O3",
    "-mpopcnt",
    "-Wall",
    "-Wextra",
    "-Wpedantic",
    "-Wconversion",
    "-Wshadow",
    "-Werror",
]


def read_json(path: Path) -> dict:
    with path.open("rb") as stream:
        raw = stream.read(2 * 1024 * 1024 + 1)
    require(len(raw) <= 2 * 1024 * 1024, "JSON exceeds two MiB")
    value = json.loads(raw)
    require(isinstance(value, dict), "JSON must be an object")
    return value


def binary_span(basis: list[int]) -> set[int]:
    assert len(basis) <= 9 and all(0 <= x < 512 for x in basis)
    span = {0}
    for value in basis:
        span |= {x ^ value for x in span}
    return span


def binary_rank(values: list[int]) -> int:
    """Ascending pivots, unlike the scanner's descending-pivot algorithm."""
    assert len(values) <= 120 and all(0 <= x < 512 for x in values)
    basis = [0] * 9
    for value in values:
        for bit in range(9):
            if not value >> bit & 1:
                continue
            if basis[bit]:
                value ^= basis[bit]
            else:
                basis[bit] = value
                break
    return sum(bool(value) for value in basis)


def fixture_geometry(fixture: dict) -> tuple:
    require(fixture.get("schema") == "p112-common-slice/v1", "wrong fixture schema")
    frame = fixture.get("omitted_frame")
    require(isinstance(frame, list) and len(frame) == 8, "frame needs eight roots")
    require(all(isinstance(row, list) and len(row) == 8 for row in frame), "bad frame")
    require(all(type(x) is int for row in frame for x in row), "nonintegral frame")
    frame = {tuple(row) for row in frame}
    lines = roots()
    require(len(frame) == 8 and frame <= set(lines), "invalid frame roots")
    require(
        all(dot(a, b) == 0 for a, b in combinations(frame, 2)), "nonorthogonal frame"
    )
    basis = fixture.get("V1_basis")
    require(isinstance(basis, list) and len(basis) == 6, "basis needs six entries")
    require(all(type(x) is int and 0 < x < 512 for x in basis), "invalid basis entry")
    span = binary_span(basis)
    require(len(span) == 64, "dependent first basis")
    live_lines = tuple(row for row in lines if row not in frame)
    labels = [label(row) for row in live_lines]
    require(len(labels) == len(set(labels)) == 112, "invalid live labels")
    covered = sum(1 << i for i, value in enumerate(labels) if value in span)
    require(covered.bit_count() == 20, "first space needs twenty live lines")
    return lines, live_lines, labels, covered


def seven_flat_cap(labels: list[int]) -> dict:
    """Separate, exhaustive codimension-two cardinality control."""
    assert len(labels) == 112
    characters = [
        sum(1 << i for i, value in enumerate(labels) if (c & value).bit_count() % 2)
        for c in range(512)
    ]
    histogram = Counter()
    for a, b in combinations(range(1, 512), 2):
        if b >= a ^ b:
            continue
        histogram[112 - (characters[a] | characters[b]).bit_count()] += 1
    require(sum(histogram.values()) == 43435, "incomplete seven-flat enumeration")
    require(max(histogram) == 36, "seven-flat cardinality cap changed")
    return {"flats": sum(histogram.values()), "maximum_lines": max(histogram)}


def build_model(fixture: dict) -> tuple[str, dict]:
    lines, live_lines, labels, covered = fixture_geometry(fixture)
    live = sum(1 << i for i, row in enumerate(lines) if row in live_lines)
    systems, orbits = orthogonality_systems(lines, live)
    require(len(systems) == 5680, "incomplete parabolic inventory")
    text = [" ".join(map(str, labels)), f"{covered & ((1 << 64) - 1)} {covered >> 64}"]
    text.append(str(len(systems)))
    dimensions = Counter()
    for system in systems:
        basis = normals(lines, system)
        dimensions[len(basis)] += 1
        off = sum(
            1 << i
            for i, row in enumerate(live_lines)
            if any(dot(row, h) for h in basis)
        )
        text.append(f"{off & ((1 << 64) - 1)} {off >> 64} {len(basis)}")
        text.extend(" ".join(map(str, row)) for row in basis)
    require(dict(dimensions) == {1: 4560, 2: 1120}, "normal dimensions changed")
    model = "\n".join(text) + "\n"
    require(len(model) < 2 * 1024 * 1024, "model capacity exceeded")
    report = {
        "schema": "p112-common-slice-result/v1",
        "model_sha256": hashlib.sha256(model.encode()).hexdigest(),
        "V1_live_labels": sorted(
            value for i, value in enumerate(labels) if covered >> i & 1
        ),
        "seven_flat_cap": seven_flat_cap(labels),
        "parabolic_orbits": orbits,
        "normal_dimensions": {str(k): dimensions[k] for k in sorted(dimensions)},
    }
    return model, report


def compile_scanner(directory: Path, source: Path | None = None) -> Path:
    executable = directory / "scan"
    subprocess.run(
        ["g++", *FLAGS, str(source or PACKAGE / "scan.cpp"), "-o", str(executable)],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return executable


def check_case(fixture: dict, witness: dict) -> dict:
    """Independently interpret a scanner boundary and its rational rank."""
    _, live_lines, labels, covered = fixture_geometry(fixture)
    ann = witness["V2_annihilator"]
    require(isinstance(ann, list) and len(ann) == 3, "invalid annihilator shape")
    require(all(type(x) is int and 0 < x < 512 for x in ann), "invalid annihilator")
    require(len(binary_span(ann)) == 8, "dependent annihilator")
    second = {x for x in range(512) if all((x & a).bit_count() % 2 == 0 for a in ann)}
    require(len(second) == 64, "second space is not six-dimensional")
    deleted = witness["deleted_labels"]
    require(isinstance(deleted, list) and len(deleted) <= 4, "excess common deletions")
    require(all(type(x) is int for x in deleted), "invalid deleted label")
    require(
        len(set(deleted)) == len(deleted) and set(deleted) <= set(labels), "bad cut"
    )
    directions = witness["directions"]
    require(
        isinstance(directions, list) and 0 < len(directions) <= 120,
        "invalid direction count",
    )
    require(
        all(isinstance(row, list) and len(row) == 8 for row in directions),
        "bad direction",
    )
    require(
        all(type(x) is int and abs(x) <= 64 for row in directions for x in row),
        "bad entry",
    )
    ranks = []
    for direction in directions:
        residual = [
            value
            for i, (row, value) in enumerate(zip(live_lines, labels, strict=True))
            if dot(row, direction)
            and not covered >> i & 1
            and value not in second
            and value not in deleted
        ]
        ranks.append(binary_rank(residual))
    require(all(rank <= 7 for rank in ranks), "witness violates residual rank")
    rank = len(echelon(directions))
    require(
        type(witness.get("rank")) is int and witness["rank"] == rank,
        "false rational rank",
    )
    require(rank <= 4, "slice span exceeds four")
    return {"residual_ranks": ranks, "rational_span": rank}


def check_rank_trace(fixture: dict, result: dict) -> dict:
    trace = result.pop("rank_checks")
    require(isinstance(trace, list) and 0 < len(trace) <= 4096, "invalid rank trace")
    require(len(trace) == result["exact_rank_checks"], "rank trace is incomplete")
    largest_residual = 0
    for case in trace:
        checked = check_case(fixture, case)
        largest_residual = max(largest_residual, max(checked["residual_ranks"]))
    payload = json.dumps(trace, sort_keys=True, separators=(",", ":")).encode()
    return {
        "cases": len(trace),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "maximum_residual_rank": largest_residual,
    }


def verify(fixture: dict, directory: Path, expected: dict | None) -> dict:
    model, report = build_model(fixture)
    executable = compile_scanner(directory)
    control = subprocess.run(
        [str(executable), "--self-test"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    require(control.stdout == "PASS_SCAN_CONTROLS\n", "scanner controls failed")
    scan = subprocess.run(
        [str(executable)],
        input=model,
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    require(len(scan.stdout) < 2 * 1024 * 1024, "scanner result exceeds capacity")
    result = json.loads(scan.stdout)
    require(result["all_flats"] == 788035, "incomplete partner-space coverage")
    require(result["distinct_live_masks"] == 776806, "partner-mask coverage changed")
    require(result["maximum_common_span"] == 4, "common span bound changed")
    report["independent_rank_trace"] = check_rank_trace(fixture, result)
    report["scan"] = result
    report["independent_witness_check"] = check_case(fixture, result["witness"])
    require(report["independent_witness_check"]["rational_span"] == 4, "sharpness lost")
    if expected is not None:
        require(report == expected, "committed receipt or model changed")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=PACKAGE / "FIXTURE.json")
    parser.add_argument("--output", type=Path, help="write an external replay receipt")
    parser.add_argument("--expected", type=Path, default=PACKAGE / "RESULT.json")
    parser.add_argument(
        "--bootstrap", action="store_true", help="do not compare a prior receipt"
    )
    args = parser.parse_args()
    try:
        fixture = read_json(args.fixture)
        expected = None if args.bootstrap else read_json(args.expected)
        with tempfile.TemporaryDirectory(prefix="p112-slice-") as temporary:
            report = verify(fixture, Path(temporary), expected)
        if args.output is not None:
            args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(
            "PASS_P112_COMMON_SLICE flats=788035 masks=776806 systems=5680 common_span=4"
        )
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        subprocess.SubprocessError,
    ) as error:
        diagnostic = getattr(error, "stderr", None) or str(error)
        parser.exit(2, f"FAIL: {diagnostic}\n")


if __name__ == "__main__":
    main()
