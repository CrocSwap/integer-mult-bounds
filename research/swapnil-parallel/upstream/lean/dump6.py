"""Dump the round-six bit and complex child-width histograms and the assembly parameters for the Lean check.
Usage (from the repository root): python3 lean/dump6.py COMPLEX_HIST_JSON"""
import sys, json, os
from fractions import Fraction as Q
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'independent/two-stage-bit')
import certificate_round6 as c6
from certificate_round3 import evaluate
a_b, cb = c6.retained_saving()
d = json.load(open(sys.argv[1])); hc = {int(k): v for k, v in d['hist'].items()}
a_c = Q(36926111, 5 * 10**11)
r = evaluate(a_b, a_c, Q(1, 1000), 'crude', m_c=d['m'], s_c=d['s'])
fr = lambda q: [Q(q).numerator, Q(q).denominator]
out = dict(bit=dict(a=fr(a_b), m=cb['m'], W=cb['W'], s=cb['s'], hist=sorted(cb['hist'].items())),
           cx=dict(a=fr(a_c), m=d['m'], W=d['W'], s=d['s'], hist=sorted(hc.items())),
           kappa=dict(beta=[1, 1000], eps=fr(r['eps']), x=fr(r['x']), c1=fr(r['c1']), kappa=fr(r['kappa']), mc=d['m']))
assert sum(w * n for w, n in out['bit']['hist']) == out['bit']['s'] and sum(w * n for w, n in out['cx']['hist']) == out['cx']['s']
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'round6-histograms.json'), 'w'))
print('kappa', r['kappa'], r['ok'])
