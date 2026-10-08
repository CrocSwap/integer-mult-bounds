"""Dump the round-seven bit histograms (staircase and round-six entrance corners) with the round-six complex
histogram, and both assemblies, for the Lean check. The bit histograms are rebuilt from the frozen schedule by
scripts/certificate_round7.py; the complex side is round six's (lean/round6-histograms.json).
Usage (from the repository root): python3 lean/dump7.py"""
import sys, json, os
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))
import certificate_round7 as c7

fr = lambda q: [Q(q).numerator, Q(q).denominator]
cx = json.load(open(os.path.join(HERE, 'round6-histograms.json')))['cx']
_, res = c7.certify(c7.HEADLINE)
out = dict(sides=[['bit', 'bit interchange, staircase entrance corner'], ['bitplain', 'bit interchange, round-six entrance corner'],
                  ['cx', 'complex interchange (round six)']],
           kappas=[['kappa', 'bit'], ['kappaplain', 'bitplain']], cx=cx)
for side, kk, key in (('bit', 'kappa', 'staircase'), ('bitplain', 'kappaplain', 'plain')):
    a, k, c = res[key]
    out[side] = dict(a=fr(a), m=c['m'], W=c['W'], s=c['s'], hist=sorted(c['hist'].items()))
    out[kk] = dict(beta=[1, 1000], eps=fr(k['eps']), x=fr(k['x']), c1=fr(k['c1']), kappa=fr(k['kappa']), mc=cx['m'])
    assert sum(w * n for w, n in out[side]['hist']) == c['s'] and cx['m'] == c7.M_C and cx['s'] == c7.S_C
    print(side, 'a_b', a, 'kappa', k['kappa'], k['ok'])
json.dump(out, open(os.path.join(HERE, 'round7-histograms.json'), 'w'))
