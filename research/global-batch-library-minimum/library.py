"""Finite exact batching libraries. See README.md for the unbounded theorem."""
from math import gcd, lcm

MAX_RANKS = 32
MAX_BATCHES = 32
MAX_INPUT = 65535


def positive(value: int) -> bool:
    return type(value) is int and 1 <= value <= MAX_INPUT


def validate(bases: tuple, levels: tuple) -> None:
    """Validate once at the public system boundary; internal helpers trust it."""
    if not isinstance(bases, tuple) or not 1 <= len(bases) <= MAX_RANKS:
        raise ValueError("bases must be a nonempty bounded tuple")
    if not all(positive(value) for value in bases):
        raise ValueError("base widths must be bounded positive integers")
    if not isinstance(levels, tuple) or len(bases) + len(levels) > MAX_RANKS:
        raise ValueError("too many levels or wrong container")
    for offset, level in enumerate(levels):
        if not isinstance(level, tuple) or len(level) != 2:
            raise ValueError("level must be a source-count/batches pair")
        sources, batches = level
        if not positive(sources):
            raise ValueError("source count must be a bounded positive integer")
        if not isinstance(batches, tuple) or len(batches) > MAX_BATCHES:
            raise ValueError("batches must be a bounded tuple")
        rank = len(bases) + offset
        for batch in batches:
            if not isinstance(batch, tuple) or len(batch) != 2:
                raise ValueError("batch must be a rank/count pair")
            child, count = batch
            if type(child) is not int or not 0 <= child < rank:
                raise ValueError("child rank must strictly descend")
            if not positive(count):
                raise ValueError("batch count must be a bounded positive integer")


def multiplier(widths: list[int], batches: tuple) -> int:
    """Local predecessor formula, applied only to validated system rows."""
    value = 1
    for child, count in batches:
        width = widths[child]
        value = lcm(value, width // gcd(width, count))
    return value


def compile_library(bases: tuple, levels: tuple, slacks: tuple) -> tuple[int, ...]:
    """Each independent positive slack gives exactly one feasible library."""
    validate(bases, levels)
    if not isinstance(slacks, tuple) or len(slacks) != len(levels):
        raise ValueError("one slack is required per nonbase rank")
    if not all(positive(value) for value in slacks):
        raise ValueError("slacks must be bounded positive integers")
    widths = list(bases)
    for (sources, batches), slack in zip(levels, slacks, strict=True):
        widths.append(sources * slack * multiplier(widths, batches))
    # All widths divide the product of base widths, sources and slacks.
    if max(widths).bit_length() > 16 * (len(bases) + 2 * len(levels)):
        raise ArithmeticError("width exceeded the proved product bound")
    return tuple(widths)


def feasible(bases: tuple, levels: tuple, widths: tuple) -> bool:
    """Literal whole-invocation conditions, without the gcd/LCM formula."""
    validate(bases, levels)
    if not isinstance(widths, tuple) or len(widths) != len(bases) + len(levels):
        raise ValueError("wrong library length")
    if not all(type(value) is int and 0 < value < (1 << 1536) for value in widths):
        raise ValueError("library widths must be bounded positive integers")
    if widths[:len(bases)] != bases:
        return False
    for rank, (sources, batches) in enumerate(levels, start=len(bases)):
        if widths[rank] % sources:
            return False
        replication = widths[rank] // sources
        if any((replication * count) % widths[child] for child, count in batches):
            return False
    return True


def recover_slacks(bases: tuple, levels: tuple, widths: tuple) -> tuple[int, ...]:
    """Recover the unique slack vector of a feasible library."""
    if not feasible(bases, levels, widths):
        raise ValueError("library is infeasible")
    slacks = []
    for rank, (sources, batches) in enumerate(levels, start=len(bases)):
        modulus = sources * multiplier(list(widths[:rank]), batches)
        if widths[rank] % modulus:
            raise ArithmeticError("literal feasibility did not imply the modulus")
        slacks.append(widths[rank] // modulus)
    return tuple(slacks)
