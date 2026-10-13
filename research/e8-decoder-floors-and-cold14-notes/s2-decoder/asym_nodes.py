"""Nodes for rank-1 shared extra totals with beta = <L, g> on Q (complex P112, frame decoder).
node = (t, w, n1, case, mu) with required-in set I and required-out set O for Q."""
import pickle, numpy as np, sys
from fractions import Fraction as Fr
from geo import *
H = pickle.load(open('hyper.pkl', 'rb'))
NORMALS = [np.array(n, dtype=np.int64) for sz in H for (n, m) in H[sz]]
NMASK = [m for sz in H for (n, m) in H[sz]]
LIVE = list(range(8, 120)); LIVEMASK = sum(1 << i for i in LIVE)
def nodes_for_g(g, targets=LIVE):
    g = np.array(g, dtype=np.int64)
    pg = L @ g
    out = []
    for t in targets:
        for w in range(1, 512):
            if w == uint[t] or not lab_dot(w, uint[t]): continue
            Z = Rmask[w] & LIVEMASK & ~(1 << t)
            Zl = members(Z)
            for k, n1 in enumerate(NORMALS):
                pn = L @ n1
                inH = [S for S in Zl if pn[S] == 0]
                rest = [S for S in Zl if pn[S] != 0]
                mus = {Fr(int(pg[S]), int(pn[S])) for S in rest}
                if len(mus) != 1: continue
                mu = mus.pop()
                for case in ('A', 'B'):
                    # h = mu*n1 (A) or h = g - mu*n1 (B)
                    if case == 'A':
                        I = [S for S in rest]
                        Ob = [S for S in inH if pg[S] != 0]
                        if any(pg[S] == 0 for S in I): continue
                        hdot_t = mu * int(pn[t])
                    else:
                        I = [S for S in inH if pg[S] != 0]
                        Ob = [S for S in rest if pg[S] != 0]
                        hdot_t = int(pg[t]) - mu * int(pn[t])
                    if mu == 0 and case == 'A': continue
                    out.append(dict(t=t, w=w, k=k, case=case, mu=mu, I=frozenset(I), O=frozenset(Ob), hdot_t=hdot_t,
                                    gt=int(pg[t]), Z=Z))
    return out
def compatible(a, b):
    if a['t'] == b['t']: return False
    if a['I'] & b['O'] or b['I'] & a['O']: return False
    Q = a['I'] | b['I']
    for S in Q:
        ra = 1 if (a['Z'] >> S & 1) or S == a['t'] else 0
        rb = 1 if (b['Z'] >> S & 1) or S == b['t'] else 0
        if ra != rb: return False
    # diag: beta_t (= g.t if t in Q else 0) != h.t
    for x in (a, b):
        bt = x['gt'] if x['t'] in Q else 0
        if bt == x['hdot_t']: return False
    return True
def node_ok_alone(a):
    bt = a['gt'] if a['t'] in a['I'] else 0
    if bt == a['hdot_t']: return False
    if not a['I']: return False      # no extra total needed would be a free relaxation (none exist)
    return True
if __name__ == '__main__':
    import networkx as nx, time
    d0 = int(sys.argv[1])
    t0 = time.time()
    nodes = [a for a in nodes_for_g(L[d0]) if node_ok_alone(a)]
    print('g = line', d0, 'nodes', len(nodes), 'targets', len({a['t'] for a in nodes}), round(time.time() - t0, 1), flush=True)
    # dedupe by (t, I, O, row-relevant Z, diag)
    Gx = nx.Graph(); Gx.add_nodes_from(range(len(nodes)))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if compatible(nodes[i], nodes[j]): Gx.add_edge(i, j)
    print('edges', Gx.number_of_edges(), flush=True)
    cl, sz = nx.max_weight_clique(Gx, weight=None)
    print('max rank-1 group', sz, sorted({nodes[i]['t'] for i in cl}), [sorted(nodes[i]['I']) for i in cl][:3], flush=True)
