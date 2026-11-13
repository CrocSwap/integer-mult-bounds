#!/usr/bin/env python3
# research/cubic-general-frames-and-2adic-obstruction/verify.py
# Author: mithrax-exo (Apache-2.0 License)
"""Zero-dependency verifier for 20 general-frame cubic repairs and odd-S 2-adic obstructions."""
import argparse
from fractions import Fraction
import json
import math
import sys

PR6653 = frozenset({6, 7, 12, 13, 21, 25, 42, 51, 52, 76, 85, 93, 97, 114, 156, 157, 160})
PR7475 = frozenset({24})

NEW_WITNESSES = [
    (48,  ((13, 184), (1, -40), (1, 24))),
    (49,  ((5, -1217), (1, -141), (1, 115))),
    (57,  ((5, -4), (1, 12), (1, 44))),
    (60,  ((5, 242), (1, -6), (1, 74))),
    (69,  ((31, 963), (1, -35), (1, 29))),
    (84,  ((11, -1235), (1, 295), (7, 2193))),
    (88,  ((5, 272), (1, -16), (1, 36))),
    (96,  ((5, -208), (1, -48), (1, 80))),
    (105, ((13, 1396), (1, 68), (7, -36))),
    (112, ((19, -120), (1, 56), (1, 88))),
    (120, ((5, 2781), (1, -263), (1, 761))),
    (121, ((37, 5067), (1, 47), (7, 73))),
    (124, ((1, 259), (1, -765), (1, -253))),
    (132, ((19, -20806), (1, 670), (7, -9390))),
    (133, ((11, 1106), (1, -10), (1, 102))),
    (148, ((19, -635), (1, -249), (11, 1357))),
    (169, ((1, 340), (1, -52), (1, 204))),
    (177, ((1, -2765), (1, -2253), (1, 1331))),
    (184, ((1, 84), (1, -160), (1, 64))),
    (192, ((7, 160), (1, 96), (1, 608))),
]

SOLVABLE_ODD_S_200 = (3, 6, 7, 11, 19, 26, 27, 42, 50, 51, 62, 90, 91, 98, 114, 155, 162)

def is_pow2(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

def odd_part(n: int) -> int:
    n = abs(n)
    return (n >> (len(bin(n)) - len(bin(n).rstrip("0")))) if n else 0

def build_odd_primes(lim: int = 400000) -> list[int]:
    sieve = bytearray(b"\x01") * (lim + 1)
    for i in range(3, int(lim ** 0.5) + 1, 2):
        if sieve[i]:
            sieve[i * i : lim + 1 : 2 * i] = b"\x00" * ((lim - i * i) // (2 * i) + 1)
    return [i for i in range(3, lim + 1, 2) if sieve[i]]

ODD_PRIMES = build_odd_primes()

def tonelli_shanks(n: int, p: int) -> int:
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return -1
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while (q & 1) == 0:
        q >>= 1
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, tmp = 1, (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, (b * b) % p, (t * b * b) % p, (r * b) % p
    return r

def factor_small(n: int) -> dict[int, int]:
    res: dict[int, int] = {}
    for p in ODD_PRIMES:
        if p * p > n:
            break
        if n % p == 0:
            c = 0
            while n % p == 0:
                n //= p
                c += 1
            res[p] = c
    if n > 1:
        res[n] = res.get(n, 0) + 1
    return res

def divs_from_fac(fac: dict[int, int]) -> list[int]:
    divs = [1]
    for p, cnt in fac.items():
        base = list(divs)
        pw = 1
        for _ in range(cnt):
            pw *= p
            divs.extend(b * pw for b in base)
    return divs

def factor_row_shears(u: int, v: int) -> list[tuple[str, int]]:
    assert math.gcd(abs(u), abs(v)) == 1 and u > 0
    aa, bb = u, v
    ops: list[tuple[str, int]] = []
    while bb != 0:
        q = aa // bb
        if q != 0:
            aa -= q * bb
            ops.append(("B+=k*A", q))
        if aa == 0:
            break
        q2 = bb // aa
        if q2 != 0:
            bb -= q2 * aa
            ops.append(("A+=k*B", q2))
    if (aa, bb) == (0, 1):
        ops.extend([("B+=k*A", -1), ("A+=k*B", 1)])
    elif (aa, bb) == (0, -1):
        ops.extend([("B+=k*A", 1), ("A+=k*B", -1)])
    elif (aa, bb) == (-1, 0):
        ops.extend([("A+=k*B", 1), ("B+=k*A", -2), ("A+=k*B", 1)])
    fwd = list(reversed(ops))
    row = [1, 0]
    for kind, k in fwd:
        row = [row[0], row[1] + k * row[0]] if kind == "A+=k*B" else [row[0] + k * row[1], row[1]]
    assert row == [u, v]
    return fwd

def verify_witness(r: int, pts: tuple[tuple[int, int], ...]) -> list[Fraction]:
    S = r * (r - 1) // 2
    two_r_1 = 2 * r - 1
    K = 6 * r * r - 6 * r - 3
    (u0, v0), (u1, v1), (u2, v2) = pts
    for u, v in pts:
        assert u > 0 and math.gcd(u, abs(v)) == 1
        factor_row_shears(u, v)
    d01, d02, d12 = u0 * v1 - u1 * v0, u0 * v2 - u2 * v0, u1 * v2 - u2 * v1
    w0, w1, w2 = 6 * v0 - two_r_1 * u0, 6 * v1 - two_r_1 * u1, 6 * v2 - two_r_1 * u2
    assert u0 * w1 * w2 + u1 * w0 * w2 + u2 * w0 * w1 + K * u0 * u1 * u2 == 0
    q0 = Fraction(-r * (r - 1) * (u1 * w2 + u2 * w1), 12 * u0 * d01 * d02)
    q1 = Fraction(r * (r - 1) * (u0 * w2 + u2 * w0), 12 * u1 * d01 * d12)
    q2 = Fraction(-r * (r - 1) * (u0 * w1 + u1 * w0), 12 * u2 * d02 * d12)
    qs = [q0, q1, q2]
    assert all(is_pow2(q.denominator) for q in qs)
    assert sum(q * (u ** 3) for q, (u, _) in zip(qs, pts)) == 0
    assert sum(3 * q * (u ** 2) * v for q, (u, v) in zip(qs, pts)) == 3 * S
    assert sum(3 * q * u * (v ** 2) for q, (u, v) in zip(qs, pts)) == S * two_r_1
    assert sum(q * (v ** 3) for q, (_, v) in zip(qs, pts)) == S * S
    norms = [w * w - K * u * u for (u, _), w in zip(pts, (w0, w1, w2))]
    m_re = w0 * w1 * w2 + K * (w0 * u1 * u2 + w1 * u0 * u2 + w2 * u0 * u1)
    assert norms[0] * norms[1] * norms[2] == m_re * m_re
    assert 144 * q1 * q2 * d01 * d02 * d12 * d12 == (r * (r - 1)) ** 2 * (-norms[0])
    return qs

def certify_odd_s_monic(r: int) -> tuple[bool, int]:
    S = r * (r - 1) // 2
    M = 2 * r * r - 2 * r - 1
    two_r_1 = 2 * r - 1
    s_fac = factor_small(odd_part(S))
    rem_arr = [odd_part(3 * (2 * k + 1) ** 2 - M) for k in range(S)]
    fac_arr = [dict(s_fac) for _ in range(S)]
    p_lim = int(math.isqrt(max(abs(3 * (2 * S - 1) ** 2 - M), M))) + 1

    for p in ODD_PRIMES:
        if p > p_lim:
            break
        if p == 3:
            if M % 3 == 0:
                for k in range(S):
                    v = rem_arr[k]
                    if v > 0 and v % 3 == 0:
                        c = 0
                        while v % 3 == 0:
                            v //= 3
                            c += 1
                        rem_arr[k] = v
                        fac_arr[k][3] = fac_arr[k].get(3, 0) + c
            continue
        inv3 = (p + 1) // 3 if p % 3 == 2 else (2 * p + 1) // 3
        rt = tonelli_shanks((M % p) * inv3 % p, p)
        if rt == -1:
            continue
        for ax_mod in {rt, (p - rt) % p}:
            k0 = ((ax_mod - 1) * ((p + 1) // 2)) % p
            for k in range(k0, S, p):
                v = rem_arr[k]
                if v > 0 and v % p == 0:
                    c = 0
                    while v % p == 0:
                        v //= p
                        c += 1
                    rem_arr[k] = v
                    fac_arr[k][p] = fac_arr[k].get(p, 0) + c
    for k in range(S):
        if rem_arr[k] > 1:
            fac_arr[k][rem_arr[k]] = fac_arr[k].get(rem_arr[k], 0) + 1

    checked = 0
    for k in range(S):
        ax = 2 * k + 1
        rem = 3 * ax * ax - M
        if rem == 0:
            for ay in divs_from_fac(factor_small(odd_part(S * ax))):
                for sx in (-1, 1):
                    x = sx * ax
                    for sy in (-1, 1):
                        y = sy * ay
                        if y == x:
                            continue
                        checked += 1
                        for w0 in (-3 * x, -x - 4 * y):
                            if (w0 + two_r_1) % 6 != 0:
                                continue
                            c0 = (w0 + two_r_1) // 6
                            q0 = Fraction(-S * (w0 + 3 * x + 3 * y), 3 * x * y)
                            q1 = Fraction(S * (w0 + 3 * y), 3 * x * (y - x))
                            q2 = Fraction(-S * (w0 + 3 * x), 3 * y * (y - x))
                            if all(is_pow2(q.denominator) for q in (q0, q1, q2)):
                                if q0 * c0 ** 3 + q1 * (c0 + x) ** 3 + q2 * (c0 + y) ** 3 == S * S:
                                    return True, checked
            continue
        y_cap = (S * ax) // (ax - S) if ax > S else None
        for ay in divs_from_fac(fac_arr[k]):
            if ay < ax or (y_cap is not None and ay > y_cap):
                continue
            for sx in (-1, 1):
                x = sx * ax
                for sy in (-1, 1):
                    y = sy * ay
                    if y == x:
                        continue
                    checked += 1
                    disc = 4 * (x * x - x * y + y * y) - M
                    if disc < 0:
                        continue
                    rt = math.isqrt(disc)
                    if rt * rt != disc:
                        continue
                    for sr in (-1, 1):
                        w0 = sr * rt - 2 * x - 2 * y
                        if (w0 + two_r_1) % 6 != 0:
                            continue
                        c0 = (w0 + two_r_1) // 6
                        q0 = Fraction(-S * (w0 + 3 * x + 3 * y), 3 * x * y)
                        q1 = Fraction(S * (w0 + 3 * y), 3 * x * (y - x))
                        q2 = Fraction(-S * (w0 + 3 * x), 3 * y * (y - x))
                        if all(is_pow2(q.denominator) for q in (q0, q1, q2)):
                            if q0 * c0 ** 3 + q1 * (c0 + x) ** 3 + q2 * (c0 + y) ** 3 == S * S:
                                return True, checked
    return False, checked

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rmax", type=int, default=60, help="Max odd-S arity to exhaust (pass 200 for full 99-arity run)")
    args = ap.parse_args()

    assert len(NEW_WITNESSES) == 20
    for r, pts in NEW_WITNESSES:
        assert r not in PR6653 and r not in PR7475
        verify_witness(r, pts)
    print("PASS_STAGE1_TWENTY_NEW_GENERAL_WITNESSES")

    solvable_expected = {r for r in SOLVABLE_ODD_S_200 if r <= args.rmax}
    solvable_found = set()
    impossible_found = []
    for r in range(3, args.rmax + 1):
        if ((r * (r - 1)) // 2) % 2 == 0:
            continue
        ok, _ = certify_odd_s_monic(r)
        if ok:
            solvable_found.add(r)
        else:
            impossible_found.append(r)
    assert solvable_found == solvable_expected, f"Mismatch: {solvable_found} != {solvable_expected}"
    for key_r in (15, 22, 30, 31):
        if key_r <= args.rmax:
            assert key_r in impossible_found
    print(f"PASS_STAGE2_UNCONDITIONAL_MONIC_OBSTRUCTION_RMAX_{args.rmax}")
    print(json.dumps({
        "status": "PASS",
        "new_general_arities": [r for r, _ in NEW_WITNESSES],
        "rmax_certified": args.rmax,
        "odd_s_solvable": sorted(solvable_found),
        "odd_s_impossible_count": len(impossible_found),
    }))
    return 0

if __name__ == "__main__":
    sys.exit(main())
