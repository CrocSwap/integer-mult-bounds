#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate dense-rank, rational-trace and exact-term-count reconstruction.

Does not import the primary checker or any predecessor executable.
"""

import gzip
import hashlib
import io
import itertools
import json
from fractions import Fraction
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/c5-dyadic-decoder-gate/inputs/"


def require(value, message):
    if not value:
        raise ValueError(message)


def read_geometry():
    inventory = HERE / "SOURCES.json"
    require(inventory.stat().st_size < 32_000, "bounded inventory")
    source = json.loads(inventory.read_bytes())
    expected = {PREFIX + "DATA-PHASES.json.gz", PREFIX + "MATCHING.json"}
    live = [r for r in source["files"] if r["usage"] == "input"]
    require(
        len(live) == 2 and {r["path"] for r in live} == expected, "two pinned inputs"
    )
    raw = {}
    for row in live:
        path = ROOT / row["path"]
        require(
            path.is_file()
            and not path.is_symlink()
            and path.stat().st_size < 2_000_000,
            "input size/type",
        )
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "input SHA256")
        require(
            hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
            == row["git_blob"],
            "input Git blob",
        )
        raw[path.name] = data
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        data = stream.read(2_000_001)
    require(len(data) <= 2_000_000, "decompression size")
    ports = {r["port"]: r["q"] for r in json.loads(data)["recipes"]}
    pairs = json.loads(raw["MATCHING.json"])["matching"]
    return [[ports[p] for p in pairs[i]] for i in (13, 23, 35, 16, 34)]


def dense_rank(left, right):
    matrix = [[(a & b).bit_count() % 2 for b in right] for a in left]
    pivot = 0
    for col in range(len(right)):
        candidates = [r for r in range(pivot, len(left)) if matrix[r][col]]
        if not candidates:
            continue
        row = candidates[0]
        matrix[pivot], matrix[row] = matrix[row], matrix[pivot]
        for r in range(len(left)):
            if r != pivot and matrix[r][col]:
                matrix[r] = [
                    x ^ y for x, y in zip(matrix[r], matrix[pivot], strict=True)
                ]
        pivot += 1
    return pivot


def table(planes):
    subsets = [
        [q for i, p in enumerate(planes) if mask & (1 << i) for q in p]
        for mask in range(32)
    ]
    blocks = ((0, 2), (0, 3), (1, 3), (1, 4), (2,), (4,), (2, 4))
    rows = []
    for a, b in itertools.product(range(32), repeat=2):
        cost = dense_rank(subsets[a], subsets[b])
        hits = []
        for block in blocks:
            mask = sum(1 << i for i in block)
            hits.append(int(bool(mask & a) and bool(mask & b)))
        defect = 2 * cost - 2 * sum(hits[:4]) - sum(hits[4:6])
        require(defect >= 0, "valid physical rank cover")
        increment = tuple(hits[:6]) + (defect, hits[6])
        if not cost:
            require(not any(increment), "zero-cost constrained support")
        rows.append((a, b, cost, increment))
    return rows


def consistent(a, b, inc, target):
    equations = []
    for k, block in enumerate(((0, 2), (0, 3), (1, 3), (1, 4), (2,), (4,))):
        if target[k] == (4 if k < 4 else 2):
            equations.append(
                [Fraction(int(i in block)) for i in range(5)] + [Fraction(inc[k])]
            )
    for i in range(5):
        if not (a & b) & (1 << i):
            equations.append([Fraction(int(i == j)) for j in range(5)] + [Fraction(0)])
    pivot = 0
    for col in range(5):
        candidates = [r for r in range(pivot, len(equations)) if equations[r][col]]
        if not candidates:
            continue
        row = candidates[0]
        equations[pivot], equations[row] = equations[row], equations[pivot]
        scale = equations[pivot][col]
        equations[pivot] = [x / scale for x in equations[pivot]]
        for r in range(len(equations)):
            if r != pivot:
                scale = equations[r][col]
                equations[r] = [
                    x - scale * y
                    for x, y in zip(equations[r], equations[pivot], strict=True)
                ]
        pivot += 1
    return all(any(row[:5]) or not row[5] for row in equations)


def enumerate_case(rows, target, cost):
    moves = {
        (inc, rank)
        for a, b, rank, inc in rows
        if rank and consistent(a, b, inc, target)
    }
    current = {(0,) * 8: 1}
    endpoint = tuple(target) + (4,)
    reachable, best = False, 0
    bound = 5 * prod(x + 1 for x in target)
    for count in range(1, cost + 1):
        following = {}
        for state, value in current.items():
            for inc, rank in moves:
                first = tuple(x + y for x, y in zip(state[:7], inc[:7], strict=True))
                if any(x > y for x, y in zip(first, target, strict=True)):
                    continue
                new = first + (min(4, state[7] + inc[7]),)
                score = value * rank**rank
                if score > following.get(new, 0):
                    following[new] = score
        require(len(following) <= bound, "bounded exact-count layer")
        value = following.get(endpoint, 0)
        reachable |= bool(value)
        if count >= 6:
            best = max(best, value)
        current = following
    return reachable, best


def check():
    planes = read_geometry()
    for i, plane in enumerate(planes):
        require(
            [[(a & b).bit_count() % 2 for b in plane] for a in plane]
            == [[1, 0], [0, 1]],
            "I2 planes",
        )
        for j in range(i):
            require(
                (dense_rank(plane, planes[j]) == 0) == ((i - j) in (1, 4)),
                "literal cycle",
            )
    rows = table(planes)
    receipt_path = HERE / "RESULT.json"
    require(receipt_path.stat().st_size < 1_000_000, "bounded receipt")
    receipt = json.loads(receipt_path.read_bytes())
    costs = [r[2] for r in rows]
    digest = hashlib.sha256(
        json.dumps(costs, separators=(",", ":")).encode()
    ).hexdigest()
    require(digest == receipt["tariff_sha256"], "complete rectangular tariff agreement")
    expected = []
    for cost in (18, 19, 20):
        for target in itertools.product(range(4, 7), repeat=4):
            for single in itertools.product(range(2, 7), repeat=2):
                defect = 2 * cost - 2 * sum(target) - sum(single)
                if defect >= 0:
                    expected.append((cost, target + single + (defect,)))
    require(len(expected) == len(receipt["cases"]) == 60, "all sixty cost/slack cases")
    maximum = 0
    for cost, target in expected:
        row = next(
            r
            for r in receipt["cases"]
            if r["cost"] == cost and tuple(r["target"]) == target
        )
        reachable, best = enumerate_case(rows, target, cost)
        require(
            reachable == row["reachable"] and best == row["six_term_max_product"],
            "separate exact product agreement",
        )
        maximum = max(maximum, best)
    require(maximum == 640_000_000_000 < 4**20, "strict entropy comparison")
    require(9 * 20**20 < 4 * 21**20, "exact small-saving interval")
    print("PASS_INDEPENDENT_C5_MOMENT cases=60 dense_ranks=1024 no_new_kappa")


if __name__ == "__main__":
    check()
