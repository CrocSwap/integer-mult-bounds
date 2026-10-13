"""Evaluate a declared final recurrence directly, independent of parent admission.

Different m/W/child counts are explicit hypotheses, not inferred constructions.
The default is the freshly recounted all72 nine-dimensional-center construction.
"""
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as Q
import argparse
import json
from pathlib import Path

import experiment as E


def decimal(x):
    x = Q(x)
    return Decimal(x.numerator)/Decimal(x.denominator)


def ranged_exp(engine, low, high):
    """Exact outward interval range reduction extends the retained exp engine."""
    E.require(0 <= low <= high, "nonnegative exponential input")
    squares = 0
    while high >= Q(1, 10):
        low /= 2; high /= 2; squares += 1
    low, high = engine.exponential(low, high)
    for _ in range(squares):
        low, high = engine.floor(low*low), engine.ceil(high*high)
    return low, high


def moment(engine, profile, m, live, b):
    E.require(type(m) is int and m > 1 and live > 0 and b >= 0, "positive recurrence parameters")
    low = high = Q(0)
    for r, n in E.ints(profile).items():
        E.require(type(n) is int and n > 0 and 0 < r < m, "proper integral child profile")
        l, u = engine.logarithm(Q(m, r))
        l, u = ranged_exp(engine, b*l, b*u)
        p = Q(r*n)/(m*live)
        low += p*l; high += p*u
    return engine.floor(low), engine.ceil(high)


def certify(engine, profile, m, live):
    """Decimal proposes a bracket; exact rational signs certify it."""
    live = Q(live)
    E.require(E.rank_mass(profile) < m*live, "positive mass deficit required")
    with localcontext() as ctx:
        ctx.prec = 75
        terms = [(decimal(Q(r*n)/(m*live)), decimal(Q(m,r)).ln())
                 for r, n in E.ints(profile).items()]
        low, high = Decimal(0), Decimal(1)
        E.require(sum(p*(high*x).exp() for p, x in terms) > 1, "root exceeds declared search interval")
        for _ in range(260):
            candidate = (low+high)/2
            if sum(p*(candidate*x).exp() for p, x in terms) < 1:
                low = candidate
            else:
                high = candidate
        tick = int((((low+high)/2)*10**24).to_integral_value(rounding=ROUND_FLOOR))
    lower = Q(tick, 10**24); upper = lower+Q(1, 10**24)
    low_sign = moment(engine, profile, m, live, lower)
    high_sign = moment(engine, profile, m, live, upper)
    E.require(low_sign[1] < 1 < high_sign[0], "exact direct-model bracket signs")
    return dict(lower=str(lower), upper=str(upper), lower_decimal=str(decimal(lower)),
                nominal_kappa_lower=str(decimal(lower/(1+lower))),
                residuals=dict(lower=[str(x-1) for x in low_sign], upper=[str(x-1) for x in high_sign]),
                strict_rational_signs=True)


def evaluate(profile, m=73, live=Q(7168)):
    E.require(__debug__, "Use normal Python: retained outer engine requires assertions")
    engines, bit, _ = E.pricing_engines()
    live = Q(live)
    bracket = certify(engines[1], profile, m, live)
    b = Q(bracket["lower"])
    # This is arithmetic under the retained transfer hypotheses. Geometry
    # changes still require their own realization; the old interface is unused.
    outer = engines[0].outer47(bit, b, engines[3]) if b < Q(1,32) else None
    return dict(status="PASS_DIRECT_DECLARED_RECURRENCE_COST", profile=E.ints(profile),
        m=m, live=str(live), capacity=str(m*live), mass=E.rank_mass(profile),
        deficit=str(m*live-E.rank_mass(profile)), complex_root=bracket, outer=outer,
        equation="sum_r r*n_r*(m/r)^b = m*W",
        interpretation="Child ranks/counts and m,W are hypotheses of this model; it does not invoke parent-interface acceptance.",
        outer_scope="47-constraint arithmetic with unchanged PR589; altered geometry requires the retained transfer hypotheses to hold there.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=E.ROOT / "build/roadmap48/PROFILES.json")
    parser.add_argument("--field", default="retained_owner_global")
    parser.add_argument("--m", type=int, default=73)
    parser.add_argument("--live", default="7168")
    parser.add_argument("--output", type=Path, default=E.ROOT / "build/roadmap48/DIRECT-COST.json")
    args = parser.parse_args()
    data = json.loads(args.profile.read_bytes())
    profile = data[args.field] if args.field else data
    result = evaluate(profile, args.m, Q(args.live))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    E.dump(args.output, result)
    print(result["status"], "b", result["complex_root"]["lower_decimal"],
          "kappa", result["outer"]["kappa_decimal"] if result["outer"] else "outside retained outer domain")


if __name__ == "__main__":
    main()
