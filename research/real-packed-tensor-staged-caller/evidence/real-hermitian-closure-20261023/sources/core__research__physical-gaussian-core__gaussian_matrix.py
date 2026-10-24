"""Polynomial-time exact setup matrices serialized on a fixed tape pool."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_rationals import Rational, read_rational, transfer_record, write_rational
from router_metadata import indices, owned
from session import borrowed_tape
from words import BLANK, need


class Matrix:
    def __init__(self, rows, columns, pool, entry=None):
        positive(rows)
        positive(columns)
        self.pool = pool
        self.rows = self.columns = self.total = self.current = self.scratch = None
        try:
            self.rows, self.columns = Count(rows), Count(columns)
            self.total = Count.product(rows, columns)
            self.current, self.scratch = pool.acquire(), pool.acquire()
            for i in indices(rows):
                for j in indices(columns):
                    with owned(Rational.literal(0) if entry is None else entry(i, j)) as (value,):
                        write_rational(value, self.current)
            self.current.rewind()
        except BaseException:
            self.close()
            raise

    def close(self):
        for value in (self.current, self.scratch):
            if value is not None:
                value.clear()
        for value in (self.rows, self.columns, self.total):
            if value is not None:
                value.close()
        self.rows = self.columns = self.total = self.current = self.scratch = None

    def position(self, row, column):
        need(compare(row, self.rows) < 0 and compare(column, self.columns) < 0,
             "exact matrix coordinate range")
        offset = Count.product(row, self.columns)
        offset.add(column)
        return offset

    def get(self, row, column):
        self.current.rewind()
        try:
            with owned(self.position(row, column)) as (offset,):
                for _ in indices(offset):
                    transfer_record(self.current)
            return read_rational(self.current)
        finally:
            self.current.rewind()

    def set(self, row, column, value):
        self.current.rewind()
        borrowed_tape(self.scratch).clear()
        try:
            with owned(self.position(row, column)) as (offset,):
                for index in indices(self.total):
                    if compare(index, offset) == 0:
                        transfer_record(self.current)
                        write_rational(value, self.scratch)
                    else:
                        transfer_record(self.current, self.scratch)
            need(self.current.read() == BLANK, "complete exact matrix record stream")
            self.current, self.scratch = self.scratch, self.current
            borrowed_tape(self.scratch).clear()
        except BaseException:
            borrowed_tape(self.scratch).clear()
            raise
        finally:
            self.current.rewind()


def inverse(matrix):
    """Exact no-pivot Gauss-Jordan setup with reduction after each operation."""
    need(compare(matrix.rows, matrix.columns) == 0, "square exact inverse")
    dimension = matrix.rows

    def entry(i, j):
        if compare(j, dimension) < 0:
            return matrix.get(i, j)
        with owned(subtract(j, dimension)) as (column,):
            return Rational.literal(1 if compare(i, column) == 0 else 0)

    with owned(Count(dimension)) as (twice,):
        twice.multiply_small(2)
        augmented = Matrix(dimension, twice, matrix.pool, entry)
    try:
        for k in indices(dimension):
            with owned(augmented.get(k, k)) as (pivot,):
                need(not pivot.numerator.negative and not pivot.numerator.magnitude.zero(),
                     "positive exact setup pivot")
                for j in indices(augmented.columns):
                    with owned(augmented.get(k, j)) as (previous,):
                        if previous.numerator.magnitude.zero():
                            continue
                        with owned(previous.over(pivot)) as (value,):
                            augmented.set(k, j, value)
            for i in indices(dimension):
                if compare(i, k) == 0:
                    continue
                with owned(augmented.get(i, k)) as (factor,):
                    if factor.numerator.magnitude.zero():
                        continue
                    for j in indices(augmented.columns):
                        with owned(augmented.get(k, j)) as (source,):
                            if source.numerator.magnitude.zero():
                                continue
                            with owned(augmented.get(i, j)) as (previous,):
                                with owned(factor.times(source)) as (product,):
                                    with owned(previous.minus(product)) as (value,):
                                        augmented.set(i, j, value)

        def right(i, j):
            with owned(Count(j)) as (column,):
                column.add(dimension)
                return augmented.get(i, column)

        return Matrix(dimension, dimension, matrix.pool, right)
    finally:
        augmented.close()


def lu(matrix):
    """Exact Doolittle setup; callers serialize only the verified bands."""
    need(compare(matrix.rows, matrix.columns) == 0, "square exact LU")
    dimension = matrix.rows
    lower = Matrix(dimension, dimension, matrix.pool)
    upper = None
    succeeded = False
    try:
        upper = Matrix(dimension, dimension, matrix.pool)
        for i in indices(dimension):
            with owned(Rational.literal(1)) as (one,):
                lower.set(i, i, one)
            for j in indices(dimension):
                if compare(j, i) < 0:
                    continue
                value = matrix.get(i, j)
                try:
                    for k in indices(i):
                        with owned(lower.get(i, k)) as (a,):
                            with owned(upper.get(k, j)) as (b,):
                                with owned(a.times(b)) as (product,):
                                    following = value.minus(product)
                        value.close()
                        value = following
                    upper.set(i, j, value)
                finally:
                    value.close()
            with owned(upper.get(i, i)) as (pivot,):
                need(not pivot.numerator.negative and not pivot.numerator.magnitude.zero(),
                     "positive exact LU pivot")
                for j in indices(dimension):
                    if compare(j, i) <= 0:
                        continue
                    value = matrix.get(j, i)
                    try:
                        for k in indices(i):
                            with owned(lower.get(j, k)) as (a,):
                                with owned(upper.get(k, i)) as (b,):
                                    with owned(a.times(b)) as (product,):
                                        following = value.minus(product)
                            value.close()
                            value = following
                        with owned(value.over(pivot)) as (quotient,):
                            lower.set(j, i, quotient)
                    finally:
                        value.close()
        succeeded = True
        return lower, upper
    finally:
        if not succeeded:
            lower.close()
            if upper is not None:
                upper.close()
