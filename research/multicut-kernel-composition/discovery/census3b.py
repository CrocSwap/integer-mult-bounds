"""Shared-donor census at cut 676559: new pivot p (unused, untouched) twin with an existing donor d, entrance = d's existing entrance (or a nested line in it)."""
import json, sys, collections, math, gzip, time, itertools
from array import array
from fractions import Fraction as Fr
from math import lcm, gcd
D, WIT, C270, OUT = sys.argv[1:5]; CUT = 676559; t0 = time.time()
st = json.load(open(D + '/249-states.json')); n, v, ZERO, FULL = st['n'], st['v'], st['ZERO'], st['FULL']; H0 = 2*v
ini = [ZERO]*n; fin = [FULL]*n
for k, x in st['initial'].items(): ini[int(k)] = x
for k, x in st['final'].items(): fin[int(k)] = x
regs = st['regs']; borrowed = set(st['borrowed']); donor_keys = set(json.load(open(D + '/249-DONOR-OWNERSHIP.json'))['donor_keys'])
rec = array('i'); rec.frombytes(open(D + '/249-records.bin', 'rb').read()); E = len(rec)//6
fj = json.load(open(D + '/frames.json'))['frames']
wit = json.load(open(WIT)); c270 = json.load(open(C270))
Tt = {}; first = {}
for i in range(E):
    k, a, b, c, f, z = rec[6*i:6*i+6]
    if k == 0:
        if a >= H0 and a not in Tt: Tt[a] = i; first[a] = c
    elif k == 1:
        if a >= H0 and a not in Tt: Tt[a] = i; first[a] = None
        if b >= H0 and b not in Tt and not (z == 4 and f == ZERO and v <= a < 2*v): Tt[b] = i; first[b] = None
    else:
        for s in (a, b):
            if s >= H0 and s not in Tt: Tt[s] = i; first[s] = None
pivots = {z['pivot'] for z in wit}; donors = collections.defaultdict(list)
for z in wit:
    B = [[int(x) for x in r] for r in z['basis']]
    for d in z['partners']: donors[d].append(dict(cut=z['cut'], dim=z['dim'], basis=B, pivot=z['pivot']))
used = pivots | set(donors)
newpairs = {z['pivot']: z for z in wit if z.get('round') and len(z['roles']) == 2}
member_of = {}
for z in newpairs.values():
    for h in z['roles']: member_of[h] = z['pivot']
donor_refs = collections.Counter(d for z in wit for d in z['partners'])
famgain = {z['pivot']: z['approx_slack_delta'] for z in newpairs.values()}
pool = [h for h in range(H0, n) if ini[h] == ZERO and fin[h] == FULL and regs[h-H0] not in borrowed and regs[h-H0] not in donor_keys and (h not in used or h in member_of) and first.get(h) is not None and Tt[h] > CUT]
print('witness families', len(wit), 'pivots', len(pivots), 'distinct donors', len(donors), 'pool of unused untouched helpers', len(pool), flush=True)
# responses at CUT
row = [1 << s for s in range(n+1)]
for i in range(CUT+1):
    k, a, b, c, f, z = rec[6*i:6*i+6]
    if k == 1:
        if c & 1: row[a] ^= row[b]
    elif k == 2: row[b] = row[a]
contam = 0
for s in range(n):
    if v <= s < 2*v: continue
    contam |= (row[s] ^ (1 << s)) >> H0
resp = collections.defaultdict(int)
for t in range(v):
    r = row[v+t] >> H0
    while r:
        low = r & -r; idx = low.bit_length()-1; resp[H0+idx] |= 1 << t; r ^= low
pool = [h for h in pool if not (contam >> (h-H0)) & 1 and resp[h]]
byresp = collections.defaultdict(list)
for h in pool: byresp[resp[h]].append(h)
phi = lambda r: 0.0 if r == 0 else r*math.log(120/r)
def contained(B, F):  # subspace rows B inside frame F (annihilator test)
    return all(sum(x*y for x, y in zip(b, a)) == 0 for b in B for a in fj[str(F)]['A'])
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
    free = [c for c in range(24) if c not in piv]; out = []
    for fcol in free:
        vec = [Fr(0)]*24; vec[fcol] = Fr(1)
        for i, pc in enumerate(piv): vec[pc] = -m[i][fcol]
        out.append(vec)
    return out
def prim(vec):
    L = 1
    for x in vec: L = lcm(L, x.denominator)
    iv = [int(x*L) for x in vec]; g = 0
    for x in iv: g = gcd(g, abs(x))
    return [x//g for x in iv]
def ann_of(B):  # annihilator rows of span(B) as integer rows
    return [prim(u) for u in nullspace(B)]
cands = []; stats = collections.Counter()
for d, fams in donors.items():
    if Tt.get(d, 0) <= CUT or d not in resp or resp[d] == 0 or (contam >> (d-H0)) & 1: stats['donor_touched_or_contaminated'] += 1; continue
    twins = byresp.get(resp[d], [])
    if not twins: continue
    for fam in fams:
        if fam['cut'] < CUT: continue
        e, B = fam['dim'], fam['basis']; rp_all = []
        for p in twins:
            Fp = first[p]; rp = fj[str(Fp)]['dim']
            if contained(B, Fp) and rp >= e:
                g = phi(rp-e) - phi(rp); cands.append(dict(gain=g, pivot=p, donor=d, e=e, basis=B, cut=CUT, mode='same-entrance', donor_cut=fam['cut'], donor_pivot=fam['pivot'])); stats['same-entrance'] += 1
            elif e >= 2:
                # line inside E_d ∩ F_p: nullspace of (ann(E_d) ∪ ann(F_p))
                inter = nullspace(ann_of(B) + fj[str(Fp)]['A'])
                if inter:
                    u = prim(inter[0])
                    if 9*sum(x*x for x in u) - sum(u)**2 != 0:
                        g = phi(rp-1) - phi(rp) + phi(1) + phi(e-1) - phi(e); cands.append(dict(gain=g, pivot=p, donor=d, e=1, basis=[u], cut=CUT, mode='nested-line', donor_cut=fam['cut'], donor_pivot=fam['pivot'])); stats['nested-line'] += 1
                    else: stats['nested-line-degenerate'] += 1
                else: stats['no-line'] += 1
            else: stats['E_not_in_Fp'] += 1
print('candidate stats', dict(stats), 'candidates', len(cands), f'({time.time()-t0:.0f}s)', flush=True)
cands.sort(key=lambda z: z['gain']); taken = set(); chosen = []; dissolved = set(); freed = set()
for z in cands:
    if z['gain'] >= 0: break
    p = z['pivot']
    if p in taken or z['donor'] in dissolved_donors if False else False: continue
    if p in taken: continue
    if p in member_of and member_of[p] not in dissolved and p not in freed:
        fam = newpairs[member_of[p]]; dnr = fam['partners'][0]
        # dissolve only if strictly better and the pair's donor is referenced by no other family (incl. chosen shared ones)
        if z['gain'] - famgain[fam['pivot']] >= 0 or donor_refs[dnr] > 1 or any(c['donor'] == dnr for c in chosen) or z['donor'] in fam['roles']: continue
        dissolved.add(fam['pivot']); freed |= set(fam['roles']); taken.add(fam['pivot']) if fam['pivot'] != p else None
    elif p in member_of and member_of[p] in dissolved and p not in freed: continue
    taken.add(p); chosen.append(z)
print('dissolved own pair families', len(dissolved))
wit = [z for z in wit if z['pivot'] not in dissolved]
print('chosen shared-donor families', len(chosen), 'by mode', collections.Counter(z['mode'] for z in chosen), 'by e', collections.Counter(z['e'] for z in chosen), 'distinct donors', len({z['donor'] for z in chosen}), 'max pivots per donor', max(collections.Counter(z['donor'] for z in chosen).values()), 'phi gain', round(sum(z['gain'] for z in chosen), 1))
print('by (pivot first dim, e):', collections.Counter((fj[str(first[z['pivot']])]['dim'], z['e']) for z in chosen).most_common(8))
# cross-check with #270's 24
sh270 = {(z['pivot'], z['partners'][0]) for z in c270 if z.get('kind') == 'reuse'}
mine = {(z['pivot'], z['donor']) for z in chosen}
print('#270 reuse pairs reproduced in my chosen set:', len(sh270 & mine), 'of 24; #270 pairs with pivot already used in union3:', sum(1 for p, d in sh270 if p in used))
chosen = [z for z in chosen if z['donor'] not in {h for f in dissolved for h in newpairs[f]['roles']} or z['donor'] in {d for z2 in wit for d in z2['partners']}]
S = sum(z['dim'] for z in wit) + sum(z['e'] for z in chosen)
while S % 3:
    for j in range(len(chosen)-1, -1, -1):
        if chosen[j]['e'] == 1: S -= 1; chosen.pop(j); break
items = [dict(pivot=z['pivot'], a=z['pivot'], roles=[z['pivot'], z['donor']], partners=[z['donor']], dim=z['e'], E_dimension=z['e'], basis=[[str(x) for x in r] for r in z['basis']], cut=z['cut'], approx_slack_delta=z['gain'], kind='shared-donor %s (donor of pivot %d at cut %d)' % (z['mode'], z['donor_pivot'], z['donor_cut']), round='shared-donor') for z in chosen]
merged = wit + items; print('merged families', len(merged), 'entrance rank', S, 'mod 3', S % 3)
json.dump(merged, open(OUT, 'w'), indent=1); open(OUT + '.gz', 'wb').write(gzip.compress(json.dumps(merged, indent=1).encode(), mtime=0))
