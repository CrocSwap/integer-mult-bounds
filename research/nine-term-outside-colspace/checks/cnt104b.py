# MASK9 counting data for case (b): rank lower bounds lb(X) = 8 - min_E |S_E(X)| (IDEAL3 Lemma 1.1 propagation, any rank-8 realisation)
# for X = C(W) ∩ C(W'), W, W' 2-dim label subspaces (C(W) = union of the classes O_c, c in W\0).
# P104 variant (cnt104b.py): orbits_P104.pkl from aut104.py; frame-containment prefilter (a frame inside X certifies X) before propagation.
# usage: cnt.py UNIT   -> writes cnt_UNIT.pkl {surv, sizes, orb2 (orbit reps of 2-dim subspaces), lb22[(rep, W')]}
import sys, os, pickle, time, random, numpy as np
from setup9 import *
unit = sys.argv[1]
L, v, G, frames, nbar, h, basis, cls = load(unit)
full = (1 << v) - 1
FR = np.array([[F >> t & 1 for t in range(v)] for F in frames], dtype=np.float32)
NB = np.array([[nbar[t] >> s & 1 for s in range(v)] for t in range(v)], dtype=np.float32)
def tobits(x): return np.array([x >> t & 1 for t in range(v)], dtype=bool)
def minS(Xs):  # Xs: B x v bool -> min_E |S_E| after propagation (0 = certified spanning)
    S = FR[None, :, :] * (~Xs)[:, None, :]
    while True:
        Wg = ((S @ NB) > 0).all(axis=1)
        S2 = S * Wg[:, None, :]
        if np.array_equal(S2, S): break
        S = S2
    return S.sum(axis=2).min(axis=1).astype(int)
random.seed(1); ks = sorted(cls)
smp = [random.getrandbits(v) & random.getrandbits(v) | random.getrandbits(v) & random.getrandbits(v) for _ in range(60)] + [cls[random.choice(ks)] & cls[random.choice(ks)] for _ in range(60)]
ref = [min(pc(s) for s in propagate(x, frames, nbar, v)) for x in smp]
got = minS(np.array([tobits(x) for x in smp]))
assert list(got) == ref, 'numpy minS disagrees with cert2.propagate'
print('validation ok', flush=True)
lb1 = minS(np.array([tobits(cls[c]) for c in ks]))
surv = {c for c, m in zip(ks, lb1) if m > 0}
print('uncertified single classes', len(surv), 'sizes', sorted(pc(cls[c]) for c in surv), flush=True)
# 2-dim subspaces (exclude any containing the all-lines class? keep all; flag)
sub2 = sorted({tuple(sorted((a, b, a ^ b))) for a in ks for b in ks if a < b})
print('2-dim subspaces', len(sub2), flush=True)
def C(W):
    x = 0
    for c in W: x |= cls[c]
    return x
sizes = {}
for W in sub2: sizes[pc(C(W))] = sizes.get(pc(C(W)), 0) + 1
print('|C(W)| dim2 distribution', sorted(sizes.items()), flush=True)
D = pickle.load(open(f'orbits_{unit}.pkl', 'rb'))
inv = {cls[c]: c for c in cls}
def img(O, p):
    r = 0
    for t in range(v):
        if O >> t & 1: r |= 1 << p[t]
    return r
cperm = [{c: inv[img(cls[c], p)] for c in ks} for p in D['perms']]
seen = {}; orb2 = []
for W in sub2:
    if W in seen: continue
    seen[W] = len(orb2); orb = [W]; st = [W]
    while st:
        x = st.pop()
        for cp in cperm:
            y = tuple(sorted(cp[c] for c in x))
            if y not in seen: seen[y] = len(orb2); orb.append(y); st.append(y)
    orb2.append(orb)
print('2-dim orbits', len(orb2), [(len(o), pc(C(o[0])), sum(c in surv for c in o[0])) for o in orb2], flush=True)
useful = [W for W in sub2 if any(c not in surv for c in W) and C(W) != full]
CB = np.array([tobits(C(W)) for W in useful], dtype=np.float32)
FinC = ((CB @ FR.T) == 8).astype(np.float32)
lb22 = {}; t0 = time.time(); BS = 512; uidx = {W: i for i, W in enumerate(useful)}
ONLY = os.environ.get('ONLY_ORBITS')   # (added for the package) comma list of orbit indices: subset replay; unset = full census
for oi, o in enumerate(orb2):
    if ONLY is not None and str(oi) not in ONLY.split(','): continue
    R = o[0]
    if all(c in surv for c in R) or C(R) == full: continue
    hit = (FinC @ FinC[uidx[R]]) > 0
    rest = [useful[i] for i in np.nonzero(~hit)[0]]
    cnt = {8: int(hit.sum())}
    for i in range(0, len(rest), BS):
        J = rest[i:i + BS]
        m = minS(np.array([tobits(C(R) & C(W)) for W in J]))
        for W, x in zip(J, m):
            if 8 - int(x) <= 7: lb22[R, W] = 8 - int(x)
            cnt[8 - int(x)] = cnt.get(8 - int(x), 0) + 1
    print('orbit', oi, 'rep', R, '|C|', pc(C(R)), 'prefilter left', len(rest), 'lb counts', sorted(cnt.items()), round(time.time() - t0), flush=True)
    pickle.dump({'surv': surv, 'orb2': orb2, 'lb22': lb22}, open(f'cnt_{unit}.pkl', 'wb'))
print('DONE', round(time.time() - t0), flush=True)
