"""Once-rounded four-term rows with bounded signed integer arithmetic.

Produced by Nick Petalas. Apache-2.0.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Words:
    """A width observer; its capacity constants are outside the data program."""

    def __init__(self, width):
        require(type(width) is int and 8 <= width <= 3074, "word capacity")
        self.width = width
        self.peak = 0
        self.operations = 0

    def check(self, value):
        require(type(value) is int, "integer word")
        limit = 1 << (self.width - 1)
        if not -limit <= value < limit:
            raise OverflowError("signed word overflow")
        self.peak = max(self.peak, abs(value).bit_length() + 1)
        self.operations += 1
        return value

    def multiply(self, left, right):
        """Shift/add multiplication; no integer multiplication instruction."""
        self.check(left)
        self.check(right)
        negative = (left < 0) != (right < 0)
        term, digits = self.check(abs(left)), self.check(abs(right))
        result = 0
        for bit in range(digits.bit_length()):
            if (digits >> bit) & 1:
                result = self.check(result + term)
            if bit + 1 < digits.bit_length():
                term = self.check(term << 1)
        return self.check(-result if negative else result)

    def divide(self, numerator, denominator):
        """Unsigned binary division, using a fixed number of bit positions."""
        require(numerator >= 0 and denominator > 0, "division domain")
        require(denominator < (1 << (self.width - 2)), "division remainder capacity")
        self.check(numerator)
        self.check(denominator)
        quotient = remainder = 0
        for bit in range(self.width - 2, -1, -1):
            remainder = self.check((remainder << 1) + ((numerator >> bit) & 1))
            quotient = self.check(quotient << 1)
            if remainder >= denominator:
                remainder = self.check(remainder - denominator)
                quotient = self.check(quotient + 1)
        require(0 <= remainder < denominator, "division remainder invariant")
        return quotient, remainder


def validate(rows, state, data_bits, coefficient_bits):
    require(type(data_bits) is int and 2 <= data_bits <= 2048, "data width")
    require(type(coefficient_bits) is int and 1 <= coefficient_bits <= 256,
            "coefficient width")
    require(type(rows) in (tuple, list), "row collection")
    require(len(state) == 4 and len(rows) == 4, "four real coordinates")
    limit = 1 << (data_bits - 1)
    require(all(type(x) is int and -limit <= x < limit for x in state),
            "signed input numerators")
    for row in rows:
        require(type(row) in (tuple, list), "row representation")
        require(len(row) == 4, "four terms per row")
        for pair in row:
            require(type(pair) is tuple and len(pair) == 2, "rational pair")
            numerator, denominator = pair
            require(type(numerator) is int and type(denominator) is int,
                    "integer rational components")
            require(abs(numerator).bit_length() <= coefficient_bits
                    and 0 < denominator < (1 << coefficient_bits),
                    "coefficient height")


def rounded_row(row, state, words):
    denominator = 1
    for _, divisor in row:
        denominator = words.multiply(denominator, divisor)
    accumulator = 0
    for term_index in range(4):
        numerator = words.multiply(row[term_index][0], state[term_index])
        for divisor_index in range(4):
            if divisor_index != term_index:
                numerator = words.multiply(numerator, row[divisor_index][1])
        accumulator = words.check(accumulator + numerator)
    quotient, remainder = words.divide(words.check(abs(accumulator)), denominator)
    twice_remainder = words.check(remainder << 1)
    if accumulator < 0:
        result = -quotient - int(twice_remainder > denominator)
    else:
        result = quotient + int(twice_remainder >= denominator)
    return words.check(result)


def apply_gate(rows, state, data_bits, coefficient_bits):
    """Overwrite four grid numerators after all outputs have been computed."""
    require(type(state) is list, "mutable four-coordinate state")
    validate(rows, state, data_bits, coefficient_bits)
    words = Words(data_bits + 4 * coefficient_bits + 2)
    before = tuple(state)
    outputs = [rounded_row(row, before, words) for row in rows]
    for index in range(4):
        state[index] = outputs[index]
    return words
