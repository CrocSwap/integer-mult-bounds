"""P5 (profile-level part): the climb mass of the #626 invoice is a forced cover: mass = mW - deficit exactly, so padding
mass is not an option, and reshaping mass is priced by the shape alone.  Checked: the mass identity from the word and the PLAN,
and the arithmetic bound 'moving 1% of the unit-climb mass into width-9 climbs gives +0.26% b'.  The frame-SA outcome (0.0% b over
legal assignments), the ~96% blocking histogram and the SSS-hourglass comparison are RECORDED (evidence/P5)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invoice import *

w = Word626(); b0 = root(w.B0, M, W0)
check('P5.cover', hmass(w.B0) == M * W0 - w.plan['deficit'] == 520704 and w.plan['deficit'] == 2560 == 64 * 112 - 4608,
      'mass %d = 73 * 7168 - 2560 (deficit 2560 = 64 v - 4608 at v = 112, an asserted constant of the invoice)' % hmass(w.B0))
local = sum(a * n for a, n in w.H.items()) - 0
per_call = {p: sum(a * n for a, n in Counter(x for r in w.d[p]['regs'] for x in r).items()) for p in CALLS}
check('P5.local-mass', per_call == {'ck': 5714, 'jp8': 5758}, 'local mass per call: ck 5714, jp8 5758 (= sum of helper widths + 1856)')
H = Counter(w.B0); u = H[1] - w.idle.get(1, 0)       # unit climbs of the 72 local words
mv = D(u) / 100
H[1] -= mv; H[9] += mv / 9
assert abs(hmass(H) - hmass(w.B0)) < D('1e-9')
g = float((root(H, M, W0) / b0 - 1) * 100)
check('P5.padding-bound', abs(g - 0.26) < 0.01, 'moving 1%% of the unit-climb mass into width-9 climbs (mass conserved): %+.3f%% b' % g)
finish()
