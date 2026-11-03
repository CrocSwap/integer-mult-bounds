"""Literal binary Jordan-chain compiler, produced by Nick Petalas.

Apache-2.0. The executable caps roles at 64; the written theorem is uniform.
"""

MAX_ROLES = 64


def compile_chain(length, roles=None):
    """Return chronological (operation, target, source) primitive records.

    ``xor`` adds one whole source role to a target. ``reflect`` applies the
    same supplied linear involution to one role; its source equals its target.
    Extra roles start arbitrary and are untouched. No clean role is needed.
    """
    if type(length) is not int or not 1 <= length <= MAX_ROLES:
        raise ValueError("chain length must be an integer from 1 through 64")
    if roles is None:
        roles = length
    if type(roles) is not int or not length <= roles <= MAX_ROLES:
        raise ValueError("role count must be an integer between length and 64")
    program = []
    for first in range(0, length - 2, 2):
        middle, last = first + 1, first + 2
        program.extend((
            ("xor", first, middle),
            ("reflect", middle, middle),
            ("xor", first, middle),
            ("xor", middle, last),
            ("reflect", middle, middle),
            ("xor", middle, last),
        ))
    if length % 2 == 0:
        first, last = length - 2, length - 1
        program.extend((
            ("xor", first, last),
            ("reflect", last, last),
            ("xor", first, last),
            ("reflect", last, last),
        ))
    return tuple(program)
