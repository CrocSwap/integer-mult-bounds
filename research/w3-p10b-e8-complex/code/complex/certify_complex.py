"""Complex supplier: Jacob Sussman's E8 unit (gcert1-e8-r783, h = 9, v = 120, R = 783, eight scatter totals).

1. The complex guard (portable_complex.py) on the pinned certificate: gx.check1 with the exact scalar identity and
   the gxcore mirror, every label and paid child, both scalar words and lifetimes, the five-window splice with all
   controls rejected, and the finite precision guard.
2. Lean binding: Sussman's own generators, vendored unchanged at 9c94857, regenerate from this certificate the 24
   Lean modules and the comparator configuration of his kernel-checked theorem wht_main_block_B2Ge8x; all 25 must
   equal the vendored upstream files byte for byte. His stand-alone replay.py (no code shared with gx) must accept
   the certificate at the figure 8762479.
3. b from the guard's own five-stage histogram with PR #315's two rational moment engines and the 10^-16 bad-class
   fallback; the next 10^-18 grid point must fail."""
import json, sys, os, subprocess, importlib.util
from fractions import Fraction as Q
H = os.path.dirname(os.path.abspath(__file__)); PR = os.path.join(H, '..', 'pricing'); E8 = os.path.join(H, 'inputs', 'e8')
sys.path.insert(0, H); os.environ.setdefault('CX_PINS', os.path.join(H, 'pins-e8.json'))
def load(n, path):
    s = importlib.util.spec_from_file_location(n, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
guard = load('portable_complex_e8', os.path.join(H, 'portable_complex.py'))
r = guard.run(package_root=H, progress=lambda t: print('  ' + t, flush=True))
assert r['status'] == 'PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION', r['status']
pg = r['precision_guard']; print('guard:', r['status'], '| gx.check1:', r['program_check']['gx_check1'][:20], '| rows', pg['physical_row_overcharge_coefficient'], '< 20161')
if os.environ.get('CX_RECEIPT'): json.dump(r, open(os.environ['CX_RECEIPT'], 'w'), indent=1)

env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
regen = subprocess.run([sys.executable, '-B', os.path.join(E8, 'tools/gx/regen_check_e8.py')], capture_output=True, text=True, env=env)
last = regen.stdout.strip().splitlines()[-1]
assert regen.returncode == 0 and last == 'RESULT: REPRODUCED (25 repository files reproduced byte for byte, 0 different, 3 generated files not in the repository)', regen.stdout + regen.stderr
print('Lean binding:', last, '(wht_main_block_B2Ge8x modules regenerated from this certificate)')
rep = subprocess.run([sys.executable, '-I', '-B', os.path.join(E8, 'tools/e8/replay.py'), os.path.join(E8, 'tools/certificate/gcert1-e8-r783.json.gz'), 'e8'], capture_output=True, text=True)
last = rep.stdout.strip().splitlines()[-1]
assert rep.returncode == 0 and last.startswith('REPLAY ACCEPTED: R=783 W=1263 D=120 cst=72 N=9039 figure=8762479'), rep.stdout + rep.stderr
print('stand-alone replay:', last)

cost = load('moment', os.path.join(PR, 'moment.py')); other = load('base_two_moment', os.path.join(PR, 'base_two_moment.py'))
CH = {int(k): v for k, v in r['five_stage_histogram'].items()}; P = guard.PINS
m = 5*P['H']; W = 4*P['V'] + P['R']; grid = Q(1, 10**18)
assert (m, W, r['ledger']['deficit']) == (45, 1263, 120)
root = cost.certify(dict(CH), m, W, True); b = Q(int(Q(root['lower'])*10**18), 10**18)
cm = cost.moment(CH, m, W, b, True); nm = cost.moment(CH, m, W, b + grid, True); assert cm[1] < 1 < nm[0]
fb = 32*m*m*sum(CH.values())
_, up = other.moment(m, W, list(CH.items()), b); _, bad = other.moment(m, W, [(1, fb)], b)
lo, _ = other.moment(m, W, list(CH.items()), b + grid); badlo, _ = other.moment(m, W, [(1, fb)], b + grid)
assert up + Q(1, 10**16)*bad < 1 < lo + Q(1, 10**16)*badlo
assert b == Q(876248285600677, 10**18), b
print('PASS complex coarse saving b =', b, float(b), '(two engines, 10^-16 fallback, adjacent grid point excluded)')
