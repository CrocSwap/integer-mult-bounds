"""A separate fixed-register diagnostic for the supplied-grid arithmetic lemma.

This is not a replacement of the predecessor kernel or a physical tape emitter.
The seven registers model arithmetic live values, not Python heap allocation.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Frame:
    def __init__(self, width):
        self.width = width
        self.limit = 1 << (width - 1)
        self.registers = [0] * 7
        self.peak = 0
        self.iterations = 0
        self.writes = 0

    def put(self, index, value):
        if not -self.limit <= value < self.limit:
            raise OverflowError("arithmetic word exceeds declared signed width")
        self.registers[index] = value
        self.peak = max(self.peak, abs(value).bit_length() + 1)
        self.writes += 1

    def multiply(self, left, right):
        negative = (left < 0) != (right < 0)
        self.put(4, abs(left))
        self.put(5, abs(right))
        self.put(6, 0)
        while self.registers[5]:
            self.iterations += 1
            if self.registers[5] & 1:
                self.put(6, self.registers[6] + self.registers[4])
            self.put(5, self.registers[5] >> 1)
            if self.registers[5]:
                self.put(4, self.registers[4] << 1)
        if negative:
            self.put(6, -self.registers[6])


def multiply_grid(u, v, bits, data_bits, *, diagnostic_width=None):
    need(type(bits) is int and type(data_bits) is int
         and data_bits >= 2 and 1 <= bits <= data_bits, "1 <= P <= B, B >= 2")
    need(isinstance(u, (tuple, list)) and isinstance(v, (tuple, list))
         and len(u) == len(v) == 2, "two complex grid numerators")
    inputs = tuple(u) + tuple(v)
    limit = 1 << (data_bits - 1)
    need(all(type(x) is int and -limit <= x < limit for x in inputs),
         "signed B-bit supplied inputs")
    width = 2 * data_bits + 1
    frame = Frame(width if diagnostic_width is None else diagnostic_width)
    frame.put(3, 1 << (bits - 1))
    for output, first, second, subtract in ((0, (0, 2), (1, 3), True),
                                           (1, (0, 3), (1, 2), False)):
        frame.multiply(inputs[first[0]], inputs[first[1]])
        frame.put(2, frame.registers[6])
        frame.multiply(inputs[second[0]], inputs[second[1]])
        frame.put(2, frame.registers[2] - frame.registers[6] if subtract
                  else frame.registers[2] + frame.registers[6])
        frame.put(2, frame.registers[2] + frame.registers[3])
        frame.put(output, frame.registers[2] >> bits)
    for index in range(2, 7):
        frame.put(index, 0)
    return tuple(frame.registers[:2]), frame
