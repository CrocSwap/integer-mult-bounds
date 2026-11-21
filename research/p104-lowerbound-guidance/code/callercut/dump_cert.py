"""Regenerate the exact dual certificates of the Q=0 RC2 LP (CC model) and store them as exact rationals.
usage (needs numpy, scipy, mpmath): python3 dump_cert.py k.. ; writes ../../certs/q0_k{k}.json
The stored dual is the HiGHS master dual of cc2.solve_store, clipped to >= 0 on inequality rows and rounded
to denominator <= 1e12 (equality duals y, wm free).  certs/verify_q0.py re-derives every row from its definition and
checks weak duality by an exhaustive partition DP in exact Fractions / 60-digit Decimal; nothing from this script is trusted."""
import os, sys, json
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cc1, cc2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'certs')
for k in [int(a) for a in sys.argv[1:]]:
    L = cc1.LP(k, list(range(3, k + 1)))
    cc2.solve_store(L)
    w, wx, we, y, wm = L.du
    R = lambda v: Fr(float(v)).limit_denominator(10**12)
    du = [max(Fr(0), R(v)) for v in list(w) + list(wx) + list(we)]
    rd = cc2.rowdefs(L)
    assert len(rd) == len(du)
    json.dump({'k': k, 'dual': [str(d) for d in du], 'y': str(R(y)), 'wm': str(R(wm)),
               'primal_float': 104 * L.prim / k}, open(os.path.join(OUT, 'q0_k%d.json' % k), 'w'))
    print('wrote k', k, 'primal %.4f' % (104 * L.prim / k), flush=True)
