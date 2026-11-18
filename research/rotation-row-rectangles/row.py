"""Describe and emit a canonical padded-rotation row.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The descriptor uses the closed descent from PR7734 and Petalas's endpoints.
"""

from dataclasses import dataclass

MAX_HEIGHT = 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Row:
    height: int
    depth: int
    rectangles: tuple

    def bit(self, address):
        require(type(address) is int and 0 <= address < 1 << self.height,
                "address outside the row")
        y, t = divmod(address, 1 << self.depth)
        return int(any(t0 <= t < t1 and y0 <= y < y1
                       for t0, t1, y0, y1 in self.rectangles))

    def ones(self):
        return sum((t1 - t0) * (y1 - y0)
                   for t0, t1, y0, y1 in self.rectangles)


def describe(height, modulus, offset, layer):
    require(all(type(v) is int for v in (height, modulus, offset, layer)),
            "integer parameters")
    require(1 <= height <= MAX_HEIGHT, "height outside the executable limit")
    require(1 <= modulus <= 1 << height, "modulus outside the address domain")
    require(0 <= offset < modulus, "offset outside the canonical interval")
    require(0 <= layer < 2 * height - 1, "layer outside the network")
    depth = min(layer, 2 * height - 2 - layer)
    period = 1 << depth
    quotient_a, remainder_a = divmod(offset, period)
    quotient_b, remainder_b = divmod(modulus - offset, period)
    cuts = sorted({0, period, period - remainder_a, remainder_b})
    rectangles = []
    for t0, t1 in zip(cuts, cuts[1:]):
        left = quotient_a + (t0 >= period - remainder_a)
        right = quotient_b + (t0 < remainder_b)
        if not left or not right:
            continue
        total = left + right
        if height - depth == 1:
            y0, y1 = 0, 2
        elif layer == depth:
            if total % 2 == 0 or left % 2 == 0:
                continue
            y0, y1 = total - 1, total + 1
        elif total % 2 == 0:
            if left % 2 == 0:
                continue
            y0, y1 = 0, total
        elif left % 2 == 0:
            y0, y1 = 0, left
        else:
            y0, y1 = left - 1, total + 1
        if rectangles and rectangles[-1][1] == t0 and rectangles[-1][2:] == (y0, y1):
            previous = rectangles.pop()
            rectangles.append((previous[0], t1, y0, y1))
        else:
            rectangles.append((t0, t1, y0, y1))
    return Row(height, depth, tuple(rectangles))


def binary_template(value, stats):
    bits = tuple(int(c) for c in reversed(format(value, "b"))) if value else ()
    stats["template_bits"] += len(bits)
    return bits


class Countdown:
    """Use an empty list for zero and remove the highest zero after a borrow."""

    def __init__(self, template, stats):
        self.bits = list(template)
        self.stats = stats
        stats["counter_bits_copied"] += len(template)

    def take(self):
        if not self.bits:
            return False
        index = 0
        while self.bits[index] == 0:
            self.bits[index] = 1
            self.stats["counter_bit_visits"] += 1
            index += 1
        self.bits[index] = 0
        self.stats["counter_bit_visits"] += 1
        if index == len(self.bits) - 1:
            self.bits.pop()
        return True


def stream(row, stats):
    """Emit current-wire order with amortized constant counter work per bit.

    The counters model bit work. Python instrumentation is not a tape bill.
    """
    stats.update(template_bits=0, counter_bits_copied=0,
                 counter_bit_visits=0, emitted_bits=0, blocks=0, phases=0)
    period = 1 << row.depth
    height = 1 << (row.height - row.depth)
    y_cuts = sorted({0, height, *(y for rect in row.rectangles for y in rect[2:])})
    t_cuts = sorted({0, period, *(t for rect in row.rectangles for t in rect[:2])})
    for y0, y1 in zip(y_cuts, y_cuts[1:]):
        stats["phases"] += 1
        outer = Countdown(binary_template(y1 - y0, stats), stats)
        runs = [(binary_template(t1 - t0, stats),
                 int(any(a <= t0 < b and c <= y0 < d
                         for a, b, c, d in row.rectangles)))
                for t0, t1 in zip(t_cuts, t_cuts[1:])]
        while outer.take():
            stats["blocks"] += 1
            for template, bit in runs:
                inner = Countdown(template, stats)
                while inner.take():
                    stats["emitted_bits"] += 1
                    yield bit
