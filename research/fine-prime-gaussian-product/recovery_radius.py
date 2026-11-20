"""Certify integer rounding from geometric operator defects and absolute grid drops."""
from fractions import Fraction
from math import prod

from gaussian_pages import admit


def page_limit(geometry):
    if not geometry.use_caller_page_limit:
        return Fraction(1, 1 << (geometry.precision + 3))
    # The joint radius is at least 3 C eta/16, since K>=1 and z=1/4.
    # A single page at or above 8/(3C) already precludes strict rounding.
    source = prod(geometry.sources)
    c = source**2 << (2 * geometry.digit_bits + 4)
    return Fraction(8, 3*c)


def rounding_numerator(geometry, pages):
    q = geometry.precision
    s = prod(geometry.sources)
    c = s**2 << (2 * geometry.digit_bits + 4)
    k = 1 << sum(expand.output_shift + compress.output_shift for _,expand,compress in pages)
    drops = 64 * len(pages) + 64
    defects = [f.defect for _,a,b in pages for f in (a,b)]
    admit(all(d >= 0 for d in defects), "negative operator defect")
    easy = drops*c*k**3
    # This is the original sufficient guard and its full local hypothesis.
    if all(d < Fraction(1,1 << (q+3)) for d in defects) and 2*easy < 1 << q:
        return easy

    h = Fraction(1,1 << q)
    e = drops*h
    eta = sum(defects, Fraction(0))
    z = Fraction(1,4)
    forward_error = k*(eta*z+e)
    forward = z+forward_error
    product_drop = 2*k**2*h
    product_radius = forward**2 + product_drop
    # Every normalized interior factor contracts. Partial digital drops sum to e.
    admit(max(z,product_radius/k**2)+e < Fraction(1,2), "possible half-disk violation")
    product_error = forward_error*(forward+z) + product_drop
    bound = c*(product_error + k*eta*product_radius + k**3*e)
    # Keep the reported upper bound on the public q grid. This also bounds its size.
    rounded_up = -(-(bound.numerator << q) // bound.denominator)
    admit(2*rounded_up < 1 << q, "unresolved pre-rounding precision")
    return rounded_up
