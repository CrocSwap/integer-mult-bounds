# JS-RANK jr_lagx: EXACT (Fraction) re-evaluation of the Lagrangian bound at saved multipliers lam_cfgC.pkl:
#   LB = sum_k min_flag sum_c lam_ck [tau_k(t) > sigma_k(s)] + sum_c min_L (f_c(L) - sum_k lam_ck L_k)   (lam >= 0 checked).
# Chain minima by the exact flag DP (jr_lag.flagmin, Fraction weights). Own code. Usage: jr_lagx.py CFG [LAM.pkl]
import sys, os, pickle
ci_ = int(sys.argv[1]); LAMF = sys.argv[2] if len(sys.argv) > 2 else f'lam_cfg{ci_}.pkl'; sys.argv = ['x', str(ci_)]; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jr_lag.py')).read().split("ci = int(sys.argv[1])")[0])
ch = chains(ci_); lam = pickle.load(open(LAMF, 'rb'))
assert all(v >= 0 for v in lam.values())
tot = Fr(0)
for k in range(8):
    W = {c: v for (c, kk), v in lam.items() if kk == k and v > 0}
    z, zp, w, u, g = ch[k]; m = flagmin(z, zp, W); tot += m; print('chain', k, 'min', m, flush=True)
loc = Fr(0)
for t in range(n):
    for s in range(n):
        if t == s or dot(Q[t], Q[s]): continue
        ks = [k for k in range(8) if prodk(ch, k, t, s)]; vals = [prodk(ch, k, t, s) for k in ks]
        best = None
        for m in range(1 << len(ks)):
            f = 0 if sum(v for i, v in enumerate(vals) if m >> i & 1) == 0 else 1
            v = f - sum(lam[(t, s), ks[i]] for i in range(len(ks)) if m >> i & 1)
            best = v if best is None or v < best else best
        loc += best
print('cfg', ci_, 'chain part', tot, 'local part', loc, 'EXACT LB', tot + loc, float(tot + loc))
