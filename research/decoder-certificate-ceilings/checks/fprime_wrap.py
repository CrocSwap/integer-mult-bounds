# F' ceilings from the MILP output of fprime_milp.py:  ceiling = (#frames) * max_k min(k,T)/minmeet_k  (reads the MILP log on stdin)
import sys, re
from fractions import Fraction
name, nframes, T, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
mm = {}
for l in sys.stdin:
    g = re.match(r'(\S+) k (\d+) status (\d+) min meet (\S+)', l)
    if g and g.group(1) == name:
        assert g.group(3) == '0'; mm[int(g.group(2))] = round(float(g.group(4)))   # integral objective: round the solver's 1e-13 noise
assert sorted(mm) == list(range(1, T + 1)), mm
c = nframes * max(Fraction(min(k, T), mm[k]) for k in mm)
print('min meet over all k-sets', mm, "-> F' ceiling", c, '=', round(float(c), 3))
print(('PASS' if lo < float(c) < hi else 'FAIL'), "F' ceiling", name, '(MILP-computed)')
