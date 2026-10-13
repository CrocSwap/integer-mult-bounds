"""Stage-two label check of the source-frame lemma on the PR #7 complex network (Side(h), h+1 centre wires).

Traces every side role and centre wire through the stage-two (inverse) PR #7 schedule, assigning each gate its
binary frame (PR #7 construction, frames section), with a1 = A, a3 = B fixed:
  D(U) = (t_A^perp (x) F (x) <t_B>) perp (<t_A> (x) U (x) <t_B>),  D0 = D(0);
  copy y a-1 uses the physical Y frame t_A^perp (x) <t_T> (x) <t_B>.
Every frame's dimension is checked against fullbatch_hist's. For each distinct (first, last) label pair of a
source-framed role it checks in F_2^m: D0 subset of both, entrance phase q_U - q_D0 = q_{L1} (rank dim L1),
exit phase wt + q_D0 - q_V = q_G with G = D0 + V^perp of dim m - dim L2, nondegenerate and nonalternating.
Input-pivot slots must fail D0 subset first label (the reason they are excluded). Usage: labcheck_pr7.py h."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from side import Side
from labels import Checker
from roles import compile_roles

h = int(sys.argv[1]); m = h ** 3; rnd = random.Random(h)
def idx(i, j, k): return (i * h + j) * h + k
def tens(a, b, c):
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
    return b
def contains(big, small):
    b = span_basis(big)
    for x in small:
        for piv, y in b.items():
            if x >> piv & 1: x ^= y
        if x: return False
    return True
class Proj:
    def __init__(s, B):
        s.B = B; n = len(B)
        G = [sum(dot(a, b) << j for j, b in enumerate(B)) | (1 << (n + i)) for i, a in enumerate(B)]
        for col in range(n):
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
def perp(B):
    R = list(span_basis(B).items()); out = []
    pivs = {pv for pv, _ in R}
    for f in range(m):
        if f in pivs: continue
        x = 1 << f
        for pv, r in R:
            if dot(r, x): x ^= 1 << pv
        out.append(x)
    return out
def _perp_small(U):
    rows = list(span_basis(U).items()); out = []
    pivs = {pv for pv, _ in rows}
    for f in range(h):
        if f in pivs: continue
        x = 1 << f
        for pv, r in rows:
            if dot(r, x): x ^= 1 << pv
        out.append(x)
    return out

c = Side(h); k = compile_roles(c); ch = Checker(c); assert ch.run()['bad'] == 0
R = k['size']; F = [1 << i for i in range(h)]; a = h; low, high = (a - 1) * h, a * h
lab = {n: ch.label(n) for n in c.active}
# trace: frame descriptors ('U', basis tuple) or ('Ydata', T); dims checked against fullbatch_hist
first = {}; last = {}
def touch(slot, desc, dim):
    got = (low + len(span_basis(list(desc[1])))) if desc[0] == 'U' else a - 1
    assert got == dim, (desc, got, dim)
    first.setdefault(slot, desc); last[slot] = desc
U = lambda B: ('U', tuple(sorted(span_basis(list(B)).values())))
cent = range(R, R + h + 1)
pieces = {t: [] for t in c.triples}
for i, sl in k['pout'].items(): pieces[c.pieces[i][0]].append(sl)
def mix(md, rev=False):
    for n, ins, outs in (reversed(k['gates']) if rev else k['gates']):
        L = {'low': [], 'high': F, 'complement': _perp_small(lab[n])}[md]
        dim = {'low': low, 'high': high, 'complement': high - len(lab[n])}[md]
        for sl in set(ins + outs): touch(sl, U(L), dim)
def inject(f, line):
    for t in c.triples:
        tm = sum(1 << q for q in t)
        for sl in pieces[t]: touch(sl, U([tm] if line else F), f)
def copy_y(f, data):
    for t, sl in k['src'].items():
        tm = sum(1 << q for q in t)
        touch(sl, ('Ydata', t) if data else U(_perp_small([tm])), f)
def central(L, f):
    for sl in cent: touch(sl, U(L), f)
# stage-two inverse schedule, exactly as fullbatch_hist.invocation(inverse=True)
copy_y(a - 1, True); central([], low); mix('low'); inject(low + 1, True)
mix('complement', True); central(F, high); central([], low)
copy_y(high - 1, False); central(F, high); mix('high'); inject(high, False)
mix('high', True)

keep = set(k['src'].values()) | set(k['rout'].values()) | set(cent)
framed = [sl for sl in range(R) if sl not in keep]
pairs = {}
for sl in framed: pairs.setdefault((first[sl], last[sl]), []).append(sl)
src_firsts = {first[sl][0] for sl in k['src'].values()}
print('h', h, 'roles', R, 'source-framed', len(framed), 'distinct (first,last) label pairs', len(pairs),
      'input-pivot first frames', src_firsts, flush=True)

T3 = [sum(1 << i for i in t) for t in c.triples]
ok = True
for trial in range(3):
    tA, tB = rnd.choice(T3), rnd.choice(T3)
    Aperp = list(span_basis([u ^ (tA if dot(u, tA) else 0) for u in F]).values())
    D0 = list(span_basis([tens(x, u, tB) for x in Aperp for u in F]).values()); assert len(D0) == low
    PD0 = Proj(D0)
    def space(desc):
        if desc[0] == 'Ydata':
            tm = sum(1 << q for q in desc[1]); return [tens(x, tm, tB) for x in Aperp], None
        E = [tens(tA, l, tB) for l in desc[1]]; return D0 + E, E
    ys = [rnd.getrandbits(m) for _ in range(20)]
    for (f, l), sls in pairs.items():
        Uf, E1 = space(f); Vl, E2 = space(l)
        inc = contains(Uf, D0) and contains(Vl, D0)
        PU, PV = Proj(list(span_basis(Uf).values())), Proj(list(span_basis(Vl).values()))
        PE = Proj(E1) if E1 else (lambda x: 0)
        Gs = list(span_basis(D0 + perp(Vl)).values()); PG = Proj(Gs)
        ent = all((q(PU, y) - q(PD0, y) - q(PE, y)) % 4 == 0 for y in ys)
        ex = all((bin(y).count('1') + q(PD0, y) - q(PV, y) - q(PG, y)) % 4 == 0 for y in ys)
        nonalt = any(dot(x, x) for x in Gs); rk = len(Gs) == m - len(E2)
        print(' trial', trial, 'first dim L1', len(E1), 'last dim L2', len(E2), 'roles', len(sls),
              '| D0 in both', inc, 'entrance ok', ent, 'exit ok', ex, 'exit rank', len(Gs), 'm-dimL2', rk,
              'nonalt', nonalt, flush=True)
        ok &= inc and ent and ex and nonalt and rk
    # excluded roles: an input pivot's first stage-two label must not contain D0
    sp, _ = space(first[k['src'][c.triples[0]]])
    neg = not contains(sp, D0); print(' trial', trial, 'input-pivot first label excludes D0 (expected):', neg)
    ok &= neg
    # centre wires: first D0, last D1 as well (they keep source 0 regardless)
    cf = {(first[s], last[s]) for s in cent}; print(' centre (first,last) dims',
          [(len(x[1]), len(y[1])) for x, y in cf])
print('ALL OK', ok)
