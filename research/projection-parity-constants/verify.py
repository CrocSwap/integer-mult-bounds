#!/usr/bin/env python3
"""Exact finite corroboration; the universal proof is PROOF.md. Apache-2.0."""
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import platform

Q = F(1, 2)
SEED = (0, 27456, 48576, 68320, 86592)
C = (F(1), F(17, 39), F(6181, 14586), F(99085, 239811))
LIMIT = F(439277, 149175)
MEAN = F(815083, 596700)
AMPLITUDE = F(323, 28)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def poch(a, n):
    return prod((1 - a * Q**i for i in range(n)), start=F(1))


def h(r):
    return F(3, 2) + Q**r - 2**r


def integer_triangle(last, drop_second=False, seed=SEED):
    """Direct source recurrence; no eigenmode or asymptotic code is used."""
    rows = {4: list(seed)}
    for k in range(5, last + 1):
        old = rows[k - 1]
        new = []
        for r in range(k + 1):
            a = 2**(k-r) - 1 + 4**k - 2**(k+r)
            b = 2 * (2**k - 2**(k-r)) + (2**r-1) * 2**(k-1)
            c = 0 if r < 2 else (2**r-1)*(2**(r-1)-1)*2**(k-r)
            terms = ((r, a), (r-1, b), (r-2, 0 if drop_second else c))
            new.append(sum(coef*old[s] for s, coef in terms if 0 <= s < k))
        rows[k] = new
    return rows


def eigenmode(j, last, h_shift=F(0)):
    e = [F(0)] * j + [F(1)]
    for r in range(j + 1, last + 1):
        b = F(2**r, 2) + F(3, 2) - 2*Q**r
        c = F(2**r, 2) - F(3, 2) + Q**r
        e.append((b*e[r-1] + c*e[r-2]) / (h(j)+h_shift-h(r)))
    return e


def mode_product(m, j):
    out = F(1)
    for k in range(5, m + 1):
        out *= F((2**(k-j)-1)*(2**(k+j)+1),
                 (2**(k-1)-1)*(2**(k+1)+1))
    return out


def constants(j):
    fj = poch(-Q, 2*j) / (poch(Q, j)*poch(-Q, j)**2)
    gj = poch(-Q, 2*j) / (6*poch(Q, j-1)**2*poch(Q, j))
    pj = prod((1-Q**i for i in range(5-j, 4)), start=F(1))
    pj /= prod((1+Q**i for i in range(6, 5+j)), start=F(1))
    return pj, fj, gj


def k_interval(n):
    need(n >= 3, "K interval domain")
    high = prod((((1-Q**i)/(1+Q**i))**2 for i in range(1, n+1)), start=F(1))
    return high*(1-4*Q**n), high


def decimals(value, digits=24):
    with localcontext() as ctx:
        ctx.prec = digits
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def outward_interval(low, high):
    out = []
    for value, direction in ((low, ROUND_FLOOR), (high, ROUND_CEILING)):
        with localcontext() as ctx:
            ctx.prec = 24
            ctx.rounding = direction
            out.append(str(Decimal(value.numerator)/Decimal(value.denominator)))
    return out


def v_values(j, last):
    s = 2**j
    out = [F(1)]
    for n in range(1, last+1):
        rhs = (1+F(4, s)*Q**n)*out[n-1]
        if n >= 2:
            rhs += (1-2*Q**n)*out[n-2]
        out.append(rhs/(2*(1+F(1, s*s)*Q**n)))
    return out


def overlap(a, b):
    return max(a[0], b[0]) <= min(a[1], b[1])


def series_interval(j, z, terms=64):
    """Explicit q-series (7); ratio of omitted terms has modulus <= 1/2."""
    need(abs(z) <= Q and terms >= j+4, "q-series domain")
    s = 2**j
    t = (1+F(1, s*s))/((1-z)*(1+z/2))
    total = F(0)
    for ell in range(terms):
        total += t
        t *= -F(1, s*s)*(1-s*z*Q**ell/2)**2
        t /= (1-z*Q**(ell+1))*(1+z*Q**(ell+2))
    return total-2*abs(t), total+2*abs(t)


def negative_residue_interval(j, terms=80):
    """Independent series evaluation at the -2 pole before q-Gauss."""
    need(isinstance(j, int) and j >= 1 and isinstance(terms, int) and terms >= 3,
         "negative residue series domain")
    s = 2**j
    t = (1+F(1, s*s))/3
    total = F(0)
    for ell in range(terms):
        total += t
        t *= -F(1, s*s)*(1+s*Q**ell)**2
        t /= (1+Q**ell)*(1-Q**(ell+1))
    return total-2*abs(t), total+2*abs(t)


def check_profile(rows, modes, coefficients=C):
    checks = 0
    for m, row in rows.items():
        ps = [mode_product(m, j) for j in range(1, 5)]
        for r in range(m+1):
            predicted = sum(coefficients[j-1]*ps[j-1]*modes[j][r] for j in range(1, 5))
            need(predicted == F(row[r], row[1]), f"profile mismatch m={m} r={r}")
            checks += 1
    return checks


def rejected(callback):
    try:
        callback()
    except ValueError:
        return 1
    raise ValueError("A negative control was incorrectly accepted")


def main():
    last = 72
    rows = integer_triangle(last)
    modes = {j: eigenmode(j, last) for j in range(1, 5)}
    checks = {"whole_profile_equalities": check_profile(rows, modes)}
    limit = mean = amplitude = F(0)
    product_checks = 0
    for j, c in enumerate(C, 1):
        p, f, g = constants(j)
        limit += c*p*f
        mean += c*p*f*(2**j-Q**j-3)/2
        amplitude += c*p*(-1)**j*2**j*g
        for m in range(4, last+1):
            end = prod((1+Q**i for i in range(m+2, m+j+1)), start=F(1))
            end /= prod((1-Q**i for i in range(m-j+1, m)), start=F(1))
            need(mode_product(m, j) == p*end, "finite product telescoping")
            product_checks += 1
    need((limit, mean, amplitude) == (LIMIT, MEAN, AMPLITUDE), "rational constants")
    checks["finite_product_identities"] = product_checks
    kl, kh = k_interval(80)
    transformations = series_checks = residue_checks = 0
    for j in range(1, 9):
        vs = v_values(j, 64)
        es = eigenmode(j, j+64)
        for n, v in enumerate(vs):
            factor = poch(Q**(n+1), j)/poch(Q, j)
            need(factor*v == es[j+n], "eigenmode transformation")
            need(0 <= v <= 1, "subconvex recurrence bound")
            transformations += 1
        for z in (F(-1, 2), F(-1, 4), F(1, 4), F(1, 2)):
            value = sum(v*z**n for n, v in enumerate(vs))
            tail = abs(z)**len(vs)/(1-abs(z))
            need(overlap((value-tail, value+tail), series_interval(j, z)), "generating series")
            series_checks += 1
        aj = poch(-Q, 2*j)/poch(-Q, j)**2
        finite = sum((-Q**(2*j))**ell * poch(F(2**j, 2), ell)**2 /
                     (poch(Q, ell)*poch(-Q, ell+1)) for ell in range(j))
        need((1+Q**(2*j))*finite == aj, "positive residue summation")
        bj = poch(-Q, 2*j)/(6*poch(Q, j-1)**2)
        need(overlap(negative_residue_interval(j), (bj*kl, bj*kh)), "negative residue q-Gauss")
        residue_checks += 2
    checks.update(eigenmode_transformations=transformations,
                  generating_series_enclosures=series_checks,
                  residue_checks=residue_checks)
    samples = []
    for m in (8, 9, 16, 17, 32, 33, 48, 49, 64, 65, 72):
        scaled = 2**m*(F(rows[m][m], rows[m][1])-LIMIT)
        lo = MEAN + AMPLITUDE*(kl if m % 2 == 0 else -kh)
        hi = MEAN + AMPLITUDE*(kh if m % 2 == 0 else -kl)
        # A finite corroboration threshold, not a claimed universal remainder constant.
        need(max(abs(scaled-lo), abs(scaled-hi)) < 32*Q**m, "asymptotic sample")
        samples.append({"m": m, "scaled_error": decimals(scaled),
                        "absolute_gap_upper": outward_interval(F(0), max(abs(scaled-lo), abs(scaled-hi)))[1]})
    controls = 0
    short = {m: rows[m] for m in range(4, 9)}
    bad_c = list(C); bad_c[3] += 1
    controls += rejected(lambda: check_profile(short, modes, bad_c))
    controls += rejected(lambda: check_profile(integer_triangle(8, drop_second=True), modes))
    bad_seed = list(SEED); bad_seed[3] += 1
    controls += rejected(lambda: check_profile(integer_triangle(8, seed=bad_seed), modes))
    bad_modes = dict(modes); bad_modes[2] = eigenmode(2, last, F(1, 100))
    controls += rejected(lambda: check_profile(short, bad_modes))
    even_scaled = 2**32*(F(rows[32][32], rows[32][1])-LIMIT)
    controls += rejected(lambda: need(abs(even_scaled-(MEAN-AMPLITUDE*kl)) < Q**20, "wrong parity"))
    b1 = poch(-Q, 2)/(6*poch(Q, 0)**2)
    controls += rejected(lambda: need(overlap(negative_residue_interval(1), (2*b1*kl, 2*b1*kh)), "wrong residue factor"))
    checks["rejected_negative_controls"] = controls
    root = Path(__file__).resolve().parent
    hashes = {name: sha256((root/name).read_bytes()).hexdigest() for name in ("PROOF.md", "verify.py")}
    result = {"status": "PASS_PROJECTION_PARITY_CONSTANTS", "python": platform.python_version(),
              "checks": checks, "exact": {"limit": str(LIMIT), "mean": str(MEAN), "K_coefficient": str(AMPLITUDE)},
              "K_interval": outward_interval(kl, kh),
              "even_interval": outward_interval(MEAN+AMPLITUDE*kl, MEAN+AMPLITUDE*kh),
              "odd_interval": outward_interval(MEAN-AMPLITUDE*kh, MEAN-AMPLITUDE*kl),
              "samples": samples, "sha256": hashes,
              "scope": "Exact finite corroboration; universal proof and classical q-Gauss are separate mathematical evidence."}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
