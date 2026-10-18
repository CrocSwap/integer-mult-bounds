"""Replay a mixed-rank P112 theorem and the 3,4^2,6^6 beta exclusion."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from vendor.geometry import chamber_ray, fixture, frame_lines, root_lines, weyl_closure

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
INPUTS = (
    "research/one-sided-six-multisets/data/data.txt",
    "research/one-sided-six-multisets/data/gens.txt",
)
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


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bound_sources(root=ROOT, package=PACKAGE):
    manifest = json.loads((package / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    checked(
        sorted(row["path"] for row in inputs) == sorted(INPUTS), "live input inventory"
    )
    retained = manifest["retained_files"]
    checked(len(retained) == 6, "retained input inventory")
    hashes = {}
    for row, path in [(r, root / r["path"]) for r in inputs] + [
        (r, package / r["copy"]) for r in retained
    ]:
        checked(path.is_file() and path.stat().st_size <= 2_000_000, "source capacity")
        actual = digest(path.read_bytes())
        checked(actual == row["sha256"], "changed source: " + str(path))
        hashes[row.get("copy", row.get("path"))] = actual
    return hashes


def run(argv, work, name, timeout=180):
    output = work / name
    with output.open("w") as stream:
        subprocess.run(
            argv,
            check=True,
            timeout=timeout,
            stdout=stream,
            stderr=subprocess.STDOUT,
            cwd=ROOT,
        )
    checked(output.stat().st_size <= 2_000_000, "native output capacity")
    return output.read_text()


def build(work, package=PACKAGE):
    compiler = shutil.which("c++")
    checked(compiler is not None, "a C++17 compiler is required")
    binary = work / "scan"
    run(
        [compiler, *FLAGS, str(package / "scan.cpp"), "-o", str(binary)],
        work,
        "build.txt",
        60,
    )
    return binary


def binary_span(values):
    result = {0}
    for value in values:
        result |= {x ^ value for x in result}
    return result


def binary_rank(values):
    basis = [0] * 9
    for value in values:
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return sum(bool(x) for x in basis)


def rational_rank(rows):
    checked(len(rows) <= 248 and all(len(r) == 8 for r in rows), "matrix capacity")
    matrix = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for col in range(8):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][col]
        matrix[rank] = [x / scale for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            scale = matrix[i][col]
            matrix[i] = [
                x - scale * y for x, y in zip(matrix[i], matrix[rank], strict=True)
            ]
        rank += 1
    return rank


def parse_fixture(text):
    lines = text.splitlines()
    checked(len(lines) == 509, "fixture coverage")
    labels = tuple(map(int, lines[0].split()))
    directions = tuple(tuple(map(int, line.split())) for line in lines[1:249])
    off = tuple(
        lo | hi << 64 for lo, hi in (map(int, s.split()) for s in lines[249:497])
    )
    checked(len(labels) == 112 and all(x & 1 for x in labels), "odd labels")
    parity = tuple(
        sum(1 << i for i, x in enumerate(labels) if (x & a).bit_count() % 2)
        for a in range(512)
    )
    return labels, directions, off, parity


def values(mask, labels):
    checked(0 <= mask < 1 << 112, "mask capacity")
    return [x for i, x in enumerate(labels) if mask >> i & 1]


def flat_check(mask, labels):
    span = binary_span(values(mask, labels))
    checked(len(span) <= 64, "not a six-flat mask")
    checked(
        mask == sum(1 << i for i, x in enumerate(labels) if x in span),
        "flat not closed",
    )


def check_cut(rest, cut, target, labels, budget=12):
    checked(type(budget) is int and 0 <= budget <= 14, "cut budget capacity")
    checked(
        0 <= cut < 1 << 112 and not cut & ~rest and cut.bit_count() <= budget,
        "invalid deletion cut",
    )
    checked(binary_rank(values(rest & ~cut, labels)) <= target, "residual rank failed")


def anchor_oracle(rest, labels, budget=12):
    """Independent explicit binary spans, rather than the native odd-XOR formula."""
    selected = values(rest, labels)
    checked(len(selected) <= 20, "anchor oracle capacity")
    if len(selected) <= budget:
        return True
    for subset in combinations(selected, min(4, len(selected))):
        span = binary_span(subset)
        if sum(x not in span for x in selected) <= budget:
            return True
    return False


def six_oracle(rest, labels, parity):
    need = binary_rank(values(rest, labels)) - 6
    if need <= 0:
        return True
    words = sorted({word for p in parity if 0 < (word := p & rest).bit_count() <= 12})
    if need == 1:
        return bool(words)
    for a, b in combinations(words, 2):
        joined = a | b
        if joined.bit_count() > 12:
            continue
        if need == 2:
            return True
        if any(
            c not in (a, b, a ^ b) and (joined | c).bit_count() <= 12 for c in words
        ):
            return True
    return False


def positive_check(parts, first, second, data):
    labels, directions, off, parity = data
    checked(parts[0] == "POS", "missing positive list")
    n = int(parts[1])
    checked(1 <= n <= 248 and len(parts) == 2 + 3 * n, "positive list capacity")
    listed = []
    for index in range(n):
        h, lo, hi = map(int, parts[2 + 3 * index : 5 + 3 * index])
        checked(0 <= h < 248 and lo >= 0 and hi >= 0, "direction or cut capacity")
        check_cut(off[h] & ~(first | second), lo | hi << 64, 6, labels)
        listed.append(h)
    screened = [h for h in range(248) if (off[h] & ~(first | second)).bit_count() <= 32]
    expected = [
        h for h in screened if six_oracle(off[h] & ~(first | second), labels, parity)
    ]
    checked(listed == expected, "rank-six direction inventory disagrees")
    rank = rational_rank([directions[h] for h in listed])
    checked(rank <= 3, "mixed-rank span theorem failed")
    return rank, listed, len(screened)


def anchor_check(parts, expected_row, data):
    checked(
        parts and parts[0] == "ANCHOR" and len(parts) == 11, "invalid anchor record"
    )
    ri, j, flo, fhi, slo, shi, h, answer, clo, chi = map(int, parts[1:])
    checked(
        ri == expected_row and 0 <= j < 776805 and 0 <= h < 248 and answer in (0, 1),
        "anchor record range",
    )
    checked(min(flo, fhi, slo, shi, clo, chi) >= 0, "negative mask component")
    first, second, cut = flo | fhi << 64, slo | shi << 64, clo | chi << 64
    labels, _, off, _ = data
    flat_check(first, labels)
    flat_check(second, labels)
    rest = off[h] & ~(first | second)
    checked(bool(answer) == anchor_oracle(rest, labels), "rank-four oracle disagrees")
    if answer:
        check_cut(rest, cut, 4, labels)
    else:
        checked(cut == 0, "negative answer has a cut")
    proof = {
        "first": [flo, fhi],
        "second": [slo, shi],
        "anchor": h,
        "anchor_cut": [clo, chi],
    }
    return answer, first, second, proof


def audit_census(text, data):
    lines = text.splitlines()
    checked(2 <= len(lines) <= 10_000, "census line capacity")
    checked(lines[0] == "COVER 776805 159", "flat/orbit coverage")
    rows, anchors, positives, witness = [], 0, 0, None
    cursor, maximum, calls = 1, 0, 0
    row_tests, row_hits, row_span = 0, 0, 0
    _, directions, _, _ = data
    while cursor < len(lines) - 1:
        parts = lines[cursor].split()
        cursor += 1
        if parts[0] == "ROW":
            row = list(map(int, parts[1:]))
            checked(
                len(row) == 6 and row[0] == len(rows), "missing or duplicate orbit row"
            )
            checked(
                row[3:] == [row_span, row_tests, row_hits], "inconsistent orbit row"
            )
            rows.append(row)
            row_tests, row_hits, row_span = 0, 0, 0
            continue
        answer, first, second, proof = anchor_check(parts, len(rows), data)
        anchors += 1
        row_tests += 1
        if not answer:
            continue
        checked(cursor < len(lines) - 1, "missing positive record")
        rank, listed, pair_calls = positive_check(
            lines[cursor].split(), first, second, data
        )
        cursor += 1
        positives += 1
        row_hits += 1
        calls += pair_calls
        row_span = max(row_span, rank)
        maximum = max(maximum, rank)
        if rank == 3 and witness is None:
            witness = proof | {
                "directions": listed,
                "vectors": [directions[x] for x in listed],
                "rank": rank,
            }
    total = census_total(lines[-1], rows, anchors, positives, maximum)
    checked(total["rank_six_oracle_calls"] == calls, "oracle call count disagrees")
    checked(witness is not None, "missing sharp-span witness")
    return {
        "rows": rows,
        "total": total,
        "witness": witness,
        "native_stdout_sha256": digest(text.encode()),
        "independent_anchor_checks": anchors,
        "independent_positive_pairs": positives,
    }


def census_total(line, rows, anchors, positives, maximum):
    parts = line.split()
    checked(len(parts) == 6 and parts[0] == "TOTAL", "malformed total")
    pairs, tests, hits, calls, span = map(int, parts[1:])
    checked(
        len(rows) == 159 and len({r[1] for r in rows}) == 159,
        "incomplete first-flat coverage",
    )
    checked(
        all(
            0 <= r[1] < 776805
            and 1 <= r[2] <= 20
            and 0 <= r[3] <= 3
            and 0 <= r[5] <= r[4]
            for r in rows
        ),
        "orbit row range",
    )
    checked(
        pairs == 123511995
        and tests == anchors == sum(r[4] for r in rows)
        and hits == positives == sum(r[5] for r in rows)
        and span == maximum == max(r[3] for r in rows) == 3
        and calls >= hits,
        "inconsistent coverage total",
    )
    return {
        "pairs": pairs,
        "anchor_tests": tests,
        "positive_pairs": hits,
        "rank_six_oracle_calls": calls,
        "max_span": span,
    }


def beta_application():
    weights = (3, 4, 4, 6, 6, 6, 6, 6, 6)
    quotient_basis = (3, 4, 6, 6)
    complement = list(weights)
    for weight in quotient_basis:
        complement.remove(weight)
    checked(complement == [4, 6, 6, 6, 6], "wrong nonbasis weights")
    support_cap = 4 + 8 + 20 + 20
    checked(
        support_cap < 53 and len(complement) > 3, "fundamental-circuit contradiction"
    )
    return {
        "cell": [5, 4],
        "weights": weights,
        "quotient_basis": quotient_basis,
        "support_cap": support_cap,
        "common_deletion_cap": 12,
        "nonbasis_weights": complement,
        "forced_direction_rank": 5,
        "finite_upper_bound": 3,
        "remaining_from_PR3162": [2, 5, 5, 5, 6, 6, 6, 6, 6],
    }


def mixed_direction_coverage(data):
    points = tuple(r for r in root_lines() if r not in frame_lines())
    checked(rational_rank(points) == 8, "P112 characteristic-zero rank")
    orbit = weyl_closure((chamber_ray(0), chamber_ray(7)))
    histogram, selected = {}, set()
    for h in orbit:
        support = sum(
            bool(sum(x * y for x, y in zip(h, r, strict=True))) for r in points
        )
        histogram[support] = histogram.get(support, 0) + 1
        if support <= 72:
            selected.add(h)
    checked(histogram == {53: 112, 56: 8, 70: 128, 73: 896, 76: 56}, "mixed cutoff gap")
    checked(selected == set(data[1]), "incomplete mixed direction catalogue")
    return {
        "support_cutoff": 72,
        "required_perpendicular_lines": 40,
        "orbit_support_histogram": sorted(histogram.items()),
        "retained": len(selected),
    }


def unanchored_control(data):
    witness = (
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
    labels, directions, off, _ = data
    first, second = witness[0] | witness[1] << 64, witness[2] | witness[3] << 64
    flat_check(first, labels)
    flat_check(second, labels)
    indices = []
    for offset in range(5, len(witness), 3):
        h, lo, hi = witness[offset : offset + 3]
        check_cut(off[h] & ~(first | second), lo | hi << 64, 6, labels)
        indices.append(h)
    checked(
        rational_rank([directions[h] for h in indices]) == 5, "unanchored control rank"
    )
    return {"source": "PR3162 WITNESS_12", "witness": witness, "rank": 5}


def fourteen_control(data, path=PACKAGE / "CONTROL14.json"):
    control = json.loads(path.read_text())
    labels = data[0]
    points = tuple(r for r in root_lines() if r not in frame_lines())
    first = control["first"][0] | control["first"][1] << 64
    second = control["second"][0] | control["second"][1] << 64
    flat_check(first, labels)
    flat_check(second, labels)
    checked(len(control["directions"]) == 5, "fourteen control capacity")
    union, vectors = 0, []
    for row, target in [(control["anchor"], 5)] + [
        (r, 6) for r in control["directions"]
    ]:
        vector = row["vector"]
        checked(
            len(vector) == 8
            and any(vector)
            and all(type(x) is int and abs(x) <= 3 for x in vector),
            "fourteen direction capacity",
        )
        rest = sum(
            1 << i
            for i, root in enumerate(points)
            if sum(x * y for x, y in zip(vector, root, strict=True))
        ) & ~(first | second)
        cut = row["cut"][0] | row["cut"][1] << 64
        check_cut(rest, cut, target, labels, 14)
        union |= cut
        if target == 6:
            vectors.append(vector)
    checked(rational_rank(vectors) == 5, "fourteen control direction rank")
    checked(union.bit_count() > 14, "fourteen control unexpectedly has a common cut")
    return {"witness": control, "rank": 5, "cut_union_size": union.bit_count()}


def solve(work):
    hashes = bound_sources()
    text, coverage = fixture(*(ROOT / name for name in INPUTS))
    data = parse_fixture(text)
    mixed_coverage = mixed_direction_coverage(data)
    path = work / "fixture.txt"
    path.write_text(text)
    binary = build(work)
    control = run([str(binary), str(path), "--self-test"], work, "oracle.txt")
    checked(
        control == "PASS_ORACLES 109239 exhaustive20 1048576\n",
        "oracle control coverage",
    )
    raw = run([str(binary), str(path)], work, "census.txt")
    audit = audit_census(raw, data)
    return {
        "status": "PASS_P112_MIXED_RANK_ANCHOR",
        "sources": hashes,
        "fixture_sha256": digest(text.encode()),
        "coverage": coverage,
        "mixed_direction_coverage": mixed_coverage,
        "oracle_comparisons": 109239,
        "census": audit,
        "unanchored_control": unanchored_control(data),
        "fourteen_control": fourteen_control(data),
        "beta": beta_application(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, help="new external diagnostics directory")
    parser.add_argument(
        "--output", type=Path, help="new receipt, otherwise compare RESULT.json"
    )
    args = parser.parse_args()
    checked(args.output is None or not args.output.exists(), "output already exists")
    if args.work:
        work = args.work.resolve()
        checked(not work.is_relative_to(ROOT), "work directory must be external")
        work.mkdir(parents=True, exist_ok=False)
        result = solve(work)
    else:
        with tempfile.TemporaryDirectory(
            prefix="p112-anchor-", dir=os.environ.get("TMPDIR")
        ) as temporary:
            result = solve(Path(temporary))
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized)
    else:
        checked(serialized == (PACKAGE / "RESULT.json").read_text(), "receipt mismatch")
    print("PASS_P112_MIXED_RANK_ANCHOR span=3 pinned_beta_exclusions=1")


if __name__ == "__main__":
    main()
