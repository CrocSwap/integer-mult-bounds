"""Exact CP-SAT for the combinatorial all-but-one(n) module model (one node per support):
nodes = supports S with one split recipe; donor A|B hands A to target A|W iff B strict-subset W. minimise adds - arcs."""
import sys, time, itertools
from ortools.sat.python import cp_model
n = int(sys.argv[1]); limit = float(sys.argv[2]); full = (1 << n) - 1
def subsets_of(mask):
    s = mask
    while s:
        yield s
        s = (s - 1) & mask
m = cp_model.CpModel()
e = {}; r = {}
for S in range(1, full + 1):
    k = bin(S).count('1')
    if k == 1: continue
    if k == n: continue
    e[S] = m.NewBoolVar('e%d' % S)
    splits = []
    for A in subsets_of(S):
        B = S ^ A
        if A and B and A < B:
            r[S, A] = m.NewBoolVar('r'); splits.append(r[S, A])
    m.Add(sum(splits) == e[S])
    if k == n - 1: m.Add(e[S] == 1)
def exists(A):
    return None if bin(A).count('1') == 1 else e[A]
for (S, A), v in r.items():
    for part in (A, S ^ A):
        ex = exists(part)
        if ex is not None: m.AddImplication(v, ex)
# usage: every non-output node must be an operand of some recipe
used_by = {}
for (S, A), v in r.items():
    for part in (A, S ^ A):
        if bin(part).count('1') >= 2: used_by.setdefault(part, []).append(v)
for S, v in e.items():
    if bin(S).count('1') <= n - 2:
        m.AddBoolOr(used_by.get(S, []) + [v.Not()])
def recipe(S, A):
    B = S ^ A
    return r[S, min(A, B)]
arcs = {}; out_by_donor = {}; in_by_slot = {}
t0 = time.time()
for A in range(1, full + 1):
    rest = full ^ A
    for W in subsets_of(rest):
        if bin(W).count('1') < 2: continue
        T = A | W
        if T == full: continue
        for B in subsets_of(W):
            if B == W: continue
            S = A | B
            v = m.NewBoolVar('a')
            arcs[A, B, W] = v
            m.AddImplication(v, recipe(S, A)); m.AddImplication(v, recipe(T, A))
            out_by_donor.setdefault(S, []).append(v); in_by_slot.setdefault((A, T), []).append(v)
for vs in out_by_donor.values(): m.Add(sum(vs) <= 1)
for vs in in_by_slot.values(): m.Add(sum(vs) <= 1)
print('n', n, 'recipes', len(r), 'arcs', len(arcs), 'built %.0fs' % (time.time() - t0), flush=True)
def rot(mask, k=1):
    return ((mask << k) | (mask >> (n - k))) & full
import os
sym = os.environ.get('SYM')
if sym:
    step = int(sym)  # rotation by `step` positions generates the symmetry group
    for (S, A), v in list(r.items()):
        S2, A2 = rot(S, step), rot(A, step); B2 = S2 ^ A2
        m.Add(v == r[S2, min(A2, B2)])
    for (A, B, W), v in list(arcs.items()):
        m.Add(v == arcs[rot(A, step), rot(B, step), rot(W, step)])
    print('symmetry: rotation by', step, flush=True)
m.Minimize(1000 * (sum(e.values()) - sum(arcs.values())) + sum(e.values()))
import os, json
hint = os.environ.get('HINT')
if hint:
    hc = json.load(open(hint)); hn = hc['input_count']; hs = [1 << i for i in range(hn)]
    seen = {}
    for x in range(hn, len(hc['args'])):
        a, b = hc['args'][x]; S = hs[a] | hs[b]; hs.append(S)
        if S not in seen: seen[S] = min(hs[a], hs[b])
    for (S, A), v in r.items(): m.AddHint(v, 1 if seen.get(S) == A else 0)
    for S, v in e.items(): m.AddHint(v, 1 if S in seen else 0)
    print('hinted', len(seen), 'nodes', flush=True)
if os.environ.get('WORKERS'): pass
s = cp_model.CpSolver(); s.parameters.num_workers = int(os.environ.get('WORKERS', '8')); s.parameters.max_time_in_seconds = limit; s.parameters.log_search_progress = False
class CB(cp_model.CpSolverSolutionCallback):
    def __init__(self): super().__init__(); self.t0 = time.time()
    def on_solution_callback(self): print('  sol debt %d adds %d bound %.1f %.0fs' % (self.ObjectiveValue() // 1000, self.ObjectiveValue() % 1000, self.BestObjectiveBound() / 1000, time.time() - self.t0), flush=True)
st = s.Solve(m, CB())
print('n', n, 'status', s.StatusName(st), 'debt', s.ObjectiveValue() // 1000, 'bound', s.BestObjectiveBound() / 1000, '%.0fs' % (time.time() - t0), flush=True)
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    nodes = [(S, A) for (S, A), v in r.items() if s.Value(v)]
    print('adds', len(nodes), 'arcs', sum(s.Value(v) for v in arcs.values()))
    print('recipes', [(bin(S)[2:].zfill(n)[::-1], bin(A)[2:].zfill(n)[::-1]) for S, A in sorted(nodes, key=lambda t: bin(t[0]).count('1'))])

    # export circuit in generator format: inputs 0..n-1, nodes by size then mask
    import json
    idx = {1 << i: i for i in range(n)}; args = [None] * n
    for S, A in sorted(nodes, key=lambda t: (bin(t[0]).count('1'), t[0])):
        B = S ^ A; args.append([idx[A], idx[B]]); idx[S] = len(args) - 1
    roots = [idx[full ^ (1 << i)] for i in range(n)]
    out = sys.argv[3] if len(sys.argv) > 3 else 'out/abo_cpsat_n%d.json' % n
    json.dump(dict(input_count=n, args=args, roots=roots, provenance=dict(source='gen5 cpsat_abo.py exact CP-SAT (combinatorial module model, one node per support)', debt=int(s.ObjectiveValue() // 1000), additions=len(nodes))), open(out, 'w'))
    from comb_model import evaluate
    print('comb_model check', evaluate(dict(input_count=n, args=args, roots=roots)))
