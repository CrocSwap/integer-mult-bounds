#!/usr/bin/env python3
"""Independent one-repeat (5,1,1) dual census at Q=7.

Does not import model.py or verify.py. Private dual path (ctypes or pure
Python). Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import ctypes
import json
import subprocess
import tempfile
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
INF = 99

_SO = None
_IntArr = ctypes.c_int * 32


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def _compile_dual_so():
    src = HERE / "dual.c"
    so = Path(tempfile.gettempdir()) / "tc_onerepeat_independent_dual.so"
    subprocess.run(
        ["gcc", "-O3", "-shared", "-fPIC", "-o", str(so), str(src)],
        check=True,
        capture_output=True,
        text=True,
    )
    return so


def _attach_dual():
    global _SO
    so = _compile_dual_so()
    lib = ctypes.CDLL(str(so))
    lib.dual_sum.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.dual_sum.restype = ctypes.c_long
    _SO = lib
    return lib


def dual(e0, e1):
    try:
        lib = _SO if _SO is not None else _attach_dual()
        result = lib.dual_sum(_IntArr(*e0), _IntArr(*e1))
        if result < 0:
            return None
        return int(result)
    except (OSError, subprocess.CalledProcessError):
        total = 0
        for m in range(1, 32):
            best = INF
            for a in range(32):
                c0 = e0[a]
                if c0 >= INF:
                    continue
                c1 = e1[a ^ m]
                if c1 < INF:
                    cost = c0 + c1
                    if cost < best:
                        best = cost
            if best >= INF:
                return None
            total += best
        return total


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


def dual_R(w0, w1):
    return dual(even_table(w0), even_table(w1))


def tariff(q, r, x, c=1):
    return 38 * q + 2 * r + 2 * x + c


def _prefix_chunk(threes):
    hist = Counter()
    covering = 0
    min_r = None
    for three in threes:
        for dbl in three:
            others = tuple(x for x in three if x != dbl)
            pref = (0,) + tuple(sorted((dbl, dbl) + others))
            rem = [x for x in range(1, 32) if x not in three]
            for sa, sb in combinations(rem, 2):
                r = dual_R(pref + (sa,), pref + (sb,))
                if r is None:
                    continue
                covering += 1
                hist[r] += 1
                if min_r is None or r < min_r:
                    min_r = r
    return covering, hist, min_r


def _suffix_chunk(fours):
    hist = Counter()
    covering = 0
    min_r = None
    for four in fours:
        pref = (0,) + four
        for c in four:
            for f in range(1, 32):
                if f in four:
                    continue
                sa, sb = (c, f) if c < f else (f, c)
                r = dual_R(pref + (sa,), pref + (sb,))
                if r is None:
                    continue
                covering += 1
                hist[r] += 1
                if min_r is None or r < min_r:
                    min_r = r
    return covering, hist, min_r


def census_prefix(workers=4):
    threes = list(combinations(range(1, 32), 3))
    with Pool(workers) as pool:
        parts = pool.map(_prefix_chunk, [threes[i::workers] for i in range(workers)])
    cov = 0
    hist = Counter()
    mr = None
    for c, h, m in parts:
        cov += c
        hist.update(h)
        if m is not None and (mr is None or m < mr):
            mr = m
    return cov, hist, mr


def census_suffix(workers=4):
    fours = list(combinations(range(1, 32), 4))
    with Pool(workers) as pool:
        parts = pool.map(_suffix_chunk, [fours[i::workers] for i in range(workers)])
    cov = 0
    hist = Counter()
    mr = None
    for c, h, m in parts:
        cov += c
        hist.update(h)
        if m is not None and (mr is None or m < mr):
            mr = m
    return cov, hist, mr


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]

    # Pure-Python dual check on pinned champions (no ctypes required).
    def dual_py(e0, e1):
        total = 0
        for m in range(1, 32):
            best = INF
            for a in range(32):
                c0 = e0[a]
                if c0 >= INF:
                    continue
                c1 = e1[a ^ m]
                if c1 < INF and c0 + c1 < best:
                    best = c0 + c1
            if best >= INF:
                return None
            total += best
        return total

    def even_py(slots):
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

    for kind in ("prefix_dup", "suffix_hit"):
        ch = cert[kind]["champion"]
        pref = tuple(ch["prefix"])
        sa = tuple(ch["suf_a"])
        sb = tuple(ch["suf_b"])
        r = dual_py(even_py(pref + sa), even_py(pref + sb))
        if r != ch["R"]:
            fail(f"python dual mismatch on {kind}: {r} != {ch['R']}")

    pcov, phist, pmin = census_prefix()
    scov, shist, smin = census_suffix()
    if pcov != 2499840 or pmin != 98 or dict(phist) != {98: 2499840}:
        fail(f"prefix census drift {pcov} {pmin} {dict(phist)}")
    if scov != 1666560 or smin != 96 or dict(shist) != {96: 1666560}:
        fail(f"suffix census drift {scov} {smin} {dict(shist)}")
    if pcov + scov != claim["combined_covering"]:
        fail("combined covering")
    if min(pmin, smin) != claim["one_repeat_min_R"]:
        fail("combined min R")
    if tariff(7, 96, 0, 1) != 459:
        fail("tariff floor")
    if tariff(7, 96, 0, 1) <= 436:
        fail("undercut")
    if claim["one_repeat_min_R"] <= claim["distinct_label_min_R"]:
        fail("must worsen distinct floor")

    print(
        "PASS_INDEPENDENT_TRANSFER_COUPLED_ONEREPEAT_7Q "
        f"prefix_min=98 suffix_min=96 combined_min=96 "
        f"covering={pcov + scov} tariff_floor=459 "
        "answers_all_shapes_oq1_onerepeat no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
