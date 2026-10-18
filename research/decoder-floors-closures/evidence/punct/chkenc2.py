r"""PUNCT7: SAT-side strengthening of chkenc.py. usage: chkenc2.py typ P nmodels
CNF (rkdirect.py, S fixed by assumptions, Minisat22)  <=>  direct test (chkenc.direct: |S|<=P, every 8-frame hit, every live line outside F*
has rank(live lines orth to it) < 7, numpy rank on L rows). Test sets:
 (a) theory family (P = 50, typ 7 only): S = N'(alpha) minus C over ALL 7-cliques C of N'(alpha)\{alpha} (expected SAT), and minus 6-cliques
     (|S| = 51, expected UNSAT by size) and minus 7-clique plus one line;
 (b) nmodels distinct solver models (blocking clauses on S vars);
 (c) every single-line deletion and 30 random single-line swaps of each (a)/(b) SAT set."""
import sys, random, numpy as np, networkx as nx
sys.path.insert(0, '/Users/mason/repo_clones/intmult-work/cards/PUNCT4')
from p4lib import G, FLATREP, L
from pysat.solvers import Minisat22
typ, P, nm = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
flat = FLATREP[typ][1]
cnf = []
for ln in open(f'cnf/rkd_{typ}_{P}.cnf'):
    if ln[0] == 'p': continue
    cnf.append([int(x) for x in ln.split()[:-1]])
orth = [set(t2 for t2 in range(120) if G[t, t2] == 0) for t in range(120)]
FR = []
def dfs(cur, cand):
    if len(cur) == 8: FR.append(cur); return
    for s in sorted(cand):
        if s > cur[-1]: dfs(cur + [s], cand & orth[s])
for t in range(120): dfs([t], orth[t])
assert len(FR) == 2025
def direct(S):
    S = set(S)
    if len(S) > P: return False
    if any(all(t not in S for t in f) for f in FR): return False
    live = [t for t in range(120) if t not in S]
    for s in live:
        if flat[s]: continue
        o = [t for t in live if G[s, t] == 0]
        if np.linalg.matrix_rank(L[o].astype(float)) >= 7: return False
    return True
sol = Minisat22(bootstrap_with=cnf); del cnf
def cnfsat(S): return sol.solve(assumptions=[(t + 1) if t in S else -(t + 1) for t in range(120)])
tests = []; satsets = []
if typ == 7 and P == 50:
    a = [t for t in range(120) if not flat[t]]
    alpha = [t for t in a if all(G[t, s] != 0 for s in a)]
    for al in alpha:
        N = [t for t in a if t != al]
        g = nx.Graph(); g.add_nodes_from(N); g.add_edges_from((i, j) for i in N for j in N if i < j and G[i, j] != 0)
        cl7 = [c for c in nx.find_cliques(g) if len(c) >= 7]
        import itertools
        seven = set(); six = set()
        for c in cl7:
            for s in itertools.combinations(sorted(c), 7): seven.add(s)
        for s in list(seven)[:200]:
            for x in itertools.combinations(s, 6): six.add(x)
        print('alpha', al, '7-cliques', len(seven), flush=True)
        for c in seven: tests.append(('fam7', set(a) - set(c)))
        for c in list(six)[:200]: tests.append(('fam6', set(a) - set(c)))
        for c in list(seven)[:100]:
            extra = random.Random(sum(c)).choice([t for t in range(120) if t not in set(a) - set(c)])
            tests.append(('fam7+1', (set(a) - set(c)) | {extra}))
models = []
while len(models) < nm and sol.solve():
    m = sol.get_model(); S = {t for t in range(120) if m[t] > 0}; models.append(S)
    sol.add_clause([-(t + 1) if t in S else (t + 1) for t in range(120)])
print('distinct solver models', len(models), flush=True)
sol.delete(); cnf = [ln for ln in open(f'cnf/rkd_{typ}_{P}.cnf') if ln[0] != 'p']
sol = Minisat22(bootstrap_with=[[int(x) for x in ln.split()[:-1]] for ln in cnf]); del cnf
for S in models: tests.append(('model', S))
rnd = random.Random(7)
base_sat = [S for k, S in tests if k in ('fam7', 'model')]
for S in base_sat[:150]:
    for t in sorted(S): tests.append(('del', S - {t}))
    for _ in range(30):
        t = rnd.choice(sorted(S)); u = rnd.choice([x for x in range(120) if x not in S]); tests.append(('swap', (S - {t}) | {u}))
from collections import Counter
cnt = Counter(); pos = Counter()
for k, S in tests:
    a_, b_ = cnfsat(S), direct(S)
    assert a_ == b_, ('MISMATCH', k, sorted(S), a_, b_)
    cnt[k] += 1; pos[k] += a_
print('type', typ, 'P', P, 'tests', sum(cnt.values()), 'SAT', sum(pos.values()), {k: (cnt[k], pos[k]) for k in cnt}, 'ALL AGREE', flush=True)
