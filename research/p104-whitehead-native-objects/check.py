#!/usr/bin/env python3
"""Replay of the objects of this package.  Standard library only, about two minutes.

    python3.12 -I -B check.py

  1. sha256 of every object against data/OBJECTS.json.
  2. The two natives (the baseline native and the one with the owned-UP prefix on the 8 hosted ports) replayed
     event by event in exact Fractions: frame law, dyadic rows, the exact endpoint X = x + alpha y, Y = x + (1 + alpha) y
     (hosted ports X = x - 2y, Y = x/2 at t = -1), owned UP mass 56 and 64.  A control declares the wrong alpha and must fail.
  3. The two roots with W stages (outer, and connected rho = 1 with 18 stages), each by its own checker, with controls.
  4. Exact kappa of the baseline and of the Whitehead invoice (Decimal, 50 digits), S, D, and the move between them.
  5. The exact targets: break-even 0.10987 / 0.13955 UP per port-call and the budget arithmetic.
  6. The helper-free Whitehead native on the 104 ports (checks/window_native.py).
The joint caller replay is the second command of VERIFY.json (checks/check_joint_w.py)."""
import gzip, hashlib, json, os, subprocess, sys, tempfile
from collections import Counter
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q

getcontext().prec = 50
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
CH = os.path.join(HERE, 'checks')


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL ' + msg)
    print('PASS ' + msg, flush=True)


def run(args, env=None):
    e = {'PATH': os.environ.get('PATH', '')}
    e.update(env or {})
    r = subprocess.run([sys.executable, '-I', '-B'] + args, capture_output=True, text=True, env=e)
    return r.returncode, r.stdout + r.stderr


# 1 ---------------------------------------------------------------- objects
man = json.load(open(os.path.join(DATA, 'OBJECTS.json')))['objects']
for name, row in man.items():
    need(hashlib.sha256(open(os.path.join(HERE, name), 'rb').read()).hexdigest() == row['sha256'], 'sha256 ' + name)

# 2 ---------------------------------------------------------------- natives
rc, out = run([os.path.join(CH, 'verify_host3w.py'), os.path.join(DATA, 'mmW.json.gz'), '1125'])
need(rc == 0 and 'PASS_HOST3 decoupled ports 96 hosted ports 8 alpha -2 beta 1/2 t -1' in out and 'endpoint bad rows 0' in out
     and "owned UP {1: 18, 2: 4, 3: 1, 4: 6, 5: 1, 6: 1}" in out and 'events 71184' in out,
     'the Whitehead native (baseline plus 8 prefixes): exact endpoint, 71,184 events, owned UP mass 64, hosted X = x - 2y, Y = x/2, t = -1')
rc, out = run([os.path.join(CH, 'verify_host3w.py'), os.path.join(DATA, 'mm.json.gz'), '1125'])
need(rc == 0 and 'PASS_HOST3 decoupled ports 96 hosted ports 8 alpha -1 beta 1/2 t -1/2' in out and 'endpoint bad rows 0' in out
     and "owned UP {1: 10, 2: 4, 3: 1, 4: 6, 5: 1, 6: 1}" in out and 'events 71144' in out,
     'baseline native: exact endpoint, 71,144 events, owned UP mass 56, t = -1/2')
W = json.load(gzip.open(os.path.join(DATA, 'mmW.json.gz'), 'rt'))
W['hosted']['alpha'] = '-1'
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, 'wrong_alpha.json.gz')
    with gzip.open(p, 'wt') as f:
        json.dump(W, f)
    rc, out = run([os.path.join(CH, 'verify_host3w.py'), p, '1125'])
need(rc != 0 and 'endpoint bad rows 16' in out, 'control: the Whitehead native declared with alpha = -1 is rejected (16 bad rows)')

# 3 ---------------------------------------------------------------- roots
rc, out = run([os.path.join(CH, 'root_check_hw.py'), os.path.join(DATA, 'rootw1g.json')], {'WSTAGES': '1'})
need(rc == 0 and out.strip().endswith('PASS_ROOT_HOSTED') and 'FAIL' not in out, 'type B root with W stages 1 and 18 (hosted checker, t = -1 exactly at W stages only)')
rc, out = run([os.path.join(CH, 'root_check_hw.py'), os.path.join(DATA, 'root_h.json')], {'WSTAGES': '1'})
need(rc != 0 and 'FAIL' in out, 'control: the root without W stages fails the W-root checker')
rc, out = run([os.path.join(CH, 'root_check_hw.py'), os.path.join(DATA, 'rootw1.json')], {'WSTAGES': '1'})
need(rc != 0 and 'FAIL' in out, 'control: the ungauged W root fails (its pairs do not match the natives)')
rc, out = run([os.path.join(CH, 'rootcheck_w.py'), os.path.join(DATA, 'rootw1g.json')])
need(rc == 0 and 'RESULT ALL_REQ_PASS' in out, 'outer W root: every requirement of the root checker')
rc, out = run([os.path.join(CH, 'rootcheck_w.py'), os.path.join(DATA, 'r1_W18_t3.json')])
need(rc == 0 and 'RESULT ALL_REQ_PASS' in out and 'rank mod p = 1444 of n^2 = 1444' in out,
     'connected rho = 1 root, 18 stages at t = -1: every requirement (product -I, symbolic whole-job identity, mask credit, rank G = n, strongly connected, irreducible)')
R = json.load(open(os.path.join(DATA, 'r1_W18_t3.json')))
need(R['n'] == 38 and len(R['stages']) == 18 and all(len(s['units']) == 2 for s in R['stages']), 'rho = 1 root shape: n = 38, 18 stages of two consecutive units (N = 39, rho = 1)')
R['X'][5][3] = str(Q(R['X'][5][3]) + 1)
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, 'bad_root.json')
    json.dump(R, open(p, 'w'))
    rc, out = run([os.path.join(CH, 'rootcheck_w.py'), p])
need(rc != 0 and 'FAIL' in out, 'control: one wrong X entry in the rho = 1 root is rejected')

# 4 ---------------------------------------------------------------- kappa
def load(f):
    i = json.load(open(os.path.join(DATA, f)))
    return Counter({int(k): v for k, v in i['T'].items()}), Counter({int(k): v for k, v in i['P'].items()})


def kap(T, P):
    rs = sorted(set(T) | set(P)); lo, hi = D('0.001'), D('0.0045')
    for _ in range(200):
        m = (lo + hi) / 2
        if sum((D(T.get(r, 0)) - D(P.get(r, 0))) * (D(r).ln() * (1 - m)).exp() for r in rs) > 0: lo = m
        else: hi = m
    return lo


T0, P0 = load('mm.chain.invoice.json'); Tw, P1 = load('w.joint.invoice.json')
S0 = sum(r * (T0[r] - P0[r]) for r in set(T0) | set(P0)); S1 = sum(r * (Tw[r] - P1[r]) for r in set(Tw) | set(P1))
Dd = lambda T, P: sum((D(T[r]) - D(P[r])) * D(r) * D(r).ln() for r in set(T) | set(P))
k0, k1 = kap(T0, P0), kap(Tw, P1)
need(S0 == 1520 and S1 == 1504, 'S = 1520 (baseline) and 1504 (Whitehead): the 8 carriers x 2 W calls cost 16')
need(str(k0).startswith('0.00362701882') and str(k1).startswith('0.0035927413806393823240'), 'exact kappa: baseline %s, Whitehead %s' % (str(k0)[:16], str(k1)[:24]))
need(+(Tw - T0) == Counter({129: 8}) and +(T0 - Tw) == Counter({145: 8}) and +(P1 - P0) == Counter({1: 16}) and +(P0 - P1) == Counter({8: 16}),
     'invoice move: T 8 x {145} -> 8 x {129} (hub-2 drop on the B ports), P -16 x {8} +16 x {1}')
pct = (k1 / k0 - 1) * 100
need(D('-0.9452') < pct < D('-0.9450'), 'Whitehead kappa against the baseline: %s%% (below it; not a candidate)' % str(pct)[:8])
need(abs(Dd(Tw, P1) - D('421735.2022776638')) < D('1e-6'), 'D = %s' % str(Dd(Tw, P1))[:14])

# 5 ---------------------------------------------------------------- exact targets
Tw = {'outer w=1 (2 calls)': D('11.4263770958522'), 'rho=1 (18 calls)': D('14.513107')}
cstar = {k: v / 104 for k, v in Tw.items()}
need(D('0.10986') < cstar['outer w=1 (2 calls)'] < D('0.10988') and D('0.13954') < cstar['rho=1 (18 calls)'] < D('0.13956'),
     'break-even per port-call c* = T / 104 = %s (outer) / %s (rho = 1); the carrier here costs 1.00' % (str(cstar['outer w=1 (2 calls)'])[:7], str(cstar['rho=1 (18 calls)'])[:7]))
mm_own = D('111.573067')
pass_outer, pass_rho = (mm_own + Tw['outer w=1 (2 calls)'] + D('49.7765')) / 104, (mm_own + Tw['rho=1 (18 calls)'] + D('49.7765')) / 104
need(D('1.6612') < pass_outer < D('1.6614') and D('1.6908') < pass_rho < D('1.6910'), 'pass line with the helper-free public layer: owned <= %s (outer) / %s (rho = 1) per port per W call' % (str(pass_outer)[:6], str(pass_rho)[:6]))

# 6 ---------------------------------------------------------------- the Whitehead native on P104
rc, out = run([os.path.join(CH, 'window_native.py')])
need(rc == 0 and out.strip().endswith('PASS_WINDOW_NATIVE'), 'helper-free d = 0 native on P104: regenerated, exact and mod-p replay, structure, price, budget, 100 mutants\n' + out)
print('PASS_PACKAGE_CHECK')
