"""Cut the physical paid job into smooth blocks without changing its chart."""

from math import prod

from counted_band import split_runs
from powered import Block, PoweredWord


class SmoothWord(PoweredWord):
    def blocks(self, indices):
        if self.low_cut != self.high_cut:
            raise ValueError("Select the same paid cap for both source classes")
        tags = tuple(self.paid[i].tag for i in indices)
        rank = prod(self.paid[i].rank for i in indices)
        first = 0
        for size, repeats in split_runs(rank, self.low_cut**self.power):
            for _ in range(repeats):
                yield Block(tags, first, size)
                first += size
        if first != rank:
            raise ArithmeticError("The physical slices must cover the complete paid job")
