# SPDX-License-Identifier: Apache-2.0
"""Guarded reversible scalar circuits with explicit cleanup and shift costs."""

from fractions import Fraction as Q

import bitadder

MAX_WIDTH = 256
MAX_GATES = 50_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def swap(left, right):
    return [("cx", left, right), ("cx", right, left), ("cx", left, right)]


def shift(width, target, half):
    """HALF requires even input; DOUBLE requires a redundant sign bit."""
    require(2 <= width <= MAX_WIDTH and target in (0, 1, 2), "shift domain")
    gates = []
    for i in range(width - 1):
        gates.extend(swap((target, i), (target, i + 1)))
    gates.append(("cx", (target, width - 2), (target, width - 1)))
    require(len(gates) == 3 * width - 2, "charged rotation and sign fill")
    return gates if half else list(reversed(gates))


def negate(width, target):
    """Two's-complement negation; lower-prefix OR is invariant under negation."""
    require(2 <= width <= MAX_WIDTH and target in (0, 1, 2), "negation domain")
    prefix = [("cx", (target, 0), (3, 0))]
    for i in range(1, width - 1):
        prefix.extend(
            [
                ("cx", (3, i - 1), (3, i)),
                ("cx", (target, i), (3, i)),
                ("ccx", (3, i - 1), (target, i), (3, i)),
            ]
        )
    flips = [("cx", (3, i - 1), (target, i)) for i in range(1, width)]
    gates = prefix + flips + list(reversed(prefix))
    require(len(gates) == 7 * width - 11, "literal negation size")
    return gates


def add(width, target, source, a, b):
    require(
        target in (0, 1, 2) and source in (0, 1, 2) and source != target,
        "distinct ADD banks",
    )
    names = {"s": source, "t": target, "c": 3}
    return [
        tuple([gate[0]] + [(names[k], i) for k, i in gate[1:]])
        for gate in bitadder.circuit(width, a, b)
    ]


def unit(width, instruction):
    kind, target = instruction[:2]
    require(target in (0, 2), "read-only external source")
    if kind == "add":
        return add(width, target, instruction[2], instruction[3], 1)
    if kind == "copy":
        require(target == 2 and instruction[2] == 1, "zero-scratch copy")
        return [("cx", (1, i), (2, i)) for i in range(width)]
    if kind == "neg":
        return negate(width, target)
    require(kind in ("double", "half"), "supported reversible unit")
    return shift(width, target, kind == "half")


def control(width, recipe):
    """Replace a scratch CLEAR by the inverse source-only preparation."""
    require(len(recipe) <= 32, "bounded inherited recipe")
    gates, preparation = [], []
    for index, instruction in enumerate(recipe):
        if instruction[0] == "clear":
            require(
                instruction == ("clear", 2)
                and index == len(recipe) - 1
                and preparation,
                "final known-scratch cleanup",
            )
            gates.extend(reversed(preparation))
        else:
            emitted = unit(width, instruction)
            gates.extend(emitted)
            if instruction[1] == 2:
                require(
                    instruction[0] != "add" or instruction[2] == 1,
                    "scratch preparation only reads preserved source",
                )
                preparation.extend(emitted)
    validate(gates, width)
    return gates


def circuit(width, kind, a, b, recipe):
    require(type(width) is int and 2 <= width <= MAX_WIDTH, "bounded width")
    require(kind in ("add", "scale"), "scalar kind")
    gates = add(width, 0, 1, a, b) if kind == "add" else control(width, recipe)
    validate(gates, width)
    require(all(port[0] != 2 for g in gates for port in g[1:]), "scratch-free caller")
    return gates


def validate(gates, width):
    require(type(width) is int and 2 <= width <= MAX_WIDTH, "bounded width")
    require(len(gates) <= MAX_GATES, "bounded Boolean circuit")
    for gate in gates:
        require(
            gate[0] in ("cx", "ccx") and len(gate) == (3 if gate[0] == "cx" else 4),
            "literal Boolean gate",
        )
        require(
            len({tuple(port) for port in gate[1:]}) == len(gate) - 1,
            "distinct gate ports",
        )
        for bank, bit in gate[1:]:
            require(
                type(bank) is int
                and 0 <= bank <= 3
                and type(bit) is int
                and 0 <= bit < width - (bank == 3),
                "owned wire",
            )
        require(gate[-1][0] != 1, "read-only source")


def apply(gates, wires, width):
    """AND/XOR evaluation also accepts packed truth columns."""
    validate(gates, width)
    require(len(wires) == 4 * width - 1, "complete bank inventory")
    state = dict(wires)
    for gate in gates:
        value = state[tuple(gate[1])]
        if gate[0] == "ccx":
            value &= state[tuple(gate[2])]
        state[tuple(gate[-1])] ^= value
    return state


def guards(width, kind, a, b, target, source):
    require(all(type(v) is int for v in (target, source)), "encoded integers")
    require(type(width) is int and 2 <= width <= MAX_WIDTH, "bounded width")
    require(type(a) is int and type(b) is int and b != 0, "integer fraction")
    q, limit = Q(a, b), 1 << (width - 1)
    require(
        abs(q.numerator) <= 255
        and q.denominator <= 4096
        and q.denominator.bit_count() == 1,
        "bounded dyadic coefficient",
    )
    require(kind in ("add", "scale"), "scalar kind")
    require(-limit <= target < limit and -limit <= source < limit, "signed inputs")
    result = target + q * source if kind == "add" else q * target
    require(result.denominator == 1, "exact common-grid endpoint")
    require(-limit <= result < limit, "signed endpoint")
    if kind == "scale":
        require(
            abs(q.numerator).bit_count() == 1 and q.denominator.bit_count() == 1,
            "power-of-two scale",
        )
        value = -target if q < 0 else target
        require(-limit <= value < limit, "negation prefix range")
        exponent = abs(q.numerator).bit_length() - q.denominator.bit_length()
        require(abs(exponent) <= 12, "bounded scale exponent")
        for _ in range(abs(exponent)):
            require(exponent > 0 or value % 2 == 0, "HALF prefix alignment")
            value = value * 2 if exponent > 0 else value // 2
            require(-limit <= value < limit, "shift prefix range")
        require(value == result, "scale prefix endpoint")
    return int(result)


def counts(gates):
    return {kind: sum(g[0] == kind for g in gates) for kind in ("cx", "ccx")}


def execute(width, kind, a, b, target, source, gates, *, carry=0, scratch=0):
    """Guard the exact endpoint and required zero stock before applying gates."""
    expected = guards(width, kind, a, b, target, source)
    require(carry == scratch == 0, "initially-zero carry and scratch")
    wires = {
        (bank, i): ((value >> i) & 1)
        for bank, value in ((0, target), (1, source), (2, scratch), (3, carry))
        for i in range(width - (bank == 3))
    }
    after = apply(gates, wires, width)
    require(all(after[1, i] == wires[1, i] for i in range(width)), "source return")
    require(
        not any(v for (bank, _), v in after.items() if bank in (2, 3)), "clean return"
    )
    observed = sum(after[0, i] << i for i in range(width))
    require(observed == expected % (1 << width), "exact guarded scalar endpoint")
    return expected
