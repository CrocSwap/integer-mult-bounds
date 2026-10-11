"""E8 in the seven-stage bridged word B_3: layout, complex checks and exact coarse saving.

1. Layout (code/complex/code/bridged.py).  The bridged word B_K with K bank pairs per class and 2K+1 stages, on the
   label space H + 2K x H.  For K = 2 it must give Jacob Sussman's five-stage B_2 idle climbs (2h+2 | 2h-2, h-1, 4);
   for K = 3 it gives the seven-stage word.  Both are checked: nested climbs, twin gates at equal frames, stage
   entry/exit frames, final frames, m - 1 moves per data role, and the exchange identity X_i = -y_i, Y_i = x_i.
2. Complex checks (code/complex/portable_complex.py), the checks of PR #352 with the layout as a parameter:
   K = 2 against #352's pins (regression), then K = 3 against pins-e8-b3.json.  gx.check1 with the exact scalar
   identity, gxcore, labels, both scalar words and lifetimes, the splice (2K+1 windows), the finite guard.
3. The helper circuit is Sussman's E8 unit: his generators regenerate the Lean data of wht_main_block_B2Ge8x from it
   byte for byte, and his stand-alone replay accepts it at 8762479.
4. b for B_2 (must equal #352's) and for B_3, from the guard's own histogram with the two rational moment engines
   and the 10^-16 fallback; the next 10^-18 grid point must fail."""
import json, os, subprocess, sys, importlib.util
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__)); CX = os.path.join(HERE, 'complex'); E8 = os.path.join(CX, 'inputs', 'e8')
PR = os.path.join(HERE, 'pricing')
sys.path.insert(0, os.path.join(CX, 'code'))
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
def load(n, path):
    s = importlib.util.spec_from_file_location(n, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

import bridged
lay2 = bridged.check(2, 9); lay3 = bridged.check(3, 9)
assert lay2['per_pair_idle'] == {1: [20], 2: [16, 8, 4]}, lay2['per_pair_idle']
assert lay3['per_pair_idle'] == {1: [38], 2: [16, 8, 22], 3: [32, 8, 6]}, lay3['per_pair_idle']
print('layout: B_2 idle climbs %s (Sussman: 2h+2 | 2h-2, h-1, 4); B_3 idle climbs %s; %d invocations, %d twin gates; '
      'nested climbs, equal-frame gates, m-1 moves per data role, exchange identity: PASS'
      % (lay2['per_pair_idle'], lay3['per_pair_idle'], lay3['invocations'], lay3['gates']), flush=True)

def guard(pins):
    out = subprocess.run([sys.executable, '-B', os.path.join(CX, 'portable_complex.py')], capture_output=True, text=True,
                         env=dict(env, CX_PINS=os.path.join(CX, pins)))
    assert out.returncode == 0, out.stderr[-2000:]
    r = json.loads(out.stdout)
    assert r['status'] == 'PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION', r['status']
    return r
r2 = guard('pins-e8.json'); r3 = guard('pins-e8-b3.json')
if os.environ.get('CX_RECEIPT'): json.dump(r3, open(os.environ['CX_RECEIPT'], 'w'), indent=1)
pg = r3['precision_guard']
print('complex checks: B_2 regression %s (#352 pins); B_3 %s | m %d, live %d, deficit %d, max child %d, rows %d < 20161, '
      'induction gap %d B' % (r2['status'], r3['status'], pg['m'], pg['live_per_vertex'], r3['ledger']['deficit'],
      r3['ledger']['max_child'], pg['physical_row_overcharge_coefficient'], pg['induction_gap_multiple_of_B']), flush=True)

regen = subprocess.run([sys.executable, '-B', os.path.join(E8, 'tools/gx/regen_check_e8.py')], capture_output=True, text=True, env=env)
last = regen.stdout.strip().splitlines()[-1]
assert regen.returncode == 0 and last == 'RESULT: REPRODUCED (25 repository files reproduced byte for byte, 0 different, 3 generated files not in the repository)', regen.stdout + regen.stderr
rep = subprocess.run([sys.executable, '-I', '-B', os.path.join(E8, 'tools/e8/replay.py'), os.path.join(E8, 'tools/certificate/gcert1-e8-r783.json.gz'), 'e8'], capture_output=True, text=True)
assert rep.returncode == 0 and rep.stdout.strip().splitlines()[-1].startswith('REPLAY ACCEPTED: R=783 W=1263 D=120 cst=72 N=9039 figure=8762479'), rep.stdout
print('circuit: the Lean data of wht_main_block_B2Ge8x regenerate byte for byte; stand-alone replay accepts at 8762479', flush=True)

moment = load('moment', os.path.join(PR, 'moment.py')); other = load('base_two_moment', os.path.join(PR, 'base_two_moment.py'))
grid = Q(1, 10**18)
def coarse(r, K):
    CH = {int(k): v for k, v in r['five_stage_histogram'].items()}
    v, R, h = 120, 783, 9; m = (2 * K + 1) * h; W = 2 * K * v + R
    assert (m, W, r['ledger']['deficit']) == (r['precision_guard']['m'], r['precision_guard']['live_per_vertex'], 2 * K * v - (2 * K + 1) * 72)
    root = moment.certify(dict(CH), m, W, True); b = Q(int(Q(root['lower']) * 10**18), 10**18)
    cm = moment.moment(CH, m, W, b, True); nm = moment.moment(CH, m, W, b + grid, True); assert cm[1] < 1 < nm[0]
    fb = 32 * m * m * sum(CH.values())
    _, up = other.moment(m, W, list(CH.items()), b); _, bad = other.moment(m, W, [(1, fb)], b)
    lo, _ = other.moment(m, W, list(CH.items()), b + grid); badlo, _ = other.moment(m, W, [(1, fb)], b + grid)
    assert up + Q(1, 10**16) * bad < 1 < lo + Q(1, 10**16) * badlo
    return b
b2 = coarse(r2, 2); b3 = coarse(r3, 3)
assert b2 == Q(876248285600677, 10**18), b2
assert b3 == Q(932783231884153, 10**18), b3
print('PASS coarse savings (two engines, 10^-16 fallback, adjacent grid point excluded): B_2 b = %s = %.12e (= #352); '
      'B_3 b = %s = %.12e (%+.3f %%)' % (b2, float(b2), b3, float(b3), 100 * (float(b3) / float(b2) - 1)), flush=True)
json.dump(dict(layout='B_3', stages=7, m=63, W=1503, deficit=r3['ledger']['deficit'], histogram=r3['five_stage_histogram'],
               b=str(b3), b_float=float(b3), b_B2=str(b2)), open(os.environ.get('B3_OUT', os.devnull), 'w'), indent=1)
