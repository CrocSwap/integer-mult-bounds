"""Run the balanced CRT tree on a complete tape, including the padded holes."""

from collections import Counter
from math import prod

from compact_crt import CompactSwitch
from streaming_routes import copy_bytes, erase, work_tapes


class CRTTree:
    def __init__(self, sides, widths, public_bits, benes, swap):
        self.sides, self.widths = tuple(sides), tuple(widths)
        self.count = len(sides)
        if not self.count or self.count & (self.count - 1) or len(widths) != self.count:
            raise ValueError("The balanced tree requires a positive dyadic axis count")
        self.benes, self.swap = benes, swap
        self.starts = [0]
        for side, bits in zip(sides, widths, strict=True):
            if not 1 < side < 1 << bits:
                raise ValueError("Every true side must fit its padded field")
            self.starts.append(self.starts[-1] + bits)
        self.L = self.starts[-1]
        self.ell = max(widths)
        self.G = 64 * (self.ell + (public_bits + 1).bit_length())
        self.H = self.L // (100 * self.G) * self.G
        self.stats = Counter()

    def bit_swap(self, source, target, left, right, bits, size):
        low, high = sorted((left, right))
        if high - low < bits:
            raise ValueError("The two complete field intervals must be disjoint")
        self.swap(
            source,
            target,
            bits,
            1 << (self.L - high - bits),
            1 << (high - low - bits),
            (1 << low) * size,
        )

    def controls(self, level, row, group, address):
        """Reconstruct the current left child and read the live Beneš switch."""
        half, last = 1 << (level - 1), self.ell
        restored = {}
        for axis in group:
            start = axis // (2 * half) * (2 * half)
            if start not in restored:
                end = start + half
                full = prod(self.sides[start:end])
                left, prefix = 0, 1
                for i in range(start, end):
                    r = self.sides[i]
                    value = (address >> self.starts[i]) % (1 << self.widths[i])
                    if value >= r:
                        left = 0
                        break
                    quotient = full // r
                    left += value * prefix * quotient * pow(quotient, -1, r)
                    prefix *= r
                restored[start] = left % full
            r = self.sides[axis]
            bits = self.widths[axis]
            word = (address >> self.starts[axis]) % (1 << bits)
            offset = restored[start] * pow(prod(self.sides[start:axis]), -1, r) % r
            permutation = tuple((x + offset) % r if x < r else x for x in range(1 << bits))
            local = row if row < bits else row - 2 * (last - bits)
            yield self.benes(permutation)[local][1][word]

    def jobs(self, level, row):
        half = 1 << (level - 1)
        targets = []
        for axis, bits in enumerate(self.widths):
            if not axis & half or bits <= row < 2 * self.ell - bits:
                continue
            index = row if row < bits else row - 2 * (self.ell - bits)
            targets.append((axis, self.starts[axis] + min(index, 2 * bits - 2 - index)))
        if self.count < 4 or self.H < self.G or self.count < 51200:
            for axis, pos in targets:
                yield None, [(axis, pos)]
            return
        if half == self.count // 2:
            chunks = [
                (self.count // 2, 3 * self.count // 4, 3 * self.count // 4, self.count),
                (3 * self.count // 4, self.count, self.count // 2, 3 * self.count // 4),
            ]
        else:
            chunks = [
                (0, self.count // 2, self.count // 2, self.count),
                (self.count // 2, self.count, 0, self.count // 2),
            ]
        cap = self.H // self.G
        for start, end, front, back in chunks:
            selected = [(i, j) for i, j in targets if start <= i < end]
            a, b = max(self.H, self.starts[front]), min(self.L - 2 * self.H, self.starts[back])
            for first in range(0, len(selected), cap):
                group = selected[first : first + cap]
                if b - a < 3 * self.H:
                    # This geometry stays in the finite individual-bit regime.
                    for target in group:
                        yield None, [target]
                else:
                    yield (a, a + self.H, a + 2 * self.H), group

    def apply(self, source, target, record_bytes, reverse=False):
        total = (1 << self.L) * record_bytes
        H, K = self.H, 64 * self.G
        with work_tapes(3) as (a, b, tmp):
            copy_bytes(source, a, total)

            def step(op):
                nonlocal a, b
                a.seek(0)
                op(a, b)
                erase(a)
                a, b = b, a

            def swap_bits(left, right, width):
                if left != right:
                    step(lambda s, d: self.bit_swap(s, d, left, right, width, record_bytes))

            levels = range(1, self.count.bit_length())
            layers = range(2 * self.ell - 1)
            for level in reversed(levels) if reverse else levels:
                for row in reversed(layers) if reverse else layers:
                    for locations, group in self.jobs(level, row):
                        # List positions in increasing order of physical significance.
                        order = list(range(self.L))
                        exchanges = (
                            []
                            if locations is None
                            else list(zip(locations, (self.L - H, self.L - 2 * H, 0), strict=True))
                        )
                        for lo, hi in exchanges:
                            swap_bits(lo, hi, H)
                            order[lo : lo + H], order[hi : hi + H] = (
                                order[hi : hi + H],
                                order[lo : lo + H],
                            )
                        inverse = [0] * self.L
                        for i, original in enumerate(order):
                            inverse[original] = i

                        def original(index):
                            return sum(((index >> i) & 1) << j for i, j in enumerate(order))

                        colors = {}
                        singles = []
                        ywidth = self.L - 3 * H
                        for axis, pos in group:
                            bit = inverse[pos]
                            if locations is None or bit - H + K > ywidth:
                                singles.append((axis, bit))
                            else:
                                if bit < H:
                                    raise ArithmeticError("A CRT target entered its own reservoir")
                                colors.setdefault((bit - H) % K, []).append((axis, bit - H))
                        for color in colors.values():
                            axes, positions = zip(*sorted(color, key=lambda x: x[1]), strict=True)

                            def controls(y):
                                return self.controls(level, row, axes, original(y << H))

                            macro = CompactSwitch(H, ywidth, self.G, K, positions, controls)
                            step(lambda s, d: macro.apply(s, d, record_bytes, self.swap))
                            self.stats.update(macro.stats)
                        for axis, bit in singles:
                            # Move this bit to the end of y. Keep all omitted back bits.
                            dest = H if locations is not None else 0
                            swap_bits(bit, dest, 1)

                            def single(src, out):
                                for prefix in range(1 << (self.L - dest - 1)):
                                    addr = prefix << (dest + 1)
                                    if ((addr >> bit) ^ (addr >> dest)) & 1:
                                        addr ^= (1 << bit) ^ (1 << dest)
                                    (flip,) = self.controls(level, row, (axis,), original(addr))
                                    CompactSwitch.rotation(
                                        src, out, tmp, 2, (1 << dest) * record_bytes, flip
                                    )

                            step(single)
                            swap_bits(bit, dest, 1)
                            self.stats["single_targets"] += 1
                        for lo, hi in reversed(exchanges):
                            swap_bits(lo, hi, H)
            a.seek(0)
            copy_bytes(a, target, total)
