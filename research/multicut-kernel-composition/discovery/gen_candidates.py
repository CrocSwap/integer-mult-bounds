"""Emit PR254-schema candidates for the response-twin rewrite at an early cut.
usage: gen_candidates.py DATA_DIR PR254_CANDIDATES_JSON CUT PHASE OUT_JSON
PHASE 1: u with sum 0, u.u = 4 (four +-1 entries), e=1.  PHASE 2: additionally u = e_i - e_j (u.u = 2)."""
import json, sys, collections, time, itertools, math, gzip
from array import array
from fractions import Fraction as Fr
from math import lcm, gcd
D, PRC, CUT, PHASE, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
t0 = time.time()
st = json.load(open(D + '/249-states.json')); n, v, ZERO, FULL = st['n'], st['v'], st['ZERO'], st['FULL']; H0 = 2*v
ini = [ZERO]*n; fin = [FULL]*n
for k, x in st['initial'].items(): ini[int(k)] = x
for k, x in st['final'].items(): fin[int(k)] = x
regs = st['regs']; borrowed = set(st['borrowed']); donor = set(json.load(open(D + '/249-DONOR-OWNERSHIP.json'))['donor_keys'])
rec = array('i'); rec.frombytes(open(D + '/249-records.bin', 'rb').read()); E = len(rec)//6
fj = json.load(open(D + '/frames.json'))['frames']
pr = json.load(open(PRC))['candidates']; prmap = {}
for z in pr: prmap[(z['a'], z['b'])] = z
# sanity on the cut: record CUT-1 is the last zero-frame initial read, none after
reads_after = sum(1 for i in range(CUT, E) if rec[6*i] == 1 and rec[6*i+5] == 4 and rec[6*i+4] == ZERO)
last_read = max(i for i in range(E) if rec[6*i] == 1 and rec[6*i+5] == 4 and rec[6*i+4] == ZERO)
print('cut', CUT, 'last initial read', last_read, 'reads after cut', reads_after); assert reads_after == 0
# prefix census
bad = collections.Counter(); reads = collections.Counter(); row = [1 << s for s in range(n+1)]
for i in range(CUT+1):
    k, a, b, c, f, z = rec[6*i:6*i+6]
    if k == 1:
        if c & 1: row[a] ^= row[b]
        if a >= H0: bad[a] += 1
        if b >= H0:
            if z == 4 and f == ZERO and v <= a < 2*v: reads[b] += 1
            else: bad[b] += 1
    elif k == 2:
        row[b] = row[a]
        for s in (a, b):
            if s >= H0: bad[s] += 1
    elif k == 3:
        for s in (a, b):
            if s >= H0: bad[s] += 1
    elif k == 0 and a >= H0: bad[a] += 1
first = {}
for i in range(CUT+1, E):
    k, a, b, c, f, z = rec[6*i:6*i+6]
    if k == 0:
        if a >= H0 and a not in first: first[a] = ('MOVE', c)
    else:
        for s in (a, b):
            if s >= H0 and s not in first: first[s] = ('OTHER', None)
contam = 0
for s in range(n):
    if v <= s < 2*v: continue
    contam |= (row[s] ^ (1 << s)) >> H0
resp = collections.defaultdict(int)
for t in range(v):
    r = row[v+t] >> H0
    while r:
        low = r & -r; idx = low.bit_length()-1; resp[H0+idx] |= 1 << t; r ^= low
elig = [h for h in range(H0, n) if ini[h] == ZERO and fin[h] == FULL and not bad[h] and regs[h-H0] not in borrowed and regs[h-H0] not in donor and h in first and first[h][0] == 'MOVE' and not (contam >> (h-H0)) & 1 and resp[h]]
cls = collections.defaultdict(list)
for h in elig: cls[resp[h]].append(h)
pairs = [tuple(m) for m in cls.values() if len(m) == 2]
print('eligible', len(elig), 'twin pairs', len(pairs), 'classes>=3', sum(1 for m in cls.values() if len(m) > 2), time.time()-t0)
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
def admissible(u):
    s = sum(u); nrm = sum(x*x for x in u)
    if s != 0: return False
    if nrm == 4 and all(abs(x) <= 1 for x in u): return True
    if PHASE >= 2 and nrm == 2: return True
    return False
def find_u(basis):
    d = len(basis)
    if d == 1:
        u = prim(basis[0]); return u if admissible(u) else None
    best = None
    for lam in itertools.product((-1, 0, 1), repeat=d):
        if not any(lam): continue
        u = [sum(l*b[i] for l, b in zip(lam, basis)) for i in range(24)]
        if all(x.denominator == 1 for x in u):
            u = prim([Fr(int(x)) for x in u])
            if admissible(u) and (best is None or sum(x*x for x in u) > sum(x*x for x in best)): best = u  # prefer norm-4 (PR rule)
    return best
phi = lambda r: 0.0 if r == 0 else r*math.log(120/r)
def annihilator(u):
    sup = [i for i in range(24) if u[i]]; last = sup[-1]; rows = []
    for k in range(24):
        if k == last: continue
        r = [0]*24; r[k] = 1
        if u[k]: r[last] = -u[k]*u[last]  # (e_k - (u_k/u_last) e_last), |u_last| = 1
        rows.append(r)
    assert len(rows) == 23 and all(sum(x*y for x, y in zip(r, u)) == 0 for r in rows)
    return rows
cands = []; stats = collections.Counter()
for a, b in pairs:
    Fa, Fb = first[a][1], first[b][1]; ra, rb = fj[str(Fa)]['dim'], fj[str(Fb)]['dim']
    basis = nullspace(fj[str(Fa)]['A'] + fj[str(Fb)]['A']); d = len(basis)
    if d == 0: stats['dim0'] += 1; continue
    u = find_u(basis)
    if u is None: stats[f'no_admissible_u_dim{d}'] += 1; continue
    gain = min(phi(ra-1)-phi(ra)+phi(1)+phi(rb-1)-phi(rb), phi(rb-1)-phi(rb)+phi(1)+phi(ra-1)-phi(ra))
    if gain >= 0: stats[f'nonpositive_gain_{tuple(sorted((ra,rb)))}'] += 1; continue
    if (a, b) in prmap or (b, a) in prmap:  # keep PR254's own pair orientation and line verbatim
        z = dict(prmap[(a, b)] if (a, b) in prmap else prmap[(b, a)]); z['approx_slack_delta'] = gain; z['source'] = 'PR254'
        assert z['first_a'] == first[z['a']][1] and z['first_b'] == first[z['b']][1]
        cands.append(z); stats['PR254_pair'] += 1; continue
    # pivot = smaller first frame (its move shrinks); tie -> more initial reads removed
    if (ra, -reads[a]) <= (rb, -reads[b]): p, q, Fp, Fq = a, b, Fa, Fb
    else: p, q, Fp, Fq = b, a, Fb, Fa
    fmt = lambda r: [str(x) for x in r]
    cands.append(dict(E_dimension=1, a=p, annihilator=[fmt(r) for r in annihilator(u)], approx_slack_delta=gain, b=q, basis=[fmt(u)], first_a=Fp, first_b=Fq, new_targets=[], nondegeneracy_not_checked=True, source='early-cut', frame_dims=[fj[str(Fp)]['dim'], fj[str(Fq)]['dim']], u_norm=sum(x*x for x in u), pivot_initial_reads=reads[p]))
    stats[f'new_pair_norm{sum(x*x for x in u)}_{(fj[str(Fp)]["dim"], fj[str(Fq)]["dim"])}'] += 1
print('stats', dict(stats))
# trim to P = 0 mod 3 by dropping the weakest gains
cands.sort(key=lambda z: z['approx_slack_delta'])
while len(cands) % 3: dropped = cands.pop(); print('dropped weakest pair', dropped['a'], dropped['b'], dropped['approx_slack_delta'])
out = dict(status='EXACT_INTERSECTION_EARLY_CUT_LOG_WEIGHTED_POSITIVE', cut_record=CUT, phase=PHASE, chart_rule='sum 0, norm 4 (four +-1)' if PHASE == 1 else 'sum 0, norm 4 or norm 2 (e_i - e_j)', approx_positive=len(cands), close_response_pairs=len(pairs), intersections=len(pairs)-stats['dim0'], max_response_symmetric_difference=0, no_kappa_claim=True, total_phi_gain=sum(z['approx_slack_delta'] for z in cands), candidates=cands)
json.dump(out, open(OUT, 'w'), indent=1); open(OUT + '.gz', 'wb').write(gzip.compress(json.dumps(out, indent=1).encode(), mtime=0))
print('wrote', OUT, 'pairs', len(cands), 'P mod 3 =', len(cands) % 3, 'phi gain', round(out['total_phi_gain'], 2), 'removed reads', sum(reads[z['a']] for z in cands), time.time()-t0)
