"""One global rounded Gaussian matrix, reused by its principal windows."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_exponentials import Exponentials
from gaussian_matrix import Matrix
from gaussian_rationals import Rational
from ring_words import Signed, difference, power_two
from router_metadata import indices, owned
from twiddle_setup import quotient
from words import need


class Axis:
    """Exact setup only; dense matrices never belong to the online data path."""
    def __init__(self, source_length, target_length, u, bandwidth, precision, pool):
        self.pool = pool
        self.fields = {}
        self.reflected_weights = 0
        self.weights = self.kernel = self.matrix = self.exponentials = None
        try:
            for name, value in (("s", source_length), ("t", target_length), ("u", u),
                                ("w", bandwidth), ("P", precision)):
                positive(value)
                self.keep(name, Count(value))
            need(compare(self.s, self.t) < 0, "Gaussian axis expands its source")
            with owned(Count(self.s), Count(self.w)) as (twice_s, twice_w):
                twice_s.multiply_small(2)
                twice_w.multiply_small(2)
                need(compare(self.t, twice_s) < 0 and compare(twice_w, self.s) < 0,
                     "near-one Gaussian ratio and distinct cyclic band entries")
            self.keep("K", subtract(self.t, self.s))
            self.keep("unit", power_two(self.P))
            self.keep("rho", Rational(Signed(Count(self.t)), Count(self.s)))
            self.keep("theta", Rational(Signed(Count(self.K)), Count(self.s)))
            self.keep("u_rational", Rational(Signed(Count(self.u)), Count.literal(1)))
            self.keep("zero", Count.literal(0))
            self.keep("one", Count.literal(1))
            self.keep("five", Count.literal(5))
            # max[u/(4 theta), u(rho*w+1/2)^2] bounds weights,
            # both kernel families, cross-cell exponents and D normalization.
            with owned(Count.product(self.u, self.s), Count(self.K)) as (numerator, denominator):
                denominator.multiply_small(4)
                first_bound = quotient(numerator, denominator, True)
            try:
                with owned(Count.product(self.t, self.w)) as (twice_tw,):
                    twice_tw.multiply_small(2)
                    twice_tw.add(self.s)
                    with owned(Count.product(twice_tw, twice_tw)) as (square,):
                        with owned(Count.product(self.u, square), Count.product(self.s, self.s)) as (top, bottom):
                            bottom.multiply_small(4)
                            second_bound = quotient(top, bottom, True)
                try:
                    self.keep("argument_bound", Count(first_bound if compare(first_bound, second_bound) >= 0
                                                       else second_bound))
                finally:
                    second_bound.close()
            finally:
                first_bound.close()
            self.exponentials = Exponentials(self.P, self.argument_bound)
            self.weights = Matrix(self.s, self.five, pool)
            self.prepare_weights()
            with owned(Count(self.w)) as (kernel_length,):
                kernel_length.increment()
                self.kernel = Matrix(kernel_length, self.one, pool, self.kernel_entry)
            self.matrix = Matrix(self.s, self.s, pool, self.matrix_entry)
            self.validate_rows()
        except BaseException:
            self.close()
            raise

    def keep(self, name, value):
        need(name not in self.fields, "one global Gaussian setup role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def close(self):
        for value in (self.matrix, self.kernel, self.weights, self.exponentials):
            if value is not None:
                value.close()
        self.matrix = self.kernel = self.weights = self.exponentials = None
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()

    def grid(self, numerator):
        return Rational(Signed(numerator), Count(self.unit))

    def field(self, index, column):
        need(column in (0, 1, 2, 3, 4), "fixed global Gaussian field")
        with owned(Count.literal(column)) as (field,):
            return self.weights.get(index, field)

    def prepare_weights(self):
        with owned(Rational.literal(1), Rational.literal(4)) as (one, four):
            with owned(one.over(four)) as (quarter,):
                for j in indices(self.s):
                    with owned(Count.product(self.t, j)) as (tj,):
                        with owned(Count(tj), Count(self.s)) as (top, bottom):
                            top.multiply_small(2)
                            top.add(self.s)
                            bottom.multiply_small(2)
                            q_index = quotient(top, bottom)
                        try:
                            with owned(Count.product(self.s, q_index)) as (sq,):
                                with owned(Signed(Count(tj)), Signed(Count(sq))) as (left, right):
                                    beta = Rational(difference(left, right), Count(self.s))
                            with owned(beta):
                                weight, diagonal = self.weight_pair(j, beta, quarter)
                                with owned(weight, diagonal):
                                    with owned(Rational(Signed(subtract(q_index, j)), Count.literal(1))) as (phase,):
                                        with owned(Rational(Signed(Count(q_index)), Count.literal(1))) as (nearest,):
                                            need(not weight.numerator.magnitude.zero(),
                                                 "positive global rounded Gaussian weight")
                                            for column, value in enumerate((weight, beta, phase, diagonal, nearest)):
                                                with owned(Count.literal(column)) as (field,):
                                                    self.weights.set(j, field, value)
                        finally:
                            q_index.close()

    def weight_pair(self, index, beta, quarter):
        with owned(subtract(self.s, index)) as (reflected,):
            if compare(reflected, index) < 0:
                with owned(self.field(reflected, 1)) as (earlier_beta,):
                    with owned(beta.times(beta), earlier_beta.times(earlier_beta)) as (first, second):
                        need(first.compare(second) == 0, "equal reflected Gaussian squared offset")
                weight = self.field(reflected, 0)
                try:
                    diagonal = self.field(reflected, 3)
                except BaseException:
                    weight.close()
                    raise
                self.reflected_weights += 1
                return weight, diagonal
        with owned(beta.times(beta)) as (square,):
            with owned(quarter.minus(square)) as (distance,):
                with owned(self.u_rational.times(distance)) as (scaled,):
                    with owned(scaled.over(self.theta)) as (exponent,):
                        weight = self.grid(self.exponentials.coefficient(exponent))
            try:
                with owned(self.u_rational.times(square)) as (exponent,):
                    with owned(Count(self.u)) as (normalization,):
                        normalization.multiply_small(2)
                        diagonal = self.grid(self.exponentials.coefficient(exponent, True, normalization))
                return weight, diagonal
            except BaseException:
                weight.close()
                raise

    def kernel_entry(self, distance, column):
        if distance.zero():
            return Rational.literal(1)
        with owned(Count.product(distance, distance)) as (square,):
            with owned(Rational(Signed(Count(square)), Count.literal(1))) as (integer,):
                with owned(self.rho.times(integer)) as (scaled,):
                    with owned(self.u_rational.times(scaled)) as (argument,):
                        return self.grid(self.exponentials.coefficient(argument))

    def matrix_entry(self, row, column):
        if compare(row, column) == 0:
            return Rational.literal(1)
        with owned(Signed(Count(column)), Signed(Count(row))) as (j, i):
            raw_delta = difference(j, i)
        try:
            direct = compare(raw_delta.magnitude, self.w) <= 0
            if direct:
                delta = raw_delta.copy()
            else:
                magnitude = subtract(self.s, raw_delta.magnitude)
                if compare(magnitude, self.w) > 0:
                    magnitude.close()
                    return Rational.literal(0)
                delta = Signed(magnitude, not raw_delta.negative)
            with owned(delta):
                with owned(self.field(row, 2)) as (first_phase,):
                    with owned(self.field(column, 2)) as (second_phase,):
                        same_cell = direct and first_phase.compare(second_phase) == 0
                if same_cell:
                    with owned(self.field(row, 0)) as (first_weight,):
                        with owned(self.field(column, 0)) as (second_weight,):
                            with owned(self.kernel.get(delta.magnitude, self.zero)) as (kernel,):
                                with owned(first_weight.times(kernel)) as (product,):
                                    return product.over(second_weight)
                with owned(Rational.integer(delta)) as (offset,):
                    with owned(self.rho.times(offset)) as (scaled,):
                        with owned(self.field(row, 1)) as (first_beta,):
                            with owned(scaled.plus(first_beta)) as (center,):
                                with owned(center.times(center)) as (first_square,):
                                    with owned(self.field(column, 1)) as (second_beta,):
                                        with owned(second_beta.times(second_beta)) as (second_square,):
                                            with owned(first_square.minus(second_square)) as (distance,):
                                                with owned(self.u_rational.times(distance)) as (argument,):
                                                    return self.grid(self.exponentials.coefficient(argument))
        finally:
            raw_delta.close()

    def validate_rows(self):
        for i in indices(self.s):
            total = Rational.literal(0)
            try:
                for j in indices(self.s):
                    if compare(i, j) == 0:
                        continue
                    with owned(self.matrix.get(i, j)) as (entry,):
                        need(not entry.numerator.negative, "nonnegative rounded Gaussian off-diagonal")
                        following = total.plus(entry)
                    total.close()
                    total = following
                with owned(Rational.literal(1)) as (one,):
                    need(total.compare(one) < 0, "global rounded Gaussian strict row dominance")
            finally:
                total.close()
