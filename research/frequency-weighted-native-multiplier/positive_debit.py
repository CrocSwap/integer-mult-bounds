"""Price the weighted Gaussian calendar from its installed edges and physical sizes."""

from fractions import Fraction as Q

from strict_moment import UNIT, power_interval

BAND_LOWER = 2048
POSITIVE_DEBIT = Q(65081, 524288)
DELTA = Q(1, 2**128)


def certify_loss(recipe, lower):
    """Return the exact finite price for this two-type numerical recipe."""
    c = recipe.trial
    t = 1 - c
    targets = recipe.targets.histogram
    paid = recipe.paid.histogram
    cells = recipe.cells
    assert lower == BAND_LOWER and recipe.ambient == 306
    assert max(targets) == 258 and min(paid) == Q(1, 2)
    assert all(w > 0 and 5 * r <= 4 * k for (r, k), w in cells.items())
    assert all(sum(w for (p, k), w in cells.items() if p == r) == 1 for r in paid)

    # The first three positive terms of log(k/r) suffice for each real edge.
    psi = Q(0)
    for (r, k), share in cells.items():
        u = Q(k - r, k + r)
        log_lower = 2 * (u + u**3 / 3 + u**5 / 5)
        psi += paid[r] * share * r * log_lower
    target_axes = sum(count * k for k, count in targets.items())
    fringe = 10 * target_axes / (t * psi)
    assert target_axes == 135150528
    assert psi > Q(1790217668064, 10000)
    assert fringe < Q(7579, 1000)

    # All bounds below improve as H grows. Check their smallest eligible H.
    M = 2**1024
    upper = 2 * (M // (2048 * recipe.ambient))
    assert 5160 <= DELTA * upper
    assert (1 - DELTA) * M <= 1024 * recipe.ambient * upper
    assert upper > 516 * lower and M * DELTA >= 1
    assert t > Q(996, 1000) and 11 * t > 10
    assert 91 / (t * 2**10) + Q(2, M**5) < 2
    assert 2**46 < Q(M**4, 2**132)
    assert 2**20 < Q(M**4, 2**132)
    assert 2 * 52608 < M
    assert 4 * (lower + 2) * 6 < 5 * lower * 5
    assert 2**19 * (upper + lower) ** 77 + lower**77 < (M * lower) ** 77

    # Keep the upper physical period, complete group padding, both endpoint
    # roundings, and the endpoint of the integral's chosen upper band.
    finite_factor = (
        (1 + DELTA)
        * (1 + Q(4 * max(targets), 1024 * recipe.ambient))
        * Q(power_interval(1024 * recipe.ambient * lower, c)[1], UNIT)
        * (1 + fringe / lower + DELTA)
        / (1 - DELTA) ** 4
    )
    assert UNIT * finite_factor < power_interval(2, POSITIVE_DEBIT)[0]
    return {
        "debit": str(POSITIVE_DEBIT),
        "lower_band": lower,
        "weighted_target_axes": target_axes,
        "fringe": str(fringe),
        "psi_lower": str(psi),
        "upper_factor": str(finite_factor),
    }
