#!/usr/bin/env python3
"""Step 1 of the Lambda direction: which climbs of #4610 are forced by the endpoints of contact partners?

Replay the forward program of research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz, tracking every field's
frame.  For every field f with climb chain S=F_0 < F_1 < ... < F_k = T, an intermediate frame F_i is REMOVABLE
(necessary condition only) if every scalar contact f has while sitting at F_i could be done either
  (defer)   at the next frame F_{i+1}: partner g must be able to reach F_{i+1}, i.e. T_g >= F_{i+1}, or
  (advance) at the previous frame F_{i-1}: partner must be able to sit there, i.e. S_g <= F_{i-1} <= T_g.
Otherwise the frame is FORCED by the partners' endpoints: with these operations and these endpoints, no retiming
or frame reassignment removes it.  k_min(f) = 1 + #forced intermediate frames is a lower bound on the number of
climbs of f, and with total rank R_f fixed, Lambda_f >= (R_f-k+1)^t + (k-1) - R_f^t (concavity).
Stdlib only, seconds.  Writes forced_result.json and progress.log.
"""
import json, gzip, collections, math, os, time
W3 = 'D:/Math/imb-docking/research/kappa-round3-warp-20261022/'
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, 'progress.log'), 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s); LOG.write(s + '\n'); LOG.flush()

w = json.loads(gzip.decompress(open(W3 + 'ACTUAL-WORD.json.gz', 'rb').read()))
c = w['canonical']; frames = c['frames']; nf = len(c['start'])
def span(fi):
    """F2-span of frame fi as a frozenset of ints (9-bit vectors)."""
    vs = frames[fi]; s = {0}
    for v in vs: s |= {x ^ v for x in s}
    return frozenset(s)
SP = {}
def sp(fi):
    if fi not in SP: SP[fi] = span(fi)
    return SP[fi]
def leq(a, b): return sp(a) <= sp(b)
S = list(c['start']); T = list(c['final'])
R = [len(frames[T[f]]) - len(frames[S[f]]) for f in range(nf)]
H = {int(k): n for k, n in json.load(open(W3 + 'ARITHMETIC.json'))['local_helpers'].items()}
nh = sum(H.values()); nm = nf - nh
log(f'fields {nf}: mains {nm} (R=8), helpers {nh}; final dims {collections.Counter(len(frames[t]) for t in T)}')

# replay: chain of frames per field, contacts per (field, frame)
cur = list(S); chain = [[S[f]] for f in range(nf)]
contacts = collections.defaultdict(list)   # (f, frame) -> list of partner fields
nscal = 0; bad = 0
for e in w['programs']['forward']:
    if e[0] == 'climb':
        f, a, b = e[2], e[3], e[4]; assert cur[f] == a; cur[f] = b; chain[f].append(b)
    elif e[0] == 'warp':
        f = e[1][1]; assert cur[f] == e[3]; cur[f] = e[4]
        if e[4] != e[3]: chain[f].append(e[4])     # same dimension, different frame: a new level for contacts
    elif e[0] == 'scalar':
        op = e[1]; F = e[2]
        roles = [r for r in op[1:] if isinstance(r, list) and r[0] == 'L']
        if op[0] in ('add', 'copy') and len(roles) == 2:
            d, s = roles[0][1], roles[1][1]
            if cur[d] != F or cur[s] != F: bad += 1
            contacts[(d, cur[d])].append(s); contacts[(s, cur[s])].append(d); nscal += 1
assert cur == T
log(f'two-field scalar contacts {nscal}; contacts not at the recorded common frame {bad}')

# per-field analysis
t = 1 - 0.0030217759
def pw(x): return 0.0 if x == 0 else math.exp(t * math.log(x))
tot_forced = 0; lam_lb = 0.0; lam_real = 0.0; per = []
forced_by = collections.Counter(); hist_k = collections.Counter(); hist_kmin = collections.Counter()
for f in range(nf):
    ch = chain[f]
    # climbs = strictly increasing dimension steps (warps keep dimension)
    climbs = [len(frames[ch[i+1]]) - len(frames[ch[i]]) for i in range(len(ch) - 1) if len(frames[ch[i+1]]) > len(frames[ch[i]])]
    lam_real += sum(pw(x) for x in climbs) - pw(R[f])
    forced = 0
    for i in range(1, len(ch) - 1):
        Fi = ch[i]
        if len(frames[Fi]) in (len(frames[ch[0]]), len(frames[ch[-1]])) and False: pass
        prev, nxt = ch[i-1], ch[i+1]
        partners = contacts.get((f, Fi), [])
        if not partners: continue          # no contact here: the level is free to drop
        ok = True; why = None
        for g in partners:
            defer = leq(nxt, T[g])
            adv = leq(S[g], prev) and leq(prev, T[g])
            if not (defer or adv):
                ok = False; why = ('helper' if g >= nm else 'main', len(frames[T[g]])); break
        if not ok:
            forced += 1; forced_by[why] += 1
    k = len(climbs); kmin = 1 + forced
    hist_k[k] += 1; hist_kmin[kmin] += 1
    tot_forced += forced
    lb = (pw(R[f] - kmin + 1) + (kmin - 1) - pw(R[f])) if R[f] >= kmin else (pw(R[f]) - pw(R[f]))
    lam_lb += lb
    per.append({'f': f, 'kind': 'main' if f < nm else 'helper', 'R': R[f], 'climbs': k, 'kmin': kmin, 'levels': len(ch)})
log(f'Lambda(real, t=1-kappa4610) = {lam_real:.4f}  (package: 23.8626 at its own root)')
log(f'forced intermediate frames: {tot_forced} of {sum(len(ch)-2 for ch in chain)} intermediate levels; by partner kind/final dim: {dict(forced_by)}')
log(f'climbs per field histogram (real): {dict(sorted(hist_k.items()))}')
log(f'k_min per field histogram (forced): {dict(sorted(hist_kmin.items()))}')
log(f'Lambda lower bound from forced frames (concavity): {lam_lb:.4f}  vs real {lam_real:.4f}')
mains = [p for p in per if p['kind'] == 'main']; helps = [p for p in per if p['kind'] == 'helper']
log(f"mains: mean climbs {sum(p['climbs'] for p in mains)/nm:.2f}, mean kmin {sum(p['kmin'] for p in mains)/nm:.2f}; helpers: mean climbs {sum(p['climbs'] for p in helps)/nh:.2f}, mean kmin {sum(p['kmin'] for p in helps)/nh:.2f}")
# contact census by frame dimension
dimc = collections.Counter(len(frames[F]) for (f, F), ps in contacts.items() for _ in ps)
log(f'contact endpoints by frame dimension: {dict(sorted(dimc.items()))}')
json.dump({'lambda_real': lam_real, 'lambda_lb_forced': lam_lb, 'forced': tot_forced, 'forced_by': {str(k): v for k, v in forced_by.items()},
           'hist_climbs': dict(hist_k), 'hist_kmin': dict(hist_kmin), 'per_field': per}, open(os.path.join(HERE, 'forced_result.json'), 'w'))
log('done forced_climbs')
