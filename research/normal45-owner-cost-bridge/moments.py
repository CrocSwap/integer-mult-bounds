# SPDX-License-Identifier: Apache-2.0
"""Independent positive-binomial enclosure of the complete T74 moment.

No numerical predecessor implementation, logarithm, exponential, floating point,
or root search is used.  See MOMENT-PROOF.md for the recurrence and tail proof.
Substantial AI assistance: OpenAI Codex, GPT-6.1 Sol.
"""

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path


BITS = 256
TERMS = 192
WIDTH = 73
REPLICAS = 74
STOCK = 896 * REPLICAS
RANK_MASS = 65088 * REPLICAS
HEADLINE_GUARD = Fraction(1, 10**46) + Fraction(1, 10**70)
BASELINE_HEAD = "81f3b5d12977eba09e06fbff729167d59faabe90"
CANDIDATE_HEAD = "a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf"
BASELINE_COMPLEX_LOWER = Fraction("1722499906443274564357/1000000000000000000000000")
CANDIDATE_COMPLEX_LOWER = Fraction("430704079965803581999/250000000000000000000000")
UPPER_PROBE_GAP = Fraction(1, 10**20)


def need(condition, message):
    """A mathematical check that remains active under python -O."""
    if not condition:
        raise ValueError(message)


def _ceil_div(numerator, denominator):
    return -((-numerator) // denominator)


def normalize(profile):
    """Accept a JSON object or integer-keyed complete/partial histogram."""
    need(isinstance(profile, dict) and bool(profile), "nonempty histogram required")
    result = {}
    for raw_rank, count in profile.items():
        need(type(raw_rank) is int or (isinstance(raw_rank, str) and raw_rank.isdecimal()),
             "rank must be an integer or decimal integer string")
        rank = int(raw_rank)
        need(0 < rank < WIDTH, "rank must lie in 1..72")
        need(type(count) is int and count > 0, "child multiplicity must be a positive integer")
        need(rank not in result, "duplicate normalized rank")
        result[rank] = count
    return dict(sorted(result.items()))


@lru_cache(maxsize=512)
def _unit_scaled(b, z, bits, terms):
    """Enclose (1-z)^(-b) by scaled integers; 0<=b<=1, 0<=z<=1/2."""
    need(0 <= b <= 1 and 0 <= z <= Fraction(1, 2), "positive binomial domain")
    need(type(bits) is int and bits >= 8 and type(terms) is int and terms >= 1,
         "positive binomial precision")
    scale = 1 << bits
    if not b or not z:
        return scale, scale
    lower_term = upper_term = scale
    lower_sum = upper_sum = scale
    for n in range(1, terms + 1):
        ratio = z * (b + n - 1) / n
        lower_term = lower_term * ratio.numerator // ratio.denominator
        upper_term = _ceil_div(upper_term * ratio.numerator, ratio.denominator)
        lower_sum += lower_term
        upper_sum += upper_term
    # t_(N+1)/(1-z) bounds all omitted terms, including the first.
    tail_factor = z * (b + terms) / ((terms + 1) * (1 - z))
    upper_tail = _ceil_div(upper_term * tail_factor.numerator, tail_factor.denominator)
    return lower_sum, upper_sum + upper_tail


@lru_cache(maxsize=512)
def _power_scaled(q, b, bits, terms):
    need(q >= 1 and 0 <= b <= 1, "power enclosure domain")
    scale = 1 << bits
    exponent = 0
    unit = q
    while unit >= 2:
        unit /= 2
        exponent += 1
    lower, upper = _unit_scaled(b, 1 - 1 / unit, bits, terms)
    two_lower, two_upper = _unit_scaled(b, Fraction(1, 2), bits, terms)
    for _ in range(exponent):
        lower = lower * two_lower // scale
        upper = _ceil_div(upper * two_upper, scale)
    return lower, upper


def power_bounds(q, b, *, bits=BITS, terms=TERMS):
    """Exact rational lower/upper bounds for q**b, q>=1, 0<=b<=1."""
    q, b = Fraction(q), Fraction(b)
    lower, upper = _power_scaled(q, b, bits, terms)
    return Fraction(lower, 1 << bits), Fraction(upper, 1 << bits)


def moment(profile, b, *, stock=STOCK, bits=BITS, terms=TERMS):
    """Enclose sum H[r]*r*(73/r)^b/(73*stock), including partial profiles.

    A partial histogram is permitted only here so omission costs can be measured;
    certify() requires the complete rank-mass identity for both profiles.
    """
    profile, b = normalize(profile), Fraction(b)
    need(type(stock) is int and stock > 0, "positive integer stock required")
    need(0 <= b <= 1, "moment parameter must lie in [0,1]")
    if not b:
        exact = Fraction(sum(rank * count for rank, count in profile.items()), WIDTH * stock)
        return exact, exact
    lower_sum = upper_sum = 0
    for rank, count in profile.items():
        lower, upper = _power_scaled(Fraction(WIDTH, rank), b, bits, terms)
        lower_sum += rank * count * lower
        upper_sum += rank * count * upper
    denominator = WIDTH * stock
    scale = 1 << bits
    return (Fraction(lower_sum // denominator, scale),
            Fraction(_ceil_div(upper_sum, denominator), scale))


def _difference(a, b):
    return a[0] - b[1], a[1] - b[0]


def _slack(bounds):
    return 1 - bounds[1], 1 - bounds[0]


def _strings(bounds):
    return [str(value) for value in bounds]


def _add_child(profile, rank):
    result = dict(profile)
    result[rank] = result.get(rank, 0) + 1
    return result


def certify(profile, baseline_profile, baseline_claim):
    """Certify the fixed moment comparison, not native/outer admission.

    `profile` is the full histogram independently reconstructed by the caller.
    The baseline claim is pinned through its exact saving parameter and matching
    full profile.  Authentication of its bytes and construction is the caller's
    separate obligation.  Output is JSON serializable and contains exact bounds.
    """
    profile, baseline_profile = normalize(profile), normalize(baseline_profile)
    need(isinstance(baseline_claim, dict), "baseline claim object required")
    need(Fraction(baseline_claim["complex_lower"]) == BASELINE_COMPLEX_LOWER,
         "exact PR2930 complex_lower required")
    previous = Fraction(baseline_claim["kappa"])
    need(previous == BASELINE_COMPLEX_LOWER - HEADLINE_GUARD,
         "exact full PR2930 guarded headline required")
    need(baseline_claim["live_families"] == STOCK and baseline_claim["replicas"] == REPLICAS
         and baseline_claim["calls"] == 9 * REPLICAS, "fixed T74 live-stock/call model required")
    need(normalize(baseline_claim["profile"]) == baseline_profile, "baseline claim/profile binding")
    for name, value in (("candidate", profile), ("baseline", baseline_profile)):
        need(sum(rank * count for rank, count in value.items()) == RANK_MASS,
             name + " complete rank-mass identity")
    need(profile.get(14) == 1, "one reconstructed rank14 residual required")

    at_previous = moment(profile, previous)
    baseline_at_previous = moment(baseline_profile, previous)
    difference = _difference(at_previous, baseline_at_previous)
    need(at_previous[1] < 1, "candidate strictly below one at exact old headline")
    need(baseline_at_previous[1] < 1, "baseline favorable at its guarded headline")
    need(difference[1] < 0, "candidate strictly cheaper than baseline at old headline")
    at_candidate = moment(profile, CANDIDATE_COMPLEX_LOWER)
    need(at_candidate[1] < 1, "candidate strictly below one at pinned complex_lower")
    upper_parameter = CANDIDATE_COMPLEX_LOWER + UPPER_PROBE_GAP
    at_upper = moment(profile, upper_parameter)
    need(at_upper[0] > 1, "true moment above one at upper probe")

    # These deliberately incomplete/overcharged bills isolate cost sensitivity.
    omitted = dict(profile)
    del omitted[14]
    omitted_at_previous = moment(omitted, previous)
    omitted_charge = moment({14: 1}, previous)
    old_slack = _slack(at_previous)
    omission_ratio = (omitted_charge[0] / old_slack[1], omitted_charge[1] / old_slack[0])
    need(omitted_at_previous[1] < at_previous[0], "omitted residual strictly undercharges")
    need(omission_ratio[0] > 3, "rank14 omission exceeds three old-headline margins")
    extra4 = moment(_add_child(profile, 4), previous)
    extra5 = moment(_add_child(profile, 5), previous)
    extra32_old = moment(_add_child(profile, 32), previous)
    extra32_candidate = moment(_add_child(profile, 32), CANDIDATE_COMPLEX_LOWER)
    need(extra4[1] < 1, "one extra rank4 fits old-headline moment slack")
    need(extra5[0] > 1, "one extra rank5 exceeds old-headline moment slack")
    need(extra32_old[0] > 1 and extra32_candidate[0] > 1,
         "added rank32 truly exceeds one at both parameters")
    need(power_bounds(Fraction(1), previous) == (1, 1), "unit power identity")
    need(moment(profile, 0) == (Fraction(RANK_MASS, WIDTH * STOCK),) * 2,
         "zero-parameter exact identity")

    return {
        "status": "PASS_INDEPENDENT_COMPLETE_PROFILE_MOMENT_NO_NEW_KAPPA",
        "method": "range-reduced positive generalized-binomial series; 192 terms; outward 256-bit dyadic bounds",
        "baseline_head": BASELINE_HEAD, "candidate_head": CANDIDATE_HEAD,
        "width": WIDTH, "live_stock": STOCK, "replicas": REPLICAS, "rank_mass": RANK_MASS,
        "parameter_semantics": "complex_lower is b directly; kappa is complex_lower minus 1e-46 and 1e-70",
        "at_exact_previous_headline": {
            "b": str(previous), "candidate": _strings(at_previous),
            "baseline": _strings(baseline_at_previous), "candidate_minus_baseline": _strings(difference),
            "candidate_slack": _strings(old_slack),
        },
        "at_pinned_candidate_complex_lower": {
            "b": str(CANDIDATE_COMPLEX_LOWER), "moment": _strings(at_candidate),
            "slack": _strings(_slack(at_candidate)),
        },
        "upper_probe": {"b": str(upper_parameter), "gap": str(UPPER_PROBE_GAP),
                        "moment": _strings(at_upper), "certified_sign": "lower_bound > 1"},
        "sensitivity": {
            "omitted_rank14_mass_defect": 14,
            "omitted_rank14_moment_at_old": _strings(omitted_at_previous),
            "omitted_rank14_charge_at_old": _strings(omitted_charge),
            "omitted_rank14_charge_over_complete_slack": _strings(omission_ratio),
            "extra_rank4_at_old": _strings(extra4), "extra_rank5_at_old": _strings(extra5),
            "extra_rank32_at_old": _strings(extra32_old),
            "extra_rank32_at_candidate_lower": _strings(extra32_candidate),
            "one_extra_child_threshold_at_old": "ranks 1..4 remain below one; ranks 5..72 exceed one",
        },
        "scope": "Fixed complete paid histogram and exact moment only. Raw ownership, operator restoration, physical stock, private buffers, coefficients, precision, all-size compilation and native/outer admission are separate obligations.",
    }


def main():
    """Read only: emit the certificate to stdout; create no receipt or cache."""
    inputs = Path(__file__).resolve().parent / "inputs"
    read = lambda name: json.loads((inputs / name).read_text(encoding="utf-8"))
    print(json.dumps(certify(read("PROFILE.json"), read("baseline-PROFILE.json"),
                             read("baseline-CLAIM.json")), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
