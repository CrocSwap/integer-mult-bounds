"""Separate finite coordinate/permutation replay of the compiler's words.

This module does not use the compiler's ADDRESS evaluator or Laurent code.
The expected endpoint comes from the direct s*r^T coordinate formula.
Full-domain coverage is finite evidence, not an implementation on tape.
"""
import hashlib
import itertools
import json
from fractions import Fraction


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def direct_push(address, exponent, modulus):
    d = address[0] - address[2] - address[3] + address[5]
    step = exponent * pow(4, -1, modulus) * d
    result = list(address)
    for i, sign in ((0, 1), (2, 1), (3, -1), (5, -1)):
        result[i] = (address[i] + sign * step) % modulus
    return tuple(result)


def literal_push(address, word, modulus):
    state = list(address)
    for event in word:
        if event[0] == "child":
            state[event[1]], state[event[2]] = state[event[2]], state[event[1]]
        else:
            _, target, diagonal, controls = event
            check(all(source < target for source, _ in controls), "physical control order")

            def scalar(c):
                c = Fraction(c)
                return c.numerator * pow(c.denominator, -1, modulus) % modulus

            check(scalar(diagonal) != 0, "nonzero dyadic diagonal")
            value = scalar(diagonal) * state[target]
            for source, coefficient in controls:
                value += scalar(coefficient) * state[source]
            state[target] = value % modulus
    return tuple(state)


def receipt_update(digest, value):
    digest.update((json.dumps(value, separators=(",", ":")) + "\n").encode())


def case(compiler, domain, modulus, j, sign, digest):
    index = {address: i for i, address in enumerate(domain)}
    baseline = compiler.baseline_program(j, sign)
    fused = compiler.fused_program(j, sign)
    inverse = compiler.inverse_program(fused)
    exponents = sorted({event[2] for word in (baseline, fused, inverse)
                        for event in word if event[0] == "query"})
    permutations = {}
    address_cases = 0
    for k in exponents:
        word = compiler.address_word(k)
        images = []
        for address in domain:
            actual = literal_push(address, word, modulus)
            expected = direct_push(address, k, modulus)
            check(actual == expected, "full-domain literal ADDRESS lowering")
            check(actual in index, "domain closure")
            images.append(index[actual])
            address_cases += 1
        check(sorted(images) == list(range(len(domain))), "complete ADDRESS bijection")
        permutations[k] = tuple(images)
    a = sign * (1 << j)
    expected_plus = [index[direct_push(z, a, modulus)] for z in domain]
    expected_minus = [index[direct_push(z, -a, modulus)] for z in domain]
    columns = 0
    for role in range(4):
        for position in range(len(domain)):
            initial = [set() for _ in range(4)]
            initial[role].add(position)
            expected = [row.copy() for row in initial]
            if role == 1:
                expected[0].symmetric_difference_update({expected_plus[position]})
                expected[0].symmetric_difference_update({expected_minus[position]})
            actual = [row.copy() for row in initial]
            old = [row.copy() for row in initial]
            compiler.run_bits(actual, fused, permutations)
            compiler.run_bits(old, baseline, permutations)
            check(actual == expected and old == expected, "complete dirty BIT column")
            receipt_update(digest, [modulus, j, sign, role, position,
                                    [sorted(row) for row in actual]])
            compiler.run_bits(actual, inverse, permutations)
            check(actual == initial, "literal inverse restores dirty BIT column")
            compiler.run_bits(old, fused, permutations)
            check(old == initial, "completed DATA involution")
            columns += 1
    # Simultaneous nonzero dirt in all four roles, with no clean private promise.
    initial = [{i for i in range(len(domain)) if (53 * i + 17 * role + 54) % 7 < 3}
               for role in range(4)]
    expected = [row.copy() for row in initial]
    for position in initial[1]:
        expected[0].symmetric_difference_update({expected_plus[position]})
        expected[0].symmetric_difference_update({expected_minus[position]})
    actual = [row.copy() for row in initial]
    compiler.run_bits(actual, fused, permutations)
    check(actual == expected, "simultaneously dirty full rows")
    compiler.run_bits(actual, inverse, permutations)
    check(actual == initial, "simultaneously dirty restoration")
    return address_cases, columns


def evidence(compiler):
    digest = hashlib.sha256()
    full_address = full_columns = full_cases = 0
    full_domains = []
    for modulus, parameters in ((3, [(j, sign) for j in (0, 1, 2, 5, 54)
                                    for sign in (-1, 1)]),
                                (5, [(0, 1), (54, 1)])):
        domain = [tuple(z) + (1, 2) for z in itertools.product(range(modulus), repeat=6)]
        fixed = sum(direct_push(z, 1, modulus) == z for z in domain)
        full_domains.append({"modulus": modulus, "six_field_addresses": len(domain),
                             "fixed_addresses": fixed, "two_spectator_values": [1, 2],
                             "j_sign_parameters": parameters})
        for j, sign in parameters:
            address, columns = case(compiler, domain, modulus, j, sign, digest)
            full_address += address
            full_columns += columns
            full_cases += 1
    orbit_address = orbit_columns = orbit_cases = 0
    lengths = []
    # Include full-order, nonunit shorter, and fixed orbits in odd prime powers.
    for modulus, scale in ((5, 1), (25, 1), (25, 5), (49, 1), (49, 7),
                           (121, 1), (121, 11), (27, 3), (9, 3), (11, 0)):
        start = (scale, 0, 0, 0, 0, 0, 7 % modulus, 8 % modulus)
        orbit = [start]
        image = direct_push(start, 1, modulus)
        while image != start:
            check(image not in orbit and len(orbit) < modulus, "orbit stopping rule")
            orbit.append(image)
            image = direct_push(image, 1, modulus)
        lengths.append([modulus, scale, len(orbit)])
        for j in (0, 1, 5, 54):
            for sign in (-1, 1):
                address, columns = case(compiler, orbit, modulus, j, sign, digest)
                orbit_address += address
                orbit_columns += columns
                orbit_cases += 1
    return {"full_domains": full_domains,
            "full_parameter_cases": full_cases,
            "full_address_query_cases": full_address,
            "full_dirty_basis_columns_per_program": full_columns,
            "full_inverse_and_involution_columns": 2 * full_columns,
            "orbit_modulus_scale_lengths": lengths,
            "orbit_parameter_cases": orbit_cases,
            "orbit_address_query_cases": orbit_address,
            "orbit_dirty_basis_columns_per_program": orbit_columns,
            "orbit_inverse_and_involution_columns": 2 * orbit_columns,
            "simultaneously_dirty_cases": full_cases + orbit_cases,
            "endpoint_stream_encoding": "canonical-json-lines-v1",
            "endpoint_stream_sha256": digest.hexdigest()}
