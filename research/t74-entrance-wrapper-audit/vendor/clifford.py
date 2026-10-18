# SPDX-License-Identifier: Apache-2.0
"""Independent exact Clifford kernel on C^(2^9) (standard library only; imports no repository code).

Conventions (README section "Operator semantics"; cross-checked against HyperplaneEnd/Exact.lean,
Clifford.lean and the published #1415 / #702 operator digests):
- a basis index is an int x; bit i of x is axis i (least significant bit = axis 0);
- an F2 matrix is a list of 9 row bitmasks, (Gx)_i = parity(G[i] & x);
- a circuit is a list of gates, the first gate applied first;
- gates: ('P', G) |x> -> |Gx>; ('X', b) |x> -> |x ^ b>; ('D', Q, a) |x> -> i^q(x) |x> with
  q(x) = sum_{i in x} a_i + 2 sum_{i<j, i,j in x} Q_ij (strict upper triangle of Q read);
  ('PH', p) multiplies by i^p; ('C', q, s) with s = +1 or -1:
  v'[x] = ((1 + s i) v[x] + (1 - s i) v[x ^ q]) / 2, i.e. C(q, +1) = sqrt(X^q), C(q, -1) its inverse.
Amplitudes are Gaussian integers over 2^k, k = number of C gates executed.
"""
N_AXES = 9
DIM = 1 << N_AXES


def parity(x):
    return bin(x).count('1') & 1


def f2_rank(rows):
    piv = {}
    for x in rows:
        while x:
            b = x.bit_length() - 1
            if b not in piv:
                piv[b] = x
                break
            x ^= piv[b]
    return len(piv)


def transpose(rows):
    return [sum(((rows[j] >> i) & 1) << j for j in range(N_AXES)) for i in range(N_AXES)]


def apply_rows(rows, x):
    return sum(parity(r & x) << i for i, r in enumerate(rows))


def f2_inverse(rows):
    a = [r | (1 << (N_AXES + i)) for i, r in enumerate(rows)]
    for j in range(N_AXES):
        k = next((i for i in range(j, N_AXES) if (a[i] >> j) & 1), None)
        if k is None:
            raise ValueError('singular F2 matrix')
        a[j], a[k] = a[k], a[j]
        for i in range(N_AXES):
            if i != j and (a[i] >> j) & 1:
                a[i] ^= a[j]
    return [r >> N_AXES for r in a]


def basis_extend(U):
    out = []
    for x in list(U) + [1 << i for i in range(N_AXES)]:
        if f2_rank(out + [x]) > len(out):
            out.append(x)
    return out


def fourier(r, sign=1):
    """F_r: sqrt(X) (sign = +1) on axes 0..r-1."""
    return [('C', 1 << i, sign) for i in range(r)]


def adjoint(circuit):
    out = []
    for g in reversed(circuit):
        if g[0] == 'P':
            out.append(('P', f2_inverse(g[1])))
        elif g[0] == 'D':
            out.append(('D', g[1], [(-x) % 4 for x in g[2]]))
        elif g[0] == 'C':
            out.append(('C', g[1], -g[2]))
        elif g[0] == 'PH':
            out.append(('PH', (-g[1]) % 4))
        elif g[0] == 'X':
            out.append(g)
        else:
            raise ValueError('unknown gate %r' % (g,))
    return out


def frame_parts(U):
    """G (columns = extended basis), its inverse, the Z4 form Q = I + Gi^T Gi and its diagonal."""
    r = len(U)
    ext = basis_extend(U)
    if len(ext) != N_AXES or ext[:r] != list(U):
        raise ValueError('frame rows are not independent')
    G = transpose(ext)
    Gi = f2_inverse(G)
    c = transpose(Gi)
    Q = [(1 << i) ^ sum(parity(c[i] & c[j]) << j for j in range(N_AXES)) for i in range(N_AXES)]
    a = [(Q[i] >> i) & 1 for i in range(N_AXES)]
    return G, Gi, Q, a


def canonical_frame(U, shortcuts=True):
    """T_U = K^-1 F_r K with K = [P(G), D(Q, a)] (the frame's rows used exactly as stored)."""
    r = len(U)
    if shortcuts and r == 0:
        return []
    if shortcuts and r == N_AXES:
        return fourier(N_AXES)
    G, Gi, Q, a = frame_parts(U)
    K = [('P', G), ('D', Q, a)]
    return adjoint(K) + fourier(r) + K


def monomial(m, order='DPXPH'):
    """[D(Q, a), P(G), X(offset), PH(phase)] for a serialized record; order='PDXPH' is a control only."""
    Q, a, G, b, p = m['quadratic_rows'], m['linear_Z4'], m['matrix_rows'], m['offset'], m['phase']
    if order == 'PDXPH':
        return [('P', G), ('D', Q, a), ('X', b), ('PH', p)]
    if order != 'DPXPH':
        raise ValueError(order)
    return [('D', Q, a), ('P', G), ('X', b), ('PH', p)]


def well_formed(m):
    if not isinstance(m, dict) or set(m) != {'linear_Z4', 'matrix_rows', 'offset', 'phase', 'quadratic_rows'}:
        return False
    Q, a, G = m['quadratic_rows'], m['linear_Z4'], m['matrix_rows']
    if not all(isinstance(x, list) and len(x) == N_AXES and all(type(e) is int for e in x) for x in (Q, a, G)):
        return False
    if not (all(0 <= e < DIM for e in Q + G) and all(0 <= e < 4 for e in a)):
        return False
    if not (type(m['offset']) is int and 0 <= m['offset'] < DIM and type(m['phase']) is int and 0 <= m['phase'] < 4):
        return False
    if not all(((Q[i] >> j) & 1) == ((Q[j] >> i) & 1) for i in range(N_AXES) for j in range(N_AXES)):
        return False
    if not all(a[i] % 2 == (Q[i] >> i) & 1 for i in range(N_AXES)):
        return False
    return f2_rank(G) == N_AXES


def c_gates(circuit):
    return sum(1 for g in circuit if g[0] == 'C')


def _z4_phase(Q, a, x):
    lin = sum(a[i] for i in range(N_AXES) if (x >> i) & 1)
    quad = sum(parity((Q[i] >> (i + 1)) & (x >> (i + 1))) for i in range(N_AXES) if (x >> i) & 1)
    return (lin + 2 * quad) % 4


_UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def run(circuit, beta):
    """Evaluate the circuit on the packed identity: row y holds sum_x N[y, x] * 2^(beta x), real and imaginary
    parts separately, with N = 2^k times the operator matrix. Exact Python integers; no masking or carry."""
    re = [1 << (beta * y) for y in range(DIM)]
    im = [0] * DIM
    for g in circuit:
        kind = g[0]
        if kind == 'P':
            table = [apply_rows(g[1], x) for x in range(DIM)]
            if len(set(table)) != DIM:
                raise ValueError('P is not a bijection')
            r2, i2 = [0] * DIM, [0] * DIM
            for x in range(DIM):
                r2[table[x]] = re[x]
                i2[table[x]] = im[x]
            re, im = r2, i2
        elif kind == 'X':
            b = g[1]
            re = [re[x ^ b] for x in range(DIM)]
            im = [im[x ^ b] for x in range(DIM)]
        elif kind in ('D', 'PH'):
            r2, i2 = [0] * DIM, [0] * DIM
            for x in range(DIM):
                k = _z4_phase(g[1], g[2], x) if kind == 'D' else g[1]
                a, b = re[x], im[x]
                if k == 0:
                    r2[x], i2[x] = a, b
                elif k == 1:
                    r2[x], i2[x] = -b, a
                elif k == 2:
                    r2[x], i2[x] = -a, -b
                else:
                    r2[x], i2[x] = b, -a
            re, im = r2, i2
        elif kind == 'C':
            q, s = g[1], g[2]
            if s not in (1, -1) or not 0 < q < DIM:
                raise ValueError('bad C gate')
            r2, i2 = [0] * DIM, [0] * DIM
            for x in range(DIM):
                a, b = re[x], im[x]
                c, d = re[x ^ q], im[x ^ q]
                if s == 1:      # (1+i)(a+bi) + (1-i)(c+di)
                    r2[x], i2[x] = a - b + c + d, a + b - c + d
                else:           # (1-i)(a+bi) + (1+i)(c+di)
                    r2[x], i2[x] = a + b + c - d, b - a + c + d
            re, im = r2, i2
        else:
            raise ValueError('unknown gate %r' % (g,))
    return re, im


def radix(K):
    """beta = 2K + 2: with |numerator components| <= 4^k after k C gates (each C at most quadruples the
    largest component; P, X, D, PH permute or negate), scaled differences satisfy |d| <= 2 * 4^K < 2^beta."""
    return 2 * K + 2


def equal(side1, k1, side2, k2, beta):
    """Exact equality of the two operators (global phase included): scaled packed rows must coincide."""
    K = max(k1, k2)
    if beta < radix(K):
        raise ValueError('radix too small for a sound packed comparison')
    s1, s2 = K - k1, K - k2
    (r1, i1), (r2, i2) = side1, side2
    return all((r1[y] << s1) == (r2[y] << s2) and (i1[y] << s1) == (i2[y] << s2) for y in range(DIM))


def same_operator(c1, c2):
    """Run both circuits at the sound radix and compare exactly."""
    k1, k2 = c_gates(c1), c_gates(c2)
    beta = radix(max(k1, k2))
    return equal(run(c1, beta), k1, run(c2, beta), k2, beta)


def columns(side, beta):
    """Decode packed rows into {x: {y: (re, im)}} numerators (balanced digits; valid when every scaled digit
    is below 2^(beta-1) in absolute value)."""
    B, half = 1 << beta, 1 << (beta - 1)
    out = {}
    for y in range(DIM):
        digits = []
        for v in side[0][y], side[1][y]:
            ds = []
            for _ in range(DIM):
                d = v & (B - 1)
                if d >= half:
                    d -= B
                ds.append(d)
                v = (v - d) >> beta
            if v != 0:
                raise ValueError('packed row does not decode')
            digits.append(ds)
        for x in range(DIM):
            if digits[0][x] or digits[1][x]:
                out.setdefault(x, {})[y] = (digits[0][x], digits[1][x])
    return out


def lean_syntax(circuit):
    """The circuit in HyperplaneEnd/Exact.lean gate syntax, for structural comparison with its literals."""
    out = []
    for g in circuit:
        if g[0] == 'P':
            out.append(('pm', list(g[1]), f2_inverse(g[1])))
        elif g[0] == 'D':
            out.append(('dg', list(g[1]), list(g[2])))
        elif g[0] == 'C':
            out.append(('cg', g[1], g[2] == 1))
        elif g[0] == 'X':
            out.append(('xg', g[1]))
        else:
            out.append(('ph', g[1]))
    return out
