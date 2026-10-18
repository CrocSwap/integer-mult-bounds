# MASK9 case (b): support filter on cnt7 residues. For each residue (Z_0, τ_0, K): every survivor assignment (matching K ∪ {term 0 if τ_0}),
# every choice of rc extra row-dead classes (J-valid), remaining extras unconstrained (all lines live: a relaxation). Known dead sets:
# term 0 rows ⊇ C(Z_0), cols ⊇ O_s0 (τ_0); small k rows ⊇ O_ck, cols ⊇ O_sk; extra with class c rows ⊇ O_c. Live sets are taken maximal
# (complements), so each test below is a necessary condition (sound):
#  (D) every line t is live on both sides for some term; (C) every orthogonal 7-/8-clique C has >= |C| terms live on C on both sides
#  (STRAYS-MASK2 §2 rule C: M[C,C] diagonal invertible).    usage: cnt8.py UNIT D
import sys
DD = int(sys.argv[2]); sys.argv = sys.argv[:2]
from m9lib import *
res = pickle.load(open(f'cnt7_{unit}_{DD}.pkl', 'rb'))
cliques = [sum(1 << t for t in c) for c in pickle.load(open(f'cliques_{unit}.pkl', 'rb')) if len(c) in (7, 8)]
csz = {Cq: pc(Cq) for Cq in cliques}
print('residues', len(res), 'cliques', len(cliques), flush=True)
allc = [c for c in ks if cls[c] != full]
def jok(sets, x, X0):
    for r in range(0, len(sets) + 1):
        for J in itertools.combinations(sets, r):
            X = cls[x]
            for c in J: X &= cls[c]
            if r >= 1 and lb(X) > 9 - (r + 1): return False
            if lb(X0 & X) > 9 - (r + 2): return False
    return True
def matchings(items, opts):
    if not items: yield {}; return
    it = items[0]
    for s in opts[it]:
        for m in matchings(items[1:], opts):
            if s not in m.values(): yield {**m, it: s}
seenZK = set(); alive = []
t0 = time.time()
for (Z, tau0, K, _) in res:
    if (Z, tau0, K) in seenZK: continue
    seenZK.add((Z, tau0, K))
    X0 = C(Z); k = len(K)
    sig0 = min(7, DD - 1 + tau0); e = 8 - k; slack = sig0 + k - 9; survleft = 8 - k - tau0
    rc = max(0, e - slack - survleft)
    S0 = [s for s in surv if rk(full ^ X0, full ^ cls[s]) == 8 - DD]
    opts = dict(tauS); opts['T0'] = S0
    items = list(K) + (['T0'] if tau0 else [])
    nok = 0
    for tx in range(0, min(survleft, e - slack) + 1):
        ncl = e - slack - tx
        extras = []
        def ext(E, cs):
            if len(E) == ncl: extras.append(tuple(E)); return
            for i, x in enumerate(cs):
                if jok(list(K) + E, x, X0): ext(E + [x], cs[i:])   # repeats allowed (two extras may share a survivor class; audit item 2)
        ext([], allc)
        for m in matchings(items, opts):
            free = [s_ for s_ in surv if s_ not in m.values()]
            for TX in itertools.combinations(free, tx):
                for E in extras:
                    terms = [(full ^ X0, full ^ (cls[m['T0']] if tau0 else 0))]
                    terms += [(full ^ cls[c], full ^ cls[m[c]]) for c in K]
                    terms += [(full ^ cls[c], full) for c in E]
                    terms += [(full, full ^ cls[s_]) for s_ in TX]
                    terms += [(full, full)] * (9 - len(terms))
                    cover = 0
                    for r_, a_ in terms: cover |= r_ & a_
                    if cover != full: continue
                    if all(sum(1 for r_, a_ in terms if r_ & Cq and a_ & Cq) >= csz[Cq] for Cq in cliques):
                        nok += 1; alive.append((Z, tau0, K, m, E, TX))
    print('Z', Z[:4], 'tau0', tau0, 'K', K, 'rc', rc, 'surviving (matching, extras)', nok, round(time.time() - t0), flush=True)
print('DONE D', DD, 'alive after support filter', len(alive), flush=True)
pickle.dump(alive, open(f'cnt8_{unit}_{DD}.pkl', 'wb'))
