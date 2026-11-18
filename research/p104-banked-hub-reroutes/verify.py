#!/usr/bin/env python3
"""Exact check of the hub-rerouted banked circuit (standard library only).

1. Rebuild the #7669 source word from K372-2 and the twelve published edits; check both SHA-256 pins.
2. Load data/CIRCUIT.json.gz (paid edges with rational source forms, public boundary).
3. Locality (every donor is cocharted with its reader) and an acyclic schedule.
4. Every paid edge joins GF(2)-nested charts with positive rank; the symplectic rank of T_b T_a^-1 equals |dim b - dim a|.
5. For every chart pair that is not a MOVE of the #7669 word, an exact Gaussian state simulation of T_b T_a^-1 spreads
   every one of the 512 columns over exactly 2^r basis states of equal modulus, r = |dim b - dim a|.
6. Exact rational outputs: every main output equals the #7669 word's; every helper (including fresh role 1501)
   returns its own normalized input.
7. Invoice on the literal 16-call #7669 caller and a certified enclosure of the crossing (PRICEKIT).
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

base = json.load(gzip.open(os.path.join(HERE, 'source', 'K372-2-WORD.json.gz'), 'rt'))
ed = json.load(open(os.path.join(HERE, 'source', '7669-EDIT.json')))
need(hashlib.sha256(enc(base)).hexdigest() == ed['source'], 'K372-2 source pin')
prog, cur = [], 0
for e in ed['edits']:
    need(base['program'][e['start']:e['stop']] == e['before'], 'edit preimage')
    prog += base['program'][cur:e['start']] + e['after']; cur = e['stop']
W = dict(base, program=prog + base['program'][cur:])
need(hashlib.sha256(enc(W)).hexdigest() == ed['candidate'] == 'ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d', '#7669 word pin')
print('#7669 word rebuilt: %d events, SHA-256 %s' % (len(W['program']), ed['candidate'][:16]))
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
    need(gauss.column_rank(fr[912], fr[913]) != 0, 'control: non-nested 912->913 must not be rank 0')
    print('5. %d pairs outside the #7669 word: exact Gaussian column rank = |dim diff| on all 512 columns: PASS (control rejects 912->913)' % len(newp))
h = W['hosted']; mains = set(W['live']) | {r + 112 for r in W['live']} | set(h['X2']) | set(h['Y2'])
ref = fold(W); EVr = exact_values(ref); EVc = exact_values(net)
need(all(EVc[net.first + r] == EVr[ref.first + r] and net.final[r] == W['final'][r] for r in mains), 'main outputs')
need(all(EVc[net.first + r] == {r: Q(1)} for r in range(len(net.init)) if r not in mains), 'helper identity')
print('6. EXACT: %d main outputs equal the #7669 word; %d helpers return their own input: PASS' % (len(mains), len(net.init) - len(mains)))
pr, inv = price_net(W, net, dim, 30)
k = pr['kappa']; need(k['status'] == 'OK', 'certified unique crossing')
print('7. paid/native %d, paid %d, targets %d, S %d; crossing in (%s, %s)' % (
    sum(hist(net, dim).values()), pr['paid_jobs'], pr['targets'], pr['S'], str(k['lo'])[:20], str(k['hi'])[:20]))
claim = Q('0.0037291618601')
need(Q(str(k['lo'])) > claim, 'claim below certified lower end')
print('PASS: kappa >= 0.0037291618601 on the stated invoice')
