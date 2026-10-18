"""Independent cross-check engine (implementation B).

Written separately from model_a: states are tuples of row byte-masks, matrix
products are computed with explicit index loops over entries (no bit-slicing
tricks), and the group multiplication uses a directly constructed table.
Used to cross-check engine A on reachable-ball sizes, meet outcomes and the
formal-algebra products at the validated radii.

Standard library only.
"""

# group as 2x2 binary matrices packed 0..15, row major bits 0..3

def _mul(p, q):
    s = 0
    for i in range(2):
        for j in range(2):
            v = 0
            for k in range(2):
                v ^= ((p >> (2 * i + k)) & 1) & ((q >> (2 * k + j)) & 1)
            s |= v << (2 * i + j)
    return s

def _elts():
    out = []
    for m in range(16):
        det = (((m & 1) & ((m >> 3) & 1)) ^ (((m >> 1) & 1) & ((m >> 2) & 1)))
        if det == 1:
            out.append(m)
    return out

ELTS = _elts()
IDENT2 = 9
A_MAT = 11   # [[1,1],[0,1]]
B_MAT = 13   # [[1,0],[1,1]]
E_IDX = ELTS.index(IDENT2)
A_IDX = ELTS.index(A_MAT)
B_IDX = ELTS.index(B_MAT)
S_MAT = _mul(_mul(A_MAT, B_MAT), A_MAT)
S_IDX = ELTS.index(S_MAT)
MUL = [[ELTS.index(_mul(ELTS[i], ELTS[j])) for j in range(6)] for i in range(6)]


def rank_one_idempotents_b(r):
    out = set()
    for v in range(1, 1 << r):
        for phi in range(1 << r):
            if bin(v & phi).count('1') & 1 != 1:
                continue
            N = tuple(tuple((((phi >> j) & 1) if ((v >> i) & 1) else 0)
                            for j in range(r)) for i in range(r))
            out.add(N)
    return sorted(out)


def call_nats(gi, N, r):
    """engine-B natural image of I + ([g]+1)N, as tuple of 2r row masks"""
    g = ELTS[gi]
    n = 2 * r
    rows = [0] * n
    for i in range(r):
        for j in range(r):
            if N[i][j]:
                # block N[i][j] * (rho(g) + I2)
                for al in range(2):
                    for be in range(2):
                        bit = ((g >> (2 * al + be)) & 1) ^ ((1 if al == be else 0))
                        if bit:
                            rows[2 * i + al] |= 1 << (2 * j + be)
    for k in range(n):
        rows[k] ^= 1 << k
    return tuple(rows)


def mul_rows(X, Y, n):
    out = [0] * n
    for i in range(n):
        acc = 0
        for k in range(n):
            if (X[i] >> k) & 1:
                acc ^= Y[k]
        out[i] = acc
    return tuple(out)


def ball_b(depth, moves, r):
    n = 2 * r
    cur = {tuple(1 << i for i in range(n))}
    for _ in range(depth):
        nxt = set()
        for st in cur:
            for mv in moves:
                nxt.add(mul_rows(st, mv, n))
        cur = nxt
    return cur
