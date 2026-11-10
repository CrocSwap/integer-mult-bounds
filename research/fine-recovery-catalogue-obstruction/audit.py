"""Exact necessary guards and independent integer recovery controls.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This module does not execute or emulate the retained physical runtime.
"""
from fractions import Fraction
from itertools import product


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_log2(x):
    need(isinstance(x, int) and x > 0, "positive integer logarithm")
    return (x - 1).bit_length()


def necessary(q, u, spacing, theta):
    """Only the three named necessary conditions, not full admission."""
    return (4 * spacing * theta > 1 and
            u >= ceil_log2(8 * q) and u * spacing <= q)


def recovery_guard(q, u, dimensions, outer_bits, S, b):
    gamma = dimensions * (2 * u + ceil_log2(32 * q) + 1)
    E = dimensions * q * q + 6 * (1 << outer_bits) + 22 + 2 * dimensions
    numerator = (1 << (2 * b + 5)) * S * S * (3 * E * (1 << gamma) + 2)
    return numerator < (1 << q), gamma, E, numerator


def finite_domain():
    """Exhaust a declared box; compare enumeration with integer projection."""
    tested = feasible = admitted_shapes = 0
    for p0 in range(2, 25):
        theta = Fraction(1, p0 * p0)
        for q in range(1, 97):
            exists = False
            for u in range(1, 17):
                for spacing in range(1, 65):
                    tested += 1
                    # Independent cross-multiplied predicate: no log helper.
                    direct = (4 * spacing > p0 * p0 and
                              8 * q <= (1 << u) and u * spacing <= q)
                    need(direct == necessary(q, u, spacing, theta),
                         "encoded-guard arithmetic versus independent powers")
                    if direct:
                        feasible += 1
                        exists = True
            minimum_u = ceil_log2(8 * q)
            minimum_d = p0 * p0 // 4 + 1
            projected = (minimum_u <= 16 and minimum_d <= 64 and
                         minimum_u * minimum_d <= q)
            need(exists == projected, "exact bounded integer projection")
            if exists:
                admitted_shapes += 1
                # Equivalent to q > (p0^2/4)*log2(2*p0^2), without logs.
                need((1 << (4 * q)) > pow(2 * p0 * p0, p0 * p0),
                     "strict relaxed precision lower bound")
    return {"p0": [2, 24], "q": [1, 96], "u": [1, 16],
            "spacing": [1, 64], "triples_with_p0": tested,
            "necessary_guard_passes": feasible, "feasible_p0_q_pairs": admitted_shapes,
            "untouched": "Outside this finite box; universal scope is proved in PROOF.md."}


def large_parameters():
    cases = 0
    # Source-alpha upper bound u < (5/4)(k+4), for p0=2^k.
    # We intentionally keep the weaker floor upper bound, still sufficient.
    for k in range(200, 1001):
        p0 = 1 << k
        upper_u = 5 * (k + 4) // 4
        lower_q = p0 * p0 // 4 + 1
        upper_q = (1 << upper_u) // 8
        need(lower_q > upper_q, "no precision between necessary endpoints")
        need(pow(p0, 3) > (1 << 16), "strict power separation")
        cases += 1
    need(sum(Fraction(3, 4) ** j / factorial(j) for j in range(4)) > 2,
         "positive-series certificate for ln2<3/4")
    return {"dyadic_k": [200, 1000], "cases": cases,
            "actual_alpha_computation": False,
            "scope": "Exact checks of proved sufficient endpoint bounds, not a numerical alpha oracle."}


def factorial(n):
    result = 1
    for j in range(2, n + 1):
        result *= j
    return result


def guard_controls():
    names = []
    def record(name, correct, mutant):
        need(correct != mutant, "distinguishing control: " + name)
        names.append(name)
    d, q, u = 4, 64, 16
    theta = Fraction(1, 4 * d)
    record("strict_lower_ratio", necessary(q, u, d, theta),
           4 * d * theta >= 1 and u >= ceil_log2(8 * q) and u * d <= q)
    q, u, d, theta = 64, 1, 16, Fraction(1, 16)
    record("concentration_required", necessary(q, u, d, theta),
           4 * d * theta > 1 and u * d <= q)
    q, u, d, theta = 64, 16, 16, Fraction(1, 16)
    record("similarity_required", necessary(q, u, d, theta),
           4 * d * theta > 1 and u >= ceil_log2(8 * q))
    q, u, d, theta = 128, 16, 100, Fraction(1, 100)
    record("external_not_private_width", necessary(q, u, d, theta),
           4 * d * theta > 1 and u >= ceil_log2(8 * q) and u * d <= 32768 * q)
    # e/s and e/t differ at a strict boundary; the source uses e/s.
    s, t, d = 31, 33, 4
    record("original_source_theta_denominator", 4 * d * Fraction(t - s, s) > 1,
           4 * d * Fraction(t - s, t) > 1)
    # A fully specified arithmetic descriptor, not a produced catalogue.
    p0, q, u, D, A, b = 384, 1024, 16, 2, 20, 64
    sides = [(1 << 20) - 3, (1 << 20) - 5]
    thetas = [Fraction((1 << 20) - s, s) for s in sides]
    need(all(Fraction(1, 4 * p0 * p0) <= theta <= Fraction(1, p0 * p0)
             for theta in thetas), "descriptor fine theta interval")
    S = sides[0] * sides[1]
    passed, gamma, E, numerator = recovery_guard(q, u, D, A, S, b)
    rejected = all(not necessary(q, u, D + 1, theta) for theta in thetas)
    need(passed and rejected, "recovery inequality does not imply catalogue admission")
    names.append("numeric_guard_cannot_waive_catalogue")
    return {"controls": names,
            "separation_descriptor": {"p0": p0, "external_q": q, "u": u,
                "D": D, "d_literal": D + 1, "A": A, "b": b, "sides": sides,
                "S": S, "gamma": gamma, "E": E,
                "guard_numerator_bits": numerator.bit_length(),
                "guard_denominator_bits": q + 1,
                "scalar_guard_passes": passed, "catalogue_necessary_guard_fails": rejected,
                "physical_execution": False,
                "full_fine_family_or_production_instance": False}}


def truncate_fraction(x, q):
    scale = 1 << q
    numerator = abs(x.numerator) * scale // x.denominator
    return Fraction(numerator if x >= 0 else -numerator, scale)


def nearest(x):
    # These controls enforce strict half-distance; tie convention is immaterial.
    if x < 0:
        return -nearest(-x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def convolution(a, b):
    n = len(a)
    return [sum(a[k] * b[(j - k) % n] for k in range(n)) for j in range(n)]


def recovery_controls():
    S, b, q, gamma = 15, 4, 56, 3
    # Original axes 3,5; P0=1,P1=3, so the retained exponent map is (k,2k).
    address = lambda k: (k % 3, (2 * k) % 5)
    need(len({address(k) for k in range(S)}) == S, "CRT bijection")
    for j, k in product(range(S), repeat=2):
        left = address(j + k)
        right = ((address(j)[0] + address(k)[0]) % 3,
                 (address(j)[1] + address(k)[1]) % 5)
        need(left == right, "CRT exponent homomorphism")
    cases = values = 0
    controls = set()
    input_pairs = [([11, 5, 7, 2], [9, 4, 3, 1]),
                   ([15, 15, 15, 15], [15, 0, 15, 15]),
                   ([1, 0, 0, 0], [1, 0, 0, 0]),
                   ([0, 0, 0, 0], [15, 15, 15, 15])]
    for digits_a, digits_b in input_pairs:
        a, bvec = digits_a + [0] * (S - len(digits_a)), digits_b + [0] * (S - len(digits_b))
        c = convolution(a, bvec)
        tensor_a = {address(k): a[k] for k in range(S)}
        tensor_b = {address(k): bvec[k] for k in range(S)}
        for j in range(S):
            x, y = address(j)
            tensor_sum = sum(tensor_a[(i, l)] * tensor_b[((x - i) % 3, (y - l) % 5)]
                             for i in range(3) for l in range(5))
            need(tensor_sum == c[j], "ordinary versus tensor cyclic convolution")
        scale = S * S * (1 << (2 * b + 4))
        output = [Fraction(x, scale) for x in c]
        grid = [truncate_fraction(x, q) for x in output]
        recovered = [nearest(x * scale) for x in grid]
        need(recovered == c, "two-S exact scale and nearest")
        need(Fraction(scale, 1 << q) < Fraction(1, 2), "strict grid recovery margin")
        if any(c):
            mutants = {
                "omit_one_source_S": [nearest(x * S * (1 << (2 * b + 4))) for x in grid],
                "omit_both_source_S": [nearest(x * (1 << (2 * b + 4))) for x in grid],
                "substitute_padded_T_squared": [nearest(x * 32 * 32 * (1 << (2 * b + 4))) for x in grid],
                # Three linear maps: two forwards and one opposite. Omitting
                # each map's restoration scales the ideal answer by 2^-3gamma.
                "omit_per_transform_gamma": [nearest(x * scale / (1 << (3 * gamma))) for x in grid],
                "restore_only_once_after_three_maps": [nearest(x * scale / (1 << (2 * gamma))) for x in grid],
                "double_restore_completed_maps": [nearest(x * scale * (1 << (3 * gamma))) for x in grid],
            }
            for name, wrong in mutants.items():
                need(wrong != c, "nonzero recovery scale discriminator: " + name)
                controls.add(name)
        # Exact radix carry: no wrap because 2*4-1<=15.
        carry = value = 0
        for j, coefficient in enumerate(recovered):
            total = carry + coefficient
            digit = total % (1 << b)
            carry = total // (1 << b)
            value += digit << (b * j)
        need(carry == 0, "terminal carry")
        left = sum(x << (b * j) for j, x in enumerate(digits_a))
        right = sum(x << (b * j) for j, x in enumerate(digits_b))
        need(value == left * right, "integer product versus convolution and carry")
        values += S
        cases += 1
    # The half-tie itself lies outside the strict guarantee.
    need(nearest(Fraction(7, 2)) != 3, "strict half-threshold cannot be weakened")
    controls.add("strict_half_integer_margin")
    return {"original_axes": [3, 5], "S": S, "padded_T_control": 32,
            "radix_bits": b, "external_q": q, "gamma_control": gamma,
            "input_pairs": cases, "coefficients": values, "CRT_addition_pairs": S * S,
            "controls": sorted(controls), "physical_or_Fourier_execution": False}
