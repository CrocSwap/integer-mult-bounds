"""Implementation A: first-order jet system (J1) of #2162 Corollary J on unit-world sub-configurations
of the #2111 121-line pool, as F2 bitmask elimination.

Unit world: every nonzero entry is +-1, and any homomorphism phi: Q* -> K* into a field of characteristic 2 has
phi(-1) = 1 (phi(-1)^2 = 1 forces phi(-1) = 1 in characteristic 2), so phi p(t) = 1_{pi(t)}, phi q(s) = 1_{sigma(s)}.
Unknowns: X_i(t) (i in pi(t)) and Y_i(s) (i in sigma(s)). For an incidence (t, s) (t != s, p(t).q(s) = 0) with
D = pi(t) & sigma(s), (J1) reads sum_{i in D} (X_i(t) + Y_i(s)) = 0; for a harmonic line t (|D(t)| = 2),
delta'_t = sum_{i in D(t)} (X_i(t) + Y_i(t)).  All coefficients are in F2, so ranks and row-space membership are
the same over every field of characteristic 2.
Written for this package (thakrarsagar, with AI assistance from Claude Opus 5.5). Apache-2.0."""
import itertools


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def supp(x):
    return frozenset(i for i in range(3) if x[i])


def prim():
    """The 13 projective {-1,0,1}^3 vectors, first nonzero coordinate positive (as #2111 checks/mcc_cex.py)."""
    return [x for x in itertools.product((-1, 0, 1), repeat=3) if any(x) and next(c for c in x if c) > 0]


def pool():
    pr = prim()
    return [(p, q) for p in pr for q in pr if dot(p, q)]


def normalise(x):
    f = next(c for c in x if c)
    return tuple(c * f for c in x)  # f = +-1


class Jet:
    """(J1) on the sub-configuration given by a list of (p, q) lines."""

    def __init__(self, lines):
        self.lines = [tuple(map(tuple, l)) for l in lines]
        v = self.v = len(self.lines)
        self.var = {}
        for t, (p, q) in enumerate(self.lines):
            for i in sorted(supp(p)):
                self.var[('X', t, i)] = len(self.var)
            for i in sorted(supp(q)):
                self.var[('Y', t, i)] = len(self.var)
        self.n = len(self.var)
        self.inc = []  # (t, s, D) incidences with D nonempty
        for t in range(v):
            for s in range(v):
                if s != t and dot(self.lines[t][0], self.lines[s][1]) == 0:
                    D = supp(self.lines[t][0]) & supp(self.lines[s][1])
                    if D:
                        self.inc.append((t, s, D))
        self.harm = [t for t, (p, q) in enumerate(self.lines) if len(supp(p) & supp(q)) == 2]
        self.wild = [(t, s) for (t, s, D) in self.inc if len(D) == 3]

    def row(self, t, s, D):
        m = 0
        for i in D:
            m ^= 1 << self.var[('X', t, i)]
            m ^= 1 << self.var[('Y', s, i)]
        return m

    def delta(self, t):
        p, q = self.lines[t]
        return self.row(t, t, supp(p) & supp(q))

    def rows(self):
        return [self.row(t, s, D) for (t, s, D) in self.inc]

    def eliminate(self, track=False):
        """Echelon basis keyed by leading bit; with track=True also the combination of (J1) rows (int bitmask)."""
        basis = {}
        for k, m in enumerate(self.rows()):
            c = (1 << k) if track else 0
            while m:
                h = m.bit_length() - 1
                if h in basis:
                    bm, bc = basis[h]
                    m ^= bm
                    c ^= bc
                else:
                    basis[h] = (m, c)
                    break
        self.basis = basis
        return len(basis)

    def reduce(self, m):
        c = 0
        while m:
            h = m.bit_length() - 1
            if h not in self.basis:
                return m, None
            bm, bc = self.basis[h]
            m ^= bm
            c ^= bc
        return 0, c

    def immovable(self):
        if not hasattr(self, 'basis'):
            self.eliminate()
        return [t for t in self.harm if self.reduce(self.delta(t))[0] == 0]

    def flow(self, t):
        """A Lemma F flow: list of incidence indices whose (J1) rows sum to delta'_t (None if t is movable)."""
        self.eliminate(track=True)
        r, c = self.reduce(self.delta(t))
        if r:
            return None
        return [k for k in range(len(self.inc)) if c >> k & 1]

    def gauge_torus(self):
        """Explicit trivial first-order motions: per-object scalings (2v vectors) and the torus a in F2^3."""
        vecs = []
        for t, (p, q) in enumerate(self.lines):
            vecs.append(sum(1 << self.var[('X', t, i)] for i in supp(p)))
            vecs.append(sum(1 << self.var[('Y', t, i)] for i in supp(q)))
        for j in range(3):
            m = 0
            for t, (p, q) in enumerate(self.lines):
                if p[j]:
                    m |= 1 << self.var[('X', t, j)]
                if q[j]:
                    m |= 1 << self.var[('Y', t, j)]
            vecs.append(m)
        return vecs


def rank_of(vecs):
    basis = {}
    for m in vecs:
        while m:
            h = m.bit_length() - 1
            if h in basis:
                m ^= basis[h]
            else:
                basis[h] = m
                break
    return len(basis)


def signed_perms():
    out = []
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product((1, -1), repeat=3):
            out.append((perm, sg))
    return out


def act(g, x):
    perm, sg = g
    y = [0, 0, 0]
    for i in range(3):
        y[perm[i]] = sg[i] * x[i]
    return tuple(y)


def canon(lines):
    """Canonical form of a set of lines modulo the order-48 signed-permutation group (projective normalisation)."""
    best = None
    for g in signed_perms():
        img = tuple(sorted((normalise(act(g, p)), normalise(act(g, q))) for p, q in lines))
        if best is None or img < best:
            best = img
    return best
