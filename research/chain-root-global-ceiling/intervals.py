"""Directed integer intervals. @CubeJerry/OpenAI assistance, Apache-2.0.

No predecessor arithmetic implementation is imported. All endpoints are
multiples of 2**-192; logarithm and exponential tails are bounded explicitly.
"""
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
BITS = 192
SCALE = 1 << BITS
LOG_TERMS = 80
EXP_TERMS = 40


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceiling(a, b):
    need(b > 0, "positive divisor")
    return -((-a) // b)


@dataclass(frozen=True)
class Interval:
    lo: int
    hi: int

    def __post_init__(self):
        need(self.lo <= self.hi, "ordered interval")

    def __add__(self, other):
        return Interval(self.lo+other.lo, self.hi+other.hi)

    def __sub__(self, other):
        return Interval(self.lo-other.hi, self.hi-other.lo)

    def times(self, value):
        q = Fraction(value)
        if q >= 0:
            return Interval(self.lo*q.numerator//q.denominator,
                            ceiling(self.hi*q.numerator,q.denominator))
        return Interval(self.hi*q.numerator//q.denominator,
                        ceiling(self.lo*q.numerator,q.denominator))

    def product(self, other):
        need(self.lo>=0 and other.lo>=0, "nonnegative product")
        return Interval(self.lo*other.lo//SCALE,
                        ceiling(self.hi*other.hi,SCALE))

    def decimal(self, places=24):
        def show(value):
            sign = "-" if value<0 else ""
            whole,frac = divmod(abs(value),10**places)
            return sign+str(whole)+"."+str(frac).zfill(places)
        return [show(self.lo*10**places//SCALE),
                show(ceiling(self.hi*10**places,SCALE))]


ZERO = Interval(0,0)
ONE = Interval(SCALE,SCALE)


def rational(q):
    q=Fraction(q)
    return Interval(q.numerator*SCALE//q.denominator,
                    ceiling(q.numerator*SCALE,q.denominator))


def log_from_atanh(numerator, denominator):
    need(0<=3*numerator<=denominator, "atanh reduction domain")
    if numerator==0:
        return ZERO
    z=rational(Fraction(numerator,denominator))
    square=z.product(z)
    term=z
    total=ZERO
    for j in range(LOG_TERMS):
        total=total+term.times(Fraction(1,2*j+1))
        term=term.product(square)
    # 2 sum_{j=N}^infty z^(2j+1)/(2j+1)
    # <= 9/[4(2N+1)3^(2N+1)], since z<=1/3.
    tail=ceiling(9*SCALE,4*(2*LOG_TERMS+1)*3**(2*LOG_TERMS+1))
    return Interval(2*total.lo,2*total.hi+tail)


@lru_cache(None)
def log_integer(rank):
    need(type(rank) is int and rank>=1, "positive integer rank")
    if rank==1:
        return ZERO
    exponent=rank.bit_length()-1
    base=1<<exponent
    return (log_from_atanh(1,3).times(exponent)
            +log_from_atanh(rank-base,rank+base))


def exponential(argument):
    need(0<=argument.lo<=argument.hi<=16*SCALE, "exponential domain")
    squarings=0
    while argument.hi>SCALE//2:
        argument=argument.times(Fraction(1,2))
        squarings+=1
    term=ONE
    total=ONE
    for j in range(1,EXP_TERMS+1):
        term=term.product(argument).times(Fraction(1,j))
        total=total+term
    following=term.product(argument).times(Fraction(1,EXP_TERMS+1))
    # Each following term ratio <= argument.hi/[SCALE*(N+2)].
    tail=ceiling(following.hi*(EXP_TERMS+2)*SCALE,
                 (EXP_TERMS+2)*SCALE-argument.hi)
    result=Interval(total.lo,total.hi+tail)
    for _ in range(squarings):
        result=result.product(result)
    return result


@lru_cache(None)
def power(rank, saving):
    saving=Fraction(saving)
    need(0<=saving<=1, "saving in [0,1]")
    denominator=exponential(log_integer(rank).times(saving))
    need(denominator.lo>0, "positive exponential")
    return Interval(rank*SCALE*SCALE//denominator.hi,
                    ceiling(rank*SCALE*SCALE,denominator.lo))


def signed_moment(coefficients, saving):
    result=ZERO
    for rank,count in coefficients.items():
        need(type(rank) is int and rank>=1 and type(count) is int,
             "integer signed profile")
        result=result+power(rank,Fraction(saving)).times(count)
    return result
