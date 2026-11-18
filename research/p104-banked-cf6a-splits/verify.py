#!/usr/bin/env python3
"""Exact check of the split banked circuit on the #7700 cf6a word (standard library only).

1. Authenticate every package asset (ASSETS.json).
2. Authenticate the #7700 cf6a source word (canonical SHA-256 pin).
3. Locality (every donor is cocharted with its reader) and an acyclic schedule of data/CIRCUIT.json.gz.
4. Every paid edge joins GF(2)-nested charts with positive rank; the symplectic rank of T_b T_a^-1 equals |dim b - dim a|.
5. For every chart pair that is not a MOVE of the word, an exact Gaussian state simulation of T_b T_a^-1 spreads every
   one of the 512 columns over exactly 2^r basis states of equal modulus (a non-nested control pair is rejected).
6. Exact rational outputs: every main output equals the word's; every helper, including the three fresh split
   roles 1501-1503, returns its own normalized input.
7. Invoice on the literal 16-call caller and a certified enclosure of the crossing (PRICEKIT).
usage: python3.12 -I -B verify.py [--skip-columns]"""
import sys, os, gzip, json, hashlib
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools'))
from bank import fold, Net, schedule, price_net, hist, pk
from exval import exact_values
import nest, phys, gauss

def enc(v): return json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
assets = json.load(open(os.path.join(HERE, 'ASSETS.json')))
for row in assets['files']:
    with open(os.path.join(HERE, row['path']), 'rb') as fh:
        if hashlib.sha256(fh.read()).hexdigest() != row['sha256']: raise SystemExit('FAIL: asset hash ' + row['path'])
print('1. %d package assets authenticated' % len(assets['files']))
def need(c, m):
    if not c: raise SystemExit('FAIL: ' + m)

W = json.load(gzip.open(os.path.join(HERE, 'source', 'WORD.json.gz'), 'rt'))
need(hashlib.sha256(enc(W)).hexdigest() == 'ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472', 'cf6a (#7700) word pin')
print('2. #7700 cf6a word authenticated: %d events, SHA-256 ae62d5d8bef6f714' % len(W['program']))
fr = W['frames']; dim = [len(f) for f in fr]

C = json.load(gzip.open(os.path.join(HERE, 'data', 'CIRCUIT.json.gz'), 'rt'))
net = Net(C['first'], C['initial'], C['final'], {int(k): tuple(v) for k, v in C['moves'].items()},
          {int(k): {int(t): Q(c) for t, c in row.items()} for k, row in C['forms'].items()})
schedule(net); print('3. locality + acyclic schedule: PASS (%d paid edges, %d public roles)' % (len(net.moves), len(net.init)))
pairs = sorted(set(net.moves.values()))
for a, b in pairs:
    r = nest.trank(fr, a, b)
    need(r is not None and r > 0, 'nested positive pair %s' % ((a, b),))
    need(phys.trank(fr[a], fr[b]) == r, 'symplectic rank %s' % ((a, b),))
print('4. %d distinct chart pairs nested, positive rank, symplectic rank = |dim diff|: PASS' % len(pairs))
wordpairs = {(e[2], e[3]) for e in W['program'] if e[0] == 'MOVE'}
newp = [p for p in pairs if p not in wordpairs]
if '--skip-columns' not in sys.argv:
    for a, b in newp:
        need(gauss.column_rank(fr[a], fr[b]) == abs(dim[a] - dim[b]), 'Gaussian column rank %s' % ((a, b),))
    ca, cb = next((a, b) for a in range(len(fr)) for b in range(a + 1, len(fr)) if dim[a] == dim[b] > 0 and not nest.nested(fr, a, b))
    need(gauss.column_rank(fr[ca], fr[cb]) != 0, 'control: a non-nested equal-dimension pair must not be rank 0')
    print('5. %d pairs outside the #7700 word: exact Gaussian column rank = |dim diff| on all 512 columns: PASS (control rejects %d->%d)' % (len(newp), ca, cb))
h = W['hosted']; mains = set(W['live']) | {r + 112 for r in W['live']} | set(h['X2']) | set(h['Y2'])
ref = fold(W); EVr = exact_values(ref); EVc = exact_values(net)
need(all(EVc[net.first + r] == EVr[ref.first + r] and net.final[r] == W['final'][r] for r in mains), 'main outputs')
need(all(EVc[net.first + r] == {r: Q(1)} for r in range(len(net.init)) if r not in mains), 'helper identity')
print('6. EXACT: %d main outputs equal the #7700 word; %d helpers return their own input: PASS' % (len(mains), len(net.init) - len(mains)))
pr, inv = price_net(W, net, dim, 30)
k = pr['kappa']; need(k['status'] == 'OK', 'certified unique crossing')
print('7. paid/native %d, paid %d, targets %d, S %d; crossing in (%s, %s)' % (
    sum(hist(net, dim).values()), pr['paid_jobs'], pr['targets'], pr['S'], str(k['lo'])[:20], str(k['hi'])[:20]))
claim = Q('0.0037427697512')
need(Q(str(k['lo'])) > claim, 'claim below certified lower end')
print('PASS: kappa >= 0.0037427697512 on the stated invoice')
