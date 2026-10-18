#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact complete-plane rank-cover certificate for one physical C5."""

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/c5-dyadic-decoder-gate/inputs/"
CORE = (10, 12, 23, 35, 16)
# (plane-support mask, integer weight, forced scalar principal-block rank)
COVER = ((2, 2, 2), (8, 1, 2), (16, 1, 2), (5, 1, 4), (9, 1, 4), (20, 1, 4))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_geometry(root=ROOT):
    inventory = json.loads((HERE / "SOURCES.json").read_bytes())
    live = {row["path"]: row for row in inventory["files"] if row["usage"] == "input"}
    require(
        set(live) == {PREFIX + "DATA-PHASES.json.gz", PREFIX + "MATCHING.json"},
        "source closure",
    )
    payloads = {}
    for name, row in live.items():
        path = root / name
        require(path.is_file() and not path.is_symlink(), "regular source input")
        require(path.stat().st_size <= 2_000_000, "bounded input")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        require(blob == row["git_blob"], "source Git blob")
        if name.endswith(".gz"):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(2_000_001)
            require(len(raw) <= 2_000_000, "bounded decompression")
        payloads[path.name] = json.loads(raw)
    recipes = payloads["DATA-PHASES.json.gz"]["recipes"]
    matching = payloads["MATCHING.json"]["matching"]
    require(len(recipes) == 112 and len(matching) == 56, "physical inventory")
    labels = {row["port"]: row["q"] for row in recipes}
    require(sorted(labels) == list(range(112)), "complete scalar ports")
    require(
        all(type(q) is int and 0 < q < 512 for q in labels.values()), "nine-bit labels"
    )
    require(all(len(pair) == 2 for pair in matching), "two-port planes")
    require(
        sorted(p for pair in matching for p in pair) == list(range(112)),
        "plane partition",
    )
    return tuple(tuple(labels[p] for p in matching[i]) for i in CORE)


def dot(a, b):
    return (a & b).bit_count() & 1


def pairing_rank(left, right):
    pivots = [0] * 10
    count = 0
    for x in left:
        word = sum(dot(x, y) << j for j, y in enumerate(right))
        for bit in range(9, -1, -1):
            if word & (1 << bit):
                if pivots[bit]:
                    word ^= pivots[bit]
                else:
                    pivots[bit] = word
                    count += 1
                    break
    return count


def support_labels(planes, mask):
    return tuple(q for i, pair in enumerate(planes) if mask & (1 << i) for q in pair)


def check_geometry(planes):
    require(len(planes) == 5, "five physical planes")
    for i, plane in enumerate(planes):
        require(
            [[dot(x, y) for y in plane] for x in plane] == [[1, 0], [0, 1]],
            "plane Gram I2",
        )
        for j in range(i + 1, 5):
            orthogonal = pairing_rank(plane, planes[j]) == 0
            require(orthogonal == (j - i in (1, 4)), "induced physical C5")
    for mask, weight, size in COVER:
        require(
            weight > 0 and len(support_labels(planes, mask)) == size, "cover block size"
        )
        for i in range(5):
            for j in range(i + 1, 5):
                if mask & (1 << i) and mask & (1 << j):
                    require(
                        pairing_rank(planes[i], planes[j]) > 0, "forced identity block"
                    )


def cover_charge(a, b, cover=COVER):
    return sum(weight for mask, weight, _ in cover if a & mask and b & mask)


def tariff_certificate(planes, cover=COVER):
    labels = [support_labels(planes, mask) for mask in range(32)]
    tariffs, margins = [], []
    for a in range(32):
        for b in range(32):
            cost = pairing_rank(labels[a], labels[b])
            margin = cost - cover_charge(a, b, cover)
            require(margin >= 0, f"rank-cover inequality fails at {a},{b}")
            tariffs.append(cost)
            margins.append(margin)
    return tariffs, margins


def check_fit(matrix, planes):
    require(
        len(matrix) == 10 and all(len(row) == 10 for row in matrix),
        "ten-coordinate fit",
    )
    for i in range(10):
        for j in range(10):
            if i // 2 == j // 2 or pairing_rank(planes[i // 2], planes[j // 2]) > 0:
                require(
                    matrix[i][j] == int(i == j), f"strict scalar constraint {i},{j}"
                )


def attaining_fit(planes, alpha=Fraction(2)):
    require(alpha != 0, "nonzero asymmetric scale")
    matrix = [[Fraction(0) for _ in range(10)] for _ in range(10)]
    total = 0
    for i in range(5):
        p, q = 2 * i + 1, 2 * ((i + 1) % 5)
        left, right = {p: Fraction(1), q: alpha}, {p: Fraction(1), q: 1 / alpha}
        for a, x in left.items():
            for b, y in right.items():
                matrix[a][b] += x * y
        block = planes[i] + planes[(i + 1) % 5]
        total += pairing_rank(block, block)
    check_fit(matrix, planes)
    require(total == 20, "complete attaining tariff")
    return matrix, total


def build(root=ROOT):
    planes = load_geometry(root)
    check_geometry(planes)
    tariffs, margins = tariff_certificate(planes)
    _, upper = attaining_fit(planes)
    lower = sum(weight * size for _, weight, size in COVER)
    require(lower == upper == 20, "sharp full-plane bound")
    return {
        "claim": "sharp_arbitrary_finite_asymmetric_cost20_on_named_residual_C5",
        "core": list(CORE),
        "physical_labels": [list(pair) for pair in planes],
        "cover": [list(row) for row in COVER],
        "lower_bound": lower,
        "attained_cost": upper,
        "ordered_tariff_sha256": hashlib.sha256(bytes(tariffs)).hexdigest(),
        "margin_histogram": {str(k): v for k, v in sorted(Counter(margins).items())},
        "support_pairs": len(tariffs),
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(
            result == json.loads((HERE / "RESULT.json").read_bytes()), "exact receipt"
        )
        print(
            "PASS_C5_RESIDUAL_WEIGHTED_COVER support_pairs=1024 "
            "sharp_cost=20 no_new_kappa"
        )


if __name__ == "__main__":
    main()
