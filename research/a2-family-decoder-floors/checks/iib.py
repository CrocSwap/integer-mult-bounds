# Class-level min-cost relaxation for Case II(b) (m' = 9) and for m' >= 10 (README 5.3, 7.2).  usage (as a module): from iib import relaxations
# A term pairs a row direction (its kill set = the label classes it kills; row directions = the row-deficient classes, one normal each; e9 = the row X; "full" = a direction killing nothing, unlimited)
# with a column direction; its cost is rank_F2 B[R, A] with R, A the supports avoiding the killed classes (exact rank formula).  Each catalogue direction is used at most once per side (merge lemma,
# non-parallel normals); the relaxation drops duality / independence and is solved by exact min-cost flow.  Column directions available:
#   S: the eta = 0 killers colS; T: the three triangle classes (each its unique killer); M: off the B-locus (gamma2 != gamma3) AT MOST ONE merged class (mergedkill.py), alone or merged with the T_i, T_j it
#   co-kills.  On the B-locus (gamma2 = gamma3) no M is killable by a direction with the rest of S, T: a column normal there kills at most one of the 11/19/3 classes: S + T only.
from a2cls import *
import networkx as nx
def solve(rows, cols, mt):
    f = [[blk(Brows, a, b) for b in cols + [list(range(v))]] for a in rows + [list(range(v))]]
    nr, nc = len(rows), len(cols)
    G = nx.DiGraph(); G.add_node('s', demand=-mt); G.add_node('t', demand=mt)
    for i in range(nr + 1): G.add_edge('s', ('r', i), capacity=1 if i < nr else mt, weight=0)
    for j in range(nc + 1): G.add_edge(('c', j), 't', capacity=1 if j < nc else mt, weight=0)
    for i in range(nr + 1):
        for j in range(nc + 1): G.add_edge(('r', i), ('c', j), capacity=mt, weight=f[i][j])
    return nx.min_cost_flow_cost(G)
def relaxations(mts):
    """returns {'off': {mt: min over off-locus column options}, 'on': {mt: B-locus value}}  for Case II rows (no e9), and the same with the e9 row for m' >= 10 ('off9', 'on9')."""
    rows2 = [sup_avoid([a]) for a in rowdef]
    rows9 = rows2 + [Xs]
    base = [sup_avoid([c]) for c in colS] + [sup_avoid([t]) for t in Tg]
    out = {'off': {}, 'on': {}, 'off9': {}, 'on9': {}}
    for mt in mts:
        opts = []
        for m in Mg:
            ts = [t for t in Tg if (t ^ m) in Tg]; tk = [t for t in Tg if t not in ts]
            opts.append(('T+singleM', m, lambda rows, m=m: solve(rows, base + [sup_avoid([m])], mt)))
            opts.append(('merged+Tk', m, lambda rows, m=m, ts=ts, tk=tk: solve(rows, [sup_avoid([c]) for c in colS] + [sup_avoid([m] + ts)] + [sup_avoid([t]) for t in tk], mt)))
        out['on'][mt] = solve(rows2, base, mt); out['on9'][mt] = solve(rows9, base, mt)
        out['off'][mt] = min(o[2](rows2) for o in opts); out['off9'][mt] = min(o[2](rows9) for o in opts)
    return out
