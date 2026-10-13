"""Exact F_2 check of the stage-two endpoint edges with source frame D0 (tensor labels in F_2^{h^3}).
Labels at stage two (a1=A, a3=B fixed): V(L) = (t_A^perp (x) F (x) <t_B>)  perp  (<t_A> (x) L (x) <t_B>),
so D0 = V(0), D1 = V(F).  For an aux role with source frame q_D0 and sink frame wt + q_D0:
  entrance  q_{V(L1)} - q_D0             should equal q_{<t_A>(x)L1(x)<t_B>}      (rank dim L1)
  exit      wt + q_D0 - q_{V(L2)}        should equal q_G, G = D0 perp V(L2)^perp  (rank m - dim L2)
G must be nondegenerate and nonalternating (orthonormal basis).  Checked at random y, plus ranks."""
import sys, random
from itertools import combinations
h = int(sys.argv[1]); m = h**3; rnd = random.Random(h)
def idx(i, j, k): return (i * h + j) * h + k
def tens(a, b, c):  # bit vectors over F_2^h -> F_2^m
    x = 0
    for i in range(h):
        if a >> i & 1:
            for j in range(h):
                if b >> j & 1:
                    for k in range(h):
                        if c >> k & 1: x |= 1 << idx(i, j, k)
    return x
def dot(x, y): return bin(x & y).count('1') & 1
def span_basis(vs):
    b = {}
    for x in vs:
        for piv, y in b.items():
            if x >> piv & 1: x ^= y
        if x:
            piv = x.bit_length() - 1
            for q in list(b):
                if b[q] >> piv & 1: b[q] ^= x
            b[piv] = x
    return list(b.values())
class Proj:
    """orthogonal projection onto span(basis) for the dot form; asserts nondegenerate"""
    def __init__(s, B):
        s.B = B; n = len(B)
        G = [sum(dot(a, b) << j for j, b in enumerate(B)) | (1 << (n + i)) for i, a in enumerate(B)]
        for col in range(n):                       # invert Gram (symmetric) by Gauss-Jordan
            r = next((r for r in range(col, n) if G[r] >> col & 1), None)
            assert r is not None, 'degenerate'
            G[col], G[r] = G[r], G[col]
            for rr in range(n):
                if rr != col and G[rr] >> col & 1: G[rr] ^= G[col]
        s.Gi = [g >> n for g in G]
    def __call__(s, x):
        c = sum(dot(b, x) << j for j, b in enumerate(s.B)); out = 0
        for i, b in enumerate(s.B):
            if bin(s.Gi[i] & c).count('1') & 1: out ^= b
        return out
def q(P, x): return bin(P(x)).count('1') % 4
def perp(B, n=m):
    """basis of complement of span(B) in F_2^m (B nondegenerate): kernel of x -> (b.x)"""
    rows = list(B); piv = []
    # solve: vectors x with b.x=0 for all b; use reduced rows
    R = span_basis(rows); pivs = {r.bit_length() - 1: r for r in R}
    out = []
    for f in range(n):
        if f in pivs: continue
        x = 1 << f
        for pv, r in pivs.items():
            if dot(r, x): x ^= 1 << pv     # r has its leading bit pv; adjust coordinate pv
        out.append(x)
    assert all(dot(r, x) == 0 for r in R for x in out) and len(out) == n - len(R)
    return out
T = [sum(1 << i for i in t) for t in combinations(range(h), 3)]
Fh = (1 << h) - 1
units = [1 << i for i in range(h)]
ok = True
for trial in range(3):
    tA, tB = rnd.choice(T), rnd.choice(T)
    Aperp = [u ^ (tA if dot(u, tA) else 0) for u in units]     # spans t_A^perp (h-1 dim)
    Aperp = span_basis(Aperp)
    D0 = span_basis([tens(a, u, tB) for a in Aperp for u in units]); assert len(D0) == (h - 1) * h
    t = rnd.choice(T); tperp = span_basis([u ^ (t if dot(u, t) else 0) for u in units])
    cases = {'L=F (generic aux)': units, 'L=t^perp (piece)': tperp, 'L=0 (retained)': [], 'L=<t>': [t]}
    PD0 = Proj(D0)
    ys = [rnd.getrandbits(m) for _ in range(20)]
    for name, L in cases.items():
        E = [tens(tA, l, tB) for l in L]
        V = D0 + E
        PV = Proj(V); PE = Proj(E) if E else (lambda x: 0)
        G = span_basis(D0 + perp(V)); PG = Proj(G)
        nonalt = any(dot(g, g) for g in G)
        ent = all((q(PV, y) - q(PD0, y) - (q(PE, y) if E else 0)) % 4 == 0 for y in ys)
        ex = all((bin(y).count('1') + q(PD0, y) - q(PV, y) - q(PG, y)) % 4 == 0 for y in ys)
        print(h, trial, name, 'dimV', len(V), 'entrance rank', len(E), 'entrance phase ok', ent,
              '| exit rank dim G', len(G), '= m-dimL', len(G) == m - len(L), 'nondeg+nonalt', nonalt,
              'exit phase ok', ex, flush=True)
        ok &= ent and ex and nonalt and len(G) == m - len(L)
print('ALL OK', ok)
