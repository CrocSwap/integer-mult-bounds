#!/usr/bin/env python3
"""Independent shared-dirt partitioned dual census at Q=8.

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

EXPECTED_26_COVERING = 3916416
EXPECTED_26_MIN = 82
EXPECTED_26_HIST = {82: 583296, 88: 2916480, 96: 416640}
EXPECTED_35_COVERING = 10416000
EXPECTED_35_MIN = 82
EXPECTED_35_HIST = {82: 1458240, 88: 7291200, 96: 1666560}
EXPECTED_44_COVERING = 14165760
EXPECTED_44_MIN = 82
EXPECTED_44_HIST = {82: 1944320, 88: 9721600, 96: 2499840}
ENDPOINT = 436
FLOOR = 468


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_odd(slots):
    n = len(slots)
    even = [INF] * 32
    odd = [INF] * 32
    even[0] = 0
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        table = even if size % 2 == 0 else odd
        if size < table[value]:
            table[value] = size
    return even, odd


def shared_R(e0, o0, e1, o1):
    re = [(a, e0[a]) for a in range(32) if e0[a] < INF]
    ro = [(a, o0[a]) for a in range(32) if o0[a] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for a, c0 in re:
            c1 = e1[a ^ m]
            if c1 < INF:
                best = min(best, c0 + c1)
        for a, c0 in ro:
            c1 = o1[a ^ m]
            if c1 < INF:
                best = min(best, c0 + c1)
        if best >= INF:
            return None
        total += best
    return total


def shared_short(e1, o1, sigma):
    total = 0
    for m in range(1, 32):
        best = e1[m]
        t = e1[m ^ sigma]
        if t < INF:
            best = min(best, 2 + t)
        t = o1[m]
        if t < INF:
            best = min(best, 1 + t)
        t = o1[m ^ sigma]
        if t < INF:
            best = min(best, 1 + t)
        if best >= INF:
            return None
        total += best
    return total


def independent_R(e0, e1):
    re = [(a, e0[a]) for a in range(32) if e0[a] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for a, c0 in re:
            c1 = e1[a ^ m]
            if c1 < INF:
                best = min(best, c0 + c1)
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


def _chunk26(chunk):
    hist = Counter()
    covering = 0
    for e1, o1 in chunk:
        for sigma in range(1, 32):
            r = shared_short(e1, o1, sigma)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
    return covering, hist


_T = None


def _init(tables):
    global _T
    _T = tables


def _work35(i):
    e0, o0 = _T[0][i]
    hist = Counter()
    covering = 0
    for e1, o1 in _T[1]:
        r = shared_R(e0, o0, e1, o1)
        if r is None:
            continue
        covering += 1
        hist[r] += 1
    return covering, hist


def _work44(i):
    tables = _T[0]
    e0, o0 = tables[i]
    hist = Counter()
    covering = 0
    r = shared_R(e0, o0, e0, o0)
    if r is not None:
        covering += 1
        hist[r] += 1
    for j in range(i + 1, len(tables)):
        e1, o1 = tables[j]
        r = shared_R(e0, o0, e1, o1)
        if r is None:
            continue
        covering += 2
        hist[r] += 2
    return covering, hist


def census_26():
    tables = [even_odd((0,) + nz) for nz in combinations(range(1, 32), 5)]
    n = max(1, os.cpu_count() or 2)
    chunk = max(1, (len(tables) + n * 4 - 1) // (n * 4))
    chunks = [tables[i : i + chunk] for i in range(0, len(tables), chunk)]
    with Pool(n) as pool:
        results = pool.map(_chunk26, chunks)
    hist = Counter()
    covering = 0
    for c, h in results:
        covering += c
        hist.update(h)
    if covering != EXPECTED_26_COVERING:
        fail(f"26 covering {covering}")
    if min(hist) != EXPECTED_26_MIN:
        fail(f"26 min {min(hist)}")
    if dict(hist) != EXPECTED_26_HIST:
        fail(f"26 hist {dict(hist)}")
    return covering, min(hist)


def census_35():
    t3 = [even_odd((0,) + nz) for nz in combinations(range(1, 32), 2)]
    t5 = [even_odd((0,) + nz) for nz in combinations(range(1, 32), 4)]
    n = max(1, os.cpu_count() or 2)
    with Pool(n, initializer=_init, initargs=((t3, t5),)) as pool:
        results = pool.map(_work35, range(len(t3)))
    hist = Counter()
    covering = 0
    for c, h in results:
        covering += c
        hist.update(h)
    if covering != EXPECTED_35_COVERING:
        fail(f"35 covering {covering}")
    if min(hist) != EXPECTED_35_MIN:
        fail(f"35 min {min(hist)}")
    if dict(hist) != EXPECTED_35_HIST:
        fail(f"35 hist {dict(hist)}")
    return covering, min(hist)


def census_44():
    t4 = [even_odd((0,) + nz) for nz in combinations(range(1, 32), 3)]
    n = max(1, os.cpu_count() or 2)
    with Pool(n, initializer=_init, initargs=((t4,),)) as pool:
        results = pool.map(_work44, range(len(t4)))
    hist = Counter()
    covering = 0
    for c, h in results:
        covering += c
        hist.update(h)
    if covering != EXPECTED_44_COVERING:
        fail(f"44 covering {covering}")
    if min(hist) != EXPECTED_44_MIN:
        fail(f"44 min {min(hist)}")
    if dict(hist) != EXPECTED_44_HIST:
        fail(f"44 hist {dict(hist)}")
    return covering, min(hist)


def champions():
    checks = [
        ((0, 16), (0, 1, 2, 4, 8, 15), 82, 92),
        ((0, 1, 2), (0, 4, 8, 15, 16), 82, None),
        ((0, 1, 2, 4), (0, 8, 15, 16), 82, None),
    ]
    for w0, w1, expect_s, expect_i in checks:
        e0, o0 = even_odd(w0)
        e1, o1 = even_odd(w1)
        rs = shared_R(e0, o0, e1, o1)
        ri = independent_R(e0, e1)
        if rs != expect_s:
            fail(f"champ shared {w0} {w1} -> {rs}")
        if ri is None or rs >= ri:
            fail(f"shared should beat independent on {w0}")
        if expect_i is not None and ri != expect_i:
            fail(f"ind champ {ri}")
        if path_X(w0) is None or path_X(w1) is None:
            fail("path")
    # Short-long identity.
    e1, o1 = even_odd((0, 1, 2, 4, 8, 15))
    if shared_short(e1, o1, 16) != 82:
        fail("short-long")
    floor = tariff(8, 82, 0)
    if floor != FLOOR or floor <= ENDPOINT:
        fail(f"tariff floor {floor}")


def main():
    pinned = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    champions()
    c26, m26 = census_26()
    c35, m35 = census_35()
    c44, m44 = census_44()
    claim = pinned["claim"]
    if claim["shared_dirt_26_covering"] != c26 or claim["shared_dirt_26_min_R"] != m26:
        fail("26 claim drift")
    if claim["shared_dirt_35_covering"] != c35 or claim["shared_dirt_35_min_R"] != m35:
        fail("35 claim drift")
    if claim["shared_dirt_44_covering"] != c44 or claim["shared_dirt_44_min_R"] != m44:
        fail("44 claim drift")
    if claim["partition_min_R"] != min(m26, m35, m44):
        fail("partition min")
    if claim["tariff_floor_at_X0"] != FLOOR:
        fail("floor claim")
    if claim["undercuts_436_after_complete_bill"] is not False:
        fail("undercut claim")
    if claim["beats_independent_dirt_floors"] is not True:
        fail("beats claim")
    if claim["endpoint_Q6_tariff"] != ENDPOINT:
        fail("endpoint")
    print(
        "PASS_SHARED_DIRT_WALKS_8Q",
        f"covering_26={c26}",
        f"covering_35={c35}",
        f"covering_44={c44}",
        f"partition_min_R={min(m26, m35, m44)}",
        f"tariff_floor={FLOOR}",
        "beats_independent_dirt_floors",
        "no_undercut_436",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
