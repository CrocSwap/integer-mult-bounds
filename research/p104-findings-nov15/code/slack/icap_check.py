"""[C-param] SLACK icap_check.py: the interval-capped line pricing correction (SLACK PROOF A), on a pinned handful of layouts.
Old pricer: caps only two-stage lines (per-boundary |S|-4). Corrected: every interval I gets N(I) <= |Z_I| - 4 (r = 4, the Crossing rank;
Extended Crossing Lemma, PROOF B/E). All prices are min over the three native columns (twins deleted / shadows / shadows+2 relays) of kappa/kappa_B.
Asserts, with the numbers quoted in README section 3:
  - the nested B layout is unchanged by the correction (1.0950 / 1.0031 / 0.9773 both ways) [control];
  - 'B + one lone extra role' prices > +0.15% (+0.20 to +0.59) with the old boundary caps and <= 0 with interval caps (all four layouts tested);
  - pair k=0 d=4 + slack 1..4: +1.56% old -> +0.20% corrected (r=4 only on intervals where the Crossing Lemma applies).
Prints PASS_ICAP."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icap import *
from layout_price import invoice
def capS(ms):
    cap = []
    for k in range(L - 1):
        if k == nl - 1: cap.append(0); continue
        S = sum(1 for m in ms if k in m and k + 1 in m); cap.append(max(S - 4, 0))
    return cap
def dying(c, k, d):
    ms = two_arm(); full = set(range(k, nl))
    for _ in range(c): ms.remove(full); ms.append(set(range(k, d + 1)))
    return ms
def mk_r(ms, rfail):
    Z = [frozenset(i for i, m in enumerate(ms) if k in m) for k in range(L)]
    def r(a, b):
        ZI = frozenset.intersection(*Z[a:b + 1])
        if any(Z[k] <= ZI or Z[k + 1] <= ZI for k in range(a, b)): return 4
        return rfail
    return r
def old(ms): T, P, Z = invoice(ms, L, capS(ms)); return price(T, P, '', quiet=True)
def new(ms): T, P, Z = invoice_iv(ms, mk_r(ms, 4)); return price(T, P, '', quiet=True)
B_old = old(two_arm()); B_new = new(two_arm())
print('B control old', ['%.4f' % x for x in B_old], 'interval', ['%.4f' % x for x in B_new])
assert ['%.4f' % x for x in B_old] == ['%.4f' % x for x in B_new] == ['1.0950', '1.0031', '0.9773']
g = lambda x: 100 * (min(p / q for p, q in zip(x, B_old)) - 1)
for je, ee in ((1, 3), (0, 4), (2, 5), (3, 6)):
    ms = two_arm(); ms.append(set(range(je, ee + 1)))
    a, b = g(old(ms)), g(new(ms)); print('B + lone %d..%d  old %+.2f  interval %+.2f' % (je, ee, a, b))
    assert a > 0.15 and b <= 0.0
ms = dying(2, 0, 4); ms.append(set(range(1, 5)))
a, b = g(old(ms)), g(new(ms)); print('pair k=0 d=4 + slack 1..4  old %+.2f  interval %+.2f' % (a, b))
assert abs(a - 1.56) < 0.006 and abs(b - 0.20) < 0.006
print('PASS_ICAP')
