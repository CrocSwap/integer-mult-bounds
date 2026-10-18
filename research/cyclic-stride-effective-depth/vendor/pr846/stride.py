"""Rounded stride-w cyclic first-order solver with linear sequential traffic.

Solves y_i = x_i + b_i * y_((i-w) mod L) for |b_i| <= 1-beta by a
Euclidean chain/closure recursion. Every array pass is in natural order
(or its reverse) and reads the lag-w predecessor from a FIFO built from two
stacks, which a fixed number of sequential tapes implement with amortized
O(1) record moves. See PROOF.md. Exact rational arithmetic is used; the only
inexactness is the explicit nearest-dyadic rounding on a grid of spacing u.
"""
from fractions import Fraction as F

ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, b): return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])
def norm2(a): return a[0] * a[0] + a[1] * a[1]


def div(a, b):
    d = norm2(b)
    if not d:
        raise ValueError('zero divisor')
    c = mul(a, (b[0], -b[1]))
    return (c[0] / d, c[1] / d)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rounded(a, bits):
    """Nearest point of the grid 2^-bits in each component, ties upward."""
    if bits is None:
        return a
    scale = 1 << bits

    def component(v):
        w = v * scale + F(1, 2)
        return F(w.numerator // w.denominator, scale)
    return (component(a[0]), component(a[1]))


class Tape:
    """Counts sequential record traffic. One unit is one B-bit record moved
    past a tape head (read or write). Stacks are tapes whose head sits at
    the top; a FIFO is two stacks; reversal copies one record per unit."""

    def __init__(self):
        self.records = 0
        self.levels = []


class Fifo:
    def __init__(self, tape, initial):
        self.tape = tape
        self.inbox = []
        self.outbox = []
        for v in initial:
            self.push(v)

    def push(self, v):
        self.tape.records += 1
        self.inbox.append(v)

    def pop(self):
        if not self.outbox:
            while self.inbox:  # one transfer per record, amortized O(1)
                self.tape.records += 2
                self.outbox.append(self.inbox.pop())
        self.tape.records += 1
        return self.outbox.pop()


def solve(x, b, w, bits, tape, trace=None, level=0):
    """Return the rounded solution. trace collects per-level (L, w, data,
    coefficients) for invariant checks. Values may be None in count-only
    mode (structure and traffic only)."""
    L = len(x)
    need(L >= 1 and len(b) == L, 'shape')
    w %= L
    if 2 * w > L:  # reverse orientation: stride L-w <= L/2
        tape.records += 2 * L  # read backwards, write forwards
        y = solve(x[::-1], b[::-1], L - w, bits, tape, trace, level)
        tape.records += 2 * L
        return y[::-1]
    tape.levels.append((L, w))
    if trace is not None:
        trace.append(dict(level=level, length=L, stride=w, x=x, b=b))
    count_only = x[0] is None
    if w == 0:  # every point is its own cycle
        tape.records += 2 * L
        if count_only:
            return [None] * L
        return [rounded(div(xi, sub(ONE, bi)), bits) for xi, bi in zip(x, b)]
    # Pass A: zero-seed chains along +w, with rounded chain products.
    fifo = Fifo(tape, [None] * w)
    z = [None] * L
    p = [None] * L
    for i in range(L):
        tape.records += 2  # read x_i, b_i
        prev = fifo.pop()
        if count_only:
            fifo.push(None)
            continue
        if prev is None:
            z[i], p[i] = x[i], b[i]
        else:
            z[i] = rounded(add(x[i], mul(b[i], prev[0])), bits)
            p[i] = rounded(mul(b[i], prev[1]), bits)
        fifo.push((z[i], p[i]))
    # Closure system on the w chain ends: Y_k = c_k + a_k Y_((k+L) mod w).
    c, a = z[L - w:], p[L - w:]
    tape.records += 2 * w  # the ends are the tail of the pass-A output
    Y = solve(c, a, (-L) % w, bits, tape, trace, level + 1)
    # Pass C: reseed chain starts from the closure values (Y_k feeds start k).
    fifo = Fifo(tape, Y)
    y = [None] * L
    for i in range(L):
        tape.records += 3  # read x_i, b_i; write y_i
        prev = fifo.pop()
        if not count_only:
            y[i] = rounded(add(x[i], mul(b[i], prev)), bits)
        fifo.push(y[i])
    return y


def levels(L, w):
    """Number of non-base recursion levels K (stride halves every level)."""
    K = 0
    while True:
        w %= L
        if 2 * w > L:
            w = L - w
        if w == 0:
            return K
        L, w, K = w, (-L) % w, K + 1


def exact_cycle_solve(x, b, w):
    """Independent oracle: per-cycle finite geometric closure."""
    L = len(x)
    y = [None] * L
    for i in range(L):
        total, weight, j = ZERO, ONE, i
        while True:
            total = add(total, mul(weight, x[j]))
            weight = mul(weight, b[j])
            j = (j - w) % L
            if j == i:
                break
        y[i] = div(total, sub(ONE, weight))
    return y


def solve_error_bound(B, beta, bits, K):
    """PROOF.md, Theorem 1: kappa*(u/beta)*(5+4B/beta)+u, kappa=min(K,1/beta)."""
    u = F(1, 1 << bits)
    kappa = min(F(max(K, 1)), 1 / beta)
    return kappa * (u / beta) * (5 + 4 * B / beta) + u


def admitted(beta, bits, K):
    u = F(1, 1 << bits)
    return beta <= F(1, 2) and u <= beta / 3 and u * 4 * (K + 1) <= beta
