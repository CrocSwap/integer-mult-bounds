"""Count the actual fixed invocation word without evaluating register values.

Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
This module imports no repository implementation. The caller supplies the
invocation function; its control flow must be independent of register values.
Subtraction counts as an addition, and coefficient signs are folded into it.
"""
from fractions import Fraction


def census(invoke, code, factor, inverse=False):
    """Return the executed addition, halving and total primitive charges."""
    counts = {'additions': 0, 'halvings': 0}

    class Paid:
        def __add__(self, other):
            if not isinstance(other, Paid):
                raise ValueError('unexpected scalar operand in cost census')
            counts['additions'] += 1
            return self

        def __sub__(self, other):
            return self.__add__(other)

        def __mul__(self, coefficient):
            if type(coefficient) not in (int, Fraction):
                raise ValueError('inexact coefficient in cost census')
            if abs(coefficient) == Fraction(1, 2):
                counts['halvings'] += 1
            elif abs(coefficient) != 1:
                raise ValueError('unpriced coefficient in cost census')
            return self

        __rmul__ = __mul__

    n = len(factor['triples'])
    banks = [[Paid() for _ in range(size)]
             for size in (n, n, code['roles'], factor['h'])]
    invoke(*banks, code, factor, inverse=inverse)
    return dict(counts, total=counts['additions'] + counts['halvings'])
