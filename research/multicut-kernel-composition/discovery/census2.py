"""Multi-cut twin/triple census excluding already-used helpers. usage: census2.py DATA USED.json OUT.json"""
import json, sys, collections, time, itertools, math
from array import array
from fractions import Fraction as Fr
from math import lcm, gcd
D, USED, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CUTS = [676559, 678000, 680080, 685000, 690000, 695000, 700582, 705000, 710000, 715000, 720000, 727593]
TRIPLE_CUTS = {676559, 690000, 700582, 727593}
t0 = time.time()
st = json.load(open(D + '/249-states.json')); n, v, ZERO, FULL = st['n'], st['v'], st['ZERO'], st['FULL']; H0 = 2*v
ini = [ZERO]*n; fin = [FULL]*n
for k, x in st['initial'].items(): ini[int(k)] = x
for k, x in st['final'].items(): fin[int(k)] = x
regs = st['regs']; borrowed = set(st['borrowed']); donor = set(json.load(open(D + '/249-DONOR-OWNERSHIP.json'))['donor_keys']); used = set(json.load(open(USED)))
rec = array('i'); rec.frombytes(open(D + '/249-records.bin', 'rb').read()); E = len(rec)//6
fj = json.load(open(D + '/frames.json'))['frames']
Tt = {}; first = {}; reads = collections.Counter()
for i in range(E):
    k, a, b, c, f, z = rec[6*i:6*i+6]
    if k == 0:
        if a >= H0 and a not in Tt: Tt[a] = i; first[a] = c
    elif k == 1:
        if a >= H0 and a not in Tt: Tt[a] = i; first[a] = None
        if b >= H0:
            if z == 4 and f == ZERO and v <= a < 2*v: reads[b] += 1
            elif b not in Tt: Tt[b] = i; first[b] = None
    else:
        for s in (a, b):
            if s >= H0 and s not in Tt: Tt[s] = i; first[s] = None
base = [h for h in range(H0, n) if ini[h] == ZERO and fin[h] == FULL and regs[h-H0] not in borrowed and regs[h-H0] not in donor and h not in used and first.get(h) is not None]
print('base (unused, clean roles, MOVE-first)', len(base), time.time()-t0, flush=True)
phi = lambda r: 0.0 if r == 0 else r*math.log(120/r)
def nullspace(rows):
    m = [[Fr(x) for x in r] for r in rows]; piv = []; r = 0
    for c in range(24):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None: continue
        m[r], m[p] = m[p], m[r]; pv = m[r][c]; m[r] = [x/pv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]; m[i] = [a - f*b for a, b in zip(m[i], m[r])]
        piv.append(c); r += 1
        if r == len(m): break
    free = [c for c in range(24) if c not in piv]; basis = []
    for fcol in free:
        vec = [Fr(0)]*24; vec[fcol] = Fr(1)
        for i, pc in enumerate(piv): vec[pc] = -m[i][fcol]
        basis.append(vec)
    return basis
def prim(vec):
    L = 1
    for x in vec: L = lcm(L, x.denominator)
    iv = [int(x*L) for x in vec]; g = 0
    for x in iv: g = gcd(g, abs(x))
    return [x//g for x in iv]
def gramdet(basis):
    k = len(basis); M = [[Fr(9*sum(a*b for a, b in zip(basis[i], basis[j])) - sum(basis[i])*sum(basis[j])) for j in range(k)] for i in range(k)]; det = Fr(1)
    for c in range(k):
        p = next((i for i in range(c, k) if M[i][c] != 0), None)
        if p is None: return 0
        if p != c: M[c], M[p] = M[p], M[c]; det = -det
        det *= M[c][c]
        for i in range(c+1, k):
            f = M[i][c]/M[c][c]; M[i] = [a - f*b for a, b in zip(M[i], M[c])]
    return det
icache = {}
def entrance(frames):
    """best (gain, e, basis_int_rows, pivot_index) for members' first frames (members ordered); returns None if no nondegenerate entrance"""
    key = tuple(frames)
    if key in icache: return icache[key]
    rows = []
    for f in frames: rows += fj[str(f)]['A']
    basis = nullspace(rows); d = len(basis); res = None
    if d:
        dims = [fj[str(f)]['dim'] for f in frames]
        # candidate entrance subspaces: single lines (each primitive basis vector, prefer small norm) and the full intersection
        options = []
        lines = sorted((prim(b) for b in basis), key=lambda u: sum(x*x for x in u))
        for u in lines:
            if 9*sum(x*x for x in u) - sum(u)**2 != 0: options.append((1, [u])); break
        if d >= 2 and gramdet(basis) != 0: options.append((d, [prim(b) for b in basis]))
        for e, B in options:
            for p in range(len(frames)):
                if dims[p] < e or any(dims[q] < e for q in range(len(frames))): continue
                g = phi(dims[p]-e) - phi(dims[p]) + sum(phi(e) + phi(dims[q]-e) - phi(dims[q]) for q in range(len(frames)) if q != p)
                if res is None or g < res[0]: res = (g, e, B, p)
    icache[key] = res; return res
row = [1 << s for s in range(n+1)]; i = 0; cands = []; stats = collections.Counter()
for cut in CUTS:
    while i <= cut:
        k, a, b, c, f, z = rec[6*i:6*i+6]
        if k == 1:
            if c & 1: row[a] ^= row[b]
        elif k == 2: row[b] = row[a]
        i += 1
    live = [h for h in base if Tt[h] > cut]
    contam = 0
    for s in range(n):
        if v <= s < 2*v: continue
        contam |= (row[s] ^ (1 << s)) >> H0
    resp = collections.defaultdict(int)
    for t in range(v):
        r = row[v+t] >> H0
        while r:
            low = r & -r; idx = low.bit_length()-1; resp[H0+idx] |= 1 << t; r ^= low
    live = [h for h in live if not (contam >> (h-H0)) & 1 and resp[h]]
    cls = collections.defaultdict(list)
    for h in live: cls[resp[h]].append(h)
    sizes = collections.Counter(len(m) for m in cls.values() if len(m) >= 2)
    npair = 0
    for m in cls.values():
        if len(m) < 2: continue
        for a, b in itertools.combinations(m, 2):
            r = entrance([first[a], first[b]])
            if r is None or r[0] >= 0: stats[('pair', 'rejected', cut)] += 1; continue
            g, e, B, p = r; piv, par = (a, b) if p == 0 else (b, a)
            cands.append(dict(gain=g, cut=cut, members=[piv, par], pivot=piv, e=e, basis=B, kind='pair', cls=len(m))); npair += 1
    ntri = 0
    if cut in TRIPLE_CUTS:
        dl = sorted(cls); Sset = set(dl)
        for x in range(len(dl)):
            for y in range(x+1, len(dl)):
                w = dl[x] ^ dl[y]
                if w > dl[y] and w in Sset:
                    for a in cls[dl[x]]:
                        for b in cls[dl[y]]:
                            for c in cls[w]:
                                r = entrance([first[a], first[b], first[c]])
                                if r is None or r[0] >= 0: stats[('triple', 'rejected', cut)] += 1; continue
                                g, e, B, p = r; mem = [a, b, c]; piv = mem[p]
                                cands.append(dict(gain=g, cut=cut, members=[piv] + [h for h in mem if h != piv], pivot=piv, e=e, basis=B, kind='triple')); ntri += 1
    print(f'cut {cut}: live {len(live)} class sizes {sorted(sizes.items())} positive pair-cands {npair} triple-cands {ntri} ({time.time()-t0:.0f}s)', flush=True)
# global greedy packing: best gain first, disjoint helpers; a helper may appear once
cands.sort(key=lambda z: z['gain']); taken = set(); chosen = []
for z in cands:
    if any(h in taken for h in z['members']): continue
    taken |= set(z['members']); chosen.append(z)
S = sum(z['e'] for z in chosen)
print('chosen families', len(chosen), 'by kind', collections.Counter(z['kind'] for z in chosen), 'by cut', collections.Counter(z['cut'] for z in chosen), 'by e', collections.Counter(z['e'] for z in chosen), 'entrance rank', S, 'total gain', round(sum(z['gain'] for z in chosen), 1))
print('chosen by (kind, e, frame dims) top:', collections.Counter((z['kind'], z['e'], tuple(fj[str(first[h])]['dim'] for h in z['members'])) for z in chosen).most_common(15))
json.dump(dict(chosen=chosen, all_candidates=len(cands)), open(OUT, 'w'))
print('done', time.time()-t0)
