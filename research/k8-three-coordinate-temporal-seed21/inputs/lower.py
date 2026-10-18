"""Smaller exact dyadic circuits for the fixed PR626 complex scalar words.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Primitive vocabulary and the original Horner circuit follow icekylinx's
PR425/433/531 lineage, retained by Jeremy Kothe's PR622 supplier.
"""
from fractions import Fraction


def power_of_two(n):
    return n > 0 and n & (n - 1) == 0


def lower(op, work=("W", 0)):
    """Return real-component primitives; work may be dirty on entry.

    Every addition leaves work zero. All operations use the macro's frame.
    The complex circuit applies this word separately to real and imaginary parts.
    """
    tag, target = op[0], tuple(op[1])
    if target == work:
        raise ValueError("coefficient work aliases a scalar register")
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        source = tuple(op[2])
        if source == work:
            raise ValueError("coefficient work used as a scalar source")
        return [("copy", target, source)]
    if tag == "scale":
        q = Fraction(op[2], op[3])
        if not power_of_two(abs(q.numerator)) or not power_of_two(q.denominator):
            raise ValueError("scale is not a signed power of two")
        shift = abs(q.numerator).bit_length() - q.denominator.bit_length()
        result = [("double" if shift > 0 else "halve", target)] * abs(shift)
        if q < 0:
            result.append(("negate", target))
        return result
    if tag != "add":
        raise ValueError("unknown scalar macro")
    source = tuple(op[2])
    q = Fraction(op[3], op[4])
    if source in (target, work) or not q or not power_of_two(q.denominator):
        raise ValueError("addition requires distinct registers and a nonzero dyadic")
    accumulate = "add" if q > 0 else "subtract"
    if abs(q) == 1:
        return [(accumulate, target, source), ("clear", work)]
    # Copy replaces clear + addition of the leading binary digit.
    result = [("copy", work, source)]
    for bit in bin(abs(q.numerator))[3:]:
        result.append(("double", work))
        if bit == "1":
            result.append(("add", work, source))
    result.extend([("halve", work)] * (q.denominator.bit_length() - 1))
    result.extend([(accumulate, target, work), ("clear", work)])
    return result
