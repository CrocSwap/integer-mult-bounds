# SPDX-License-Identifier: Apache-2.0
"""Exact real-arithmetic lowering, not a physical stream implementation."""

from fractions import Fraction as Q

MAX_RECIPE = 32
POLICIES = ("scratch", "source_walk", "target_walk")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def coefficient(a, b):
    require(type(a) is int and type(b) is int and b != 0, "integer fraction")
    q = Q(a, b)
    require(abs(q.numerator) <= 255, "bounded numerator")
    require(q.denominator <= 4096, "bounded denominator")
    require(q.denominator & (q.denominator - 1) == 0, "dyadic fraction")
    return q


def fractional_walk(numerator, denominator, sign, maximum, *, on_target):
    """Two equal-cost digit walks with different intermediate-width contracts."""
    whole, remainder = divmod(numerator, denominator)
    shifts = denominator.bit_length() - 1
    cost = whole + remainder.bit_count() + 2 * shifts
    if cost >= maximum:
        return None
    recipe = [("add", 0, 1, sign)] * whole
    for index in range(shifts):
        recipe.append(("double", 0) if on_target else ("half", 1))
        if remainder >> (shifts - index - 1) & 1:
            recipe.append(("add", 0, 1, sign))
    recipe.extend([("half", 0) if on_target else ("double", 1)] * shifts)
    require(len(recipe) == cost, "complete inverse shifts are charged")
    return recipe


def lower(kind, a=1, b=1, *, policy="scratch"):
    """Local indices 0=target, 1=source, 2=initially-zero scratch."""
    require(policy in POLICIES, "lowering policy")
    require(kind in ("clear", "copy", "add", "scale"), "scalar kind")
    if kind == "clear":
        return [("clear", 0)]
    if kind == "copy":
        return [("copy", 0, 1)]
    q = coefficient(a, b)
    if kind == "scale":
        n = abs(q.numerator)
        require(n > 0 and n & (n - 1) == 0, "power-of-two scale")
        exponent = n.bit_length() - q.denominator.bit_length()
        return ([("neg", 0)] if q < 0 else []) + [
            ("double" if exponent > 0 else "half", 0)
        ] * abs(exponent)
    if not q:
        return []
    n, d = abs(q.numerator), q.denominator
    sign = 1 if q > 0 else -1
    direct = [("add", 0, 1, sign)] * n if d == 1 and n <= 4 else None
    recipe = [("copy", 2, 1)]
    for bit in bin(n)[3:]:
        recipe.append(("double", 2))
        if bit == "1":
            recipe.append(("add", 2, 1, 1))
    recipe.extend([("half", 2)] * (d.bit_length() - 1))
    recipe.extend([("add", 0, 2, sign), ("clear", 2)])
    if direct is not None and len(direct) <= len(recipe):
        recipe = direct
    if policy != "scratch":
        candidate = fractional_walk(
            n, d, sign, len(recipe), on_target=policy == "target_walk"
        )
        if candidate is not None:
            recipe = candidate
    require(len(recipe) <= MAX_RECIPE, "bounded recipe")
    return recipe


def execute(recipe, initial):
    """Replay three rows over independent arbitrary target/source columns."""
    require(len(recipe) <= MAX_RECIPE, "bounded instruction list")
    require(len(initial) == 3 and all(len(row) == 2 for row in initial), "three rows")
    rows = [tuple(map(Q, row)) for row in initial]
    for instruction in recipe:
        require(len(instruction) >= 2, "instruction shape")
        kind, target = instruction[:2]
        require(type(target) is int and 0 <= target < 3, "target index")
        require(kind in ("add", "copy", "clear", "neg", "double", "half"), "unit kind")
        if kind in ("add", "copy"):
            require(len(instruction) == (4 if kind == "add" else 3), "binary shape")
            source = instruction[2]
            require(type(source) is int and 0 <= source < 3, "source index")
            require(source != target, "distinct binary operands")
            if kind == "copy":
                rows[target] = rows[source]
            else:
                sign = instruction[3]
                require(type(sign) is int and sign in (-1, 1), "unit sign")
                rows[target] = tuple(
                    x + sign * y
                    for x, y in zip(rows[target], rows[source], strict=True)
                )
        else:
            require(len(instruction) == 2, "unary shape")
            factor = {"clear": 0, "neg": -1, "double": 2, "half": Q(1, 2)}[kind]
            rows[target] = tuple(factor * x for x in rows[target])
    return tuple(rows)


def certify(kind, a=1, b=1, recipe=None, *, policy="scratch"):
    default_recipe = lower(kind, a, b, policy=policy)
    recipe = default_recipe if recipe is None else recipe
    q = coefficient(a, b)
    target = {"clear": (0, 0), "copy": (0, 1), "add": (1, q), "scale": (q, 0)}[kind]
    result = execute(recipe, ((1, 0), (0, 1), (0, 0)))
    require(
        result == (target, (0, 1), (0, 0)),
        "macro identity/source preservation/scratch cleanup",
    )
    return recipe


def alphabet():
    """Thirty unit instructions, including destructive copy/clear on any row."""
    result = [
        (kind, r) for kind in ("clear", "neg", "double", "half") for r in range(3)
    ]
    result += [("copy", t, s) for t in range(3) for s in range(3) if t != s]
    result += [
        ("add", t, s, sign)
        for t in range(3)
        for s in range(3)
        if t != s
        for sign in (-1, 1)
    ]
    require(len(result) == 30, "complete unit alphabet")
    return result


def exclude_short_blocks():
    """Exact breadth-first closure through length 3, with zero scratch."""
    start = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(0), Q(0)))
    forbidden = {
        ((0, -1), (1, -1), (0, 0)),
        ((-1, 1), (-1, 0), (0, 0)),
        ((-1, -1), (1, 0), (0, 0)),
        ((0, 1), (-1, -1), (0, 0)),
    }
    states = {start}
    counts = [1]
    for _ in range(3):
        following = set(states)
        require(len(states) <= 30_000, "bounded search layer")
        for state in states:
            for instruction in alphabet():
                following.add(execute([instruction], state))
        states = following
        require(not states & forbidden, "no shorter forward or inverse block")
        counts.append(len(states))
    return {
        "alphabet": 30,
        "cumulative_states": counts,
        "excluded_lengths": [0, 1, 2, 3],
    }
