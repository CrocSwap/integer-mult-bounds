"""Finite macro reference for the declared batched order, not a fast backend.

Python arrays and integers implement an exact semantic oracle here. The written
construction uses the source-bound fixed-tape C routine and paid reversible
history; this reference does not emit or time that machine.
"""
from dataclasses import dataclass


def need(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Plan:
    n: int
    rank: int
    d: int
    spacing: int
    suffix: int

    def __post_init__(self):
        need(all(type(x) is int for x in (self.n, self.rank, self.d, self.spacing, self.suffix)), "integer plan fields")
        need(1 <= self.rank <= self.n <= 12 and self.d >= 1 and self.spacing >= 1 and
             0 <= self.suffix <= self.rank, "finite reference plan domain")

    def blocks(self):
        chunks = (self.rank-self.suffix)//self.spacing
        result = []
        for first in range(0, chunks, self.d):
            height = min(self.d, chunks-first)
            for offset in range(self.spacing):
                result.append(tuple(self.suffix+(first+j)*self.spacing+offset for j in range(height)))
        return tuple(result)

    def direct(self):
        stop = self.suffix+((self.rank-self.suffix)//self.spacing)*self.spacing
        return tuple(range(stop, self.rank))+tuple(range(self.suffix))

    def order(self):
        return tuple(axis for block in self.blocks() for axis in block)+self.direct()


def pair(a, b, inverse=False):
    """Independent spelling of the credited signed floor lift."""
    real, imag = a[0]-b[0], a[1]-b[1]
    mean = (b[0]+real//2, b[1]+imag//2)
    real, imag = (imag, -real) if inverse else (-imag, real)
    low = (mean[0]-real//2, mean[1]-imag//2)
    return (low[0]+real, low[1]+imag), low


def lifted(values, axes, inverse=False):
    result = list(values)
    for axis in reversed(axes) if inverse else axes:
        step = 1 << axis
        for start in range(0, len(result), 2*step):
            for at in range(start, start+step):
                result[at], result[at+step] = pair(result[at], result[at+step], inverse)
    return result


def linear_numerators(values, axes, inverse=False):
    """Exact U numerator over denominator2**len(axes), with no floors."""
    result = list(values)
    for axis in axes:
        step = 1 << axis
        for start in range(0, len(result), 2*step):
            for at in range(start, start+step):
                a, b = result[at], result[at+step]
                total = (a[0]+b[0], a[1]+b[1])
                difference = (a[0]-b[0], a[1]-b[1])
                turn = (difference[1], -difference[0]) if inverse else (-difference[1], difference[0])
                result[at] = (total[0]+turn[0], total[1]+turn[1])
                result[at+step] = (total[0]-turn[0], total[1]-turn[1])
    return result


def scaled(values, axes, inverse=False, guard=None):
    k = len(axes)
    g = k//2+1 if guard is None else guard
    need(0 <= g <= k, "finite scaled guard")
    denominator = 1 << (k-g)
    result = linear_numerators(values, axes, inverse)
    need(all(a % denominator == b % denominator == 0 for a, b in result), "exact scaled Gaussian output")
    return [(a//denominator, b//denominator) for a, b in result]


def encode(values, width):
    limit = 1 << (width-1)
    need(all(-limit <= value < limit for z in values for value in z), "finite signed word headroom")
    return [(a % (2*limit), b % (2*limit)) for a, b in values]


def decode(values, width):
    limit = 1 << (width-1)
    return [(a if a < limit else a-2*limit, b if b < limit else b-2*limit) for a, b in values]


def xor_words(left, right):
    return [(a ^ c, b ^ d) for (a, b), (c, d) in zip(left, right, strict=True)]


class DirectOracle:
    """Function-level XOR oracle; no fast execution or history trace claim."""
    def __init__(self):
        self.calls = []

    def apply(self, source, target, axes, width, inverse=False):
        self.calls.append((tuple(axes), inverse))
        return xor_words(target, encode(scaled(source, axes, inverse), width))


def evaluate(source, target, axes, width, oracle, inverse=False, omit_cleanup=False):
    """Source-preserving B_k XOR evaluator with explicit private macro cleanup."""
    saved_source = tuple(source)
    g = len(axes)//2+1
    quotient = [(a >> g, b >> g) for a, b in source]
    residues = [(a % (1 << g), b % (1 << g)) for a, b in source]
    zero = [(0, 0)]*len(source)
    wide = oracle.apply(quotient, zero, axes, width, inverse)
    narrow = lifted(residues, axes, inverse)
    value = [(a+c, b+d) for (a, b), (c, d) in zip(decode(wide, width), narrow, strict=True)]
    result = xor_words(target, encode(value, width))
    returned_residues = lifted(narrow, axes, not inverse)
    need(returned_residues == residues, "literal narrow inverse restores residues")
    if not omit_cleanup:
        wide = oracle.apply(quotient, wide, axes, width, inverse)
    need(wide == zero, "backend private output must return zero")
    need(tuple(source) == saved_source, "borrowed source preserved")
    # XOR-uncopy the restored split fields against the same retained input.
    quotient = [(a ^ (x >> g), b ^ (y >> g)) for (a, b), (x, y) in zip(quotient, source, strict=True)]
    residues = [(a ^ (x % (1 << g)), b ^ (y % (1 << g))) for (a, b), (x, y) in zip(returned_residues, source, strict=True)]
    need(quotient == residues == zero, "split fields return zero")
    return result


def inplace_block(source, axes, width, oracle, inverse=False):
    zero = [(0, 0)]*len(source)
    output = evaluate(source, zero, axes, width, oracle, inverse)
    old = evaluate(decode(output, width), encode(source, width), axes, width, oracle, not inverse)
    need(old == zero, "inverse evaluator clears old bank before swap")
    return decode(output, width)


def execute(values, plan, width, inverse=False):
    need(len(values) == 1 << plan.n, "complete ambient payload")
    result, oracle = list(values), DirectOracle()
    if inverse:
        result = lifted(result, plan.direct(), True)
    for block in reversed(plan.blocks()) if inverse else plan.blocks():
        result = inplace_block(result, block, width, oracle, inverse)
    if not inverse:
        result = lifted(result, plan.direct())
    return result, oracle.calls
