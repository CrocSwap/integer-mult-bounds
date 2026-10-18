"""F1 (fragmentation at the shipped op order). Inputs: the ck / jp8 CANONICAL words of the #622/#623 K-triangle
providers (vendored from the #656 audit copy).  Port of cards B80 gap.py/slack.py/upr.py and B11 upper.py."""
import math
from collections import Counter, defaultdict
from common import *

def basis(vs):
    b = {}
    for x in vs:
        for p in sorted(b, reverse=True):
            if x >> p & 1: x ^= b[p]
        if x:
            p = x.bit_length() - 1
            for q in b:
                if b[q] >> p & 1: b[q] ^= x
            b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))
def spanset(B):
    s = {0}
    for b in B: s |= {x ^ b for x in s}
    return frozenset(s)
dim = lambda s: len(s).bit_length() - 1
psi = lambda r: r * math.log(73 / r) if r > 0 else 0
def rank(vs):
    b = []
    for x in vs:
        for y in b: x = min(x, x ^ y)
        if x: b.append(x)
    return len(b)
def upper(d, ss):
    curU = [ss[f] for f in d['final']]; F = {}
    def rev(part):
        for i in range(len(d[part]) - 1, -1, -1):
            e = d[part][i]; regs = [e[1]] + ([e[2]] if e[0] == 'add' else [])
            U = curU[regs[0]]
            for r in regs[1:]: U = U & curU[r]
            F[part, i] = U
            for r in regs: curU[r] = U
    rev('tail'); rev('B')
    for k, r in enumerate(d['centers']): curU[r] = ss[d['center_frames'][k]]
    v = d['v']
    for t in range(v): curU[v + t] = ss[d.get('target_levels', {}).get(str(t), 0)]
    rev('A')
    return F
viol = [0]
def per_class(d, ss, F, cl):
    cur = [ss[f] for f in d['start']]; tot = defaultdict(float)
    def climb(r, s):
        if cur[r] == s: return
        if not cur[r] <= s: viol[0] += 1
        tot[cl(r)] += psi(dim(s) - dim(cur[r])); cur[r] = s
    for part in ('A', 'B', 'tail'):
        for i, e in enumerate(d[part]):
            for r in [e[1]] + ([e[2]] if e[0] == 'add' else []): climb(r, F[part, i])
    for r, f in enumerate(d['final']): climb(r, ss[f])
    return tot

for prov, name in (('ck', 'pr656-k492audit-pr622-ck-CANONICAL-WORD.json.gz'), ('jp8', 'pr656-k492audit-pr622-jp8-CANONICAL-WORD.json.gz')):
    d = jgz(name); v = d['v']; C = set(d['centers']); ports = d['ports']
    cl = lambda r: 'S' if r < v else 'T' if r < 2 * v else 'C' if r in C else 'H'
    ss = [spanset(f) for f in d['frames']]
    F0 = {(p, i): ss[e[-1]] for p in ('A', 'B', 'tail') for i, e in enumerate(d[p])}
    FU = upper(d, ss)
    check(f'f1.{prov}.shipped-frames-below-ceiling', all(F0[k] <= FU[k] for k in F0))
    tb = [k for k in F0 if any(cl(r) == 'T' for r in ([d[k[0]][k[1]][1]] + ([d[k[0]][k[1]][2]] if d[k[0]][k[1]][0] == 'add' else [])))]
    atU = sum(1 for k in tb if F0[k] == FU[k])
    sl = Counter(dim(FU[k]) - dim(F0[k]) for k in tb)
    check(f'f1.{prov}.target-ops-1096-950-at-legal-ceiling', (len(tb), atU, dict(sl)) == (1096, 950, {0: 950, 1: 146}), f'{len(tb)} target ops, {atU} at ceiling, slack {dict(sl)}')
    t0 = per_class(d, ss, F0, cl)
    F2 = dict(F0)
    for k in tb: F2[k] = FU[k]
    viol[0] = 0; t2 = per_class(d, ss, F2, cl); nv = viol[0]
    print('   non-monotone climbs in target-only raise:', nv)
    net = sum(t2.values()) - sum(t0.values())
    check(f'f1.{prov}.target-only-raise-is-not-a-legal-assignment', nv == 50 if prov == 'ck' else nv > 0, f'{nv} non-monotone climbs')
    tU = per_class(d, ss, FU, cl); viol[0] = 0
    check(f'f1.{prov}.legal-all-ops-at-ceiling-costs-more', sum(tU.values()) - sum(t0.values()) > 400, f'delta psi/call {sum(tU.values())-sum(t0.values()):+.1f}')
    check(f'f1.{prov}.target-only-raise-model-delta', abs(net + 5.6) < 0.1, f'model delta psi/call {net:+.2f} on the NON-legal target-only raise (indicative only) (T {t2["T"]-t0["T"]:+.2f}, H {t2["H"]-t0["H"]:+.2f}, S {t2["S"]-t0["S"]:+.2f}); far below the 65 psi GO line')
    frag = sum(psi(x) for x in [0]) # placeholder keeps style
    if prov == 'ck':
        # direct-port ceiling c(o) = 9 - rank(ports of o's unserved target readers), same reader order
        ev = [(p, i, e) for p in ('A', 'B') for i, e in enumerate(d[p])]
        isT = lambda r: v <= r < 2 * v
        reads = defaultdict(list); tops = defaultdict(list)
        for tm, (p, i, e) in enumerate(ev):
            if e[0] != 'add': continue
            a, b = e[1], e[2]; f = len(d['frames'][e[-1]])
            if isT(a) and not isT(b): tops[a].append([tm, b, f, None]); reads[b].append((tm, a))
            elif isT(b) and not isT(a): tops[b].append([tm, a, f, None]); reads[a].append((tm, b))
            elif isT(a) and isT(b): tops[a].append([tm, b, f, b]); tops[b].append([tm, a, f, a])
        cap = {}
        for o, lst in reads.items():
            for k, (tm, t) in enumerate(lst): cap[t, tm] = 9 - rank([ports[x - v] for _, x in lst[k:]])
        save = 0; nviol = 0
        def steps(ds):
            out = []; cur = 0
            for x in ds + [8]:
                if x > cur: out.append(x - cur); cur = x
            return out
        shipped_frag = 0
        for t, L in tops.items():
            L.sort(); caps = []
            for tm, o, f, ot in L:
                c = 9 - rank([ports[t - v], ports[ot - v]]) if ot is not None else cap[t, tm]
                c = min(c, 8); caps.append(c); nviol += f > c
            sm = caps[:]
            for j in range(len(sm) - 2, -1, -1): sm[j] = min(sm[j], sm[j + 1])
            sh = steps([x[2] for x in L]); idl = steps(sm)
            save += sum(psi(s) for s in sh) - sum(psi(s) for s in idl); shipped_frag += sum(psi(s) for s in sh)
        check('f1.ck.loose-port-cap-bound-614-psi-per-call', round(save) == 614 and nviol == 0,
              f'slack {save:.1f} psi/call (fixed reader order, {nviol} violations); LOOSE: ignores every constraint on the operand other than the port cap')
        check('f1.ck.target-fragmentation-1342-psi-per-call', round(shipped_frag - 112 * psi(8)) == 1342, f'{shipped_frag - 112 * psi(8):.1f}')
done()
