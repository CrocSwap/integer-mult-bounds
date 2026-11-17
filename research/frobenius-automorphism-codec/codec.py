"""Generator-image codec for local characteristic-power algebras. Apache-2.0."""

from itertools import product
from math import prod

from linear import Field, gl_order, gl_rank, gl_unrank, require


class Codec:
    """No multiplication table is constructed. Bounds apply to the executable."""

    def __init__(self, q, heights):
        self.field = Field(q)
        require(isinstance(heights, tuple) and len(heights) <= 4, "height shape")
        require(all(type(h) is int and 1 <= h <= 6 for h in heights), "height range")
        self.heights = heights
        self.cutoffs = tuple(self.field.p**h for h in heights)
        require(prod(self.cutoffs) <= 64, "algebra dimension capacity")
        self.monomials = tuple(product(*(range(t) for t in self.cutoffs)))
        self.n = len(self.monomials)
        self.units = tuple(self.monomials.index(tuple(int(i == j) for j in range(len(heights))))
                           for i in range(len(heights)))
        self.groups = tuple(tuple(i for i, h in enumerate(heights) if h == e)
                            for e in sorted(set(heights)))
        self.allowed = tuple(tuple(any(a * self.field.p**h >= t
                                      for a, t in zip(exponent, self.cutoffs))
                                   for exponent in self.monomials) for h in heights)
        diagonal = {(i, self.units[j]) for group in self.groups for i in group for j in group}
        self.free = tuple((i, a) for i in range(len(heights)) for a in range(self.n)
                          if self.allowed[i][a] and (i, a) not in diagonal)
        self.block_orders = tuple(gl_order(q, len(group)) for group in self.groups)
        self.order = q**len(self.free) * prod(self.block_orders)

    def unrank(self, index):
        require(type(index) is int and 0 <= index < self.order, "automorphism index")
        images = [[0] * self.n for _ in self.heights]
        for group, block_order in zip(self.groups, self.block_orders):
            index, block_index = divmod(index, block_order)
            block = gl_unrank(self.field, len(group), block_index)
            for i, column in zip(group, block):
                for j, coefficient in zip(group, column):
                    images[i][self.units[j]] = coefficient
        for i, a in self.free:
            index, images[i][a] = divmod(index, self.field.q)
        require(index == 0, "automorphism index was not exhausted")
        return tuple(tuple(image) for image in images)

    def rank(self, images):
        require(isinstance(images, tuple) and len(images) == len(self.heights), "image shape")
        require(all(isinstance(v, tuple) and len(v) == self.n for v in images), "image length")
        for i, image in enumerate(images):
            for a, coefficient in enumerate(image):
                require(type(coefficient) is int and 0 <= coefficient < self.field.q,
                        "coefficient range")
                require(self.allowed[i][a] or coefficient == 0, "power relation violated")
        index, place = 0, 1
        for group, block_order in zip(self.groups, self.block_orders):
            block = tuple(tuple(images[i][self.units[j]] for j in group) for i in group)
            index += place * gl_rank(self.field, block)
            place *= block_order
        for i, a in self.free:
            index += place * images[i][a]
            place *= self.field.q
        require(place == self.order and index < place, "rank range invariant")
        return index
