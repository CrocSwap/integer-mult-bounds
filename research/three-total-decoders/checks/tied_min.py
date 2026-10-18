"""Group G1: the sharp example tied_min (12 lines, cost = v = 12), fprime/PROOF.md sections 11.5, 12.1-12.3, 12.7, 13.3, 14.
Re-checks: the structure; step (a) and (b) of the exchange proof (the computational steps); the projection fact used in (c);
an independent CNF for 'cost <= 11' (UNSAT) and 'cost <= 12' (SAT); all 217 optima (enumeration to exhaustion), their structure,
their rowspace data, their exact Q-lifts; and 'every one-line deletion costs 12'."""
import sys, os, itertools, subprocess, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *
from satlib import enumerate_B, cost_leq
from pysat.solvers import Cadical153
from pysat.formula import IDPool

P, Q = load_cfg('tied_min.json'); v = len(P)
miss = lambda q: [k for k in range(3) if q[k] == 0][0]
cls = {k: [s for s in range(v) if miss(Q[s]) == k] for k in range(3)}
inc = lambda t, s: t != s and dot(P[t], Q[s]) == 0
R, A, free = setup(P, Q)
D = [[t for t in range(v) if P[t][j] and Q[t][j]] for j in range(3)]
nin = sum(1 for t in range(v) for s in range(v) if inc(t, s))
print("TM structure: v=%d points all full support with entries +-1: %s; q two-support: %s; |D(t)|=2 for every line (tied): %s; incidences %d; block row sets all %d rows: %s" % (
    v, all(all(abs(x) == 1 for x in p) for p in P), all(sum(1 for x in q if x) == 2 for q in Q),
    all(sum(1 for k in range(3) if P[t][k] and Q[t][k]) == 2 for t in range(v)), nin, v, all(len(R[j]) == v for j in range(3))))
print("TM classes (missing coordinate of q): sizes %s; distinct points %d, distinct q-lines %d" % (
    [len(cls[k]) for k in range(3)], len(set(map(tuple, P))), len(set(map(tuple, Q)))))

# SCC (Lemma SCC): H is strongly connected on tied_min
H = {t: [s for s in range(v) if inc(t, s) and any(P[t][k] and Q[s][k] for k in range(3))] for t in range(v)}
def reach(src, G):
    seen = {src}; st = [src]
    while st:
        u = st.pop()
        for w in G[u]:
            if w not in seen: seen.add(w); st.append(w)
    return seen
Hr = {t: [s for s in range(v) if t in H[s]] for t in range(v)}
print("TM H strongly connected (Lemma SCC): %s" % (len(reach(0, H)) == v and len(reach(0, Hr)) == v))

# (a) MAS(G[D_j]) = 3
def mas(nodes):
    idx = {t: i for i, t in enumerate(nodes)}
    o = [sum(1 << idx[s] for s in range(v) if s in idx and inc(t, s)) for t in nodes]
    return int(subprocess.run([os.path.join(BIN, 'mas')], input="%d\n" % len(nodes) + "\n".join(map(str, o)), capture_output=True, text=True, check=True).stdout)
print("TM step (a): MAS(G[D_j]) for j=0,1,2: %s" % [mas(D[j]) for j in range(3)])

# (b) block of rank <= 3: unique filling of its 8 columns (exhaustive SAT enumeration), then dims
def rank3_fillings(j):
    cols = A[j]; r = 3; pool = IDPool(); cl = []
    for t in range(v):
        for s in cols:
            target = True if t == s else (pool.id(('B', t, s)) if inc(t, s) else False); ands = []
            for k in range(r):
                x = pool.id(('X', t, k)); y = pool.id(('Y', k, s)); z = pool.id(('Z', t, s, k)); cl += [[-z, x], [-z, y], [z, -x, -y]]; ands.append(z)
            acc = ands[0]
            for z in ands[1:]:
                n = pool.id(('C', t, s, z)); cl += [[-n, acc, z], [-n, -acc, -z], [n, -acc, z], [n, acc, -z]]; acc = n
            if target is True: cl.append([acc])
            elif target is False: cl.append([-acc])
            else: cl += [[-acc, target], [acc, -target]]
    bv = {(t, s): pool.id(('B', t, s)) for t in range(v) for s in cols if inc(t, s)}
    S = Cadical153(bootstrap_with=cl); sols = []
    while S.solve():
        m = set(l for l in S.get_model() if l > 0)
        sols.append({k for k, x in bv.items() if x in m})
        S.add_clause([-x if x in m else x for x in bv.values()])
    return sols, cols
def colvec(ent, s):
    return sum((1 if (t == s or (t, s) in ent) else 0) << t for t in range(v))
for j in range(3):
    sols, cols = rank3_fillings(j)
    ks = [k for k in range(3) if k != j]
    out = []
    for ent in sols:
        d = [rank2([colvec(ent, s) for s in cls[ks[0]]]), rank2([colvec(ent, s) for s in cls[ks[1]]]), rank2([colvec(ent, s) for s in cls[ks[0]] + cls[ks[1]]])]
        zr = all(((t == s) or ((t, s) in ent)) is False for s in cols for t in cls[j])
        out.append((tuple(d), zr))
    print("TM step (b) j=%d: block rank <= 3 fillings of its %d columns: %d; (dim S_k, dim S_l, dim(S_k+S_l), class-%d rows vanish) = %s" % (j, len(cols), len(sols), j, out))

# (c) the projection onto the class-j rows: B[T_j, C_j] has rank >= 2 for every filling
okc = []
for j in range(3):
    T = cls[j]; C = cls[j]
    fr = [(t, s) for t in T for s in C if inc(t, s)]
    mn = 9
    for g in range(1 << len(fr)):
        rows = [sum((1 if (t == s or ((t, s) in fr and g >> fr.index((t, s)) & 1)) else 0) << i for i, s in enumerate(C)) for t in T]
        mn = min(mn, rank2(rows))
    okc.append((len(fr), mn))
print("TM step (c): B[T_j,C_j] is 4x4 with (free entries, minimum F2 rank over all fillings) = %s" % okc)

# independent CNF: cost <= 11 UNSAT, cost <= 12 SAT with ranks (4,4,4)
print("TM CNF cost<=11: %s" % ("UNSAT" if cost_leq(P, Q, 11) is None else "SAT"))
B12 = cost_leq(P, Q, 12)
print("TM CNF cost<=12: %s, block ranks recomputed by elimination %s" % ("SAT" if B12 else "UNSAT", blockranks(B12, R, A) if B12 else None))

# all 217 optima
opt = enumerate_B(P, Q, (4, 4, 4))
print("TM optima: B with block ranks <= (4,4,4) enumerated to exhaustion: %d" % len(opt))
cl_of = [miss(Q[t]) for t in range(v)]
kinds = collections.Counter(); sumcost = set(); blkr = set(); lift_ok = 0; wholeTU = 0; rhow = collections.Counter(); costid = 0
Bs = []
for ent in opt:
    B = [[1 if t == s else 0 for s in range(v)] for t in range(v)]
    for (t, s) in ent: B[t][s] = 1
    Bs.append(B)
    cross = sum(1 for (t, s) in ent if cl_of[t] != cl_of[s])
    br = tuple(blockranks(B, R, A)); blkr.add(br); sumcost.add(sum(br))
    rho = rank2([sum(B[t][s] << s for s in range(v)) for t in range(v)])
    # rowspace W by enumeration of all 2^rho elements; w_j = dim(W cap F2^{C_j}) from the count of elements supported on C_j
    rows = [sum(B[t][s] << s for s in range(v)) for t in range(v)]
    basis = []
    for x in rows:
        for b in basis: x = min(x, x ^ b)
        if x: basis.append(x)
    Wset = {0}
    for b in basis: Wset |= {w ^ b for w in Wset}
    assert len(Wset) == 1 << rho
    w = []
    for j in range(3):
        mask = sum(1 << s for s in cls[j]); cnt = sum(1 for x in Wset if x & ~mask == 0); w.append(cnt.bit_length() - 1)
    costid += (3 * rho - sum(w) == sum(br))
    Sdim = [rank2([colvec(set(ent), s) for s in cls[k]]) for k in range(3)]
    if cross == 0:
        kinds[('class-diagonal', tuple(Sdim), rho, tuple(w), tuple(rank2([sum(B[t][s] << i for i, s in enumerate(cls[k])) for t in cls[k]]) for k in range(3)))] += 1
    else:
        kinds[('cross-class entries %d' % cross, tuple(Sdim), rho, tuple(w), None)] += 1
print("TM optima: block-rank triples %s, costs %s" % (sorted(blkr), sorted(sumcost)))
for k, c in sorted(kinds.items(), key=lambda kv: -kv[1]):
    print("TM optimum kind: %s: dim S_k %s, rank B %d, w %s, class-block ranks %s -> %d matrices" % (k[0], k[1], k[2], k[3], k[4], c))
print("TM F2S identity cost = 3*rho - sum_j w_j (w_j by counting the elements of the row space on C_j) holds for %d of %d optima" % (costid, len(opt)))
# the special optimum: S_0 = S_1 = S_2 = W as column spaces
spec = [B for B, ent in zip(Bs, opt) if sum(1 for (t, s) in ent if cl_of[t] != cl_of[s]) > 0]
def colspace(B, S):
    basis = []
    for s in S:
        x = sum(B[t][s] << t for t in range(v))
        for b in basis: x = min(x, x ^ b)
        if x: basis.append(x)
    el = {0}
    for b in basis: el |= {w ^ b for w in el}
    return frozenset(el)
print("TM special optimum B0: S_0 = S_1 = S_2 = W (column spaces equal, dim 4): %s" % (
    all(len({colspace(B, cls[0]), colspace(B, cls[1]), colspace(B, cls[2]), colspace(B, range(v))}) == 1 for B in spec) and len(spec) == 1))

# lifts: joint block-TU signing, whole-matrix TU signability, exact Q block ranks
fl = jsign_batch(Bs, R, A, True)
for B, (f, sgn) in zip(Bs, fl):
    if f[0] and block_q(signed_matrix(B, sgn), R, A) == blockranks(B, R, A): lift_ok += 1
    wholeTU += tus(B, range(v), range(v))
print("TM lifts: joint block-TU signing from the Camion system with exact Q block ranks equal to the F2 ranks (4,4,4): %d of %d; whole 12x12 B TU-signable: %d of %d" % (lift_ok, len(Bs), wholeTU, len(Bs)))

# one-line deletions and the exact cost of lone lines
dels = []
for t in range(v):
    keep = [u for u in range(v) if u != t]
    dels.append((cost_leq([P[u] for u in keep], [Q[u] for u in keep], 11) is None))
print("TM every one-line deletion has cost >= 12 (cost <= 11 UNSAT): %d of %d" % (sum(dels), v))
# a tight subconfiguration of size 10 (cost = v)
found = None
for S in itertools.combinations(range(v), 10):
    Ps = [P[u] for u in S]; Qs = [Q[u] for u in S]
    if cost_leq(Ps, Qs, 9) is None and cost_leq(Ps, Qs, 10) is not None:
        found = S; break
print("TM first tight 10-line subconfiguration (cost <= 9 UNSAT, cost <= 10 SAT): %s" % (found,))
