# Recomputes the finite geometric INPUTS the counting uses (all inputs stated in README section 3): unit sizes, frame counts, the label table (h = 9,
# 511 classes), the Lemma 1.1 survivors (classes whose propagation fixed point leaves S_E != empty for every... i.e. NOT certified), survivor
# pair ranks, orthogonal 7-cliques inside survivors, "no plane of the label space contains 3 survivors".   usage: inputs_check.py
import sys, itertools, networkx as nx
from setup9 import *
from common2 import B0rows, rank_f2
from lib2 import E8, dot
ok = True
def chk(name, cond, detail=''):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name + (' ' + str(detail) if detail != '' else ''), flush=True)
for unit, nl, nfr, nsurv, pairranks, nstar in [('P112', 112, 1260, 8, {8}, 56), ('P104', 104, 759, 16, {7, 8}, 52)]:
    L, v, G, frames, nbar, h, basis, cls = load(unit)
    chk(f'{unit}: lines / 8-frames / label dimension h', (v, len(frames), h) == (nl, nfr, 9), (v, len(frames), h))
    chk(f'{unit}: 511 distinct nonzero label classes', len(set(cls.values())) == 511 and all(cls.values()))
    surv = [c for c in sorted(cls) if min(pc(s) for s in propagate(cls[c], frames, nbar, v)) > 0]
    chk(f'{unit}: Lemma 1.1 leaves exactly {nsurv} classes uncertified (survivors), each of {nstar} lines', len(surv) == nsurv and all(pc(cls[c]) == nstar for c in surv), (len(surv), sorted({pc(cls[c]) for c in surv})))
    full = (1 << v) - 1; B0 = B0rows(L)
    def rk(R, A):
        Rl = [t for t in range(v) if R >> t & 1]; Al = [s for s in range(v) if A >> s & 1]
        return rank_f2([sum(1 << i for i, s in enumerate(Al) if B0[t] >> s & 1) for t in Rl])
    rks = {rk(full ^ cls[a], full ^ cls[b]) for a in surv for b in surv}
    chk(f'{unit}: survivor-pair ranks rank_F2 B[V\\O_z, V\\O_z\'] in {sorted(pairranks)}', rks == pairranks, sorted(rks))
    og = nx.Graph(); og.add_nodes_from(range(v)); og.add_edges_from((t, s) for t in range(v) for s in range(t + 1, v) if G[t][s] == 0)
    om = [max(len(c) for c in nx.find_cliques(og.subgraph([t for t in range(v) if cls[s] >> t & 1]))) for s in surv]
    chk(f'{unit}: every survivor class contains an orthogonal 7-clique and no 8-frame', set(om) == {7}, sorted(set(om)))
    chk(f'{unit}: no plane of label space contains 3 survivors (survivors pairwise sum to non-survivors)', all((a ^ b) not in surv for a, b in itertools.combinations(surv, 2)))
    F0_, F1_ = load_frames(); rem = F0_ if unit == 'P112' else F0_ + F1_
    live = [i for i in range(120) if i not in set(rem)]
    perp = {sum(1 << k for k, i in enumerate(live) if dot(E8[i], E8[f]) == 0) for f in rem}
    chk(f'{unit}: the survivors are exactly the sets of live lines orthogonal to one removed root (Gram-deficient classes)', {cls[c] for c in surv} == perp, len(perp))
print('ALL PASS' if ok else 'SOME FAIL'); sys.exit(0 if ok else 1)
