"""Adversarial controls on the theorem's scope, not a physical simulator.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as Q

from audit_bounds import caller_bounds, ceil_log2, require, word_bounds


def rejects(call, phrase):
    try:
        call()
    except ValueError as error:
        require(phrase in str(error), "specific control rejection: " + str(error))
        return str(error)
    raise ValueError("negative control unexpectedly accepted: " + phrase)


def controls(word, caller):
    checks = {}
    count = 0
    for a in range(1, 130):
        for b in range(1, 130):
            value = Q(a, b)
            k = ceil_log2(value)
            upper = Q(2) ** k
            require(upper / 2 < value <= upper, "independent exact logarithm bracket")
            count += 1
    checks["exact_logarithm_brackets"] = count
    checks["too_small_S225"] = rejects(lambda: word_bounds(word, 225), "odd clearing fails at event 1101")

    tiny = {"initial": [0, 0], "final": [0, 0], "owned_fields": 0,
            "program": [["ADD", 0, 1, "1/7", 0]]}
    checks["unfunded_prime"] = rejects(lambda: word_bounds(tiny, 1125), "odd clearing fails")
    tiny["program"] = [["ADD", 0, 1, "1", 1]]
    checks["wrong_frame"] = rejects(lambda: word_bounds(tiny), "ADD common frame")
    tiny["program"] = [["COPY", 0, 1, "1", 0]]
    checks["copy_nonzero_public"] = rejects(lambda: word_bounds(tiny), "COPY into owned zero")
    tiny["program"] = [["MOVE", 0, 1, 0, False]]
    checks["wrong_move_source"] = rejects(lambda: word_bounds(tiny), "MOVE source frame")
    tiny["program"] = [["SCALE", 0, "1/3", 0]]
    checks["nondyadic_completed_endpoint"] = rejects(lambda: word_bounds(tiny), "public endpoint dyadic")

    bad = deepcopy(caller)
    entry = next(e for e in bad["events"] if e[0] != "J" and e[1] == "ADD")
    entry[4] = "1/3"
    checks["odd_caller_scalar"] = rejects(lambda: caller_bounds(bad), "caller scalar must be dyadic")
    bad = deepcopy(caller)
    joint = next(e for e in bad["events"] if e[0] == "J")
    joint[2][1] = joint[2][0]
    checks["joint_alias"] = rejects(lambda: caller_bounds(bad), "four distinct A ports")
    bad = deepcopy(caller)
    joint = next(e for e in bad["events"] if e[0] == "J")
    joint[3][3] = "1/3"
    checks["changed_B_endpoint"] = rejects(lambda: caller_bounds(bad), "retained B endpoint")

    # An identity endpoint can still incur one odd division per unfinished
    # context. A single outer scale3 funds depth1 and fails at depth2.
    def once_scaled(depth, initial):
        value = initial
        for _ in range(depth):
            require(value.denominator == 1 and value.numerator % 3 == 0,
                    "nested boundary-only odd remainder")
            value /= 3
        for _ in range(depth):
            value *= 3
        return value

    require(once_scaled(1, Q(3)) == 3, "one-level positive control")
    checks["one_outer_scale_fails_at_depth_two"] = rejects(
        lambda: once_scaled(2, Q(3)), "nested boundary-only odd remainder")

    def per_call(depth, x):
        scaled = 3*x
        require(scaled.denominator == 1 and scaled.numerator % 3 == 0,
                "per-call exact odd division")
        middle = scaled/3
        if depth:
            middle = per_call(depth-1, middle)
        scaled_out = 3*middle
        require(scaled_out.numerator % 3 == 0, "per-call exact return division")
        return scaled_out/3

    for depth in range(21):
        for x in range(-5, 6):
            require(per_call(depth, Q(x)) == x, "per-call scaled nested identity")
    checks["per_call_nested_signed_cases"] = 21*11
    value = Q(1)
    for _ in range(100):
        value = per_call(0, value)
    require(value == 1, "completed siblings preserve entrance debt")
    checks["completed_siblings"] = 100

    # D=1 and P=diag(1,0): (P C P)^3 has (-1+i)/4, exceeding the
    # Clifford denominator cap 2^ceil(D/2). Thus active selection is excluded.
    def cmul(a, b):
        return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
    z = (Q(1), Q(0))
    for _ in range(3):
        z = cmul(z, (Q(1,2), Q(1,2)))
    require(z == (Q(-1,4), Q(1,4)) and max(x.denominator for x in z) > 2,
            "active projection destroys fixed-root Clifford denominator cap")
    checks["active_projector_counterexample"] = [str(x) for x in z]

    # The text proves the quantified inequalities; this detects off-by-one
    # mistakes at finite boundary cases and is not their universal proof.
    samples = 0
    for D in range(1, 2001):
        for t in {0, (D-1)//356}:
            require(356*t < D, "boundary depth sample")
            require((D+1)//2+178*t <= D, "fractional format boundary")
            require((D+2)//2+161*t+1 <= D+2, "magnitude format boundary")
            samples += 1
    checks["format_integer_boundary_samples"] = samples
    checks["universal_proof_from_finite_sweep"] = False
    return checks
