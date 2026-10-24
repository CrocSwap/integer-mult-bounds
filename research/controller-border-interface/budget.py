"""Exact optimistic moment obstruction for idle-free border controllers.

This proves a finite-invoice obstruction, conditional on the stated determinant
and output-count invariants.  It does not certify a native border implementation.
All numerical bounds use integer comparisons, not floating point arithmetic.
Prepared by Dillon with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRECISION = 48


def need(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(None)
def power(base, exponent):
    """Outward dyadic enclosure of integer base**rational exponent in [0,1]."""
    exponent = Q(exponent)
    need(isinstance(base, int) and base >= 1, "Positive integer power base")
    need(0 <= exponent <= 1, "Power exponent in [0,1]")
    if exponent in (0, 1) or base == 1:
        value = Q(base if exponent else 1)
        return value, value
    scale = 1 << PRECISION
    a, q = exponent.numerator, exponent.denominator
    target = base ** a * scale ** q
    lo, hi = scale, base * scale
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** q <= target:
            lo = mid
        else:
            hi = mid
    need(lo ** q <= target < (lo + 1) ** q, "Exact nth-root enclosure")
    return Q(lo, scale), Q(lo + 1, scale)


def add(*values):
    return sum(x[0] for x in values), sum(x[1] for x in values)


def scale(value, factor):
    products = [value[0] * factor, value[1] * factor]
    return min(products), max(products)


def point(value):
    return Q(value), Q(value)


def moment(profile, t):
    return add(*(scale(power(r, t), count) for r, count in profile.items()))


def shown(value):
    return {"lower": str(value[0]), "upper": str(value[1])}


def read_profiles():
    complex_data = json.loads((ROOT / "research/joint-helper-lattice/RESULT.json").read_text())
    bit_data = json.loads((ROOT / "research/query-thinned-controllers/BIT-CONTROLLER.json").read_text())["invoice"]
    complex_h = {int(r): n for r, n in complex_data["local_helpers"].items()}
    complex_c = {int(r): n for r, n in complex_data["local_paid"].items()}
    full = bit_data["thick_calls"]
    bit_target = Counter({int(r): n for r, n in bit_data["targets"].items()})
    bit_cost = Counter({int(r): n for r, n in bit_data["paid"].items()})
    bit_target.subtract({int(r): n for r, n in bit_data["main"].items()})
    bit_cost.subtract({int(r): n for r, n in bit_data["whole_idle"].items()})
    bit_cost[1] -= bit_data["thin_queries"]
    need(full > 0 and all(n >= 0 and n % full == 0 for n in [*bit_target.values(), *bit_cost.values()]),
         "Exact BIT local profile division")
    bit_h = {r: n // full for r, n in bit_target.items() if n}
    bit_c = {r: n // full for r, n in bit_cost.items() if n}
    need(complex_h == {4: 28, 7: 7, 8: 47, 9: 326}, "Pinned complex helpers")
    need(complex_c == {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}, "Pinned complex paid calls")
    need(bit_h == {8: 439}, "Pinned BIT helpers")
    need(bit_c == {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}, "Pinned BIT paid calls")
    return {"complex": (8, 112, complex_h, complex_c, Q(6)),
            "BIT": (7, 111, bit_h, bit_c, Q(15, 2))}


def coefficients(b, v, helpers, paid, saving):
    t = 1 - Q(saving)
    h = add(moment(helpers, t), scale(moment(paid, t), -1))
    a = add(scale(power(1 + b, t), 2 * v), h, point(-v))
    exact_b = add(scale(add(power(1 + 2 * b, t), scale(power(1 + b, t), -1)), 4 * v), scale(h, 2), point(v))
    # Concavity gives x**t <= u**t + t*u**(t-1)*(x-u).
    # Here u=1+b, x=1+b+2b/p; using u**(t-1)=u**t/u.
    jensen_b = add(scale(power(1 + b, t), Q(4 * v * b) * t / (1 + b)), scale(h, 2), point(v))
    first = add(scale(power(1 + 3 * b, t), 2 * v), scale(h, 3))
    second = add(scale(power(1 + 2 * b, t), 4 * v), scale(h, 4), point(-v))
    return {"saving": str(saving), "t": str(t), "h": h, "A": a,
            "exact_B": exact_b, "Jensen_B": jensen_b,
            "p_one_margin": first, "p_two_margin": second}


def explicit_profiles(b, v, helpers, paid, p):
    need(isinstance(p, int) and p >= 1, "Positive controller parameter")
    target = Counter({r: (p + 2) * n for r, n in helpers.items()})
    cost = Counter({r: (p + 2) * n for r, n in paid.items()})
    cost[1] += v * (p - 1)
    if p == 1:
        target[1 + 3 * b] += 2 * v
    else:
        target[1 + 2 * b] += 4 * v
        target[1 + b] += 2 * v * (p - 2)
    return target, cost


def run():
    output = {"status": "PASS_OPTIMISTIC_BORDER_BUDGET_CEILING", "power_precision_bits": PRECISION,
              "scope": "All positive integer p, unchanged full-call and thin-query invoices, 2vp main fields and determinant rank sum 2v[p+b(p+2)], even granting coefficient extraction and extra routing free.",
              "target_saving": "1/100", "profiles": {}}
    for name, (b, v, helpers, paid, separator) in read_profiles().items():
        cutoff = Q(3, 500) if name == "complex" else Q(7, 1000)
        signed = {r: helpers.get(r, 0) - paid.get(r, 0) for r in set(helpers) | set(paid)}
        positive = {r: n for r, n in signed.items() if n > 0}
        negative = {r: -n for r, n in signed.items() if n < 0}
        need(all(r > separator for r in positive), "All positive helper terms above separator")
        need(all(r < separator for r in negative), "All negative helper terms below separator")
        need(1 + b > separator > 1, "Jensen main base above and thin query below separator")
        # Dividing the Jensen envelope by separator**t makes every summand
        # strictly increasing in t.  Failure at the cutoff therefore extends
        # to every saving in [cutoff,1], with Jensen valid for t in [0,1].
        checks = []
        for saving in (Q(1, 100), cutoff):
            row = coefficients(b, v, helpers, paid, saving)
            need(row["A"][1] < 0 and row["Jensen_B"][1] < 0, "All-p Jensen upper bound is negative")
            need(row["p_one_margin"][1] < 0 and row["p_two_margin"][1] < 0, "Explicit p=1 and p=2 are negative")
            need(row["exact_B"][1] < 0, "Explicit affine intercept is negative")
            checks.append({k: shown(value) if isinstance(value, tuple) else value for k, value in row.items()})
        controls = {}
        for p in (1, 2, 3, 16, 64):
            targets, costs = explicit_profiles(b, v, helpers, paid, p)
            rank_margin = sum(r * n for r, n in targets.items()) - sum(r * n for r, n in costs.items())
            need(rank_margin == 48 * p - (16 if name == "complex" else 15), "Independent exact rank-surplus control")
            if p >= 2:
                row = coefficients(b, v, helpers, paid, cutoff)
                direct = add(moment(targets, 1 - cutoff), scale(moment(costs, 1 - cutoff), -1))
                affine = add(scale(row["A"], p), row["exact_B"])
                need(max(direct[0], affine[0]) <= min(direct[1], affine[1]), "Direct invoice and affine formula agree")
        # A cheaper exponent passes this optimistic necessary test. This guards
        # against a verifier that rejects every controller by construction.
        saving, p = (Q(1, 200), 32) if name == "complex" else (Q(3, 500), 64)
        targets, costs = explicit_profiles(b, v, helpers, paid, p)
        margin = add(moment(targets, 1 - saving), scale(moment(costs, 1 - saving), -1))
        need(margin[0] > 0, "Strict positive optimistic invoice control")
        controls["smaller_saving_pass"] = {"saving": str(saving), "p": p, "margin": shown(margin),
                                             "scope": "Necessary moment test only; no border extraction or native admission claimed."}
        # Omitting the thin-query bill reverses the target-exponent conclusion.
        # The row is a deliberately invalid invoice, never a candidate result.
        targets, costs = explicit_profiles(b, v, helpers, paid, 64)
        costs[1] -= v * 63
        undercharged = add(moment(targets, Q(99, 100)), scale(moment(costs, Q(99, 100)), -1))
        need(undercharged[0] > 0, "Missing-query-cost fault reverses the conclusion")
        controls["invalid_missing_thin_queries"] = {"saving": "1/100", "p": 64,
                                                        "omitted_rank_one_calls": v * 63,
                                                        "invalid_margin": shown(undercharged)}
        # Repeated whole-controller evaluations may keep every independent
        # helper, but only one copy of each intended main output is required.
        # K>=2 therefore has main + K*(full helpers - full costs - thin costs).
        # At K=2,t=1 the determinant fixes an affine, strictly negative margin.
        # Rank separation proves negativity for all t in [0,1], and h(t)<0
        # makes every additional evaluation strictly worse.
        local_rank_difference = sum(r * n for r, n in signed.items())
        need(local_rank_difference < 0, "Local helper-minus-paid moment negative at t=1")
        k2_slope = 2 * v * (1 + b) + 2 * local_rank_difference - 2 * v
        k2_intercept = 4 * v * b + 4 * local_rank_difference + 2 * v
        need(k2_slope < 0 and k2_intercept < 0, "Two-evaluation rank margin negative for every p")
        for trial_p in (1, 2, 3, 16, 64):
            trial_targets, trial_costs = explicit_profiles(b, v, helpers, paid, trial_p)
            trial_targets.update({r: (trial_p + 2) * n for r, n in helpers.items()})
            direct_k2_rank = sum(r * n for r, n in trial_targets.items()) - 2 * sum(r * n for r, n in trial_costs.items())
            need(direct_k2_rank == k2_slope * trial_p + k2_intercept,
                 "Direct twice-evaluated invoice credits fresh helpers and main once")
        # Deliberately crediting duplicate main outputs is an invalid positive
        # control: repetition does not produce additional independent outputs.
        targets, costs = explicit_profiles(b, v, helpers, paid, 2)
        single_rank_margin = sum(r * n for r, n in targets.items()) - sum(r * n for r, n in costs.items())
        need(single_rank_margin > 0, "Duplicating every credited output would spuriously pass at t=1")
        repeated = {"minimum_evaluations": 2, "all_integer_p_at_least": 1,
                    "all_savings": ["0", "1"],
                    "two_evaluation_rank_margin": {"coefficient_of_p": k2_slope, "constant": k2_intercept},
                    "local_rank_helper_minus_paid": local_rank_difference,
                    "independent_helpers_credited_per_evaluation": True,
                    "main_outputs_credited_once": True,
                    "scope": "Whole-controller repeated evaluations with unchanged local invoices; no general exactification barrier.",
                    "invalid_duplicate_main_credit_control": {"p": 2, "saving": "0", "wrong_margin": 2 * single_rank_margin,
                                                             "correct_margin": 2 * k2_slope + k2_intercept}}
        output["profiles"][name] = {"block": b, "ports": v, "ceiling_strict": str(cutoff),
                                    "excluded_savings": [str(cutoff), "1"], "separator": str(separator),
                                    "signed_helpers_minus_paid": dict(sorted(signed.items())),
                                    "checks": checks, "controls": controls,
                                    "repeated_evaluation_obstruction": repeated}
    return output


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
