#!/usr/bin/env python3
"""Check every character of the actual rank-thirty phase section."""

from fractions import Fraction as F
from hashlib import sha256
from math import lcm
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent / "lanes"
PINS = {
    "response": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "directions": (
        "history-encoding/independent-skeleton-20261018/fresh-three-child/"
        "FRESH-THREE-CHILD-PROGRAMS.json.gz",
        "b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5",
    ),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def product(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)]
            for row in a]


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    rows = [row[:] + unit for row, unit in zip(a, identity(n))]
    for k in range(n):
        p = next((p for p in range(k, n) if rows[p][k]), None)
        need(p is not None, "Every character block is invertible")
        rows[k], rows[p] = rows[p], rows[k]
        pivot = rows[k][k]
        rows[k] = [x / pivot for x in rows[k]]
        for i in range(n):
            if i == k or not rows[i][k]:
                continue
            scale = rows[i][k]
            rows[i] = [x - scale * y for x, y in zip(rows[i], rows[k])]
    out = [row[n:] for row in rows]
    need(product(a, out) == identity(n), "Right inverse")
    need(product(out, a) == identity(n), "Left inverse")
    return out


def main():
    sources = {}
    for name, (path, digest) in PINS.items():
        raw = (LANES / path).read_bytes()
        if path.endswith(".gz"):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == digest, name + " source pin")
        sources[name] = json.loads(raw)
    response = sources["response"]
    q = [row["q"] for row in sources["directions"]["transfers"]]
    u = [{int(j): F(c) for j, c in row.items()}
         for row in response["correction_U"]]
    v = [{int(j): F(c) for j, c in row.items()}
         for row in response["correction_V"]]
    need(len(u) == 112 and len(v) == 30, "Actual full factor sizes")
    records = []
    denominator = 1
    max_row_norm = F(0)
    for chi in range(512):
        t = [[F(0)] * 30 for _ in range(30)]
        for i, row in enumerate(v):
            for p, a in row.items():
                sign = 1 - 2 * ((chi & q[p]).bit_count() % 2)
                for j, b in u[p].items():
                    t[i][j] += sign * a * b
        need(all(not t[i][j] for i in range(30) for j in range(30)
                 if (i >= 16 or j >= 16) and i != j),
             "Fourteen separate scalar character blocks")
        ti = inverse([row[:16] for row in t[:16]])
        small = [t[i][i] for i in range(16, 30)]
        need(all(x and x.denominator == 1 and int(x) % 2 for x in small),
             "Odd clique sums never vanish")
        small_inverse = [1 / x for x in small]
        coefficients = [x for row in ti for x in row] + small_inverse
        for x in coefficients:
            denominator = lcm(denominator, x.denominator)
        max_row_norm = max(max_row_norm,
                           max(sum(abs(x) for x in row) for row in ti),
                           max(abs(x) for x in small_inverse))
        records.append({
            "chi": chi,
            "large_inverse": [[str(x) for x in row] for row in ti],
            "small_diagonal": [str(x) for x in small],
        })
    odd_denominator = denominator
    while odd_denominator % 2 == 0:
        odd_denominator //= 2
    payload = {"characters": records}
    payload_path = HERE / "RANK30-PHASE-SECTION-BLOCKS-20261020.json.gz"
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with payload_path.open("wb") as stream:
        stream.write(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_RANK30_PHASE_SECTION",
        "source_sha256": {name: pin for name, (_, pin) in PINS.items()},
        "character_count": 512,
        "large_block_dimension": 16,
        "scalar_blocks_per_character": 14,
        "inverse_common_denominator": denominator,
        "inverse_common_odd_denominator": odd_denominator,
        "max_character_inverse_row_norm": str(max_row_norm),
        "blocks_decompressed_sha256": sha256(raw).hexdigest(),
        "scope": "Exact all-character inverse; source-query formation is not supplied",
    }
    path = HERE / "RANK30-PHASE-SECTION-CHECKS-20261020.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    print("receipt_sha256=" + sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
