"""Literal replay of complete programs on dense random F2 maps.

A schedule (word, ports, transfers per gap) becomes a full program of B, C and
A calls. Each nonzero mask m gets one A_m readout at each of two cuts on the
same connector whose dirt agrees and whose source parts differ by m. The
program then runs on random non-commuting maps with arbitrary dirt.
"""
import random


def program(word, ports, gaps, n=5):
    """Return (ops, cut list). ops are ('B', j, p), ('C',), and later ('A', m, p)."""
    ops, cuts = [], []
    z0 = q1 = par = 0
    def cut():
        cuts.append((len(ops), z0, par, q1))
    cut()
    for g in range(2 * n + 1):
        for _ in range(gaps[g]):
            ops.append(('C',))
            z0 ^= q1
            par ^= 1
            cut()
        if g < 2 * n:
            j = word[g]
            p = ports >> j & 1
            ops.append(('B', j, p))
            if p:
                q1 ^= 1 << j
            else:
                z0 ^= 1 << j
            cut()
    if par or z0 or q1:
        raise ValueError('schedule does not restore the connectors')
    return ops, cuts


def place_readouts(ops, cuts, n=5):
    """Insert two A_m calls per nonzero mask; raise if a mask is not covered."""
    inserts = []
    for m in range(1, 1 << n):
        found = None
        for a in range(len(cuts)):
            for b in range(a + 1, len(cuts)):
                pa, za, ra, qa = cuts[a]
                pb, zb, rb, qb = cuts[b]
                if qa ^ qb == m:
                    found = (pa, pb, 1)
                elif ra == rb and za ^ zb == m:
                    found = (pa, pb, 0)
                if found:
                    break
            if found:
                break
        if not found:
            raise ValueError('mask %d is not covered' % m)
        inserts += [(found[0], m, found[2]), (found[1], m, found[2])]
    out = list(ops)
    for pos, m, p in sorted(inserts, key=lambda t: -t[0]):
        out.insert(pos, ('A', m, p))
    return out


def matvec(rows, v):
    return sum((bin(r & v).count('1') & 1) << i for i, r in enumerate(rows))


def run(ops, n=5, width=4, trials=20, seed=0):
    """True when every trial computes y_m += sum_{j in m} A_m B_j x_j and restores z0, z1, x."""
    rng = random.Random(seed)
    lim = 1 << width
    for _ in range(trials):
        mat = lambda: [rng.randrange(lim) for _ in range(width)]
        B = [mat() for _ in range(n)]
        A = {m: mat() for m in range(1, 1 << n)}
        x = [rng.randrange(lim) for _ in range(n)]
        z = [rng.randrange(lim), rng.randrange(lim)]
        y0 = {m: rng.randrange(lim) for m in A}
        y, start, x0 = dict(y0), list(z), list(x)
        for op in ops:
            if op[0] == 'B':
                z[op[2]] ^= matvec(B[op[1]], x[op[1]])
            elif op[0] == 'C':
                z[0] ^= z[1]
            else:
                y[op[1]] ^= matvec(A[op[1]], z[op[2]])
        want = {m: y0[m] ^ _sum(matvec(A[m], matvec(B[j], x[j])) for j in range(n) if m >> j & 1) for m in A}
        if y != want or z != start or x != x0:
            return False
    return True


def _sum(values):
    out = 0
    for v in values:
        out ^= v
    return out
