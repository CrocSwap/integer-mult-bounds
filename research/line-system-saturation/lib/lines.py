"""Line systems over the integers/rationals: the non-orthogonality adjacency A-bar over F2 (bit rows), its symplectic labels, the dense window.
Standard library only.  Vectors are tuples of ints/Fractions; a 'line system' is a list of vectors (one per line, distinct up to sign)."""
from exact import rank_f2


def parity(x):
    return x.bit_count() & 1


def abar_rows(G):
    """A-bar_ts = 1 iff t != s and G_ts != 0, as a list of int bit rows (bit s of row t)."""
    n = len(G)
    return [sum((1 << s) for s in range(n) if s != t and G[t][s] != 0) for t in range(n)]


def apply(rows, x):
    """A x over F2 for a symmetric matrix given by bit rows, x an int bit vector (bit s = coordinate s)."""
    out = 0
    s = 0
    while x:
        if x & 1:
            out ^= rows[s]
        x >>= 1
        s += 1
    return out


def alt_labels(rows):
    """Symplectic factorisation A-bar = L^T b L (b standard).  Returns (labels, k) with labels[t] an int whose bit 2i is a_i(t), bit 2i+1 is c_i(t).
    Self-verifying: raises AssertionError unless b(l_t, l_s) = A-bar_ts for ALL pairs and rank = 2k."""
    v = len(rows)
    for t in range(v):
        assert not (rows[t] >> t) & 1, "diagonal must be zero (alternating)"
        for s in range(t):
            assert ((rows[t] >> s) & 1) == ((rows[s] >> t) & 1), "must be symmetric"
    W = [1 << t for t in range(v)]
    es, fs = [], []
    while True:
        found = None
        for xi, x in enumerate(W):
            Ax = apply(rows, x)
            for yi, y in enumerate(W):
                if yi != xi and parity(y & Ax):
                    found = (xi, yi, Ax)
                    break
            if found:
                break
        if not found:
            break
        xi, yi, Ax = found
        x, y = W[xi], W[yi]
        Ay = apply(rows, y)
        new = []
        for wi, w in enumerate(W):
            if wi in (xi, yi):
                continue
            w2 = w ^ (x if parity(w & Ay) else 0) ^ (y if parity(w & Ax) else 0)
            new.append(w2)
        es.append(x)
        fs.append(y)
        W = new
    k = len(es)
    # unit vector delta_t = sum_i [A(t,f_i) e_i + A(t,e_i) f_i] + radical, so a_i(t) = (A f_i)_t, c_i(t) = (A e_i)_t
    a = [apply(rows, f) for f in fs]
    c = [apply(rows, e) for e in es]
    labels = [0] * v
    for t in range(v):
        l = 0
        for i in range(k):
            l |= ((a[i] >> t) & 1) << (2 * i)
            l |= ((c[i] >> t) & 1) << (2 * i + 1)
        labels[t] = l
    # verify A-bar = sum_i (a_i c_i^T + c_i a_i^T) as bit rows
    for t in range(v):
        r = 0
        for i in range(k):
            if (a[i] >> t) & 1:
                r ^= c[i]
            if (c[i] >> t) & 1:
                r ^= a[i]
        assert r == rows[t], "symplectic factorisation failed"
    assert rank_f2(rows) == 2 * k
    return labels, k


def window(rows):
    """(rank_F2(A-bar), rank_F2(J + A-bar), whether the all-ones vector lies in the column space of A-bar)."""
    v = len(rows)
    ones = (1 << v) - 1
    r = rank_f2(rows)
    h = rank_f2([ones ^ x for x in rows])
    inc = rank_f2(rows + [ones]) == r
    return r, h, inc


def gram_int(V, div=1):
    """Integer Gram matrix (exact) of int vectors, divided by div (asserted exact); upper triangle computed once."""
    n = len(V)
    G = [[0] * n for _ in range(n)]
    for a in range(n):
        va = V[a]
        for b in range(a, n):
            d = sum(x * y for x, y in zip(va, V[b]))
            assert d % div == 0
            G[a][b] = G[b][a] = d // div
    return G
