#!/usr/bin/env python3
"""Bounded exact checks. Standard library, read-only, no random search."""
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from math import factorial, gcd, isqrt, lcm, prod
import json

def need(condition, message):
    if not condition:
        raise RuntimeError(message)

def partitions(total, least=1):
    if total == 0:
        yield ()
    for first in range(least, total + 1):
        for rest in partitions(total - first, first):
            yield (first,) + rest

def encode(word, n):
    value = 0
    for digit in word:
        value = n * value + digit
    return value

def coordinate_action(n, lengths, signs=None):
    """Literal block rotations, with an optional reflection on each wrap."""
    signs = tuple(signs) if signs is not None else (0,) * len(lengths)
    need(len(signs) == len(lengths), "one sign per coordinate cycle required")
    result = []
    for word in product(range(n), repeat=sum(lengths)):
        target = list(word)
        start = 0
        for length, sign in zip(lengths, signs):
            for offset in range(length):
                digit = word[start + (offset + 1) % length]
                target[start + offset] = n - 1 - digit if sign and offset == length - 1 else digit
            start += length
        result.append(encode(target, n))
    need(sorted(result) == list(range(n ** sum(lengths))), "nonbijective action")
    return tuple(result)

def direct_cycles(action):
    unseen, histogram = set(range(len(action))), Counter()
    while unseen:
        first = current = min(unseen)
        length = 0
        while current in unseen:
            unseen.remove(current)
            current = action[current]
            length += 1
        need(current == first, "orbit did not return to its own start")
        histogram[length] += 1
    return sum(histogram.values()), dict(sorted(histogram.items()))

def burnside(n, lengths, signs=None):
    signs = tuple(signs) if signs is not None else (0,) * len(lengths)
    order = lcm(*(length * (2 if sign else 1) for length, sign in zip(lengths, signs)))
    fixed_total = 0
    for k in range(order):
        fixed = 1
        for length, sign in zip(lengths, signs):
            cycles = gcd(length, k)
            twisted = sign and ((k // cycles) % 2)
            labels = n % 2 if twisted else n
            fixed *= labels ** cycles
        fixed_total += fixed
    need(fixed_total % order == 0, "nonintegral Burnside average")
    return fixed_total // order, order

def prime_power(length):
    for p in range(2, isqrt(length) + 1):
        if length % p == 0:
            remaining, exponent = length, 0
            while remaining % p == 0:
                remaining //= p
                exponent += 1
            need(remaining == 1, "not one prime power")
            return p, exponent
    need(length >= 2, "prime power below two")
    return length, 1

def block_cycles(n, length):
    p, exponent = prime_power(length)
    total, power = n ** length, 1
    for _ in range(exponent):
        previous = power
        power *= p
        total += (power - previous) * n ** (length // power)
    need(total % length == 0, "nonintegral divisor formula")
    return total // length

def product_cycles(n, d, lengths):
    primes = [prime_power(length)[0] for length in lengths]
    need(len(set(primes)) == len(primes), "noncoprime prime-power blocks")
    need(sum(lengths) <= d, "coordinate budget exceeded")
    return n ** (d - sum(lengths)) * prod(block_cycles(n, length) for length in lengths)

def landau_table(limit):
    primes = [p for p in range(2, limit + 1)
              if all(p % divisor for divisor in range(2, isqrt(p) + 1))]
    table = [(1, ()) for _ in range(limit + 1)]
    for p in primes:
        old, powers, power = table, [], p
        table = old.copy()
        while power <= limit:
            powers.append(power)
            power *= p
        for capacity in range(limit + 1):
            for power in powers:
                if power > capacity:
                    break
                candidate = old[capacity - power][0] * power
                if candidate > table[capacity][0]:
                    table[capacity] = candidate, old[capacity - power][1] + (power,)
    return table

def predicted_automorphisms(n, d, signed):
    vertices, images = list(product(range(n), repeat=d)), set()
    for permutation in permutations(range(d)):
        for signs in product(range(2) if signed else range(1), repeat=d):
            image = []
            for x in vertices:
                y = [n - 1 - x[permutation[i]] if signs[i] else x[permutation[i]]
                     for i in range(d)]
                image.append(encode(y, n))
            images.add(tuple(image))
    return images

def exponent_matrix(n, d, shifted):
    """Exact base-2 exponents for q=1/2,v=1 or2; no logs evaluated."""
    vertices = list(product(range(n), repeat=d))
    return tuple(tuple(-sum((a - b) ** 2 for a, b in zip(x, y))
                       + (sum(x) - sum(y) if shifted else 0)
                       for y in vertices) for x in vertices)

def preserves(matrix, permutation):
    return all(matrix[permutation[i]][permutation[j]] == matrix[i][j]
               for i in range(len(matrix)) for j in range(len(matrix)))

def gaussian(n, d, q, v):
    vertices = list(product(range(n), repeat=d))
    return tuple(tuple(q ** sum((a - b) ** 2 for a, b in zip(x, y))
                       * v ** (sum(x) - sum(y)) for y in vertices) for x in vertices)

def dyadic_round(value, bits):
    scaled = value * (1 << bits)
    rounded = (2 * scaled.numerator + scaled.denominator) // (2 * scaled.denominator)
    return Fraction(rounded, 1 << bits)

def main():
    table = landau_table(256)
    partition_cases = 0
    for d in range(1, 25):
        orders = []
        for lengths in partitions(d):
            orders.append(lcm(*lengths))
            partition_cases += 1
        need(max(orders) == table[d][0], "partition/prime-power maxima disagree")
    unsigned_cases = signed_cases = 0
    for n, maximum in ((2, 10), (3, 6), (4, 4)):
        for d in range(1, maximum + 1):
            for lengths in partitions(d):
                actual, histogram = direct_cycles(coordinate_action(n, lengths))
                average, order = burnside(n, lengths)
                need(actual == average, "unsigned direct/Burnside mismatch")
                need(sum(r * count for r, count in histogram.items()) == n ** d,
                     "unsigned orbit coverage")
                need(order <= table[d][0] and actual * table[d][0] >= n ** d,
                     "unsigned order/orbit lower bound")
                unsigned_cases += 1
    for n in (2, 3):
        for d in range(1, 7):
            for lengths in partitions(d):
                for signs in product(range(2), repeat=len(lengths)):
                    actual, histogram = direct_cycles(coordinate_action(n, lengths, signs))
                    average, order = burnside(n, lengths, signs)
                    need(actual == average, "signed direct/Burnside mismatch")
                    need(order <= 2 * table[d][0] and 2 * actual * table[d][0] >= n ** d,
                         "signed order/orbit lower bound")
                    need(lcm(*histogram) == order, "signed faithful action order")
                    signed_cases += 1
    construction_cases = 0
    for d in range(1, 257):
        order, lengths = table[d]
        need(prod(lengths) == order and sum(lengths) <= d, "DP witness invalid")
        for n in (2, 3, 5):
            cycles = product_cycles(n, d, lengths)
            ratio = Fraction(cycles * order, n ** d)
            need(1 <= ratio < 4, "absolute cycle correction failed")
            if d <= 10 and n == 2:
                literal, _ = direct_cycles(coordinate_action(n, lengths + (1,) * (d - sum(lengths))))
                need(literal == cycles, "maximum-order product/direct mismatch")
            construction_cases += 1
    correction_cases = 0
    for length in range(2, 1025):
        try:
            p, _ = prime_power(length)
        except RuntimeError:
            continue
        for n in (2, 3, 7):
            correction = Fraction(length * block_cycles(n, length), n ** length)
            prime_bound = 1 + Fraction(p - 1, n ** (p - 1))
            need(1 <= correction <= prime_bound, "prime-power correction lemma failed")
            if length <= 16:
                average, _ = burnside(n, (length,))
                need(average == block_cycles(n, length), "divisor/Burnside block mismatch")
            correction_cases += 1
    automorphism_cases = []
    for n, d in ((2, 2), (2, 3), (3, 1), (3, 2)):
        for shifted in (False, True):
            matrix = exponent_matrix(n, d, shifted)
            found = {p for p in permutations(range(n ** d)) if preserves(matrix, p)}
            expected = predicted_automorphisms(n, d, not shifted)
            need(found == expected, "complete finite automorphism classification failed")
            automorphism_cases.append({"n": n, "d": d, "v": 2 if shifted else 1,
                "tested_vertex_permutations": factorial(n ** d), "automorphisms": len(found)})
    controls = []
    c23, _ = direct_cycles(coordinate_action(2, (2, 3)))
    c5, _ = direct_cycles(coordinate_action(2, (5,)))
    need(table[5][0] == 6 and c23 == 12 and c5 == 8,
         "finite maximal-order/minimum-cycle counterexample changed")
    controls.append({"name": "maximal_order_need_not_minimize_cycles", "d": 5,
                     "g": 6, "cycles_2_plus_3": c23, "cycles_5": c5})
    cnegative, _ = direct_cycles(coordinate_action(2, (2,), (1,)))
    need(cnegative == 1 and cnegative * table[2][0] < 4,
         "missing signed factor-two control failed")
    controls.append({"name": "unshifted_lower_bound_needs_factor_two", "cycles": cnegative})
    c22, _ = direct_cycles(coordinate_action(2, (2, 2)))
    false_product = block_cycles(2, 2) ** 2
    need(c22 == 10 and false_product == 9, "repeated-prime negative control")
    try:
        product_cycles(2, 4, (2, 2))
    except RuntimeError:
        pass
    else:
        raise RuntimeError("repeated-prime domain check failed open")
    controls.append({"name": "repeated_prime_product_fails", "actual": c22, "false": false_product})
    composite, _ = burnside(2, (6,))
    false_prime = Fraction(2 ** 6 + 5 * 2, 6)
    need(composite != false_prime, "composite-as-prime control")
    controls.append({"name": "composite_is_not_prime", "actual": composite,
                     "false_numerator": false_prime.numerator, "false_denominator": false_prime.denominator})
    need(Fraction(3, 4) > Fraction(1, 2) and
         Fraction(4 * block_cycles(2, 4), 2 ** 4) == Fraction(3, 2),
         "special four-cycle needs its exact count")
    controls.append({"name": "crude_four_cycle_bound_is_too_large", "exact_correction": "3/2"})
    arbitrary = list(range(8))
    arbitrary[0], arbitrary[1] = arbitrary[1], arbitrary[0]
    need(not preserves(exponent_matrix(2, 3, False), arbitrary), "nonisometry accepted")
    need(preserves(tuple((1,) * 8 for _ in range(8)), arbitrary), "constant-kernel control")
    controls.append({"name": "q_equals_one_has_additional_symmetries"})
    flip = coordinate_action(2, (1, 1), (1, 0))
    need(preserves(exponent_matrix(2, 2, False), flip) and
         not preserves(exponent_matrix(2, 2, True), flip), "shift reversal control")
    controls.append({"name": "nontrivial_shift_excludes_reversal"})
    qnear = Fraction(1023, 1024)
    coarse = tuple(tuple(dyadic_round(value, 0) for value in row)
                   for row in gaussian(2, 3, qnear, Fraction(1)))
    need(all(value == 1 for row in coarse for value in row) and
         preserves(coarse, arbitrary), "coarse rounding did not add symmetry")
    controls.append({"name": "nearest_integer_rounding_can_add_symmetries", "q": "1023/1024"})
    vertices = list(product(range(2), repeat=2))
    heterogeneous = [[prod(Fraction(1, denominator) ** ((x[i] - y[i]) ** 2)
                             for i, denominator in enumerate((2, 3)))
                      for y in vertices] for x in vertices]
    swap = tuple(encode((x[1], x[0]), 2) for x in vertices)
    need(not preserves(heterogeneous, swap), "heterogeneous swap control")
    controls.append({"name": "unequal_coordinate_kernels_break_swap"})
    # Distinct tiny diagonal perturbations leave only the identity symmetry.
    delta = Fraction(1, 1024)
    broken = [list(row) for row in gaussian(2, 5, Fraction(1, 2), Fraction(1))]
    for i in range(32):
        broken[i][i] += delta * Fraction(i + 1, 33)
    need(len({broken[i][i] for i in range(32)}) == 32 and
         2 * delta < Fraction(1, 4) and 32 * table[5][0] > 4 * 32,
         "arbitrary perturbation should not retain constructive upper bound")
    controls.append({"name": "arbitrary_small_perturbations_can_destroy_all_nonidentity_symmetries",
                     "dimension": 5, "cycles": 32, "g": 6})
    rounding_cases = []
    for n, d in ((2, 3), (3, 2)):
        for v in (Fraction(1), Fraction(3, 2)):
            q, delta = Fraction(1, 2), Fraction(1, 128)
            exact = gaussian(n, d, q, v)
            rounded = tuple(tuple(dyadic_round(value, 6) for value in row) for row in exact)
            error = max(abs(rounded[i][j] - exact[i][j])
                        for i in range(n ** d) for j in range(n ** d))
            need(error <= delta, "rounding error envelope failed")
            if v == 1:
                need(2 * delta < q - q ** 2, "unshifted gap not strict")
            else:
                need(q * v <= 1 and q / v <= 1 and
                     4 * delta + 2 * delta ** 2 < q ** 2 - q ** 4 and
                     2 * delta < q * abs(v - 1 / v), "shifted gaps not strict")
            found = {p for p in permutations(range(n ** d)) if preserves(rounded, p)}
            need(found == predicted_automorphisms(n, d, v == 1),
                 "rounded complete symmetry group differs despite strict gaps")
            rounding_cases.append({"n": n, "d": d, "v": str(v), "bits": 6,
                "global_error": str(error), "automorphisms": len(found),
                "tested_vertex_permutations": factorial(n ** d)})
    n, d, q, v = 2, 3, Fraction(1, 2), Fraction(3, 2)
    factor = gaussian(n, 1, q, v)
    rounded_factor = [[dyadic_round(value, 6) for value in row] for row in factor]
    vertices = list(product(range(n), repeat=d))
    rounded_tensor = tuple(tuple(prod(rounded_factor[x[i]][y[i]] for i in range(d))
                                 for y in vertices) for x in vertices)
    exact = gaussian(n, d, q, v)
    epsilon = Fraction(1, 128)
    delta = d * epsilon * (1 + epsilon) ** (d - 1)
    error = max(abs(rounded_tensor[i][j] - exact[i][j]) for i in range(8) for j in range(8))
    need(error <= delta and 4 * delta + 2 * delta ** 2 < q ** 2 - q ** 4 and
         2 * delta < q * abs(v - 1 / v), "factorwise rounding transfer/gaps")
    found = {p for p in permutations(range(8)) if preserves(rounded_tensor, p)}
    need(found == predicted_automorphisms(n, d, False), "factorwise rounded group")
    rounding_cases.append({"n": n, "d": d, "v": str(v), "bits": 6,
        "method": "common factorwise rounding and tensor error transfer",
        "global_error": str(error), "global_error_bound": str(delta), "automorphisms": len(found),
        "tested_vertex_permutations": factorial(8)})
    result = {"status": "PASS", "arithmetic": "exact integers and Fraction; no random search",
        "partition_vs_prime_power_dp": {"dimension_max": 24, "partitions": partition_cases},
        "direct_unsigned_cycle_types": unsigned_cases,
        "direct_signed_cycle_types": signed_cases,
        "maximum_order_constructions": {"dimension_max": 256, "cases": construction_cases},
        "individual_prime_power_corrections": {"length_max": 1024, "cases": correction_cases},
        "complete_small_automorphism_searches": automorphism_cases,
        "complete_rounded_automorphism_searches": rounding_cases,
        "negative_controls": controls,
        "coverage_limits": "Finite domains only. Universal claims are proved in PROOF.md; Landau asymptotic is cited classical input. No rank/runtime/kappa lower bound."}
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
