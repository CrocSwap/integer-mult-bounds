"""ARF descent.py (own code): falsification. Annealed heat-bath descent over exact validity-preserving Gibbs port
resamples (tau48/gibbs.py resample). Objective 'C' (decoder cost) or 'rho' (rho_A+rho_B, GF(2^16) rank).
Flags any valid decoder with C < 56 or certified (Rado ub) rho_A+rho_B < 56. Logs tau-rank stats at Rado-exact points.
usage: descent.py MODE SEED MINUTES"""
import sys, os, time, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tau48'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tau48'))
ARGS = sys.argv[1:]; sys.argv = sys.argv[:1]
from gibbs import *
mode = ARGS[0]; seed = int(ARGS[1]); minutes = float(ARGS[2])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
rng = np.random.default_rng(seed)
def start(kind, extra):
    if kind == 'e8':
        W = np.load('../orbitlp/e8W.npy') % 4; V = np.load('../orbitlp/e8V.npy') % 4
        W = np.concatenate([W, np.zeros((n, extra), np.int64)], 1); V = np.concatenate([V, np.zeros((n, extra), np.int64)], 1)
        return W, V
    W0 = Cc % 4; V0 = (Cc @ Gb) % 4; m = extra
    while True:
        Xm = rng.integers(0, 4, (8, m)); Pi = inv4(Xm[:, :8])
        if Pi is not None: break
    Ym = np.zeros((8, m), dtype=np.int64); Ym[:, :8] = Pi.T
    return (W0 @ Xm) % 4, (V0 @ Ym) % 4
def fval(W, V):
    RB = spaces_B(W, V, Q); RA = spaces_A(W, V, Q)
    U = f2basis([x for t in range(n) for x in RA[t]]); Vv = f2basis([x for t in range(n) for x in RB[t]])
    bt = lambda x: np.array([(x >> (n - 1 - s)) & 1 for s in range(n)])
    MU = np.array([bt(x) for x in U]); MV = np.array([bt(x) for x in Vv])
    return len(U) + len(Vv) - (rk(MU @ MV.T) if len(U) and len(Vv) else 0)
def obj(W, V):
    if mode == 'C': return cost(W, V, Q)
    if mode == 'f': return fval(W, V)
    return trank(spaces_A(W, V, Q), n, 1) + trank(spaces_B(W, V, Q), n, 1)
starts = [('e8', 4), ('rf', 12), ('e8', 8), ('rf', 16), ('e8', 2), ('rf', 10)]
t0 = time.time(); per = minutes * 60 / len(starts)
taus = []; glob_best = 10**9
for si, (kind, extra) in enumerate(starts):
    W, V = start(kind, extra); assert check(W, V)
    cur = obj(W, V); best = cur; bW, bV = W.copy(), V.copy(); ts = time.time(); step = 0
    print('START', kind, extra, 'obj', cur, 'C', cost(W, V, Q), flush=True)
    while time.time() - ts < per:
        frac = (time.time() - ts) / per; T = 2.0 * (1 - frac) + 0.15
        t = int(rng.integers(n)); side = 'W' if rng.random() < 0.5 else 'V'
        cands = [(W, V, cur)]
        for _ in range(4):
            W2, V2 = resample(W, V, t, rng, side); cands.append((W2, V2, obj(W2, V2)))
        vals = np.array([c[2] for c in cands], float); p = np.exp(-(vals - vals.min()) / T); p /= p.sum()
        W, V, cur = cands[int(rng.choice(len(cands), p=p))]
        step += 1
        if cur < best:
            best = cur; bW, bV = W.copy(), V.copy()
        if step % 2000 == 0:
            tr, ex, rs = report(W, V, '%s%d step%d T%.2f' % (kind, extra, step, T))
            if ex: taus.append(tr)
    assert check(bW, bV)
    tr, ex, rs = report(bW, bV, 'BEST %s%d obj %d' % (kind, extra, best))
    if ex: taus.append(tr)
    Cb = cost(bW, bV, Q); glob_best = min(glob_best, best if mode == 'f' else (Cb if mode == 'C' else rs))
    if mode == 'f': print('f', fval(bW, bV), flush=True)
    if mode == 'f' and fval(bW, bV) < 56: print('!!!!! f < 56 (J=all tau-rank > 48)', flush=True)
    np.save(OUT + 'best_%s_%d_%s%d_W.npy' % (mode, seed, kind, extra), bW); np.save(OUT + 'best_%s_%d_%s%d_V.npy' % (mode, seed, kind, extra), bV)
    if Cb < 56: print('!!!!! C < 56 VALID DECODER FOUND', Cb, flush=True)
    if mode == 'rho':
        vb, _ = rado_ub(spaces_B(bW, bV, Q), n); va, _ = rado_ub(spaces_A(bW, bV, Q), n)
        print('rado ub', va, vb, 'sum', va + vb, flush=True)
        if va + vb < 56: print('!!!!! CERTIFIED rho_A+rho_B < 56', flush=True)
print('DONE mode', mode, 'global best', glob_best, 'tau-rank at Rado-exact points: n', len(taus), 'max', max(taus) if taus else None,
      'hist', {v: taus.count(v) for v in sorted(set(taus))}, flush=True)
