"""Check the serial arithmetic against independent host arithmetic and exact budgets."""

from fractions import Fraction
from itertools import product
from math import gcd
from random import Random
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from serial_setup import bezout, quotient_remainder, rational


def integer(x):
    return (-1 if x < 0 else 1, format(abs(x), "b"))


def value(x):
    return x[0] * int(x[1], 2)


def check_pair(a, b):
    if b:
        q, r = quotient_remainder(integer(a)[1], integer(b)[1])
        assert (int(q, 2), int(r, 2)) == divmod(abs(a), abs(b))
    else:
        try:
            quotient_remainder(integer(a)[1], "0")
        except ZeroDivisionError:
            pass
        else:
            raise AssertionError("division by zero")
    g, x, y = bezout(integer(a), integer(b))
    assert value(x)*a + value(y)*b == int(g, 2) == gcd(a, b)


def rat(x):
    return integer(x.numerator), format(x.denominator, "b")


def check_rational(x, y, op):
    if op == "/" and not y:
        try:
            rational(op, rat(x), rat(y))
        except ZeroDivisionError:
            return
        raise AssertionError("rational division by zero")
    expected = {"+": Fraction.__add__, "-": Fraction.__sub__,
                "*": Fraction.__mul__, "/": Fraction.__truediv__}[op](x, y)
    assert rational(op, rat(x), rat(y)) == rat(expected)


def clock():
    w = 2**38
    h = 2*w + 2
    # The bound for a Euclid step includes both signed coefficient updates.
    bezout_cost = 2**16*(h + 4)*(7*h + 9)
    elementary = 2**16*(h + 4)**2
    scalar = bezout_cost + 8*elementary
    assert scalar < 2**110
    store = 4*w*2**68
    lookup = 8*store*512*128
    assert store == 2**108 and lookup == 2**127
    action = lookup + scalar + 2**120
    assert action < 2**128
    total = (2**68 + 1)*action*2**32
    assert total < 2**228
    return dict(max_datum_bits=w, lookup=lookup, local_arithmetic=scalar,
                all_setup=total, setup_exponent=228)


def main():
    pairs = list(product(range(-31, 32), repeat=2))
    for width in (1, 2, 11, 31, 63, 127, 256, 512):
        a = 2**width - 1
        for b in (1, a, a + 1, 2**(width//2) + 1):
            pairs.append((a, b))
            pairs.append((-b, a))
    rng = Random(17813)
    for width in (16, 64, 256):
        for _ in range(12):
            pairs.append((rng.getrandbits(width), -rng.getrandbits(width)))
    a, b = 0, 1
    while b.bit_length() < 512:
        a, b = b, a + b
    pairs.extend(((a, b), (-b, -a)))
    for a, b in pairs:
        check_pair(a, b)
    numbers = sorted({Fraction(a, b) for a in range(-6, 7) for b in range(1, 6)})
    rational_cases = 0
    for x, y in product(numbers, repeat=2):
        for op in "+-*/":
            check_rational(x, y, op)
            rational_cases += 1
    print(json.dumps(dict(integer_pairs=len(pairs), rational_cases=rational_cases, **clock()), indent=2))


if __name__ == "__main__":
    main()
