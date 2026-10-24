"""Complete sequential solves against independent rounded LU arithmetic."""
from fractions import Fraction as Q
from hashlib import sha256
from gaussian_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_boundary import BandedSolve, prepare_bands
    from gaussian_matrix import Matrix, lu
    from gaussian_rationals import Rational
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK
    pool = ScratchPool(256)
    scope = OuterScope(pool)
    owner = BandedSolve()
    results = []
    for data in ([Q(1, 4), Q(-1, 2), Q(3, 8)], [Q(-3, 8)]):
        n, bits = len(data), 12
        matrix_values = ([[Q(4), Q(-1), Q(0)], [Q(1, 4), Q(5), Q(-1, 2)],
                          [Q(0), Q(1, 4), Q(3)]] if n == 3 else [[Q(3, 2)]])
        exact_lower = ([[Q(1), Q(0), Q(0)], [Q(1, 16), Q(1), Q(0)],
                        [Q(0), Q(4, 81), Q(1)]] if n == 3 else [[Q(1)]])
        exact_upper = ([[Q(4), Q(-1), Q(0)], [Q(0), Q(81, 16), Q(-1, 2)],
                        [Q(0), Q(0), Q(245, 81)]] if n == 3 else [[Q(3, 2)]])
        def make(value):
            return Rational(Signed(Count.literal(abs(value.numerator)), value < 0), Count.literal(value.denominator))
        def rounded(value):
            return Q(int(value*(1 << bits)), 1 << bits)
        low = [[rounded(v) for v in row] for row in exact_lower]
        high = [[rounded(v) for v in row] for row in exact_upper]
        reciprocal = [rounded(1/exact_upper[i][i]) for i in range(n)]
        y, expected = [Q(0)]*n, [Q(0)]*n
        for i in range(n):
            y[i] = rounded(data[i]-sum((low[i][j]*y[j] for j in range(i)), Q(0)))
        for i in reversed(range(n)):
            expected[i] = rounded(reciprocal[i]*(y[i]-sum((high[i][j]*expected[j] for j in range(i+1, n)), Q(0))))
        with owned(Count.literal(n), Count.literal(2), Count.literal(40), Count.literal(bits)) as (length, band, width, precision):
            with sealed_constructors(), scope.installed():
                matrix = lower = upper = lower_tape = upper_tape = rhs = None
                try:
                    matrix = Matrix(length, length, pool, lambda i, j: make(matrix_values[decode(i)][decode(j)]))
                    with no_decode():
                        lower, upper = lu(matrix)
                        lower_tape, upper_tape = prepare_bands(lower, upper, band, width, precision, pool)
                    rhs = pool.acquire()
                    for value in data:
                        integer = int(value*(1 << bits))
                        with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (number,):
                            write_signed(number, rhs, width)
                    rhs.rewind()
                    saved = [body(borrowed_tape(t)) for t in (lower_tape, upper_tape, rhs)]
                    products = owner.arithmetic.products
                    with scope.suspended(), no_decode():
                        output = owner.run(lower_tape, upper_tape, rhs, length, band, width, precision)
                    raw = body(output)
                    actual = []
                    for _ in data:
                        with owned(read_signed(output, width)) as (value,):
                            actual.append(Q((-1 if value.negative else 1)*decode(value.magnitude), 1 << bits))
                    require(actual == expected and output.read() == BLANK,
                            "complete banded solve matches independent rounded arithmetic")
                    residual = max(abs(sum(matrix_values[i][j]*actual[j] for j in range(n))-data[i]) for i in range(n))
                    require(residual < Q(8, 1 << bits), "finite exact source residual")
                    require(saved == [body(borrowed_tape(t)) for t in (lower_tape, upper_tape, rhs)],
                            "banded solve preserves factors and right-hand side")
                    require(owner.arithmetic.products-products == 5*n, "all band and reciprocal products execute")
                    owner.idle()
                    require(owner.closed and not owner.pool.live, "closed banded-solve owner")
                    require(all(t.head == 1 and all(v == BLANK for v in t.cells) for t in owner.pool.tapes),
                            "banded solve restores its owned roles")
                    results.append({"length": n, "band": 2, "values": [str(v) for v in actual],
                                    "residual": str(residual), "sha256": sha256(raw).hexdigest(),
                                    "products": 5*n, "pool_peak": owner.pool.peak})
                    output.clear()
                    erase_marker(output)
                finally:
                    for value in (matrix, lower, upper):
                        if value is not None:
                            value.close()
                    for tape in (lower_tape, upper_tape, rhs):
                        if tape is not None:
                            tape.clear()
                    pool.empty()
    for tape in pool.tapes:
        erase_marker(tape)
    return {"packets": results, "setup_pool_peak": pool.peak,
            "scope": "complete exact LU preparation and rounded sequential boundary solves; global Schur assembly remains separate"}
