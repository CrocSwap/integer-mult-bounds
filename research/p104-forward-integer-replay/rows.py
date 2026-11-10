"""Use exact sparse or packed integer rows.

Shared denominators and Kronecker substitution are classical methods.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache


@lru_cache(maxsize=128, typed=True)
def coefficient(value):
    """Cache only the exact immutable coefficient, with separate input types."""
    return Q(value)


class Sparse:
    def __init__(self, values, exponent=0):
        self.values, self.exponent = values, exponent

    @classmethod
    def unit(cls, index):
        return cls({index: 1})

    @classmethod
    def zero(cls):
        return cls({})

    def __bool__(self):
        return bool(self.values)

    def scale(self, q):
        return type(self)({k: q.numerator*v for k, v in self.values.items()},
                          self.exponent+q.denominator.bit_length()-1)

    def add(self, other, q):
        extra = q.denominator.bit_length()-1
        level = max(self.exponent, other.exponent+extra)
        left, right = level-self.exponent, level-other.exponent-extra
        multiplier = q.numerator << right
        if left:
            self.values = {k: v << left for k, v in self.values.items()}
        for k, value in other.values.items():
            result = self.values.get(k, 0) + multiplier*value
            if result:
                self.values[k] = result
            else:
                self.values.pop(k, None)
        self.exponent = level

    def exact(self):
        return {k: Q(v, 1 << self.exponent) for k, v in self.values.items()}

    def __eq__(self, expected):
        return self.exact() == expected


def radix_bound(word):
    """Bound every signed numerator without using coefficient cancellation."""
    size = word['public'] + word.get('owned_fields', 8)
    bounds, exponents = [1]*size, [0]*size
    largest, largest_exponent = 1, 0
    for event in word['program']:
        op, target = event[:2]
        if not 0 <= target < size:
            raise ValueError('Role index')
        if op in ('INIT', 'CLEAR'):
            bounds[target], exponents[target] = 0, 0
        elif op != 'MOVE':
            q = coefficient(event[-2])
            numerator, extra = abs(q.numerator), q.denominator.bit_length()-1
            if q.denominator != 1 << extra:
                raise ValueError('Dyadic scalar coefficient')
            if op == 'SCALE':
                bounds[target] *= numerator
                exponents[target] += extra
            else:
                source = event[2]
                if not 0 <= source < size:
                    raise ValueError('Common scalar chart')
                if op == 'COPY':
                    bounds[target] = numerator*bounds[source]
                    exponents[target] = exponents[source]+extra
                else:
                    level = max(exponents[target], exponents[source]+extra)
                    bounds[target] = ((bounds[target] << (level-exponents[target]))
                                      + numerator*(bounds[source] << (level-exponents[source]-extra)))
                    exponents[target] = level
        largest = max(largest, bounds[target])
        largest_exponent = max(largest_exponent, exponents[target])
    # Include the numerator of each expected endpoint coefficient.
    width = (2*(largest+(1 << largest_exponent))).bit_length()
    return width, size, largest, largest_exponent


def packed_type(width, size):
    """Fix a typed radix for one complete word."""
    if type(width) is not int or width < 2 or type(size) is not int or size < 1:
        raise ValueError('Positive packed dimensions')
    radix = 1 << width

    class Packed:
        def __init__(self, value, exponent=0):
            self.value, self.exponent = value, exponent

        @classmethod
        def unit(cls, index):
            return cls(1 << (width*index))

        @classmethod
        def zero(cls):
            return cls(0)

        def __bool__(self):
            return bool(self.value)

        def scale(self, q):
            return type(self)(q.numerator*self.value,
                              self.exponent+q.denominator.bit_length()-1)

        def add(self, other, q):
            extra = q.denominator.bit_length()-1
            level = max(self.exponent, other.exponent+extra)
            self.value = ((self.value << (level-self.exponent))
                          + ((q.numerator*other.value) << (level-other.exponent-extra)))
            self.exponent = level

        def exact(self):
            value, out = self.value, {}
            for index in range(size):
                digit = value & (radix-1)
                if digit >= radix//2:
                    digit -= radix
                if digit:
                    out[index] = Q(digit, 1 << self.exponent)
                value = (value-digit) >> width
            if value:
                raise ValueError('Packed coefficient overflow')
            return out

        def __eq__(self, expected):
            value = 0
            for index, coefficient in expected.items():
                numerator = Q(coefficient)*(1 << self.exponent)
                if numerator.denominator != 1:
                    return False
                value += numerator.numerator << (width*index)
            return self.value == value

    return Packed
