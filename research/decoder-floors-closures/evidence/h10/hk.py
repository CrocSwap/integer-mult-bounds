"""STRAYS-H10 hk.py (Gram-realisation stacking query G(h,K,H)): exists fitting B = U V^T of rank <= h and K independent c_i in col U, all supported inside the
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
h, K, rep, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
import pickle
Hset = set(pickle.load(open('/Users/mason/repo_clones/intmult-work/cards/STRAYS-H10/hyp_reps.pkl','rb'))[rep]) if rep >= 0 else None
SYM = os.environ.get('SYM') == '1'
V = list(e8.P112)
def nonorth(t, s): return G[t, s] % 2 != 0
og = nx.Graph(); og.add_nodes_from(V); og.add_edges_from((t, s) for t in V for s in V if t < s and not nonorth(t, s))
frames = [sorted(c) for c in nx.find_cliques(og) if len(c) == 8]
assert len(frames) == 1260, len(frames)
H = nx.Graph(); H.add_nodes_from(V); H.add_edges_from((t, s) for t in V for s in V if t < s and nonorth(t, s))
S = sorted(max(nx.find_cliques(H), key=len)); assert len(S) == 8
# H11: GAUGE=R: gauge clique = first non-orthogonal 8-clique maximising |S \ Hset| (any non-orth 8-clique is a valid gauge, THEORY §1).
# Lines of S outside H force the matching coordinates of every phi to 0 (c = U phi vanishes off H).
if os.environ.get('GAUGE') == 'R' and Hset is not None:
    _c = sorted(sorted(c) for c in nx.find_cliques(H) if len(c) == 8)
    S = max(_c, key=lambda c: len(set(c) - Hset)); print('GAUGE R |S off H|', len(set(S) - Hset), file=sys.stderr)
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
# functionals
phi = [[new() for _ in range(h)] for _ in range(K)]
cval = {}
for i in range(K):
    for t in V:
        acc = ('c', 0)
        for k in range(h): acc = XOR(acc, AND(ub(t, k), ('v', phi[i][k])))
        cval[i, t] = acc
        if Hset is not None and t not in Hset: force(acc, 0)
for gam in itertools.product((0, 1), repeat=K):
    if not any(gam): continue
    ors = []
    for t in V:
        if Hset is not None and t not in Hset: continue
        acc = ('c', 0)
        for i in range(K):
            if gam[i]: acc = XOR(acc, cval[i, t])
        if acc[0] == 'c':
            if acc[1]: ors = None; break
            continue
        ors.append(acc[1])
    if ors is not None: cls.append(ors)
# RREF symmetry breaking (PROVEN: every K-dim subspace has a unique basis in reduced row echelon form w.r.t. the order of Hset; RREF => independent)
if os.environ.get('RREF') == '1' and Hset is not None:
    Hl = sorted(Hset); n = len(Hl)
    piv = [[new() for _ in range(n)] for _ in range(K)]
    for i in range(K):
        cls.append(piv[i][:])                      # some pivot
        for a in range(n):
            for b in range(a + 1, n): cls.append([-piv[i][a], -piv[i][b]])
    def cl(i, t):
        a = cval[i, t]; return a
    for i in range(K):
        for a in range(n):
            p = piv[i][a]
            ci = cl(i, Hl[a])
            if ci[0] == 'c':
                if ci[1] == 0: cls.append([-p])
            else: cls.append([-p, ci[1]])
            for b in range(a):                   # zeros before pivot
                x = cl(i, Hl[b])
                if x[0] == 'c':
                    if x[1]: cls.append([-p])
                else: cls.append([-p, -x[1]])
            for j in range(K):                   # pivot column is a unit column
                if j == i: continue
                x = cl(j, Hl[a])
                if x[0] == 'c':
                    if x[1]: cls.append([-p])
                else: cls.append([-p, -x[1]])
            if i + 1 < K:                        # increasing pivots
                for b in range(a + 1): cls.append([-p, -piv[i + 1][b]])
with open(out, 'w') as f:
    f.write(f'p cnf {nv} {len(cls)}\n')
    for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
print('h', h, 'K', K, 'rep', rep, '|H|', len(Hset) if Hset else None, 'vars', nv, 'clauses', len(cls), '->', out, flush=True)
if len(sys.argv) > 5:
    o = subprocess.run(['kissat', '-q', out], capture_output=True, text=True).stdout
    print(o.splitlines()[0], flush=True)
