#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense linear algebra mod P = 2^31 - 1 on numpy int64 arrays (backend of tokdrop.py).

If python-flint is importable it is used (fast); otherwise a pure-numpy fallback runs.
Both backends return the same canonical objects (rank, reduced row echelon form, a
null-space basis spanning the same space), so engine verdicts do not depend on the backend.

  rank(A)            rank of A mod P
  rref(A)            (R, rank): canonical reduced row echelon form mod P
  nullspace(A)       n x k int64 basis of {x : A x = 0} (columns)
  matmul(A, B)       A @ B mod P without int64 overflow (float64 limbs, exact)
"""
import numpy as np

P = 2 ** 31 - 1
try:                                    # optional accelerator
    from flint import nmod_mat as _nm
except Exception:                       # pragma: no cover - depends on environment
    _nm = None
BACKEND = 'flint' if _nm is not None else 'numpy'


def _to_flint(A):
    A = np.asarray(A, dtype=np.int64) % P
    return _nm(A.shape[0], A.shape[1], [int(x) for x in A.ravel()], P)


def _from_flint(M):
    return np.array([[int(M[i, j]) for j in range(M.ncols())] for i in range(M.nrows())], dtype=np.int64).reshape(
        M.nrows(), M.ncols())


def _rref_np(A):
    A = np.array(A, dtype=np.int64) % P
    m, n = A.shape
    r = 0
    pivots = []
    for c in range(n):
        if r == m:
            break
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0:
            continue
        p = r + int(nz[0])
        if p != r:
            A[[r, p]] = A[[p, r]]
        inv = pow(int(A[r, c]), P - 2, P)
        A[r] = A[r] * inv % P
        col = A[:, c].copy()
        col[r] = 0
        rows = np.nonzero(col)[0]
        if len(rows):
            A[rows] = (A[rows] - (col[rows, None] * A[r][None, :]) % P) % P
        pivots.append(c)
        r += 1
    return A, r, pivots


def rank(A):
    A = np.asarray(A)
    if A.size == 0:
        return 0
    if _nm is not None:
        return _to_flint(A).rank()
    return _rref_np(A)[1]


def rref(A):
    A = np.asarray(A)
    if _nm is not None:
        R, rk = _to_flint(A).rref()
        return _from_flint(R), rk
    R, rk, _ = _rref_np(A)
    return R, rk


def nullspace(A):
    A = np.asarray(A, dtype=np.int64)
    n = A.shape[1]
    if _nm is not None:
        M = _to_flint(A)
        N, k = M.nullspace()
        return _from_flint(N)[:, :k].reshape(n, k)
    R, rk, piv = _rref_np(A)
    free = [c for c in range(n) if c not in set(piv)]
    out = np.zeros((n, len(free)), dtype=np.int64)
    for j, f in enumerate(free):
        out[f, j] = 1
        for i, c in enumerate(piv):
            out[c, j] = (-R[i, f]) % P
    return out


def matmul(A, B):
    """Exact A @ B mod P. Splits entries into 16/15-bit limbs so every float64 dot product is exact."""
    A = np.asarray(A, dtype=np.int64) % P
    B = np.asarray(B, dtype=np.int64) % P
    if A.shape[1] == 0:
        return np.zeros((A.shape[0], B.shape[1]), dtype=np.int64)
    assert A.shape[1] < (1 << 21), 'inner dimension too large for exact float64 limbs'
    a0 = (A & 0xFFFF).astype(np.float64)
    a1 = (A >> 16).astype(np.float64)
    b0 = (B & 0xFFFF).astype(np.float64)
    b1 = (B >> 16).astype(np.float64)
    m = lambda x, y: np.rint(x @ y).astype(np.int64) % P
    c00 = m(a0, b0)
    c01 = (m(a0, b1) + m(a1, b0)) % P
    c11 = m(a1, b1)
    s16 = pow(2, 16, P)
    s32 = pow(2, 32, P)
    return (c00 + c01 * s16 % P + c11 * s32 % P) % P
