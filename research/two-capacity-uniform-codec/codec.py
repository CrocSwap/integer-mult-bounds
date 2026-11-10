"""Exact enumerative construction of two-capacity completions.

Produced by Nick Petalas. Apache-2.0.
"""

from dataclasses import dataclass
from itertools import product
from math import isqrt

from count import count
from linear import apply, basis, coordinates, require


def draw_rank(total, bits):
    """Recycle fair bits; return (rank or None, bits consumed) on finite input."""
    require(type(total) is int and 1 <= total < 2**4096, "Invalid sample cardinality")
    require(type(bits) is tuple and len(bits) <= 4096
            and all(type(bit) is int and bit in (0, 1) for bit in bits),
            "Expected at most 4096 canonical bits")
    if total == 1:
        return 0, 0
    width, value = 1, 0
    for used, bit in enumerate(bits, 1):
        width *= 2
        value = 2 * value + bit
        if width >= total:
            if value < total:
                return value, used
            width -= total
            value -= total
        require(0 <= value < width < total, "Invalid residual uniform interval")
    return None, len(bits)


@dataclass(frozen=True)
class Contract:
    n: int
    prime: int
    fixed: tuple
    capacities: tuple

    def __post_init__(self):
        require(type(self.n) is int and 0 <= self.n <= 12, "Dimension outside 0..12")
        p = self.prime
        require(type(p) is int and 2 <= p <= 31
                and all(p % d for d in range(2, isqrt(p) + 1)), "Unsupported prime")
        require(p**self.n <= 4096, "Candidate vector budget exceeds 4096")
        require(type(self.fixed) is tuple and len(self.fixed) <= self.n,
                "Invalid fixed injection")
        require(type(self.capacities) is tuple and len(self.capacities) == 2,
                "Exactly two capacities required")
        for pair in self.fixed:
            require(type(pair) is tuple and len(pair) == 2, "Invalid fixed pair")
            for vector in pair:
                self.check_vector(vector)
        for pair in self.capacities:
            require(type(pair) is tuple and len(pair) == 2, "Invalid capacity pair")
            for rows in pair:
                require(type(rows) is tuple and len(rows) <= self.n, "Invalid subspace basis")
                for vector in rows:
                    self.check_vector(vector)
                require(len(basis(rows, self.n, p)) == len(rows), "Dependent capacity basis")
        for side in range(2):
            require(len(basis(tuple(pair[side] for pair in self.fixed), self.n, p))
                    == len(self.fixed), "Dependent fixed injection")

    def check_vector(self, vector):
        require(type(vector) is tuple and len(vector) == self.n
                and all(type(x) is int and 0 <= x < self.prime for x in vector),
                "Noncanonical field vector")


class Codec:
    def __init__(self, contract):
        require(type(contract) is Contract, "Expected a validated Contract")
        self.contract = contract
        self.count_calls = 0
        self.total = self.weight(contract.fixed)
        domain = tuple(x for x, _ in contract.fixed)
        complement = []
        for i in range(contract.n):
            vector = tuple(int(i == j) for j in range(contract.n))
            if len(basis(domain + tuple(complement) + (vector,), contract.n,
                         contract.prime)) > len(domain) + len(complement):
                complement.append(vector)
        self.complement = tuple(complement)
        require(len(domain) + len(self.complement) == contract.n, "Incomplete domain basis")

    def weight(self, fixed):
        self.count_calls += 1
        c = self.contract
        return count(c.n, c.prime, fixed, c.capacities)

    def branches(self, fixed, source):
        c = self.contract
        images = tuple(y for _, y in fixed)
        for vector in product(range(c.prime), repeat=c.n):
            if len(basis(images + (vector,), c.n, c.prime)) == len(images):
                yield vector, 0
            else:
                yield vector, self.weight(fixed + ((source, vector),))

    def unrank(self, index):
        require(type(index) is int and 0 <= index < self.total, "Rank outside completion set")
        fixed = self.contract.fixed
        for source in self.complement:
            found = False
            for image, weight in self.branches(fixed, source):
                if index < weight:
                    fixed += ((source, image),)
                    found = True
                    break
                index -= weight
            require(found, "Conditional counts do not partition parent")
        require(index == 0, "Nonunit leaf count")
        c = self.contract
        domain = tuple(x for x, _ in fixed)
        images = tuple(y for _, y in fixed)
        columns = []
        for i in range(c.n):
            vector = tuple(int(i == k) for k in range(c.n))
            coefficients = coordinates(domain, vector, c.prime)
            columns.append(tuple(sum(a * y[j] for a, y in zip(coefficients, images)) % c.prime
                                 for j in range(c.n)))
        return tuple(columns)

    def rank(self, columns):
        self.check_completion(columns)
        c, fixed, index = self.contract, self.contract.fixed, 0
        for source in self.complement:
            actual = apply(columns, source, c.prime)
            found = False
            for image, weight in self.branches(fixed, source):
                if image == actual:
                    require(weight > 0, "Completion has zero conditional count")
                    fixed += ((source, image),)
                    found = True
                    break
                index += weight
            require(found, "Missing image branch")
        require(0 <= index < self.total, "Encoded rank outside completion set")
        return index

    def check_completion(self, columns):
        c = self.contract
        require(type(columns) is tuple and len(columns) == c.n, "Invalid matrix columns")
        for vector in columns:
            c.check_vector(vector)
        require(len(basis(columns, c.n, c.prime)) == c.n, "Singular completion")
        require(all(apply(columns, x, c.prime) == y for x, y in c.fixed),
                "Prescribed injection changed")
        for source, target in c.capacities:
            require(all(len(basis(target + (apply(columns, x, c.prime),), c.n,
                                  c.prime)) == len(target) for x in source),
                    "Capacity violated")

    def sample(self, bits):
        """Uniform on success for independent fair bits; report budget exhaustion."""
        require(self.total > 0, "Cannot sample an empty completion set")
        index, used = draw_rank(self.total, bits)
        return (None if index is None else self.unrank(index)), used
