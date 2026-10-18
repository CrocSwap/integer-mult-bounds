#!/usr/bin/env python3
"""Reproduce the complete bounded P112 rank-six census and mixed-rank reduction."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 12):
    raise SystemExit("Python 3.12 or later is required")

from geometry import exact_label, fixture, frame_lines, root_lines
from survivors import remaining_shapes

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
FLAGS = (
    "-std=c++17",
    "-O3",
    "-Wall",
    "-Wextra",
    "-Wpedantic",
    "-Wconversion",
    "-Wsign-conversion",
    "-Wshadow",
    "-Werror",
)


def checked(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def bound_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        checked(path.is_file() and path.stat().st_size <= 2_000_000, "source capacity")
        digest = sha256(path.read_bytes())
        checked(digest == row["sha256"], "changed source: " + row["path"])
        hashes[row["path"]] = digest
    checked(len(hashes) == 2, "live source inventory")
    upstream = json.loads((PACKAGE / "UPSTREAM.json").read_text())
    checked(len(upstream["files"]) == 8, "upstream inventory")
    for row in upstream["files"]:
        path = PACKAGE / row["path"]
        checked(path.is_file() and path.stat().st_size <= 40_000, "vendor capacity")
        checked(
            sha256(path.read_bytes()) == row["sha256"],
            "changed predecessor: " + row["path"],
        )
    return hashes


def run(argv, timeout, output):
    with output.open("w") as stream:
        subprocess.run(
            argv,
            cwd=ROOT,
            check=True,
            timeout=timeout,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
    return output.read_text()


def build(work):
    compiler = shutil.which("c++")
    checked(compiler is not None, "a C++17 compiler is required")
    binary = work / "census"
    run(
        [compiler, *FLAGS, str(PACKAGE / "census.cpp"), "-o", str(binary)],
        60,
        work / "build.txt",
    )
    return binary


def parse_census(text, budget):
    lines = text.splitlines()
    checked(lines[0] == f"flats 776805 reps 159 budget {budget}", "flat/orbit coverage")
    rows, witness = [], None
    for line in lines[1:-1]:
        words = line.split()
        if words[0] == "WITNESS":
            checked(witness is None, "duplicate witness")
            witness = list(map(int, words[1:]))
            continue
        checked(
            words[::2]
            == ["rep", "flat", "lines", "active", "maxdirs", "positive_pairs"],
            "malformed census row",
        )
        rows.append(list(map(int, words[1::2])))
    checked([row[0] for row in rows] == list(range(159)), "incomplete orbit slice")
    words = lines[-1].split()
    checked(
        len(words) == 7
        and words[0] == "TOTAL"
        and words[1] == "maxdirs"
        and words[3] == "positive_pairs"
        and words[5] == "oracle_calls",
        "malformed census total",
    )
    checked(
        int(words[2]) == max(row[4] for row in rows)
        and int(words[4]) == sum(row[5] for row in rows),
        "inconsistent census total",
    )
    total = {
        "max_directions": int(words[2]),
        "positive_pairs": int(words[4]),
        "oracle_calls": int(words[6]),
    }
    checked(
        total["max_directions"] == (1 if budget == 4 else 3),
        "direction-bound counterexample",
    )
    return {
        "budget": budget,
        "pairs": 123_511_995,
        "rows": rows,
        "total": total,
        "witness": witness,
        "stdout_sha256": sha256(text.encode()),
    }


def span(values):
    """Independent small-rank check by explicit XOR closure, at most 512 values."""
    result = {0}
    checked(len(values) <= 112, "rank-check capacity")
    for value in values:
        checked(0 < value < 512, "label range")
        result |= {x ^ value for x in result}
    return result


def check_cut(h, cut, covered, roots, points, labels):
    checked(0 <= h < 120, "witness direction range")
    off = sum(
        1 << i
        for i, row in enumerate(points)
        if sum(x * y for x, y in zip(row, roots[h], strict=True))
    )
    rest = off & ~covered
    checked(not cut & ~rest and cut.bit_count() <= 8, "witness deletion budget")
    retained = [x for i, x in enumerate(labels) if (rest & ~cut) >> i & 1]
    checked(len(span(retained)) <= 64, "witness residual rank")


def witness_check(witness):
    checked(
        witness is not None and len(witness) == 14 and witness[4] == 3,
        "missing three-direction witness",
    )
    roots = root_lines()
    points = tuple(row for row in roots if row not in frame_lines())
    labels = tuple(exact_label(row) for row in points)
    first, second = witness[0] | witness[1] << 64, witness[2] | witness[3] << 64
    for mask in (first, second):
        values = span([x for i, x in enumerate(labels) if mask >> i & 1])
        checked(len(values) == 64, "witness flat rank")
        checked(
            mask == sum(1 << i for i, x in enumerate(labels) if x in values),
            "witness flat closure",
        )
    vectors, cuts = [], []
    for k in range(3):
        h, lo, hi = witness[5 + 3 * k : 8 + 3 * k]
        cut = lo | hi << 64
        check_cut(h, cut, first | second, roots, points, labels)
        vectors.append(roots[h])
        cuts.append(cut)
    gram = [
        [sum(x * y for x, y in zip(a, b, strict=True)) for b in vectors]
        for a in vectors
    ]
    a, b, c = gram
    determinant = (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )
    checked(determinant == 256, "independent direction minor")
    return {
        "gram_determinant": determinant,
        "cut_sizes": [x.bit_count() for x in cuts],
        "cut_union_size": (cuts[0] | cuts[1] | cuts[2]).bit_count(),
        "scope": "Sharp for separate deletion sets; no common-set attainment claim.",
    }


def reproduce(work):
    sources = bound_sources()
    text = fixture(
        ROOT / "research/one-sided-six-multisets/data/data.txt",
        ROOT / "research/one-sided-six-multisets/data/gens.txt",
    )
    data = work / "fixture.txt"
    data.write_text(text)
    binary = build(work)
    oracle = run([str(binary), str(data), "--self-test"], 60, work / "oracle.txt")
    checked(
        oracle == "PASS_ORACLE 36864 subsets 4096 budgets 9\n",
        "exhaustive oracle controls",
    )
    censuses = [
        parse_census(run([str(binary), str(data), str(p)], 180, work / f"p{p}.txt"), p)
        for p in (4, 8)
    ]
    result = {
        "status": "PASS_P112_MIXED_RANK_REDUCTION",
        "source_sha256": sources,
        "fixture_sha256": sha256(text.encode()),
        "annihilators": 788035,
        "flat_cap": 20,
        "root_directions": 120,
        "oracle_checks": 36864,
        "censuses": censuses,
        "positive_control": witness_check(censuses[1]["witness"]),
        "reduction": remaining_shapes(),
        "new_kappa": False,
    }
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work",
        type=Path,
        help="new external directory for retained replay diagnostics",
    )
    parser.add_argument(
        "--write-result", action="store_true", help="explicitly regenerate RESULT.json"
    )
    args = parser.parse_args()
    if args.work:
        work = args.work.resolve()
        checked(not work.is_relative_to(ROOT), "use an external replay directory")
        work.mkdir(parents=True, exist_ok=False)
        result = reproduce(work)
    else:
        with tempfile.TemporaryDirectory(prefix="p112-mixed-") as directory:
            result = reproduce(Path(directory))
    destination = PACKAGE / "RESULT.json"
    if args.write_result:
        destination.write_text(json.dumps(result, indent=2) + "\n")
    else:
        checked(
            result == json.loads(destination.read_text()), "committed receipt differs"
        )
    print(result["status"], "p8_maxdirs=3", "survivors=4->0", "no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2) from error
