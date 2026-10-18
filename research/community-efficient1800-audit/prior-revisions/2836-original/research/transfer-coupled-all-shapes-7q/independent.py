#!/usr/bin/env python3
"""Independent transfer-coupled companion census at Q=7.

Does not import model.py or verify.py. Uses the same dual.c formula via a
private ctypes load (or pure Python fallback). Prepared by Wentao Li with
substantial AI assistance. Apache-2.0.
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

COMPANIONS = (
    (1, 1, 5),
    (1, 2, 4),
    (1, 3, 3),
    (2, 1, 4),
    (2, 2, 3),
    (3, 1, 3),
    (3, 2, 2),
)

_SO = None
_SO_PATH = None
_IntArr = ctypes.c_int * 32


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def _compile_dual_so():
    global _SO_PATH
    src = HERE / "dual.c"
    so = Path(tempfile.gettempdir()) / "tc7q_independent_dual.so"
    subprocess.run(
        ["gcc", "-O3", "-shared", "-fPIC", "-o", str(so), str(src)],
        check=True,
        capture_output=True,
        text=True,
    )
    _SO_PATH = so
    return so


def _attach_dual(so_path=None):
    global _SO
    path = Path(so_path) if so_path is not None else _compile_dual_so()
    lib = ctypes.CDLL(str(path))
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


def tariff(q, r, x, c=1):
    return 38 * q + 2 * r + 2 * x + c


def _chunk(args):
    p, a, b, prefs = args
    # Fresh dual load inside worker.
    hist = Counter()
    covering = 0
    min_r = None
    for pn in prefs:
        rem = [x for x in range(1, 32) if x not in pn]
        pref = (0,) + tuple(pn)
        Asets = list(combinations(rem, a))
        Atables = {A: even_table(pref + A) for A in Asets}
        if a == b:
            for i, A in enumerate(Asets):
                sa = set(A)
                ea = Atables[A]
                for B in Asets[i + 1 :]:
                    if sa & set(B):
                        continue
                    r = dual(ea, Atables[B])
                    if r is None:
                        continue
                    covering += 1
                    hist[r] += 1
                    if min_r is None or r < min_r:
                        min_r = r
        else:
            Bsets = list(combinations(rem, b))
            Btables = {B: even_table(pref + B) for B in Bsets}
            for A, ea in Atables.items():
                sa = set(A)
                for B, eb in Btables.items():
                    if sa & set(B):
                        continue
                    r = dual(ea, eb)
                    if r is None:
                        continue
                    covering += 1
                    hist[r] += 1
                    if min_r is None or r < min_r:
                        min_r = r
    return covering, hist, min_r


def _pool_init(so_path):
    """Preload the shared dual library once per worker."""
    _attach_dual(so_path)


def census(p, a, b, workers=4):
    prefs = list(combinations(range(1, 32), p - 1))
    chunks = [(p, a, b, prefs[i::workers]) for i in range(workers)]
    so_path = _compile_dual_so()
    with Pool(workers, initializer=_pool_init, initargs=(str(so_path),)) as pool:
        parts = pool.map(_chunk, chunks)
    hist = Counter()
    covering = 0
    min_r = None
    for cov, h, mr in parts:
        covering += cov
        hist.update(h)
        if mr is not None and (min_r is None or mr < min_r):
            min_r = mr
    return covering, hist, min_r


def x0_covering_511():
    def nbrs(v):
        return [v ^ (1 << i) for i in range(5)]

    paths = [(0,)]
    for _ in range(4):
        paths = [p + (w,) for p in paths for w in nbrs(p[-1]) if w not in p]
    covering = 0
    for pref in paths:
        end = pref[-1]
        used = set(pref)
        cands = [
            sa
            for sa in (1, 2, 4, 8, 16)
            if sa not in used and (end ^ sa).bit_count() == 1
        ]
        for i, sa in enumerate(cands):
            for sb in cands[i + 1 :]:
                r = dual(even_table(pref + (sa,)), even_table(pref + (sb,)))
                if r is not None:
                    covering += 1
    return covering


def dual_py_champ(e0, e1):
    """Separate pure-Python dual for the critical champion cross-check."""
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


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]
    if claim["global_covering_min_R"] != 84:
        fail("cert global min")
    if claim["tariff_floor_after_complete_bill"] != 439:
        fail("cert floor")
    if claim["undercuts_436_after_complete_bill"] is not False:
        fail("cert undercut flag")

    # Warm the dual helper for the X=0 lemma and champion check.
    try:
        _attach_dual(_compile_dual_so())
    except (OSError, subprocess.CalledProcessError):
        pass

    x0 = x0_covering_511()
    if x0 != 0:
        fail(f"X0 covering {x0}")

    ch = cert["critical_5_1_1"]["champion"]
    pref = tuple(ch["prefix"])
    sa = tuple(ch["suf_a"])
    sb = tuple(ch["suf_b"])
    r = dual_py_champ(even_table(pref + sa), even_table(pref + sb))
    if r != 84:
        fail(f"critical champ R {r}")

    companions = cert.get("companion_shapes") or {}
    for p, a, b in COMPANIONS:
        key = f"{p}_{a}_{b}"
        covering, hist, min_r = census(p, a, b)
        pinned = companions.get(key)
        if pinned is None:
            fail(f"missing companion {key}")
        if covering != pinned["covering_pairs"]:
            fail(f"{key} covering {covering} != {pinned['covering_pairs']}")
        if min_r != pinned["min_R"]:
            fail(f"{key} min_R {min_r} != {pinned['min_R']}")
        if {str(k): hist[k] for k in sorted(hist)} != pinned["histogram"]:
            fail(f"{key} histogram drift")
        if min_r < 86:
            fail(f"{key} broke R>=86 companion floor")

    floor = tariff(7, 84, 2, 1)
    if floor != 439 or floor <= 436:
        fail(f"tariff floor {floor}")
    if tariff(7, 86, 0, 1) != 439:
        fail("R86 floor")

    print(
        "PASS_INDEPENDENT_TRANSFER_COUPLED_7Q",
        f"companions={len(COMPANIONS)}",
        "critical_champ_R=84",
        "x0_covering=0",
        "tariff_floor=439",
        "answers_independent_walks_transfer_coupled",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
