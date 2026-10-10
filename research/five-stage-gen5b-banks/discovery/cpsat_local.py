"""Exact CP-SAT model of the per-cube local-channel debt: 12 planes x 15 recipe trees; donors = pair nodes; arcs to
partner roots / direct uses of a source at other pair, triple or plane nodes; feasibility from exact initial frames."""
import sys, pickle, json, time
from itertools import combinations
from ortools.sat.python import cp_model
from local_model import *
F = pickle.load(open('out/feas.pkl', 'rb'))
cubes = load_cubes('out/cube_data.pkl'); c = cubes[0]; T = c.T
pairs, planes_of, patterns, RECIPES = F['pairs'], F['planes_of'], F['patterns'], F['RECIPES']
ann_pair = {(x, S): T.join_many([c.PA[k] for k in S] + [c.cover_pad(x)]) for x in pairs for S in patterns[x]}
ann_plane = {k: T.join(c.PA[k], c.cover_pad(MEMBERS[k])) for k in PLANES}
ann_triple = {(k, frozenset(tri)): T.join(c.PA[k], c.cover_pad(frozenset(tri))) for k in PLANES for tri in combinations(MEMBERS[k], 3)}
partner = c.partner
m = cp_model.CpModel()
Tv = {(k, i): m.NewBoolVar('T_%s_%d' % (k, i)) for k in PLANES for i in range(15)}
for k in PLANES: m.AddExactlyOne(Tv[k, i] for i in range(15))
def recipe_pairs(r): return [r[1], r[2]] if r[0] == 'bal' else [r[1]]
def recipe_direct_sources(r): return [] if r[0] == 'bal' else [r[2], r[3]]  # 'cat': ((pr)+third)+last: third used by triple, last by plane
U = {}
for x in pairs:
    for k in planes_of[x]:
        U[x, k] = m.NewBoolVar('U')
        lits = [Tv[k, i] for i, r in enumerate(RECIPES[k]) if x in recipe_pairs(r)]
        m.AddMaxEquality(U[x, k], lits)
E = {}
for x in pairs:
    E[x] = m.NewBoolVar('E'); m.AddMaxEquality(E[x], [U[x, k] for k in planes_of[x]])
cat = {k: m.NewBoolVar('cat') for k in PLANES}
for k in PLANES: m.Add(cat[k] == sum(Tv[k, i] for i, r in enumerate(RECIPES[k]) if r[0] == 'cat'))
# use-existence literals
def tri_use(k, tri, y):  # triple node in plane k with recipe (tri-{y}) + y
    return [Tv[k, i] for i, r in enumerate(RECIPES[k]) if r[0] == 'cat' and r[1] | {r[2]} == tri and r[2] == y]
def plane_use(k, y):
    return [Tv[k, i] for i, r in enumerate(RECIPES[k]) if r[0] == 'cat' and r[3] == y]
A = {}; use_vars = {}
def pattern_lits(x, S):  # literals asserting U[x,.] == S
    return [U[x, k] if k in S else U[x, k].Not() for k in planes_of[x]]
for x in pairs:
    for y in x:
        targets = [('root',)] + [('pair', t) for t in pairs if t != x and y in t]
        for k in PLANES:
            if y in MEMBERS[k]:
                targets.append(('plane', k))
                for tri in combinations(MEMBERS[k], 3):
                    tri = frozenset(tri)
                    if y in tri: targets.append(('tri', k, tri))
        for tgt in targets:
            a = m.NewBoolVar('A'); A[x, y, tgt] = a
            m.AddImplication(a, E[x])
            use_vars.setdefault((y, tgt), []).append(a)
            if tgt[0] == 'pair':
                t = tgt[1]; m.AddImplication(a, E[t])
                for Sx in patterns[x]:
                    for St in patterns[t]:
                        ax, at = ann_pair[x, Sx], ann_pair[t, St]
                        ok = T.contained(at, ax) and at != ax
                        if not ok: m.AddBoolOr([a.Not()] + [l.Not() for l in pattern_lits(x, Sx) + pattern_lits(t, St)])
            else:
                if tgt[0] == 'tri': ex = tri_use(tgt[1], tgt[2], y); at = ann_triple[tgt[1], tgt[2]]
                elif tgt[0] == 'plane': ex = plane_use(tgt[1], y); at = ann_plane[tgt[1]]
                else: ex = None; at = partner[y]
                if ex is not None: m.AddBoolOr(ex + [a.Not()])
                for Sx in patterns[x]:
                    ax = ann_pair[x, Sx]
                    ok = T.contained(at, ax) and (tgt[0] == 'root' or at != ax)
                    if not ok: m.AddBoolOr([a.Not()] + [l.Not() for l in pattern_lits(x, Sx)])
for x in pairs:
    m.Add(sum(A[k] for k in A if k[0] == x) <= 1)
for key, vs in use_vars.items(): m.Add(sum(vs) <= 1)
debt = 12 + sum(cat.values()) + sum(E.values()) - sum(A.values())
m.Minimize(debt)
solver = cp_model.CpSolver(); solver.parameters.num_workers = 8; solver.parameters.max_time_in_seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 600
t0 = time.time(); st = solver.Solve(m)
print('status', solver.StatusName(st), 'obj', solver.ObjectiveValue(), 'bound', solver.BestObjectiveBound(), '%.1fs' % (time.time() - t0))
# extract design
def tree_of(r):
    if r[0] == 'bal':
        p1, p2 = sorted(r[1]), sorted(r[2]); return [[list(p1[0]), list(p1[1])], [list(p2[0]), list(p2[1])]]
    p = sorted(r[1]); return [[[list(p[0]), list(p[1])], list(r[2])], list(r[3])]
design = []
for k in PLANES:
    i = next(i for i in range(15) if solver.Value(Tv[k, i])); design.append([list(k), tree_of(RECIPES[k][i])])
nodes = design_to_nodes(design)
res = [cu.evaluate(nodes) for cu in cubes]
from collections import Counter
print('independent evaluation on all cubes:', Counter(res))
print('arcs chosen:', [(tuple(sorted(k[0])), k[1], k[2][:2]) for k, v in A.items() if solver.Value(v)])
json.dump(dict(design=design, provenance=dict(source='gen5 cpsat_local.py exact CP-SAT optimum', debt=solver.ObjectiveValue())), open('out/design_opt.json', 'w'))
