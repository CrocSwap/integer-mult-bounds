#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate dense-rank, five-subset, rational-trace, cost-layer reconstruction.

No primary or predecessor executable is imported. PR3256 supplies the
attributed rank/trace method; PROOF.md states the complete scalar argument.
"""

import gzip
import hashlib
import io
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAIRS = ((0, 2), (0, 3), (1, 3), (1, 4))
PHASE = "DATA-PHASES.json.gz"
PINS = {
    PHASE: "682092a4c656e0be4bdaa419783440772a80ae875cca4845aea2067927b560f6",
    "MATCHING.json": "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sources():
    payloads = {}
    for name, pin in PINS.items():
        path = ROOT / "research/c5-dyadic-decoder-gate/inputs" / name
        need(
            path.is_file()
            and not path.is_symlink()
            and path.stat().st_size <= 2_000_000,
            "regular bounded source",
        )
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin, "independent source SHA256")
        if name.endswith(".gz"):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(2_000_001)
            need(len(raw) <= 2_000_000, "bounded source expansion")
        payloads[name] = json.loads(raw)
    matching = payloads["MATCHING.json"]["matching"]
    recipes = payloads["DATA-PHASES.json.gz"]["recipes"]
    need(len(matching) == 56 and len(recipes) == 112, "fixed physical domain")
    labels = {r["port"]: r["q"] for r in recipes}
    return [[labels[p] for p in pair] for pair in matching]


def dot(a, b):
    return sum(((a >> bit) & 1) * ((b >> bit) & 1) for bit in range(9)) % 2


def rank(matrix):
    rows = [row[:] for row in matrix]
    used = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(used, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[used], rows[pivot] = rows[pivot], rows[used]
        for i in range(used + 1, len(rows)):
            if rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[used], strict=True)]
        used += 1
    return used


def census(planes):
    masks = [
        sum(
            (not any(dot(a, b) for a in x for b in y)) << j
            for j, y in enumerate(planes)
            if i != j
        )
        for i, x in enumerate(planes)
    ]
    result = set()
    for subset in combinations(range(56), 5):
        bits = sum(1 << i for i in subset)
        if all((masks[i] & bits).bit_count() == 2 for i in subset):
            # A simple degree-two graph on five vertices must be one C5.
            result.add(subset)
    need(len(result) == 23, "independent complete five-subset census")
    return result


def rows_for(planes):
    bases = [
        [x for i in range(5) if mask >> i & 1 for x in planes[i]] for mask in range(32)
    ]
    rows = []
    for a in range(32):
        for b in range(32):
            cost = rank([[dot(x, y) for y in bases[b]] for x in bases[a]])
            counts = [
                int(bool(a & ((1 << i) | (1 << j))) and bool(b & ((1 << i) | (1 << j))))
                for i, j in PAIRS
            ]
            counts += [int(bool(a & b & 4)), int(bool(a & b & 16))]
            defect = 2 * cost - 2 * sum(counts[:4]) - sum(counts[4:])
            inc = tuple(counts + [defect, int(bool(a & 20) and bool(b & 20))])
            need(defect >= 0, "actual rectangular tariff cover")
            need(cost or not any(inc), "free support has zero count image")
            rows.append((a, b, cost, inc))
    return rows


def consistent(record, target):
    a, b, _, inc = record
    equations = []
    for i in range(5):
        if not (a & b) >> i & 1:
            row = [Fraction(0)] * 6
            row[i] = Fraction(1)
            equations.append(row)
    for k, (i, j) in enumerate(PAIRS + ((2, 2), (4, 4))):
        if target[k] == (4 if k < 4 else 2):
            row = [Fraction(0)] * 6
            row[i] = row[j] = Fraction(1)
            row[5] = Fraction(inc[k])
            equations.append(row)
    used = 0
    for col in range(5):
        pivot = next(
            (i for i in range(used, len(equations)) if equations[i][col]), None
        )
        if pivot is None:
            continue
        equations[used], equations[pivot] = equations[pivot], equations[used]
        scale = equations[used][col]
        equations[used] = [x / scale for x in equations[used]]
        for i in range(used + 1, len(equations)):
            scale = equations[i][col]
            equations[i] = [
                x - scale * y
                for x, y in zip(equations[i], equations[used], strict=True)
            ]
        used += 1
    return all(any(row[:5]) or not row[5] for row in equations)


def layered(rows, target):
    profiles = {
        (r[2], r[3])
        for r in rows
        if r[2] and r[3][6] <= target[6] and consistent(r, target)
    }
    total = (2 * sum(target[:4]) + sum(target[4:6]) + target[6]) // 2
    need(total in (18, 19), "declared exact cost case")
    layers = [set() for _ in range(total + 1)]
    layers[0].add((0,) * 8)
    for price in range(total + 1):
        for state in layers[price]:
            for cost, inc in profiles:
                if price + cost > total:
                    continue
                new = tuple(state[i] + inc[i] for i in range(7))
                if all(new[i] <= target[i] for i in range(7)):
                    layers[price + cost].add(new + (min(4, state[7] + inc[7]),))
    return {
        "target": list(target),
        "states": sum(len(layer) for layer in layers),
        "profiles": len(profiles),
        "reachable": tuple(target) + (4,) in layers[total],
    }


def case_targets():
    result = {(4, 4, 4, 4, 2, 2, 0)}
    for excess in product(range(2), repeat=4):
        for a, b in product(range(3), repeat=2):
            slack = 2 - 2 * sum(excess) - a - b
            if slack >= 0:
                result.add(tuple(4 + x for x in excess) + (2 + a, 2 + b, slack))
    need(len(result) == 11, "complete independent slack allocations")
    return result


def run():
    planes = sources()
    receipt = json.loads((HERE / "RESULT.json").read_bytes())
    all_cores = census(planes)
    covered = receipt["covered"]
    need(len(covered) == 18 and len(receipt["unresolved"]) == 5, "receipt domain")
    need(
        {tuple(sorted(row["cycle"])) for row in covered}
        | {tuple(sorted(c)) for c in receipt["unresolved"]}
        == all_cores,
        "exact physical-core partition",
    )
    for row in covered:
        order = row["order"]
        need(sorted(order) == sorted(row["cycle"]), "physical order bijection")
        local = [planes[i] for i in order]
        for i in range(5):
            for j in range(5):
                block = [[dot(x, y) for y in local[j]] for x in local[i]]
                if i == j:
                    need(block == [[1, 0], [0, 1]], "plane Gram")
                else:
                    need((rank(block) == 0) == ((i - j) % 5 in (1, 4)), "ordered C5")
        rows = rows_for(local)
        raw = json.dumps([r[2] for r in rows], separators=(",", ":")).encode()
        need(
            hashlib.sha256(raw).hexdigest() == row["tariff_sha256"], "dense tariff hash"
        )
        need(len(row["cases"]) == 11, "18 and all ten19 cases")
        need(
            {tuple(c["target"]) for c in row["cases"]} == case_targets(),
            "complete exact case targets",
        )
        for case in row["cases"]:
            need(
                layered(rows, case["target"]) == case, "independent count reachability"
            )
    print(
        "PASS_C5_PHYSICAL_INDEPENDENT subsets=3819816 cores=23 "
        "certificates=18 cases=198"
    )


if __name__ == "__main__":
    run()
