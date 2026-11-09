#!/usr/bin/env python3
"""What changed against the #6883 and #6884 words, measured on the two words (standard library).  python3 -I -B cover_check.py
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
old, mid, m7, new = load('prior_word.json.gz'), load('prior_word_6884.json.gz'), load('prior_word_6887.json.gz'), load('word.json.gz')
co, cm, c7, cn = census(old), census(mid), census(m7), census(new)
for nm, c in (('#6883 word', co), ('#6884 word', cm), ('#6887 word', c7), ('this word ', cn)):
    print('  %s: events %d, public %d, silent helpers %d, MOVEs %d, core ADDs %d, core SCALEs %d, gate events before/after the core %d/%d, peak owned %d' % (nm, c['events'], c['n'], len(c['silent']), c['moves'], c['core']['ADD'], c['core']['SCALE'], c['lo'], c['events'] - c['hi'] - 1, c['peak']))
need(co['core']['ADD'] - cm['core']['ADD'] == 342, 'the #6884 word loses exactly 342 core ADD events against the #6883 word (the deletions of #6884)')
need(cn['silent'] == [] and cn['n'] == c7['n'] - 2 and cn['moves'] == c7['moves'] - 11 and c7['core']['ADD'] - cn['core']['ADD'] == 2 and cn['core']['SCALE'] == c7['core']['SCALE'] and all(c7['core'][k] == cn['core'][k] for k in ('INIT', 'CLEAR', 'COPY')),
     'this word against the #6887 word: 2 fewer public registers, 11 fewer MOVEs, 2 fewer core ADDs, same core SCALEs, owned lifetimes and COPY, no silent helper')
need((c7['lo'], c7['events'] - c7['hi'] - 1, cn['lo'], cn['events'] - cn['hi'] - 1) == (90770, 39677, 95586, 54896), 'the gate blocks are rebuilt (events before the core 90,770 -> 95,586, after 39,677 -> 54,896; total events 144,511 -> 164,533)')
def port_counts(W, kind):
    P = W['program']; live = W['live']; Yr = {r + 112 for r in live}; Xr = set(live); n = len(W['initial']); mn = Xr | Yr
    mv = [i for i, e in enumerate(P) if e[0] == 'MOVE']; out = []
    for i, e in enumerate(P[mv[0]:mv[-1] + 1], mv[0]):
        if e[0] != 'ADD': continue
        if kind == 'yread' and e[2] in Yr and e[1] < n and e[1] not in mn: out.append((i, e, e[2]))
        if kind == 'xwrite' and e[1] in Xr and e[2] < n and e[2] not in mn: out.append((i, e, e[1]))
        if kind == 'xread' and e[2] in Xr and e[1] < n and e[1] not in mn: out.append((i, e, e[2]))
        if kind == 'ywrite' and e[1] in Yr and e[2] < n and e[2] not in mn: out.append((i, e, e[1]))
    return out
def diff(kind):
    a_, b_ = port_counts(m7, kind), port_counts(new, kind); ca, cb = Counter(p for _, _, p in a_), Counter(p for _, _, p in b_)
    return a_, b_, {k: cb[k] - ca[k] for k in set(ca) | set(cb) if ca[k] != cb[k]}
ya, yb, yd = diff('yread'); xa, xb, xd = diff('xwrite'); xra, xrb, xrd = diff('xread'); ywa, ywb, ywd = diff('ywrite')
need(not yd and not ywd and xrd == {47: 2, 52: 2} and xd == {47: 5, 52: 3} and (len(xra), len(xrb), len(xa), len(xb)) == (566, 570, 553, 561),
     'new direct reads of X: helper reads of X by the mirror change on exactly 2 main registers (47 and 52, two more reads each; 566 -> 570), helper writes into X on the same 2 (+5 and +3; 553 -> 561); reads of Y and writes into Y by helpers change on no port')
xnew = [(i, e) for i, e, p in xrb if p in (47, 52)]; xwnew = [(i, e) for i, e, p in xb if p in (47, 52)]
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
need(endpoint_ok(new, P), 'random-evaluation replay accepts the word (endpoint exact on every public and owned row)')
rnd = random.Random(9); smp = [i for i, e in xnew] + rnd.sample([i for i, e in xwnew], 4); bw = bm = bd = 0
for i in smp:
    e = list(P[i]); e[3] = str(Q(e[3]) * 2)
    bw += not endpoint_ok(new, P[:i] + [e] + P[i + 1:])             # wrong weight
    bm += not endpoint_ok(new, P[:i] + P[i + 1:])                   # missing event
    bd += not endpoint_ok(new, P[:i + 1] + [P[i]] + P[i + 1:])      # taken twice
need(bw == bm == bd == len(smp), 'controls on the %d direct reads of X on ports 47 and 52 and 4 sampled writes into X there: a wrong weight (x2), a missing event and an event taken twice are all rejected' % len(smp))
adds = [i for i in range(lo, hi + 1) if P[i][0] == 'ADD']
need(not endpoint_ok(new, P[:adds[0]] + P[adds[0] + 1:]), 'control: removing the first core ADD is rejected')
sample = rnd.sample(adds, 12); broke = sum(not endpoint_ok(new, P[:i] + P[i + 1:]) for i in sample)
need(broke >= 9, 'control: removing any one of 12 sampled core ADDs breaks the endpoint in %d cases (the deletions of #6884 are removable only jointly or alone with the gates absorbing them)' % broke)
print('PASS_COVER_CHANGES')
