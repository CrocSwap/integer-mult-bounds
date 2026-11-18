#!/usr/bin/env python3
"""Note check: two hub reroutes on the #7717 banked graph (standard library only).

This is NOT a full certificate. The package's certify.py cannot check #7717's helper-removal boundary (its graph has
1,470 public roles, against 1,504 for the cf6a word), so the reroutes are checked only against #7717's own graph:
  1. the graph is the one #7717 prices (canonical SHA-256 equals results/application.json graph_sha256);
  2. hubbuild.py rebuilds both reroutes from the two recorded hits, and the result equals REROUTES.json exactly;
  3. locality and an acyclic schedule; every paid edge GF(2)-nested with positive rank and symplectic rank = |dim diff|
     (the graph's own frames);
  4. EXACT rational equality of all 1,470 outputs with the unmodified #7717 graph;
  5. pricing: #7717's published 16-call invoice reproduces its bracket; adding 16 x the paid change per native gives the
     note's crossing. Targets are unchanged because every boundary is unchanged.
usage: python3.12 -I -B note-7717/check.py"""
import sys, os, json, hashlib
from collections import Counter
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from bank import load, load_graph, Net, schedule, transpose, hist, pk
from exval import exact_values
import nest, phys, hubbuild


def need(c, m):
    if not c: raise SystemExit('FAIL: ' + m)


G = load(os.path.join(HERE, 'GRAPH-7717.json.gz'))
A = load(os.path.join(HERE, 'APPLICATION-7717.json'))
D = load(os.path.join(HERE, 'REROUTES.json'))
sha = hashlib.sha256(json.dumps(G, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
need(sha == D['base_canonical_sha256'] == A['graph_sha256'], 'graph pin')
print('1. #7717 graph authenticated: canonical SHA-256 %s (= its application receipt)' % sha[:16])
fr = G['frames']; dim = [len(f) for f in fr]
base = load_graph(os.path.join(HERE, 'GRAPH-7717.json.gz'))

new = base.copy(); new.forms = dict(base.forms)
for k, (before, after) in D['moves_before_after'].items():
    need(list(base.moves[int(k)]) == before, 'diff base move %s' % k); new.moves[int(k)] = tuple(after)
for k, row in D['forms_after'].items():
    new.forms[int(k)] = {int(t): Q(c) for t, c in row.items()}

net = base
for h in D['hub_reroutes']:
    nn = net if h['dir'] == 'forward' else transpose(net)
    b = hubbuild.build(nn, exact_values(nn), h)
    need(b is not None, 'hub rebuild %s/%s' % (h['e1'], h['e2']))
    net = b if h['dir'] == 'forward' else transpose(b)
need(net.moves == new.moves and net.forms == new.forms, 'rebuilt circuit differs from REROUTES.json')
print('2. hubbuild.py rebuilds both reroutes from the recorded hits; equal to REROUTES.json (%d moves, %d forms changed)'
      % (len(D['moves_before_after']), len(D['forms_after'])))

schedule(new)
for a, b in set(new.moves.values()):
    r = nest.trank(fr, a, b)
    need(r is not None and r > 0, 'nesting %s' % ((a, b),)); need(phys.trank(fr[a], fr[b]) == r, 'symplectic %s' % ((a, b),))
print('3. locality + acyclic schedule; %d paid edges nested, symplectic rank = |dim diff|: PASS' % len(new.moves))

E0, E1 = exact_values(base), exact_values(new); n = len(base.init)
need(new.init == base.init and new.final == base.final, 'boundary')
need(all(E1[new.first + r] == E0[base.first + r] for r in range(n)), 'outputs')
print('4. EXACT: all %d outputs equal the unmodified #7717 graph' % n)

h0, h1 = hist(base, dim), hist(new, dim)
delta = {r: h1[r] - h0[r] for r in sorted(set(h0) | set(h1)) if h1[r] != h0[r]}
need(delta == {2: 2, 3: -2, 6: -2, 7: 2}, 'paid change %s' % delta)
inv = A['invoice']; calls = A['caller']['calls']; need(calls == 16, 'calls')
T = {int(r): v for r, v in inv['targets'].items()}; P = {int(r): v for r, v in inv['paid'].items()}
p0 = pk.price(dict(T=T, P=P), 30)
need(Q(str(p0['kappa']['lo'])) >= Q(A['bracket'][0]) - Q(1, 10 ** 14) and Q(str(p0['kappa']['hi'])) <= Q(A['bracket'][1]) + Q(1, 10 ** 14),
     '#7717 bracket not reproduced')
P1 = dict(P)
for r, d in delta.items(): P1[r] = P1.get(r, 0) + calls * d
P1 = {r: v for r, v in P1.items() if v}
p1 = pk.price(dict(T=T, P=P1), 30)
print('5. #7717 invoice: crossing %s (published bracket %s..%s); paid change per native %s x %d calls'
      % (pk.kstr(p0['kappa'], 16), A['bracket'][0], A['bracket'][1], delta, calls))
print('   with the reroutes: S %d, crossing in (%s, %s), %+.4f%% over #7717'
      % (p1['S'], str(p1['kappa']['lo'])[:16], str(p1['kappa']['hi'])[:16],
         100 * (float(p1['kappa']['lo']) / float(p0['kappa']['lo']) - 1)))
need(Q(str(p1['kappa']['lo'])) > Q('0.0037634645'), 'note crossing')
print('PASS (note only: conditional on #7717 and its own boundary; see README)')
