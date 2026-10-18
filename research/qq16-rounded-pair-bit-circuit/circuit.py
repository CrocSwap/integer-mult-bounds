"""Literal bounded Boolean DAGs for one signed, rounded Gaussian pair.

Gate basis: two-input AND/XOR/OR and one-input NOT. Wires, constants and
fan-out are free. These are irreversible arithmetic circuits, not tape costs.
New material: Nick Petalas, Apache-2.0.
"""

from dataclasses import dataclass

MAX_WIDTH = 4096
MAX_CASES = 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Circuit:
    width: int
    scale: int | None
    inputs: int
    gates: tuple
    outputs: tuple


class Builder:
    def __init__(self, inputs):
        self.inputs = inputs
        self.gates = []

    def gate(self, operation, left, right=0):
        result = self.inputs + 2 + len(self.gates)
        require(0 <= left < result and 0 <= right < result, "noncausal gate")
        self.gates.append((operation, left, right))
        return result

    def add(self, left, right, subtract=False):
        require(len(left) == len(right), "adder width")
        carry = int(subtract)
        result = []
        for a, b in zip(left, right, strict=True):
            if subtract:
                b = self.gate("NOT", b)
            cross = self.gate("XOR", a, b)
            result.append(self.gate("XOR", cross, carry))
            both = self.gate("AND", a, b)
            propagated = self.gate("AND", cross, carry)
            carry = self.gate("XOR", both, propagated)
        return result

    def increment(self, value, carry):
        result = []
        for bit in value:
            result.append(self.gate("XOR", bit, carry))
            carry = self.gate("AND", bit, carry)
        return result

    def mux(self, ordinary, shifted, select):
        difference = self.gate("XOR", ordinary, shifted)
        chosen = self.gate("AND", select, difference)
        return self.gate("XOR", ordinary, chosen)

    def fixed_round(self, value, scale):
        sticky = 0
        for bit in value[:scale]:
            sticky = self.gate("OR", sticky, bit)
        odd_or_sticky = self.gate("OR", sticky, value[scale + 1])
        carry = self.gate("AND", value[scale], odd_or_sticky)
        # One extra sign bit prevents a retained quotient from wrapping.
        retained = value[scale + 1 :] + [value[-1]]
        return [0] * scale + self.increment(retained, carry)

    def variable_round(self, value, controls):
        shifted, sticky = list(value), 0
        size = len(value)
        for stage, select in enumerate(controls):
            distance = 1 << stage
            lost = shifted[0]
            for bit in shifted[1:distance]:
                lost = self.gate("OR", lost, bit)
            enabled = self.gate("AND", select, lost)
            sticky = self.gate("OR", sticky, enabled)
            candidate = shifted[distance:] + [shifted[-1]] * distance
            shifted = [
                self.mux(a, b, select) for a, b in zip(shifted, candidate, strict=True)
            ]
        carry = self.gate("AND", shifted[0], self.gate("OR", sticky, shifted[1]))
        result = self.increment(shifted[1:] + [shifted[-1]], carry)
        for stage, select in enumerate(controls):
            distance = 1 << stage
            candidate = [0] * distance + result[: size - distance]
            result = [
                self.mux(a, b, select) for a, b in zip(result, candidate, strict=True)
            ]
        return result


def gate_count(width, scale=None):
    size = width + 2
    if scale is not None:
        return 52 * size - 4 * scale + 8
    stages = (size - 2).bit_length()
    return 24 * size * stages + 52 * size + 4 * (1 << stages) + 4 * stages + 4


def compile_pair(width, sign, scale=None):
    require(type(width) is int and 1 <= width <= MAX_WIDTH, "input width capacity")
    require(type(sign) is int and sign in (-1, 1), "static sign")
    size = width + 2
    require(
        scale is None or type(scale) is int and 0 <= scale <= size - 2, "scale domain"
    )
    stages = (size - 2).bit_length() if scale is None else 0
    builder = Builder(4 * width + stages)
    values = []
    for component in range(4):
        bits = list(range(2 + component * width, 2 + (component + 1) * width))
        values.append(bits + [bits[-1]] * 2)
    ar, ai, br, bi = values
    sr, si = builder.add(ar, br), builder.add(ai, bi)
    dr, di = builder.add(ar, br, True), builder.add(ai, bi, True)
    raw = (
        builder.add(sr, di, sign == 1),
        builder.add(si, dr, sign == -1),
        builder.add(sr, di, sign == -1),
        builder.add(si, dr, sign == 1),
    )
    controls = list(range(2 + 4 * width, 2 + 4 * width + stages))
    if scale is None:
        outputs = tuple(tuple(builder.variable_round(value, controls)) for value in raw)
    else:
        outputs = tuple(tuple(builder.fixed_round(value, scale)) for value in raw)
    require(len(builder.gates) == gate_count(width, scale), "literal gate invoice")
    require(all(len(value) == size for value in outputs), "output widths")
    return Circuit(width, scale, builder.inputs, tuple(builder.gates), outputs)


def evaluate(circuit, inputs, cases=1):
    """Evaluate one scalar input or up to 65,536 bit-sliced truth assignments."""
    require(type(cases) is int and 1 <= cases <= MAX_CASES, "truth batch capacity")
    require(len(inputs) == circuit.inputs, "input wire count")
    require(
        all(type(v) is int and 0 <= v and v.bit_length() <= cases for v in inputs),
        "input masks",
    )
    mask = (1 << cases) - 1
    wires = [0, mask, *inputs]
    for operation, a, b in circuit.gates:
        if operation == "AND":
            value = wires[a] & wires[b]
        elif operation == "XOR":
            value = wires[a] ^ wires[b]
        elif operation == "OR":
            value = wires[a] | wires[b]
        elif operation == "NOT":
            value = mask ^ wires[a]
        else:
            raise ValueError("unknown gate")
        wires.append(value)
    return tuple(tuple(wires[bit] for bit in value) for value in circuit.outputs)


def run(circuit, values, scale):
    width = circuit.width
    require(type(scale) is int and 0 <= scale <= width, "scale domain")
    require(circuit.scale is None or circuit.scale == scale, "fixed scale mismatch")
    require(
        len(values) == 4
        and all(
            type(v) is int and -(1 << (width - 1)) <= v < 1 << (width - 1)
            for v in values
        ),
        "signed inputs",
    )
    inputs = [(value >> bit) & 1 for value in values for bit in range(width)]
    if circuit.scale is None:
        inputs.extend((scale >> bit) & 1 for bit in range(width.bit_length()))
    result = evaluate(circuit, inputs)
    size = width + 2
    unsigned = [sum(bit << i for i, bit in enumerate(value)) for value in result]
    return tuple(value - ((value >> (size - 1)) << size) for value in unsigned)
