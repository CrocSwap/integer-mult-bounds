#!/usr/bin/env python3
"""What the word is made of, counted on the word and compared with the #6902 word (standard library).  python3 -I -B cover_check.py
Counts the two port types (96 with second mains, 8 hosted), the events that touch second mains or the hosted ports, and runs controls on a random-evaluation replay (mod 2^61-1):
a wrong port type, a swapped assignment of two ports, and for sampled events a wrong weight (x2), a missing event and an event taken twice, are all rejected."""
import gzip, json, os, random
from collections import Counter
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
def load(n): return json.load(gzip.open(os.path.join(HERE, 'data', n), 'rt'))
new, old = load('word.json.gz'), load('prior_word_6902.json.gz')
H = new['hosted']; X2 = H['X2']; Y2 = H['Y2']; live = new['live']; DP = H['Dports']
X = set(live); Y = {r + 112 for r in live}; M1 = X | Y; M2 = set(X2) | set(Y2); n = len(new['initial'])
BP = [i for i in range(104) if i not in set(DP)]
P = new['program']; lo = next(i for i, e in enumerate(P) if e[0] == 'MOVE'); hi = max(i for i, e in enumerate(P) if e[0] == 'MOVE'); Po = old['program']
hel_n = [r for r in range(n) if r not in M1 and r not in M2]
no = len(old['initial']); mo = set(old['live']) | {r + 112 for r in old['live']} | set(old['hosted']['X2']) | set(old['hosted']['Y2'])
print('  #6902 word: events %d, public %d, MOVEs %d' % (len(Po), no, sum(e[0] == 'MOVE' for e in Po)))
print('  this word : events %d, public %d (%d mains, %d helpers), MOVEs %d' % (len(P), n, len(M1) + len(M2), len(hel_n), sum(e[0] == 'MOVE' for e in P)))
need(len(DP) == 96 and len(BP) == 8 and len(M2) == 192 and len(M1 | M2) == 400 and n == 1367 and len(hel_n) == 967, 'two port types: 96 ports with second mains and 8 hosted ports (no second mains): 400 mains, 967 helpers, 1367 public (the #6902 word: 416 mains, 959 helpers, 1375 public)')
mv_by = Counter()
for e in P:
    if e[0] == 'MOVE': mv_by['second main' if e[1] in M2 else 'first main' if e[1] in M1 else 'owned' if e[1] >= n else 'helper'] += 1
need(mv_by['first main'] > mv_by['second main'] > 0, 'each register pays its own moves: first-plane mains %d MOVEs, second-plane mains %d MOVEs (no move is shared or fused)' % (mv_by['first main'], mv_by['second main']))
need(all(new['initial'][x2] == new['initial'][live[i]] and new['final'][x2] == new['final'][live[i]] and new['initial'][y2] == new['initial'][live[i] + 112] and new['final'][y2] == new['final'][live[i] + 112] for i, x2, y2 in zip(DP, X2, Y2)), 'second mains carry the same initial and final frame labels as the first mains of their port (declared)')
touch = [i for i, e in enumerate(P) if e[0] == 'ADD' and (e[1] in M2 or e[2] in M2)]
hmains = {live[i] for i in BP} | {live[i] + 112 for i in BP}
htouch = [i for i, e in enumerate(P) if e[0] == 'ADD' and (e[1] in hmains or e[2] in hmains)]
direct = [i for i in touch if (P[i][1] in M2 and P[i][2] in M1) or (P[i][2] in M2 and P[i][1] in M1)]
print('  events that read or write a second main: %d; events that read or write a hosted-port main: %d' % (len(touch), len(htouch)))
incore = [i for i in direct if lo <= i <= hi]
port_of = {}
for i_, r in enumerate(live): port_of[r] = i_; port_of[r + 112] = i_
hp = {port_of[P[i][2] if P[i][1] in M2 else P[i][1]] for i in incore}
need(len(direct) == 397 and len(incore) == 12 and hp <= set(BP), 'events that couple a second-plane main with a first-plane main directly: %d, of which %d lie in the two gate blocks (frames Z and V) and %d lie inside the core; all %d of the core events pair a second main of a two-chain port with a main of a HOSTED port (ports %s): a new fact against #6902, where none lay in the core' % (len(direct), len(direct) - len(incore), len(incore), len(incore), sorted(hp)))
# cross-type traffic, by an explicit definition: the type of a main is the type of its port (two-chain or hosted)
port = {}; role = {}
for i_, r in enumerate(live): port[r] = i_; role[r] = 'X'; port[r + 112] = i_; role[r + 112] = 'Y'
for i_, a_, b_ in zip(DP, X2, Y2): port[a_] = i_; role[a_] = 'X2'; port[b_] = i_; role[b_] = 'Y2'
DPs = set(DP); typ = lambda r: 'two-chain' if port[r] in DPs else 'hosted'
cross = [(k, e) for k, e in enumerate(P) if e[0] in ('ADD', 'COPY') and e[1] in port and e[2] in port and typ(e[1]) != typ(e[2])]
cross2 = [(k, e) for k, e in cross if role[e[1]] in ('X2', 'Y2') or role[e[2]] in ('X2', 'Y2')]
hD = set(); hH = set()
for e in P:
    if e[0] == 'ADD':
        for a_, b_ in ((e[1], e[2]), (e[2], e[1])):
            if b_ in port and a_ < n and a_ not in port: (hD if typ(b_) == 'two-chain' else hH).add(a_)
need(len(cross) == 180 and len(cross2) == 96 and sum(1 for k, e in cross2 if e[4] != 127) == 16, 'cross-type main-main traffic (definition: an ADD or COPY whose destination and source are both mains and whose ports have different types): %d events, of which %d involve a second main (16 of those at a frame other than 127); legal (frame law clean: common chart); the 12 core events counted above are the subset of second-main to first-main couplings that lie inside the core and pair with a hosted port' % (len(cross), len(cross2)))
need(len(hD & hH) == 279, '%d helpers have ADD events directly against mains of both port types (the 8 hosted ports share 279 helpers with the two-chain ports)' % len(hD & hH))
rq = [({r: Q(1)} if r < n else {}) for r in range(n + new['owned_fields'])]; hold = 0
for e in P:
    op = e[0]; r = e[1]
    if op in ('INIT', 'CLEAR'): rq[r] = {}
    elif op == 'SCALE': rq[r] = {k: v * Q(e[2]) for k, v in rq[r].items()}
    elif op in ('ADD', 'COPY'):
        if op == 'COPY': rq[r] = {}
        R_ = rq[r]
        for k, v in rq[e[2]].items():
            t = R_.get(k, 0) + Q(e[3]) * v
            if t: R_[k] = t
            else: R_.pop(k, None)
        if r in port and any(k in port and typ(k) != typ(r) for k in R_): hold += 1
foreign = sum(1 for r in port if any(k in port and typ(k) != typ(r) for k in rq[r]))
need(foreign == 0 and hold == 3053, 'the endpoint rows of all %d mains hold no input of a port of the other type; transiently a main holds a foreign-type input after %d events, and it cancels' % (len(port), hold))
# random-evaluation replay with the endpoint of each port type; types may be altered for the controls
M = (1 << 61) - 1
al, be, a2 = Q(H['alpha']), Q(H['beta']), Q(H['alpha2'])
fm = lambda q: (lambda f: f.numerator % M * pow(f.denominator, M - 2, M) % M)(Q(q)); X2s = set(X2); Y2s = set(Y2)
def endpoint_ok(prog, dports=DP, K=2, seed=3):
    NR = n + new['owned_fields']; rnd = random.Random(seed); dX = {live[i] for i in dports}; x2of = dict(zip(X2, Y2))
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
        elif r in X: ex = list(v0[r]) if r in dX else [(v0[r][k] + fm(al) * v0[r + 112][k]) % M for k in range(K)]
        elif r in Y: ex = [(v0[r - 112][k] + v0[r][k]) % M for k in range(K)] if r - 112 in dX else [(fm(be) * v0[r - 112][k] + fm(1 + al * be) * v0[r][k]) % M for k in range(K)]
        elif r in X2s: ex = [(v0[r][k] + fm(a2) * v0[x2of[r]][k]) % M for k in range(K)]
        elif r in Y2s: ex = list(v0[r])
        else: ex = v0[r]
        if v[r] != ex: return False
    return True
need(endpoint_ok(P), 'random-evaluation replay accepts the word (endpoint exact on every public and owned row, both port types)')
need(not endpoint_ok(P, dports=DP[1:]), 'control: wrong port type: one two-chain port declared hosted fails (the endpoint rows of that port differ)')
need(not endpoint_ok(P, dports=sorted(DP[1:] + [BP[0]])), 'control: swapped assignment: a two-chain port and a hosted port exchanged in the type list fails')
rnd = random.Random(9); smp = rnd.sample(touch, 8) + rnd.sample(htouch, 8); bw = bm = bd = 0
for i in smp:
    e = list(P[i]); e[3] = str(Q(e[3]) * 2)
    bw += not endpoint_ok(P[:i] + [e] + P[i + 1:])
    bm += not endpoint_ok(P[:i] + P[i + 1:])
    bd += not endpoint_ok(P[:i + 1] + [P[i]] + P[i + 1:])
need(bw == bm == bd == len(smp), 'controls on %d sampled events (8 that read or write a second main, 8 that read or write a hosted-port main): a wrong weight (x2), a missing event and an event taken twice are all rejected' % len(smp))
adds = [i for i in range(lo, hi + 1) if P[i][0] == 'ADD']
need(not endpoint_ok(P[:adds[0]] + P[adds[0] + 1:]), 'control: removing the first core ADD is rejected')
sample = rnd.sample(adds, 12); broke = sum(not endpoint_ok(P[:i] + P[i + 1:]) for i in sample)
need(broke >= 9, 'control: removing any one of 12 sampled core ADDs breaks the endpoint in %d cases' % broke)
print('PASS_COVER_CHANGES')
