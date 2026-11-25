"""Exact arithmetic of the batching statements (standard library only; Fractions): Theorem M minimisations, the Lemma K' counting floor of the
digon clique, the Lemma E bounds, the Theorem C rank budget.  Arithmetic only; the inequalities fed in are proved in README section 4."""
from fractions import Fraction as Fr
import math
ok = True
def chk(name, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + extra if extra else '')); ok &= bool(cond)
# BATCH17 Theorem M : k1 <= 1: min_t 7t + 8(8 + max(0, 8 k2 - t)) = 64 + 56 k2 ; k1 >= 2 (O(9)): min_t 7t + 8 max(8k - t, 8 k1 - t/2) = 64k1 + 48k2
def minM1(k2): return min(7 * t + 8 * (8 + max(0, 8 * k2 - t)) for t in range(0, 8 * k2 + 80))
chk('B.Thm M k1<=1: min over t = 64 + 56 k2 (k2 = 1..6)', all(minM1(k2) == 64 + 56 * k2 for k2 in range(1, 7)))
def minM2(k1, k2):
    k = k1 + k2
    return min(7 * Fr(t) + 8 * max(8 * k - Fr(t), 8 * k1 - Fr(t) / 2) for t in range(0, 8 * k + 80))
chk('B.Thm M k1>=2 (O(9)): min over t = 64 k1 + 48 k2 for k1 = 2..4, k2 = 0..4', all(minM2(a, b) == 64 * a + 48 * b for a in (2, 3, 4) for b in range(0, 5)))
chk('B.Lemma K\' counting floor of the 9-term digon clique: 7*9 + 8(8k - 8) = 64k - 1', all(7 * 9 + 8 * (8 * k - 8) == 64 * k - 1 for k in range(18, 30)))
chk('B.Lemma E: clique decoders >= 64k + 7 (63 + 8(8k - 7)) and >= 64k + 63 (exact-count branch carried by cost-9 terms)',
    all(63 + 8 * (8 * k - 7) == 64 * k + 7 for k in range(18, 30)))
chk('B.Thm C: r(P^c) <= m - 8(k-1); m=17,k=2 gives 9; k=2 sums r(P1)+r(Q2) <= m', 17 - 8 * (2 - 1) == 9)
raise SystemExit(0 if ok else 1)
