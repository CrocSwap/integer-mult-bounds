#!/usr/bin/env python3
"""Step 1b: exact-frame version.  A contact of f at its i-th frame F_i can move only to a frame that the partner's
chain also contains EXACTLY (an ADD needs one common frame).  F_i is removable (necessary condition) iff every
partner's chain contains F_{i+1}(f) (defer) or F_{i-1}(f) (advance).  Otherwise the partners' chains diverge at
F_i and the level is forced for this operation set, whatever the order and timing.  Also: a 'strict' variant that
demands ALL partners of the level agree on the same direction (all defer or all advance)."""
import json, gzip, collections, math, os, time
W3 = 'D:/Math/imb-docking/research/kappa-round3-warp-20261022/'
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, 'progress.log'), 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s); LOG.write(s + '\n'); LOG.flush()
w = json.loads(gzip.decompress(open(W3 + 'ACTUAL-WORD.json.gz', 'rb').read()))
c = w['canonical']; frames = c['frames']; nf = len(c['start']); S = list(c['start']); T = list(c['final'])
R = [len(frames[T[f]]) - len(frames[S[f]]) for f in range(nf)]
nm = 224
cur = list(S); chain = [[S[f]] for f in range(nf)]; contacts = collections.defaultdict(list)
for e in w['programs']['forward']:
    if e[0] == 'climb': f = e[2]; cur[f] = e[4]; chain[f].append(e[4])
    elif e[0] == 'warp':
        f = e[1][1]; cur[f] = e[4]
        if e[4] != e[3]: chain[f].append(e[4])
    elif e[0] == 'scalar':
        op = e[1]; roles = [r for r in op[1:] if isinstance(r, list) and r[0] == 'L']
        if op[0] in ('add', 'copy') and len(roles) == 2:
            d, s = roles[0][1], roles[1][1]; contacts[(d, cur[d])].append(s); contacts[(s, cur[s])].append(d)
chainset = [set(ch) for ch in chain]
t = 1 - 0.0030217759
def pw(x): return 0.0 if x == 0 else math.exp(t * math.log(x))
res = {}
for mode in ('any', 'strict'):
    forced_tot = 0; lam_lb = 0.0; hist = collections.Counter(); forced_dim = collections.Counter(); lv_tot = 0
    for f in range(nf):
        ch = chain[f]; forced = 0
        for i in range(1, len(ch) - 1):
            ps = contacts.get((f, ch[i]), [])
            if not ps: continue
            lv_tot += 1
            defer = [ch[i+1] in chainset[g] for g in ps]; adv = [ch[i-1] in chainset[g] for g in ps]
            if mode == 'any': ok = all(dd or aa for dd, aa in zip(defer, adv))
            else: ok = all(defer) or all(adv)
            if not ok: forced += 1; forced_dim[len(frames[ch[i]])] += 1
        kmin = 1 + forced; hist[kmin] += 1; forced_tot += forced
        lam_lb += (pw(R[f] - kmin + 1) + (kmin - 1) - pw(R[f])) if R[f] >= kmin else 0.0
    log(f'[{mode}] forced levels {forced_tot} of {lv_tot} contact levels; k_min histogram {dict(sorted(hist.items()))}; by dim {dict(sorted(forced_dim.items()))}; Lambda_lb = {lam_lb:.4f} (real 23.8626)')
    res[mode] = {'forced': forced_tot, 'levels': lv_tot, 'hist_kmin': dict(hist), 'lambda_lb': lam_lb}
# how do partner chains diverge: at a contact level F of f, how many distinct NEXT frames do the partners take?
div = collections.Counter()
nxt = {}
for f in range(nf):
    ch = chain[f]
    for i in range(len(ch) - 1): nxt[(f, ch[i])] = ch[i+1]
for (f, F), ps in contacts.items():
    nx = {nxt.get((g, F)) for g in ps if (g, F) in nxt}
    div[len(nx)] += 1
log(f'distinct next frames among the partners of a (field, level): {dict(sorted(div.items()))}')
json.dump(res, open(os.path.join(HERE, 'forced_exact_result.json'), 'w'), indent=1)
