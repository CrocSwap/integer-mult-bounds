"""Complex certificate checks: Jacob Sussman's gx.check1 (E0-E7: sizes, labels/nesting, equal frames at gates, scatter
cut, gate shapes, bracket rule, exact scalar x-content replay E5, price data E6, exterior gauges E7) and his gxcore
mirror histogram, a flipped-sign control (must fail E5), and the source-span rule (our check: the x-content support of
every non-y operand, and of a slot destination after the gate, lies in the gate frame).
usage: cxcheck.py CERT.json.gz GXDIR"""
import sys, os, gzip, json, copy
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxretime import CX
c = json.load(gzip.open(sys.argv[1])); sys.path.insert(0, sys.argv[2]); import gx, gxcore
st = {}; gx.check1(c, scalar=True, stats=st)
Hinv = Counter()
for w in c['blocks'].values():
    for r, n in w.items(): Hinv[int(r)] += n
assert gxcore.mirror(gxcore.normal(copy.deepcopy(c)))['hist'] == dict(Hinv), 'gxcore histogram'
c2 = copy.deepcopy(c)
for g in c2['A']:
    if g[0] in ('out', 'in') and g[3]: t, a, b = g[3][0]; g[3][0] = [t, -a, b]; break
try: gx.check1(c2, scalar=True); raise SystemExit('flipped sign accepted')
except AssertionError as e: assert str(e).startswith('E5'), str(e)
sv = CX(c).span_ok(); assert sv == 0, sv
print('   %s: gx.check1 PASS (E0-E7, exact scalar), gxcore mirror PASS, flipped sign rejected (E5), source-span violations 0 | h %d v %d R %d cst %d N %d, gates A/B %d/%d, frames %d'
      % (os.path.basename(sys.argv[1]), c['h'], c['v'], c['R'], c['cst'], c['N'], len(c['A']), len(c['B']), len(c['frames'])))
