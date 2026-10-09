"""Exact-mod-p subspace arithmetic in Q^h (p = 2^61 - 1; ranks over Q equal ranks mod p for these small integer
matrices with overwhelming probability; the release checkers recompute everything exactly)."""
P = (1 << 61) - 1


class Span:
    """row space given by an echelon list of (pivot, row); rows normalised at their pivot."""
    __slots__ = ('h', 'rows')

    def __init__(self, h, rows=()):
        self.h = h
        self.rows = list(rows)

    def copy(self):
        return Span(self.h, self.rows)

    def __len__(self):
        return len(self.rows)

    def reduce(self, u):
        u = [x % P for x in u]
        for p, r in self.rows:
            c = u[p]
            if c:
                u = [(x - c * y) % P for x, y in zip(u, r)]
        return u

    def insert(self, u):
        u = self.reduce(u)
        for p in range(self.h):
            if u[p]:
                inv = pow(u[p], P - 2, P)
                self.rows.append((p, [x * inv % P for x in u]))
                return True
        return False

    def contains(self, u):
        return not any(self.reduce(u))

    def add_span(self, other):
        """in place: self += other; returns self."""
        if len(self.rows) < self.h:
            for _, r in other.rows:
                self.insert(r)
                if len(self.rows) == self.h:
                    break
        return self

    def vectors(self):
        return [r for _, r in self.rows]


def span_of(h, vecs):
    s = Span(h)
    for u in vecs:
        if len(s) == h:
            break
        s.insert(u)
    return s


def kernel(K):
    """basis (list of vectors) of {x : k.x = 0 for k in K} (K a Span of covectors)."""
    h = K.h
    # bring K to reduced row echelon form
    rows = [list(r) for _, r in K.rows]
    piv = [p for p, _ in K.rows]
    for i in range(len(rows)):
        p = piv[i]
        for j in range(len(rows)):
            if j != i and rows[j][p]:
                c = rows[j][p]
                rows[j] = [(x - c * y) % P for x, y in zip(rows[j], rows[i])]
    pivset = set(piv)
    out = []
    for f in range(h):
        if f in pivset:
            continue
        x = [0] * h
        x[f] = 1
        for i, p in enumerate(piv):
            x[p] = (-rows[i][f]) % P
        out.append(x)
    return out


def gram_rank(B):
    """rank of the Gram matrix of the rows B under G' = 9I - J (G = I - J/9 up to the positive factor 9)."""
    k = len(B)
    if not k:
        return 0
    sums = [sum(b) % P for b in B]
    M = [[(9 * sum(x * y for x, y in zip(B[i], B[j])) - sums[i] * sums[j]) % P for j in range(k)] for i in range(k)]
    return len(span_of(k, M))


def nondegenerate(B):
    return gram_rank(B) == len(B)
