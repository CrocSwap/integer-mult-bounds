# SPDX-License-Identifier: Apache-2.0
"""Separate semantic checker for the serialized primitive recipes."""

from fractions import Fraction
from functools import lru_cache

from lower import require


@lru_cache(maxsize=128)
def local_map(instructions, kind, q):
    """A second interpreter, independent of lower.execute and its row updates."""
    require(len(instructions) <= 32, "bounded literal recipe")
    columns = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0)],
    ]
    for op in instructions:
        tag, t = op[:2]
        for column in columns:
            if tag == "clear":
                column[t] = Fraction(0)
            elif tag == "copy":
                column[t] = column[op[2]]
            elif tag == "add":
                column[t] += op[3] * column[op[2]]
            elif tag == "neg":
                column[t] = -column[t]
            elif tag == "double":
                column[t] *= 2
            elif tag == "half":
                column[t] /= 2
            else:
                raise ValueError("unknown literal instruction")
    expected = {"clear": (0, 0), "copy": (0, 1), "add": (1, q), "scale": (q, 0)}[kind]
    require(tuple(column[0] for column in columns) == expected, "literal target map")
    require(
        tuple(column[1] for column in columns) == (0, 1), "literal source preservation"
    )
    require(tuple(column[2] for column in columns) == (0, 0), "literal scratch cleanup")


def check_macro(events, kind, q, target, source, component, frame):
    names = {(*target, component): 0, ("K", 0, component): 2}
    if source is not None:
        names[(*source, component)] = 1
    require(len(events) <= 32, "bounded emitted macro")
    instructions = []
    for event in events:
        require(
            len(event) == 3 and event[0] == "primitive" and event[2] == frame,
            "literal primitive frame",
        )
        op = event[1]
        require(
            2 <= len(op) <= 4
            and op[0] in ("clear", "copy", "add", "neg", "double", "half"),
            "literal primitive shape",
        )
        kind_op = op[0]
        require(
            len(op) == (4 if kind_op == "add" else 3 if kind_op == "copy" else 2),
            "literal arity",
        )
        require(tuple(op[1]) in names, "literal target ownership")
        translated = [kind_op, names[tuple(op[1])]]
        if kind_op in ("copy", "add"):
            require(tuple(op[2]) in names, "literal source ownership")
            translated.append(names[tuple(op[2])])
            require(translated[1] != translated[2], "literal distinct operands")
        if kind_op == "add":
            require(type(op[3]) is int and op[3] in (-1, 1), "literal sign")
            translated.append(op[3])
        instructions.append(tuple(translated))
    local_map(tuple(instructions), kind, q)
