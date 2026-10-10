import json, sys, collections, time, pickle, itertools
from array import array
from fractions import Fraction as Fr
from math import lcm, gcd
D = sys.argv[1]; T = pickle.load(open(sys.argv[2], 'rb')); C = pickle.load(open(sys.argv[3], 'rb')); CUT = int(sys.argv[4])
t0 = time.time()
st = json.load(open(D + '/249-states.json')); n, v, ZERO, FULL = st['n'], st['v'], st['ZERO'], st['FULL']
ini, fin, regs = T['ini'], T['fin'], st['regs']; borrowed = set(st['borrowed']); donor = set(json.load(open(D + '/249-DONOR-OWNERSHIP.json'))['donor_keys'])
rec = array('i'); rec.frombytes(open(D + '/249-records.bin', 'rb').read()); E = len(rec)//6; H0 = 2*v
Tt, kind = C['Tt'], C['kind']
fj = json.load(open(D + '/frames.json'))['frames']
# first MOVE destination frame after CUT for each helper
ff = {}
for i in range(CUT+1, E):
    k,a,b,c,f,z = rec[6*i:6*i+6]
    if k == 0 and a >= H0 and a not in ff: ff[a] = c
row = [1 << s for s in range(n+1)]
for i in range(CUT+1):
    k,a,b,c,f,z = rec[6*i:6*i+6]
    if k == 1:
        if c & 1: row[a] ^= row[b]
    elif k == 2: row[b] = row[a]
base = [h for h in range(H0, n) if ini[h] == ZERO and fin[h] == FULL and regs[h-H0] not in borrowed and regs[h-H0] not in donor and Tt[h] > CUT and kind[h][0] == 'MOVE']
contam = 0
for s in range(n):
    if v <= s < 2*v: continue
    contam |= (row[s] ^ (1 << s)) >> H0
resp = collections.defaultdict(int)
for t in range(v):
    r = row[v+t] >> H0
    while r:
        low = r & -r; idx = low.bit_length()-1; resp[H0+idx] |= 1 << t; r ^= low
live = [h for h in base if not (contam >> (h-H0)) & 1 and resp[h]]
cls = collections.defaultdict(list)
for h in live: cls[resp[h]].append(h)
print(f'CUT {CUT}: base {len(base)} live(clean,nonzero resp) {len(live)} distinct responses {len(cls)} class sizes {sorted(collections.Counter(len(m) for m in cls.values()).items())}')
def nullspace(rows):
    m = [[Fr(x) for x in r] for r in rows]; ncol = 24; piv = []; r = 0
    for c in range(ncol):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None: continue
        m[r], m[p] = m[p], m[r]; pv = m[r][c]; m[r] = [x/pv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]; m[i] = [a - f*b for a, b in zip(m[i], m[r])]
        piv.append(c); r += 1
        if r == len(m): break
    free = [c for c in range(ncol) if c not in piv]; basis = []
    for fcol in free:
        vec = [Fr(0)]*ncol; vec[fcol] = Fr(1)
        for i, pc in enumerate(piv): vec[pc] = -m[i][fcol]
        basis.append(vec)
    return basis, free
def gramdet(basis):
    k = len(basis); M = [[9*sum(a*b for a, b in zip(basis[i], basis[j])) - sum(basis[i])*sum(basis[j]) for j in range(k)] for i in range(k)]
    det = Fr(1)
    for c in range(k):
        p = next((i for i in range(c, k) if M[i][c] != 0), None)
        if p is None: return 0
        if p != c: M[c], M[p] = M[p], M[c]; det = -det
        det *= M[c][c]
        for i in range(c+1, k):
            f = M[i][c]/M[c][c]; M[i] = [a - f*b for a, b in zip(M[i], M[c])]
    return det
def shape4(u): return sorted(abs(x) for x in u) == [0]*20 + [1]*4 and sum(u) == 0
def prim(vec):
    L = 1
    for x in vec: L = lcm(L, x.denominator)
    iv = [int(x*L) for x in vec]; g = 0
    for x in iv: g = gcd(g, abs(x))
    return [x//g for x in iv]
def classify(frames):
    rows = []
    for f in frames: rows += fj[str(f)]['A']
    basis, free = nullspace(rows); d = len(basis)
    if d == 0: return 'dim0', None
    g = gramdet(basis)
    if d == 1: u = prim(basis[0]); return (f'dim1_{"shape4" if shape4(u) else "other"}' + ('_degenerate' if g == 0 else ''), u)
    if d <= 8:
        for lam in itertools.product((-1, 0, 1), repeat=d):
            if not any(lam): continue
            u = [sum(l*b[i] for l, b in zip(lam, basis)) for i in range(24)]
            if all(x.denominator == 1 for x in u) and shape4([int(x) for x in u]): return f'dim{d}_has_shape4' + ('_degenerate' if g == 0 else ''), [int(x) for x in u]
        return f'dim{d}_no_shape4' + ('_degenerate' if g == 0 else ''), None
    return f'dim{d}_unchecked', None
res = collections.Counter(); fdims = collections.Counter(); otheru = []
final_pairs = {tuple(sorted(m)) for r, m in T['classes'].items() if r and len(m) == 2}
pairs = [tuple(sorted(m)) for m in cls.values() if len(m) == 2]
for p in pairs:
    key, u = classify([ff[p[0]], ff[p[1]]]); res[(key, p in final_pairs)] += 1; fdims[(fj[str(ff[p[0]])]['dim'], fj[str(ff[p[1]])]['dim'])] += 1
    if key == 'dim1_other' and p in final_pairs: otheru.append(u)
print('twin pairs by (intersection class, is-final-cut-pair):'); [print('  ', k, c) for k, c in sorted(res.items(), key=lambda x: -x[1])]
print('first-frame dim pairs (top 12):', fdims.most_common(12))
print('u vectors of final-cut dim1_other pairs:'); [print('  ', u, 'norm', sum(x*x for x in u), 'sum', sum(u)) for u in otheru]
big = [m for m in cls.values() if len(m) >= 3]
print('classes of size>=3:', [len(m) for m in big])
bres = collections.Counter()
for m in big:
    key, u = classify([ff[h] for h in m]); bres[(len(m), key)] += 1
print('size>=3 classes common-intersection:', dict(bres))
print('done', time.time()-t0)
