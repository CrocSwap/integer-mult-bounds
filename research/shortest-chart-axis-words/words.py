"""Exact ranking of shortest binary symplectic chart words, for 1 <= n <= 6."""

from math import prod

Chart = frozenset[int]
MAX_N = 6


def pairing(x: int, y: int, n: int) -> int:
    mask = (1 << n) - 1
    return (((x & mask) & (y >> n)).bit_count()
            + ((y & mask) & (x >> n)).bit_count()) & 1


def validate(chart: Chart, n: int) -> None:
    if type(n) is not int or not 1 <= n <= MAX_N:
        raise ValueError("dimension must be an integer from 1 through 6")
    if not isinstance(chart, frozenset) or len(chart) != 1 << n or 0 not in chart:
        raise ValueError("a chart must contain exactly 2^n vectors, including zero")
    if any(type(x) is not int or not 0 <= x < 1 << (2 * n) for x in chart):
        raise ValueError("vector outside the ambient space")
    for x in chart:
        for y in chart:
            if x ^ y not in chart or pairing(x, y, n):
                raise ValueError("chart must be an isotropic subspace")


def distance(left: Chart, right: Chart, n: int) -> int:
    return n - ((len(left & right)).bit_length() - 1)


def move(chart: Chart, axis: int, n: int) -> Chart:
    return frozenset(x ^ (axis if pairing(x, axis, n) else 0) for x in chart)


def count(n: int, r: int, *, literal: bool = True) -> int:
    if type(n) is not int or type(r) is not int or not 1 <= n <= MAX_N or not 0 <= r <= n:
        raise ValueError("require 1 <= n <= 6 and 0 <= distance <= n")
    paths = prod((1 << j) - 1 for j in range(1, r + 1))
    return paths << (r * (n - 1)) if literal else paths


def choices(current: Chart, target: Chart, n: int) -> list[tuple[int, Chart]]:
    r = distance(current, target, n)
    if r == 0:
        return []
    result = []
    for axis in range(1, 1 << (2 * n)):
        changed = move(current, axis, n)
        if distance(changed, target, n) == r - 1:
            result.append((axis, changed))
    if len(result) != (1 << (n - 1)) * ((1 << r) - 1):
        raise ArithmeticError("distance-decreasing axis multiplicity failed")
    return result


def unrank(left: Chart, right: Chart, n: int, index: int) -> tuple[int, ...]:
    """Lexicographic bijection from [0,count(n,r)) to shortest literal words."""
    validate(left, n)
    validate(right, n)
    r = distance(left, right, n)
    if type(index) is not int or not 0 <= index < count(n, r):
        raise ValueError("word index outside the exact range")
    current = left
    word = []
    for remaining in range(r, 0, -1):
        block = count(n, remaining - 1)
        digit, index = divmod(index, block)
        axis, current = choices(current, right, n)[digit]
        word.append(axis)
    if current != right or index != 0:
        raise ArithmeticError("unranking did not reach the target")
    return tuple(word)


def rank(left: Chart, right: Chart, n: int, word: tuple[int, ...]) -> int:
    validate(left, n)
    validate(right, n)
    r = distance(left, right, n)
    if not isinstance(word, tuple) or len(word) != r:
        raise ValueError("word must be a tuple with the minimum length")
    current = left
    index = 0
    for step, axis in enumerate(word):
        if type(axis) is not int or not 0 < axis < 1 << (2 * n):
            raise ValueError("invalid nonzero axis")
        options = choices(current, right, n)
        position = next((i for i, item in enumerate(options) if item[0] == axis), None)
        if position is None:
            raise ValueError("word is not distance-decreasing")
        index += position * count(n, r - step - 1)
        current = options[position][1]
    if current != right:
        raise ArithmeticError("ranked word did not reach the target")
    return index
