# SPDX-License-Identifier: Apache-2.0
"""Explicit subspaces of F_2^9, following the PR3057 representation."""

from functools import lru_cache

Space = frozenset[int]
ZERO = frozenset({0})
FULL = frozenset(range(512))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    require(isinstance(vectors, (list, tuple)) and len(vectors) <= 9,
            "at most nine frame generators")
    result = ZERO
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512, "nine-bit generator")
        result |= frozenset(x ^ vector for x in result)
    return result


def rank(frame):
    return len(frame).bit_length() - 1


def join(a, b):
    return frozenset(x ^ y for x in a for y in b)


@lru_cache(maxsize=1024)
def domain(lower, upper):
    require(lower <= upper and rank(upper) - rank(lower) <= 3,
            "quotient dimension at most three")
    choices = {lower}
    for _ in range(rank(upper) - rank(lower)):
        choices |= {frame | frozenset(x ^ vector for x in frame)
                    for frame in choices for vector in upper - frame}
    require(len(choices) <= 16, "at most sixteen intermediate subspaces")
    return tuple(sorted(choices, key=lambda f: (len(f), tuple(sorted(f)))))


def operands(gate):
    require(isinstance(gate, list) and gate[0] in ("add", "scale"), "scalar gate")
    add = gate[0] == "add"
    require(len(gate) == 5 + add, "scalar arity")
    registers = tuple(gate[1:3] if add else gate[1:2])
    require(all(type(r) is int and 0 <= r < 704 for r in registers), "register range")
    require(len(set(registers)) == len(registers), "distinct ADD operands")
    return registers
