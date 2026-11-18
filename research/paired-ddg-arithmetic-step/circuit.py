"""Reversible arithmetic for one draw of the fixed (1/13, 1/13) sampler."""

type Signal = int | bool
type Word = tuple[Signal, ...]
type Gate = tuple[int, tuple[int, ...]]

PACKET_WIDTH = 11
COIN_WIRE = PACKET_WIDTH
PACKET = tuple(range(PACKET_WIDTH))
BACKING = tuple(range(COIN_WIRE + 1, COIN_WIRE + 1 + PACKET_WIDTH))
FIRST_SCRATCH = BACKING[-1] + 1
MAX_SCRATCH = 2048
MODULUS = 169


class Circuit:
    """Allocate one zero wire per intermediate Boolean value."""

    def __init__(self) -> None:
        self.gates: list[Gate] = []
        self.next_wire = FIRST_SCRATCH

    def fresh(self) -> int:
        if self.next_wire == FIRST_SCRATCH + MAX_SCRATCH:
            raise ValueError("Boolean scratch capacity exceeded")
        wire = self.next_wire
        self.next_wire += 1
        return wire

    def toggle(self, target: int, signal: Signal) -> None:
        if signal is True:
            self.gates.append((target, ()))
        elif signal is not False:
            self.gates.append((target, (signal,)))

    def xor(self, left: Signal, right: Signal) -> Signal:
        if left is False or right is False:
            return right if left is False else left
        if type(left) is type(right) and left == right:
            return False
        target = self.fresh()
        self.toggle(target, left)
        self.toggle(target, right)
        return target

    def both(self, left: Signal, right: Signal) -> Signal:
        if left is False or right is False:
            return False
        if left is True or right is True:
            return right if left is True else left
        if left == right:
            return left
        target = self.fresh()
        self.gates.append((target, (left, right)))
        return target

    def add(self, left: Word, right: Word, carry: Signal = False) -> Word:
        if len(left) != len(right) or not 1 <= len(left) <= 9:
            raise ValueError("invalid ripple adder widths")
        total = []
        for x, y in zip(left[:-1], right[:-1], strict=True):
            difference = self.xor(x, y)
            total.append(self.xor(difference, carry))
            carry = self.xor(self.both(x, y), self.both(difference, carry))
        total.append(self.xor(self.xor(left[-1], right[-1]), carry))
        return tuple(total)

    def select(self, flag: Signal, low: Word, high: Word) -> Word:
        if len(low) != len(high) or not 1 <= len(low) <= 8:
            raise ValueError("invalid selector widths")
        return tuple(
            self.xor(x, self.both(flag, self.xor(x, y)))
            for x, y in zip(low, high, strict=True)
        )

    def equal(self, left: Word, right: Word) -> Signal:
        if len(left) != len(right) or len(left) != 3:
            raise ValueError("invalid index widths")
        equal: Signal = True
        for x, y in zip(left, right, strict=True):
            equal = self.both(equal, self.xor(self.xor(x, y), True))
        return equal


def bits(value: int, width: int) -> Word:
    if not 1 <= width <= 9 or not 0 <= value < 1 << width:
        raise ValueError("constant does not fit its word")
    return tuple(bool(value & (1 << index)) for index in range(width))


def add_mod(circuit: Circuit, left: Word, right: Word) -> Word:
    total = circuit.add((*left, False), (*right, False))
    reduced = circuit.add(total, bits(512 - MODULUS, 9))
    return circuit.select(reduced[8], reduced[:8], total[:8])


def phase_digits(circuit: Circuit, phase: Word, doubled: Word) -> tuple[Signal, Signal, Signal]:
    triple = add_mod(circuit, doubled, phase)
    six = add_mod(circuit, triple, triple)
    twelve = add_mod(circuit, six, six)
    twenty_four = add_mod(circuit, twelve, twelve)
    twenty_five = add_mod(circuit, twenty_four, phase)

    threshold = bits(256 - 85, 9)
    high_25 = circuit.add((*twenty_five, False), threshold)[8]
    high_12 = circuit.add((*twelve, False), threshold)[8]
    high_1 = circuit.add((*phase, False), threshold)[8]
    return circuit.xor(high_25, True), high_12, high_1


def prefix_indices(circuit: Circuit, first: Signal, middle: Signal) -> tuple[Word, Word, Word]:
    return (first, False, False), (circuit.xor(first, True), first, False), (first, middle, False)


def advance(circuit: Circuit) -> Word:
    phase = PACKET[:8]
    doubled = add_mod(circuit, phase, phase)
    first, middle, last = phase_digits(circuit, phase, doubled)
    rank = (COIN_WIRE, *PACKET[8:10])
    p01, p10, p11 = prefix_indices(circuit, first, middle)
    leaf_00 = circuit.both(first, circuit.equal(rank, bits(0, 3)))
    leaf_01 = circuit.both(middle, circuit.equal(rank, p01))
    leaf_10 = circuit.both(middle, circuit.equal(rank, p10))
    leaf_11 = circuit.both(last, circuit.equal(rank, p11))
    low = circuit.xor(leaf_01, leaf_11)
    high = circuit.xor(leaf_10, leaf_11)
    done = circuit.xor(circuit.xor(leaf_00, leaf_01), circuit.xor(leaf_10, leaf_11))

    count = circuit.add((first, middle, False), (last, False, False))
    complement = tuple(circuit.xor(bit, True) for bit in count)
    index = circuit.add(rank, complement, carry=True)[:2]
    return (*doubled, *circuit.select(done, index, (low, high)), done)


def retreat(circuit: Circuit) -> Word:
    doubled = PACKET[:8]
    offset = tuple(circuit.both(doubled[0], bit) for bit in bits(MODULUS, 9))
    phase = circuit.add((*doubled, False), offset)[1:]
    first, middle, last = phase_digits(circuit, phase, doubled)
    low, high, done = PACKET[8:]
    p01, p10, p11 = prefix_indices(circuit, first, middle)
    lower = circuit.select(low, bits(0, 3), p01)
    upper = circuit.select(low, p10, p11)
    leaf_rank = circuit.select(high, lower, upper)

    count = circuit.add((first, middle, False), (last, False, False))
    live_rank = circuit.add((low, high, False), count)
    rank = circuit.select(done, live_rank, leaf_rank)
    return (*phase, *rank[1:], False)


def clean_oracle(circuit: Circuit, output: Word) -> tuple[Gate, ...]:
    computation = tuple(circuit.gates)
    for target, signal in zip(BACKING, output, strict=True):
        circuit.toggle(target, signal)
    return (*circuit.gates, *reversed(computation))


def reversible_step() -> tuple[tuple[Gate, ...], int]:
    forward = Circuit()
    forward_oracle = clean_oracle(forward, advance(forward))
    backward = Circuit()
    backward_oracle = clean_oracle(backward, retreat(backward))
    swap = tuple(
        gate
        for a, b in zip(PACKET, BACKING, strict=True)
        for gate in ((a, (b,)), (b, (a,)), (a, (b,)))
    )
    scratch_end = max(forward.next_wire, backward.next_wire)
    return (*forward_oracle, *swap, *backward_oracle), scratch_end
