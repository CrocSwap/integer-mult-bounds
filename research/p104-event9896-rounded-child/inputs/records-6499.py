"""Exact integer records for the selected P104 scalar events.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def require(ok, message):
    if not ok:
        raise ValueError(message)


def quotient(value, divisor):
    require(value % divisor == 0, 'exact scalar division')
    return value//divisor


def run(word, initial, native, grid=5):
    """Native returns are integers in the coarse grid; all records use 2^-grid."""
    require(type(grid) is int and grid >= 0, 'nonnegative grid')
    require(len(initial) == word['public'] and all(type(v) is int for v in initial), 'integer public entrance')
    scale = 1 << grid
    values = [v*scale for v in initial]+[0]*word['owned_fields']
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':
            value = native(j,r,values[r],scale)
            require(type(value) is int, 'integer native return')
            values[r] = value*scale
        elif op in ('INIT','CLEAR'):
            values[r] = 0
        else:
            q = Q(e[-2])
            require(q.denominator & (q.denominator-1) == 0, 'dyadic scalar')
            if op == 'SCALE':
                values[r] = quotient(q.numerator*values[r],q.denominator)
            else:
                v = quotient(q.numerator*values[e[2]],q.denominator)
                values[r] = v if op == 'COPY' else values[r]+v
        yield j,r,values[r]
