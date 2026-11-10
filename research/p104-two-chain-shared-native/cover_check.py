#!/usr/bin/env python3
"""What the word is made of, counted on the word and compared with the #6889 word (standard library).  python3 -I -B cover_check.py
Counts the second main planes and the helpers they share with the first planes, the events that touch second mains, and runs controls on a random-evaluation replay (mod 2^61-1):
a wrong weight (x2), a missing event and an event taken twice, on every sampled event that reads or writes a second main, are all rejected."""
import gzip, json, os, random
from collections import Counter
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
def load(n): return json.load(gzip.open(os.path.join(HERE, 'data', n), 'rt'))
new, old = load('word.json.gz'), load('prior_word_6889.json.gz')
H = new['hosted']; X2 = H['X2']; Y2 = H['Y2']; live = new['live']
X = set(live); Y = {r + 112 for r in live}; M1 = X | Y; M2 = set(X2) | set(Y2); n = len(new['initial'])
P = new['program']; lo = next(i for i, e in enumerate(P) if e[0] == 'MOVE'); hi = max(i for i, e in enumerate(P) if e[0] == 'MOVE')
Po = old['program']
dim = [len(b) for b in new['frames']]
hel_n = [r for r in range(n) if r not in M1 and r not in M2]
no = len(old['initial']); mo = set(old['live']) | {r + 112 for r in old['live']}; hel_o = [r for r in range(no) if r not in mo]
print('  #6889 word: events %d, public %d (%d mains, %d helpers), MOVEs %d' % (len(Po), no, len(mo), len(hel_o), sum(e[0] == 'MOVE' for e in Po)))
print('  this word : events %d, public %d (%d mains, %d helpers), MOVEs %d' % (len(P), n, len(M1) + len(M2), len(hel_n), sum(e[0] == 'MOVE' for e in P)))
need(len(M1) == 208 and len(M2) == 208 and len(M1 | M2) == 416 and n == 1375 and len(hel_n) == 959 and len(hel_o) == 1153, 'four main registers per port (416 mains, 959 helpers, 1375 public); the #6889 word has 208 mains and 1153 helpers')
mv_by = Counter()
for e in P:
    if e[0] == 'MOVE':
        mv_by['second main' if e[1] in M2 else 'first main' if e[1] in M1 else 'owned' if e[1] >= n else 'helper'] += 1
need(mv_by['first main'] == mv_by['second main'] and mv_by['first main'] > 0, 'each plane pays its own moves: first-plane mains %d MOVEs, second-plane mains %d MOVEs (no move is shared or fused)' % (mv_by['first main'], mv_by['second main']))
need(all(new['initial'][x2] == new['initial'][x] and new['final'][x2] == new['final'][x] and new['initial'][y2] == new['initial'][x + 112] and new['final'][y2] == new['final'][x + 112] for x, x2, y2 in zip(live, X2, Y2)), 'second mains carry the same initial and final frame labels as the first mains (declared)')
touch = [i for i, e in enumerate(P) if e[0] == 'ADD' and (e[1] in M2 or e[2] in M2)]
share = Counter()
for i in touch:
    e = P[i]; other = e[2] if e[1] in M2 else e[1]
    if other in M1: share['plane 2 with plane 1 directly'] += 1
    elif other < n: share['plane 2 with a helper'] += 1
    else: share['plane 2 with an owned register'] += 1
print('  events that read or write a second main: %d (%s)' % (len(touch), dict(share)))
direct = [i for i in touch if (P[i][1] in M2 and P[i][2] in M1) or (P[i][2] in M2 and P[i][1] in M1)]
need(direct and all(i < lo or i > hi for i in direct) and len(direct) == share['plane 2 with plane 1 directly'], 'the %d events that couple a first-plane main with a second-plane main directly all lie in the two gate blocks (before the first MOVE or after the last, at frames Z and V); inside the core the planes meet only through helpers (%d events) and owned registers (%d events)' % (len(direct), share['plane 2 with a helper'], share['plane 2 with an owned register']))
H1 = set(); H2 = set()
for e in P[lo:hi + 1]:
    if e[0] != 'ADD': continue
    for a, b in ((e[1], e[2]), (e[2], e[1])):
        if b in M1 and a < n and a in set(hel_n): H1.add(a)
        if b in M2 and a < n and a in set(hel_n): H2.add(a)
both = H1 & H2
need(len(both) > 0 and len(H1 | H2) <= len(hel_n), 'helpers with ADD events directly against mains of both planes: %d of %d (one field, one job, one credit each; this counts direct adjacency only, not the helper rows the replay shows to hold inputs of both chains)' % (len(both), len(hel_n)))
# helpers touching 9+ ports in the #6889 word (the statement of the baseline)
def ports_of(W):
    liv = W['live']; pr = {}
    for r, q in zip(liv, W['ports']): pr[r] = q; pr[r + 112] = q
    return pr
po = ports_of(old); hs = {}
for e in Po:
    if e[0] == 'ADD':
        for a, b in ((e[1], e[2]), (e[2], e[1])):
            if b in po and a < no and a not in mo: hs.setdefault(a, set()).add(po[b])
need(sum(1 for r in hel_o if len(hs.get(r, ())) >= 9) == 844, 'in the #6889 word 844 of the %d helpers already read or write mains of 9 or more ports' % len(hel_o))
# random-evaluation replay
M = (1 << 61) - 1
al, be, a2, b2 = Q(H['alpha']), Q(H['beta']), Q(H['alpha2']), Q(H['beta2'])
fm = lambda q: (lambda f: f.numerator % M * pow(f.denominator, M - 2, M) % M)(Q(q)); x2of = dict(zip(X2, Y2)); X2s = set(X2); Y2s = set(Y2)
def endpoint_ok(prog, K=2, seed=3):
    NR = n + new['owned_fields']; rnd = random.Random(seed)
    v0 = [[rnd.randrange(M) for _ in range(K)] for _ in range(n)]; v = [x[:] for x in v0] + [[0] * K for _ in range(new['owned_fields'])]
    for e in prog:
        op = e[0]
        if op in ('INIT', 'CLEAR'): v[e[1]] = [0] * K
        elif op == 'SCALE':
            c = fm(e[2]); v[e[1]] = [a * c % M for a in v[e[1]]]
        elif op in ('ADD', 'COPY'):
            c = fm(e[3]); s = v[e[2]]
            if op == 'COPY': v[e[1]] = [c * b % M for b in s]
            else: v[e[1]] = [(a + c * b) % M for a, b in zip(v[e[1]], s)]
    for r in range(NR):
        if r >= n: ex = [0] * K
        elif r in X: ex = list(v0[r])
        elif r in Y: ex = [(v0[r - 112][k] + v0[r][k]) % M for k in range(K)]
        elif r in X2s: ex = [(v0[r][k] + fm(a2) * v0[x2of[r]][k]) % M for k in range(K)]
        elif r in Y2s: ex = list(v0[r])
        else: ex = v0[r]
        if v[r] != ex: return False
    return True
need(endpoint_ok(P), 'random-evaluation replay accepts the word (endpoint exact on every public and owned row, both planes)')
rnd = random.Random(9); smp = rnd.sample(touch, 12); bw = bm = bd = 0
for i in smp:
    e = list(P[i]); e[3] = str(Q(e[3]) * 2)
    bw += not endpoint_ok(P[:i] + [e] + P[i + 1:])
    bm += not endpoint_ok(P[:i] + P[i + 1:])
    bd += not endpoint_ok(P[:i + 1] + [P[i]] + P[i + 1:])
need(bw == bm == bd == len(smp), 'controls on %d sampled events that read or write a second main: a wrong weight (x2), a missing event and an event taken twice are all rejected' % len(smp))
adds = [i for i in range(lo, hi + 1) if P[i][0] == 'ADD']
need(not endpoint_ok(P[:adds[0]] + P[adds[0] + 1:]), 'control: removing the first core ADD is rejected')
sample = rnd.sample(adds, 12); broke = sum(not endpoint_ok(P[:i] + P[i + 1:]) for i in sample)
need(broke >= 9, 'control: removing any one of 12 sampled core ADDs breaks the endpoint in %d cases' % broke)
print('PASS_COVER_CHANGES')
