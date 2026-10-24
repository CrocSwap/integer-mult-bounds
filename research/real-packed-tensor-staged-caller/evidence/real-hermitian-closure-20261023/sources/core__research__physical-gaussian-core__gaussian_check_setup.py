"""Independent exact identities for reduced rationals, matrix setup and rows."""
from fractions import Fraction
from math import gcd
from gaussian_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from compact_counts import write_fixed
    from gaussian_matrix import Matrix, inverse, lu
    from gaussian_rationals import Rational, read_rational, write_rational
    from gaussian_rows import reverse_records
    from records import Tape
    from ring_check_words import body, decode
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK

    def make(value):
        value = Fraction(value)
        return Rational(Signed(Count.literal(abs(value.numerator)), value < 0),
                        Count.literal(value.denominator))

    def number(value):
        n, d = decode(value.numerator.magnitude), decode(value.denominator)
        require(gcd(n, d) == 1 and d > 0, "reduced physical rational")
        return Fraction(-n if value.numerator.negative else n, d)

    def snapshot(value):
        tape = borrowed_tape(value.tape)
        return bytes(tape.cells), tape.head

    def matrix_values(matrix):
        result = []
        for i in range(decode(matrix.rows)):
            row = []
            for j in range(decode(matrix.columns)):
                with owned(Count.literal(i), Count.literal(j)) as (a, b):
                    with owned(matrix.get(a, b)) as (value,):
                        row.append(number(value))
            result.append(row)
        return result

    pool = ScratchPool(256)
    scope = OuterScope(pool)
    cases = 0
    values = (Fraction(0), Fraction(1), Fraction(-1), Fraction(17, 23), Fraction(-5, 7))
    with sealed_constructors(), scope.installed():
        try:
            for a in values:
                for b in values:
                    with owned(make(a), make(b), Count.literal(7)) as (left, right, precision):
                        saved = tuple(snapshot(x) for x in
                                      (left.numerator.magnitude, left.denominator,
                                       right.numerator.magnitude, right.denominator))
                        for operation, expected in (("plus", a+b), ("minus", a-b), ("times", a*b)):
                            with no_decode():
                                result = getattr(left, operation)(right)
                            with owned(result):
                                require(number(result) == expected, "exact encoded rational operation")
                        if b:
                            with no_decode():
                                result = left.over(right)
                            with owned(result):
                                require(number(result) == a/b, "exact encoded rational quotient")
                        with no_decode():
                            truncated = left.rounded(precision)
                            floor = left.integer_part()
                            ceil = left.integer_part(True)
                        with owned(truncated, floor, ceil):
                            def signed(x):
                                return (-1 if x.negative else 1)*decode(x.magnitude)
                            require(signed(truncated) == int(a*128), "signed dyadic truncation")
                            require(signed(floor) == a.__floor__() and signed(ceil) == a.__ceil__(),
                                    "signed floor and ceiling")
                        require(saved == tuple(snapshot(x) for x in
                                              (left.numerator.magnitude, left.denominator,
                                               right.numerator.magnitude, right.denominator)),
                                "rational setup preserves input carriers")
                        cases += 1
            with owned(Count.literal(3)) as (dimension,):
                source = [[Fraction(4), Fraction(-1), Fraction(0)],
                          [Fraction(1, 3), Fraction(5), Fraction(-1, 2)],
                          [Fraction(0), Fraction(1, 4), Fraction(3)]]
                # Host lookup creates this boundary fixture only. All matrix
                # elimination and its numerical indices use encoded tapes.
                matrix = Matrix(dimension, dimension, pool,
                                lambda i, j: make(source[decode(i)][decode(j)]))
                inv = lower = upper = None
                try:
                    with no_decode():
                        inv = inverse(matrix)
                        lower, upper = lu(matrix)
                    actual, low, high = (matrix_values(x) for x in (inv, lower, upper))
                    for i in range(3):
                        for j in range(3):
                            require(sum(source[i][k]*actual[k][j] for k in range(3)) == int(i == j),
                                    "exact inverse identity against independent rationals")
                            require(sum(low[i][k]*high[k][j] for k in range(3)) == source[i][j],
                                    "exact LU identity against independent rationals")
                    require(matrix_values(matrix) == source, "matrix setup preserves source")
                finally:
                    for value in (inv, lower, upper, matrix):
                        if value is not None:
                            value.close()
            with owned(Count.literal(4), Count.literal(3)) as (length, width):
                source, result, restored = pool.acquire(), pool.acquire(), pool.acquire()
                try:
                    for value in (0, 3, 5, 7):
                        with owned(Count.literal(value)) as (word,):
                            write_fixed(word, source, width)
                    original = body(borrowed_tape(source))
                    with no_decode():
                        reverse_records(source, result, length, width)
                        reverse_records(result, restored, length, width)
                    require(body(borrowed_tape(result)) == b"".join(
                        original[offset:offset+3] for offset in (9, 6, 3, 0)),
                            "record reversal preserves each record bit order")
                    require(body(borrowed_tape(restored)) == original
                            and body(borrowed_tape(source)) == original, "reversal involution and input preservation")
                finally:
                    for value in (source, result, restored):
                        value.clear()
            with owned(make(Fraction(-17, 23))) as (value,):
                tape = pool.acquire()
                try:
                    with no_decode():
                        write_rational(value, tape)
                        tape.rewind()
                        restored = read_rational(tape)
                    with owned(restored):
                        require(number(restored) == Fraction(-17, 23) and tape.read() == BLANK,
                                "canonical exact rational record")
                finally:
                    tape.clear()
        finally:
            pool.empty()
    require(not pool.live, "closed setup scratch pool")
    for tape in pool.tapes:
        erase_marker(tape)
        require(tape.head == 1 and all(v == BLANK for v in tape.cells), "setup scratch restoration")
    return {"rational_pairs": cases, "matrix_dimension": 3, "matrix_identities": 18,
            "record_reversal": [4, 3], "pool_peak": pool.peak}
