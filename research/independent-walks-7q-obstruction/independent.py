#!/usr/bin/env python3
"""Independent partitioned dual-walk census at Q=7.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
INF = 99


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_table(slots):
    n = len(slots)
    even = [INF] * 32
    even[0] = 0
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        if size % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size < even[value]:
            even[value] = size
    return even


def dual_full(e0, e1):
    total = 0
    for m in range(1, 32):
        best = INF
        for a in range(32):
            c0, c1 = e0[a], e1[a ^ m]
            if c0 < INF and c1 < INF:
                best = min(best, c0 + c1)
        if best >= INF:
            return None
        total += best
    return total


def dual_short(e_long, sigma):
    total = 0
    for m in range(1, 32):
        best = INF
        if e_long[m] < INF:
            best = e_long[m]
        if e_long[m ^ sigma] < INF:
            best = min(best, 2 + e_long[m ^ sigma])
        if best >= INF:
            return None
        total += best
    return total


def path_X(slots):
    closed = slots + (0,)
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        if delta == 0:
            return None
        total += 2 * (delta.bit_count() - 1)
    return total


def tariff(q, r, x):
    return 38 * q + 2 * r + 2 * x


def census_25():
    hist = Counter()
    covering = 0
    tables = {
        nz: even_table((0,) + nz) for nz in combinations(range(1, 32), 4)
    }
    for sigma in range(1, 32):
        for e_long in tables.values():
            r = dual_short(e_long, sigma)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
    return covering, hist


def census_34():
    hist = Counter()
    covering = 0
    t3 = {nz: even_table((0,) + nz) for nz in combinations(range(1, 32), 2)}
    t4 = {nz: even_table((0,) + nz) for nz in combinations(range(1, 32), 3)}
    for e0 in t3.values():
        for e1 in t4.values():
            r = dual_full(e0, e1)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
    return covering, hist


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]

    c25, h25 = census_25()
    c34, h34 = census_34()
    if c25 != claim["partition_25_covering"]:
        fail(f"25 covering {c25} != {claim['partition_25_covering']}")
    if c34 != claim["partition_34_covering"]:
        fail(f"34 covering {c34} != {claim['partition_34_covering']}")
    if min(h25) != 112 or set(h25) != {112}:
        fail(f"25 hist {dict(h25)}")
    if min(h34) != 112 or set(h34) != {112}:
        fail(f"34 hist {dict(h34)}")
    if h25[112] != c25 or h34[112] != c34:
        fail("histogram counts")

    # Champions
    w25_a, w25_b = (0, 1), (0, 2, 4, 8, 16)
    w34_a, w34_b = (0, 1, 2), (0, 4, 8, 16)
    r25 = dual_short(even_table(w25_b), 1)
    r34 = dual_full(even_table(w34_a), even_table(w34_b))
    if r25 != 112 or r34 != 112:
        fail(f"champion R {r25} {r34}")
    x25 = path_X(w25_a) + path_X(w25_b)
    x34 = path_X(w34_a) + path_X(w34_b)
    if x25 != 6 or x34 != 6:
        fail(f"champion X {x25} {x34}")
    if path_X((0,)) is not None:
        fail("length-1 should be invalid")

    floor = tariff(7, 112, 0)
    if floor != 490 or floor <= 436:
        fail(f"tariff floor {floor}")
    if tariff(7, 112, x25) < floor or tariff(7, 112, x34) < floor:
        fail("champion tariff below floor")

    print(
        "PASS_INDEPENDENT_PARTITIONED_WALKS_7Q",
        f"covering_25={c25}",
        f"covering_34={c34}",
        "partition_min_R=112",
        f"tariff_floor={floor}",
        "endpoint=436",
        "answers_independent_walks_partitioned",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
