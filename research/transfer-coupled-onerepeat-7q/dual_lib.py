"""Compile and load the dual_sum C helper (falls back to pure Python).

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INF = 99

_dual_c = None
_IntArr = ctypes.c_int * 32


def _compile_dual():
    # Each worker gets its own build directory. Never rewrite a mapped library.
    src = HERE / "dual.c"
    try:
        with tempfile.TemporaryDirectory(prefix="integer-mult-dual-") as tmp:
            so = Path(tmp) / "dual.so"
            subprocess.run(
                ["gcc", "-O3", "-shared", "-fPIC", "-o", str(so), str(src)],
                check=True, capture_output=True, text=True,
            )
            lib = ctypes.CDLL(str(so))
            lib.dual_sum.argtypes = [
                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ]
            lib.dual_sum.restype = ctypes.c_long
            return lib
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"failed to build private dual library: {exc}") from exc


def get_dual_c():
    global _dual_c
    if _dual_c is None:
        _dual_c = _compile_dual()
    return _dual_c


def dual_sum_c(e0, e1):
    """Return dual R or None if uncovered."""
    lib = get_dual_c()
    result = lib.dual_sum(_IntArr(*e0), _IntArr(*e1))
    if result < 0:
        return None
    return int(result)


def dual_sum_py(e0, e1):
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


def dual_sum(e0, e1):
    try:
        return dual_sum_c(e0, e1)
    except RuntimeError:
        return dual_sum_py(e0, e1)
