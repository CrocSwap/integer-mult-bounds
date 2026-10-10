import json, sys, collections, math
from decimal import Decimal as Dc, getcontext
getcontext().prec = 50
c259 = json.load(open(sys.argv[1])); mine = json.load(open(sys.argv[2]))['candidates']; rep = json.load(open(sys.argv[3])); fj = json.load(open(sys.argv[4]))['frames']
items = c259 if isinstance(c259, list) else c259['candidates']
print('PR259 candidates', len(items), 'item key sets', collections.Counter(tuple(sorted(z.keys())) for z in items).most_common(4))
used = set(); piv = set(); cuts = collections.Counter(); dims = collections.Counter(); fam = collections.Counter()
for z in items:
    if 'roles' in z: p = z['pivot']; roles = list(z['roles']); d = z['dim']
    else: p = z['a']; roles = [z['a'], z['b']]; d = z['E_dimension']
    piv.add(p); used |= set(roles); cuts[z.get('cut', 727593)] += 1; dims[d] += 1; fam[len(roles)] += 1
print('pivots', len(piv), 'distinct helpers', len(used), 'cuts', dict(cuts), 'E dims', sorted(dims.items()), 'family sizes', sorted(fam.items()))
print('sum of dims (entrance rank)', sum((z['dim'] if 'roles' in z else z['E_dimension']) for z in items))
my_used = {z['a'] for z in mine} | {z['b'] for z in mine}
print('my pairs', len(mine), 'my helpers', len(my_used), 'overlap helpers with PR259', len(my_used & used), 'my pivots that are PR259 pivots', len({z['a'] for z in mine} & piv))
free = [z for z in mine if z['a'] not in used and z['b'] not in used]
half = [z for z in mine if (z['a'] in used) != (z['b'] in used)]
print('my pairs fully disjoint from PR259 helpers:', len(free), ' pairs with exactly one helper used by PR259:', len(half))
print('free pairs by frame dims:', collections.Counter(tuple(z.get('frame_dims', [3, 3])) for z in free))
print('free pairs by source:', collections.Counter(z.get('source', '?') for z in free))
# price union: PR259 histogram (x40 + completions) and W=173435, then add free pairs e=1 (drop weakest to keep count = 0 mod 3)
LN = {}
def moment(H, W, a, m=120):
    s = Dc(0); N = 0
    for r, n in H.items():
        if n == 0: continue
        if r not in LN: LN[r] = (Dc(m)/Dc(r)).ln()
        s += Dc(r*n)/(Dc(m)*W) * (LN[r]*a).exp(); N += n
    if 'm' not in LN: LN['m'] = Dc(m).ln()
    return s + Dc(32*m*m*N)/(Dc(m)*W) * (LN['m']*a).exp() / Dc(10)**16
grid = Dc(10)**18
def price(H, W):
    lo, hi = Dc('0.0005'), Dc('0.001'); assert moment(H, W, lo) < 1 < moment(H, W, hi)
    for _ in range(80):
        mid = (lo+hi)/2
        if moment(H, W, mid) < 1: lo = mid
        else: hi = mid
    z = int(lo*grid); assert moment(H, W, Dc(z)/grid) < 1 and moment(H, W, Dc(z+1)/grid) > 1
    c = Dc(z)/grid; bit = Dc(384599)/Dc(10)**10
    for _ in range(3): bit = (1-c)*c + c*bit
    eta = Dc(1)/Dc(10)**12; q = bit*(1-2*eta); bound = (1-eta)*q/(1+q)
    return Dc(int(bound*grid))/grid, c
H = {int(k): 40*v for k, v in rep['histogram'].items()}
for r in (4, 23, 46, 50): H[r] = H.get(r, 0) + 16*1760
k259, c259v = price(H, Dc(173435)); print('PR259 kappa reproduced:', k259, 'coarse', c259v)
free.sort(key=lambda z: z['approx_slack_delta'])
while len(free) % 3: free.pop()
H2 = dict(H)
for z in free:
    ra, rb = z.get('frame_dims') or [fj[str(z['first_a'])]['dim'], fj[str(z['first_b'])]['dim']]
    for r, dn in ((ra, -40), (rb, -40), (ra-1, 40), (1, 40), (rb-1, 40)):
        if r > 0: H2[r] = H2.get(r, 0) + dn
W2 = Dc(173435) - Dc(len(free))/3
k2, c2 = price(H2, W2)
print(f'UNION projection: PR259 + {len(free)} free e=1 pairs -> kappa={k2} coarse={c2} W={W2} mass={sum(r*n for r,n in H2.items())} deficit={120*W2-sum(r*n for r,n in H2.items())}')
print(f'  dk vs PR259 = {k2-k259}   dk vs PR263 (7.11032e-4 nominal) = {k2-Dc("0.000711032")}')
json.dump(dict(free=[(z['a'], z['b']) for z in free]), open(sys.argv[5], 'w'))
