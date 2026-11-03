"""Bound the fixed 48-term source interval with bounded dyadic arithmetic.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
Integer Taylor evaluation: ywz65 and Nick Petalas. Outward rounding is standard.
"""
from fractions import Fraction as Q


def ceildiv(a, b):
    return -(-a//b)


def exponential(x, bits=160):
    if type(x) not in (int, Q) or not 0 <= x < 1:
        raise ValueError('Exact argument in [0,1) required')
    if type(bits) is not int or not 8 <= bits <= 4096:
        raise ValueError('Precision must be an integer from 8 through 4096')
    x = Q(x)
    if max(x.numerator.bit_length(),x.denominator.bit_length()) > 16384:
        raise ValueError('Input capacity exceeded')
    unit = 1 << bits
    low = x.numerator*unit//x.denominator
    high = ceildiv(x.numerator*unit,x.denominator)
    tl = th = sl = sh = unit
    for j in range(1,49):
        tl = tl*low//(unit*j)
        th = ceildiv(th*high,unit*j)
        sl += tl
        sh += th
    following = ceildiv(th*high,unit*49)
    tail = ceildiv(following*50*unit,50*unit-high)
    return Q(sl,unit),Q(sh+tail,unit)


class Moment:
    """Use the retained logarithms with an explicit exponential function."""
    def __init__(self, logarithms, exponential_function):
        self.logarithms = logarithms
        self.exponential = exponential_function
        self.cache = {}
        self.calls = []

    def power(self, rank, kappa):
        key = rank,kappa
        if key not in self.cache:
            if rank in (0,1):
                value = Q(rank),Q(rank)
            else:
                a,b = self.logarithms(rank)
                first,second = self.exponential(kappa*a),self.exponential(kappa*b)
                self.calls.extend([(kappa*a,first),(kappa*b,second)])
                value = Q(rank)/second[1],Q(rank)/first[0]
            self.cache[key] = value
        return self.cache[key]

    def moment(self, profile, kappa):
        low = high = Q(0)
        for rank,count in profile.items():
            a,b = self.power(rank,kappa)
            low += count*(a if count >= 0 else b)
            high += count*(b if count >= 0 else a)
        return low,high


def logarithm(rank, bits=160):
    """Contain the retained 80-term atanh series for an integer rank."""
    if type(rank) is not int or rank < 1 or rank.bit_length() > 16384:
        raise ValueError('Positive integer rank within input capacity required')
    if type(bits) is not int or not 8 <= bits <= 4096:
        raise ValueError('Precision must be an integer from 8 through 4096')
    unit = 1 << bits

    def series(numerator,denominator):
        # The exact atanh argument is numerator/denominator, at most one third.
        lo = numerator*unit//denominator
        hi = ceildiv(numerator*unit,denominator)
        square_lo = lo*lo//unit
        square_hi = ceildiv(hi*hi,unit)
        pl,ph = lo,hi
        sl = sh = 0
        for j in range(80):
            sl += pl//(2*j+1)
            sh += ceildiv(ph,2*j+1)
            pl = pl*square_lo//unit
            ph = ceildiv(ph*square_hi,unit)
        tail = ceildiv(2*ph*unit,161*(unit-square_hi))
        return 2*sl,2*sh+tail

    exponent = rank.bit_length()-1
    power = 1 << exponent
    al,ah = series(1,3)
    bl,bh = series(rank-power,rank+power)
    return Q(exponent*al+bl,unit),Q(exponent*ah+bh,unit)
