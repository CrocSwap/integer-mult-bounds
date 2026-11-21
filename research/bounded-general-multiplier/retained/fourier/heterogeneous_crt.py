"""Run balanced CRT switch programs on dyadic sides of different widths."""

from math import gcd, prod


def local_switch_row(max_width, width, global_row):
    """Return the true Beneš row, or None when the local network is idle."""
    if not 1 <= width <= max_width or not 0 <= global_row < 2 * max_width - 1:
        raise ValueError("Invalid global or local switch index")
    if global_row < width:
        return global_row
    if global_row >= 2 * max_width - width:
        return global_row - 2 * (max_width - width)
    return None


class HeterogeneousCRT:
    """An executable address map with the full set of declared side widths.

    The caller supplies the retained one-axis Beneš compiler. The cached
    controls keep the small integration checks practical. The complete-tape
    construction generates controls per paid fiber.
    """

    def __init__(self, sides, widths, compiler):
        self.sides = tuple(sides)
        self.widths = tuple(widths)
        self.count = len(self.sides)
        if not self.count or self.count & (self.count - 1) or len(self.widths) != self.count:
            raise ValueError("Use a power-of-two count of declared sides")
        prefix = 1
        for side, width in zip(self.sides, self.widths, strict=True):
            if width < 1 or not 2 <= side <= 1 << width or gcd(prefix, side) != 1:
                raise ValueError("Use pairwise coprime sides within their declared target")
            prefix *= side
        self.max_width = max(self.widths)
        self.compiler = compiler
        self.tables = {}

    def network(self, width, side, offset):
        key = width, side, offset
        if key not in self.tables:
            permutation = tuple((x + offset) % side if x < side else x for x in range(1 << width))
            self.tables[key] = self.compiler(permutation)
        return self.tables[key]

    def offset_programs(self, state, level):
        """Freeze the level's offsets on unchanged left-child coordinates."""
        programs = []
        size = 1 << level
        for start in range(0, self.count, size):
            middle = start + size // 2
            left = self.sides[start:middle]
            left_size = prod(left)
            restored = 0
            prefix = 1
            if all(state[start + j] < side for j, side in enumerate(left)):
                for j, side in enumerate(left):
                    complement = left_size // side
                    restored += (state[start + j] * prefix * complement
                                 * pow(complement, -1, side))
                    prefix *= side
                restored %= left_size
            prefix = left_size
            for axis in range(middle, start + size):
                side = self.sides[axis]
                width = self.widths[axis]
                offset = restored * pow(prefix, -1, side) % side
                programs.append((axis, width, self.network(width, side, offset)))
                prefix *= side
        return programs

    def route(self, coordinates, reverse=False):
        if len(coordinates) != self.count or any(not 0 <= x < 1 << w
                for x, w in zip(coordinates, self.widths, strict=True)):
            raise ValueError("Coordinate outside the declared rectangle")
        state = list(coordinates)
        levels = range(1, self.count.bit_length())
        rows = range(2 * self.max_width - 1)
        if reverse:
            levels = levels[::-1]
            rows = rows[::-1]
        for level in levels:
            programs = self.offset_programs(state, level)
            for global_row in rows:
                for axis, width, network in programs:
                    row = local_switch_row(self.max_width, width, global_row)
                    if row is not None:
                        bit, table = network[row]
                        state[axis] ^= table[state[axis]] << bit
        return tuple(state)
