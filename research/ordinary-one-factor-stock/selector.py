"""Opt-in one-factor stock plan for PR2899's existing execute_plan hook.

Tekalign, with substantial OpenAI Codex assistance; Apache-2.0.
Uses Jose Manuel's encoded selector/ownership vocabulary unchanged. The smaller
NODE-guard divisor is Nick Petalas's PR3246 result. This is a conditional
consumer adapter, not admission of a different physical-depth format.
"""
from dataclasses import replace

import encoded
from cardinal_counts import Count
from words import need


def select_guard_stock(original, q, profile=encoded.Profile(row_factor=28416),
                       compatibility=9475):
    """All data-dependent arithmetic stays on Count tapes.

    profile.row_factor is W, not W*Q. q, profile and compatibility are compiled
    source constants. Use only with a callee whose requirement is the NODE
    guard contract; a dual full-depth-format consumer needs the legacy plan.
    The caller owns every returned Count and must close it after consumption.
    """
    need(type(q) is int and q >= 2, "compiled radix at least two")
    need(type(compatibility) is int and compatibility >= 1,
         "positive compiled compatibility factor")
    need(type(profile.row_factor) is int and profile.row_factor >= 1,
         "positive live-family factor")
    need(type(profile.dimension) is int and type(profile.child_rank) is int
         and 1 <= profile.child_rank < profile.dimension,
         "contracting compiled depth profile")
    need(type(profile.numerator) is int and type(profile.denominator) is int
         and profile.denominator > 0
         and 0 <= profile.numerator <= profile.denominator,
         "compiled width exponent between zero and one")
    plan = encoded.select(original, q, profile)
    try:
        if compatibility != 1 and not plan["depth"].zero():
            plan["stock"].multiply_small(compatibility)
        # The first selection found the least radix power covering b^D. Grow
        # it to cover Q*b^D. Recompute BOTH fit and the body after changing k.
        while encoded.compare(plan["rows"], plan["stock"]) < 0:
            plan["rows"].multiply_small(q)
            plan["borrowed"].increment()
        twice = Count(plan["borrowed"])
        try:
            twice.multiply_small(2)
            plan["fits"] = encoded.compare(twice, original) < 0
        finally:
            twice.close()
        for key in ("body", "remainder"):
            old = plan[key]
            plan[key] = Count.literal(0)
            old.close()
        if plan["fits"]:
            remaining = encoded.subtract(original, plan["borrowed"])
            dimension = Count.literal(profile.dimension)
            try:
                body, remainder = encoded.divide(remaining, plan["width"])
                plan["body"].close()
                plan["remainder"].close()
                plan["body"], plan["remainder"] = body, remainder
                plan["fits"] = encoded.compare(body, dimension) >= 0
            finally:
                remaining.close()
                dimension.close()
        return plan
    except BaseException:
        close_plan(plan)
        raise


def close_plan(plan):
    for key, value in plan.items():
        if key != "fits":
            value.close()


def legacy_profile(profile, compatibility):
    """Comparison input only; no production caller is silently replaced."""
    return replace(profile, row_factor=profile.row_factor * compatibility)
