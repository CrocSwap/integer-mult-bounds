import json, sys, collections, time, pickle
from array import array
D = sys.argv[1]  # data dir
OUT = sys.argv[2]
t0 = time.time()
st = json.load(open(D + '/249-states.json'))
n, v, ZERO, FULL = st['n'], st['v'], st['ZERO'], st['FULL']
ini = [ZERO]*n; fin = [FULL]*n
for k, x in st['initial'].items(): ini[int(k)] = x
for k, x in st['final'].items(): fin[int(k)] = x
regs = st['regs']; borrowed = set(st['borrowed']); removed = set(st['removed'])
donor = set(json.load(open(D + '/249-DONOR-OWNERSHIP.json'))['donor_keys'])
rec = array('i'); rec.frombytes(open(D + '/249-records.bin', 'rb').read())
E = len(rec)//6
print('events', E, 'n', n, 'v', v, 'ZERO', ZERO, 'FULL', FULL, 'helpers', n-2*v)
cut = [i for i in range(E) if rec[6*i]==1 and rec[6*i+1]==3491 and rec[6*i+2]==3488 and rec[6*i+3]==-1 and rec[6*i+5]==25]
assert len(cut)==1; cut = cut[0]; print('cut', cut)
# per-helper prefix touch census
H0 = 2*v
init_reads = collections.Counter(); bad_touch = collections.Counter(); moves_before = collections.Counter()
row = [1 << s for s in range(n+1)]
kinds = collections.Counter()
for i in range(cut+1):
    k,a,b,c,f,z = rec[6*i:6*i+6]
    kinds[(k,z)] += 1
    if k == 1:
        if c & 1: row[a] ^= row[b]
        if a >= H0: bad_touch[a] += 1
        if b >= H0:
            if z == 4 and f == ZERO and v <= a < 2*v: init_reads[b] += 1
            else: bad_touch[b] += 1
    elif k == 2:
        row[b] = row[a]
        if a >= H0: bad_touch[a] += 1
        if b >= H0: bad_touch[b] += 1
    elif k == 3:
        assert row[a] == row[b]
        if a >= H0: bad_touch[a] += 1
        if b >= H0: bad_touch[b] += 1
    elif k == 0:
        if a >= H0: moves_before[a] += 1
print('prefix replayed', time.time()-t0)
print('prefix event kinds (k,z) top', kinds.most_common(12))
# responses
resp = [0]*n
for t in range(v):
    r = row[v+t] >> H0
    h = H0
    while r:
        low = r & -r
        idx = low.bit_length()-1
        resp[H0+idx] |= 1 << t
        r ^= low
contam = 0
for s in range(n):
    if v <= s < 2*v: continue
    contam |= (row[s] ^ (1 << s)) >> H0
contaminated = {H0+i for i in range(n-H0) if (contam >> i) & 1}
print('responses built', time.time()-t0, 'contaminating helpers', len(contaminated))
# first use after cut
first = {}
for i in range(cut+1, E):
    k,a,b,c,f,z = rec[6*i:6*i+6]
    if k == 0:
        if a >= H0 and a not in first: first[a] = (i, 'MOVE', b, c, z)
    else:
        fr = f if k == 1 else c
        for s in (a, b):
            if s >= H0 and s not in first: first[s] = (i, ('ADD','COPY','ERASE')[k-1], f if k==1 else None, fr, z)
print('first uses found', len(first))
elig = []; reasons = collections.Counter()
for h in range(H0, n):
    why = []
    if ini[h] != ZERO: why.append('ini!=ZERO')
    if fin[h] != FULL: why.append('fin!=FULL')
    if bad_touch[h]: why.append('touched')
    if moves_before[h]: why.append('moved_before')
    if h in contaminated: why.append('contaminates_nontarget')
    if regs[h-H0] in borrowed: why.append('source_owner')
    if regs[h-H0] in donor: why.append('donor')
    if h not in first: why.append('never_used_after')
    elif first[h][1] != 'MOVE': why.append('firstuse_not_MOVE')
    if why: reasons[tuple(why)] += 1
    else: elig.append(h)
print('eligible helpers', len(elig)); print('ineligibility reasons', reasons.most_common(20))
classes = collections.defaultdict(list)
for h in elig: classes[resp[h]].append(h)
sizes = collections.Counter(len(m) for m in classes.values())
print('response classes among eligible: distinct responses', len(classes), 'size dist', sorted(sizes.items()))
print('zero-response eligible helpers', len(classes.get(0, [])))
wt = collections.Counter(bin(resp[h]).count('1') for h in elig); print('response weight dist (eligible)', sorted(wt.items()))
ir = collections.Counter(init_reads[h] for h in elig); print('initial read count dist (eligible)', sorted(ir.items()))
# helpers with a twin
twin_helpers = sum(len(m) for r, m in classes.items() if r != 0 and len(m) >= 2)
twin_pairs = sum(len(m)*(len(m)-1)//2 for r, m in classes.items() if r != 0 and len(m) >= 2)
print('eligible helpers with >=1 nonzero-response twin', twin_helpers, 'unordered twin pairs', twin_pairs)
# compare with candidates
cand = json.load(open(D + '/candidates.json'))['candidates']
ok = 0; mism = []
for z in cand:
    a, b = z['a'], z['b']
    if resp[a] == resp[b] and a in set(elig) and b in set(elig): ok += 1
    else: mism.append((a, b, resp[a]==resp[b], a in elig, b in elig))
    if first.get(a, (0,0,0,None))[3] != z['first_a'] or first.get(b,(0,0,0,None))[3] != z['first_b']: mism.append(('frame', a, b, first.get(a), z['first_a'], first.get(b), z['first_b']))
print('candidates confirmed twins & eligible', ok, 'mismatches', mism[:5], len(mism))
# first-use frame dims and times
pickle.dump(dict(cut=cut, elig=elig, resp={h: resp[h] for h in range(H0, n)}, first=first, init_reads=dict(init_reads), classes={r: m for r, m in classes.items()}, ini=ini, fin=fin, contaminated=contaminated, bad_touch=dict(bad_touch), moves_before=dict(moves_before)), open(OUT, 'wb'))
# linear dependence among distinct nonzero responses of eligible helpers (F2 rank)
basis = {}
def reduce(x):
    while x:
        p = x.bit_length()-1
        if p in basis: x ^= basis[p]
        else: return x
    return 0
distinct = [r for r in classes if r]
rank = 0; dependent = []
for r in sorted(distinct):
    y = reduce(r)
    if y: basis[y.bit_length()-1] = y; rank += 1
    else: dependent.append(r)
print('distinct nonzero responses', len(distinct), 'F2 rank', rank, 'dependent responses', len(dependent))
# close pairs: symmetric difference 1 or 2 among distinct responses of eligible helpers
# and triples R_a ^ R_b = R_c
S = set(distinct)
sd1 = 0; sd2 = 0
dl = distinct
import itertools
# symmetric difference <=2 via bit flips
sdset = collections.Counter()
for r in dl:
    bits = [i for i in range(v) if (r >> i) & 1]
    # weight small, so enumerate flips of up to 2 bits among all v positions is 1760+1760^2/2 - too many; use flips of existing bits + adding 1 bit
    for i in range(v):
        if (r ^ (1 << i)) in S: sdset[1] += 1
    for i in range(v):
        for j in bits:
            if j != i and (r ^ (1 << i) ^ (1 << j)) in S: sdset[2] += 1
print('ordered distinct-response pairs at sym diff 1:', sdset[1]//2, ' at sym diff 2 (both-in-weight-change or one-flip-one-add):', sdset[2]//2)
# triples: r_c = r_a ^ r_b with all three distinct eligible responses
tri = 0
dl_sorted = sorted(dl)
Sset = S
for i in range(len(dl_sorted)):
    for j in range(i+1, len(dl_sorted)):
        x = dl_sorted[i] ^ dl_sorted[j]
        if x in Sset and x != dl_sorted[i] and x != dl_sorted[j]: tri += 1
print('XOR triples (a,b unordered, c=a^b in set), counted per pair:', tri, ' -> distinct triples', tri//3)
print('done', time.time()-t0)
