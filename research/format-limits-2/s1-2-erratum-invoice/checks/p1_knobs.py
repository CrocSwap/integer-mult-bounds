"""P1 (complex invoice calculus, exact knobs on #626) and P3 w9 row.  Also P4 gate lives in p4_s7.py.
Gate: b of the word-built invoice = b of the PLAN profile of #626, and kappa = b/(1+b) equals the README literal to
16+ digits.  Knobs are finite differences of the exact (Decimal, 50 digits) root."""
from decimal import Decimal as D
from fractions import Fraction
import gzip, re, statistics as S
from collections import Counter
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invoice import *

w = Word626()
b0 = root(w.B0, M, W0)
check('P1.gate-profile', dict(w.B0) == w.prof and hmass(w.B0) == M * W0 - 2560 and w.plan['deficit'] == 2560 and w.plan['live'] == W0,
      'word climbs + idle remainder {1:123, 37:1, 48:2215} = PLAN profile of #626; mass %d = mW - 2560' % hmass(w.B0))
check('P1.gate-idle', dict(w.idle) == {1: 123, 37: 1, 48: 2215}, 'idle remainder = I - Hz = 387072 - 280592 = 106480 = 2215*48 + 123 + 37')
kappa = b0 / (1 + b0)
txt = gzip.decompress(open(os.path.join(INP, 'pr626/README.md.gz'), 'rb').read()).decode()
lit = re.search(r'Conditional kappa = \*\*([0-9.]+)\*\*', txt).group(1)
exact = Fraction(51110230636731, 31250000000000000)
check('P1.gate-kappa', str(kappa)[:20] == lit and 0 <= kappa - D(exact.numerator) / D(exact.denominator) < D('1e-18'),
      'kappa = b/(1+b) = %s... vs README %s (exact 51110230636731/31250000000000000), b = %s' % (str(kappa)[:22], lit, str(b0)[:22]))


def pct(H, W=W0, m=M):
    return float((root(H, m, W, start=b0 * D('0.9')) / b0 - 1) * 100)


def mass_ok(H, dM):
    return hmass(H) - (M * W0 - 2560) == dM


# centre: remove (climbs [1,1,1,1,4,8,1] = 17, host -9 -> idle child 9), per call
ctr = Counter()
for p in CALLS:
    d = w.d[p]
    for c in d['centers']:
        ctr[tuple(d['regs'][c])] += 1
check('P1.centre-shape', set(ctr) == {(1, 1, 1, 1, 4, 8, 1)} and sum(ctr.values()) == 16, 'all 8 centres of both words have climbs (1,1,1,1,4,8,1), mass 17')
H = Counter(w.B0)
for p, c in CALLS.items():
    for x in (1, 1, 1, 1, 4, 8, 1):
        H[x] -= c
    H[9] += c
check('P1.centre', mass_ok(H, -576) and abs(pct(H) - 22.598) < 0.0006, 'remove 1 centre: %+.3f%% b (local -17, host -9, deficit +576)' % pct(H))
# cst unit: centre cut climb 8 -> 7 in every call (and: one unit climb dropped)
H = Counter(w.B0); H[8] -= 72; H[7] += 72
c1 = pct(H)
H2 = Counter(w.B0); H2[1] -= 72
check('P1.cst-unit', mass_ok(H, -72) and abs(c1 - 2.8099) < 0.0006 and abs(pct(H2) - 2.8242) < 0.0006,
      '1 cst unit per call: cut climb 8->7 %+.4f%%, one unit climb dropped %+.4f%%' % (c1, pct(H2)))
# source end FULL->8 (shape 1,1,1,5 -> 1,1,1,4) and target end 8->7 (4 -> 3), one register, all calls
srcs = Counter(tuple(r) for p in CALLS for r in w.d[p]['regs'][:w.d[p]['v']])
tgts = Counter(tuple(r) for p in CALLS for r in w.d[p]['regs'][w.d[p]['v']:2 * w.d[p]['v']])
check('P1.src-tgt-shape', all(sum(k) == 8 for k in list(srcs) + list(tgts)) and srcs[(1, 1, 1, 5)] == 140 and tgts[(1, 1, 4, 1, 1)] == 104,
      'every source and target register has climb mass 8; modal shapes (1,1,1,5) x140 of 224 sources and (1,1,4,1,1) x104 of 224 targets are the ones priced')
Hs = Counter(w.B0); Ht = Counter(w.B0)
for p, c in CALLS.items():
    Hs[5] -= c; Hs[4] += c; Ht[4] -= c; Ht[3] += c
check('P1.src-tgt-end', abs(pct(Hs) - 2.8123) < 0.0006 and abs(pct(Ht) - 2.8135) < 0.0006,
      'source end FULL->8: %+.4f%% /unit; target end 8->7: %+.4f%% /unit' % (pct(Hs), pct(Ht)))
# port: v -> v-1 (one source + one target gone per call; idle 48-bins -72; live W -64)
Hp = Counter(w.B0)
for p, c in CALLS.items():
    for x in (1, 1, 1, 5, 1, 1, 4, 1, 1):
        Hp[x] -= c
Hp[48] -= 72
Wn = W0 - 64
check('P1.port', hmass(Hp) == M * Wn - 2496 and abs(pct(Hp, Wn) + 2.153998) < 0.0006,
      'v-1: %+.4f%% b (deficit 2496, mass residual 0), so one port = +2.15%%' % pct(Hp, Wn))
# w9 helper removed in all 72 calls: mean over the helper registers of each word, ck + jp8
tot = {'narrow': 0.0, 'merge48': 0.0}
for p, c in CALLS.items():
    regs = w.helpers(p, 9)
    for rule in tot:
        vals = []
        for cl in regs:
            H = Counter(w.B0)
            for x in cl:
                H[x] -= c
            if rule == 'narrow':
                H[9] += c
            else:
                H[48] += D(9 * c) / 48
            assert abs(hmass(H) - (M * W0 - 2560)) < 1e-6
            vals.append(pct(H))
        tot[rule] += S.mean(vals)
check('P1.w9-helper', abs(tot['narrow'] - 0.0676) < 0.0006 and abs(tot['merge48'] - 0.1371) < 0.0006,
      'one w9 helper removed in all 72 calls (ck mean + jp8 mean): %+.4f%% narrow, %+.4f%% with 48-merge' % (tot['narrow'], tot['merge48']))
finish()
