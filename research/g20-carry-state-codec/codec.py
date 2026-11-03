"""A 24-bit between-row encoding of the PR6503 carry producer.

Produced by Nick Petalas. Apache-2.0.
The quotient tables and carry/packet contract are Ali Romman's PR6503/6474.
"""

from dataclasses import dataclass
from fractions import Fraction
from math import lcm

MAX_STATES = 2406
MAX_ROWS = 65536
MATURE_BASE = 257


def require(condition, message):
    if not condition:
        raise ValueError(message)


def capacity(states):
    require(type(states) is int and 1 <= states <= MAX_STATES, "state count")
    return MATURE_BASE + 4096 * states


def pack_mature(states, quotient, comparisons, residue, high, last):
    capacity(states)
    require(type(quotient) is int and 0 <= quotient < states, "quotient")
    require(type(comparisons) is int and 0 <= comparisons < 256, "comparisons")
    require(type(residue) is int and 0 <= residue < 4, "residue")
    require(type(high) is int and high in (0, 1), "high")
    require(type(last) is int and last in (0, 1), "last")
    return MATURE_BASE + 4096 * quotient + 16 * comparisons + 4 * residue + 2 * high + last


def unpack_mature(states, code):
    limit = capacity(states)
    require(type(code) is int and MATURE_BASE <= code < limit, "mature code")
    quotient, tail = divmod(code - MATURE_BASE, 4096)
    comparisons, tail = divmod(tail, 16)
    residue, tail = divmod(tail, 4)
    high, last = divmod(tail, 2)
    return quotient, comparisons, residue, high, last


def read_bits(data, offset, width):
    require(0 <= width <= 12 and 0 <= offset <= 8 * len(data) - width, "table address")
    start = offset // 8
    stop = (offset + width + 7) // 8
    return (int.from_bytes(data[start:stop], "little") >> (offset % 8)) & ((1 << width) - 1)


@dataclass(frozen=True)
class Model:
    coefficients: tuple
    denominator: int
    digits: tuple
    states: int
    start: int
    width: int
    edge_offset: int
    output_offset: int
    data: bytes

    def digit(self, bitmap):
        return sum(a * ((bitmap >> i) & 1) for i, a in enumerate(self.coefficients))

    def next_quotient(self, state, digit, bit):
        letter = 2 * self.digits.index(digit) + bit
        offset = self.edge_offset + (state * 2 * len(self.digits) + letter) * self.width
        result = read_bits(self.data, offset, self.width)
        require(result < self.states, "table successor")
        return result

    def output(self, state):
        return read_bits(self.data, self.output_offset + 5 * state, 5) - 16


def bind(column, descriptors, data):
    require(len(column) == 8, "eight coefficients")
    require(len(descriptors) == 23 and type(data) is bytes and len(data) == 464866, "table domain")
    denominator = lcm(*(x.denominator for x in column))
    require(denominator in (1, 4), "denominator")
    coefficients = tuple(int(denominator * x) for x in column)
    require(all(abs(x) <= 16 for x in coefficients), "coefficient domain")
    sums = {0}
    for coefficient in coefficients:
        sums |= {x + coefficient for x in tuple(sums)}
    digits = tuple(sorted(sums))
    lo = sum(min(x, 0) for x in coefficients)
    hi = max(0, sum(max(x, 0) for x in coefficients) - 1)
    matches = [d for d in descriptors if d["model"] == [lo, hi, list(digits)]]
    require(len(matches) == 1, "unique source model")
    d = matches[0]
    capacity(d["states"])
    require(d["index_bits"] == (d["states"] - 1).bit_length(), "index width")
    require(0 <= d["start"] < d["states"], "start")
    return Model(coefficients, denominator, digits, d["states"], d["start"],
                 d["index_bits"], d["edge_offset"], d["output_offset"], data)


def decoded(model, code):
    """Return the source state and transition-lookup count; empty is separate."""
    require(type(code) is int and 1 <= code < capacity(model.states), "nonempty code")
    if code < MATURE_BASE:
        bitmap = code - 1
        digit = model.digit(bitmap)
        quotient = model.next_quotient(model.start, digit, 1)
        return (quotient, bitmap, digit % model.denominator, 0, 1, 1), 1
    return (*unpack_mature(model.states, code), 2), 0


def step(model, code, row):
    """Rows encode eight low-input bits then the radix bit in bit position 8."""
    require(type(row) is int and 0 <= row < 512, "binary row")
    require(type(code) is int and 0 <= code < capacity(model.states), "code")
    bitmap, bit = row & 255, row >> 8
    if code == 0:
        require(bit == 1, "odd radix")
        return 1 + bitmap, 0
    (quotient, comparisons, residue, high, last, phase), queries = decoded(model, code)
    digit = model.digit(bitmap)
    quotient = model.next_quotient(quotient, digit, bit)
    comparisons = comparisons & bitmap if bit else comparisons | bitmap
    if phase == 1:
        residue = (residue + 2 * digit) % model.denominator
        high = bit
    return pack_mature(model.states, quotient, comparisons, residue, high, bit), queries + 1


def finish(model, code):
    (quotient, comparisons, residue, high, last, phase), queries = decoded(model, code)
    require(last == 1, "canonical radix ending")
    require(comparisons == 0, "canonical low inputs")
    u = model.output(quotient)
    carry = u - (u - residue * (1 + 2 * high)) % model.denominator
    packet = carry * (4 // model.denominator) + 16
    require(0 <= packet < 32, "packet envelope")
    return packet, queries + 1


def produce(model, rows):
    require(1 <= len(rows) <= MAX_ROWS, "row count")
    code = queries = 0
    for row in rows:
        code, used = step(model, code, row)
        queries += used
    packet, used = finish(model, code)
    require(queries + used == len(rows) + 1, "query invariant")
    return packet, code, queries + used


def source_columns(source):
    """Extract column contracts, without running any predecessor verifier."""
    result = set()
    for basis in ("ports", "scale_free_ports"):
        require(len(source[basis]) == 111, "source ports")
        for record in source[basis]:
            for direction in ("forward", "inverse"):
                require(len(record[direction]) <= 64, "source word length")
                rows = [[Fraction(i == j) for j in range(8)] for i in range(8)]
                for event in record[direction]:
                    require(event[0] in ("ADD", "SCALE"), "source gate")
                    for row in rows:
                        if event[0] == "ADD":
                            row[event[2]] += Fraction(event[-1]) * row[event[1]]
                        else:
                            row[event[1]] *= Fraction(event[-1])
                result.update(zip(*rows))
    return tuple(sorted(result))
