"""Exact arithmetic of the closure statements (standard library only; Fractions).  Re-derives numbers the README quotes from the cards PUNCT4/5,
PUNCTTHEORY, PUNCT-MID (puncture bars, E7q closure table, Theorem M8 case arithmetic, template 7m-2beta) and the f(s) >= 7s table.  It re-derives ARITHMETIC from the cards' stated inputs; the inputs themselves are the cards' results."""
from fractions import Fraction as Fr
import math
ok = True
def chk(name, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + extra if extra else '')); ok &= bool(cond)
x9 = Fr(54, 102)
def need(p): return math.ceil(x9 * (120 - p))          # smallest cost that does not beat 54/102 * v   (win <=> cost < x9*v)
chk('1.bar p=45 : 54/102*75 = 39.70..., need cost >= 40', x9 * 75 == Fr(675, 17) and need(45) == 40)
chk('1.bar p=46 : 666/17 = 39.17..., need >= 40', x9 * 74 == Fr(666, 17) and need(46) == 40)
chk('1.bar p=47 : 657/17 = 38.64..., need >= 39', x9 * 73 == Fr(657, 17) and need(47) == 39)
chk('1.need(p), p=48..56 = 39,38,38,37,36,36,35,35,34 (PUNCTTHEORY Thm M8)', [need(p) for p in range(48, 57)] == [39, 38, 38, 37, 36, 36, 35, 35, 34])
# template cost >= 7m - 2*beta, beta <= floor((55 - c_p)/2), c_p = need - 1 (largest winning cost)
for p in (45, 46, 47):
    c = need(p) - 1; beta = (55 - c) // 2
    chk('1.template p=%d: m>=8, beta<=%d: 7m-2beta >= %d >= need %d' % (p, beta, 56 - 2 * beta, need(p)), beta == 8 and 56 - 2 * beta >= need(p))
# E7q: cost >= 49 - 2q; Q(p) = largest q with 49 - 2q >= need (p = 56 uses h(K)=9 as proved in PUNCTTHEORY 2.3)
Q = {p: max(q for q in range(0, 10) if 49 - 2 * q >= need(p)) for p in range(47, 57)}
chk('1.E7q Q(p) = 5,5,5,5,6,6,6,7,7,7 for p = 47..56', [Q[p] for p in range(47, 57)] == [5, 5, 5, 5, 6, 6, 6, 7, 7, 7], str(Q))
# Theorem M8 case A: m=8 : 35 + (9 - smax); m>=9 : 5(m-2) + 2(9 - smax)
def smax(p): return 5 if p <= 49 else (6 if p <= 51 else 8)
okA = True
for p in range(48, 57):
    for m in range(8, 40):
        c = 35 + (9 - smax(p)) if m == 8 else 5 * (m - 2) + 2 * (9 - smax(p))
        okA &= c >= need(p)
chk('1.M8 case A: 35+(9-smax) = 39,38,36 style bounds and 5(m-2)+2(9-smax) >= need(p), p=48..56, m=8..39', okA)
okB = all(5 * m >= need(p) for p in range(48, 54) for m in range(8, 40))
okB &= all((40 - 5 if m == 8 else 5 * m - 10) >= need(p) for p in (54, 55, 56) for m in range(8, 40))
chk('1.M8 case B: p<=53 5m >= need; p=54..56 with |Q|<=5: 40-|Q| and 5m-2|Q| >= need', okB)
# the 571 + sums
chk('1.p=46 leaf table sum 16+29+92+197+148+51+28+10 = 571', 16 + 29 + 92 + 197 + 148 + 51 + 28 + 10 == 571)
# f(s) >= 7 s
f = {1: 8, 2: 14, 3: 23, 4: 32, 5: 38, 6: 46, 7: 52, 8: 56}
chk('1.f(s) >= 7s for s=1..8 from the table f(1..8) = 8,14,23,32,38,46,52,56 (f(6) >= 46 is the #2338 DRAT value; PUNCTTHEORY quotes 42, also >= 42 = 7*6)',
    all(f[s] >= 7 * s for s in f) and 42 >= 7 * 6)
# Lemma CA numbers (E7 minus frame support): 16 s/3
chk('1.Lemma CA E7 support: |R|=32, omega=6 => f(s) >= 16 s/3 ; s/f(s) <= 3/16', Fr(32 * 1, 6) == Fr(16, 3))
raise SystemExit(0 if ok else 1)
