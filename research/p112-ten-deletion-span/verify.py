"""Replay the complete rank-six census and one new TWOSIDE beta exclusion."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

from beta import reduction
from geometry import direction_catalogue, exact_label, fixture, frame_lines, root_lines

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
WITNESS_12 = (
    298398672570286131,
    52776760246272,
    516232,
    28051596928,
    5,
    2,
    162762907430420484,
    8797703766112,
    7,
    108508605669441600,
    8800924893472,
    221,
    1152930301523001344,
    3367275333632,
    230,
    18577350611437568,
    8830453975040,
    246,
    86704654336,
    73701659770888,
)
FLAGS = (
    "-std=c++17",
    "-mpopcnt",
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
        if row["usage"] == "input":
            path = ROOT / row["path"]
            checked(
                path.is_file() and path.stat().st_size <= 2_000_000, "source capacity"
            )
            digest = sha256(path.read_bytes())
            checked(digest == row["sha256"], "changed source: " + row["path"])
            hashes[row["path"]] = digest
    checked(
        set(hashes)
        == {
            "research/one-sided-six-multisets/data/data.txt",
            "research/one-sided-six-multisets/data/gens.txt",
        },
        "live source inventory",
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
    checked(budget in (8, 10), "unsupported census budget")
    lines = text.splitlines()
    checked(
        len(lines) >= 2 and lines[0] == f"flats 776805 reps 159 budget {budget}",
        "flat/orbit coverage",
    )
    rows, witness = [], None
    for line in lines[1:-1]:
        words = line.split()
        checked(bool(words), "empty census row")
        if words[0] == "WITNESS":
            checked(witness is None, "duplicate witness")
            witness = list(map(int, words[1:]))
        else:
            checked(
                words[::2]
                == [
                    "rep",
                    "flat",
                    "lines",
                    "maxspan",
                    "active",
                    "maxdirs",
                    "positive_pairs",
                ],
                "malformed census row",
            )
            rows.append(list(map(int, words[1::2])))
    checked([row[0] for row in rows] == list(range(159)), "incomplete orbit slice")
    checked(len({row[1] for row in rows}) == 159, "duplicate flat representative")
    checked(
        all(
            0 <= r[1] < 776805
            and 1 <= r[2] <= 20
            and 0 <= r[3] <= min(8, r[5])
            and r[5] <= r[4] <= 248
            and 0 <= r[6] <= 776805
            for r in rows
        ),
        "census row range",
    )
    total = census_total(lines[-1].split(), rows, budget)
    return {
        "budget": budget,
        "pairs": 123511995,
        "rows": rows,
        "total": total,
        "witness": witness,
        "stdout_sha256": sha256(text.encode()),
    }


def census_total(words, rows, budget):
    checked(
        len(words) == 9
        and words[0:2] == ["TOTAL", "maxdirs"]
        and words[3] == "maxspan"
        and words[5] == "positive_pairs"
        and words[7] == "oracle_calls",
        "malformed census total",
    )
    total = {
        "max_directions": int(words[2]),
        "max_span": int(words[4]),
        "positive_pairs": int(words[6]),
        "oracle_calls": int(words[8]),
    }
    checked(
        total["max_directions"] == max(r[5] for r in rows)
        and total["max_span"] == max(r[3] for r in rows)
        and total["positive_pairs"] == sum(r[6] for r in rows),
        "inconsistent census total",
    )
    checked(
        total["max_span"] == (3 if budget == 8 else 4), "direction-span counterexample"
    )
    return total


def matrix_rank(rows):
    checked(
        len(rows) <= 248 and all(len(row) == 8 for row in rows),
        "rational matrix capacity",
    )
    matrix = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for col in range(8):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        value = matrix[rank][col]
        matrix[rank] = [x / value for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            value = matrix[i][col]
            matrix[i] = [
                x - value * y for x, y in zip(matrix[i], matrix[rank], strict=True)
            ]
        rank += 1
    return rank


def binary_span(values):
    checked(
        len(values) <= 112 and all(0 < x < 512 for x in values), "binary rank capacity"
    )
    result = {0}
    for value in values:
        result |= {x ^ value for x in result}
    return result


def witness_check(witness, budget):
    checked(budget in (8, 10, 12), "unsupported witness budget")
    expected = {8: 3, 10: 4, 12: 5}[budget]
    checked(
        witness is not None
        and len(witness) == 5 + 3 * expected
        and witness[4] == expected,
        "missing sharp-span witness",
    )
    directions, _ = direction_catalogue()
    points = tuple(row for row in root_lines() if row not in frame_lines())
    checked(matrix_rank(points) == 8, "P112 real rank")
    labels = tuple(exact_label(row) for row in points)
    first, second = witness[0] | witness[1] << 64, witness[2] | witness[3] << 64
    checked(0 <= first < 1 << 112 and 0 <= second < 1 << 112, "witness flat capacity")
    for mask in (first, second):
        span = binary_span([x for i, x in enumerate(labels) if mask >> i & 1])
        checked(
            len(span) == 64
            and mask == sum(1 << i for i, x in enumerate(labels) if x in span),
            "witness flat closure",
        )
    independent, cuts = [], []
    for offset in range(5, len(witness), 3):
        h, lo, hi = witness[offset : offset + 3]
        checked(0 <= h < 248 and lo >= 0 and hi >= 0, "witness direction or cut")
        direction = directions[h]
        off = sum(
            1 << i
            for i, row in enumerate(points)
            if sum(x * y for x, y in zip(row, direction, strict=True))
        )
        residual = off & ~(first | second)
        cut = lo | hi << 64
        checked(
            not cut & ~residual and cut.bit_count() <= budget, "witness deletion budget"
        )
        checked(
            len(
                binary_span(
                    [x for i, x in enumerate(labels) if (residual & ~cut) >> i & 1]
                )
            )
            <= 64,
            "witness residual rank",
        )
        independent.append(direction)
        cuts.append(cut)
    checked(matrix_rank(independent) == expected, "dependent sharp-span witness")
    union = 0
    for cut in cuts:
        union |= cut
    return {
        "rank": expected,
        "common_union_size": union.bit_count(),
        "directions": independent,
    }


def rank_controls(binary, fixture_path, work):
    directions, _ = direction_catalogue()
    for i in range(248):
        indices = (i, (7 * i + 13) % 248, (17 * i + 31) % 248)
        expected = matrix_rank([directions[j] for j in indices])
        actual = run(
            [str(binary), str(fixture_path), "--rank", *map(str, indices)],
            5,
            work / "rank.txt",
        )
        checked(actual == f"RANK {expected}\n", "independent rational-rank oracle")
    lines = fixture_path.read_text().splitlines()
    lines[1:4] = ["1 1 0 0 0 0 0 0", "1 0 1 0 0 0 0 0", "0 1 1 0 0 0 0 0"]
    mutant = work / "rank-fixture.txt"
    mutant.write_text("\n".join(lines) + "\n")
    checked(
        run([str(binary), str(mutant), "--rank", "0", "1", "2"], 5, work / "rank.txt")
        == "RANK 3\n",
        "rank over Q versus F2 control",
    )
    lines[3] = "2 1 1 0 0 0 0 0"
    mutant.write_text("\n".join(lines) + "\n")
    checked(
        run([str(binary), str(mutant), "--rank", "0", "1", "2"], 5, work / "rank.txt")
        == "RANK 2\n",
        "dependent rank control",
    )
    return 250


def solve(work):
    sources = bound_sources()
    fixture_text, coverage = fixture(
        ROOT / "research/one-sided-six-multisets/data/data.txt",
        ROOT / "research/one-sided-six-multisets/data/gens.txt",
    )
    fixture_path = work / "fixture.txt"
    fixture_path.write_text(fixture_text)
    binary = build(work)
    oracle = run(
        [str(binary), str(fixture_path), "--self-test"], 30, work / "oracle.txt"
    )
    checked(
        oracle == "PASS_ORACLE 45056 subsets 4096 budgets 11\n",
        "deletion-oracle controls",
    )
    rank_checks = rank_controls(binary, fixture_path, work)
    censuses = []
    for budget in (8, 10):
        raw = run(
            [str(binary), str(fixture_path), str(budget)],
            240,
            work / f"census-{budget}.txt",
        )
        census = parse_census(raw, budget)
        census["witness_check"] = witness_check(census["witness"], budget)
        censuses.append(census)
    return {
        "status": "PASS_P112_TEN_DELETION_SPAN",
        "source_sha256": sources,
        "fixture_sha256": sha256(fixture_text.encode()),
        "coverage": coverage,
        "oracle_checks": 45056,
        "rational_rank_checks": rank_checks,
        "censuses": censuses,
        "separate_twelve_control": {
            "witness": WITNESS_12,
            "check": witness_check(WITNESS_12, 12),
        },
        "beta": reduction(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work", type=Path, help="new external directory to retain replay diagnostics"
    )
    parser.add_argument(
        "--output", type=Path, help="new receipt path; otherwise compare RESULT.json"
    )
    args = parser.parse_args()
    checked(sys.version_info >= (3, 12), "Python 3.12 or later is required")
    checked(args.output is None or not args.output.exists(), "output already exists")
    if args.work:
        work = args.work.resolve()
        checked(
            not work.is_relative_to(ROOT), "work directory must be outside the checkout"
        )
        work.mkdir(parents=True, exist_ok=False)
        result = solve(work)
    else:
        with tempfile.TemporaryDirectory(
            prefix="p112-ten-", dir=os.environ.get("TMPDIR")
        ) as temporary:
            result = solve(Path(temporary))
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized)
    else:
        checked(serialized == (PACKAGE / "RESULT.json").read_text(), "receipt mismatch")
    print("PASS_P112_TEN_DELETION_SPAN span=4 beta_5_4_remaining=2")


if __name__ == "__main__":
    main()
