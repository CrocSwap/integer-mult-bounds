#!/usr/bin/env python3
"""Certify the best shared recurrence exponent within the generalized h family.

Uses rational enclosures of logarithms, plus a tail bound for all h>=200.
The result concerns the counting formulas, conditional on the network proof.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
from certify import network, require

ROOT = Path(__file__).resolve().parents[1]


def log_ratio_bounds(x, terms=24):
    """Bounds for log(x), 1 <= x <= 2, by the atanh series."""
    require(1 <= x <= 2, "Log series expects 1<=x<=2")
    z = (x-1)/(x+1)
    lower = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
    tail = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return lower, lower+tail


def log_integer_bounds(m):
    k = m.bit_length()-1
    lo2, hi2 = log_ratio_bounds(Q(2))
    lo, hi = log_ratio_bounds(Q(m, 2**k))
    return k*lo2+lo, k*hi2+hi


def saving_bounds(n, bit_only=False):
    eta = n["eta_b"] if bit_only else min(n["eta_b"], n["eta_c"])
    require(0 < eta < Q(1, 2), "Need a positive small rank deficit")
    # Shared exponent saving is min(-log(1-eta_b),-log(1-eta_c))/log(m).
    lo_num, hi_num = log_ratio_bounds(1/(1-eta), terms=3)
    lo_den, hi_den = log_integer_bounds(n["m"])
    return lo_num/hi_den, hi_num/lo_den


def search(bit_only=False):
    bounds = {}
    rejected = []
    for h in range(7, 200):
        if h == 9:
            rejected.append(h)
            continue
        n = network(h)
        if 2*n["Lb"] >= n["N"] or 2*n["Lc"] >= n["N"]:
            rejected.append(h)
            continue
        bounds[h] = saving_bounds(n, bit_only=bit_only)
    winner = max(bounds, key=lambda h: bounds[h][0])
    lo, hi = bounds[winner]
    require(all(lo > b[1] for h, b in bounds.items() if h != winner),
            "Enclosures do not separate a unique winner")
    # eta_b < 1/(3*z_b*m), and -log(1-eta_b) < eta_b/(1-eta_b).
    # For h>=200, z_b and m increase and log(m)>1. This bounds ALL the tail.
    n200 = network(200)
    tail_upper = Q(1, 3*n200["zb"]*n200["m"]-1)
    require(lo > tail_upper, "Tail could contain a better network")
    dyadic_power = 1
    while Q(1, 2**dyadic_power) >= lo:
        dyadic_power += 1
    require(hi < Q(1, 2**(dyadic_power-1)), "Cannot certify optimal dyadic saving")
    return {
        "scope": ("Bit-network saving alone" if bit_only else "Common tau=sigma saving")
                 + "; generalized counting formulas, construction conditional",
        "winner_h": winner,
        "saving_lower": str(lo), "saving_upper": str(hi),
        "largest_certified_dyadic_saving": f"2^-{dyadic_power}",
        "tail_start": 200, "tail_saving_upper": str(tail_upper),
        "excluded_h": rejected,
        "finite_enclosures": {str(h): {"lower": str(b[0]), "upper": str(b[1])}
                              for h, b in bounds.items()},
    }


def parameter_ceiling():
    """Upper bound for kappa even with variable beta and separate sigma.

    Put a=1-tau. The final g4>0 gives epsilon<a. If c<a then
    min(ac,1-lambda')<a^2. Otherwise beta<1 and the packed constraint
    give 1-lambda'<1-(1-a)(1+a)=a^2. Hence min(g2,g3)<a^3.
    """
    result = search(bit_only=True)
    upper = Q(result["saving_upper"])**3
    witness = Q(58, 10**34)
    require(upper < Q(5838, 10**36), "Unexpected parameter ceiling")
    require(upper < Q(1, 2**107), "Cannot exclude the next dyadic kappa")
    require(witness > Q(99, 100)*upper, "Witness below 99% of ceiling")
    return {"bit_network_search": result, "kappa_upper": str(upper),
            "simple_kappa_upper": str(Q(5838, 10**36)),
            "witness": str(witness), "witness_fraction_of_upper": str(witness/upper),
            "next_dyadic_excluded": "2^-107",
            "scope": "Seven-margin accounting and stated network rank bounds; not all algorithms"}


if __name__ == "__main__":
    result = search()
    result["parameter_ceiling"] = parameter_ceiling()
    path = ROOT / "certificates/network-search.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(f"Certified h={result['winner_h']} best within the stated counting family,")
    print(f"including all h>=200 by a tail bound; dyadic saving {result['largest_certified_dyadic_saving']}")
