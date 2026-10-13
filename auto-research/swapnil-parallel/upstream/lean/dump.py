"""Dump the round-five bit and complex child-width histograms for the Lean check (run from the repository root)."""
import sys, json, os
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'independent/two-stage-bit')
from fractions import Fraction as Q
import certificate_round5 as c5, moment
a_b, cb = c5.bit_saving(side=True)
d = json.load(open(sys.argv[1]))   # from independent/complex-network/fullbatch_hist.py 28 OUT sf
hc = {int(k): v for k, v in d['hist'].items()}
out = dict(bit=dict(a=[a_b.numerator, a_b.denominator], m=cb['m'], W=cb['W'], s=cb['s'], hist=sorted(cb['hist'].items())),
           cx=dict(a=[4079603, 25*10**10], m=d['m'], W=d['W'], s=d['s'], hist=sorted(hc.items())))
# python-side check with the atanh ln bound used by the Lean file
for k in ('bit', 'cx'):
    o = out[k]; c = dict(m=o['m'], W=o['W'], hist=dict(o['hist']))
    lu = {w: moment.ln_upper(Q(o['m'], w)) for w in c['hist']}
    print(k, 'sum==s', sum(w*n for w, n in o['hist']) == o['s'], 'F_upper<1', moment.F_upper(c, Q(*o['a']), lu) < 1, 'widths', len(o['hist']))
from certificate_round3 import evaluate
r = evaluate(a_b, Q(*out['cx']['a']), Q(1, 1000), 'crude', m_c=d['m'], s_c=d['s'])
fr = lambda q: [Q(q).numerator, Q(q).denominator]
out['kappa'] = dict(beta=[1, 1000], eps=fr(r['eps']), x=fr(r['x']), c1=fr(r['c1']), kappa=fr(r['kappa']), mc=d['m'])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'round5-histograms.json'), 'w'))
