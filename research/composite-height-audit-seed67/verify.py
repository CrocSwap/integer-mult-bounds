#!/usr/bin/env python3
"""Exact finite evidence for the composite-height audit; not an analytic prover.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor arithmetic implementation is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from math import comb, gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = 134
SEED = 67


def require(condition, message):
    if not condition:
        raise ValueError(message)


def factors(n):
    require(isinstance(n, int) and n >= 1, "positive integer required")
    result = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            result.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        result.append(n)
    return result


def phi(n):
    answer = n
    for p in factors(n):
        answer = answer // p * (p - 1)
    return answer


def units(n):
    return [k for k in range(1, n) if gcd(k, n) == 1]


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def harmonic(n):
    return sum((Q(1, j) for j in range(1, n + 1)), Q(0))


def log_interval(x, terms=24):
    """Independent positive atanh series, used only to enclose log(2)."""
    x = Q(x)
    require(x >= 1 and terms > 0, "log oracle domain")
    y = (x - 1) / (x + 1)
    low = 2 * sum((y ** (2 * j + 1) / (2 * j + 1)
                   for j in range(terms)), Q(0))
    tail = 2 * y ** (2 * terms + 1) / ((2 * terms + 1) * (1 - y * y))
    return low, low + tail


def bound(r):
    require(isinstance(r, int) and r >= 3, "radix must be at least three")
    n, degree, ell = r - 1, phi(r), (r - 1).bit_length()
    old_t = n * degree * r
    # Consecutive integers make 3*n*r/2 integral. No float or rounded log.
    averaged_t = 3 * n * r * (ell + 1) ** 2 // 2 + 2 * n * degree * ell
    gap_bits = 1 + 2 * ell + min(old_t, averaged_t)
    return {
        "r": r, "phi": degree, "ell": ell,
        "totient_ratio": str(Q(r, degree)),
        "old_coarse_gap_bits": 1 + 2 * ell + old_t,
        "averaged_term": averaged_t,
        "gap_bits": gap_bits,
        "inverse_norm_bits": 2 * gap_bits + r + 2,
        "precondition": "nonzero conjugate-reciprocal resultant",
    }


def audit_fibers(limit=LIMIT):
    rows = []
    total_members = 0
    total_characters = 0
    for r in range(3, limit + 1):
        ur = units(r)
        require(len(ur) == phi(r), "independent totient count")
        max_ratio = max(Q(d, phi(d)) for d in divisors(r))
        require(max_ratio == Q(r, phi(r)), "divisor-totient domination")
        per_divisor = Counter()
        for h in range(1, r):
            common = gcd(h, r)
            d = r // common
            # Literal character exponents in the reduced order-d root.
            actual = Counter((h // common * k) % d for k in ur)
            expected = {j: len(ur) // phi(d) for j in units(d)}
            require(actual == expected, f"nonuniform primitive fibers r={r}, h={h}")
            total_members += len(ur)
            total_characters += 1
            per_divisor[d] += 1
        envelope_rows = []
        for d in divisors(r):
            if d == 1:
                continue
            # Concavity of sine: 1/sin(pi*j/d) <= d/(2*min(j,d-j)).
            actual_envelope = Q(d, 2 * phi(d)) * sum(
                (Q(1, min(j, d - j)) for j in units(d)), Q(0))
            all_residue_envelope = Q(d, phi(d)) * harmonic(d // 2)
            uniform_envelope = Q(r, phi(r)) * harmonic(d // 2)
            require(actual_envelope <= all_residue_envelope <= uniform_envelope,
                    "rational geometric envelope")
            require(per_divisor[d] == phi(d), "character-order census")
            envelope_rows.append([d, str(actual_envelope), str(uniform_envelope)])
        rows.append({"r": r, "phi": len(ur), "envelopes": envelope_rows})
    return {"radices": [3, limit], "radix_count": len(rows),
            "character_count": total_characters, "fiber_member_count": total_members,
            "rows": rows}


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p or [0]


def mul(a, b, modulus=None):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    if modulus:
        out = [x % modulus for x in out]
    return trim(out)


def add(a, b, modulus=None):
    out = [0] * max(len(a), len(b))
    for i, x in enumerate(a):
        out[i] += x
    for i, x in enumerate(b):
        out[i] += x
    if modulus:
        out = [x % modulus for x in out]
    return trim(out)


def divmod_monic(a, b):
    require(b[-1] == 1, "monic divisor required")
    a = trim(a)
    q = [0] * max(1, len(a) - len(b) + 1)
    while a != [0] and len(a) >= len(b):
        shift, c = len(a) - len(b), a[-1]
        q[shift] = c
        for j, x in enumerate(b):
            a[shift + j] -= c * x
        a = trim(a)
    return trim(q), a


def cyclotomics(limit):
    """Construct Phi_n by exact division of x^n-1, independently of lifting."""
    result = {}
    for n in range(1, limit + 1):
        value = [-1] + [0] * (n - 1) + [1]
        for d in divisors(n):
            if d != n:
                value, remainder = divmod_monic(value, result[d])
                require(remainder == [0], "cyclotomic division")
        result[n] = value
    return result


def tail(r, residue, modulus):
    """Literal kernel coefficients, in ascending z order."""
    value = [0] * r
    value[-1] = 1
    for j in range(r - 2, -1, -1):
        value[j] = value[j + 1] * (1 - pow(residue, j + 1, modulus)) % modulus
    return value


def lifted_bezout(r, p, f, reciprocal):
    # Since g=1+2z, divide using its root beta and evaluate the literal f there.
    beta = -pow(2, -1, p) % p
    f_beta = 0
    for coefficient in reversed(f):
        f_beta = (f_beta * beta + coefficient) % p
    require(f_beta != 0, "seed obstruction: lifted f vanishes at reciprocal root")
    constant = pow(f_beta, -1, p)
    dividend = add([1], [-constant * x for x in f], p)
    quotient = [0] * (len(dividend) - 1)
    remainder = dividend[:]
    for i in range(len(dividend) - 1, 0, -1):
        coefficient = remainder[i] * pow(2, -1, p) % p
        quotient[i - 1] = coefficient
        remainder[i] = (remainder[i] - 2 * coefficient) % p
        remainder[i - 1] = (remainder[i - 1] - coefficient) % p
    require(trim(remainder) == [0], "linear polynomial division")
    identity = add([constant * x for x in f], mul(quotient, reciprocal, p), p)
    require(identity == [1], "lifted Bezout identity")
    require(len(trim(quotient)) - 1 < r - 1, "cofactor degree bound")
    return {"constant_multiplier": constant, "reciprocal_multiplier": trim(quotient),
            "f_at_reciprocal_root": f_beta}


def audit_lifting(limit=LIMIT):
    polys = cyclotomics(limit)
    cases = []
    for p in range(5, limit // 2 + 1):
        if factors(p) != [p]:
            continue
        power, exponent = p, 1
        while 2 * power <= limit:
            r = 2 * power
            degree = power // p * (p - 1)
            expected_phi = [comb(degree, j) % p for j in range(degree + 1)]
            require([x % p for x in polys[r]] == expected_phi,
                    "mixed cyclotomic reduction")
            require(all(k % 2 for k in units(r)), "primitive residues must be odd")
            f = tail(r, p - 1, p)
            inverse_residue = pow(p - 1, -1, p)
            reciprocal = trim(list(reversed(tail(r, inverse_residue, p))))
            require(f == [0] * (r - 2) + [2, 1], "literal tail reduction")
            require(reciprocal == [1, 2], "reciprocal has no leading shift")
            witness = lifted_bezout(r, p, f, reciprocal)
            cases.append({"r": r, "p": p, "a": exponent, **witness})
            power *= p
            exponent += 1
    return {"radix_limit": limit, "case_count": len(cases), "cases": cases}


def audit_budgets():
    finite = [bound(r) for r in range(3, LIMIT + 1)]
    family = []
    primes = [p for p in range(5, SEED + 1) if factors(p) == [p]]
    for p in primes:
        for a in range(1, 9):
            row = bound(2 * p ** a)
            row.update(p=p, a=a, precondition="proved by the retained seed-2 lifting argument")
            family.append(row)
    for row in finite + family:
        r, ell, degree = row["r"], row["ell"], row["phi"]
        n = r - 1
        # Separate Fraction expression checks the rational-to-dyadic conversion.
        rational_term = n * degree * (Q(3, 2) * Q(r, degree) * (ell + 1) ** 2 + 2 * ell)
        require(rational_term.denominator == 1 and rational_term == row["averaged_term"],
                "totient cancellation")
        require(2 ** (ell - 1) < r <= 2 ** ell, "ceiling log2")
        require(row["gap_bits"] <= row["old_coarse_gap_bits"], "fallback increased")
        require(row["averaged_term"] <= Q(35, 8) * r * r * ell * ell,
                "uniform quadratic-log-squared envelope")
        if len(factors(r)) == 1:
            predecessor = 1 + 2 * ell + n * degree * min(r, 8 * ell * ell)
            require(row["gap_bits"] <= predecessor, "prime-power predecessor comparison")
    return {"finite_conditional_radices": finite, "lifted_family": family,
            "lifted_family_count": len(family), "seed_family": [x for x in family if x["p"] == SEED]}


def controls():
    outcomes = []

    def rejected(name, action):
        try:
            action()
        except ValueError:
            outcomes.append(name)
            return
        raise ValueError("negative control was accepted: " + name)

    rejected("prime_power_ratio_reused_at_134", lambda: require(Q(134, phi(134)) <= 2, "false ratio"))
    rejected("nonunits_in_character_average", lambda: require(
        Counter(k % 6 for k in range(1, 6)) == Counter(units(6)), "nonprimitive residues"))
    rejected("unequal_fiber_multiplicity", lambda: require(
        Counter(k % 3 for k in units(12)) == {1: 1, 2: 1}, "lost fiber multiplicity"))
    rejected("radix_two_outside_formula", lambda: bound(2))
    rejected("noninteger_radix", lambda: bound(Q(7, 2)))
    f = tail(10, 4, 5)
    rejected("shifted_reciprocal", lambda: lifted_bezout(10, 5, f, [0] * 8 + [1, 2]))
    rejected("missing_reciprocal_constant", lambda: lifted_bezout(10, 5, f, [0, 2]))
    # At p=3 both reduced polynomials vanish at z=1. This is a failed lifting
    # route, not a characteristic-zero counterexample for radix six.
    f6 = tail(6, 2, 3)
    require(sum(f6) % 3 == 0 and (1 + 2) % 3 == 0, "excluded-prime witness")
    rejected("excluded_seed_prime_three", lambda: lifted_bezout(6, 3, f6, [1, 2]))
    rejected("wrong_seed_bezout_sign", lambda: require(
        add(mul([2], [2, 1]), [1, 2]) == [3], "changed seed identity"))
    # Check the rational constants used in the written dyadic conversion.
    low, high = log_interval(2)
    require(Q(2, 3) < low <= high < Q(3, 4), "log2 enclosure")
    return {"rejected": outcomes, "count": len(outcomes),
            "log2_interval": [str(low), str(high)],
            "counterexample_ratio": {"r": 134, "phi": 66, "ratio": "67/33", "excess_over_two": "1/33"},
            "excluded_prime_scope": "p=3 defeats this modular route only; no complex unit-circle root is asserted"}


def check_sources(root):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            data = (root / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"], "source drift: " + row["path"])


def build_receipt():
    return {
        "status": "PASS_COMPOSITE_HEIGHT_AUDIT_S67",
        "assignment_seed": SEED,
        "scope": "Exact finite group, modular-polynomial and budget evidence for the written analytic proof; no full theorem formalization or paid solver",
        "fibers": audit_fibers(), "lifting": audit_lifting(),
        "budgets": audit_budgets(), "controls": controls(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", type=Path, help="write a proposed receipt to this path")
    ap.add_argument("--source-root", type=Path, default=HERE.parents[1])
    args = ap.parse_args()
    check_sources(args.source_root)
    receipt = build_receipt()
    if args.write:
        require(args.write.resolve() != (HERE / "EXPECTED.json").resolve(),
                "write a proposed receipt elsewhere, then review before replacing EXPECTED.json")
        args.write.write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        require(receipt == expected, "receipt mismatch")
    print(f"{receipt['status']} radices={receipt['fibers']['radix_count']} "
          f"characters={receipt['fibers']['character_count']} "
          f"lifts={receipt['lifting']['case_count']} "
          f"family_budgets={receipt['budgets']['lifted_family_count']} "
          f"controls={receipt['controls']['count']} no_new_kappa")


if __name__ == "__main__":
    main()
