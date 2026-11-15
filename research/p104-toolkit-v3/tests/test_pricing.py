# SPDX-License-Identifier: Apache-2.0
"""pricekit.py, kformula.py, layout_price.py, cap_check.py: controls on the vendored #7546 word and #7113 caller."""
import contextlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import io
import math
import runpy
from collections import Counter

from common import ok, check_data, base_word, caller_path, word_7601, KAPPA_7546, KAPPA_7601, PKG
import pricekit as pk
import kformula as kf

check_data()
W = base_word(); C = pk.load(caller_path())

# ---------------------------------------------------------------- pricekit
nat = pk.native_from_word(W)
R = pk.run(caller_path(), nat)
pr = R['price']
ok(pr['S'] == 1424 and pk.kstr(pr['kappa'], 26) == KAPPA_7546 and pr['kappa']['status'] == 'OK',
   'pricekit: #7546 = S 1424, kappa %s (certified enclosure, uniqueness proved)' % KAPPA_7546)
ok('%.4f' % float(pr['D0']) == '393242.1350' and pr['paid_jobs'] == 110468, 'pricekit: #7546 D0 393242.1350, 110468 paid jobs')
ok(pr['kappa']['hi'] - pr['kappa']['lo'] < 1e-50, 'pricekit: enclosure width < 1e-50')
p1 = pk.run(caller_path(), pk.native_from_word(word_7601(W)))['price']
ok(str(p1['kappa']['lo']).startswith(KAPPA_7601) and p1['S'] == 1424,
   'pricekit: #7601 word (rebuilt from our edit list) kappa %s' % KAPPA_7601)
sl = pk.check_slots(C, nat)
ok(all(sl[t]['law_d_eq_m'] for t in ('A', 'B')), 'pricekit: ledger law d = m holds on #7113 x #7546 (both port types)')
# negative controls
bad = dict(T=Counter({1: 1}), P=Counter({8: 1}))
ok(pk.kappa(bad['T'], bad['P'])['status'] == 'NO_CROSSING', 'pricekit NEG: S <= 0 gives NO_CROSSING, no kappa')
inv = pk.invoice(pk.caller_invoice(C), nat)
inv2 = dict(T=Counter(inv['T']), P=Counter(inv['P'])); inv2['P'][1] += 104
ok(pk.price(inv2, 30)['kappa']['lo'] < pr['kappa']['lo'], 'pricekit NEG: 104 extra rank-1 paid jobs (one per port) lower kappa')

# ---------------------------------------------------------------- kformula
C7 = pk.caller_invoice(C); c17 = kf.caller(17)
ok(c17['T'] == C7['T'] and c17['P'] == C7['P'] and C7['nJ'] == 17, 'kformula: closed-form C(17) == the #7113 caller invoice (T and P)')
ok(pk.kstr(kf.price(17, nat)['kappa'], 26) == KAPPA_7546, 'kformula: C(17) x #7546 native prices kappa(#7546)')
ok(kf.caller(16)['T'] != C7['T'], 'kformula NEG: C(16) differs from the #7113 caller')
ok(all(pk.S_of(*[pk.invoice(kf.caller(k), nat)[x] for x in ('T', 'P')]) == kf.S_closed(k) for k in range(4, 65)),
   'kformula: S(k) = 96k - 208 exactly for k = 4..64')
kap = {k: kf.price(k, nat, 20)['kappa']['lo'] for k in range(6, 41)}
kbest = max(kap, key=kap.get)
ok(kbest == 17, 'kformula: exact sweep k = 6..40 peaks at k = 17 (kappa(16) %.10f, kappa(18) %.10f)' % (kap[16], kap[18]))
ok(all(kap[k] > kap[k + 1] for k in range(17, 40)) and all(kap[k] < kap[k + 1] for k in range(6, 17)),
   'kformula: kappa(k) strictly unimodal on 6..40')
def D0_of(k):
    iv = pk.invoice(kf.caller(k), nat)
    return float(pk.Dsum(iv['T'], iv['P'], 0))
D0 = {k: D0_of(k) for k in (1000, 2000)}
beta = (D0[2000] / 2 - D0[1000]) / (1000 * math.log(2)) / 104
ok(abs(beta - 34) < 0.2, 'kformula: D0(k)/104 slope beta = 2(2h-1) = 34 (measured %.3f from k = 1000, 2000)' % beta)
s_over_d = 1424 / float(pr['D0'])
ok(abs(float(kap[17]) / s_over_d - 1.0075) < 0.0005, 'kformula: kappa(17) / (S/D0) = %.4f (first-order law kappa ~ S/D0)' % (float(kap[17]) / s_over_d))
fo = kf.first_order(17, 124.913)
ok(abs(fo / float(kap[17]) - 1) < 0.01, 'kformula: asymptotic first-order formula at k = 17 within 1%% of exact (%.7f vs %.7f)' % (fo, float(kap[17])))
eps, rho, beta_ = 2 * (1 - 56 / 104), 2, 34
gam = 1 + 124.913 / beta_ + math.log(rho / eps)
u = gam
for _ in range(60):
    u = gam + math.log(u)          # u - ln u = gamma, larger root (= -W_{-1}(-e^-gamma))
kst, kapst = rho / eps * u, eps / (beta_ * u)
ok(abs(gam - 5.4471) < 1e-3 and abs(kst - 16.15) < 0.01 and abs(kapst - 0.003641) < 2e-6 and abs(17 * kst * kapst - 1) < 1e-12,
   'kformula: Lambert optimum gamma %.4f, k* = %.2f, kappa* = %.6f, (2h-1) k* kappa* = 1 (exact family optimum k = 17)' % (gam, kst, kapst))

# ---------------------------------------------------------------- layout_price / cap_check
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(str(PKG / 'layout_price.py'), run_name='__main__')
txt = buf.getvalue()
ok('td 1.0950  sh 1.0031  rel 0.9773' in txt.split('model B (built B')[1].splitlines()[0],
   'layout_price: model B reproduces the built B caller readings 1.0950 / 1.0031 / 0.9773 [C-param]')
ok('td 1.8950  sh 1.6368  rel 1.5695' in txt, 'layout_price NEG/reference: uncapped lines give the unreachable 1.8950 / 1.6368 / 1.5695')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path(str(PKG / 'cap_check.py'), run_name='__main__')
txt = buf.getvalue()
blines = [l for l in txt.splitlines() if l.strip().startswith('boundaries:')]
ok(len(blines) == 2 and all(l.count('ry4 rx4') == 15 and '8|9:S2 ry2 rx2 cap0' in l for l in blines),
   'cap_check: on the built #7113 B, rank(Y_k,Y_k+1|S) = rank(X_k,X_k+1|S) = 4 at all 15 non-centre boundaries (q0 = 1 and i)')
fl = [l for l in txt.splitlines() if 'floor (' in l]
eq = sum(1 for l in fl for tok in l.split(': ', 1)[1].split() if tok.split(':')[1].split('/')[1] == tok.split(':')[1].split('/')[2])
ok(len(fl) == 2 and eq == 2 * 15, 'cap_check: Floor lemma rank(X_arm, hubs) = |Z_k| at every non-centre call (15 x 2)')
print('PASS_TOOLKIT_PRICING')
