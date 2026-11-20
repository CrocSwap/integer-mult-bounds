"""Apply a bounded streamed multiplier in Fourier coordinates on an original tensor."""

from math import prod
from spectral import fourier_axis
from tensor_word import TensorWord
from word_product import word_product


def live_positions(sizes, widths):
    """Emit physical membership in the original block with one mixed-radix counter."""
    position = [0] * len(sizes)
    outside = 0
    for _ in range(prod(widths)):
        yield outside == 0
        for j, width in enumerate(widths):
            old = position[j]
            new = old + 1
            carry = new == width
            position[j] = 0 if carry else new
            outside += int(position[j] >= sizes[j]) - int(old >= sizes[j])
            if not carry:
                break


class SpectralFilter:
    def __init__(self, sizes, compiler, routes, grid):
        self.sizes = tuple(sizes)
        if not self.sizes or any(type(r) is not int or r < 2 for r in self.sizes):
            raise ValueError("Expected at least one cyclic axis of length two or more")
        axes = [fourier_axis(compiler, r, 1 << (r-1).bit_length(), -1, grid.bits+8)
                for r in self.sizes]
        self.transform = TensorWord(axes, compiler, routes, grid)

    def apply(self, values, multipliers, bound=1):
        """Apply the streamed mask to the live block and restore every incoming hole."""
        widths, grid = self.transform.sides, self.transform.grid
        if len(values) != prod(widths) or type(bound) is not int or bound < 0:
            raise ValueError("Expected a full field and a nonnegative integer modulus bound")
        saved = []
        working = []
        positions = lambda: live_positions(self.sizes, widths)
        for live, value in zip(positions(), values, strict=True):
            if (not isinstance(value, tuple) or len(value) != 2
                    or any(type(v) is not int for v in value)):
                raise ValueError("Expected one complex grid word per physical coordinate")
            if live:
                working.append(value)
            else:
                saved.append(value)
                working.append((0,0))
        data = self.transform.apply(working)
        weights, end = iter(multipliers), object()
        limit2 = (bound*grid.unit)**2
        for j, live in enumerate(positions()):
            if live:
                weight = next(weights, end)
                if (not isinstance(weight, tuple) or len(weight) != 2
                        or any(type(v) is not int for v in weight)):
                    raise ValueError("Expected one complex grid multiplier per frequency")
                a, b = weight
                if word_product(a,a)+word_product(b,b) > limit2:
                    raise ValueError("A Fourier multiplier exceeds the declared bound")
                data[j] = grid.multiply(weight, data[j])
            else:
                data[j] = (0,0)
        if next(weights, end) is not end:
            raise ValueError("The multiplier stream has trailing data")
        data = self.transform.apply(data, opposite=True)
        original_size = prod(self.sizes)
        holes = iter(saved)
        for j, live in enumerate(positions()):
            if live:
                a, b = data[j]
                data[j] = (word_product(original_size,a), word_product(original_size,b))
            else:
                data[j] = next(holes)
        return data
