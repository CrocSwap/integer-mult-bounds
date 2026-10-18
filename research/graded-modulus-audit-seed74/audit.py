"""Exact admission and witnesses for PR524's unchanged grade recurrence.

Research audit by Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. The carry-filter packing is adapted from Chafik Boukhalfa's PR524.
"""

from itertools import product
from math import prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(shape, modulus=None):
    shape = tuple(shape)
    require(bool(shape) and all(type(n) is int and n > 0 for n in shape),
            "shape must contain positive integer radices")
    if modulus is not None:
        require(type(modulus) is int and modulus > 0,
                "modulus must be a positive integer")
    return shape


def count_witnesses(shape):
    """Return each attainable count and a subset of gaps producing it.

    This is an exact finite subset-sum calculation, not a rational-frame or
    circuit search. Only one witness is retained when several subsets agree.
    """
    shape = validate(shape)
    active = [i for i, n in enumerate(shape) if n > 1]
    witnesses = {0: ()}
    for left, right in zip(active, active[1:]):
        previous = list(witnesses.items())
        for count, selected in previous:
            witnesses.setdefault(count + right - left, selected + (left,))
    return witnesses


def admissible(shape, modulus):
    shape = validate(shape, modulus)
    return not any(c > 0 and c % modulus == 0 for c in count_witnesses(shape))


def least_modulus(shape):
    shape = validate(shape)
    for modulus in range(1, len(shape) + 1):
        if admissible(shape, modulus):
            return modulus
    raise RuntimeError("the inherited T=D choice must be admissible")


def witness(shape, count):
    """Construct input digits realizing a specified attainable carry count."""
    shape = validate(shape)
    choices = count_witnesses(shape)
    require(count in choices, "requested carry count is unattainable")
    selected = set(choices[count])
    a, b, c, carries = [], [], [], []
    incoming = 0
    for i, radix in enumerate(shape):
        if radix == 1:
            x = y = z = 0
            outgoing = incoming
        else:
            outgoing = int(i in selected)
            # For outgoing 1, x+y+incoming = radix+incoming.
            x, y = (radix - 1, 1) if outgoing else (0, 0)
            z = incoming
        require(x + y + incoming == z + radix * outgoing,
                "constructed digit transition failed")
        a.append(x)
        b.append(y)
        c.append(z)
        carries.append(outgoing)
        incoming = outgoing
    require(incoming == 0 and sum(carries) == count,
            "constructed carry count or final carry failed")
    return {"a": a, "b": b, "c": c, "carries": carries, "count": count}


def layout(shape, modulus, *, index_padding=True, grade_wrap=True):
    """PR524's layout with an explicitly supplied modulus; no admission implied."""
    shape = validate(shape, modulus)
    size = prod(shape)
    stride, weight = 1, 1 % modulus
    strides, weights = [], []
    for radix in shape:
        strides.append(stride)
        weights.append(weight)
        stride *= radix
        weight = (radix * weight - 1) % modulus
    coordinates = list(product(*(range(n) for n in shape)))
    indices = [sum(x * s for x, s in zip(a, strides)) for a in coordinates]
    grades = [sum(x * w for x, w in zip(a, weights)) % modulus
              for a in coordinates]
    width = 2 * size - 1 if index_padding else size
    slots = [i + width * g for i, g in zip(indices, grades)]
    outputs = []
    for i, g in zip(indices, grades):
        grades_to_read = [g]
        if grade_wrap and g + modulus <= 2 * modulus - 2:
            grades_to_read.append(g + modulus)
        outputs.append([i + width * r for r in grades_to_read])
    return {"coordinates": coordinates, "indices": indices, "grades": grades,
            "slots": slots, "outputs": outputs, "product_slots": 2 * max(slots) + 1}


def convolve(f, g, shape, modulus, *, admit=True, index_padding=True,
             grade_wrap=True, signed_cross=True):
    """Four exact nonnegative integer products; controls can bypass admission.

    The coefficient-slot bound and signed split are inherited from PR524.
    This research adapter is not installed in the predecessor or selected code.
    """
    shape = validate(shape, modulus)
    require(not admit or admissible(shape, modulus), "inadmissible grade modulus")
    size = prod(shape)
    require(len(f) == len(g) == size, "coefficient vector length mismatch")
    require(all(type(x) is int for v in (f, g) for x in v),
            "coefficients must be integers")
    info = layout(shape, modulus, index_padding=index_padding, grade_wrap=grade_wrap)
    bound = size * max(map(abs, f), default=0) * max(map(abs, g), default=0)
    slot_bits = max(1, bound.bit_length())
    slot_mask = (1 << slot_bits) - 1

    def pack(values, sign):
        return sum(max(0, sign * value) << (slot_bits * index)
                   for value, index in zip(values, info["slots"]))

    packed_f = [pack(f, sign) for sign in (1, -1)]
    packed_g = [pack(g, sign) for sign in (1, -1)]
    result = [0] * size
    for i, pf in enumerate(packed_f):
        for j, pg in enumerate(packed_g):
            if not signed_cross and i != j:
                continue
            packed_product = pf * pg
            sign = 1 if i == j else -1
            for k, slots in enumerate(info["outputs"]):
                result[k] += sign * sum((packed_product >> (slot_bits * slot)) & slot_mask
                                        for slot in slots)
    return result
