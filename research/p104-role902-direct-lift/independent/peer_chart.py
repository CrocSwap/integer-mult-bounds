#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Physical check of the two new chart pairs, with exact Gaussian dyadic arithmetic.

Standard library only; written for this package. The chart convention is the
one of the native verifiers retained in the repository (for example
research/current-serial-monomial-leaf/vendor/monomial/vendor/selected/native_verify.py,
function `frame`): a frame with basis vectors U of F2^9 is
    chart^-1 . C(e_0) ... C(e_{r-1}) . chart,   chart = P(G) then D(Q, diag Q),
where G is the transpose of U extended by unit vectors, Q_i = e_i xor
sum_j <c_i, c_j> e_j over the columns c of G^-1, P(G)|x> = |Gx>,
D(Q, l)|x> = i^(sum_{i in x} l_i + 2 sum_{i<j in x} Q_ij)|x>, and
C(d)|x> = ((1+i)|x> + (1-i)|x xor d>)/2.

A paid MOVE from chart a to chart b applies frame(a)^-1 then frame(b). For
each of the 512 basis inputs this script computes the output exactly and
requires: support inside x + span(b), exactly 2^g nonzero amplitudes, all
of squared modulus 2^-g, where g = dim b - dim a. For a Clifford operator
this is the statement that it is a rank-g child: monomial . g Fourier
factors . monomial. Controls: the same check on chart pairs that #7334
already uses with the same dimensions must pass, and a non-nested pair and a
frame with its quadratic phase removed must fail.
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 9


def require(cond, label):
    if not cond:
        raise AssertionError(label)


def parity(v):
    return bin(v).count('1') & 1


def mul(rows, v):
    return sum(parity(row & v) << i for i, row in enumerate(rows))


def transpose(rows):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(N))


def invert(rows):
    aug = [row | (1 << (N + i)) for i, row in enumerate(rows)]
    for j in range(N):
        p = next(i for i in range(j, N) if aug[i] >> j & 1)
        aug[j], aug[p] = aug[p], aug[j]
        for i in range(N):
            if i != j and aug[i] >> j & 1:
                aug[i] ^= aug[j]
    require([row & ((1 << N) - 1) for row in aug] == [1 << i for i in range(N)], 'invertible')
    return tuple(row >> N for row in aug)


def extend(vectors):
    cols, piv = [], {}
    for v in list(vectors) + [1 << i for i in range(N)]:
        w = v
        while w:
            j = w.bit_length() - 1
            if j not in piv:
                piv[j] = w
                cols.append(v)
                break
            w ^= piv[j]
    require(len(cols) == N, 'basis extension')
    return tuple(cols)


def frame(vectors, with_phase=True):
    r = len(vectors)
    if r == 0:
        return []
    fourier = [('C', 1 << i, 1) for i in range(r)]
    if r == N:
        return fourier
    G = transpose(extend(vectors))
    cols = transpose(invert(G))
    Q = tuple((1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(cols)) for i, a in enumerate(cols))
    lin = tuple((row >> i) & 1 for i, row in enumerate(Q))
    chart = [('P', G)] + ([('D', Q, lin)] if with_phase else [])
    inv = [('P', invert(g[1])) if g[0] == 'P' else ('D', g[1], tuple(-x % 4 for x in g[2])) for g in reversed(chart)]
    return inv + fourier + chart


def inverse_circuit(circ):
    out = []
    for g in reversed(circ):
        if g[0] == 'P':
            out.append(('P', invert(g[1])))
        elif g[0] == 'D':
            out.append(('D', g[1], tuple(-x % 4 for x in g[2])))
        else:
            out.append(('C', g[1], -g[2]))
    return out


ROT = (lambda a, b: (a, b), lambda a, b: (-b, a), lambda a, b: (-a, -b), lambda a, b: (b, -a))


def compile_gate(g):
    if g[0] == 'P':
        return ('P', [mul(g[1], x) for x in range(1 << N)])
    if g[0] == 'D':
        Q, lin = g[1], g[2]
        ph = []
        for x in range(1 << N):
            p = sum(lin[i] for i in range(N) if x >> i & 1)
            p += 2 * sum(parity((Q[i] >> (i + 1)) & (x >> (i + 1))) for i in range(N) if x >> i & 1)
            ph.append(p % 4)
        return ('D', ph)
    return g


def run(gates, x):
    """Exact output for input |x>: amplitudes (a + bi) / 2^den."""
    vec, den = {x: (1, 0)}, 0
    for g in gates:
        out = {}
        if g[0] == 'C':
            d, s = g[1], g[2]
            for y, (a, b) in vec.items():
                for t, (p, q) in ((y, (a - s * b, b + s * a)), (y ^ d, (a + s * b, b - s * a))):
                    u = out.get(t, (0, 0))
                    out[t] = (u[0] + p, u[1] + q)
            den += 1
            vec = {y: v for y, v in out.items() if v != (0, 0)}
        elif g[0] == 'P':
            vec = {g[1][y]: v for y, v in vec.items()}
        else:
            vec = {y: ROT[g[1][y]](*v) for y, v in vec.items()}
    return vec, den


def child_rank(a, b, phase_b=True):
    """Return g if frame(a)^-1 frame(b) is a rank-g child on every column, else raise."""
    gates = [compile_gate(g) for g in inverse_circuit(frame(a)) + frame(b, phase_b)]
    sb = {0}
    for v in b:
        sb |= {s ^ v for s in sb}
    g = len(b) - len(a)
    require(g >= 0, 'ascending pair')
    for x in range(1 << N):
        vec, den = run(gates, x)
        require(len(vec) == 1 << g, 'column %d support %d != 2^%d' % (x, len(vec), g))
        require(all((y ^ x) in sb for y in vec), 'column %d support inside x + span(b)' % x)
        mods = {a_ * a_ + b_ * b_ for a_, b_ in vec.values()}
        require(len(mods) == 1, 'column %d equal moduli' % x)
        # |amp|^2 = m / 4^den must equal 2^-g.
        require(mods.pop() * (1 << g) == 4 ** den, 'column %d modulus 2^-g/2' % x)
    return g


def main():
    W = json.loads(gzip.decompress((HERE / 'data' / 'word.json.gz').read_bytes()))
    B = json.loads(gzip.decompress((HERE / 'data' / 'base-7334-word.json.gz').read_bytes()))
    fr = W['frames']
    pairs = lambda X: sorted({(tuple(X['frames'][e[2]]), tuple(X['frames'][e[3]])) for e in X['program'] if e[0] == 'MOVE'})
    new = sorted(set(pairs(W)) - set(pairs(B)))
    require(len(new) == 2, 'two new pairs')
    for a, b in new:
        g = child_rank(a, b)
        print('PASS new pair %s -> %s: 512 columns, rank %d = dim gap' % (list(a), list(b), g))
    # Positive controls: #7334's own pairs with the same dimensions.
    shapes = {(len(a), len(b)) for a, b in new}
    seen = {}
    for a, b in pairs(B):
        k = (len(a), len(b))
        if k in shapes and len(seen.setdefault(k, [])) < 2:
            seen[k].append((a, b))
    for k, lst in sorted(seen.items()):
        for a, b in lst:
            require(child_rank(a, b) == k[1] - k[0], 'control pair')
            print('PASS control #7334 pair %d -> %d passes the same check' % k)
    # Negative controls.
    (a46, b46) = [p for p in new if len(p[0]) == 4][0]
    other = next(b for a, b in pairs(B) if len(b) == 6 and not set(a46) <= set(b))
    sb = {0}
    for v in other:
        sb |= {s ^ v for s in sb}
    require(not all(v in sb for v in a46), 'control target does not contain the source')
    try:
        child_rank(a46, other)
        raise RuntimeError('non-nested control passed')
    except AssertionError as exc:
        print('PASS control rejected: 4 -> 6 into a chart not containing the source (%s)' % exc)
    try:
        child_rank(a46, b46, phase_b=False)
        raise RuntimeError('phase control passed')
    except AssertionError as exc:
        print('PASS control rejected: 4 -> 6 with the target quadratic phase removed (%s)' % exc)
    print('PASS_NEW_CHART_PAIRS')


if __name__ == '__main__':
    sys.exit(main())
