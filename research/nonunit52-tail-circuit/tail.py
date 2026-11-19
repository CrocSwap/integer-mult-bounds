"""One reversible draw for complementary tails. Ali Romman, with Codex. Apache-2.0."""

from sources import arithmetic as source

PACKET = tuple(range(7))
COIN = 7
PARAMETER_U = tuple(range(8, 12))
PARAMETER_V = tuple(range(12, 16))
ORIENTATION = 16
MIXED = 17
BACKING = tuple(range(18, 25))
FIRST_SCRATCH = 25
READ_ONLY = (COIN, *PARAMETER_U, *PARAMETER_V, ORIENTATION, MIXED)
bits = source.bits


class Circuit(source.Circuit):
    """Use the unchanged Boolean primitives with an explicit tail layout."""

    def __init__(self):
        self.gates = []
        self.next_wire = FIRST_SCRATCH

    def fresh(self):
        if self.next_wire == FIRST_SCRATCH + 4096:
            raise ValueError('Boolean scratch capacity exceeded')
        wire = self.next_wire
        self.next_wire += 1
        return wire


def add_mod(circuit, left, right):
    total = circuit.add((*left, False), (*right, False))
    reduced = circuit.add(total, bits(19, 5))
    return circuit.select(reduced[4], reduced[:4], total[:4])


def scale(circuit, powers, parameter):
    terms = [tuple(circuit.both(flag, bit) for bit in word)
             for word, flag in zip(powers, parameter, strict=True)]
    result = terms[0]
    for term in terms[1:]:
        result = add_mod(circuit, result, term)
    return result


def advance(circuit):
    powers = [PACKET[:4]]
    for _ in range(3):
        powers.append(add_mod(circuit, powers[-1], powers[-1]))
    residues = [scale(circuit, powers, parameter) for parameter in (PARAMETER_U, PARAMETER_V)]
    du, dv = [circuit.add((*word, False), bits(9, 5))[4] for word in residues]
    row_low = circuit.select(COIN, (du,), (dv,))[0]
    swap = circuit.both(du, circuit.xor(dv, True))
    column = circuit.xor(COIN, swap)
    column_high = circuit.select(column, (du,), (dv,))[0]
    mixed_label = circuit.select(ORIENTATION, (row_low, COIN), (column, column_high))
    endpoint_label = circuit.select(ORIENTATION, (du, False), (False, du))
    leaf = circuit.select(MIXED, endpoint_label, mixed_label)
    stop = circuit.select(MIXED, (circuit.xor(COIN, True),),
                          (circuit.xor(PACKET[4], True),))[0]
    live = (circuit.both(MIXED, COIN), False)
    return (*powers[1], *circuit.select(stop, live, leaf), stop)


def retreat(circuit):
    doubled = PACKET[:4]
    offset = tuple(circuit.both(doubled[0], bit) for bit in bits(13, 5))
    phase = circuit.add((*doubled, False), offset)[1:]
    node = circuit.both(MIXED, circuit.xor(PACKET[6], True))
    return (*phase, node, False, False)


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


def recipe(a, b):
    if any(type(value) is not int or not 0 <= value < 52 for value in (a, b)):
        raise ValueError('residue outside [0,51]')
    if (a % 13 == 0) == (b % 13 == 0):
        raise ValueError('not a nonempty nonunit tail')
    orientation = int(b % 13 == 0)
    multiple, other = (b, a) if orientation else (a, b)
    if multiple == 0:
        u = 4 * other % 13
        return dict(mixed=0, orientation=orientation, u=u, v=u)
    t = multiple // 13
    return dict(mixed=1, orientation=orientation, u=(4-t)*other % 13, v=t*other % 13)
