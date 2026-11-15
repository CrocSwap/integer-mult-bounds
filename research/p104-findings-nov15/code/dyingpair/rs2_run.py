"""CALLEROPEN rs2_run.py: O3 feasibility rows (rs2 model).  Stopping rule: STARTS random starts per row, nfev 600 each."""
import sys, json, time
from rs2 import *
STARTS = int(sys.argv[1]) if len(sys.argv) > 1 else 6
Ls = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else [4, 5, 6]
out = []
for L in Ls:
    nl = L // 2; rows = []
    n, o, th = two_arm(L, 2); Z = [it[1] for it in o if it[0] == 'S']
    rows.append(('ctl B two-hub', n, o, ()))
    rows.append(('neg one-hub (Thm 1\')', *two_arm(L, 1)[:2], ()))
    rows.append(('TEST tight (outer masks = hubs only)', *two_arm(L, 2, outer_own=0)[:2], ()))
    rows.append(('TEST B + 2 lines across LEFT outer bdry', n, o, ((0, 1, 2),)))
    rows.append(('TEST B + 1 line across LEFT outer bdry', n, o, ((0, 1, 1),)))
    rows.append(('TEST B + 2 lines across RIGHT outer bdry', n, o, ((L - 2, L - 1, 2),)))
    if nl >= 3:
        S = len(set(Z[1]) & set(Z[2]))
        rows.append(('ctl B, |S|-4=%d lines across left 1|2' % (S - 4), n, o, ((1, 2, S - 4),)))
        rows.append(('TEST B, |S|-3=%d lines across left 1|2 (Lemma C: no)' % (S - 3), n, o, ((1, 2, S - 3),)))
    for lab, n_, o_, ln in rows:
        t0 = time.time(); m = Model(n_, o_, -0.5, ln); h, b, z = run(m, STARTS)
        print('L=%d %-48s n=%2d N=%2d vars %4d solved %d/%d best %.1e  (%.0fs)' % (L, lab, n_, m.N, m.dim, h, STARTS, b, time.time() - t0), flush=True)
        out.append(dict(L=L, row=lab, n=n_, N=m.N, vars=m.dim, solved=h, starts=STARTS, best=b))
        if h: np.save('sol_L%d_%s.npy' % (L, ''.join(c for c in lab if c.isalnum())[:30]), z)
json.dump(out, open('rs2_%s.json' % '_'.join(map(str, Ls)), 'w'), indent=1)
