#!/usr/bin/env python3
"""Independent rational pricing of the credited PR2733/2751 composition.

The atanh/Taylor method is standard and follows the retained exact-moment
lineage, including Tekalign's PR2751. This implementation imports no producer
or predecessor arithmetic. Finite pricing is not native or outer admission.
David Arias, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIMENSION, LIVE, CALLS, MASS = 73, 66304, 666, 4816512
LOW = Q("0.001717256973467002308270")
HIGH = LOW + Q(1, 10**24)
KAPPA = LOW - Q(1, 10**46) - Q(1, 10**70)
SCALE = 2**160


def need(condition, message):
    if not condition:
        raise ValueError(message)


def profile(raw):
    need(isinstance(raw, dict) and raw, "nonempty rank histogram")
    out = {}
    for key, value in raw.items():
        need(isinstance(key, str) and key.isdecimal(), "decimal rank key")
        rank = int(key)
        need(str(rank) == key and 0 < rank < DIMENSION, "canonical positive rank")
        need(type(value) is int and value > 0, "positive integer multiplicity")
        out[rank] = value
    return out


@lru_cache(None)
def logarithm(x):
    """Rational enclosure of log(x), x>=1, using 36 positive atanh terms."""
    need(x >= 1, "logarithm input")
    exponent = 0
    reduced = x
    while reduced >= 2:
        reduced /= 2
        exponent += 1

    def core(y):
        z = (y-1)/(y+1)
        need(0 <= z <= Q(1, 3), "atanh reduction")
        lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(36)), Q(0))
        tail = 2*z**73/(73*(1-z*z))
        return lo, lo+tail

    lo, hi = core(reduced)
    two_lo, two_hi = core(Q(2))
    return lo+exponent*two_lo, hi+exponent*two_hi


def exponential(x):
    """Positive Taylor polynomial through degree 20 plus a geometric tail."""
    need(0 <= x < Q(1, 100), "small exponential input")
    term = total = Q(1)
    for degree in range(1, 21):
        term = term*x/degree
        total += term
    next_term = term*x/21
    tail = next_term/(1-x/22)
    return total, total+tail


def moment(histogram, saving, live=LIVE):
    need(type(live) is int and live == LIVE, "source-bound live normalization")
    need(Q(0) < saving < Q(1, 500), "certified saving domain")
    lo = hi = Q(0)
    for rank, count in sorted(histogram.items()):
        log_lo, log_hi = logarithm(Q(DIMENSION, rank))
        exp_lo, _ = exponential(saving*log_lo)
        _, exp_hi = exponential(saving*log_hi)
        weight = Q(count*rank, DIMENSION*live)
        lo += weight*exp_lo
        hi += weight*exp_hi
    return lo, hi


def floor(x):
    return x.numerator//x.denominator


def dyadic(lo, hi):
    """Small exact outward display; acceptance uses the full rational values."""
    return {"lower_numerator": floor(lo*SCALE),
            "upper_numerator": -floor(-hi*SCALE), "denominator": SCALE}


def require_bracket(histogram, low, high):
    need(low < high, "strictly ordered root endpoints")
    a, b = moment(histogram, low)
    c, d = moment(histogram, high)
    need(b < 1 < c, "strict adjacent root bracket")
    return {"lower_endpoint": str(low), "upper_endpoint": str(high),
            "lower_moment_minus_one": dyadic(a-1, b-1),
            "upper_moment_minus_one": dyadic(c-1, d-1)}


def check(candidate_raw, source_raw, claim):
    candidate, source = profile(candidate_raw), profile(source_raw)
    need(sum(r*n for r, n in source.items()) == MASS, "source paid mass")
    expected = dict(source)
    expected[1] -= 2*CALLS
    expected[2] += CALLS
    need(candidate == expected, "complete 666-call H2-minus-2H1 invoice")
    need(sum(r*n for r, n in candidate.items()) == MASS, "candidate paid mass")
    need(Q(claim["complex_lower"]) == LOW and Q(claim["complex_upper"]) == HIGH,
         "claim root endpoints")
    need(Q(claim["kappa"]) == KAPPA, "conditional modern outer target")
    need(profile(claim["profile"]) == candidate, "claim full profile")
    bracket = require_bracket(candidate, LOW, HIGH)
    source_lo, source_hi = moment(source, LOW)
    need(source_lo > 1, "unchanged source does not certify the new endpoint")
    # An exact sign comparison is independent of the transcendental engine:
    # 0<p<1 implies 2^p<2. Thus 666*(2^p-2)/(W*73^p)<0.
    need(0 < LOW < HIGH < 1, "strict concavity domain")
    rejected = []

    def reject(name, operation):
        try:
            operation()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control accepted: "+name)

    reject("unmodified_source_at_new_endpoint", lambda: require_bracket(source, LOW, HIGH))
    reject("reversed_root_endpoints", lambda: require_bracket(candidate, HIGH, LOW))
    reject("upper_endpoint_admitted_as_lower",
           lambda: require_bracket(candidate, HIGH, HIGH+Q(1, 10**21)))
    reverse = dict(source)
    reverse[1] += 2*CALLS
    reverse[2] -= CALLS
    need(sum(r*n for r, n in reverse.items()) == MASS, "control keeps paid mass")
    reject("mass_preserving_reversed_fusion", lambda: require_bracket(reverse, LOW, HIGH))
    reject("changed_live_denominator", lambda: moment(candidate, LOW, LIVE+1))
    # Check the intervals on exact algebraic constants, not merely their signs
    # at this one candidate. No logarithm/exp floating-point oracle is used.
    need(logarithm(Q(1)) == (0, 0), "log one control")
    need(exponential(Q(0)) == (1, 1), "exp zero control")
    root2_lo, root2_hi = logarithm(Q(2))
    root4_lo, root4_hi = logarithm(Q(4))
    need((root4_lo, root4_hi) == (2*root2_lo, 2*root2_hi), "exact log scaling")
    return {"status": "PASS_EXACT_COMPOSED_FRAME_MOMENT", "dimension": DIMENSION,
            "live": LIVE, "call_equivalents": CALLS, "paid_mass": MASS,
            "profile": {str(r): n for r, n in sorted(candidate.items())},
            "bracket": bracket, "conditional_kappa": str(KAPPA),
            "source_moment_at_candidate_lower_minus_one": dyadic(source_lo-1, source_hi-1),
            "controls_rejected": rejected,
            "scope": "Independent exact finite moment and invoice arithmetic; native, hosting and modern outer admission are separate."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-profile", type=Path, default=HERE/"PROFILE.json")
    parser.add_argument("--source-profile", type=Path, default=HERE/"vendor/pr2751/PROFILE.json")
    parser.add_argument("--claim", type=Path, default=HERE/"CLAIM.json")
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text())
    print(json.dumps(check(read(args.candidate_profile), read(args.source_profile), read(args.claim)),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
