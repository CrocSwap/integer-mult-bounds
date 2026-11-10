"""Independent exact matrix oracle; no seven-product formula or kernel import.

Fixture-only host integers are outside the physical program and its tariff.
@CubeJerry, with substantial OpenAI assistance. Apache-2.0.
"""

from hashlib import sha256
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def classical(first, second, dimension):
    require(type(dimension) is int and dimension > 0, "positive oracle dimension")
    require(len(first) == len(second) == dimension*dimension, "oracle matrix extents")
    require(all(type(x) is int for x in (*first, *second)), "oracle integer entries")
    # Deliberately ordinary i,j,k dot products: no quadrants, bilinear
    # identities, recursive formula, or import from the physical kernel.
    return tuple(sum(first[i*dimension+k]*second[k*dimension+j]
                     for k in range(dimension))
                 for i in range(dimension) for j in range(dimension))


def check(first, second, actual, dimension, width, wide):
    require(type(width) is int and width > 0 and type(wide) is int and wide > 0,
            "positive oracle record widths")
    low, high = -(1 << (width-1)), 1 << (width-1)
    require(all(low <= x < high for x in (*first, *second)), "admitted input carrier")
    expected = classical(first, second, dimension)
    require(all(-(1 << (wide-1)) <= x < (1 << (wide-1)) for x in expected),
            "admitted output carrier")
    require(tuple(actual) == expected, "exact classical matrix product mismatch")
    encoded = json.dumps(expected, separators=(",", ":")).encode("ascii")
    return {"dimension": dimension, "width": width, "wide": wide,
            "entries": len(expected), "maximum_absolute_entry": max(map(abs, expected)),
            "exact_output_sha256": sha256(encoded).hexdigest(),
            "oracle": "independent exact integer i,j,k dot sums"}


def fixtures():
    cases = []
    def add(name, n, w, a, b):
        ell = n.bit_length()-1
        require(n == 1 << ell, "dyadic fixture")
        cases.append({"name": name, "dimension": n, "width": w,
                      "wide": 2*w+ell+2, "first": tuple(a), "second": tuple(b)})
    add("singleton_signed_minimum", 1, 2, (-2,), (-2,))
    add("two_noncommuting", 2, 4, (7, -8, 3, -1), (-2, 5, 7, -8))
    add("four_mixed_cancellation", 4, 4,
        (((3*i+5*j+1) % 16)-8 for i in range(4) for j in range(4)),
        (((7*i+2*j+3) % 16)-8 for i in range(4) for j in range(4)))
    add("eight_all_signed_minima", 8, 2, (-2,)*64, (-2,)*64)
    add("singleton_after_large", 1, 1, (-1,), (0,))
    add("eight_mixed_after_short", 8, 3,
        (((7*i+3*j+5) % 8)-4 for i in range(8) for j in range(8)),
        (((5*i+6*j+1) % 8)-4 for i in range(8) for j in range(8)))
    return tuple(cases)


def selfcheck():
    rows = []
    for case in fixtures():
        n, a, b = case["dimension"], case["first"], case["second"]
        exact = classical(a, b, n)
        rows.append(check(a, b, exact, n, case["width"], case["wide"]))
    case = fixtures()[1]
    a, b, n = case["first"], case["second"], case["dimension"]
    expected = classical(a, b, n)
    transposed = tuple(b[j*n+i] for i in range(n) for j in range(n))
    mutants = (classical(b, a, n), classical(a, transposed, n),
               tuple(expected[j*n+i] for i in range(n) for j in range(n)),
               (expected[0]+1, *expected[1:]))
    for value in mutants:
        try:
            check(a, b, value, n, case["width"], case["wide"])
        except ValueError:
            pass
        else:
            raise ValueError("classical oracle accepted a decisive mutant")
    # The all-minimum fixture has a small finished dot product, while the
    # repeatedly summed diagonal operand has magnitude B times its input.
    # Squaring that magnitude reaches the positive limit of the root ABI
    # carrier; using root wide for every intermediate must reject it.
    large = fixtures()[3]
    summed_magnitude = large["dimension"] * (1 << (large["width"]-1))
    oversized = summed_magnitude**2
    require(oversized >= 1 << (large["wide"]-1), "internal guard witness")
    require(max(map(abs, classical(large["first"], large["second"], 8)))
            < 1 << (large["wide"]-1), "finished product still fits")
    return {"cases": rows, "decisive_oracle_mutants": len(mutants),
            "root_carrier_internal_witness": oversized,
            "actual_finished_minimum_fixture_entry": 32}
