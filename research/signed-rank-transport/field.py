"""Exact Q(omega), with omega^2+omega+1=0, in two rational coordinates."""
from dataclasses import dataclass
from fractions import Fraction as Q


@dataclass(frozen=True)
class E:
    a: Q = Q(0)
    b: Q = Q(0)

    def __post_init__(self):
        if not isinstance(self.a, (str, int, Q)) or not isinstance(self.b, (str, int, Q)):
            raise TypeError('Use exact integer, rational or string coordinates')
        object.__setattr__(self, 'a', Q(self.a))
        object.__setattr__(self, 'b', Q(self.b))

    @staticmethod
    def cast(value):
        return value if isinstance(value, E) else E(value)

    def __add__(self, other):
        other = E.cast(other)
        return E(self.a+other.a, self.b+other.b)

    __radd__ = __add__

    def __neg__(self):
        return E(-self.a, -self.b)

    def __sub__(self, other):
        return self+-E.cast(other)

    def __rsub__(self, other):
        return E.cast(other)+-self

    def __mul__(self, other):
        other = E.cast(other)
        a, b, c, d = self.a, self.b, other.a, other.b
        return E(a*c-b*d, a*d+b*c-b*d)

    __rmul__ = __mul__

    def conjugate(self):
        return E(self.a-self.b, -self.b)

    def norm(self):
        return self.a*self.a-self.a*self.b+self.b*self.b

    def __truediv__(self, other):
        other = E.cast(other)
        norm = other.norm()
        if not norm:
            raise ZeroDivisionError('Zero Eisenstein element')
        numerator = self*other.conjugate()
        return E(numerator.a/norm, numerator.b/norm)

    def __rtruediv__(self, other):
        return E.cast(other)/self

    def __bool__(self):
        return bool(self.a or self.b)

    def __eq__(self, other):
        if not isinstance(other, (E, int, Q)):
            return NotImplemented
        other = E.cast(other)
        return self.a == other.a and self.b == other.b

    def __hash__(self):
        return hash(self.a) if not self.b else hash((E, self.a, self.b))

    def real(self):
        return self.a-self.b/2

    def json(self):
        return [str(self.a), str(self.b)]


ZERO, ONE, OMEGA = E(), E(1), E(0, 1)
