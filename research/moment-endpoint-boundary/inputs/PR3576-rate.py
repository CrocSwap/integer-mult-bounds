# SPDX-License-Identifier: Apache-2.0
"""Exact complete-profile budget for the retuned ordinary/T74 interface.

Hiroki Kumazaki, with substantial OpenAI Codex assistance.
Uses Douglas Colkitt's retained outward log/exp engine and Nick Petalas's
independently implemented PR3342 positive-series engine. No numerical-method
priority is claimed. These checks do not execute the production payload.
"""

from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import types


ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "research/rank7-joint-endframes/allocation/PROFILE.json":
        "94a819747f3ced41f1544ada0036c983fc0c92847b9644380f877a06cd7931cf",
    "research/rank7-joint-endframes/allocation/ORDER.json":
        "519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1",
    "research/complex-local-word-ceiling/ceiling.py":
        "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
    "research/rank7-selected-transfer-budget/intervals.py":
        "a247fb83211d2ae83305d73126fc13f2a699e3657a580522cf81d90884e36447",
}
DIMENSION = 73
FAMILIES = 896 * 74
SIGMA = Q(998271, 10**6)
TAU = Q(332353, 332929)
BETA = Q(1, 1000)
ALPHA = Q(998273, 10**6)
RESERVATION = Q(499, 500)
OLD_TAU = Q(99830289, 10**8)
OLD_ALPHA = Q(199661, 200000)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def read_sources(root=ROOT):
    """Authenticate all bytes before compiling either executable input."""
    raw = {}
    for relative, expected in PINS.items():
        path = Path(root) / relative
        need(path.is_file() and not path.is_symlink(), "regular source: " + relative)
        value = path.read_bytes()
        need(sha256(value).hexdigest() == expected, "source hash: " + relative)
        raw[relative] = value
    modules = []
    for name, relative in (
            ("retuned_ceiling", "research/complex-local-word-ceiling/ceiling.py"),
            ("retuned_independent", "research/rank7-selected-transfer-budget/intervals.py")):
        module = types.ModuleType(name)
        exec(compile(raw[relative], relative, "exec", optimize=0), module.__dict__)
        modules.append(module)
    profile = modules[1].profile(json.loads(raw[next(iter(PINS))]), DIMENSION)
    order = json.loads(raw["research/rank7-joint-endframes/allocation/ORDER.json"])
    need(type(order) is list and all(type(row) is list and len(row) == 2
         and all(type(value) is int for value in row) for row in order),
         "integer call-order pairs")
    need(len(order) == 666 and set(map(tuple, order)) ==
         {(stage, replica) for stage in range(9) for replica in range(74)},
         "complete 74-replica nine-stage order")
    need(sum(rank * count for rank, count in profile.items()) == 4816512
         and sum(profile.values()) == 2394506,
         "complete paid profile, including idle children")
    return profile, order, modules


def first_moment(engine, profile, exponent):
    lower = upper = Q(0)
    for rank, count in profile.items():
        left, right = engine.child_cost(rank, DIMENSION, 1 - exponent)
        lower += count * left / FAMILIES
        upper += count * right / FAMILIES
    return lower, upper


def two_moments(engines, profile, exponent):
    first = first_moment(engines[0], profile, exponent)
    second = engines[1].moment(profile, DIMENSION, FAMILIES, 1 - exponent)
    need(all(left <= right for left, right in (first, second)), "ordered moment enclosures")
    need(max(first[0], second[0]) <= min(first[1], second[1]),
         "independent complete-moment enclosures overlap")
    return first, second


def outward(bounds, places=30):
    scale = 10**places
    lower, upper = bounds
    return dict(lower=lower.numerator * scale // lower.denominator,
                upper=-((-upper.numerator * scale) // upper.denominator),
                denominator=scale)


def budget(tau, sigma, beta, alpha, reservation=RESERVATION):
    """A sufficient strict-power contract; see the all-size tree proof."""
    need(0 < tau < 1 and 0 < sigma < 1 and 0 < beta < 1 and 0 < alpha < 1,
         "positive subunit rate parameters")
    internal = max(tau, sigma)
    leaf = sigma + beta * (1 - sigma)
    margins = dict(internal=alpha - internal, leaf=alpha - leaf,
                   reservation=alpha - reservation)
    for name, gap in margins.items():
        need(gap > 0, "strict " + name + " power margin")
    return dict(internal=internal, leaf=leaf, reservation=reservation, margins=margins)


def rejected(action, expected):
    try:
        action()
    except ValueError as error:
        need(expected in str(error), "control rejected for the wrong reason")
        return True
    raise ValueError("control unexpectedly accepted: " + expected)


def run(root=ROOT):
    profile, order, engines = read_sources(root)
    need(TAU == 1 - Q(576, 332929), "PR3562 ordinary exponent")
    need(TAU < SIGMA, "changed ordering requires the tau<=sigma tree branch")
    moments = two_moments(engines, profile, SIGMA)
    need(all(upper < 1 for _lower, upper in moments), "complete T74 moment passes")
    # A round, source-relative gap is convenient for the written tree bound.
    need(all(1 - upper > Q(9, 10**8) for _lower, upper in moments),
         "strict moment gap above nine times ten to minus eight")
    rates = budget(TAU, SIGMA, BETA, ALPHA)
    need(rates["leaf"] == Q(998272729, 10**9), "actual stopping-rule leaf exponent")
    need(rates["margins"] == dict(internal=Q(1, 500000),
         leaf=Q(271, 10**9), reservation=Q(273, 10**6)),
         "complete exact power margins")

    # These are failed mathematical alternatives, not altered PASS strings.
    naive = two_moments(engines, profile, TAU)
    need(all(lower > 1 for lower, _upper in naive),
         "ordinary exponent cannot itself serve as T74 moment exponent")
    extra_child = dict(profile)
    extra_child[1] += 1
    extra = two_moments(engines, extra_child, SIGMA)
    need(all(lower > 1 for lower, _upper in extra),
         "one uncharged rank-one child breaks the chosen moment")
    controls = {
        "direct_ordinary_moment_rejected_by_both_engines": True,
        "one_extra_rank_one_child_rejected_by_both_engines": True,
        "old_ordinary_profile_rejected": rejected(
            lambda: budget(OLD_TAU, SIGMA, BETA, ALPHA), "strict internal power margin"),
        "earlier_stopping_at_power_500_rejected": rejected(
            lambda: budget(TAU, SIGMA, Q(1, 500), ALPHA), "strict leaf power margin"),
        "omitted_leaf_penalty_target_rejected": rejected(
            lambda: budget(TAU, SIGMA, BETA, SIGMA + Q(1, 10**6)), "strict leaf power margin"),
        "unabsorbed_internal_log_rejected": rejected(
            lambda: budget(TAU, SIGMA, BETA, SIGMA), "strict internal power margin"),
        "unabsorbed_reservation_log_rejected": rejected(
            lambda: budget(TAU, SIGMA, BETA, ALPHA, ALPHA), "strict reservation power margin"),
    }
    return dict(
        status="PASS_CONDITIONAL_RETUNED_T74_RATE",
        calls=len(order), families=FAMILIES, dimension=DIMENSION,
        profile={str(rank): count for rank, count in sorted(profile.items())},
        children=sum(profile.values()), rank_mass=sum(r * n for r, n in profile.items()),
        sigma=str(SIGMA), ordinary_exponent=str(TAU), stopping_exponent=str(BETA),
        internal_exponent=str(rates["internal"]), leaf_exponent=str(rates["leaf"]),
        reservation_exponent=str(rates["reservation"]), final_exponent=str(ALPHA),
        moment_gap_lower="9/100000000",
        moments={"retained_256_bit": outward(moments[0]),
                 "independent_positive_series": outward(moments[1])},
        rejected_alternatives={
            "direct_ordinary_moment": [outward(value) for value in naive],
            "one_extra_rank_one_child": [outward(value) for value in extra]},
        margins={name: str(gap) for name, gap in rates["margins"].items()},
        layer_saving=str(1 - ALPHA), prior_layer_saving=str(1 - OLD_ALPHA),
        improvement=str(OLD_ALPHA - ALPHA), controls=controls,
        scope="Conditional complete T74 layer with retuned ordinary cost; no payload, integer kappa or outer-transfer admission.")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
