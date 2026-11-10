"""Centered low-residue child. Produced by Nick Petalas. Apache-2.0."""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def child_bits(n, digit_bits, k):
    """Attained maximum magnitude bit length at declared parent width n."""
    need(all(type(x) is int for x in (n, digit_bits, k)), "integer widths")
    need(1 <= digit_bits <= 64 and 1 <= k <= digit_bits, "digit/residue width")
    need(1 <= n <= 228 * digit_bits, "parent capacity")
    length = (n + digit_bits - 1) // digit_bits
    top = n - digit_bits * (length - 1)
    slot = 2 * k - 1 + (length - 1).bit_length()
    return min(k, top) + (length - 1) * slot


def centered_digits(values, k):
    need(type(k) is int and 1 <= k <= 64, "residue width")
    need(type(values) in (list, tuple) and 1 <= len(values) <= 228, "array capacity")
    need(all(type(x) is int and 0 <= x < 1 << 64 for x in values), "unsigned digits")
    half = 1 << (k - 1)
    modulus = 2 * half
    return tuple((x + half) % modulus - half for x in values)


def decode(packed_product, left_length, right_length, k, slot):
    """Decode using the asymmetric interval, including its positive endpoint."""
    need(type(packed_product) is int, "integer product")
    need(all(type(x) is int and 1 <= x <= 228 for x in (left_length, right_length)),
         "decode capacity")
    need(type(k) is int and 1 <= k <= 64, "residue width")
    expected = 2 * k - 1 + (min(left_length, right_length) - 1).bit_length()
    need(type(slot) is int and slot == expected, "signed slot width")
    need(abs(packed_product).bit_length() <= 2 * k + (left_length + right_length - 2) * slot,
         "product capacity")
    half = 1 << (k - 1)
    base = 1 << slot
    coefficients = []
    remaining = packed_product
    for j in range(left_length + right_length - 1):
        overlap = min(left_length - 1, j) - max(0, j - right_length + 1) + 1
        lower = -overlap * half * (half - 1)
        upper = overlap * half * half
        need(upper - lower < base, "separated signed interval")
        coefficient = lower + (remaining - lower) % base
        need(coefficient <= upper, "coefficient outside signed interval")
        coefficients.append(coefficient)
        remaining = (remaining - coefficient) // base
    need(remaining == 0, "unconsumed packed product")
    return coefficients


def residue_lane(left, right, k):
    """One nonnegative magnitude multiplication; signs and extraction are charged work."""
    a = centered_digits(left, k)
    b = centered_digits(right, k)
    overlap = min(len(a), len(b))
    slot = 2 * k - 1 + (overlap - 1).bit_length()
    packed_a = sum(x << (j * slot) for j, x in enumerate(a))
    packed_b = sum(x << (j * slot) for j, x in enumerate(b))
    magnitude_product = abs(packed_a) * abs(packed_b)
    signed_product = -magnitude_product if (packed_a < 0) != (packed_b < 0) else magnitude_product
    coefficients = decode(signed_product, len(a), len(b), k, slot)
    modulus = 1 << k
    bill = {
        "exact_child_calls": 1, "residue_bits": k, "slot_bits": slot,
        "overlap": overlap, "coefficient_count": len(coefficients),
        "left_child_bits": abs(packed_a).bit_length(),
        "right_child_bits": abs(packed_b).bit_length(),
        "left_child_bound": k + (len(a) - 1) * slot,
        "right_child_bound": k + (len(b) - 1) * slot,
        "signed_coefficient_lower": -overlap * (modulus // 2) * (modulus // 2 - 1),
        "signed_coefficient_upper": overlap * (modulus // 2) ** 2,
        "slot_capacity": 1 << slot,
    }
    need(bill["left_child_bits"] <= bill["left_child_bound"], "left magnitude bound")
    need(bill["right_child_bits"] <= bill["right_child_bound"], "right magnitude bound")
    return [x % modulus for x in coefficients], bill
