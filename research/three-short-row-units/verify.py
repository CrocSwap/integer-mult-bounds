#!/usr/bin/env python3
"""Three short rows and unit coefficients (#4600 open question 2, petalas), exact for m <= 13.

Model: #4280's row model as restated in #4600 (profiles lambda, rho, beta with m nonincreasing entries in [0, m];
correct iff sum L = sum rho = sum beta = sum rho L = sum B(L) = 0 and sum rho B(L) = -c (mod m)). #4600 proves that
unit c needs at least three short rows and asks whether three suffice for every unit when m >= 6.

This verifier enumerates the model exactly (every nonincreasing rho and beta, every lambda with exactly three short
rows L1 >= L2 >= L3, L1 + L2 + L3 = 0 mod m, preceded by f full rows) and finds, for each m <= 13:
  * m <= 5: no nonzero coefficient at all is realized with three short rows (so no unit);
  * 6 <= m <= 13: every unit is realized with exactly three short rows.
So the answer to #4600's open question 2 is yes for 6 <= m <= 13, and the threshold m >= 6 is sharp.
Further, the single shape lambda = (m-1, m-2, 3), rho = (m, a, b, padding) (one (a, b) per target, beta exact by a
dynamic programme) realizes every unit for 7 <= m <= 30; and an explicit construction with rho = (m, 3, 2, 1^(m-5),
0, 0), beta = (balanced block of sum u + 2m, middle of length m - 5 with sum = -2(u + 2m) mod m just above (m-5)u,
u, 0) realizes every c = u with 1 <= u <= m - 2; with rho = (m, 3t, 2t, padding) for a unit 2 <= t < m/3 it also
realizes c = -1. Such t exists for every m >= 14 (t = 2 for odd m; t = 3 if 3 does not divide m; otherwise the
smallest prime p not dividing m satisfies 3p < m). Checked for every nonzero c and 14 <= m <= 200. With the exact
enumeration for m <= 13: three short rows realize every unit for every m >= 6, every nonzero c for every m >= 7.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from math import gcd
import json
import sys


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def profiles(m):
    out = []

    def rec(prefix, top):
        if len(prefix) == m:
            out.append(tuple(prefix))
            return
        for v in range(top, -1, -1):
            prefix.append(v)
            rec(prefix, v)
            prefix.pop()
    rec([], m)
    return out


def three_row_coefficients(m):
    balanced = [p for p in profiles(m) if sum(p) % m == 0]
    rho = {f: {(p[f] % m, p[f + 1] % m, p[f + 2] % m) for p in balanced} for f in range(m - 2)}
    prefixes = []
    for p in balanced:
        pre = [0]
        for v in p:
            pre.append(pre[-1] + v)
        prefixes.append([x % m for x in pre])
    found = set()
    for l1 in range(1, m):
        for l2 in range(1, l1 + 1):
            for l3 in range(1, l2 + 1):
                if (l1 + l2 + l3) % m:
                    continue
                bs = {(pr[l1], pr[l2], pr[l3]) for pr in prefixes if (pr[l1] + pr[l2] + pr[l3]) % m == 0}
                for f in range(m - 2):
                    for a, b, c in rho[f]:
                        if (a * l1 + b * l2 + c * l3) % m == 0:
                            for x, y, z in bs:
                                v = -(a * x + b * y + c * z) % m
                                if v:
                                    found.add(v)
    return found


def template_units(m):
    """Units realized by the fixed shape lambda = (m-1, m-2, 3), rho = (m, a, b, padding <= b, ...), exact over beta."""
    states = {(m, 0, None)}
    for i in range(1, m + 1):
        nxt = set()
        for last, s, info in states:
            for v in range(last + 1):
                s2 = (s + v) % m
                if i == 3:
                    inf = s2
                elif i == m - 2:
                    inf = (info, s2)
                elif i == m - 1:
                    inf = (info[0], info[1], (info[0] + info[1] + s2) % m)
                else:
                    inf = info
                nxt.add((v, s2, inf))
        states = nxt
    xy = {(x, y) for _, s, (x, y, t) in states if s == 0 and t == 0}
    got = set()
    for a in range(m + 1):
        for b in range(a + 1):
            pad = -(m + a + b) % m
            if (a * (m - 2) + 3 * b) % m == 0 and any(k % m == pad for k in range(b * (m - 3) + 1)):
                got |= {-(a * y + b * x) % m for x, y in xy}
    return got


def even_split(total, n):
    q, r = divmod(total, n)
    return [q + 1] * r + [q] * (n - r)


def multiplier(m, c):
    """t = 1 unless c = -1; then a unit 2 <= t < m/3 (t = 2 for odd m, else the smallest prime not dividing m)."""
    if c != m - 1:
        return 1
    return next(t for t in range(2, m) if 3 * t < m and gcd(t, m) == 1)


def construction(m, c):
    """Explicit three-short-row profiles realizing any nonzero c (m >= 14): rho = (m, 3t, 2t, padding),
    B(3) = X with X = c / t (mod m) in [1, m - 2], coefficient (3t - 2t) X = c."""
    t = multiplier(m, c)
    x = c * pow(t, -1, m) % m
    need(1 <= x <= m - 2, "X avoids -1 because t != 1 when c = -1")
    lam = [m - 1, m - 2, 3] + [0] * (m - 3)
    pad = -(m + 5 * t) % m
    need(pad <= 2 * t * (m - 3), "rho padding")
    rho = [m, 3 * t, 2 * t] + even_split(pad, m - 3)
    first = even_split(x + 2 * m, 3)
    low = (m - 5) * x
    mid_sum = low + (-2 * (x + 2 * m) - low) % m
    need(mid_sum <= (m - 5) * first[-1], "middle fits under the first block")
    beta = first + even_split(mid_sum, m - 5) + [x, 0]
    for p in (lam, rho, beta):
        need(len(p) == m and all(0 <= v <= m for v in p) and all(a >= b for a, b in zip(p, p[1:])), "profile")
    pre = [0]
    for v in beta:
        pre.append(pre[-1] + v)
    need(sum(lam) % m == sum(rho) % m == sum(beta) % m == 0, "sums")
    need(sum(a * l for a, l in zip(rho, lam)) % m == 0 and sum(pre[l] for l in lam) % m == 0, "weighted sums")
    need(-sum(a * pre[l] for a, l in zip(rho, lam)) % m == c, "coefficient")


def main():
    table = {}
    for m in range(2, 14):
        found = three_row_coefficients(m)
        units = {c for c in range(1, m) if gcd(c, m) == 1}
        if m <= 5:
            need(not found, "m <= 5: nothing realized with three short rows")
        else:
            need(units <= found, "m = %d: every unit realized with three short rows" % m)
        table[m] = sorted(found)
    for m in range(14, 201):
        for c in range(1, m):
            construction(m, c)
    for m in range(7, 31):
        need({c for c in range(1, m) if gcd(c, m) == 1} <= template_units(m), "fixed-shape template, m = %d" % m)
    print(json.dumps({"status": "PASS_THREE_SHORT_ROW_UNITS", "realized_by_m": table, "template_m_range": [7, 30], "new_kappa_claimed": False},
                     indent=1))


if __name__ == "__main__":
    sys.exit(main())
