# SPDX-License-Identifier: Apache-2.0
"""One-clean-carry scalar circuits with temporarily writable operands."""

from fractions import Fraction

MAX_WIDTH = 256
MAX_GATES = 20_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(width, gates):
    require(type(width) is int and 4 <= width <= MAX_WIDTH, "bounded width")
    require(len(gates) <= MAX_GATES, "bounded gate inventory")
    for gate in gates:
        require(len(gate) in (2, 3), "CX or CCX gate")
        require(len(set(gate)) == len(gate), "distinct gate wires")
        require(
            all(type(i) is int and 0 <= i <= 2 * width for i in gate),
            "two operand banks and one carry",
        )


def adder(source, target, carry):
    """MAJ/UMA modulo 2**n; both operand banks may be written internally."""
    n = len(source)
    require(1 <= n <= MAX_WIDTH and len(target) == n, "adder widths")
    require(len({*source, *target, carry}) == 2 * n + 1, "disjoint wires")
    require(
        all(
            type(i) is int and 0 <= i <= 2 * MAX_WIDTH
            for i in (*source, *target, carry)
        ),
        "bounded integer wire names",
    )
    if n == 1:
        return [(source[0], target[0])]
    gates = []
    for i in range(n - 1):
        a, b, c = source[i], target[i], carry if i == 0 else source[i - 1]
        gates.extend(((a, c), (a, b), (b, c, a)))
    gates.extend(((source[-1], target[-1]), (source[-2], target[-1])))
    for i in reversed(range(n - 1)):
        a, b, c = source[i], target[i], carry if i == 0 else source[i - 1]
        gates.extend(((b, c, a), (a, c), (c, b)))
    require(len(gates) == 6 * n - 4, "literal MAJ/UMA tariff")
    return gates


def shifted(width, exponent):
    validate(width, ())
    require(type(exponent) is int and -12 <= exponent <= 8, "bounded shift")
    source, target = tuple(range(width, 2 * width)), tuple(range(width))
    if exponent >= width:
        return []
    if exponent >= 0:
        return adder(source[: width - exponent], target[exponent:], 2 * width)
    k = -exponent
    require(k < width, "right shift below width")
    fill = [(source[-1], source[i]) for i in range(k)]
    active = source[k:] + source[:k]
    return fill + adder(active, target, 2 * width) + list(reversed(fill))


def negate(width):
    """Three modular shears and a swap: (T,S) -> (-T,S)."""
    validate(width, ())
    target, source = tuple(range(width)), tuple(range(width, 2 * width))
    forward = adder(source, target, 2 * width)
    backward = adder(target, source, 2 * width)
    gates = forward + list(reversed(backward)) + forward
    for t, s in zip(target, source, strict=True):
        gates.extend(((t, s), (s, t), (t, s)))
    return gates


def circuit(width, kind, a, b, recipe, powers):
    validate(width, ())
    require(kind in ("add", "scale"), "scalar kind")
    require(type(a) is int and type(b) is int and b != 0, "integer coefficient")
    q = Fraction(a, b)
    require(
        abs(q.numerator) <= 255
        and q.denominator <= 4096
        and q.denominator.bit_count() == 1,
        "bounded dyadic coefficient",
    )
    require(len(recipe) <= 32, "bounded recipe")
    require(len(powers) <= 9, "bounded signed powers")
    gates = []
    if kind == "add":
        require(
            all(
                sign in (-1, 1) and type(e) is int and -12 <= e <= 8
                for sign, e in powers
            ),
            "signed-power alphabet",
        )
        require(
            sum(Fraction(sign) * Fraction(2) ** e for sign, e in powers)
            == Fraction(a, b),
            "exact coefficient expansion",
        )
        require(
            all(e >= 1 - q.denominator.bit_length() for _, e in powers),
            "powers use only coefficient denominator alignment",
        )
        for sign, exponent in powers:
            emitted = shifted(width, exponent)
            gates.extend(emitted if sign > 0 else reversed(emitted))
    else:
        require(not powers, "scale has no ADD powers")
        gates = scale(width, recipe, q)
    validate(width, gates)
    return gates


def scale(width, recipe, coefficient):
    require(abs(coefficient.numerator).bit_count() == 1, "power-of-two SCALE")
    exponent = (
        abs(coefficient.numerator).bit_length() - coefficient.denominator.bit_length()
    )
    expected = [("neg", 0)] if coefficient < 0 else []
    expected += [("double" if exponent > 0 else "half", 0)] * abs(exponent)
    require(recipe == expected, "canonical guarded SCALE recipe")
    gates, product = [], Fraction(1)
    for instruction in recipe:
        require(len(instruction) == 2 and instruction[1] == 0, "scale target bank")
        name = instruction[0]
        require(name in ("neg", "half", "double"), "scale-only recipe")
        product *= -1 if name == "neg" else Fraction(1, 2) if name == "half" else 2
        if name == "neg":
            gates.extend(negate(width))
        else:
            shift = []
            for i in range(width - 1):
                shift.extend(((i, i + 1), (i + 1, i), (i, i + 1)))
            shift.append((width - 2, width - 1))
            gates.extend(shift if name == "half" else reversed(shift))
    require(product == coefficient, "exact SCALE recipe coefficient")
    return gates


def apply(width, gates, wires):
    """AND/XOR interpreter, also for bit-packed exhaustive truth columns."""
    validate(width, gates)
    require(len(wires) == 2 * width + 1, "complete wire inventory")
    require(
        all(type(v) is int and 0 <= v and v.bit_length() <= 65536 for v in wires),
        "bounded scalar or packed truth columns",
    )
    result = list(wires)
    for gate in gates:
        control = result[gate[0]]
        if len(gate) == 3:
            control &= result[gate[1]]
        result[gate[-1]] ^= control
    return result


def execute(width, gates, source, target, *, carry=0):
    validate(width, gates)
    require(carry == 0, "clean carry entrance")
    require(all(type(v) is int for v in (source, target)), "integer operands")
    limit = 1 << (width - 1)
    require(-limit <= source < limit and -limit <= target < limit, "signed operands")
    wires = [(value >> i) & 1 for value in (target, source) for i in range(width)]
    after = apply(width, gates, wires + [carry])
    require(after[width : 2 * width] == wires[width:], "source restored")
    require(after[-1] == 0, "carry restored")
    return sum(after[i] << i for i in range(width))


def counts(gates):
    return {
        "cx": sum(len(g) == 2 for g in gates),
        "ccx": sum(len(g) == 3 for g in gates),
    }
