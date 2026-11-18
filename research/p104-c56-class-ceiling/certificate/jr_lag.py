# JS-RANK jr_lag: separable lower bound on min |J| in the C=56 flag model, per config.
# Valid inequality per even cell c with chain set K(c): if chain k lies in NO zero-sum subset of {prod_k(c)}, killing c needs k
# to avoid c, so junk_c >= live_k(c). Average over the m(c) mandatory chains: junk_c >= (1/m) sum_{k mandatory} live_k(c).
# Single-chain cells: m = 1 (F1). Then LB = sum_k min_flag sum_c w_kc [tau_k(t) > sigma_k(s)], exact DP over complete flags
# <z'> .. z^perp (same lattice DP as F1/W2 flagdp, re-implemented with Fraction weights). Own code.
import sys, os
sys.argv_ = sys.argv; sys.argv = ['x']; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jr_c56.py')).read().split("if __name__")[0]); sys.argv = sys.argv_
def red(B, v):
    for b in B: v = min(v, v ^ b)
    return v
def canon(B):
    out = []
    for v in B:
        v = red(out, v)
        if v: out = [min(b, b ^ v) for b in out] + [v]
    out = [red([x for x in out if x != b], b) for b in out]
    return tuple(sorted(out, reverse=True))
def flagmin(z, zp, W):            # W: dict (t,s) -> weight >= 0 ; min over complete flags of sum W[t,s] [tau(t) > sigma(s)]
    bys = {}
    for (t, s), w in W.items(): bys.setdefault(s, []).append((t, w))
    zperp = [v for v in range(512) if not dot(v, z)]; info = {}
    def masks(B):
        ps = [s for s in bys if all(not dot(b, Q[s]) for b in B)]
        ni = {t for t in range(n) if red(sorted(B, reverse=True), Q[t])}
        return set(ps), ni
    layer = {canon([zp]): Fr(0)}
    for dd in range(1, 8):
        nxt = {}
        for B, c in layer.items():
            if B not in info: info[B] = masks(B)
            ps, ni = info[B]; seen = set()
            for v in zperp:
                r = red(list(B), v)
                if r == 0 or r in seen: continue
                seen.add(r); B2 = canon(list(B) + [r])
                if B2 not in info: info[B2] = masks(B2)
                cost = sum(w for s in ps - info[B2][0] for (t, w) in bys[s] if t in ni)
                if B2 not in nxt or c + cost < nxt[B2]: nxt[B2] = c + cost
        layer = nxt
    (Bf, cmin), = layer.items()
    ps, ni = masks(Bf)                 # symbols still legal at z^perp: sigma = 7; t with tau > 7 never (t in z^perp when w_t != 0)
    return cmin
ci = int(sys.argv[1]); ch = chains(ci)
W = [dict() for _ in range(8)]
for t in range(n):
    for s in range(n):
        if t == s or dot(Q[t], Q[s]): continue
        ks = [k for k in range(8) if prodk(ch, k, t, s)]; vals = [prodk(ch, k, t, s) for k in ks]
        inzero = set()
        for m in range(1, 1 << len(ks)):
            if sum(v for i, v in enumerate(vals) if m >> i & 1) == 0: inzero |= {ks[i] for i in range(len(ks)) if m >> i & 1}
        mand = [k for k in ks if k not in inzero]
        for k in mand: W[k][t, s] = Fr(1, len(mand))
tot = Fr(0)
for k in range(8):
    z, zp, w, u, g = ch[k]; m = flagmin(z, zp, W[k]); tot += m
    print('cfg', ci, 'chain', k, 'cells', len(W[k]), 'weight', float(sum(W[k].values())), 'min', m, flush=True)
print('cfg', ci, 'SEPARABLE LB', tot, float(tot))
