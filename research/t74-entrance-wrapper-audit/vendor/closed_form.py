# SPDX-License-Identifier: Apache-2.0
"""Kernel B: closed-form amplitudes on C^(2^9), sparse exact columns (standard library only; no repository imports).

Conventions (as in #1781's README "Operator semantics"; bit i of an index is axis i, F2 matrices are lists of row
bitmasks, (Gx)_i = parity(G[i] & x)):

- frame operator, closed form: for a frame U of r independent rows, extend U by unit vectors to a basis, let G have
  those vectors as columns, h = G^-1, Q = I + h^T h, a = diag Q and q(x) = sum_{i in x} a_i + 2 sum_{i<j in x} Q_ij.
  Then T_U |x> = 2^-r sum_{delta < 2^r} i^(q(y) - q(x)) (1+i)^(r - |delta|) (1-i)^|delta| |y>, y = G (h x XOR delta);
  T_0 = I and T_FULL = F_9 (the 9-axis sqrt-X product).
- monomial record m: M |x> = i^(phase + q_m(x)) |G_m x XOR offset> with q_m from (quadratic_rows, linear_Z4).
- F_w: sqrt(X) on axes 0..w-1; on one axis, |b> -> ((1+i)|b> + (1-i)|b XOR 1>)/2.

A column is a dict {y: (re, im)} of Gaussian-integer numerators over a common 2^e (the exponent is carried
separately). Nothing here evaluates a gate list: T_U, M and F_w are applied from their formulas.
"""
DIM = 512
N_AXES = 9
_UNIT = ((1, 0), (0, 1), (-1, 0), (0, -1))     # i^k


def _par(x):
    return bin(x).count('1') & 1


def _mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _rank(rows):
    piv = {}
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in piv:
                x ^= piv[h]
            else:
                piv[h] = x
                break
    return len(piv)


def _apply(rows, x):
    return sum(_par(r & x) << i for i, r in enumerate(rows))


def _columns_to_rows(cols):
    return [sum(((cols[j] >> i) & 1) << j for j in range(N_AXES)) for i in range(N_AXES)]


def _invert(rows):
    """F2 inverse by solving G z = e_k for each k (exhaustive over the 512 vectors, independent of elimination)."""
    image = {_apply(rows, z): z for z in range(DIM)}
    if len(image) != DIM:
        raise ValueError('singular')
    cols = [image[1 << k] for k in range(N_AXES)]          # column k of G^-1
    return _columns_to_rows(cols)


def _phase(Q, a, x):
    lin = sum(a[i] for i in range(N_AXES) if (x >> i) & 1)
    quad = sum(((Q[i] >> j) & 1) for i in range(N_AXES) for j in range(i + 1, N_AXES) if (x >> i) & 1 and (x >> j) & 1)
    return (lin + 2 * quad) % 4


_PARTS = {}


def frame_parts(U):
    key = tuple(U)
    if key not in _PARTS:
        _PARTS[key] = _frame_parts(U)
    return _PARTS[key]


def _frame_parts(U):
    ext = []
    for x in list(U) + [1 << k for k in range(N_AXES)]:
        if _rank(ext + [x]) > len(ext):
            ext.append(x)
    if len(ext) != N_AXES or ext[:len(U)] != list(U):
        raise ValueError('frame rows not independent')
    G = _columns_to_rows(ext)
    h = _invert(G)
    hc = [sum(((h[i] >> j) & 1) << i for i in range(N_AXES)) for j in range(N_AXES)]   # columns of h
    Q = [sum(_par(hc[i] & hc[j]) << j for j in range(N_AXES)) ^ (1 << i) for i in range(N_AXES)]
    a = [(Q[i] >> i) & 1 for i in range(N_AXES)]
    table = [_phase(Q, a, z) for z in range(DIM)]
    return G, h, Q, a, table


def frame_column(U, x):
    """column x of T_U: ({y: (re, im)}, exponent e) with amplitudes = numerators / 2^e."""
    r = len(U)
    if r == 0:
        return {x: (1, 0)}, 0
    if r == N_AXES:
        G, h, q = None, None, lambda z: 0
        base = x
        img = lambda z: z            # noqa: E731
    else:
        G, h, Q, a, table = frame_parts(U)
        q = table.__getitem__
        base = _apply(h, x)
        img = lambda z: _apply(G, z)   # noqa: E731
    col = {}
    qx = q(x)
    for delta in range(1 << r):
        k = bin(delta).count('1')
        amp = (1, 0)
        for _ in range(r - k):
            amp = _mul(amp, (1, 1))
        for _ in range(k):
            amp = _mul(amp, (1, -1))
        y = img(base ^ delta)
        amp = _mul(amp, _UNIT[(q(y) - qx) % 4])
        col[y] = (col.get(y, (0, 0))[0] + amp[0], col.get(y, (0, 0))[1] + amp[1])
    return {y: v for y, v in col.items() if v != (0, 0)}, r


def monomial_apply(m, col):
    Q, a, G, b, p = m['quadratic_rows'], m['linear_Z4'], m['matrix_rows'], m['offset'], m['phase']
    out = {}
    for y, v in col.items():
        z = _apply(G, y) ^ b
        out[z] = _mul(v, _UNIT[(p + _phase(Q, a, y)) % 4])
    return out


def fourier_apply(w, col, e):
    for axis in range(w):
        bit = 1 << axis
        out = {}
        for y, v in col.items():
            for target, c in ((y, (1, 1)), (y ^ bit, (1, -1))):
                t = _mul(v, c)
                old = out.get(target, (0, 0))
                out[target] = (old[0] + t[0], old[1] + t[1])
        col = {y: v for y, v in out.items() if v != (0, 0)}
        e += 1
    return col, e


def _scaled(col, e, E):
    s = 1 << (E - e)
    return {y: (v[0] * s, v[1] * s) for y, v in col.items()}


def wrapper_identity(E_rows, U_rows, left, right, w):
    """L o F_w o R o T_E = T_U on every column, exactly (global phase included). Returns the first failing column or None."""
    for x in range(DIM):
        col, e = frame_column(E_rows, x)
        col = monomial_apply(right, col)
        col, e = fourier_apply(w, col, e)
        col = monomial_apply(left, col)
        ref, f = frame_column(U_rows, x)
        E = max(e, f)
        if _scaled(col, e, E) != _scaled(ref, f, E):
            return x
    return None


def kernel_digest_702(U):
    """#702's frame-kernel digest: numerators over 2^r, unreduced, columns x = 0..511, rows ascending."""
    import hashlib
    import json
    body = []
    for x in range(DIM):
        col, _ = frame_column(U, x)
        body.append([[y, col[y][0], col[y][1]] for y in sorted(col)])
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def matrix_digest_1415(E_rows, U_rows):
    """#1415's digest of T_U o T_E^-1: per column, reduce by 2 while all numerators are even."""
    import hashlib
    import json
    adj = [dict() for _ in range(DIM)]                     # T_E^dagger columns, built from T_E's columns
    for y in range(DIM):
        col, _ = frame_column(E_rows, y)
        for x, (re, im) in col.items():
            adj[x][y] = (re, -im)
    rE, rU = len(E_rows), len(U_rows)
    h, dens, nonzero = hashlib.sha256(), set(), 0
    tcols = [frame_column(U_rows, z)[0] for z in range(DIM)]
    for x in range(DIM):
        out = {}
        for z, v in adj[x].items():
            for y, u in tcols[z].items():
                t = _mul(u, v)
                old = out.get(y, (0, 0))
                out[y] = (old[0] + t[0], old[1] + t[1])
        col = {y: v for y, v in out.items() if v != (0, 0)}
        e = rE + rU
        while e > 0 and all(re % 2 == 0 and im % 2 == 0 for re, im in col.values()):
            col = {y: (re // 2, im // 2) for y, (re, im) in col.items()}
            e -= 1
        dens.add(e)
        nonzero += len(col)
        h.update((json.dumps([e, [[y, col[y][0], col[y][1]] for y in sorted(col)]], sort_keys=True, separators=(',', ':')) + '\n').encode())
    return h.hexdigest(), sorted(dens), nonzero
