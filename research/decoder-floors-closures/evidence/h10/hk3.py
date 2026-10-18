"""STRAYS-H10 hk3.py TERM query T(h,l,k,H1,H2), R = P112 minus H1, A = P112 minus H2:
exists fitting B = U V^T (U,V in F2^{112 x h}) with l independent psi in F2^h, V[A] psi = 0, and k independent phi in F2^h with U[R] phi = 0 and
phi in rowspan V[A]. Since rank U[R]V[A]^T = rank V[A] - dim(rowspan V[A] cap ker U[R]) (exact), SAT for some l+k = h - c  <=>  some fitting B of rank <= h
has rank B[R,A] <= c.  usage: hk3.py H l k PAIRS.pkl IDX OUT.cnf [solve]
(older docstring follows) JOINT query J(h,K1,K2,H1,H2): fitting B = U V^T rank <= h with K1 independent vectors of col U supported in H1 AND K2 independent
vectors of col V (= row B) supported in H2. usage: hk2.py H K1 K2 PAIRS.pkl IDX OUT.cnf [solve].  (hk.py docstring follows)
 (Gram-realisation stacking query G(h,K,H)): exists fitting B = U V^T of rank <= h and K independent c_i in col U, all supported inside the
hyperplane section H (lines orthogonal to a maximal-flat normal x). UNSAT => no term R(x) of a root-code decoder avoids a K-dim subspace of col B.
(Original h10.py docstring follows.)
 deficiency stacking under a global fitting table of rank <= h on P112.
Query D(h,k): exists fitting B = U V^T (U,V in F2^{112 x h}; B_tt=1, B_ts=0 on non-orthogonal pairs) and k functionals phi_1..phi_k whose
vectors c_i = U phi_i are linearly independent, such that O = {t : (c_1(t),..,c_k(t)) != 0} (= union of supports of the k-dim subspace span c_i
of col U ⊇ col B) is NOT certified non-deficient by one round of Lemma 1.1 (IDEAL3), i.e. every P112 frame E contains a 'survivor' e:
  e not in O, and for every frame F there is g in F \\ O with e in Nbar(g) (Nbar = non-orthogonal or equal).
UNSAT => for every fitting B of rank <= h, every k-dim subspace of col(B) (and, by the transpose symmetry, of row(B)) has a support union that is
non-deficient in every rank-8 realisation of P112.
Gauge (rigid2.py, PROVEN there): U[S] = (e_1..e_8) on a non-orthogonal 8-clique S.  SYM=1: U=V.
usage: hk.py H K REP OUT.cnf [solve]   (REP = index into hyp_reps.pkl, or -1 for no restriction)"""
import sys, os, itertools, subprocess, numpy as np, networkx as nx
sys.path.insert(0, '/Users/mason/repo_clones/intmult-work/cards/STRAYS')
import e8
from e8 import G
h, Lr, Kr, pf, pi, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6]
import pickle
H1, H2 = [set(x) for x in pickle.load(open(pf, 'rb'))[pi]]
SYM = os.environ.get('SYM') == '1'
V = list(e8.P112)
def nonorth(t, s): return G[t, s] % 2 != 0
og = nx.Graph(); og.add_nodes_from(V); og.add_edges_from((t, s) for t in V for s in V if t < s and not nonorth(t, s))
frames = [sorted(c) for c in nx.find_cliques(og) if len(c) == 8]
assert len(frames) == 1260, len(frames)
H = nx.Graph(); H.add_nodes_from(V); H.add_edges_from((t, s) for t in V for s in V if t < s and nonorth(t, s))
S = sorted(max(nx.find_cliques(H), key=len)); assert len(S) == 8
# H11: GAUGE=A (resp. R): use the lexicographically first non-orthogonal 8-clique inside A (resp. R) as the gauge clique (any non-orthogonal
# 8-clique is a valid gauge, THEORY §1). With S inside A, V[S] = (I|0) forces psi into span(e_8..e_{h-1}).
if os.environ.get('GAUGE') in ('A', 'R'):
    _HH = set(pickle.load(open(pf, 'rb'))[pi][0 if os.environ['GAUGE'] == 'R' else 1]); _X = set(V) - _HH
    _c = sorted(sorted(c) for c in nx.find_cliques(H.subgraph(_X)) if len(c) == 8)
    assert _c, 'no 8-clique inside ' + os.environ['GAUGE']; S = _c[0]
if os.environ.get('GAUGE') == 'RA':   # first non-orthogonal 8-clique maximising |S & R| + |S & A| (partial version of GAUGE=A/R)
    _P = pickle.load(open(pf, 'rb'))[pi]; _R = set(V) - set(_P[0]); _A = set(V) - set(_P[1])
    _c = sorted(sorted(c) for c in nx.find_cliques(H) if len(c) == 8)
    S = max(_c, key=lambda c: len(set(c) & _R) + len(set(c) & _A))
    print('GAUGE RA |S&R|', len(set(S) & _R), '|S&A|', len(set(S) & _A), file=sys.stderr)
nv = 0; cls = []
def new():
    global nv; nv += 1; return nv
Uv = {t: [new() for _ in range(h)] for t in V if t not in S}
Vv = Uv if SYM else {t: [new() for _ in range(h)] for t in V}
def ub(t, k): return ('c', int(S.index(t) == k)) if t in S else ('v', Uv[t][k])
def vb(t, k):  # second gauge (PROVEN, THEORY §1): GL(h) elements fixing U[S]=(I|0) are g=[[I,0],[C,D]]; V -> V g^{-T}; C = V[S]_2^T makes V[S]=(I|0)
    if SYM or t in S: return ub(t, k)
    return ('v', Vv[t][k])
def AND(a, b):
    if a[0] == 'c' and b[0] == 'c': return ('c', a[1] & b[1])
    if a[0] == 'c': return b if a[1] else ('c', 0)
    if b[0] == 'c': return a if b[1] else ('c', 0)
    if a[1] == b[1]: return a
    z = new(); x, y = a[1], b[1]; cls.extend([[-z, x], [-z, y], [z, -x, -y]]); return ('v', z)
def XOR(a, b):
    if a[0] == 'c' and b[0] == 'c': return ('c', a[1] ^ b[1])
    if a[0] == 'c': return ('v', -b[1]) if a[1] else b
    if b[0] == 'c': return ('v', -a[1]) if b[1] else a
    z = new(); x, y = a[1], b[1]; cls.extend([[-z, x, y], [-z, -x, -y], [z, -x, y], [z, x, -y]]); return ('v', z)
def OR(lits):
    z = new(); cls.append([-z] + lits); cls.extend([[z, -l] for l in lits]); return z
def force(l, val):
    if l[0] == 'c':
        if l[1] != val: cls.append([])
        return
    cls.append([l[1] if val else -l[1]])
def lit(l):  # literal for a term that must be a variable or constant -> return ('c',x) or int
    return l
for t in V:
    acc = ('c', 0)
    for k in range(h): acc = XOR(acc, AND(ub(t, k), vb(t, k)))
    force(acc, 1)
    for s in V:
        if s != t and nonorth(t, s) and (not SYM or t < s):
            acc = ('c', 0)
            for k in range(h): acc = XOR(acc, AND(ub(t, k), vb(s, k)))
            force(acc, 0)
# term query
R = [t for t in V if t not in H1]; A = [t for t in V if t not in H2]
def indep(vecs):
    K = len(vecs)
    for gam in itertools.product((0, 1), repeat=K):
        if not any(gam): continue
        ors = []
        for k in range(h):
            acc = ('c', 0)
            for i in range(K):
                if gam[i]: acc = XOR(acc, vecs[i][k])
            if acc[0] == 'c':
                if acc[1]: ors = None; break
                continue
            ors.append(acc[1])
        if ors is not None: cls.append(ors)
# H11: RREF symmetry breaking (env RREF=1; PROVEN: the conditions on the tuple psi (resp. phi) depend only on its span, a linear subspace of F2^h
# (ker V[A], resp. rowspan V[A] cap ker U[R]), and every l-dim subspace has a unique basis in reduced row echelon form w.r.t. coordinates 0..h-1).
def rref(vecs):
    K = len(vecs)
    if K == 0: return
    piv = [[new() for _ in range(h)] for _ in range(K)]
    def cl(l):
        if l[0] == 'c': return l
        return l
    for i in range(K):
        cls.append(piv[i][:])
        for a in range(h):
            for b in range(a + 1, h): cls.append([-piv[i][a], -piv[i][b]])
    for i in range(K):
        for a in range(h):
            p = piv[i][a]; ci = vecs[i][a]
            if ci[0] == 'c':
                if ci[1] == 0: cls.append([-p])
            else: cls.append([-p, ci[1]])
            for b in range(a):
                x = vecs[i][b]
                if x[0] == 'c':
                    if x[1]: cls.append([-p])
                else: cls.append([-p, -x[1]])
            for j in range(K):
                if j == i: continue
                x = vecs[j][a]
                if x[0] == 'c':
                    if x[1]: cls.append([-p])
                else: cls.append([-p, -x[1]])
            if i + 1 < K:
                for b in range(a + 1): cls.append([-p, -piv[i + 1][b]])
    return piv
PIVS = {}
psi = [[('v', new()) for _ in range(h)] for _ in range(Lr)]
for p in psi:
    for s in A:
        acc = ('c', 0)
        for k in range(h): acc = XOR(acc, AND(vb(s, k), p[k]))
        force(acc, 0)
indep(psi)
if os.environ.get('RREF') == '1': PIVS['psi'] = rref(psi)
phis = []
for i in range(Kr):
    lam = {s: ('v', new()) for s in A}
    p = []
    for k in range(h):
        acc = ('c', 0)
        for s in A: acc = XOR(acc, AND(lam[s], vb(s, k)))
        p.append(acc)
    for t in R:
        acc = ('c', 0)
        for k in range(h): acc = XOR(acc, AND(ub(t, k), p[k]))
        force(acc, 0)
    phis.append(p)
indep(phis)
# H11: ORTH=1 adds the implied constraints phi_i . psi_j = 0 (rowspan V[A] = (ker V[A])^perp over F2; sound, redundant)
if os.environ.get('ORTH') == '1':
    for p_ in phis:
        for q_ in psi:
            acc = ('c', 0)
            for k in range(h): acc = XOR(acc, AND(p_[k], q_[k]))
            force(acc, 0)
if os.environ.get('RREF') == '1': PIVS['phi'] = rref(phis)
# H11 cube splitting (env PIV="psi:i:a,phi:j:b", needs RREF=1): unit clause "pivot of RREF basis vector i of psi (phi) is coordinate a".
# Pivots are one-hot per vector, so the cubes {a} over a = 0..h-1 cover the instance exactly.
if os.environ.get('PIV'):
    for it in os.environ['PIV'].split(','):
        nm, i, a = it.split(':'); cls.append([PIVS[nm][int(i)][int(a)]])
with open(out, 'w') as f:
    f.write(f'p cnf {nv} {len(cls)}\n')
    for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
print('h', h, 'l', Lr, 'k', Kr, pf, pi, '|R|', len(R), '|A|', len(A), 'vars', nv, 'clauses', len(cls), flush=True)
if len(sys.argv) > 7:
    o = subprocess.run(['kissat', '-q', out], capture_output=True, text=True).stdout
    print(o.splitlines()[0], flush=True)
