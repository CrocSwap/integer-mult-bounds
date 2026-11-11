"""Outward integer intervals, scaled by 10**70, for ranks at most 145.

No transcendental library call participates in a certificate. Decimal values
used by the caller only nominate rational points for these checks.
"""
from fractions import Fraction

Q = 10**70
LOG_TERMS = 100
EXP_TERMS = 80


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ceiling(a, b):
    return -(-a // b)


def rational(x):
    value = Fraction(x)
    return value.numerator * Q // value.denominator, ceiling(value.numerator * Q, value.denominator)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def scale(a, n):
    return (a[0] * n, a[1] * n) if n >= 0 else (a[1] * n, a[0] * n)


def multiply(a, b):
    require(0 <= a[0] <= a[1] and 0 <= b[0] <= b[1], "nonnegative factors required")
    return a[0] * b[0] // Q, ceiling(a[1] * b[1], Q)


def log_unit(value):
    """2 atanh z, z=(value-1)/(value+1), 1 <= value <= 2."""
    require(1 <= value <= 2, "log range reduction")
    z = (value - 1) / (value + 1)
    total, power = Fraction(0), z
    for j in range(LOG_TERMS):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * LOG_TERMS + 1) * (1 - z * z))
    return rational(total)[0], rational(total + tail)[1]


def log_rank(rank):
    require(isinstance(rank, int) and 1 <= rank <= 145, "rank outside 1..145")
    shift = rank.bit_length() - 1
    return add(scale(log_unit(Fraction(2)), shift), log_unit(Fraction(rank, 2**shift)))


def exp_small(x):
    """exp(x) for 0 <= x <= 1/8, with an explicit geometric tail."""
    require(0 <= x[0] <= x[1] <= Q // 8, "exponential argument outside 0..1/8")
    term, total = (Q, Q), (Q, Q)
    for j in range(1, EXP_TERMS + 1):
        term = term[0] * x[0] // (Q * j), ceiling(term[1] * x[1], Q * j)
        total = add(total, term)
    next_upper = ceiling(term[1] * x[1], Q * (EXP_TERMS + 1))
    # All subsequent term ratios are <= 1/(8*82) < 1/2.
    return total[0], total[1] + 2 * next_upper


def power(rank, log, k):
    """rank**(1-k) = rank/exp(k*log(rank))."""
    denominator = exp_small(multiply(k, log))
    return rank * Q * Q // denominator[1], ceiling(rank * Q * Q, denominator[0])


class Oracle:
    def __init__(self, ranks):
        require(len(ranks) <= 145, "too many ranks")
        self.logs = {r: log_rank(r) for r in ranks}

    def powers(self, low, high=None):
        lo, hi = rational(low), rational(low if high is None else high)
        require(0 <= lo[0] <= hi[1] <= Q // 50, "k outside 0..0.02")
        k = lo[0], hi[1]
        return {r: power(r, log, k) for r, log in self.logs.items()}

    def moment(self, coefficients, low, high=None, derivative=False):
        powers, total = self.powers(low, high), (0, 0)
        for r, n in coefficients.items():
            value = multiply(powers[r], self.logs[r]) if derivative else powers[r]
            total = add(total, scale(value, n))
        return total

    def certify(self, coefficients):
        """Certify -F' > 0 by a Lipschitz grid on [0,1/50]."""
        bound = sum(abs(n) * r * multiply(log, log)[1]
                    for r, n in coefficients.items() for log in [self.logs[r]])
        step = Fraction(1, 500)
        error = ceiling(bound, 500)
        for j in range(11):
            require(self.moment(coefficients, j * step, derivative=True)[0] > error,
                    "slope interval does not prove monotonicity")
        require(self.moment(coefficients, 0)[0] > 0, "initial margin not positive")
        require(self.moment(coefficients, Fraction(1, 50))[1] < 0, "final margin not negative")

    def bracket(self, coefficients, low, high):
        require(Fraction(low) < Fraction(high), "reversed root bracket")
        require(self.moment(coefficients, low)[0] > 0, "lower root endpoint not positive")
        require(self.moment(coefficients, high)[1] < 0, "upper root endpoint not negative")


def close(interval, approximation):
    """The printed approximation has absolute error less than 10**-39."""
    middle = rational(approximation)
    error = Q // 10**39
    require(middle[1] - error < interval[0] <= interval[1] < middle[0] + error,
            "approximation outside certified error bound")
