"""Task 2: explicit two-stage bit frames at small h (Gram I-J/9 on F=Q^h, G(x)G on F(x)F).
Builds every role class's label chain per invocation from the notes' schedules, checks monotonicity
(including X_a: U_a -> F), edge ranks, the ranks exceeding m/2, the per-role rank sums against
s_edge = Wm - 2N + 2L, and the batching hypothesis (simultaneous invertible corners after one
conjugation S0; full Bruhat profile of S_p on the selected projectors)."""
import random, sys
from itertools import combinations
from fractions import Fraction as Q
from factor import rank, inv, mul, bruhat, swapmat, predicted

def kron(A, B):
    return [[a*b for a in ra for b in rb] for ra in A for rb in B]
def T(A): return [list(r) for r in zip(*A)]

class Space:
    """Subspace of Q^n given by a list of basis row vectors (reduced)."""
    def __init__(self, vecs, n):
        self.n = n; M = [list(v) for v in vecs]; B = []
        for v in M:
            w = v[:]
            for b, c in B:
                if w[c]: f = w[c]/b[c]; w = [x-f*y for x, y in zip(w, b)]
            c = next((i for i, x in enumerate(w) if x), None)
            if c is not None: B.append((w, c))
        self.B = [b for b, _ in B]
    @property
    def dim(self): return len(self.B)
    def __le__(self, o): return Space(o.B+self.B, self.n).dim == o.dim
    def __add__(self, o): return Space(self.B+o.B, self.n)
    def __eq__(self, o): return self <= o and o <= self

def tens(U, V): return Space([[a*b for a in u for b in w] for u in U.B for w in V.B], U.n*V.n)

def perp(U, G, n):
    """G-orthogonal complement of U in Q^n."""
    if not U.B: return Space([[Q(int(i == j)) for j in range(n)] for i in range(n)], n)
    A = mul(U.B, G)                                   # rows: functionals u^T G
    # null space of A
    M = [r[:] for r in A]; piv = []; r0 = 0
    for c in range(n):
        p = next((i for i in range(r0, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r0], M[p] = M[p], M[r0]; f = M[r0][c]; M[r0] = [x/f for x in M[r0]]
        for i in range(len(M)):
            if i != r0 and M[i][c]: g = M[i][c]; M[i] = [x-g*y for x, y in zip(M[i], M[r0])]
        piv.append(c); r0 += 1
    free = [c for c in range(n) if c not in piv]; out = []
    for fcol in free:
        v = [Q(0)]*n; v[fcol] = Q(1)
        for i, c in enumerate(piv): v[c] = -M[i][fcol]
        out.append(v)
    return Space(out, n)

def proj(U, G):
    """G-orthogonal projector onto nondegenerate U (column convention: p x)."""
    n = U.n
    if not U.B: return [[Q(0)]*n for _ in range(n)]
    Bc = T(U.B)                                        # n x d
    Gr = mul(mul(U.B, G), Bc)                          # d x d Gram
    assert rank(Gr) == len(Gr), 'degenerate label'
    return mul(mul(Bc, inv(Gr)), mul(U.B, G))

def run(h, data_sample, side_sample, seed=1, bruhat_count=None):
    rng = random.Random(seed)
    m = h*h; trip = list(combinations(range(h), 3)); v = len(trip)
    G = [[Q(int(i == j))-Q(1, 9) for j in range(h)] for i in range(h)]
    G2 = kron(G, G)
    tv = [[Q(int(i in t)) for i in range(h)] for t in trip]
    F = Space([[Q(int(i == j)) for j in range(h)] for i in range(h)], h)
    zeroF = Space([], h); FF = tens(F, F); zero = Space([], m)
    line = [Space([x], h) for x in tv]; lperp = [perp(L, G, h) for L in line]
    edges = []          # (role class, from, to) per traced role
    def chain(name, labels):
        for a, b in zip(labels, labels[1:]):
            if a <= b: edges.append((name, b.dim-a.dim, a, b, 'up'))
            else:
                assert b <= a, (name, 'incomparable labels')
                edges.append((name, a.dim-b.dim, a, b, 'down'))
    # source spans: common point i, target T containing i, sources S with S cap T = {i}
    def rect(T_):
        i = rng.choice(T_)
        src = [s for s, t in enumerate(trip) if i in t and set(t) & set(trip[T_]) == {i}] if False else \
              [s for s, t in enumerate(trip) if i in t and set(t) & set(T_) == {i}]
        S = rng.sample(src, rng.randint(1, min(4, len(src))))
        U = Space([tv[s] for s in S], h)
        return S, U
    batched = {}
    for a2 in range(v):        # stage 1, fixed a2 (Q = line a2); D0 = 0, D1 = F (x) t_a2
        Qs = line[a2]; D0 = zero; D1 = tens(F, Qs)
        X = {a1: tens(line[a1], Qs) for a1 in range(v)}
        Y = {a1: tens(lperp[a1], Qs) for a1 in range(v)}
        for _ in range(side_sample):
            T_ = trip[rng.randrange(v)]; S, U = rect(T_)
            DU = tens(U, Qs); tY = trip.index(T_)
            for s in S:
                assert line[s] <= U and U <= lperp[tY]
            chain('s1 input-only', [zero, D0, X[S[0]], DU, D1, FF])
            chain('s1 output-only', [zero, D0, DU, Y[tY], D1, FF])
        chain('s1 center', [zero, D0, D1, D0, D1, FF])
        batched[('s1 aux', a2)] = (D1, FF)
    for a1 in range(v):        # stage 2 reverse, fixed a1; D0 = t_a1^perp (x) F, D1 = F (x) F
        D0 = tens(lperp[a1], F); D1 = FF; P = line[a1]
        X = {a2: D0 + tens(P, line[a2]) for a2 in range(v)}
        Y = {a2: D0 + tens(P, lperp[a2]) for a2 in range(v)}
        for _ in range(side_sample):
            T_ = trip[rng.randrange(v)]; S, U = rect(T_); tY = trip.index(T_)
            DU = D0 + tens(P, U)
            # reverse: physical X are the rectangle's logical targets; physical roles swap descriptions
            chain('s2 input-only', [zero, D0, X[S[0]], DU, D1])
            chain('s2 output-only', [zero, D0, DU, Y[tY], D1])
        chain('s2 center', [zero, D0, D1, D0, D1])
        batched[('s2 aux', a1)] = (zero, D0)
    # data roles (sampled pairs a=(a1,a2)): stage-1 forward then stage-2 reverse
    pairs = [(rng.randrange(v), rng.randrange(v)) for _ in range(data_sample)]
    Xmono = True
    for a1, a2 in pairs:
        Ua = tens(line[a1], line[a2]); Uap = perp(Ua, G2, m)
        s1X = [Ua, tens(line[a1], line[a2]), tens(F, line[a2])]                      # V at X_t, G/V at D1
        s1Y = [zero, zero, tens(lperp[a1], line[a2])]                                 # J,R at D0=0, J at Y_t
        D0 = tens(lperp[a1], F)
        s2X = [tens(F, line[a2]), D0 + tens(line[a1], line[a2]), FF]                  # J at X_t, R/J at D1
        s2Y = [tens(lperp[a1], line[a2]), D0, D0 + tens(line[a1], lperp[a2])]         # V,G at D0, V at Y_t
        assert s1X[-1] == s2X[0] and s1Y[-1] == s2Y[0], 'interstage boundary mismatch'
        assert s2Y[-1] == Uap, 'Y terminal is not U_a^perp'
        Xch = s1X+s2X[1:]
        Xmono &= all(a <= b for a, b in zip(Xch, Xch[1:])) and Xch[0] == Ua and Xch[-1] == FF
        chain('data X', Xch); chain('data Y', s1Y+s2Y[1:])
        batched[('data', a1, a2)] = (tens(F, line[a2]), D0 + tens(line[a1], line[a2]))
    # summarize edges
    summary = {}
    for name, r, a, b, d in edges:
        summary.setdefault(name, {}).setdefault((d, r), 0); summary[name][(d, r)] += 1
    per_role = {}
    for name, r, a, b, d in edges: per_role.setdefault(name, 0); per_role[name] += r
    print('h=%d m=%d v=%d: X_a monotone U_a->F on %d sampled pairs: %s' % (h, m, v, len(pairs), Xmono))
    for name, d in summary.items(): print('  %-16s (direction, rank): count  %s' % (name, dict(sorted(d.items()))))
    big = sorted({(name, r) for name, r, a, b, dd in edges if r > m//2})
    print('  edges with rank > m/2:', big, ' predicted aux m-h=%d, data m-2h+1=%d' % (m-h, m-2*h+1))
    # batching hypothesis on the selected projectors after ONE conjugation S0
    projs = {}
    for key, (U, V) in batched.items():
        p = [[x-y for x, y in zip(r1, r2)] for r1, r2 in zip(proj(V, G2), proj(U, G2))]
        assert mul(p, p) == p
        projs[key] = p
    while True:
        Lw = [[Q(rng.randint(-2, 2)) if j < i else Q(int(i == j)) for j in range(m)] for i in range(m)]
        Up = [[Q(rng.randint(-2, 2)) if j > i else Q(int(i == j)) for j in range(m)] for i in range(m)]
        S0 = mul(Lw, Up); S0i = inv(S0)
        conj = {k_: mul(mul(S0, p), S0i) for k_, p in projs.items()}
        bad = []
        unconj_bad = 0
        for k_, p in conj.items():
            a = m-rank([[Q(int(i == j))-x for j, x in enumerate(r)] for i, r in enumerate(p)])
            kk = m-a
            if rank([r[m-kk:] for r in p[:kk]]) < kk: bad.append(k_)
            if rank([r[m-kk:] for r in projs[k_][:kk]]) < kk: unconj_bad += 1
        print('  unconjugated selected projectors with singular corner: %d / %d' % (unconj_bad, len(projs)))
        print('  after one unimodular S0: singular corners %d / %d' % (len(bad), len(projs)))
        if not bad: break
    # full Bruhat profile of S_p on conjugated selected projectors
    keys = list(conj)
    if bruhat_count is not None: keys = rng.sample(keys, min(bruhat_count, len(keys)))
    okc = 0
    for k_ in keys:
        p = conj[k_]; Sp = swapmat(p); piv, L1, Mon, L2 = bruhat(Sp)
        assert mul(mul(L1, Mon), L2) == Sp
        a = sum(1 for i, c in enumerate(piv) if c > i); kk = m-a
        cp, *_ = bruhat([r[m-kk:] for r in p[:kk]], track=False)
        okc += piv == predicted({l: m-kk+cp[l] for l in range(kk)}, m, kk)
    print('  Bruhat profile == k corner swaps + one aligned width-t block on %d / %d selected projectors' % (okc, len(keys)))
    return per_role

if __name__ == '__main__':
    h = int(sys.argv[1]); run(h, int(sys.argv[2]), int(sys.argv[3]), bruhat_count=(None if sys.argv[4] == 'all' else int(sys.argv[4])))
