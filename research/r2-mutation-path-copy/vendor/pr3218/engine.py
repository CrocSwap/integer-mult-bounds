#!/usr/bin/env python3
"""Exact signed-Pauli action and an absolute phase anchor, for 1..9 axes.

Tekalign (@tekuuu), substantial OpenAI Codex assistance, Apache-2.0.
The complete tableau-plus-column criterion predates this implementation.
Gate conventions follow Sagar Thakrar's PR1781 kernel; bounded binary table
recurrences follow the credited PR662/2638 approach, independently coded here.
"""
from functools import lru_cache


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def inverse(rows):
    n = len(rows)
    a = [r | 1 << (n + j) for j, r in enumerate(rows)]
    for j in range(n):
        k = next((k for k in range(j, n) if a[k] >> j & 1), None)
        require(k is not None, 'singular P gate')
        a[k], a[j] = a[j], a[k]
        for k in range(n):
            if k != j and a[k] >> j & 1:
                a[k] ^= a[j]
    return tuple(r >> n for r in a)


def apply(rows, x):
    return sum(parity(r & x) << j for j, r in enumerate(rows))


def freeze(circuit, n):
    require(type(n) is int and 1 <= n <= 9, 'axis domain 1..9')
    require(isinstance(circuit, (list, tuple)), 'circuit sequence')
    out = []
    for g in circuit:
        require(isinstance(g, (list, tuple)) and len(g) > 0, 'gate sequence')
        kind = g[0]
        require(type(kind) is str and kind in ('P', 'D', 'C', 'X', 'PH'), 'unsupported gate')
        require(len(g) == (3 if kind in ('D', 'C') else 2), 'gate arity')
        if kind in ('P', 'D'):
            require(isinstance(g[1], (list, tuple)) and len(g[1]) == n and
                    all(type(r) is int and 0 <= r < 1 << n for r in g[1]), 'binary rows')
            if kind == 'P':
                out.append((kind, tuple(g[1])))
            else:
                require(isinstance(g[2], (list, tuple)) and len(g[2]) == n and
                        all(type(a) is int and 0 <= a < 4 for a in g[2]), 'Z4 linear coefficients')
                out.append((kind, tuple(g[1]), tuple(g[2])))
        elif kind == 'C':
            require(type(g[1]) is int and 0 < g[1] < 1 << n and
                    type(g[2]) is int and g[2] in (-1, 1), 'C gate domain')
            out.append(tuple(g))
        else:
            require(type(g[1]) is int and 0 <= g[1] < (4 if kind == 'PH' else 1 << n), 'offset/phase domain')
            out.append(tuple(g))
    # Validate both complete words even if their early tableaus will differ.
    for g in out:
        tables(g, n)
    return tuple(out)


@lru_cache(maxsize=64)
def tables(g, n):
    """Immutable gate tables only; never cache states or equality decisions."""
    kind = g[0]
    if kind == 'P':
        inv = inverse(g[1])
        inv_transpose = tuple(sum(((inv[j] >> i) & 1) << j for j in range(n)) for i in range(n))
        cols = [apply(g[1], 1 << j) for j in range(n)]
        table = [0] * (1 << n)
        for x in range(1, 1 << n):
            j = (x & -x).bit_length() - 1
            table[x] = table[x ^ (1 << j)] ^ cols[j]
        return tuple(table), inv_transpose
    if kind == 'D':
        q, a = g[1:]
        # The legacy semantics read only the strict upper triangle of Q.
        cross = tuple((q[j] & ~((1 << (j + 1)) - 1)) |
                      sum(((q[i] >> j) & 1) << i for i in range(j)) for j in range(n))
        derivative = tuple(cross[j] | ((a[j] & 1) << j) for j in range(n))
        table = [0] * (1 << n)
        for x in range(1, 1 << n):
            bit = x & -x
            j, y = bit.bit_length() - 1, x ^ bit
            table[x] = (table[y] + a[j] + 2 * parity(cross[j] & y)) % 4
        return tuple(table), derivative
    return ()


def pauli_action(word, n):
    """Images of X_j then Z_j, in the convention i^p X^x Z^z."""
    images = [(0, 1 << j, 0) for j in range(n)] + [(0, 0, 1 << j) for j in range(n)]
    for g in word:
        kind = g[0]
        updated = []
        for p, x, z in images:
            if kind == 'P':
                permutation, inv_t = tables(g, n)
                x, z = permutation[x], apply(inv_t, z)
            elif kind == 'D':
                phases, derivative = tables(g, n)
                p, z = p + phases[x], z ^ apply(derivative, x)
            elif kind == 'X':
                p += 2 * parity(z & g[1])
            elif kind == 'C' and parity(z & g[1]):
                p, x = p - g[2], x ^ g[1]
            updated.append((p % 4, x, z))
        images = updated
    return tuple(images)


def rotate(value, k):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[k % 4]


def anchor(word, n):
    """U|0>, as a sparse Gaussian-integer vector divided by 2^k."""
    state, k = {0: (1, 0)}, 0
    for g in word:
        kind = g[0]
        if kind == 'P':
            perm = tables(g, n)[0]
            state = {perm[x]: v for x, v in state.items()}
        elif kind == 'X':
            state = {x ^ g[1]: v for x, v in state.items()}
        elif kind in ('D', 'PH'):
            phases = tables(g, n)[0] if kind == 'D' else None
            state = {x: rotate(v, phases[x] if phases is not None else g[1]) for x, v in state.items()}
        else:
            q, s = g[1:]
            out = {}
            for x in state.keys() | {x ^ q for x in state}:
                a, b = state.get(x, (0, 0))
                c, d = state.get(x ^ q, (0, 0))
                v = (a - s * b + c + s * d, s * a + b - s * c + d)
                if v != (0, 0):
                    out[x] = v
            state, k = out, k + 1
    return state, k


def same_operator(first, second, n=9):
    """Exact operator equality, including global phase; no sampling."""
    a, b = freeze(first, n), freeze(second, n)
    if pauli_action(a, n) != pauli_action(b, n):
        return False
    (v, k), (w, ell) = anchor(a, n), anchor(b, n)
    if v.keys() != w.keys():
        return False
    K = max(k, ell)
    return all((v[x][0] << (K - k), v[x][1] << (K - k)) ==
               (w[x][0] << (K - ell), w[x][1] << (K - ell)) for x in v)
