# CALLERWORD cw2: does a CONSISTENT piece attribution exist on #7113 (each D-incidence event e -> one role r(e),
# S_e ⊆ M_r, v_e(r) != 0 at every stage of S_e, and per role the assigned S_e PARTITION M_r)?  CP-SAT, 1 thread.
import sys, json
sys.argv = [sys.argv[0], sys.argv[1]]
exec(open('cw1.py').read().split("for ty in ('A', 'B'):")[0])
from ortools.sat.python import cp_model
for ty in ('A', 'B'):
    n, ev, masks, exs = expand(ty)
    I = lambda: [[F(int(i == j)) for j in range(n)] for i in range(n)]
    P = I(); Pinv = I(); incs = []
    for j, e in enumerate(ev):
        apply(P, e, F(1)); inv_apply_right(Pinv, e)
        if e[0] == 'idle' and e[2]:
            v = [Pinv[r][e[1]] for r in range(n)]; w = [P[e[1]][r] for r in range(n)]
            incs.append((j, frozenset(e[2]), v, w, e[1]))
    for strict in (True, False):
        m = cp_model.CpModel(); x = {}
        for a, (j, S, v, w, reg) in enumerate(incs):
            for r in range(n):
                if S <= masks[r] and (not strict or (v[r] != 0 and w[r] != 0)):
                    x[a, r] = m.NewBoolVar('')
            m.AddExactlyOne([x[a, r] for r in range(n) if (a, r) in x])
        for r in range(n):
            for t in masks[r]:
                m.AddExactlyOne([x[a, r] for a, inc in enumerate(incs) if t in inc[1] and (a, r) in x])
        s = cp_model.CpSolver(); s.parameters.num_workers = 1; s.parameters.max_time_in_seconds = 600
        st = s.Solve(m)
        regok = sum(1 for a, inc in enumerate(incs) if s.StatusName(st) in ('OPTIMAL', 'FEASIBLE') and s.Value(x.get((a, inc[4]), m.NewConstant(0))) == 1) if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None
        print(ty, 'incidence events', len(incs), 'strict(v,w nonzero)' if strict else 'mask-only', '->', s.StatusName(st),
              ' (#events assigned to their own register:', regok, ')')
