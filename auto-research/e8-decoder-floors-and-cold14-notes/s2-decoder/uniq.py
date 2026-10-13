"""Is the 9-total F2 decoder of a punctured bit pattern unique (= B0 restricted)?  And is c=8 UNSAT?"""
import sys, numpy as np
from geo import *
from minrank_sat import solve_asym, solve_minrank
from e8units import first_clique
def run(live):
    v = len(live)
    pat = {(i, j) for i in range(v) for j in range(v) if i != j and G[live[i], live[j]] != 0}
    adj = [[i != j and G[live[i], live[j]] != 0 for j in range(v)] for i in range(v)]
    K = first_clique(adj, 8)
    B0l = B0[np.ix_(live, live)]
    out = {}
    if K is None:
        out['clique'] = None; return out
    for c, mode in ((9, 'neB0'), (8, 'none')):
        r = solve_asym(v, pat, B0l, c, mode, K)
        out[(c, mode)] = r['result']
    return out
if __name__ == '__main__':
    P = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 and sys.argv[1] else []
    live = [i for i in range(NL) if i not in P]
    print(len(live), run(live), flush=True)
