#!/usr/bin/env python3
"""Independent partitioned dual-walk census at Q=9 (binding (2,7) + champions).

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
INF = 99

_WORKER_TABLES = None


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
    reach0 = [(a, e0[a]) for a in range(32) if e0[a] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for a, c0 in reach0:
            c1 = e1[a ^ m]
            if c1 < INF:
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


def _work_short_chunk(chunk):
    hist = Counter()
    covering = 0
    for e in chunk:
        for sigma in range(1, 32):
            r = dual_short(e, sigma)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
    return covering, hist


def _merge(results):
    hist = Counter()
    covering = 0
    for c, h in results:
        covering += c
        hist.update(h)
    return covering, hist


def census_27():
    tables = [even_table((0,) + nz) for nz in combinations(range(1, 32), 6)]
    n = max(1, os.cpu_count() or 2)
    chunk = max(1, (len(tables) + n * 4 - 1) // (n * 4))
    chunks = [tables[i : i + chunk] for i in range(0, len(tables), chunk)]
    with Pool(n) as pool:
        return _merge(pool.map(_work_short_chunk, chunks))


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]

    c27, h27 = census_27()
    if c27 != claim["partition_27_covering"]:
        fail(f"27 covering {c27} != {claim['partition_27_covering']}")
    if min(h27) != 80:
        fail(f"27 min {min(h27)}")
    expected_hist = {
        80: 972160,
        82: 2041536,
        86: 6319040,
        88: 8749440,
        92: 972160,
        100: 1458240,
    }
    if dict(h27) != expected_hist:
        fail(f"27 hist {dict(h27)}")

    # Pinned (3,6)/(4,5) covering constants + champion recomputes (no full redo).
    if claim["partition_36_covering"] != 69370560:
        fail("36 covering constant")
    if claim["partition_45_covering"] != 122561600:
        fail("45 covering constant")
    if claim["partition_36_min_R"] != 88 or claim["partition_45_min_R"] != 92:
        fail("36/45 min constants")

    w27_a, w27_b = (0, 19), (0, 1, 2, 4, 8, 15, 16)
    w36_a, w36_b = (0, 1, 2), (0, 4, 8, 13, 16, 22)
    w45_a, w45_b = (0, 1, 2, 4), (0, 7, 8, 16, 25)
    r27 = dual_short(even_table(w27_b), 19)
    r36 = dual_full(even_table(w36_a), even_table(w36_b))
    r45 = dual_full(even_table(w45_a), even_table(w45_b))
    if r27 != 80 or r36 != 88 or r45 != 92:
        fail(f"champion R {r27} {r36} {r45}")
    x27 = path_X(w27_a) + path_X(w27_b)
    x36 = path_X(w36_a) + path_X(w36_b)
    x45 = path_X(w45_a) + path_X(w45_b)
    if x27 != 26 or x36 != 18 or x45 != 22:
        fail(f"champion X {x27} {x36} {x45}")
    if path_X((0,)) is not None:
        fail("length-1 should be invalid")

    floor = tariff(9, 80, 0)
    if floor != 502 or floor <= 436:
        fail(f"tariff floor {floor}")
    if floor <= 466:
        fail(f"floor {floor} should exceed same-walk Q9 floor 466")
    if tariff(9, 80, x27) < floor:
        fail("champion 27 tariff below floor")
    if tariff(9, 88, x36) < floor or tariff(9, 92, x45) < floor:
        fail("champion tariffs below floor")

    print(
        "PASS_INDEPENDENT_PARTITIONED_WALKS_9Q",
        f"covering_27={c27}",
        "partition_min_R=80",
        "covering_36=69370560",
        "covering_45=122561600",
        f"tariff_floor={floor}",
        "endpoint=436",
        "same_walk_q9_floor=466",
        "answers_threerepeat_oq2",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
