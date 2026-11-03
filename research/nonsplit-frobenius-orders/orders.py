"""Exact symmetry orders. Produced by Nick Petalas. Apache-2.0."""

from collections import Counter
from math import factorial, prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


def gl_order(q, dimension):
    require(2 <= q <= 256 and 0 <= dimension <= 32, "GL domain")
    return prod(q**dimension - q**i for i in range(dimension))


def local_order(q, p, heights):
    """Bounded executable version; the written formula has no size cap."""
    require(p in (2, 3, 5, 7, 11, 13), "unsupported characteristic")
    require(isinstance(q, int) and 2 <= q <= 256, "field size")
    require(q in tuple(p**i for i in range(1, 9)), "field characteristic")
    require(len(heights) <= 4, "generator count")
    require(all(isinstance(h, int) and 1 <= h <= 4 for h in heights), "height")
    dimension = p ** sum(heights)
    require(dimension <= 16, "local dimension")
    multiplicities = Counter(heights)
    kernels = tuple(dimension - p ** sum(max(j - h, 0) for j in heights)
                    for h in heights)
    exponent = sum(kernels) - sum(r*r for r in multiplicities.values())
    require(exponent >= 0, "negative nonlinear exponent")
    return q**exponent * prod(gl_order(q, r) for r in multiplicities.values())


def product_orders(q, p, types):
    """Each row is (residue degree, height tuple, number of copies)."""
    require(1 <= len(types) <= 4, "product size")
    require(len({(d, tuple(sorted(h))) for d, h, _ in types}) == len(types),
            "combine identical types")
    automorphisms, units, dimension = 1, 1, 0
    for degree, heights, copies in types:
        require(1 <= degree <= 8 and 1 <= copies <= 4, "type multiplicity")
        residue = q**degree
        order = local_order(residue, p, heights)
        local_dimension = p ** sum(heights)
        automorphisms *= (degree*order)**copies * factorial(copies)
        units *= ((residue-1)*residue**(local_dimension-1))**copies
        dimension += degree*local_dimension*copies
    stabilizer = units**2 * automorphisms
    ambient = gl_order(q, dimension)**3
    require(ambient % stabilizer == 0, "nonintegral orbit")
    return {"automorphisms": automorphisms, "units": units,
            "stabilizer": stabilizer, "gl_orbit": ambient // stabilizer,
            "dimension": dimension}
