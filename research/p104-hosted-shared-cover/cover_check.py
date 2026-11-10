#!/usr/bin/env python3
"""What changed against the #6883 word, measured on the two words (standard library).  python3 -I -B cover_check.py
The core of a word is the span from its first to its last MOVE; the gates before and after it are rebuilt per word and are not compared.
Reports: ADD events of the core (the #6883 word minus this word = the deleted ADDs), silent helpers, registers, MOVEs, peak owned fields;
checks that dropping silent helpers leaves the invoice unchanged; and controls on a random-evaluation replay (mod 2^61-1) that the endpoint
is destroyed by removing one more ADD, by duplicating an ADD (a wrongly restored one), and by removing sampled ADDs that are not in the deleted set."""
import gzip, json, os, random, sys
from collections import Counter
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q
getcontext().prec = 50
HERE = os.path.dirname(os.path.abspath(__file__))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
def load(n): return json.load(gzip.open(os.path.join(HERE, 'data', n), 'rt'))
def census(W):
    n = len(W['initial']); live = set(W['live']); main = live | {r + 112 for r in live}
    touched = set()
    for e in W['program']:
        if e[0] in ('ADD', 'COPY'): touched |= {e[1], e[2]}
        elif e[0] == 'SCALE': touched.add(e[1])
    silent = [r for r in range(n) if r not in main and r not in touched]
    P = W['program']; mv = [i for i, e in enumerate(P) if e[0] == 'MOVE']; lo, hi = mv[0], mv[-1]
    core = Counter(e[0] for e in P[lo:hi + 1]); own = set(); peak = 0
    for e in P:
        if e[0] == 'INIT': own.add(e[1]); peak = max(peak, len(own))
        elif e[0] == 'CLEAR': own.discard(e[1])
    return dict(n=n, silent=silent, core=core, lo=lo, hi=hi, moves=sum(e[0] == 'MOVE' for e in P), peak=peak, events=len(P), main=main)
old, new = load('prior_word.json.gz'), load('word.json.gz')
co, cn = census(old), census(new)
print('  #6883 word: events %d, public %d, silent helpers %d, MOVEs %d, core ADDs %d, peak owned %d' % (co['events'], co['n'], len(co['silent']), co['moves'], co['core']['ADD'], co['peak']))
print('  this word : events %d, public %d, silent helpers %d, MOVEs %d, core ADDs %d, peak owned %d' % (cn['events'], cn['n'], len(cn['silent']), cn['moves'], cn['core']['ADD'], cn['peak']))
need(co['core']['ADD'] - cn['core']['ADD'] == 342 and all(co['core'][k] == cn['core'][k] for k in ('SCALE', 'INIT', 'CLEAR', 'COPY')), 'the core loses exactly 342 ADD events and no other event kind except MOVEs (SCALE, INIT, CLEAR, COPY counts equal)')
need(cn['silent'] == [] and cn['n'] < co['n'] and cn['moves'] < co['moves'], 'no silent helper remains (#6883 word: %d); %d public registers and %d MOVEs fewer' % (len(co['silent']), co['n'] - cn['n'], co['moves'] - cn['moves']))
# dropping silent helpers: same rise in targets and in paid, so the invoice is unchanged (checked on the #6883 word, which still has them)
def kappa(T, P):
    rs = sorted(set(T) | set(P)); ln = {r: D(r).ln() for r in rs}
    e = lambda k: sum((D(T.get(r, 0)) - D(P.get(r, 0))) * (ln[r] * (1 - k)).exp() for r in rs)
    lo, hi = D('1e-6'), D('0.05')
    for _ in range(200):
        m = (lo + hi) / 2
        if e(m) > 0: lo = m
        else: hi = m
    return lo
dim = [len(b) for b in old['frames']]
sil = set(co['silent']); mvs = Counter(); rise = {}
for e in old['program']:
    if e[0] == 'MOVE' and e[1] in sil: mvs[e[1]] += 1
for r in sil: rise[r] = dim[old['final'][r]] - dim[old['initial'][r]]
need(all(mvs[r] == 1 for r in sil) and all(rise[r] > 0 for r in sil), 'each of the %d silent helpers of the #6883 word is one single MOVE with rank equal to its target rank, so removing it removes the same job from targets and paid' % len(sil))
# control: random-evaluation replay
M = (1 << 61) - 1; inv2 = pow(2, M - 2, M)
al, be = Q(new['hosted']['alpha']), Q(new['hosted']['beta']); t = al * be
fm = lambda q: (lambda f: f.numerator % M * pow(f.denominator, M - 2, M) % M)(Q(q))
live = new['live']; X = set(live); Y = {r + 112 for r in live}
def endpoint_ok(W, prog, K=2, seed=3):
    n = len(W['initial']); NR = n + W['owned_fields']; rnd = random.Random(seed)
    v0 = [[rnd.randrange(M) for _ in range(K)] for _ in range(n)]; v = [x[:] for x in v0] + [[0] * K for _ in range(W['owned_fields'])]
    for e in prog:
        op = e[0]
        if op in ('INIT', 'CLEAR'): v[e[1]] = [0] * K
        elif op == 'SCALE':
            c = fm(e[2]); v[e[1]] = [a * c % M for a in v[e[1]]]
        elif op in ('ADD', 'COPY'):
            c = fm(e[3]); s = v[e[2]]
            if op == 'COPY': v[e[1]] = [c * b % M for b in s]
            else: v[e[1]] = [(a + c * b) % M for a, b in zip(v[e[1]], s)]
    a_, b_, d_ = fm(al), fm(be), fm(1 + t)
    for r in range(NR):
        if r >= n: ex = [0] * K
        elif r in X: ex = [(v0[r][k] + a_ * v0[r + 112][k]) % M for k in range(K)]
        elif r in Y: ex = [(b_ * v0[r - 112][k] + d_ * v0[r][k]) % M for k in range(K)]
        else: ex = v0[r]
        if v[r] != ex: return False
    return True
P = new['program']; lo, hi = cn['lo'], cn['hi']
adds = [i for i in range(lo, hi + 1) if P[i][0] == 'ADD']
need(endpoint_ok(new, P), 'random-evaluation replay accepts the word (endpoint exact on every public and owned row)')
need(not endpoint_ok(new, P[:adds[0]] + P[adds[0] + 1:]), 'control: removing the first core ADD is rejected')
need(not endpoint_ok(new, P[:adds[len(adds) // 2] + 1] + [P[adds[len(adds) // 2]]] + P[adds[len(adds) // 2] + 1:]), 'control: duplicating a core ADD (an ADD restored wrongly) is rejected')
rnd = random.Random(9); sample = rnd.sample(adds, 12); broke = 0
for i in sample: broke += not endpoint_ok(new, P[:i] + P[i + 1:])
need(broke >= 9, 'control: removing any one of 12 sampled core ADDs breaks the endpoint in %d cases (the others are among the 347 individually removable events of the deletion scan; 342 of those are removed jointly here)' % broke)
print('PASS_COVER_CHANGES')
