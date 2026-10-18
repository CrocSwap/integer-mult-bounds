# HELPER stage 2: full one-big-term residue + support filter for d0 = D, over the admissible D-dim subspaces found by ind.py (ind_level_D.pkl).
import sys, itertools, pickle, time
DD = int(sys.argv[1])
src = open('ind.py').read().split('# ---- stage A')[0]
sys.argv = ['ind.py', str(DD)]
exec(src)
import networkx as nx
level = pickle.load(open(f'ind_level_{DD}.pkl', 'rb'))
print('subspaces', len(level), flush=True)
# orthogonal cliques of size 6..8 (all subsets of maximal orthogonal cliques)
og = nx.Graph(); og.add_nodes_from(range(v)); og.add_edges_from((a, b) for a in range(v) for b in range(a + 1, v) if G[a][b] == 0)
cl = set()
for c in nx.find_cliques(og):
    if len(c) >= 6:
        for r in (6, 7, 8):
            for s in itertools.combinations(sorted(c), r):
                if len(s) <= len(c): cl.add(s)
cl = sorted(cl)
CL = np.zeros((len(cl), v), dtype=np.float32); csize = np.array([len(c) for c in cl])
for i, c in enumerate(cl): CL[i, list(c)] = 1
m78 = csize >= 7
print('orthogonal cliques sizes 6-8:', len(cl), 'sizes>=7:', int(m78.sum()), flush=True)
def addable(inter, X0, x):
    new = [I & cls[x] for I in inter]
    for j, X in enumerate(new):
        size = bin(j).count('1') + 1
        if size >= 2 and lb(X) > 9 - size: return None
        if lb(X0 & X) > 9 - (size + 1): return None
    return new
def enumK(X0, S0, tau0):
    out = []
    cand = [c for c in small if lb(X0 & cls[c]) <= 7]
    def dfs(K, inter, cs):
        out.append(tuple(K))
        for i, x in enumerate(cs):
            new = addable(inter, X0, x)
            if new is None: continue
            if not matchable(K + [x], S0 if tau0 else None): continue
            dfs(K + [x], inter + new, cs[i + 1:])
    dfs([], [FULL], cand)
    return out
def classExtras(K, X0, rc):
    """rc extra row-dead classes (repeats allowed), jointly J-valid with X0 and K; returns list of all tuples (non-decreasing)."""
    res = []
    inter = [FULL]
    for c in K: inter = inter + [I & cls[c] for I in inter]
    def rec(E, inter, start):
        if len(E) == rc: res.append(tuple(E)); return
        for i in range(start, len(allc)):
            x = allc[i]
            new = addable(inter, X0, x)
            if new is None: continue
            rec(E + [x], inter + new, i)
    rec([], inter, 0)
    return res
def matchings(items, opts):
    if not items: yield {}; return
    it = items[0]
    for s in opts[it]:
        for m in matchings(items[1:], opts):
            if s not in m.values(): yield {**m, it: s}
def livemat(terms):
    R = np.zeros((9, v), dtype=np.float32); C = np.zeros((9, v), dtype=np.float32)
    for i, (r, a) in enumerate(terms):
        R[i] = bits(r); C[i] = bits(a)
    return R, C
def pass_support(terms, mask):
    cover = 0
    for r, a in terms: cover |= r & a
    if cover != FULL: return False
    R, C = livemat(terms)
    cnt = ((CL @ R.T > 0) & (CL @ C.T > 0)).sum(1)
    return bool((cnt[mask] >= csize[mask]).all())
t0 = time.time(); nres = 0; nalive_all = 0; nalive_78 = 0; kdist = {}
for zi, Z in enumerate(level):
    X0 = Cset(Z)
    S0 = [s for s in surv if blkrank(FULL ^ X0, FULL ^ cls[s]) == 8 - DD]
    for tau0 in ([1, 0] if S0 else [0]):
        sig0 = min(7, DD - 1 + tau0)
        for K in enumK(X0, S0, tau0):
            k = len(K); e = 8 - k; slack = sig0 + k - 9
            if slack < 0: continue
            z = e - slack; survleft = 8 - k - tau0
            if z > e: continue
            kdist[(tau0, k)] = kdist.get((tau0, k), 0) + 1
            rc = max(0, z - survleft)
            exs = classExtras(K, X0, rc)
            if not exs: continue
            nres += 1
            # support filter: every txx (number of tau-extras), survivor assignment, class extras
            items = list(K) + (['T0'] if tau0 else [])
            opts = dict(tauS); opts['T0'] = S0
            ok_any = False
            for tx in range(0, min(survleft, z) + 1):
                ncl = z - tx
                exs2 = exs if ncl == rc else classExtras(K, X0, ncl)
                for mt in matchings(items, opts):
                    free = [s for s in surv if s not in mt.values()]
                    for TX in itertools.combinations(free, tx):
                        for E in exs2:
                            terms = [(FULL ^ X0, FULL ^ (cls[mt['T0']] if tau0 else 0))]
                            terms += [(FULL ^ cls[c], FULL ^ cls[mt[c]]) for c in K]
                            terms += [(FULL ^ cls[c], FULL) for c in E]
                            terms += [(FULL, FULL ^ cls[s]) for s in TX]
                            terms += [(FULL, FULL)] * (9 - len(terms))
                            if pass_support(terms, np.ones(len(cl), bool)): nalive_all += 1; ok_any = True
                            if pass_support(terms, m78): nalive_78 += 1
    if zi % 20 == 0: print('Z', zi, 'residue', nres, 'alive(6-8 cliques)', nalive_all, 'alive(7-8)', nalive_78, round(time.time() - t0), flush=True)
print('STAGE2 DONE D', DD, 'subspaces', len(level), 'class-level residue configs', nres, 'alive after support filter (cliques 6-8):', nalive_all, '(7-8 only, as MASK9):', nalive_78)
print('valid-K size distribution (tau0,k):count', sorted(kdist.items()))
