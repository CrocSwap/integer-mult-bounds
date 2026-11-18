"""A reversible draw with runtime residues. Ali Romman, with Codex. Apache-2.0.

The Boolean primitives are Nick Petalas's unchanged PR7746 implementation.
"""

from sources import arithmetic as source

PACKET = tuple(range(11))
COIN = 11
PARAMETER_A = tuple(range(12, 16))
PARAMETER_B = tuple(range(16, 20))
BACKING = tuple(range(20, 31))
FIRST_SCRATCH = 31
MAX_SCRATCH = 8192
READ_ONLY = (COIN, *PARAMETER_A, *PARAMETER_B)
bits = source.bits
add_mod = source.add_mod


class Circuit(source.Circuit):
    """Use the source Boolean primitives with the explicit parameter layout."""

    def __init__(self):
        self.gates = []
        self.next_wire = FIRST_SCRATCH

    def fresh(self):
        if self.next_wire == FIRST_SCRATCH + MAX_SCRATCH:
            raise ValueError('Boolean scratch capacity exceeded')
        wire = self.next_wire
        self.next_wire += 1
        return wire


def doubles(circuit, word):
    result = [word]
    for _ in range(3):
        result.append(add_mod(circuit, result[-1], result[-1]))
    return tuple(result)


def scale(circuit, multiples, parameter):
    terms = tuple(tuple(circuit.both(flag, bit) for bit in word)
                  for word, flag in zip(multiples, parameter, strict=True))
    result = terms[0]
    for term in terms[1:]:
        result = add_mod(circuit, result, term)
    return result


def subtract_mod(circuit, left, right):
    complement = tuple(circuit.xor(bit, True) for bit in (*right, False))
    difference = circuit.add((*left, False), complement, carry=True)
    corrected = circuit.add(difference, bits(169, 9))
    return circuit.select(difference[8], difference[:8], corrected[:8])


def phase_digits(circuit, phase):
    powers = doubles(circuit, phase)
    a_phase = scale(circuit, powers, PARAMETER_A)
    b_phase = scale(circuit, powers, PARAMETER_B)
    a_powers = doubles(circuit, a_phase)
    b_powers = doubles(circuit, b_phase)
    product = scale(circuit, a_powers, PARAMETER_B)
    alpha = add_mod(circuit, add_mod(circuit, a_powers[0], a_powers[2]), a_powers[3])
    beta = add_mod(circuit, add_mod(circuit, b_powers[0], b_powers[2]), b_powers[3])
    residues = (subtract_mod(circuit, subtract_mod(circuit, product, alpha), beta),
                subtract_mod(circuit, beta, product),
                subtract_mod(circuit, alpha, product), product)
    digits = tuple(circuit.add((*residue, False), bits(171, 9))[8] for residue in residues)
    return powers[1], digits


def prefixes(circuit, digits):
    count = bits(0, 3)
    result = []
    for digit in digits:
        result.append(count)
        count = circuit.add(count, (digit, False, False))
    return tuple(result), count


def advance(circuit):
    doubled, digits = phase_digits(circuit, PACKET[:8])
    starts, count = prefixes(circuit, digits)
    rank = (COIN, *PACKET[8:10])
    leaves = tuple(circuit.both(digit, circuit.equal(rank, start))
                   for digit, start in zip(digits, starts, strict=True))
    low = circuit.xor(leaves[1], leaves[3])
    high = circuit.xor(leaves[2], leaves[3])
    done = circuit.xor(circuit.xor(leaves[0], leaves[1]), circuit.xor(leaves[2], leaves[3]))
    complement = tuple(circuit.xor(bit, True) for bit in count)
    node = circuit.add(rank, complement, carry=True)[:2]
    return (*doubled, *circuit.select(done, node, (low, high)), done)


def retreat(circuit):
    doubled = PACKET[:8]
    offset = tuple(circuit.both(doubled[0], bit) for bit in bits(169, 9))
    phase = circuit.add((*doubled, False), offset)[1:]
    _, digits = phase_digits(circuit, phase)
    starts, count = prefixes(circuit, digits)
    low, high, done = PACKET[8:]
    lower = circuit.select(low, starts[0], starts[1])
    upper = circuit.select(low, starts[2], starts[3])
    leaf_rank = circuit.select(high, lower, upper)
    live_rank = circuit.add((low, high, False), count)
    rank = circuit.select(done, live_rank, leaf_rank)
    return (*phase, *rank[1:], False)


def clean_oracle(circuit, output):
    computation = tuple(circuit.gates)
    for target, signal in zip(BACKING, output, strict=True):
        circuit.toggle(target, signal)
    return (*circuit.gates, *reversed(computation))


def reversible_step():
    forward = Circuit()
    first = clean_oracle(forward, advance(forward))
    backward = Circuit()
    last = clean_oracle(backward, retreat(backward))
    swap = tuple(gate for a, b in zip(PACKET, BACKING, strict=True)
                 for gate in ((a, (b,)), (b, (a,)), (a, (b,))))
    return (*first, *swap, *last), max(forward.next_wire, backward.next_wire)
