"""Two-stage search: zero-gain cycles that raise free(X), then a second cycle on the same X (relaxed DP reused).
argv: LIBDIR START OUT_PREFIX DEPTH"""
import sys
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3], '0', sys.argv[4]]
exec(open(sys.argv[1] + '/chain.py').read().split("m = lib.Limbo")[0])
from collections import Counter
m = lib.Limbo(lib.read(start)); m._out = set()
A, wit, absorb, awit = build(m); Ps, args = paths(A)
stk = np.stack(Ps); best = stk.max(0); bestd = stk.argmax(0); del stk
Tidx = np.arange(T)
def closures(mm, X, thr):
    fX = mm.free(X); out = []
    allowedX = np.zeros(T, bool); allowedX[list(mm.allowed[X])] = True
    famocc = np.array([mm.fam[X] in mm.occ[t] for t in range(T)])
    for r0 in mm.members[X]:
        z = mm.roles[r0]; w0, t0_ = z['width'], z['time']; i = sid(w0, t0_)
        okT = allowedX & (~famocc | (Tidx == t0_))
        for wk in WS:
            if wk >= w0 or wk > fX + w0: continue   # X must strictly gain
            tot = np.where(okT, best[i, WI[wk]*T:(WI[wk]+1)*T] + (g(fX + w0 - wk) - g(fX)), -1e9)
            for tk in np.nonzero(tot > thr)[0]: out.append((float(tot[tk]), X, r0, i, sid(wk, int(tk))))
    return sorted(out, key=lambda c: -c[0])
stage1 = []
for X in m.cap:
    if m.members[X]: stage1 += closures(m, X, -1e-6)
print('stage1 zero/positive X-gaining cycles (relaxed):', len(stage1), Counter(round(c[0], 3) for c in stage1).most_common(5), flush=True)
byX = Counter(c[1] for c in stage1); print('distinct X', len(byX))
found = None; tried = 0; perX = Counter(); sec_rel = Counter(); sec_exact = 0
for c in stage1:
    if perX[c[1]] >= 3: continue
    perX[c[1]] += 1
    tot, X, r0, i, j = c
    r = try_apply(m, X, r0, recon(Ps, args, int(bestd[i, j]), i, j), 'X', wit, awit)
    if not r: continue
    m1, dE1, mv1, J1 = r; tried += 1
    if dE1 > 1e-6: found = (m1, dE1, mv1); break
    cl2 = closures(m1, X, -1e-6); sec_rel[len(cl2) > 0] += 1
    for c2 in cl2[:200]:
        tot2, _, r02, i2, j2 = c2
        if tot2 + dE1 <= 1e-6 and m1.free(X) == 0: continue
        r2 = try_apply(m1, X, r02, recon(Ps, args, int(bestd[i2, j2]), i2, j2), 'X', wit, awit)
        if r2: sec_exact += 1
        if r2 and dE1 + r2[1] > 1e-6: found = (r2[0], dE1 + r2[1], mv1 + r2[2]); break
        if r2: r2[3].undo()
    if not found: J1.undo()
    if found or tried > 40000: break
print('first cycles applied', tried, 'X with relaxed 2nd closures', dict(sec_rel), 'exact 2nd cycles', sec_exact)
print('exact stage1 cycles tried', tried)
if found:
    mm, dE, moves = found; roles = lib.compact(mm.roles); au = lib.audit(roles); pr = lib.price(au['profile'])
    print('FOUND dE', dE, 'moves', moves, 'idle', au['idle'], 'kappa', pr['kappa_decimal'])
    open(outp + '.OWNERS.json.gz', 'wb').write(gzip.compress(json.dumps(roles).encode(), mtime=0))
else: print('NONE')
