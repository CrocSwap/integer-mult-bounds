#!/usr/bin/env python3
"""Exact certificate for four projection modes and a sharp geometric tail.

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.
Standard library, no network/Git/source imports, no writes, no assert statements.
The universal argument is in PROOF.md; finite tests are labelled separately.
"""

from fractions import Fraction as Q
import json


SEED = (0, 27456, 48576, 68320, 86592)
LIMIT = Q(439277, 149175)  # Petalas #5151, exact pinned theorem in PROOF.md.
COEFFICIENTS = (Q(1), Q(17, 39), Q(6181, 14586), Q(99085, 239811))
MAX_BLOCK = 48


def require(condition, message):
    if not condition:
        raise ValueError(message)


def expect_rejection(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def raw_step(old, k, omit_two_drop=False):
    """Literal integer recurrence, independent of the mode implementation."""
    require(len(old) == k, "wrong old profile length")
    result = []
    for r in range(k + 1):
        value = 0
        if r < k:
            value += (2**(k-r) - 1 + 4**k - 2**(k+r)) * old[r]
        if r >= 1:
            value += (2*(2**k - 2**(k-r))
                      + (2**r - 1)*2**(k-1)) * old[r-1]
        if r >= 2 and not omit_two_drop:
            value += (2**r - 1)*(2**(r-1) - 1)*2**(k-r) * old[r-2]
        result.append(value)
    return result


def diagonal(k, j):
    require(1 <= j <= k, "diagonal domain")
    return (2**(k-j) - 1)*(2**(k+j) + 1)


def h(j):
    return Q(3, 2) + Q(1, 2**j) - 2**j


def mode(j, maximum):
    values = [Q(0)]*j + [Q(1)]
    for r in range(j+1, maximum+1):
        y = 2**r
        b = Q(y+3, 2) - Q(2, y)
        c = Q(y-3, 2) + Q(1, y)
        values.append((b*values[r-1] + c*values[r-2]) / (h(j)-h(r)))
    return values


def reconstruct_seed(modes, coefficients):
    return [sum(coefficients[j-1]*modes[j][r] for j in range(1, 5))
            for r in range(5)]


def alpha(x):
    return Q((x-1)*(x+4), (x-2)*(2*x+1))


def beta(x, eigenvalue):
    return Q(x-1, 2*x+1) * (1 + Q(2*x, (x-4)*(x+1))*eigenvalue)


def transfer(x, eigenvalue):
    b = beta(x, eigenvalue)
    f = x*(alpha(x)+b-1)
    return ((1+f/x, -2*b/x), (f, -2*b))


def involution(eigenvalue):
    return ((Q(1), Q(0)), (eigenvalue+Q(3, 2), Q(-1)))


def matrix_product(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def matrix_difference(a, b):
    return tuple(tuple(a[i][j]-b[i][j] for j in range(2)) for i in range(2))


def matrix_norm(a):
    return max(sum(abs(value) for value in row) for row in a)


def matrix_vector(a, v):
    return tuple(sum(a[i][j]*v[j] for j in range(2)) for i in range(2))


IDENTITY = ((Q(1), Q(0)), (Q(0), Q(1)))


# Bivariate polynomial arithmetic; keys are powers of (x,h). This checks the
# displayed identity as a polynomial identity, not merely at sampled points.
def poly_add(*polynomials):
    result = {}
    for p in polynomials:
        for powers, value in p.items():
            result[powers] = result.get(powers, Q(0)) + value
    return {powers: value for powers, value in result.items() if value}


def poly_scale(p, scalar):
    return {powers: value*scalar for powers, value in p.items() if value*scalar}


def poly_mul(*polynomials):
    result = {(0, 0): Q(1)}
    for p in polynomials:
        new = {}
        for (i, j), a in result.items():
            for (k, ell), b in p.items():
                key = (i+k, j+ell)
                new[key] = new.get(key, Q(0)) + a*b
        result = {powers: value for powers, value in new.items() if value}
    return result


def check_symbolic_identity():
    one = {(0, 0): Q(1)}
    x = {(1, 0): Q(1)}
    hp = {(0, 1): Q(1)}

    def shifted(a, b):
        return poly_add(poly_scale(x, a), poly_scale(one, b))

    an = poly_mul(shifted(1, -1), shifted(1, 4))
    ad = poly_mul(shifted(1, -2), shifted(2, 1))
    bn = poly_mul(shifted(1, -1), poly_add(
        poly_mul(shifted(1, -4), shifted(1, 1)), poly_scale(poly_mul(x, hp), 2)))
    bd = poly_mul(shifted(2, 1), shifted(1, -4), shifted(1, 1))
    fn = poly_mul(x, poly_add(poly_mul(an, bd), poly_mul(bn, ad),
                             poly_scale(poly_mul(ad, bd), -1)))
    fd = poly_mul(ad, bd)
    difference_numerator = poly_add(fn, poly_scale(poly_mul(
        poly_add(hp, poly_scale(one, Q(3, 2))), fd), -1))
    displayed_numerator = {
        (3, 1): Q(6), (3, 0): Q(9), (2, 1): Q(10), (2, 0): Q(-21),
        (1, 1): Q(-36), (1, 0): Q(-54), (0, 1): Q(-16), (0, 0): Q(-24)}
    displayed_denominator = poly_scale(poly_mul(
        shifted(1, -4), shifted(1, -2), shifted(1, 1), shifted(2, 1)), 2)
    require(poly_mul(difference_numerator, displayed_denominator)
            == poly_mul(displayed_numerator, fd), "F remainder polynomial identity")
    require(Q(3, 2)+30*Q(16, 15) < 40, "beta remainder constant")
    require(99+Q(171, 64)+Q(594, 64**2)+Q(264, 64**3) < 104,
            "numerator majorant")
    require(4*Q(15, 16)*Q(31, 32) > 3, "denominator minorant")
    require(Q(104, 3) < 64, "F remainder constant")
    require(16*128+64*16+Q(8192, 64) <= 4096, "two-step constant")


def check_uniform_fixture(x, eigenvalue, remainder_constant=128):
    require(x >= 64 and -15 <= eigenvalue <= 0, "uniform lemma domain")
    j = involution(eigenvalue)
    a = transfer(x, eigenvalue)
    require(matrix_product(j, j) == IDENTITY, "J squared")
    require(matrix_norm(j) <= 16, "J norm")
    require(matrix_norm(matrix_difference(a, j)) <= Q(remainder_constant, x),
            "one-step perturbation bound")
    require(matrix_norm(matrix_difference(matrix_product(
        transfer(2*x, eigenvalue), a), IDENTITY)) <= Q(4096, x),
        "two-step perturbation bound")


def tail_enclosure(u, coefficients, start):
    require(start >= 5, "two-step domain")
    s = Q(8192, 3*2**start)
    require(s < 1, "summable product bound needs S < 1")
    center, radius = Q(0), Q(0)
    for j in range(1, 5):
        z = 2**start*(u[j][start]-u[j][start-1])
        norm = max(abs(u[j][start]), abs(z))
        center += coefficients[j-1]*z
        radius += abs(coefficients[j-1])*s/(1-s)*norm
    return center, radius


def certify_interval(center, radius, low, high):
    require(radius >= 0 and low < center-radius and center+radius < high,
            "tail interval not certified")


def check_error(top, m, limit=LIMIT):
    require(Q(1, 2**m) < top-limit < Q(2, 2**m), "geometric error enclosure")


def main():
    check_symbolic_identity()
    inherited_limit = Q(11, 10)*(30 + 280*Q(SEED[2], SEED[1])
                               + 960*Q(SEED[3], SEED[1])
                               + 1024*Q(SEED[4], SEED[1]))/2295
    require(inherited_limit == LIMIT, "cited limit specialization")
    modes = {j: mode(j, MAX_BLOCK) for j in range(1, 5)}
    require(all(c > 0 for c in COEFFICIENTS), "positive seed coefficients")
    expected_seed = [Q(a, SEED[1]) for a in SEED]
    require(reconstruct_seed(modes, COEFFICIENTS) == expected_seed, "seed decomposition")

    raw = list(SEED)
    products = {j: Q(1) for j in range(1, 5)}
    u = {j: {} for j in range(1, 5)}
    tops = {}
    profile_checks = 0
    scalar_checks = 0
    matrix_checks = 0
    for m in range(4, MAX_BLOCK+1):
        if m > 4:
            old_one = raw[1]
            raw = raw_step(raw, m)
            require(raw[1] == old_one*diagonal(m, 1), "denominator identity")
            for j in products:
                require(diagonal(m, j) == diagonal(m, 1)+2**m*h(j),
                        "raw eigenvalue identity")
                products[j] *= Q(diagonal(m, j), diagonal(m, 1))
        for r in range(m+1):
            reconstructed = sum(COEFFICIENTS[j-1]*products[j]*modes[j][r]
                                for j in range(1, 5))
            require(reconstructed == Q(raw[r], raw[1]), "full profile identity")
            profile_checks += 1
        tops[m] = Q(raw[-1], raw[1])
        for j in products:
            u[j][m] = products[j]*modes[j][m]
            if m >= 6:
                require(u[j][m] == alpha(2**m)*u[j][m-1]
                        + beta(2**m, h(j))*u[j][m-2], "scalar mode recurrence")
                scalar_checks += 1
                before = (u[j][m-1], 2**(m-1)*(u[j][m-1]-u[j][m-2]))
                after = (u[j][m], 2**m*(u[j][m]-u[j][m-1]))
                require(matrix_vector(transfer(2**m, h(j)), before) == after,
                        "scaled state transfer")
                matrix_checks += 1
        if m > 4:
            require(tops[m] < tops[m-1], "finite-prefix strict decrease")
            check_error(tops[m], m)
    require([tops[k] for k in (4, 5, 6)]
            == [Q(41, 13), Q(834241, 278850), Q(1188222, 399685)], "calibrations")

    tail_rows = []
    for start, coarse_center, radius_bound, interval in (
            (32, (Q(-858261, 10**6), Q(-858260, 10**6)), Q(3, 10**6),
             (Q(-9, 10), Q(-4, 5))),
            (33, (Q(-1873709, 10**6), Q(-1873708, 10**6)), Q(2, 10**6),
             (Q(-2), Q(-9, 5)))):
        center, radius = tail_enclosure(u, COEFFICIENTS, start)
        require(coarse_center[0] < center < coarse_center[1], "checkpoint center")
        require(radius < radius_bound, "checkpoint radius")
        certify_interval(center, radius, *interval)
        tail_rows.append({"start": start, "center_interval": list(map(str, coarse_center)),
                          "radius_less_than": str(radius_bound),
                          "all_same_parity_scaled_differences": list(map(str, interval))})
    require(Q(2, 3)*Q(9, 5)+Q(1, 3)*Q(4, 5) == Q(22, 15) > 1,
            "even lower error")
    require(Q(2, 3)*2+Q(1, 3)*Q(9, 10) == Q(49, 30) < 2, "even upper error")
    require(Q(2, 3)*Q(4, 5)+Q(1, 3)*Q(9, 5) == Q(17, 15) > 1,
            "odd lower error")
    require(Q(2, 3)*Q(9, 10)+Q(1, 3)*2 == Q(19, 15) < 2, "odd upper error")

    # Corroboration of (3.1), separate from the uniform written proof.
    fixture_count = 0
    for eigenvalue in [Q(-15), Q(0), Q(-1, 2)] + [h(j) for j in range(1, 5)]:
        for x in [64, 65, 127, 128, 1024, 2**32, 2**64]:
            check_uniform_fixture(x, eigenvalue)
            fixture_count += 1

    controls = []

    def reject(label, operation):
        expect_rejection(operation)
        controls.append(label)

    reject("omit distance-two term", lambda: require(
        Q(raw_step(list(SEED), 5, True)[-1], raw_step(list(SEED), 5, True)[1])
        == tops[5], "wrong recurrence"))
    altered = list(COEFFICIENTS)
    altered[-1] += Q(1, 1000)
    reject("perturb fourth mode coefficient", lambda: require(
        reconstruct_seed(modes, altered) == expected_seed, "wrong seed"))
    reject("domain x below 64", lambda: check_uniform_fixture(63, h(4)))
    reject("eigenvalue outside uniform domain", lambda: check_uniform_fixture(64, Q(-16)))
    reject("understate matrix perturbation", lambda: check_uniform_fixture(64, h(4), 1))
    wrong_j = ((Q(1), Q(0)), (h(4)+Q(3, 2), Q(1)))
    reject("lose involution sign", lambda: require(
        matrix_product(wrong_j, wrong_j) == IDENTITY, "wrong involution"))
    reject("tail product without S less than one", lambda: tail_enclosure(u, COEFFICIENTS, 5))
    odd_center, odd_radius = tail_enclosure(u, COEFFICIENTS, 33)
    reject("apply even interval to odd tail", lambda: certify_interval(
        odd_center, odd_radius, Q(-9, 10), Q(-4, 5)))
    reject("perturb inherited limit", lambda: check_error(tops[33], 33, LIMIT+Q(1, 149175)))
    constant_seed = [0, 1, 1, 1, 1]
    constant_next = raw_step(constant_seed, 5)
    reject("claim all nonnegative seeds decrease", lambda: require(
        Q(constant_next[-1], constant_next[1]) < 1, "constant seed increases"))

    print(json.dumps({
        "status": "PASS_PROJECTION_GEOMETRIC_TAIL",
        "claim_type": "scoped arithmetic proof with exact finite tail certificate",
        "seed": SEED,
        "limit_from_pr5151": str(LIMIT),
        "seed_coefficients": list(map(str, COEFFICIENTS)),
        "full_profile_equalities": profile_checks,
        "scalar_mode_equalities": scalar_checks,
        "scaled_state_equalities": matrix_checks,
        "finite_monotonicity_and_error_blocks": [5, MAX_BLOCK],
        "symbolic_F_remainder_identity": True,
        "uniform_lemma_fixtures": fixture_count,
        "tail_certificates": tail_rows,
        "rejected_controls": controls,
        "unrun": ["hook ranks", "physical/recursive admission", "selected cold replay",
                  "Lean", "independent human review"],
        "new_kappa": False,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
