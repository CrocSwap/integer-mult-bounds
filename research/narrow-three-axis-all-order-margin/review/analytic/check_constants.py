"""Exact rational audit of the analytic budget, independent of author code."""
from fractions import Fraction as F
from math import factorial
import json


def require(value, message):
    if not value:
        raise ValueError(message)


def power(exponent):
    return F(2**exponent) if exponent >= 0 else F(1, 2**(-exponent))


minimum = F(7, 131072)
gradient, shifted_mass = 156, 6656
h_bound = power(-30)
box = power(-24)
after_box = minimum - gradient * box
after_taylor = after_box - shifted_mass * h_bound
require(after_box > power(-15), "continuous box margin")
require(after_taylor >= power(-16), "complete Taylor tail")
require(factorial(8) * 2**8 < 2**24, "determinant mass ceiling")
require(power(24) * power(-42) <= power(-18), "higher-w tail")
require(power(-16) - power(-18) >= power(-18), "remaining determinant")

p = 2**20
require(F(24) < F(p, 9216), "log endpoint bound using ln(2)<1")
require(F(1, 1024*p) <= h_bound, "physical h bound")
require(F(1, 2**32 * 32**4) <= power(-42), "w versus h bound")
require(power(-26) + F(2, p**70) + power(-31) < box,
        "physical source center neighborhood")
physical_ratio = F(2**299 * p**55, p**72)
require(physical_ratio == power(-41) < 1, "actual lower-entry difference")
require(379 + 72*20 == 1819 < p, "fractional precision endpoint")

require(16 * power(-68) <= power(-21) - power(-22),
        "forward displacement perturbation")
require(power(17) * power(-68) <= power(-49) - power(-50),
        "inverse displacement perturbation")
require(3 * power(-73) < power(-71), "three factor error sources")
require(F(32**2, 8) - 8 > 93, "alias bound even using ln(2)<1")

# These controls invalidate this proof budget, not the source theorem itself.
require(minimum - gradient*box - shifted_mass*power(-15) < 0,
        "weakened h guard must fail this certificate")
require(F(2**299*p**55, p**54) > 1,
        "weakened t guard must fail the lower-entry comparison")
print(json.dumps({
    "status": "PASS_INDEPENDENT_ANALYTIC_BUDGET",
    "after_center_variation": str(after_box),
    "after_complete_Taylor_tail": str(after_taylor),
    "physical_lower_entry_allowance_ratio_at_endpoint": str(physical_ratio),
    "sufficient_fractional_bits_at_p_min": 1819,
    "negative_controls": ["weakened_h_guard", "weakened_t_guard"],
    "scope": "Exact arithmetic for universal inequalities justified in the root review; no source-generation or full-runtime claim."
}, indent=2, sort_keys=True))
