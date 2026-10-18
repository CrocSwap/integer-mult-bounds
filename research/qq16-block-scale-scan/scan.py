"""Literal block-scale Boolean DAG. Arham Tahir / Codex. Apache-2.0."""
from dataclasses import dataclass

MAX_WIDTH = 4096
MAX_COMPONENTS = 1024
MAX_INPUT_BITS = 65536
MAX_CASES = 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Circuit:
    width: int
    components: int
    reserve: int
    gates: tuple
    exponent: tuple
    zero: int
    admissible: int


def popcount_sum(count):
    """Sum popcount(i), 0 <= i < count, without enumerating count rows."""
    require(type(count) is int and count >= 0, "popcount domain")
    answer = 0
    while count:
        top = count.bit_length() - 1
        power = 1 << top
        answer += top * (power >> 1) + count - power
        count -= power
    return answer


def gate_count(width, components, reserve):
    require(type(width) is int and width >= 1, "width")
    require(type(components) is int and components >= 1, "components")
    require(type(reserve) is int and 0 <= reserve < width, "reserve")
    return width * (4 * components + 2) - 2 * reserve + popcount_sum(width - reserve) + 3


def compile_scan(width, components, reserve):
    gate_count(width, components, reserve)
    require(width <= MAX_WIDTH, "width capacity")
    require(components <= MAX_COMPONENTS, "component capacity")
    require(width * components <= MAX_INPUT_BITS, "input bit capacity")
    inputs = width * components
    gates = []

    def gate(operation, a, b=0):
        result = 2 + inputs + len(gates)
        require(0 <= a < result and 0 <= b < result, "noncausal gate")
        gates.append((operation, a, b))
        return result

    magnitudes = []
    for component in range(components):
        raw = list(range(2 + component * width, 2 + (component + 1) * width))
        sign = raw[-1]
        carry = sign
        magnitude = []
        for bit in raw:
            complemented = gate("XOR", bit, sign)
            magnitude.append(gate("XOR", complemented, carry))
            carry = gate("AND", complemented, carry)
        magnitudes.append(magnitude)
    aggregate = list(magnitudes[0])
    for magnitude in magnitudes[1:]:
        aggregate = [gate("OR", a, b) for a, b in zip(aggregate, magnitude, strict=True)]
    seen = 0
    exponent = [0] * width.bit_length()
    for index in range(width - 1, reserve - 1, -1):
        hit = gate("AND", aggregate[index], gate("NOT", seen))
        seen = gate("OR", seen, aggregate[index])
        for bit in range(len(exponent)):
            if ((index - reserve) >> bit) & 1:
                exponent[bit] = gate("OR", exponent[bit], hit)
    low = 0
    for bit in aggregate[:reserve]:
        low = gate("OR", low, bit)
    zero = gate("NOT", gate("OR", seen, low))
    admissible = gate("OR", seen, zero)
    require(len(gates) == gate_count(width, components, reserve), "literal invoice")
    return Circuit(width, components, reserve, tuple(gates), tuple(exponent), zero, admissible)


def evaluate(circuit, inputs, cases=1):
    """Bit-sliced evaluator: exponent bits, zero and admissibility."""
    require(type(cases) is int and 1 <= cases <= MAX_CASES, "case capacity")
    require(len(inputs) == circuit.width * circuit.components, "input count")
    require(all(type(v) is int and v >= 0 and v.bit_length() <= cases for v in inputs), "input masks")
    mask = (1 << cases) - 1
    wires = [0, mask, *inputs]
    for operation, a, b in circuit.gates:
        if operation == "AND":
            value = wires[a] & wires[b]
        elif operation == "OR":
            value = wires[a] | wires[b]
        elif operation == "XOR":
            value = wires[a] ^ wires[b]
        elif operation == "NOT":
            value = mask ^ wires[a]
        else:
            raise ValueError("unknown gate")
        wires.append(value)
    return tuple(wires[i] for i in (*circuit.exponent, circuit.zero, circuit.admissible))


def run(circuit, values):
    require(len(values) == circuit.components, "component count")
    width = circuit.width
    require(all(type(v) is int and -(1 << (width - 1)) <= v < 1 << (width - 1) for v in values), "signed inputs")
    result = evaluate(circuit, [(v >> i) & 1 for v in values for i in range(width)])
    return sum(v << i for i, v in enumerate(result[:-2])), result[-2], result[-1]
