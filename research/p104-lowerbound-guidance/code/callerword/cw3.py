# CALLERWORD cw3: built frames (C1 d3star-caller, c33 hosted-root-caller): replay, stage incidence/biorth/support,
# and existence of a consistent piece attribution (mask-only and strict), CP-SAT 1 thread. Own code; JSON = data.
import sys, json
from fractions import Fraction as F
src = open('cw1.py').read().split("for ty in ('A', 'B'):")[0].replace("C = json.load(open(sys.argv[1]))", "C = {'stages': 0, 'types': {}}")
exec(src)
from ortools.sat.python import cp_model
def expand2(C):
    n = C['roles']; ev = []
    for e in C['events']:
        op = e[0]
        if op == 'HOST':
            t, s, tt, a, b = e[1] - 1, e[2], e[3], F(e[4]), F(e[5])
            ev += [('host', s, tt, a, b), ('idle', s, {t}, 0), ('idle', tt, {t}, 0)]
        elif op == 'ADD': ev.append(('add', e[1], e[2], F(e[3])))
        elif op == 'SCALE': ev.append(('scale', e[1], F(e[2])))
        elif op == 'SWAP': ev.append(('swap', e[1], e[2]))
        elif op == 'QUERY': ev.append(('query', e[1], e[2], e[3]))
        elif op == 'LAMBDA': ev.append(('lam', e[1], e[2]))
        elif op == 'IDLE_ONE': ev.append(('idle', e[1], {s - 1 for s in e[2]}, 0))
        else: raise ValueError(op)
    masks = [{s for s, b in enumerate(dg[2:]) if b} for dg in C['diagonal']]
    return n, ev, masks, [dg[0] for dg in C['diagonal']]
for f in sys.argv[1:]:
    C = json.load(open(f)); k = C['stages']
    n, ev, masks, exs = expand2(C)
    I = lambda: [[F(int(i == j)) for j in range(n)] for i in range(n)]
    for q in (1, -1):
        M = I()
        for e in ev: apply(M, e, F(q))
        print(f.split('/')[-1], 'replay q=%d:' % q, all(M[i][j] == (F(qp(q, exs[i])) if i == j else 0) for i in range(n) for j in range(n)))
    P = I(); Pinv = I(); incs = []; ncol = 0
    for e in ev:
        apply(P, e, F(1)); inv_apply_right(Pinv, e); ncol += len(terms(e))
        if e[0] == 'idle' and e[2]:
            incs.append((frozenset(e[2]), [Pinv[r][e[1]] for r in range(n)], [P[e[1]][r] for r in range(n)], e[1]))
    bad = 0
    for t in range(k):
        E = [r for r in range(n) if t in masks[r]]; It = [i for i in incs if t in i[0]]
        bad += len(E) != len(It)
        bad += any(sum(a[2][r] * b[1][r] for r in range(n)) != (1 if a is b else 0) for a in It for b in It)
        bad += any((i[1][r] or i[2][r]) for i in It for r in range(n) if r not in E)
    multi = sum(1 for i in incs if len(i[0]) > 1)
    print('  n', n, 'k', k, 'columns', ncol, 'incidences', len(incs), 'multi-stage', multi, 'violations', bad)
    for strict in (True, False):
        m = cp_model.CpModel(); x = {}
        for a, (S, v, w, reg) in enumerate(incs):
            for r in range(n):
                if S <= masks[r] and (not strict or (v[r] != 0 and w[r] != 0)):
                    x[a, r] = m.NewBoolVar('')
            m.AddExactlyOne([x[a, r] for r in range(n) if (a, r) in x])
        for r in range(n):
            for t in masks[r]:
                m.AddExactlyOne([x[a, r] for a, inc in enumerate(incs) if t in inc[0] and (a, r) in x])
        s = cp_model.CpSolver(); s.parameters.num_workers = 1; s.parameters.max_time_in_seconds = 300
        print('  attribution', 'strict' if strict else 'mask-only', s.StatusName(s.Solve(m)))
