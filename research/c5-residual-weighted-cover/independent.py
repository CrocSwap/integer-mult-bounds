#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate dense-matrix reconstruction; imports no primary verifier."""

import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def dense_rank(matrix):
    rows = [row[:] for row in matrix]
    if not rows:
        return 0
    pivot = 0
    for col in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if rows[i][col]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return pivot


def physical_matrix():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())["files"]
    data = {}
    for row in sources:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        check(
            path.stat().st_size < 2_000_000 and not path.is_symlink(), "source boundary"
        )
        payload = path.read_bytes()
        check(
            hashlib.sha256(payload).hexdigest() == row["sha256"],
            "independent source hash",
        )
        if path.name.endswith(".gz"):
            with gzip.GzipFile(fileobj=io.BytesIO(payload)) as stream:
                payload = stream.read(2_000_001)
            check(len(payload) <= 2_000_000, "decompression boundary")
        data[path.name] = json.loads(payload)
    by_port = {
        item["port"]: item["q"] for item in data["DATA-PHASES.json.gz"]["recipes"]
    }
    matching = data["MATCHING.json"]["matching"]
    labels = [by_port[p] for plane in (10, 12, 23, 35, 16) for p in matching[plane]]
    check(len(labels) == 10 and len(set(labels)) == 10, "named physical scalar labels")
    # Explicit nine-coordinate vectors, not the primary packed-word dot product.
    vectors = [[(label >> k) & 1 for k in range(9)] for label in labels]
    gram = [
        [sum(x * y for x, y in zip(a, b, strict=True)) % 2 for b in vectors]
        for a in vectors
    ]
    return labels, gram


def all_tariffs(gram):
    indices = [[j for j in range(10) if mask & (1 << (j // 2))] for mask in range(32)]
    # Full scalar-coordinate sets of the six forced identity blocks.
    blocks = (
        ([2, 3], 2),
        ([6, 7], 1),
        ([8, 9], 1),
        ([0, 1, 4, 5], 1),
        ([0, 1, 6, 7], 1),
        ([4, 5, 8, 9], 1),
    )
    tariffs, slack = [], []
    for left in indices:
        for right in indices:
            price = dense_rank([[gram[i][j] for j in right] for i in left])
            charge = sum(
                w
                for block, w in blocks
                if set(left) & set(block) and set(right) & set(block)
            )
            check(price >= charge, "independent rectangular inequality")
            tariffs.append(price)
            slack.append(price - charge)
    check(sum(len(block) * w for block, w in blocks) == 20, "weighted identity rank")
    return tariffs, slack


def rational_attainment(gram):
    matrix = [[Fraction(i == j) for j in range(10)] for i in range(10)]
    # The ten singleton terms give an independent arbitrary-term upper bound.
    price = sum(
        dense_rank(
            [
                row[2 * (j // 2) : 2 * (j // 2) + 2]
                for row in gram[2 * (j // 2) : 2 * (j // 2) + 2]
            ]
        )
        for j in range(10)
    )
    check(price == 20, "singleton upper bound")
    for i in range(10):
        for j in range(10):
            # I10 fits even the optional/free entries, so no mask inference is needed.
            check(matrix[i][j] == int(i == j), "exact rational identity")


def main():
    labels, gram = physical_matrix()
    for i in range(5):
        block = [row[2 * i : 2 * i + 2] for row in gram[2 * i : 2 * i + 2]]
        check(block == [[1, 0], [0, 1]], "physical I2 planes")
    for i in range(5):
        for j in range(i + 1, 5):
            zero = all(
                gram[a][b] == 0
                for a in range(2 * i, 2 * i + 2)
                for b in range(2 * j, 2 * j + 2)
            )
            check(zero == (j - i in (1, 4)), "independent C5")
    tariffs, margins = all_tariffs(gram)
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    check(
        labels == [q for pair in expected["physical_labels"] for q in pair],
        "label agreement",
    )
    check(
        hashlib.sha256(bytes(tariffs)).hexdigest() == expected["ordered_tariff_sha256"],
        "all tariff agreement",
    )
    check(
        {str(k): v for k, v in sorted(Counter(margins).items())}
        == expected["margin_histogram"],
        "all slack agreement",
    )
    rational_attainment(gram)
    print("PASS_C5_RESIDUAL_INDEPENDENT dense_tariffs=1024 singleton_upper=20")


if __name__ == "__main__":
    main()
