"""Rational harmonic-sum exclusion; imports no predecessor implementation.

OpenAI Codex for the requesting contributor; substantial AI assistance.
Apache-2.0. The construction and rank/assembly hypotheses are inherited.
"""
from fractions import Fraction
from math import comb


TARGET = Fraction(1, 2**26)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prime_powers(limit):
    """Prime sieve followed by explicit powers, independently of characteristic()."""
    sieve = [True] * (limit + 1)
    sieve[:2] = [False, False]
    for p in range(2, limit + 1):
        if sieve[p]:
            for composite in range(p * p, limit + 1, p):
                sieve[composite] = False
    powers = {}
    for p in range(2, limit + 1):
        if sieve[p]:
            q = p
            while q <= limit:
                powers[q] = p
                q *= p
    return powers


def log_lower(h):
    # On [j-1,j], 1/t > 1/j except at the endpoint.
    # Summing integrals gives log(h^3) > 3*(H_h-1), h>=2.
    require(type(h) is int and h >= 2, "Invalid harmonic ground size")
    return 3 * sum((Fraction(1, j) for j in range(2, h + 1)), Fraction())


def case(q, h):
    k, j = 2 * q - 1, q - 1
    n, r = comb(h, k), comb(h, j)
    deficit = n - 6 * h * r
    if deficit <= 0:
        return {"q": q, "h": h, "positive_deficit": False}
    require(h >= 3 * q, "Positive deficit violates support-domain lemma")
    outputs = comb(k, j)
    side_floor = 2 * outputs * n
    eta = Fraction(deficit, 2 * h**3 * (n + side_floor + r))
    require(0 < eta < 1, "Invalid deficit ratio")
    upper = eta / (5 * (1 - eta) * log_lower(h))
    return {
        "q": q, "h": h, "positive_deficit": True,
        "n": n, "r": r, "outputs_per_label": outputs,
        "side_role_floor": side_floor, "eta_upper": str(eta),
        "harmonic_kappa_upper": str(upper),
    }


def exclusion():
    # Fixed stopping rule: first rational dimension-tail bound below 2^-26.
    # It is decreasing because both positive denominator factors increase.
    for h in range(2, 101):
        tail = 1 / (5 * (4 * h**3 - 1) * log_lower(h))
        if tail < TARGET:
            cutoff = h
            break
    else:
        raise ValueError("Harmonic tail not closed within the stated budget")
    powers = prime_powers((cutoff + 1) // 2)
    cases = [case(q, h) for q in sorted(powers)
             for h in range(2 * q - 1, cutoff)]
    positive = [row for row in cases if row["positive_deficit"]]
    require(positive, "Empty positive-deficit domain")
    best = max(positive, key=lambda row: Fraction(row["harmonic_kappa_upper"]))
    require(all(Fraction(row["harmonic_kappa_upper"]) < TARGET for row in positive),
            "Independent harmonic envelope has a survivor")
    return {
        "target": str(TARGET), "tail_start": cutoff,
        "tail_kappa_upper": str(tail),
        "previous_tail_kappa_upper": str(
            1 / (5 * (4 * (cutoff - 1)**3 - 1) * log_lower(cutoff - 1))),
        "prime_powers": {str(q): p for q, p in sorted(powers.items())},
        "cases": cases, "finite_cases": len(cases),
        "positive_cases": len(positive), "best": best,
        "scope": "Inherited rank-one three-stage/common-subset model, S>=2*C(2q-1,q-1)*n, W>=4*n^3 and kappa<a_b/5 only",
    }


def check_historical(certificate, report):
    """Check every historical row against independently reconstructed counts.

    The independent exclusion does not use the historical logarithm bounds.
    Their exact values are separately covered by the isolated producer replay.
    """
    envelope = certificate["envelope"]
    require(Fraction(envelope["target"]) == TARGET, "Historical target changed")
    require(envelope["all_prime_powers_and_ground_sizes_excluded"] is True,
            "Missing historical exclusion claim")
    tail = envelope["tail_dimension_exclusion"]
    require(tail["first_excluded_dimension"] == 65
            and tail["largest_not_excluded_dimension"] == 64
            and tail["W_over_N_lower"] == 4
            and tail["all_larger_dimensions_excluded"] is True
            and tail["achievability_claimed"] is False,
            "Historical tail model changed")
    require(Fraction(tail["target_kappa"]) == TARGET
            and Fraction(tail["required_bit_saving"]) == 5 * TARGET
            and 0 < Fraction(tail["upper_at_excluded"]) < 5 * TARGET,
            "Invalid historical tail values")
    expected = {(q, h): case(q, h) for q in prime_powers(33)
                for h in range(2 * q - 1, 65)}
    actual = {}
    for row in envelope["cases"]:
        key = (row["q"], row["h"])
        require(key not in actual, "Duplicate historical case")
        actual[key] = row
    require(set(actual) == set(expected), "Historical finite domain incomplete")
    for key, independent in expected.items():
        old = actual[key]
        require(old["positive_deficit"] is independent["positive_deficit"],
                "Historical deficit sign differs")
        if not independent["positive_deficit"]:
            require(set(old) == {"q", "h", "positive_deficit"},
                    "Unexpected nonpositive row fields")
            continue
        for field in ("n", "r", "outputs_per_label", "side_role_floor"):
            require(type(old[field]) is int and old[field] == independent[field],
                    "Historical integer count differs: " + field)
        require(Fraction(old["eta_upper"]) == Fraction(independent["eta_upper"]),
                "Historical deficit ratio differs")
        upper = Fraction(old["kappa_upper"])
        require(0 < upper < Fraction(independent["harmonic_kappa_upper"]) < TARGET,
                "Historical upper bound outside independent envelope")
        require(Fraction(old["bit_saving_upper"]) == 5 * upper,
                "Historical assembly conversion differs")
    best = max(actual.values(), key=lambda row: Fraction(row.get("kappa_upper", "0")))
    require(envelope["best_finite_upper"] == best, "Historical best row differs")
    require((best["q"], best["h"]) == (report["best"]["q"], report["best"]["h"]),
            "Maximizing ground size differs between envelopes")
    return {"cases": len(actual), "positive_cases": sum(
        row["positive_deficit"] for row in actual.values()),
        "extra_harmonic_cases": report["finite_cases"] - len(actual)}
