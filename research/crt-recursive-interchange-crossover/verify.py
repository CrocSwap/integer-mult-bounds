"""Crossover width and reservoir length for the recursive ordinary interchange.

Two engines decide the least width H with H**a2 > rho: a rigorous fixed-point
interval logarithm (integer arithmetic only) and Python's correctly rounded
decimal ln/exp. The layout search then finds the least accepted #4174
reservoir length L whose width H = floor(L/(100G))*G reaches a given width.
Standard library only. Exit status 0 means every check passed.
"""
from __future__ import annotations

import decimal
import hashlib
import json
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[2]
PKG = pathlib.Path(__file__).resolve().parent

C_BIT = Fraction(8667, 5000000)
A2 = C_BIT * (1 - C_BIT * C_BIT)
H_BRANCH = 27706412  # PR4942: least binary width on BIT.md's recursive branch
D_MIN_EXPONENT = 16  # least power of two d >= 51200
RHOS = ["1/2", "1", "103/100", "1031/1000", "1032/1000", "21/20", "11/10",
        "3/2", "2", "4", "10"]


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit("FAIL: " + msg)


# ---------- engine 1: rigorous fixed-point interval logarithm ----------

def _atanh_bounds(num: int, den: int, prec: int) -> tuple[int, int]:
    """Integers lo, hi with lo <= 2**prec * atanh(num/den) <= hi, 0<=num/den<=1/3."""
    need(0 <= 3 * num <= den, "atanh argument outside [0,1/3]")
    one = 1 << prec
    if num == 0:
        return 0, 0
    z_lo = (num * one) // den
    z_hi = -((-num * one) // den)
    z2_lo = (z_lo * z_lo) >> prec
    z2_hi = -((-(z_hi * z_hi)) >> prec)
    lo = hi = 0
    p_lo, p_hi = z_lo, z_hi
    j = 0
    while p_hi > 2:
        lo += p_lo // (2 * j + 1)
        hi += -((-p_hi) // (2 * j + 1))
        p_lo = (p_lo * z2_lo) >> prec
        p_hi = -((-(p_hi * z2_hi)) >> prec)
        j += 1
    # Floors of lower bounds stay lower bounds; ceilings stay upper bounds.
    # Tail: sum_{i>=j} z^(2i+1)/(2i+1) <= z^(2j+1)/(1-z^2) <= (9/8) p_hi ulps.
    return lo, hi + 4


def ln_bounds(x: Fraction, prec: int) -> tuple[int, int]:
    """Integers lo, hi with lo <= 2**prec * ln(x) <= hi, for rational x > 0."""
    need(x > 0, "ln of nonpositive value")
    e = x.numerator.bit_length() - x.denominator.bit_length()
    y = x / (Fraction(2) ** e)
    while y >= 2:
        y /= 2
        e += 1
    while y < 1:
        y *= 2
        e -= 1
    z = (y - 1) / (y + 1)  # in [0, 1/3)
    a_lo, a_hi = _atanh_bounds(z.numerator, z.denominator, prec)
    l2_lo, l2_hi = _atanh_bounds(1, 3, prec)
    lo = 2 * a_lo + (2 * e * l2_lo if e >= 0 else 2 * e * l2_hi)
    hi = 2 * a_hi + (2 * e * l2_hi if e >= 0 else 2 * e * l2_lo)
    return lo, hi


def power_exceeds(h: int, rho: Fraction) -> bool:
    """Exact decision of h**a2 > rho via certified intervals (fails if unresolved)."""
    need(h >= 1 and rho > 0, "power_exceeds domain")
    if h == 1:
        return rho < 1  # 1**a2 = 1 exactly
    prec = 2 * h.bit_length() + 2 * max(rho.numerator.bit_length(), rho.denominator.bit_length()) + 128
    hl, hh = ln_bounds(Fraction(h), prec)
    rl, rh = ln_bounds(rho, prec)
    a, b = A2.numerator, A2.denominator
    left_lo = (hl * a) // b if hl >= 0 else -((-hl * a + b - 1) // b)
    left_hi = -((-hh * a) // b) if hh >= 0 else -((-hh * a) // b)
    if left_lo > rh:
        return True
    if left_hi < rl:
        return False
    raise SystemExit(f"FAIL: unresolved comparison h={h} rho={rho}")


# ---------- engine 2: correctly rounded decimal ln/exp ----------

def least_width_decimal(rho: Fraction) -> int:
    """Candidate least H with H**a2 > rho from decimal ln/exp."""
    if rho < 1:
        return 1
    if rho == 1:
        return 2
    ctx = decimal.Context(prec=60)
    lr = ctx.ln(ctx.divide(decimal.Decimal(rho.numerator), decimal.Decimal(rho.denominator)))
    x = ctx.divide(lr, ctx.divide(decimal.Decimal(A2.numerator), decimal.Decimal(A2.denominator)))
    digits = int(x / decimal.Decimal(2.302585)) + 40
    ctx = decimal.Context(prec=digits + 40)
    lr = ctx.ln(ctx.divide(decimal.Decimal(rho.numerator), decimal.Decimal(rho.denominator)))
    x = ctx.divide(lr, ctx.divide(decimal.Decimal(A2.numerator), decimal.Decimal(A2.denominator)))
    return int(ctx.exp(x).to_integral_value(rounding=decimal.ROUND_FLOOR)) + 1


def least_width(rho: Fraction) -> int:
    """Least integer H >= 1 with H**a2 > rho, certified by engine 1."""
    h = least_width_decimal(rho)
    need(power_exceeds(h, rho), f"engine 1 rejects candidate {h} for rho={rho}")
    if h > 1:
        need(not power_exceeds(h - 1, rho), f"engine 1 finds smaller width than {h} for rho={rho}")
    return h


# ---------- layout search over the #4174 accepted domain ----------

def least_length(h_star: int) -> tuple[int, dict]:
    """Least L = sum w_i over accepted layouts with floor(L/(100G))*G >= h_star.

    Domain (crt-reservoir-placement README): d = 2**s >= 51200, integers
    2 <= m <= ell with m = ceil(log2(p+2)) for some p >= 1, every w_i in
    {ell-1, ell}, so L ranges over all integers in [d(ell-1), d*ell];
    G = 64(ell+m) = 64k with ell+2 <= k <= 2*ell.
    """
    best = None
    witness: dict = {}
    k = 4
    while True:
        g = 64 * k
        r = -(-h_star // g)
        t = 100 * g * r  # least L with floor(L/(100G)) >= r
        if best is not None and 6400 * k > best:
            break  # t >= 6400k and every L >= t for this and larger k
        ell_min, ell_max = (k + 1) // 2, k - 2
        if ell_min <= ell_max:
            # d*ell >= t needs d >= t/ell_max; start at the first such power of two
            s = max(D_MIN_EXPONENT, (-(-t // ell_max) - 1).bit_length())
            while True:
                d = 1 << s
                ell_t = max(-(-t // d), 1)
                if ell_t > ell_max:
                    s += 1
                    continue
                if ell_t >= ell_min:
                    cand, ell = t, ell_t
                else:
                    ell = ell_min
                    cand = max(t, d * (ell - 1))
                if best is None or cand < best:
                    best = cand
                    witness = {"L": cand, "d": d, "ell": ell, "m": k - ell, "G": g,
                               "r_max": cand // (100 * g), "H": (cand // (100 * g)) * g}
                if ell_t <= ell_min:
                    break  # larger d only raises d*(ell_min-1)
                s += 1
        k += 1
    need(best is not None, "no accepted layout")
    return best, witness


def check_layout_witness(w: dict, h_star: int) -> None:
    d, ell, m, L = w["d"], w["ell"], w["m"], w["L"]
    need(d >= 51200 and d & (d - 1) == 0, "d not an admissible power of two")
    need(2 <= m <= ell, "m outside [2, ell]")
    p = (1 << (m - 1)) - 1 if m > 2 else 1
    need(p >= 1 and (p + 1).bit_length() == m, "no p with ceil(log2(p+2)) = m")
    need(d * (ell - 1) <= L <= d * ell, "L not a sum of d widths in {ell-1, ell}")
    g = 64 * (ell + m)
    need((L // (100 * g)) * g >= h_star, "witness width below target")


def brute_least_length(h_star: int, max_s: int) -> int:
    """Independent slow scan over (s, ell, m) for small fixtures."""
    best = None
    for s in range(D_MIN_EXPONENT, max_s + 1):
        d = 1 << s
        for ell in range(2, 400):
            for m in range(2, ell + 1):
                g = 64 * (ell + m)
                r = -(-h_star // g)
                lo = max(d * (ell - 1), 100 * g * r)
                if lo <= d * ell and (best is None or lo < best):
                    best = lo
    need(best is not None, "brute scan found nothing")
    return best


def main() -> None:
    bit = (ROOT / "research/unconditional-batched-crt/BIT.md").read_text()
    need("c=8667/5000000," in bit and "a2=c(1-c^2)=0.001733394791695384296." in bit,
         "BIT.md constants not found")
    place = (ROOT / "research/crt-reservoir-placement/README.md").read_text()
    for phrase in ["`ell>=max(2,ceil(log2(p+2)))`", "`w_i in {ell-1,ell}`",
                   "`G=64(ell+ceil(log2(p+2)))`, `r_max=floor(L/(100G))`, `H=r_max G`",
                   "power-of-two `d>=51200`"]:
        need(phrase in place, f"placement domain phrase missing: {phrase}")
    need(abs(float(A2) - 0.001733394791695384296) < 1e-18, "a2 value")

    # engine sanity: ln 2 and ln 10 against decimal
    for v in (2, 10, Fraction(3, 7)):
        lo, hi = ln_bounds(Fraction(v), 200)
        c80 = decimal.Context(prec=80)
        fv = Fraction(v)
        dv = c80.ln(c80.divide(decimal.Decimal(fv.numerator), decimal.Decimal(fv.denominator)))
        scaled = c80.multiply(dv, c80.power(decimal.Decimal(2), 200))
        need(lo <= scaled <= hi and hi - lo < 4096, f"ln bounds for {v}")

    # critical ratio rho_c = H_BRANCH**a2
    prec = 400
    hl, hh = ln_bounds(Fraction(H_BRANCH), prec)
    ctx = decimal.Context(prec=60)
    two_p = ctx.power(decimal.Decimal(2), prec)
    a2d = ctx.divide(decimal.Decimal(A2.numerator), decimal.Decimal(A2.denominator))
    rc_lo = ctx.exp(ctx.multiply(a2d, ctx.divide(decimal.Decimal(hl), two_p)))
    rc_hi = ctx.exp(ctx.multiply(a2d, ctx.divide(decimal.Decimal(hh), two_p)))
    rho_c = str(rc_lo.quantize(decimal.Decimal("1e-30"), rounding=decimal.ROUND_FLOOR, context=ctx))
    need(str(rc_hi.quantize(decimal.Decimal("1e-30"), rounding=decimal.ROUND_FLOOR, context=ctx)) == rho_c, "rho_c digits unstable")
    rc_frac_lo = Fraction(rho_c)
    rc_frac_hi = rc_frac_lo + Fraction(1, 10**30)
    need(power_exceeds(H_BRANCH, rc_frac_lo) and not power_exceeds(H_BRANCH, rc_frac_hi),
         "rho_c bracket")
    # just below / above rho_c
    need(least_width(rc_frac_lo) <= H_BRANCH, "below rho_c the branch threshold binds")
    need(least_width(rc_frac_hi) == H_BRANCH + 1, "just above rho_c the width is H_BRANCH+1")

    # exact least length at the branch threshold, with independent brute check
    l_branch, w_branch = least_length(H_BRANCH)
    check_layout_witness(w_branch, H_BRANCH)
    need(l_branch >= 100 * H_BRANCH, "PR4942 lower bound violated")
    # small fixtures: fast search vs brute scan
    fixtures = []
    for h in (10752, 15360, 27706, 100000, 123457):
        fast, wit = least_length(h)
        check_layout_witness(wit, h)
        # completeness of the brute ranges: any L <= fast has ell-1 <= L/65536
        # (so ell < 400) and d <= L (so s <= 30)
        need(fast <= 65536 * 398 and fast <= 1 << 30, f"brute ranges too small at H={h}")
        slow = brute_least_length(h, 30)
        need(fast == slow, f"layout search mismatch at H={h}: {fast} vs {slow}")
        fixtures.append({"H_target": h, "least_L": fast})

    # rejection controls: each must fail
    def rejects(fn) -> bool:
        try:
            fn()
        except SystemExit:
            return True
        return False
    bad = dict(w_branch, L=w_branch["L"] - 1)
    need(rejects(lambda: check_layout_witness(bad, H_BRANCH)), "control: L-1 accepted")
    need(rejects(lambda: check_layout_witness(dict(w_branch, m=1), H_BRANCH)), "control: m=1 accepted")
    need(rejects(lambda: check_layout_witness(dict(w_branch, d=1 << 15), H_BRANCH)), "control: d=2^15 accepted")
    need(not power_exceeds(H_BRANCH, rc_frac_hi), "control: width above rho_c accepted")
    need(rejects(lambda: power_exceeds(2, Fraction(0))), "control: nonpositive rho accepted")

    rows = []
    for rs in RHOS:
        rho = Fraction(rs)
        hw = least_width(rho)
        h_star = max(H_BRANCH, hw)
        row = {"rho": rs, "least_H_with_H^a2>rho": str(hw) if hw < 10**30 else None,
               "binding": "branch threshold" if hw <= H_BRANCH else "bill ratio",
               "H_star": str(h_star) if h_star < 10**30 else None,
               "H_star_bits": h_star.bit_length()}
        if h_star == H_BRANCH:
            row["least_L"] = l_branch
        elif h_star <= 10**9:
            l_row, w_row = least_length(h_star)
            check_layout_witness(w_row, h_star)
            row["least_L"] = l_row
            row["witness"] = w_row
        else:
            row["L_lower_bound_100H"] = str(100 * h_star) if h_star < 10**30 else f"100*H_star, H_star has {h_star.bit_length()} bits"
        rows.append(row)
        need((rho < rc_frac_lo) == (h_star == H_BRANCH) or rs in ("1031/1000",), f"regime classification {rs}")

    out = {
        "a2": f"{A2.numerator}/{A2.denominator}",
        "H_branch": H_BRANCH,
        "rho_c_floor_1e-30": rho_c,
        "least_L_at_branch": l_branch,
        "witness_at_branch": w_branch,
        "layout_fixtures": fixtures,
        "rows": rows,
    }
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    target = PKG / "RESULT.json"
    if "--write" in sys.argv:
        target.write_text(text)
    else:
        need(target.read_text() == text, "RESULT.json differs from fresh rebuild")
    print(f"PASS_CRT_RECURSIVE_INTERCHANGE_CROSSOVER rho_c={rho_c} "
          f"least_L_at_branch={l_branch} sha256={hashlib.sha256(text.encode()).hexdigest()[:16]}")


if __name__ == "__main__":
    main()
