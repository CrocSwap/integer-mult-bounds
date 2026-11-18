"""Execute the generated gates and compare all wires to signed integer arithmetic."""

from collections import Counter
from itertools import batched, product
from random import Random

from circuit import compile_row


def check_batch(width, size, gates, cases):
    """Each bit of a Python integer simulates one independent circuit input."""
    states = [0] * size
    expected_outputs = [0] * (width + 1)
    limit = 1 << (width - 1)
    for lane, (donors, target, diagnostic) in enumerate(cases):
        for port, value in enumerate((*donors, target)):
            for bit in range(width):
                states[port * width + bit] |= ((value >> bit) & 1) << lane
        states[9 * width] |= diagnostic << lane
        numerator = sum(donors[:4]) - sum(donors[4:])
        quotient, remainder = divmod(numerator, 2)
        invalid = bool(remainder or not -limit <= quotient < limit)
        for bit in range(width):
            expected_outputs[bit] |= (((target ^ quotient) >> bit) & 1) << lane
        expected_outputs[-1] |= (diagnostic ^ invalid) << lane
    expected = states.copy()
    expected[8 * width:9 * width + 1] = expected_outputs
    for gate in gates:
        flip = states[gate[0]]
        if len(gate) == 3:
            flip &= states[gate[1]]
        states[gate[-1]] ^= flip
    if states != expected:
        raise ValueError("gate output differs from the full expected wire state")


def cases_for(width):
    limit = 1 << (width - 1)
    if width <= 2:
        for values in product(range(-limit, limit), repeat=8):
            # Targets are XOR outputs. Cover every donor configuration.
            yield values, sum(values) % (2 * limit) - limit, values[0] & 1
        return
    low, high = -limit, limit - 1
    for numerator in (-1, 0, 1, 2):
        yield (numerator,) + (0,) * 7, numerator // 2, 0
    for value in (low, high):
        yield (value, value, 0, 0, 0, 0, 0, 0), value, 0
        opposite = -1 - value
        quotient = 2 * (value - opposite)
        wrapped = (quotient + limit) % (2 * limit) - limit
        yield (value,) * 4 + (opposite,) * 4, wrapped, 0
    rng = Random(88937)
    for _ in range(24):
        words = [rng.randrange(low, high + 1) for _ in range(9)]
        yield tuple(words[:8]), words[8], rng.randrange(2)


def main():
    for width in (1, 2, 1076):
        size, gates = compile_row(width)
        counts = Counter(map(len, gates))
        for gate in gates:
            if (len(gate) not in (2, 3) or len(set(gate)) != len(gate)
                    or min(gate) < 0 or max(gate) >= size or gate[-1] < 8 * width):
                raise ValueError(f"illegal gate {gate}")
        work = size - 9 * width - 1
        if (len(gates), work) != (87 * width + 199, 14 * width + 39):
            raise ValueError("emitted gate or workspace count differs from the proof")
        checked = 0
        for batch in batched(cases_for(width), 256):
            check_batch(width, size, gates, batch)
            checked += len(batch)
        print(f"w={width} cases={checked} CNOT={counts[2]} Toffoli={counts[3]} "
              f"total={len(gates)} work={size - 9 * width - 1}")
    print("PASS_HALF_SUM_CLEAR")


if __name__ == "__main__":
    main()
