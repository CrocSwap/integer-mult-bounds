import gzip, json, sys
from collections import Counter, defaultdict
W = json.load(gzip.open(sys.argv[1], 'rt'))
n = W['public']; N = n + W['owned_fields']
fr = [frozenset() for _ in W['frames']]
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
sp = [span(b) for b in W['frames']]; dim = [len(b) for b in W['frames']]
def meetdim(a, b): return len(sp[a] & sp[b]).bit_length() - 1
def d(a, b): return dim[a] + dim[b] - 2 * meetdim(a, b)
# build per-lifetime stop lists: [chart, nops]
cur = list(W['initial']) + [None] * W['owned_fields']
life = defaultdict(list)  # key (reg, lifeno) -> list of [chart, ops]
lno = Counter()
for r in range(n): life[(r, 0)].append([cur[r], 0])
for e in W['program']:
    op, r = e[0], e[1]
    if op == 'MOVE':
        life[(r, lno[r])].append([e[3], 0])
    elif op == 'INIT':
        lno[r] += 1; life[(r, lno[r])].append([e[2], 0])
    elif op == 'CLEAR':
        life[(r, lno[r])][-1][1] += 1  # count the clear as an op at that chart
    elif op in ('ADD', 'COPY'):
        life[(r, lno[r])][-1][1] += 1
        s = e[2]; life[(s, lno[s])][-1][1] += 1
    elif op == 'SCALE':
        life[(r, lno[r])][-1][1] += 1
# analysis
tot_turn = Counter(); empty_mono = 0; rows = []
for (r, l), stops in life.items():
    owned = r >= n
    for i in range(1, len(stops) - 1):
        a, b, c = stops[i-1][0], stops[i][0], stops[i+1][0]
        if stops[i][1] == 0:
            r1, r2, rf = d(a, b), d(b, c), d(a, c)
            mono = (sp[a] < sp[b] < sp[c]) or (sp[a] > sp[b] > sp[c])
            if mono: empty_mono += 1
            rows.append((owned, r, i, dim[a], dim[b], dim[c], r1, r2, rf, mono))
print('lifetimes', len(life), 'empty intermediate stops', len(rows), 'monotone', empty_mono)
for x in rows[:60]: print(x)
# helper hop statistics and per-helper D0 cost f(credit) - sum f(hops)
import math
f = lambda r: r*math.log(r) if r > 0 else 0.0
main = set(W['live']) | {r+112 for r in W['live']} | set(W['hosted']['X2']) | set(W['hosted']['Y2'])
hopsc = Counter(); noops = 0; cost = 0.0; firstops = Counter()
for r in range(n):
    if r in main: continue
    st = life[(r, 0)]
    hops = [d(st[i-1][0], st[i][0]) for i in range(1, len(st))]
    hopsc[len(hops)] += 1
    if all(s[1] == 0 for s in st): noops += 1
    cost += f(sum(hops)) - sum(f(h) for h in hops)
    firstops[(st[0][1] > 0, st[-1][1] > 0)] += 1
print('helper hop-count hist', sorted(hopsc.items()), 'helpers with no ops', noops)
print('helper D0 cost per call', round(cost, 2), '(ops at first stop, ops at last stop) hist', dict(firstops))
for r in range(n):
    if r in main: continue
    st = life[(r, 0)]
    if st[0][1] == 0 or st[-1][1] == 0:
        print('helper', r, [(dim[c], k) for c, k in st])
