"""CHAINBOUND needs.py (own code; replay adapted from our HOSTLP imp.py).
Per frame G of #7615 with the fixed registers (mains + owned) and their events fixed:
  V_G = pi-projected contents of fixed registers at every fixed event at G (arrival, departure, read by a fixed reg,
        CLEAR, final residency, initial residency)       R_G = rank V_G  (mod 2^31-1)
  n_G = # fixed arrivals into G that can carry content in SOME helper layer (initial residents + every fixed MOVE in;
        INIT arrivals are exactly zero and are not counted)
  m_G = # fixed departures out of G (every fixed MOVE out + every CLEAR + every final resident)
  in_G  = R_G - n_G   (pass-through helpers needed to bring content in)
  out_G = R_G - m_G   (pass-through helpers needed to take content out)
  B_G = max(0, in_G, out_G).
Also the #7615 interior helper stops per frame (soundness check)."""
import gzip, json, collections, pickle, sys
from fractions import Fraction
import flint
PR = 2147483647
def fr(s):
    f = Fraction(s); return (f.numerator % PR) * pow(f.denominator % PR, PR - 2, PR) % PR
W = json.load(gzip.open('../../ATTACK/COURIER226/hit_c226_1.json.gz'))
F = W['frames']; NP = W['public']; NO = W['owned_fields']; live = W['live']; H = W['hosted']
mains = set(live) | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
fixed = lambda r: r >= NP or r in mains
hel = [r for r in range(NP) if not fixed(r)]; hset = set(hel)
keep = [r for r in range(NP) if r not in hset]; col = {r: i for i, r in enumerate(keep)}; NC = len(keep)
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
FS = [span(b) for b in F]
FK = {}; KEYS = []          # canonical frame id per span
for i, s in enumerate(FS):
    if s not in FK: FK[s] = len(KEYS); KEYS.append(s)
fid = [FK[s] for s in FS]
dimk = [len(F[KEYS.index(s)]) if False else None for s in KEYS]
for i, s in enumerate(FS): dimk[fid[i]] = len(F[i])
N = NP + NO
row = [{r: 1} if r < NP else {} for r in range(N)]
cur = list(W['initial']) + [None] * NO
def vec(r):
    return {col[k]: c for k, c in row[r].items() if k in col}
V = collections.defaultdict(list); n = collections.Counter(); m = collections.Counter()
for r in range(NP):
    if fixed(r): V[fid[cur[r]]].append(vec(r)); n[fid[cur[r]]] += 1
def addto(d, src, c):
    for k, v in src.items():
        nv = (d.get(k, 0) + c * v) % PR
        if nv: d[k] = nv
        else: d.pop(k, None)
for i, e in enumerate(W['program']):
    op, r = e[0], e[1]
    if op == 'MOVE':
        if fixed(r):
            a, b = fid[e[2]], fid[e[3]]
            v = vec(r); V[a].append(v); V[b].append(v); m[a] += 1; n[b] += 1
        cur[r] = e[3]; continue
    if op == 'INIT': row[r] = {}; cur[r] = e[2]; continue
    if op == 'CLEAR': V[fid[e[2]]].append(vec(r)); m[fid[e[2]]] += 1; row[r] = {}; cur[r] = None; continue
    if op == 'SCALE':
        q = fr(e[2]); row[r] = {k: v * q % PR for k, v in row[r].items()}; continue
    s = e[2]; c = fr(e[3]); f = fid[e[4]]
    if fixed(s) and fixed(r): V[f].append(vec(s)); V[f].append(vec(r))  # contents at a fixed event (before)
    if op == 'COPY': row[r] = {}
    addto(row[r], row[s], c)
    if fixed(s) and fixed(r): V[f].append(vec(r))                       # and after
for r in range(NP):
    if fixed(r): V[fid[cur[r]]].append(vec(r)); m[fid[cur[r]]] += 1
def rank(vs):
    vs = [v for v in vs if v]
    if not vs: return 0
    M = flint.nmod_mat(len(vs), NC, PR)
    for i, v in enumerate(vs):
        for j, c in v.items(): M[i, j] = c
    return M.rank()
# #7615 helper chains (frame ids) and interior stops
chain = {h: [fid[W['initial'][h]]] for h in hel}
for e in W['program']:
    if e[0] == 'MOVE' and e[1] in chain: chain[e[1]].append(fid[e[3]])
P = collections.Counter()
for h, ch in chain.items():
    for x in ch[1:-1]: P[x] += 1
out = {}
for G in set(V) | set(P):
    R = rank(V[G]); B = max(0, R - n[G], R - m[G])
    out[G] = dict(dim=dimk[G], R=R, n=n[G], m=m[G], inn=R - n[G], out=R - m[G], B=B, P=P[G])
tot = lambda k: sum(max(0, o[k]) for o in out.values())
import math
print('frames', len(out), 'sum in+', tot('inn'), 'sum out+', tot('out'), 'sum B', tot('B'))
print('floor 2ln2*sumB = %.4f' % (2 * math.log(2) * tot('B')))
viol = [(G, o) for G, o in out.items() if o['P'] < o['B']]
print('violations on #7615', len(viol), viol[:5])
print('B by dim', sorted(collections.Counter({o['dim']: 0 for o in out.values()}).items()) and
      sorted((d, sum(o['B'] for o in out.values() if o['dim'] == d)) for d in range(10)))
print('frames out>in', sum(1 for o in out.values() if o['out'] > max(0, o['inn'])))
pickle.dump(dict(out=out, keys=[sorted(k) for k in KEYS], dimk=dimk, chain=chain,
                 ends={h: (dimk[ch[0]], dimk[ch[-1]]) for h, ch in chain.items()}), open('needs.pkl', 'wb'))
