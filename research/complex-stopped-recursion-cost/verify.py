#!/usr/bin/env python3
"""Verifier for the #4100 COMPLEX.md stopped-recursion cost audit.

JoyboyBrian, with substantial assistance from Anthropic Claude (Claude Code).
Apache-2.0. Python 3.12 standard library only.

Checks, in order:
  1. Source binding: the histogram, W, root b, q, a_eff, eta, stop rule and
     child rule are read from the pinned COMPLEX.md; a2 from PROOF.md.
  2. Exponent order used by PROOF.md section 1: 1-a2 < tau < 1-q and
     1-b+eta*b < 1-q, exactly over the rationals.
  3. Certified rational enclosures of mu_tau and mu_(1-b) (outward-rounded
     atanh/exp series), giving mu_(1-b) < 1, mu_tau < 1 and an enclosure of
     the uniform constant 1/(1-mu_tau).
  4. Rejection controls: a root above the certified bracket, one extra
     rank-48 child per W, and the ceiling child rule all fail.
  5. Finite numerical corroboration (Decimal, 60 digits) of the two tree
     sums that the written induction bounds, on complete recursion trees.
The all-size statement is the written proof in PROOF.md; items 3-5 do not
replace it.
"""
from decimal import Decimal, getcontext
from fractions import Fraction as F
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'research' / 'unconditional-batched-crt'
GRID = 10 ** 110


def fail(message):
    print('FAIL_COMPLEX_STOPPED_RECURSION_COST: ' + message)
    sys.exit(1)


def check(condition, message):
    if not condition:
        fail(message)


def flat(path):
    return ' '.join(path.read_text(encoding='utf-8').split())


# ---------------------------------------------------------------- sources
complex_md = flat(SRC / 'COMPLEX.md')
proof_md = flat(SRC / 'PROOF.md')

hist_match = re.search(r'exact paid histogram is \{([0-9:,]+)\}', complex_md)
check(hist_match is not None, 'histogram sentence not found in COMPLEX.md')
HIST = {int(k): int(v) for k, v in (item.split(':') for item in hist_match.group(1).split(','))}
check(HIST == {1: 8060060, 2: 2310120, 3: 751813, 4: 327210, 5: 66425, 8: 25920, 48: 138492},
      'unexpected histogram')
w_match = re.search(r'Set W=(\d+) and', complex_md)
check(w_match is not None, 'W not found')
W = int(w_match.group(1))
check(W == 322560, 'unexpected W')
b_match = re.search(r'Let b=\.(\d+);', complex_md)
check(b_match is not None, 'root b not found')
B_ROOT = F(int(b_match.group(1)), 10 ** len(b_match.group(1)))
a2_match = re.search(r'a2=\.(\d+)\.', proof_md)
check(a2_match is not None, 'a2 not found in PROOF.md')
A2 = F(int(a2_match.group(1)), 10 ** len(a2_match.group(1)))
for sentence in ('Put q=b-10^-28, a_eff=(b+q)/2, eta=10^-32 and tau=1-a_eff.',
                 'Stop at width max(73,h^eta).',
                 'Every child r floor(e/73), r<=48, decreases D',
                 'all adapters, monomials, packet scans and parking cost O(V e^(1-a2) polylog(p))',
                 'O(V h^(1-q) polylog(p))',
                 'The placement and its inverse cost O(V h^(1-a2) polylog(p)+V polylog(p)).'):
    check(sentence in complex_md, 'COMPLEX.md sentence missing: ' + sentence)
check('Each transform costs O(V ell d^(1-q) polylog(p)).' in proof_md, 'PROOF.md caller sentence missing')

Q = B_ROOT - F(1, 10 ** 28)
A_EFF = (B_ROOT + Q) / 2
ETA = F(1, 10 ** 32)
TAU = 1 - A_EFF

# ------------------------------------------------------- exponent order
check(A_EFF < A2, 'need a_eff < a2, so that e^(1-a2) <= e^tau')
check(Q < A_EFF, 'need q < a_eff, so that tau < 1-q')
check(ETA * B_ROOT < B_ROOT - Q, 'need 1-b+eta*b < 1-q')
check(0 < Q, 'need q > 0')
# remainder absorption: 72 <= 74^tau, via a_eff < 1/200 and 74^199 >= 72^200
check(A_EFF < F(1, 200) and 74 ** 199 >= 72 ** 200, 'need 72 <= e^tau for every internal width e >= 74')


# ---------------------------------------------- certified enclosures
def down(x):
    return F((x.numerator * GRID) // x.denominator, GRID)


def up(x):
    return F(-((-x.numerator * GRID) // x.denominator), GRID)


def atanh_inv(m):
    """Enclosure of atanh(1/m) for an integer m >= 3."""
    lo = hi = F(0)
    power, k = F(1, m), 0        # power = m^-(2k+1), exact (denominator is a power of m)
    while power > F(10 ** 10, GRID):
        lo += down(power / (2 * k + 1))
        hi += up(power / (2 * k + 1))
        power /= m * m
        k += 1
    return lo, up(hi + power / ((2 * k + 1) * (1 - F(1, m * m))))


def iadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def iscale(c, x):
    return (c * x[0], c * x[1]) if c >= 0 else (c * x[1], c * x[0])


def two_atanh(m):
    return iscale(2, atanh_inv(m))


LN2 = two_atanh(3)            # ln 2
LN32 = two_atanh(5)           # ln 3/2
LN54 = two_atanh(9)           # ln 5/4
LN7372 = two_atanh(145)       # ln 73/72
LN3 = iadd(LN2, LN32)
LN = {1: (F(0), F(0)), 2: LN2, 3: LN3, 4: iscale(2, LN2), 5: iadd(iscale(2, LN2), LN54),
      8: iscale(3, LN2), 48: iadd(iscale(4, LN2), LN3)}
LN73 = iadd(iadd(iscale(3, LN2), iscale(2, LN3)), LN7372)
L73 = {r: (LN73[0] - LN[r][1], LN73[1] - LN[r][0]) for r in LN}   # ln(73/r) > 0


def exp_bounds(y):
    """Enclosure of exp(y) for 0 <= y <= 8 (positive Taylor terms)."""
    lo = hi = F(0)
    t_lo = t_hi = F(1)           # outward-rounded n-th Taylor terms y^n/n!
    n = 0
    while t_hi > F(10 ** 10, GRID) or n < 2 * int(y) + 4:
        lo += t_lo
        hi += t_hi
        n += 1
        t_lo, t_hi = down(t_lo * y / n), up(t_hi * y / n)
    # remaining tail <= t_hi / (1 - y/(n+1)) once n+1 > 2y
    return lo, up(hi + t_hi / (1 - y / (n + 1)))


def power_ratio(r, x):
    """Enclosure of (r/73)^x = exp(-x ln(73/r)) for rational x > 0."""
    if r == 73:
        return F(1), F(1)
    lo_y, hi_y = x * L73[r][0], x * L73[r][1]
    return down(1 / exp_bounds(up(hi_y))[1]), up(1 / exp_bounds(down(lo_y))[0])


def mu(x, hist=None):
    hist = HIST if hist is None else hist
    lo, hi = F(0), F(0)
    for r, count in hist.items():
        p_lo, p_hi = power_ratio(r, x)
        lo += F(count, W) * p_lo
        hi += F(count, W) * p_hi
    return lo, hi


MU_EDGE = mu(1 - B_ROOT)
check(MU_EDGE[1] < 1, 'mu_(1-b) < 1 not certified')
MU_TAU = mu(TAU)
check(MU_TAU[1] < 1, 'mu_tau < 1 not certified')
GAP = (1 - MU_TAU[1], 1 - MU_TAU[0])
check(GAP[1] - GAP[0] < GAP[0] / 10 ** 12, 'enclosure of 1-mu_tau is not sharp enough')
K_LO, K_HI = 1 / GAP[1], 1 / GAP[0]
K_WINDOW = (F(70535 * 10 ** 23), F(70536 * 10 ** 23))   # PROOF.md fact 3
check(K_WINDOW[0] < K_LO and K_HI < K_WINDOW[1], '1/(1-mu_tau) outside the stated window')

# ------------------------------------------------------- controls
BAD_ROOT = B_ROOT + F(1, 10 ** 47)
check(mu(1 - BAD_ROOT)[0] > 1, 'control: a root above the bracket should make mu_(1-b) > 1')
extra = dict(HIST)
extra[48] += 1
check(mu(TAU, extra)[0] > 1, 'control: one extra rank-48 child per W should break mu_tau < 1')
check(mu(1 - B_ROOT, extra)[0] > 1, 'control: one extra rank-48 child per W should break mu_(1-b) <= 1')
ceil_bad = [e for e in range(74, 2000) if 48 * (-(-e // 73)) >= e]
check(ceil_bad and ceil_bad[0] == 74 and 48 * 2 == 96, 'control: ceiling child rule should grow width 74 to 96')
check(all(48 * (e // 73) < e and e // 73 >= 1 for e in range(74, 200000)),
      'floor child rule must shrink every internal width')

# ------------------------------------- finite numerical corroboration
getcontext().prec = 60
D_TAU = Decimal(TAU.numerator) / Decimal(TAU.denominator)
D_EDGE = 1 - Decimal(B_ROOT.numerator) / Decimal(B_ROOT.denominator)
D_A2 = 1 - Decimal(A2.numerator) / Decimal(A2.denominator)
WEIGHTS = [(r, Decimal(c) / Decimal(W)) for r, c in sorted(HIST.items())]


def tree_sums(h, stop):
    """Return (internal tau-sum, frontier (1-b)-sum, unit-cost total) per unit root volume.

    Unit-cost model: internal node own cost e^(1-a2) + (e mod 73), leaf cost e.
    """
    memo = {}

    def walk(e):
        if e in memo:
            return memo[e]
        de = Decimal(e)
        if e <= stop:
            out = (Decimal(0), de ** D_EDGE, de)
        else:
            f = e // 73
            internal, frontier, cost = de ** D_TAU, Decimal(0), de ** D_A2 + (e - 73 * f)
            for r, weight in WEIGHTS:
                ci, cf, cc = walk(r * f)
                internal += weight * ci
                frontier += weight * cf
                cost += weight * cc
            out = (internal, frontier, cost)
        memo[e] = out
        return out

    return walk(h)


SAMPLES = [74, 100, 146, 1000, 5329, 10 ** 4, 389017, 10 ** 6, 10 ** 9, 10 ** 12]
rows = []
for stop in (73, 500, 5000):
    for h in (SAMPLES if stop == 73 else SAMPLES[:8]) + list(range(75, 1500, 37)):
        internal, frontier, cost = tree_sums(h, stop)
        dh = Decimal(h)
        check(frontier <= dh ** D_EDGE * (1 + Decimal(10) ** -40), 'frontier (1-b)-sum exceeds h^(1-b)')
        k1 = Decimal(K_HI.numerator) / Decimal(K_HI.denominator)
        bound = 2 * k1 * dh ** D_TAU + dh ** D_EDGE * Decimal(max(stop, 1)) ** (1 - D_EDGE)
        check(cost <= bound, 'unit-cost total exceeds the written bound')
        check(internal <= k1 * dh ** D_TAU, 'internal tau-sum exceeds h^tau/(1-mu_tau)')
        if stop == 73 and h in SAMPLES and h not in [row[0] for row in rows]:
            rows.append((h, float(internal / dh ** D_TAU), float(frontier / dh ** D_EDGE),
                         float(cost / dh ** (1 - Decimal(Q.numerator) / Decimal(Q.denominator)))))

print('mu_(1-b) in [1-%.6e, 1-%.6e]' % (float(1 - MU_EDGE[0]), float(1 - MU_EDGE[1])))
print('1-mu_tau in [%.12e, %.12e]; 1/(1-mu_tau) in [%.6e, %.6e]'
      % (float(GAP[0]), float(GAP[1]), float(K_LO), float(K_HI)))
print('h, internal/h^tau, frontier/h^(1-b), unit cost/h^(1-q) at stop 73:')
for row in rows:
    print('  %-26d %10.4f %10.6f %10.4f' % row)
print('PASS_COMPLEX_STOPPED_RECURSION_COST')
