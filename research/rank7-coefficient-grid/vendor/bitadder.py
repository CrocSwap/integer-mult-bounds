# SPDX-License-Identifier: Apache-2.0
"""Read-only shifted-source ADDs with explicit reversible Boolean gates."""

from fractions import Fraction

MAX_WIDTH = 256
MAX_GATES = 20_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational(a, b):
    require(type(a) is int and type(b) is int and b > 0, "integer fraction")
    q = Fraction(a, b)
    require(abs(q.numerator) <= 255, "bounded numerator")
    require(q.denominator <= 4096, "bounded denominator")
    require(q.denominator.bit_count() == 1, "dyadic denominator")
    return q


def terms(a, b, signed=True):
    """At most nine signed powers, each (sign, binary exponent)."""
    q = rational(a, b)
    n, exponent = abs(q.numerator), 1 - q.denominator.bit_length()
    sign = -1 if q < 0 else 1
    result = []
    for _ in range(9):
        if n == 0:
            break
        if n & 1:
            digit = 2 - n % 4 if signed and n > 1 else 1
            result.append((sign * digit, exponent))
            n -= digit
        n //= 2
        exponent += 1
    require(n == 0 and len(result) <= 9, "bounded signed expansion")
    reconstructed = sum(Fraction(s) * Fraction(2) ** e for s, e in result)
    require(reconstructed == q, "exact coefficient expansion")
    return result


def adder(width, shift):
    """Modulo 2**width, add the virtually shifted source, preserving it."""
    require(type(width) is int and 1 <= width <= MAX_WIDTH, "bounded width")
    require(type(shift) is int and -12 <= shift <= 8, "bounded shift")
    first = max(0, shift)
    active = width - first
    if active <= 0:
        return []
    source = [("s", min(i - shift, width - 1)) for i in range(first, width)]
    target = [("t", i) for i in range(first, width)]
    carry = [("c", i) for i in range(active - 1)]
    if active == 1:
        return [("cx", source[0], target[0])]
    gates = [("ccx", source[0], target[0], carry[0])]
    for i in range(1, active - 1):
        gates.extend(
            [
                ("ccx", source[i], target[i], carry[i]),
                ("cx", source[i], target[i]),
                ("ccx", target[i], carry[i - 1], carry[i]),
            ]
        )
    gates.extend(
        [
            ("cx", source[-1], target[-1]),
            ("cx", carry[-1], target[-1]),
        ]
    )
    for i in range(active - 2, 0, -1):
        gates.extend(
            [
                ("ccx", target[i], carry[i - 1], carry[i]),
                ("cx", source[i], target[i]),
                ("ccx", source[i], target[i], carry[i]),
                ("cx", source[i], target[i]),
                ("cx", carry[i - 1], target[i]),
            ]
        )
    gates.extend(
        [
            ("ccx", source[0], target[0], carry[0]),
            ("cx", source[0], target[0]),
        ]
    )
    require(len(gates) == 8 * active - 11, "literal adder size")
    return gates


def circuit(width, a, b, *, signed=True):
    result = []
    for sign, shift in terms(a, b, signed):
        gates = adder(width, shift)
        result.extend(gates if sign > 0 else reversed(gates))
    require(len(result) <= MAX_GATES, "bounded circuit")
    validate(result, width)
    return result


def validate(gates, width):
    require(type(width) is int and 1 <= width <= MAX_WIDTH, "bounded width")
    require(len(gates) <= MAX_GATES, "bounded gate list")
    for gate in gates:
        require(gate[0] in ("cx", "ccx"), "Boolean gate kind")
        require(len(gate) == (3 if gate[0] == "cx" else 4), "gate arity")
        require(len(set(gate[1:])) == len(gate) - 1, "distinct gate ports")
        for kind, index in gate[1:]:
            require(kind in ("s", "t", "c"), "wire bank")
            limit = width - 1 if kind == "c" else width
            require(type(index) is int and 0 <= index < limit, "wire index")
        require(gate[-1][0] != "s", "source is read-only")


def apply(gates, wires, width):
    """Also executes bit-packed truth columns with the same AND/XOR rules."""
    validate(gates, width)
    result = dict(wires)
    require(len(result) == 3 * width - 1, "complete owned wire banks")
    for kind, limit in (("s", width), ("t", width), ("c", width - 1)):
        require(all((kind, i) in result for i in range(limit)), "owned wire")
    for gate in gates:
        control = result[gate[1]]
        if gate[0] == "ccx":
            control &= result[gate[2]]
        result[gate[-1]] ^= control
    return result


def execute(width, a, b, source, target, *, gates=None, exact=True):
    q = rational(a, b)
    require(type(source) is int and type(target) is int, "integer inputs")
    require(1 <= width <= MAX_WIDTH, "bounded width")
    modulus = 1 << width
    require(-modulus // 2 <= source < modulus // 2, "signed source range")
    require(-modulus // 2 <= target < modulus // 2, "signed target range")
    require(source % q.denominator == 0, "base-format alignment")
    endpoint = target + q * source
    if exact:
        require(-modulus // 2 <= endpoint < modulus // 2, "signed endpoint range")
    generated = circuit(width, a, b) if gates is None else gates
    wires = {
        (k, i): (v >> i) & 1
        for k, v in (("s", source), ("t", target))
        for i in range(width)
    }
    wires.update({("c", i): 0 for i in range(width - 1)})
    after = apply(generated, wires, width)
    require(all(after["s", i] == wires["s", i] for i in range(width)), "source return")
    require(all(after["c", i] == 0 for i in range(width - 1)), "clean carry return")
    observed = sum(after["t", i] << i for i in range(width))
    require(observed == int(endpoint) % modulus, "literal modular endpoint")
    return observed - modulus if observed >= modulus // 2 else observed
