# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Independent Lemma G checker: imports no package script.
"""Exact Gaussian-dyadic batch vectors on C^(2^9) and an independent applier for Clifford circuit primitives.

A register value is (re + i*im) / 2^d with re, im int64 arrays of shape (512, k) (k simultaneous input columns).
Every operation asserts |numerator| < 2^60 afterwards, so int64 never wraps: a result is exact or the run aborts.

Primitive semantics (written here from the documented conventions of the vendored compiler, not imported):
  ('P', G)          v'[G x] = v[x]                (G given by its 9 rows over F2)
  ('X', b)          v'[x]   = v[x ^ b]
  ('D', Q, alpha)   v'[x]   = i^(sum_i alpha_i x_i + 2 sum_{i<j} Q_ij x_i x_j) v[x]
  ('phase', p)      v'      = i^p v
  ('C', q, s)       v'[x]   = ((1 + s i) v[x] + (1 - s i) v[x ^ q]) / 2
Inverse primitives: P -> G^-1, D -> conjugate phases, X -> X, phase -> -p, C(q,s) -> C(q,-s).
`selftest()` compares this applier with the vendored compiler's own state-vector routine on basis vectors."""
import numpy as np

N = 512; n = 9
XS = np.arange(N, dtype=np.int64)
LIM = 1 << 60


def par(x): return bin(x).count('1') & 1


def mv(rows, x): return sum(par(r & x) << i for i, r in enumerate(rows))


_pcache = {}
def pidx(G):
    G = tuple(G)
    if G not in _pcache: _pcache[G] = np.array([mv(G, x) for x in range(N)], dtype=np.int64)
    return _pcache[G]


_dcache = {}
def qarr(Q, alpha):
    key = (tuple(Q), tuple(alpha))
    if key not in _dcache:
        out = np.zeros(N, dtype=np.int64)
        for x in range(N):
            s = sum(alpha[i] for i in range(n) if x >> i & 1)
            s += 2 * sum(1 for i in range(n) for j in range(i + 1, n) if x >> i & 1 and x >> j & 1 and Q[i] >> j & 1)
            out[x] = s % 4
        _dcache[key] = out
    return _dcache[key]


class GD:
    __slots__ = ('re', 'im', 'd')
    def __init__(self, re, im, d=0): self.re, self.im, self.d = re, im, d
    @staticmethod
    def zeros(k): return GD(np.zeros((N, k), np.int64), np.zeros((N, k), np.int64), 0)
    def copy(self): return GD(self.re.copy(), self.im.copy(), self.d)
    def k(self): return self.re.shape[1]
    def guard(self):
        if self.re.size and (np.abs(self.re).max() >= LIM or np.abs(self.im).max() >= LIM): raise OverflowError('int64 guard')
    def norm(self):
        while self.d > 0 and not np.any((self.re | self.im) & 1):
            self.re >>= 1; self.im >>= 1; self.d -= 1
        return self
    def is_zero(self): return not np.any(self.re) and not np.any(self.im)
    def equals(self, o):
        a = self.copy().norm(); b = o.copy().norm()
        if a.is_zero() and b.is_zero(): return True
        return a.d == b.d and np.array_equal(a.re, b.re) and np.array_equal(a.im, b.im)
    def mul_ipow(self, q):            # q: scalar or (512,) array of exponents mod 4
        q = np.asarray(q) % 4
        if q.ndim: q = q[:, None]
        re, im = self.re, self.im
        nre = np.where(q == 0, re, np.where(q == 1, -im, np.where(q == 2, -re, im)))
        nim = np.where(q == 0, im, np.where(q == 1, re, np.where(q == 2, -im, -re)))
        self.re, self.im = nre, nim
        return self
    def apply_prim(self, p, inverse=False):
        t = p[0]
        if t == 'P':
            idx = pidx(p[1])
            if inverse: self.re, self.im = self.re[idx], self.im[idx]
            else:
                r = np.empty_like(self.re); i = np.empty_like(self.im); r[idx] = self.re; i[idx] = self.im; self.re, self.im = r, i
        elif t == 'X':
            idx = XS ^ p[1]; self.re, self.im = self.re[idx], self.im[idx]
        elif t == 'D':
            q = qarr(p[1], p[2]); self.mul_ipow(-q if inverse else q)
        elif t == 'phase':
            self.mul_ipow(-p[1] if inverse else p[1])
        elif t == 'C':
            q, s = p[1], p[2]
            if inverse: s = -s
            idx = XS ^ q; wr, wi = self.re[idx], self.im[idx]
            re, im = self.re, self.im
            self.re = re - s * im + wr + s * wi
            self.im = im + s * re + wi - s * wr
            self.d += 1
        else: raise ValueError(p)
        self.guard()
        return self
    def apply_circ(self, circ, inverse=False):
        for p in (reversed(circ) if inverse else circ): self.apply_prim(p, inverse)
        return self.norm()
    def add_scaled(self, src, num, den):
        """self += (num/den) * src, den a power of two"""
        assert den > 0 and den & (den - 1) == 0
        e = den.bit_length() - 1
        D = max(self.d, src.d + e)
        a = self.re << (D - self.d); b = self.im << (D - self.d)
        sh = D - src.d - e
        a = a + num * (src.re << sh); b = b + num * (src.im << sh)
        self.re, self.im, self.d = a, b, D
        self.guard(); return self.norm()
    def scale(self, num, den):
        assert den > 0 and den & (den - 1) == 0
        self.re = self.re * num; self.im = self.im * num; self.d += den.bit_length() - 1
        self.guard(); return self.norm()


def circ_of(op):
    """primitive list of a vendored Op (used only to read the DEFINITION of canonical frames / gates)"""
    return [tuple(e) for e in op.circuit]


def monomial_circ(rec):
    """decode a serialized Gaussian monomial: diag(Q, alpha), then perm(G), then translation, then global phase"""
    return [('D', tuple(rec['quadratic_rows']), tuple(rec['linear_Z4'])), ('P', tuple(rec['matrix_rows'])), ('X', rec['offset']), ('phase', rec['phase'])]


def fourier_circ(axes): return [('C', 1 << i, 1) for i in axes]


def recipe_circ(rec):
    """serialized child recipe: right monomial, Fourier on the first `rank` axes, left monomial (rank 0: the monomial in `left`)"""
    if rec['rank'] == 0: return monomial_circ(rec['left'])
    return monomial_circ(rec['right']) + fourier_circ(range(rec['rank'])) + monomial_circ(rec['left'])


def basis_batch(cols):
    """GD with column c = basis vector e_{cols[c]}"""
    g = GD.zeros(len(cols))
    for c, b in enumerate(cols): g.re[b, c] = 1
    return g


def identity_batch(): return basis_batch(list(range(N)))


def selftest(vendor):
    import random
    ce = vendor
    rng = random.Random(1)
    FULL = tuple(1 << i for i in range(n))
    ops = [ce.canonical_frame(n, ()), ce.canonical_frame(n, FULL), ce.canonical_frame(n, (510,)), ce.canonical_frame(n, (408, 102)),
           ce.cgate(n, 7), ce.cgate(n, 13).adjoint(), ce.fourier(n, range(5))]
    for _ in range(6):
        U = []
        while len(U) < rng.randint(1, 8):
            x = rng.randrange(1, N)
            if ce.rank(U + [x]) > len(U): U.append(x)
        ops.append(ce.canonical_frame(n, tuple(U)))
        ops.append(ce.canonical_frame(n, tuple(U)).adjoint().then(ce.canonical_frame(n, FULL)))
    for op in ops:
        cols = rng.sample(range(N), 12)
        g = basis_batch(cols).apply_circ(circ_of(op))
        for c, b in enumerate(cols):
            vec, den = op.zero_state(b)
            ref = GD(np.array([[a] for a, _ in vec], np.int64), np.array([[bb] for _, bb in vec], np.int64), den)
            col = GD(g.re[:, c:c + 1].copy(), g.im[:, c:c + 1].copy(), g.d)
            assert col.equals(ref), 'applier disagrees with vendored state vector'
        h = g.copy().apply_circ(circ_of(op), inverse=True)
        assert h.equals(basis_batch(cols)), 'inverse applier'
    return len(ops)
