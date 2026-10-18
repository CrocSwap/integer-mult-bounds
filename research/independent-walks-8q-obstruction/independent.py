#!/usr/bin/env python3
"""Independent partitioned dual-walk census at Q=8.

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


def _init_tables(tables):
    global _WORKER_TABLES
    _WORKER_TABLES = tables


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


def _work_pair_index(i):
    e0 = _WORKER_TABLES[0][i]
    hist = Counter()
    covering = 0
    for e1 in _WORKER_TABLES[1]:
        r = dual_full(e0, e1)
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


def census_26():
    tables = [even_table((0,) + nz) for nz in combinations(range(1, 32), 5)]
    n = max(1, os.cpu_count() or 2)
    chunk = max(1, (len(tables) + n * 4 - 1) // (n * 4))
    chunks = [tables[i : i + chunk] for i in range(0, len(tables), chunk)]
    with Pool(n) as pool:
        return _merge(pool.map(_work_short_chunk, chunks))


def census_35():
    t3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    t5 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 4)]
    n = max(1, os.cpu_count() or 2)
    with Pool(n, initializer=_init_tables, initargs=((t3, t5),)) as pool:
        return _merge(pool.map(_work_pair_index, range(len(t3))))


def census_44():
    t4 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 3)]
    n = max(1, os.cpu_count() or 2)
    with Pool(n, initializer=_init_tables, initargs=((t4, t4),)) as pool:
        return _merge(pool.map(_work_pair_index, range(len(t4))))


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]

    c26, h26 = census_26()
    c35, h35 = census_35()
    c44, h44 = census_44()
    if c26 != claim["partition_26_covering"]:
        fail(f"26 covering {c26} != {claim['partition_26_covering']}")
    if c35 != claim["partition_35_covering"]:
        fail(f"35 covering {c35} != {claim['partition_35_covering']}")
    if c44 != claim["partition_44_covering"]:
        fail(f"44 covering {c44} != {claim['partition_44_covering']}")
    if min(h26) != 92 or set(h26) != {92, 96, 104}:
        fail(f"26 hist {dict(h26)}")
    if min(h35) != 98 or set(h35) != {98, 104}:
        fail(f"35 hist {dict(h35)}")
    if min(h44) != 100 or set(h44) != {100, 104, 112}:
        fail(f"44 hist {dict(h44)}")
    if h26[92] != 1416576 or h26[96] != 1249920 or h26[104] != 1249920:
        fail("26 histogram counts")
    if h35[98] != 3124800 or h35[104] != 7291200:
        fail("35 histogram counts")
    if h44[100] != 3610880 or h44[104] != 9999360 or h44[112] != 555520:
        fail("44 histogram counts")

    w26_a, w26_b = (0, 16), (0, 1, 2, 4, 8, 15)
    w35_a, w35_b = (0, 1, 2), (0, 4, 8, 13, 16)
    w44_a, w44_b = (0, 1, 2, 4), (0, 7, 8, 16)
    r26 = dual_short(even_table(w26_b), 16)
    r35 = dual_full(even_table(w35_a), even_table(w35_b))
    r44 = dual_full(even_table(w44_a), even_table(w44_b))
    if r26 != 92 or r35 != 98 or r44 != 100:
        fail(f"champion R {r26} {r35} {r44}")
    x26 = path_X(w26_a) + path_X(w26_b)
    x35 = path_X(w35_a) + path_X(w35_b)
    x44 = path_X(w44_a) + path_X(w44_b)
    if x26 != 16 or x35 != 12 or x44 != 16:
        fail(f"champion X {x26} {x35} {x44}")
    if path_X((0,)) is not None:
        fail("length-1 should be invalid")

    floor = tariff(8, 92, 0)
    if floor != 488 or floor <= 436:
        fail(f"tariff floor {floor}")
    if tariff(8, 92, x26) < floor:
        fail("champion 26 tariff below floor")
    if tariff(8, 98, x35) < floor or tariff(8, 100, x44) < floor:
        fail("champion tariffs below floor")

    print(
        "PASS_INDEPENDENT_PARTITIONED_WALKS_8Q",
        f"covering_26={c26}",
        f"covering_35={c35}",
        f"covering_44={c44}",
        "partition_min_R=92",
        f"tariff_floor={floor}",
        "endpoint=436",
        "answers_priced_alphabet_q8_oq",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
