"""Run the p = 10 complex guard on the shipped gcert/1 program, then certify b from its own five-stage histogram with
PR #315's two rational moment engines and the 10^-16 bad-class fallback; the next 10^-18 grid point must fail."""
import json, sys, os, importlib.util
from fractions import Fraction as Q
H = os.path.dirname(os.path.abspath(__file__)); PR = os.path.join(H, '..', 'pricing')
sys.path.insert(0, H); os.environ.setdefault('CX_PINS', os.path.join(H, 'pins-p10f.json'))
def load(n, path):
    s = importlib.util.spec_from_file_location(n, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
guard = load('portable_complex_p10', os.path.join(H, 'portable_complex.py'))
r = guard.run(package_root=H, progress=lambda t: print('  ' + t, flush=True))
assert r['status'] == 'PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION', r['status']
pg = r['precision_guard']; print('guard:', r['status'], '| gx.check1:', r['program_check']['gx_check1'][:20], '| rows', pg['physical_row_overcharge_coefficient'], '< 20161')
cost = load('moment', os.path.join(PR, 'moment.py')); other = load('base_two_moment', os.path.join(PR, 'base_two_moment.py'))
CH = {int(k): v for k, v in r['five_stage_histogram'].items()}; m = 100; W = 4*960 + 6265; grid = Q(1, 10**18)
root = cost.certify(dict(CH), m, W, True); b = Q(int(Q(root['lower'])*10**18), 10**18)
cm = cost.moment(CH, m, W, b, True); nm = cost.moment(CH, m, W, b + grid, True); assert cm[1] < 1 < nm[0]
fb = 32*m*m*sum(CH.values())
_, up = other.moment(m, W, list(CH.items()), b); _, bad = other.moment(m, W, [(1, fb)], b)
lo, _ = other.moment(m, W, list(CH.items()), b + grid); badlo, _ = other.moment(m, W, [(1, fb)], b + grid)
assert up + Q(1, 10**16)*bad < 1 < lo + Q(1, 10**16)*badlo
assert b == Q(396604388013523, 500000000000000000), b
print('PASS complex coarse saving b =', b, float(b), '(two engines, 10^-16 fallback, adjacent grid point excluded)')
