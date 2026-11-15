#!/usr/bin/env python3
"""Regression test for interval_gate_signed.py against the pinned original gate.

Runs 32 cases (passes, rejections, mutants). Prints one line per case and exits 1
unless every case has the expected outcome. Only repository files and
data/frontier_invoices.json are used; nothing is written to the repository.
"""
import sys, json, importlib.util, traceback
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode = True
getcontext().prec = 70
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[1]
SWSC = ROOT / 'research' / 'shared-wire-split-composition'

def mod(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

ORIG = mod('orig_gate', SWSC / 'interval_gate.py')
PATS = (PKG / 'interval_gate_signed.py').read_text()
PAT = mod('pat_gate', PKG / 'interval_gate_signed.py')
INV = json.loads((PKG / 'data' / 'frontier_invoices.json').read_text())['invoices']

def M(T, P, k):
    f = lambda H: sum(D(c) * D(int(r)) * (-k * D(int(r)).ln()).exp() for r, c in H.items())
    return f(T) - f(P)

def crossing(T, P, lo=D('0.001'), hi=D('0.02')):
    assert M(T, P, lo) > 0 and M(T, P, hi) < 0
    for _ in range(200):
        m = (lo + hi) / 2
        if M(T, P, m) > 0: lo = m
        else: hi = m
    return lo

NP = NF = 0
def run(g, T, P, claim, tested, lo, hi, pin=None, tag='', expect=True):
    global NP, NF
    try:
        r = g.gate({'T': T, 'P': P}, claim, tested, lo, hi, *([pin] if pin else []))
        ok = True; info = 'cap %s' % r['input_lift']['interval_kappa_cap']
    except AssertionError:
        ok = False; tb = traceback.extract_tb(sys.exc_info()[2])[-1]
        info = 'line %d: %s' % (tb.lineno, tb.line.strip()[:60])
    good = (ok == expect); NP += good; NF += (not good)
    print('%s %s %-58s %s' % ('OK ' if good else 'BAD', 'PASS' if ok else 'REJ ', tag, info))
    return ok

def par(T, P, claim, g=D('1e-16')):
    x = crossing(T, P)
    lo = x.quantize(D('1e-33'), rounding='ROUND_FLOOR'); hi = lo + D('1e-33')
    return str(claim), str(D(claim) + 7 * g), str(lo), str(hi), x

# 1. control: the #7000 recorded invoice with its recorded parameters
R = json.loads((SWSC / 'FULL-RESULT.json').read_text())
T7, P7 = R['invoice']['T'], R['invoice']['P']; gg = R['gate']
af = [F(x) for x in (gg['claim'], gg['tested'], *gg['raw_bracket'])]
a = tuple('%s' % (D(x.numerator) / D(x.denominator)) for x in af)
print('== #7000 control', a[0])
run(ORIG, T7, P7, *a, tag='#7000 original gate')
run(PAT, T7, P7, *a, tag='#7000 signed gate')
r0 = ORIG.gate({'T': T7, 'P': P7}, *a); r1 = PAT.gate({'T': T7, 'P': P7}, *a, '.00376669')
c1 = all(str(r0[k]) == str(gg[k]) for k in ('alpha', 'gamma', 'delta', 'H', 'minimum_log_power', 'compiler_gap'))
c2 = r0['outer']['minimum_margin'] == gg['outer']['minimum_margin']
c3 = all(r0[k] == r1[k] for k in r0 if k != 'input_lift')
print('   original output reproduces FULL-RESULT gate fields:', c1, '| outer:', c2)
print('   signed gate at the old pin: non-lift fields equal original:', c3)
if not (c1 and c2 and c3): NF += 1

# 2. frontier words #7617 and #7615
claims = {'7617': '0.00365760025222', '7615': '0.00365455370060'}
for name in ('7617', '7615'):
    T, P = INV[name]['T'], INV[name]['P']; c, t, lo, hi, x = par(T, P, claims[name])
    print('==', name, 'crossing %.20f' % x)
    run(ORIG, T, P, c, t, lo, hi, tag=name + ' original')
    run(PAT, T, P, c, t, lo, hi, tag=name + ' signed')
    run(PAT, {**T, '9': T['9'] - 1}, P, c, t, lo, hi, tag=name + ' corrupt: drop one rank-9 target', expect=False)
    run(PAT, T, {**P, '1': P['1'] + 1}, c, t, lo, hi, tag=name + ' corrupt: add one rank-1 paid', expect=False)
    k = max(P, key=int); run(PAT, T, {**P, k: P[k] + 1}, c, t, lo, hi, tag=name + ' corrupt: add one top-rank paid', expect=False)
    run(PAT, T, P, str(D(c) + D('1e-12')), str(D(c) + D('1e-12') + D('7e-16')), lo, hi, tag=name + ' claim 1e-12 above crossing', expect=False)
    run(PAT, T, P, c, str(D(c) + D('6e-16')), lo, hi, tag=name + ' gap numerator != 1 (6e-16/7)', expect=False)
T0, P0 = dict(INV['7617']['T']), dict(INV['7617']['P'])

# 3. BIT pin ceiling on a synthetic invoice whose crossing is above the pin
T = dict(T0); T['1'] += 85; x = crossing(T, P0)
lo = x.quantize(D('1e-33'), rounding='ROUND_FLOOR'); hi = lo + D('1e-33')
pin = D('.00385248'); g = D('1e-16')
print('== pin ceiling, synthetic crossing %.10f' % x)
run(PAT, T, P0, str(pin - 8 * g), str(pin - g), str(lo), str(hi), tag='tested = pin - 1e-16', expect=True)
run(PAT, T, P0, str(pin - 7 * g), str(pin), str(lo), str(hi), tag='tested = pin exactly', expect=False)
run(PAT, T, P0, str(pin - 6 * g), str(pin + g), str(lo), str(hi), tag='tested = pin + 1e-16', expect=False)
run(PAT, T, P0, str(pin - 5 * g), str(pin + 2 * g), str(lo), str(hi), pin=str(pin + 3 * g),
    tag='pin above admitted BIT saving (C3 assert)', expect=False)
run(ORIG, T, P0, str(D('.00376669') - 8 * g), str(D('.00376669') - g), str(lo), str(hi), tag='ORIGINAL tested just below old pin', expect=True)
run(ORIG, T, P0, str(D('.00376669') - 6 * g), str(D('.00376669') + g), str(lo), str(hi), tag='ORIGINAL tested just above old pin', expect=False)

# 4. lift ceiling -d1/N = .006957747...; LIFT_RANGE and the C3 pin cap are relaxed so only the lift assertion binds
T = dict(T0); T['1'] += 1300; x = crossing(T, P0)
lo = x.quantize(D('1e-33'), rounding='ROUND_FLOOR'); hi = lo + D('1e-33')
print('== lift ceiling, synthetic crossing %.8f' % x)
PAT.LIFT_RANGE = F(1, 10); PAT.BIT_PIN = '.1'
for cap, exp in (('.00695774704', True), ('.006957747045', False), ('.0069577', True), ('.0069578', False)):
    run(PAT, T, P0, str(D(cap) - D('1e-8')), str(D(cap) - D('1e-8') + 7 * g), str(lo), str(hi), pin=cap,
        tag='lift: pin = lift_cap = %s' % cap, expect=exp)
PAT.LIFT_RANGE = F('.0069')   # BIT_PIN stays relaxed: these two cases test the LIFT_RANGE branch only
run(PAT, T, P0, '.0069', '.0069000000000007', str(lo), str(hi), pin='.00691', tag='pin .00691 > LIFT_RANGE: lift_cap = tested .0069', expect=True)
run(PAT, T, P0, '.00696', '.0069600000000007', str(lo), str(hi), pin='.00697', tag='pin > LIFT_RANGE, tested .00696 > signed ceiling', expect=False)

PAT.BIT_PIN = '.00385248'

# 5. mutants of the signed gate
def mutant(tag, old, new, expect):
    assert PATS.count(old) == 1, tag
    m = types_module(tag, PATS.replace(old, new))
    c, t, lo2, hi2, _ = par(T0, P0, claims['7617'])
    run(m, T0, P0, c, t, lo2, hi2, tag='mutant: ' + tag, expect=expect)
def types_module(tag, src):
    import types
    m = types.ModuleType('mut'); m.__file__ = str(PKG / 'interval_gate_signed.py')
    exec(compile(src, m.__file__, 'exec'), m.__dict__); return m
mutant('curvature sign-flipped (subtract neg part)', 'if sign<0:curvature=add(curvature,smul(mul(log(r),log(r)),c*r))', 'if sign<0:curvature=sub(curvature,smul(mul(log(r),log(r)),c*r))', False)
mutant('lift histogram pos/neg swapped', 'pos={7:1,3:1,5:1};neg={9:1,4:1,1:2}', 'neg={7:1,3:1,5:1};pos={9:1,4:1,1:2}', False)
mutant('d1 sign flipped', 'd1=add(d1,smul(log(r),sign*c*r))', 'd1=add(d1,smul(log(r),-sign*c*r))', False)
mutant('LIFT_RANGE .1 with the real pin (still passes)', "LIFT_RANGE=F('.0069')", "LIFT_RANGE=F('.1')", True)
print('TOTAL as-expected %d, unexpected %d' % (NP, NF))
sys.exit(1 if NF or NP != 32 else 0)
