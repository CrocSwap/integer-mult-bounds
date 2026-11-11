#!/usr/bin/env python3
"""Proof checker for the integral four-odd-c length-6 obstruction.

PROOF.md is the argument. Checks raise, so python -O does not skip them.
The norm-4 scan at the end is a control. It is not the proof.
"""

from fractions import Fraction
from itertools import combinations


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def add(frames):
    rows = tuple(frames)
    return tuple(sum(frame[index] for frame in rows) for index in range(3))


def sub(left, right):
    return tuple(left[index] - right[index] for index in range(3))


def scale(factor, frame):
    return tuple(factor * value for value in frame)


A = (1, 0, 0)
B = (0, 1, 0)
P = (0, 0, 1)
Q = (1, 1, -1)
TWO_A = (2, 0, 0)
TWO_B = (0, 2, 0)
TWO_P = (0, 0, 2)
TWO_Q = (2, 2, -2)
FOUR = (4, 4, 0)
TWO_I = (2, 2, 0)
TARGETS = {
    "AP": (1, 0, 1),
    "AQ": (2, 1, -1),
    "BP": (0, 1, 1),
    "BQ": (1, 2, -1),
}
PROJECTORS = {"A": A, "B": B, "P": P, "Q": Q}


def twice_det(frame):
    a, b, c = frame
    return 2 * a * b + c * (a + b)


def rank_one_nonzero(frame):
    return frame != (0, 0, 0) and twice_det(frame) == 0


def odd(value):
    return value % 2 != 0


def odd_c(frame):
    return odd(frame[2])


def even_sum_ab(frame):
    return not odd(frame[0] + frame[1])


def ee_frame(frame):
    return rank_one_nonzero(frame) and (not odd_c(frame)) and even_sum_ab(frame)


def oe_frame(frame):
    return rank_one_nonzero(frame) and (not odd_c(frame)) and (not even_sum_ab(frame))


# --- polynomial arithmetic in Z[a,b,c] ---------------------------------------

def poly_add(left, right):
    total = dict(left)
    for key, value in right.items():
        total[key] = total.get(key, 0) + value
        if total[key] == 0:
            del total[key]
    return total


def poly_sub(left, right):
    return poly_add(left, {key: -value for key, value in right.items()})


def poly_mul(left, right):
    total = {}
    for left_key, left_value in left.items():
        for right_key, right_value in right.items():
            key = tuple(left_key[index] + right_key[index] for index in range(3))
            total[key] = total.get(key, 0) + left_value * right_value
            if total[key] == 0:
                del total[key]
    return total


def poly_const(value):
    if value == 0:
        return {}
    return {(0, 0, 0): value}


def poly_var(index):
    key = [0, 0, 0]
    key[index] = 1
    return {tuple(key): 1}


VAR_A = poly_var(0)
VAR_B = poly_var(1)
VAR_C = poly_var(2)


def det_poly():
    # 2ab + c(a+b), the numerator of the determinant.
    return poly_add(poly_mul(poly_const(2), poly_mul(VAR_A, VAR_B)), poly_mul(VAR_C, poly_add(VAR_A, VAR_B)))


def complement_det_poly(goal):
    p, q, r = goal
    pa = poly_sub(poly_const(p), VAR_A)
    qb = poly_sub(poly_const(q), VAR_B)
    rc = poly_sub(poly_const(r), VAR_C)
    width = poly_sub(poly_const(p + q), poly_add(VAR_A, VAR_B))
    return poly_add(poly_mul(poly_const(2), poly_mul(pa, qb)), poly_mul(rc, width))


def elimination_data(goal):
    p, q, r = goal
    degree = p + q
    u_coeff = 2 * q + r
    v_coeff = 2 * p + r
    k_coeff = 2 * p * q + r * degree
    linear = u_coeff + v_coeff - 2 * degree
    quad_a = linear * linear - 4 * u_coeff * v_coeff
    quad_b = -2 * linear * k_coeff + 4 * u_coeff * k_coeff
    quad_c = k_coeff * k_coeff
    return {
        "goal": goal,
        "D": degree,
        "U": u_coeff,
        "V": v_coeff,
        "K": k_coeff,
        "coefB": linear,
        "A2": quad_a,
        "A1": quad_b,
        "A0": quad_c,
    }


def is_square(value):
    if value < 0:
        return None
    root = 0
    while (root + 1) * (root + 1) <= value:
        root += 1
    if root * root == value:
        return root
    return None


def integer_pairs(goal):
    data = elimination_data(goal)
    require(data["D"] != 0 and data["U"] != 0, "elimination met a zero divisor")
    found = []
    for second in range(-4, 5):
        discriminant = data["A2"] * second * second + data["A1"] * second + data["A0"]
        root = is_square(discriminant)
        if root is None:
            continue
        linear_value = data["coefB"] * second - data["K"]
        for sign in (1, -1):
            numerator = -linear_value + sign * root
            denominator = 2 * data["U"]
            if numerator % denominator != 0:
                continue
            first = numerator // denominator
            raw_c = data["K"] - first * data["U"] - second * data["V"]
            if raw_c % data["D"] != 0:
                continue
            third = raw_c // data["D"]
            left = (first, second, third)
            right = (goal[0] - first, goal[1] - second, goal[2] - third)
            if rank_one_nonzero(left) and rank_one_nonzero(right):
                found.append(tuple(sorted((left, right))))
    return sorted(set(found))


def outside_range_is_negative():
    # PROOF.md, Section 3. Delta = A2 b^2 + A1 b + A0 with A2 < 0 is at most
    # -(|A2| b^2 - |A1| |b| - |A0|). For n >= 5 the positive polynomial
    # f(n) = |A2| n^2 - |A1| n - |A0| stays positive because f(5) > 0 and
    # f(n+1) - f(n) = |A2|(2n+1) - |A1| >= 11|A2| - |A1| > 0.
    goals = list(TARGETS.values()) + [sub(FOUR, target) for target in TARGETS.values()] + [TWO_I]
    for goal in goals:
        data = elimination_data(goal)
        require(data["A2"] < 0, "discriminant is not eventually negative")
        absolute_a2 = -data["A2"]
        absolute_a1 = abs(data["A1"])
        absolute_a0 = abs(data["A0"])
        def lower(n):
            return absolute_a2 * n * n - absolute_a1 * n - absolute_a0

        require(lower(5) > 0, "f(5) was not positive for " + str(goal))
        require(absolute_a2 * 11 - absolute_a1 > 0, "the n=5 difference was not positive for " + str(goal))
        for step_n in range(5, 20):
            difference = lower(step_n + 1) - lower(step_n)
            require(difference == absolute_a2 * (2 * step_n + 1) - absolute_a1,
                    "the discriminant difference identity failed")
            require(2 * step_n + 1 >= 11 and difference > 0 and lower(step_n) > 0,
                    "the |b|>=5 induction failed for " + str(goal))
        for second in range(-8, 9):
            if abs(second) < 5:
                continue
            discriminant = data["A2"] * second * second + data["A1"] * second + data["A0"]
            require(discriminant < 0, "Delta stayed nonnegative outside the proved range")


def polynomial_identity(goal):
    data = elimination_data(goal)
    first = det_poly()
    second = complement_det_poly(goal)
    gap = poly_add(poly_mul(VAR_C, poly_const(data["D"])), poly_const(-data["K"]))
    gap = poly_add(gap, poly_mul(VAR_A, poly_const(data["U"])))
    gap = poly_add(gap, poly_mul(VAR_B, poly_const(data["V"])))
    # g - f + (c D - K + U a + V b) = 0, so f = g = 0 forces the c formula.
    require(poly_add(poly_sub(second, first), gap) == {}, "elimination identity failed")
    cleared = poly_add(
        poly_mul(poly_const(2 * data["D"]), poly_mul(VAR_A, VAR_B)),
        poly_mul(
            poly_sub(poly_const(data["K"]), poly_add(poly_mul(VAR_A, poly_const(data["U"])), poly_mul(VAR_B, poly_const(data["V"])))),
            poly_add(VAR_A, VAR_B),
        ),
    )
    # The cleared numerator equals -(U a^2 + (coefB b - K) a + b(V b - K)).
    quadratic = poly_mul(poly_const(data["U"]), poly_mul(VAR_A, VAR_A))
    linear = poly_sub(poly_mul(poly_const(data["coefB"]), VAR_B), poly_const(data["K"]))
    quadratic = poly_add(quadratic, poly_mul(linear, VAR_A))
    tail = poly_mul(VAR_B, poly_sub(poly_mul(poly_const(data["V"]), VAR_B), poly_const(data["K"])))
    quadratic = poly_add(quadratic, tail)
    require(poly_add(cleared, quadratic) == {}, "quadratic numerator identity failed")


def pair_classification():
    outside_range_is_negative()
    for name, target in TARGETS.items():
        polynomial_identity(target)
        polynomial_identity(sub(FOUR, target))
        require(integer_pairs(target) == [tuple(sorted((PROJECTORS[name[0]], PROJECTORS[name[1]])))],
                name + " has an unexpected integer splitting")
        require(integer_pairs(sub(FOUR, target)) == [], name + " complement has an integer splitting")
    polynomial_identity(TWO_I)
    require(set(integer_pairs(TWO_I)) == {tuple(sorted((TWO_A, TWO_B))), tuple(sorted((TWO_P, TWO_Q)))},
            "2I has an unexpected integer splitting")
    for pair in integer_pairs(TWO_I):
        require(all(not odd_c(frame) for frame in pair), "an odd-c frame entered a 2I splitting")


def target_identities():
    require(add(TARGETS.values()) == FOUR, "the targets do not sum to 4I")
    for name, target in TARGETS.items():
        require(sum(target) == 2, name + " lost trace 2")
        require(twice_det(target) == 1, name + " lost determinant 1/2")
        complement = sub(FOUR, target)
        require(twice_det(complement) == 17, name + " complement lost determinant 17/2")
        require(odd(target[0] + target[1]) and odd_c(target), name + " lost parity (1,1)")
        require(target != (0, 0, 0) and not rank_one_nonzero(target), name + " became rank one")
        require(not rank_one_nonzero(complement), name + " complement became rank one")


def parity_lemma():
    # 2ab is even. The determinant numerator is even exactly when c(a+b) is even.
    # An odd c therefore forces a+b even on every integer rank-one frame.
    for a_bit in (0, 1):
        for b_bit in (0, 1):
            for c_bit in (0, 1):
                product = (c_bit * ((a_bit + b_bit) % 2)) % 2
                if product == 0 and c_bit == 1:
                    require((a_bit + b_bit) % 2 == 0, "odd c survived with odd a+b")
    require(ee_frame(TWO_A) and ee_frame(TWO_B) and oe_frame(A) and oe_frame(B), "projector types moved")
    require(odd_c(P) and odd_c(Q) and even_sum_ab(P) and even_sum_ab(Q), "P or Q left type EO")
    for first in range(-2, 3):
        for second in range(-2, 3):
            for third in range(-2, 3):
                frame = (first, second, third)
                negated = scale(-1, frame)
                require(odd_c(frame) == odd_c(negated), "negation changed c parity")
                require(even_sum_ab(frame) == even_sum_ab(negated), "negation changed a+b parity")


def carrier_signature():
    # Every carrier has exactly one OE frame. Size 3 then needs one EE and one EO.
    # Count φ-sums over the three available types. OO is already excluded.
    signatures = []
    for first in ((0, 0), (1, 0), (0, 1)):
        for second in ((0, 0), (1, 0), (0, 1)):
            for third in ((0, 0), (1, 0), (0, 1)):
                total = tuple((first[index] + second[index] + third[index]) % 2 for index in range(2))
                if total == (1, 1):
                    counts = sorted([first, second, third])
                    signatures.append(tuple(counts))
    require(set(signatures) == {((0, 0), (0, 1), (1, 0))}, "a size-3 signature other than EE+EO+OE appeared")
    pair_signatures = []
    for first in ((0, 0), (1, 0), (0, 1)):
        for second in ((0, 0), (1, 0), (0, 1)):
            total = tuple((first[index] + second[index]) % 2 for index in range(2))
            if total == (1, 1):
                pair_signatures.append(tuple(sorted((first, second))))
    require(set(pair_signatures) == {((0, 1), (1, 0))}, "a size-2 signature other than EO+OE appeared")


def solved_branch(width, anchor, projectors, triples):
    # total = projectors + anchor + G + sum(H - anchor - G).
    # Coefficient of G and of anchor is 1 - width.
    constant = add(list(projectors) + list(triples))
    coefficient = 1 - width
    right = sub(sub(FOUR, constant), scale(coefficient, anchor))
    return coefficient, right


def odd_anchor_cases():
    # n_OE = 1, n_EE = 1. The unique OE anchor is A or B.
    # BP,BQ are triples when the anchor is A; AP,AQ are triples when it is B.
    layouts = {
        A: {
            "forced_triples": (TARGETS["BP"], TARGETS["BQ"]),
            "optional_pairs": {"P": P, "Q": Q},
            "optional_targets": {"P": TARGETS["AP"], "Q": TARGETS["AQ"]},
        },
        B: {
            "forced_triples": (TARGETS["AP"], TARGETS["AQ"]),
            "optional_pairs": {"P": P, "Q": Q},
            "optional_targets": {"P": TARGETS["BP"], "Q": TARGETS["BQ"]},
        },
    }
    for anchor, layout in layouts.items():
        forced = layout["forced_triples"]
        require(sub(forced[0], forced[1]) != (0, 0, 0), "forced triple targets collided")
        # k = 4: every target is a triple. Then G = -anchor, so G has the anchor's type.
        all_targets = tuple(TARGETS.values())
        coefficient, right = solved_branch(4, anchor, (), all_targets)
        require(coefficient == -3 and right == scale(3, anchor), "the four-triple relation moved")
        require(not ee_frame(scale(-1, anchor)), "negating the OE anchor produced an EE frame")
        # k = 2: both optional targets are pairs, so both P and Q are labels.
        both = (P, Q)
        coefficient, right = solved_branch(2, anchor, both, forced)
        require(coefficient == -1, "two-pair branch lost coefficient -1")
        frame_g = scale(-1, right)
        images = [sub(target, add((anchor, frame_g))) for target in forced]
        require(add([anchor, frame_g, *both, *images]) == FOUR, "two-pair plug-in missed 4I")
        require(not ee_frame(frame_g), "two-pair branch produced an EE frame")
        require(len(set(images)) == 2, "two-pair images collided")
        for projector in both:
            for target in forced:
                candidate = sub(target, add((anchor, projector)))
                require(not ee_frame(candidate), "two-pair overlap produced an EE frame")
        # k = 3: exactly one optional target is a pair.
        for name, projector in layout["optional_pairs"].items():
            triples = forced + (layout["optional_targets"][{"P": "Q", "Q": "P"}[name]],)
            coefficient, right = solved_branch(3, anchor, (projector,), triples)
            require(coefficient == -2, "three-triple branch lost coefficient -2")
            require(any(odd(value) for value in right), "three-triple branch allowed an integer G")
            for target in triples:
                candidate = sub(target, add((anchor, projector)))
                require(not ee_frame(candidate), "overlap produced an EE frame at " + name)
            fractional = tuple(Fraction(value, coefficient) for value in right)
            images = [
                sub(tuple(Fraction(value) for value in target), add((anchor, fractional)))
                for target in triples
            ]
            total = add([anchor, fractional, projector, *images])
            require(total == FOUR, "fractional three-triple plug-in missed 4I")
            require(any(part.denominator != 1 for part in fractional), "fractional G was secretly integral")
    nonprojector = (3, 0, 0)
    require(oe_frame(nonprojector), "3A is no longer an OE frame")
    coefficient, right = solved_branch(4, nonprojector, (), tuple(TARGETS.values()))
    require(coefficient == -3 and right == scale(3, nonprojector), "four triples used that the anchor is a projector")
    require(not ee_frame(scale(-1, nonprojector)), "negating 3A produced an EE frame")


def no_even_type_cases():
    # n_OE = 0: every frame has even a+b, every subset misses the target parity.
    sample = (P, P, Q, Q, TWO_A, TWO_B)
    require(add(sample) == FOUR, "the four-odd sample does not sum to 4I")
    require(sum(odd_c(frame) for frame in sample) == 4, "the four-odd sample lost its count")
    require(all(even_sum_ab(frame) for frame in sample), "the four-odd sample gained an OE frame")
    seen = set()
    for mask in range(1, 1 << len(sample)):
        chosen = [sample[index] for index in range(len(sample)) if mask & (1 << index)]
        if any(odd(frame[0] + frame[1]) for frame in chosen):
            raise SystemExit("FAIL: an even-a+b sample produced an odd subset")
        total = add(chosen)
        if total in TARGETS.values():
            seen.add(total)
    require(seen == set(), "a target survived inside an OE-free sample")
    # n_EE = 0 and both A and B present: the two extra odd frames would split 2I.
    require(add((A, B, P, Q)) == TWO_I, "A+B+P+Q is no longer 2I")
    for pair in integer_pairs(TWO_I):
        require(sum(odd_c(frame) for frame in pair) == 0, "2I gained an odd-c splitting")


def boundary_witness():
    labels = (A, B, P, Q, TWO_A, TWO_B)
    require(add(labels) == FOUR, "the #7100 labels do not sum to 4I")
    require(sum(odd_c(frame) for frame in labels) == 2, "the boundary witness is no longer a two-odd example")
    require(all(rank_one_nonzero(frame) for frame in labels), "a boundary label lost rank one")
    seen = set()
    for mask in range(1, 1 << len(labels)):
        total = add(labels[index] for index in range(len(labels)) if mask & (1 << index))
        if total in TARGETS.values():
            seen.add(total)
    require(seen == set(TARGETS.values()), "the boundary witness lost support")
    tampered = (A, B, P, Q, add((TWO_A, A)), TWO_B)
    require(add(tampered) != FOUR, "shifting 2A by A kept the sum")
    require(not rank_one_nonzero((0, 0, 0)), "zero became rank one")
    require(twice_det((1, 1, 0)) == 2 and not rank_one_nonzero((1, 1, 0)), "I changed determinant")


def rank_one_box(bound):
    frames = set()
    for value in range(1, bound + 1):
        frames.add((value, 0, 0))
        frames.add((-value, 0, 0))
        frames.add((0, value, 0))
        frames.add((0, -value, 0))
    for third in range(-bound, bound + 1):
        if third == 0:
            continue
        square = third * third
        divisors = []
        step = 1
        while step * step <= square:
            if square % step == 0:
                divisors.append(step)
                if step * step != square:
                    divisors.append(square // step)
            step += 1
        for divisor in divisors:
            for first_factor in (divisor, -divisor):
                second_factor = square // first_factor
                if (first_factor - third) % 2 or (second_factor - third) % 2:
                    continue
                first = (first_factor - third) // 2
                second = (second_factor - third) // 2
                if max(abs(first), abs(second), abs(third)) <= bound:
                    frames.add((first, second, third))
    frames.discard((0, 0, 0))
    return list(frames)


def meets_support(labels):
    seen = set()
    width = len(labels)
    for mask in range(1, 1 << width):
        total = add(labels[index] for index in range(width) if mask & (1 << index))
        if total in TARGETS.values():
            seen.add(total)
            if len(seen) == 4:
                return True
    return False


def bounded_control():
    """Control only: every integral solution inside max-norm 4 with odd-c count at least 4 misses support.

    The witness sits in this box and meets support with odd-c count 2. A hit at count 4 or 6
    would falsify the theorem inside the box. Absence in the box is not the proof.
    """
    pool = rank_one_box(4)
    pairs = {}
    for left in range(len(pool)):
        for right in range(left, len(pool)):
            total = add((pool[left], pool[right]))
            pairs.setdefault(total, []).append((left, right))
    support_counts = set()
    high_support = 0
    examined = 0
    for left_name, right_name in combinations(("A", "B", "P", "Q"), 2):
        old = (PROJECTORS[left_name], PROJECTORS[right_name])
        residual = sub(sub(FOUR, old[0]), old[1])
        base = odd_c(old[0]) + odd_c(old[1])
        for total, lefts in pairs.items():
            need = sub(residual, total)
            if need < total:
                continue
            rights = pairs.get(need)
            if not rights:
                continue
            for i, j in lefts:
                odd_left = odd_c(pool[i]) + odd_c(pool[j])
                for k, l in rights:
                    if total == need and (k, l) < (i, j):
                        continue
                    examined += 1
                    count = base + odd_left + odd_c(pool[k]) + odd_c(pool[l])
                    labels = [old[0], old[1], pool[i], pool[j], pool[k], pool[l]]
                    if meets_support(labels):
                        support_counts.add(count)
                        if count >= 4:
                            high_support += 1
    require(examined >= 200, "the norm-4 control enumerated fewer quadruples than the recorded box")
    require(2 in support_counts, "the norm-4 control lost the two-odd witness")
    require(high_support == 0 and all(count < 4 for count in support_counts),
            "the norm-4 control found a four-odd support solution")


def main():
    target_identities()
    parity_lemma()
    carrier_signature()
    pair_classification()
    odd_anchor_cases()
    no_even_type_cases()
    boundary_witness()
    bounded_control()
    print("PASS four-odd-c-length6-absence checks")


if __name__ == "__main__":
    main()
