#!/usr/bin/env python3
"""Independent exact oracle and bounded native census. Apache-2.0."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
FLAGS = ("-std=c++20", "-O3", "-Wall", "-Wextra", "-Wpedantic",
         "-Wconversion", "-Wsign-conversion", "-Wshadow", "-Werror")


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def xor_rank(vectors: list[int] | tuple[int, ...]) -> int:
    basis: dict[int, int] = {}
    for value in vectors:
        for pivot in sorted(basis, reverse=True):
            if value >> pivot & 1:
                value ^= basis[pivot]
        if value:
            basis[value.bit_length() - 1] = value
    return len(basis)


def row_basis(space: tuple[int, ...]) -> tuple[int, ...]:
    rows = list(space[1:])
    used = 0
    for pivot in range(5):
        selected = next((i for i in range(used, len(rows)) if rows[i] >> pivot & 1), None)
        if selected is None:
            continue
        rows[used], rows[selected] = rows[selected], rows[used]
        for i in range(len(rows)):
            if i != used and rows[i] >> pivot & 1:
                rows[i] ^= rows[used]
        used += 1
    return tuple(rows[:used])


def image_spaces() -> dict[int, list[tuple[int, ...]]]:
    """Enumerate actual binary subspaces, not the engine's RREF bit strings."""
    current = {(0,)}
    result: dict[int, list[tuple[int, ...]]] = {}
    for dimension in range(1, 5):
        following = set()
        for space in current:
            for vector in range(1, 32):
                if vector not in space:
                    following.add(tuple(sorted(space + tuple(x ^ vector for x in space))))
        current = following
        if dimension < 2:
            continue
        retained = []
        for space in sorted(current):
            rows = row_basis(space)
            columns = tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows))
                            for j in range(5))
            if 0 in columns:
                continue
            if all(xor_rank(columns[:j] + columns[j + 1:]) == dimension for j in range(5)):
                retained.append(columns)
        def encoded(columns: tuple[int, ...], r: int = dimension) -> int:
            return sum(sum(((columns[j] >> i) & 1) << j for j in range(5)) << (5*i)
                       for i in range(r))
        result[dimension] = sorted(retained, key=encoded)
    need([len(result[r]) for r in (2, 3, 4)] == [35, 35, 1], "image-space count")
    return result


def relation_directions() -> list[tuple[int, ...]]:
    result = [(0,)*5]
    for reverse in itertools.product((-1, 0, 1), repeat=5):
        direction = reverse[::-1]
        support = [value for value in direction if value]
        if len(support) >= 2 and support[0] == 1:
            result.append(direction)
    need(len(result) == 117, "relation count")
    return result


def quotient(exponent: tuple[int, ...], direction: tuple[int, ...]) -> tuple[int, ...]:
    pivot = next((i for i in range(5) if direction[i]), None)
    if pivot is None:
        return exponent
    # Rational elimination along a primitive relation, not subset-pair tables.
    return tuple(exponent[i] - exponent[pivot] * direction[i] * direction[pivot]
                 for i in range(5))


def propagate(x: tuple[int, ...], y: tuple[int, ...], vector: int) -> dict[tuple[int, ...], int]:
    state = {(0,)*5: vector}
    for j in range(5):
        following = dict(state)
        for exponent, value in state.items():
            if (value & y[j]).bit_count() % 2 == 0:
                continue
            shifted = tuple(exponent[i] + int(i == j) for i in range(5))
            following[exponent] = following.get(exponent, 0) ^ x[j]
            following[shifted] = following.get(shifted, 0) ^ x[j]
        state = {key: value for key, value in following.items() if value}
        need(len(state) <= 32, "polynomial capacity")
    return state


def oracle(dimension: int, x: tuple[int, ...], y: tuple[int, ...],
           directions: list[tuple[int, ...]]) -> list[list[tuple[int, int]]]:
    vectors = [propagate(x, y, v) for v in range(1, 1 << dimension)]
    result = []
    for direction in directions:
        representatives = {}
        for mask in range(32):
            exponent = tuple(mask >> j & 1 for j in range(5))
            representatives.setdefault(quotient(exponent, direction), mask)
        eigenvectors = []
        for vector, state in enumerate(vectors, 1):
            grouped: dict[tuple[int, ...], int] = {}
            for exponent, value in state.items():
                key = quotient(exponent, direction)
                grouped[key] = grouped.get(key, 0) ^ value
            surviving = [(key, value) for key, value in grouped.items() if value]
            if len(surviving) == 1 and surviving[0][1] == vector:
                eigenvectors.append((vector, representatives[surviving[0][0]]))
        result.append(eigenvectors)
    return result


def expected_probes(spaces: dict[int, list[tuple[int, ...]]]) -> set[tuple[int, ...]]:
    result = set()
    for dimension, columns_list in spaces.items():
        index = 0
        for x in columns_list:
            choices = [tuple(y for y in range(1, 1 << dimension) if (y & v).bit_count() % 2)
                       for v in x]
            for reverse in itertools.product(*choices[::-1]):
                y = reverse[::-1]
                if dimension == 2 or index % 997 == 0 or y == tuple(c[0] for c in choices):
                    result.add((dimension,) + x + y)
                index += 1
    return result


def high_possible(mask: int, direction: tuple[int, ...]) -> bool:
    return min(sum((mask >> j & 1) + multiple*direction[j] != 0 for j in range(5))
               for multiple in range(-2, 3)) >= 3


def verify_engine_output(output: str) -> dict:
    spaces = image_spaces()
    directions = relation_directions()
    expected = expected_probes(spaces)
    seen = set()
    summaries = []
    lines = iter(output.splitlines())
    rank_two_histogram = [0]*16
    rank_two_monomials = 0
    footer = False
    for line in lines:
        fields = line.split()
        if fields[0] == "P":
            key = tuple(map(int, fields[1:]))
            need(key in expected and key not in seen, "unexpected/repeated probe")
            seen.add(key)
            dimension, x, y = key[0], key[1:6], key[6:11]
            for index, eigenvectors in enumerate(oracle(dimension, x, y, directions)):
                record = next(lines).split()
                actual = [tuple(map(int, pair.split(":"))) for pair in record[2:]]
                need(record[:2] == ["E", str(index)] and actual == eigenvectors,
                     "independent eigenvector oracle mismatch")
                if dimension == 2:
                    high = sum(high_possible(mask, directions[index]) for _, mask in eigenvectors)
                    rank_two_histogram[high] += 1
                    rank_two_monomials += len(eigenvectors)
        elif fields[0] == "R":
            summaries.append(list(map(int, fields[1:])))
        else:
            need(line == "PASS_CLEAN_REDUCED_CENSUS" and not footer, "unexpected engine record")
            footer = True
    need(seen == expected, "missing oracle probe")
    need(footer, "missing engine footer")
    need(len(summaries) == 3, "missing census summary")
    for dimension, summary in zip((2, 3, 4), summaries, strict=True):
        need(len(summary) == 21 and summary[0] == dimension, "summary shape")
        expected_words = len(spaces[dimension]) * (1 << (dimension-1))**5
        need(summary[1:3] == [len(spaces[dimension]), expected_words], "census coverage")
        need(summary[4] == 0 and sum(summary[5:]) == expected_words*117, "candidate/coverage")
    need(summaries[0][3] == rank_two_monomials, "independent full rank-two count")
    need(summaries[0][5:] == rank_two_histogram, "independent full rank-two histogram")
    records = [{"image_dimension": row[0], "image_spaces": row[1],
                "words": row[2], "monomial_vectors": row[3],
                "candidate_cases": row[4], "high_rank_vector_histogram": row[5:]}
               for row in summaries]
    return {"summaries": records, "oracle_probes": len(seen),
            "oracle_relations": len(seen)*117, "relation_patterns": 117}


def physical_apply(calls: list[tuple[int, int, tuple[int | Fraction, ...]]], vector: int) -> dict:
    state = {(0,)*9: vector}
    need(len(calls) <= 7, "fixture call capacity")
    for x, y, frame in calls:
        following = dict(state)
        for exponent, value in state.items():
            if (value & y).bit_count() % 2:
                shifted = tuple(a+b for a, b in zip(exponent, frame, strict=True))
                following[exponent] = following.get(exponent, 0) ^ x
                following[shifted] = following.get(shifted, 0) ^ x
        state = {key: value for key, value in following.items() if value}
    return state


def fixture_controls() -> dict:
    frames = [tuple(int(j == 3*i+i) for j in range(9)) for i in range(3)]
    identity = (1, 0, 0, 0, 1, 0, 0, 0, 1)
    other = (Fraction(1, 2), 0, 0, Fraction(1, 3), -1, 0,
             2, Fraction(1, 4), Fraction(3, 2))
    columns = [tuple(value if j % 3 == column else 0 for j, value in enumerate(other))
               for column in range(3)]
    direct = [(1, 1, frame) for frame in frames] + [(2, 2, frame) for frame in columns]
    target = [{identity: 1}, {other: 2}]
    need([physical_apply(direct, v) for v in (1, 2)] == target, "six-call fixture")
    need([physical_apply(direct[:-1], v) for v in (1, 2)] != target, "omission control")
    borrowed = direct[:2] + [(16, 16, frames[0])] + direct[2:]
    need([physical_apply(borrowed, v) for v in (1, 2)] == target, "coloop deletion")
    need(physical_apply(borrowed, 16) != physical_apply(direct, 16), "clean-only distinction")
    # A rank-one target permits an active coloop: the lemma must exclude it.
    clean_only = [(1, 3, frames[0])]
    need(physical_apply(clean_only, 1) == {frames[0]: 1}, "rank-one clean endpoint")
    need(physical_apply(clean_only, 2) != {(0,)*9: 2}, "unconstrained clean column")
    need(physical_apply([], 1) != physical_apply(clean_only, 1), "active coloop boundary")
    return {"six_call_positive": True, "omission_rejected": True,
            "removable_clean_coloop": True, "rank_one_boundary": True}


def check_sources() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for source in sources["files"]:
        if source["usage"] == "input":
            digest = hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
            need(digest == source["sha256"], "source input changed: " + source["path"])


def run_census() -> dict:
    compiler = shutil.which(os.environ.get("CXX", "c++"))
    need(compiler is not None, "a C++20 compiler is required")
    with tempfile.TemporaryDirectory(prefix="clean-workspace-") as work:
        executable = Path(work) / "census"
        build = subprocess.run([compiler, *FLAGS, str(PACKAGE / "engine.cpp"), "-o", str(executable)],
                               text=True, capture_output=True, timeout=60, check=False)
        need(build.returncode == 0 and not build.stderr, "compiler failed: " + build.stderr)
        run = subprocess.run([str(executable)], text=True, capture_output=True, timeout=60, check=False)
        need(run.returncode == 0 and not run.stderr, "engine failed: " + run.stderr)
        need(len(run.stdout) <= 2_000_000, "engine output capacity")
        return verify_engine_output(run.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate only RESULT.json")
    arguments = parser.parse_args()
    check_sources()
    result = {"schema_version": 1, "census": run_census(), "controls": fixture_controls()}
    receipt = PACKAGE / "RESULT.json"
    if arguments.write:
        receipt.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(receipt.read_text() == json.dumps(result, indent=2) + "\n", "receipt mismatch")
    print("PASS_CLEAN_WORKSPACE_COMPRESSION words=69728 candidates=0 no_new_kappa")


if __name__ == "__main__":
    main()
