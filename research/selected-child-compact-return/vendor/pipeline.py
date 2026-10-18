"""Whole selected child, one column, composed with sequential parking return."""
from dataclasses import asdict

import streams


class TrackingTape(streams.Tape):
    """Track actual source/working tape extents without changing the primitives."""
    def __init__(self, meter, data=b''):
        super().__init__(meter, data)
        if not hasattr(meter, 'tapes'):
            meter.tapes, meter.live, meter.peak = [], 0, 0
        meter.tapes.append(self)
        meter.live += len(self.data)
        meter.peak = max(meter.peak, meter.live)

    def write(self, value):
        super().write(value)
        self.meter.live += len(value)
        self.meter.peak = max(self.meter.peak, self.meter.live)

    def erase(self):
        self.meter.live -= len(self.data)
        super().erase()


# Load the authenticated descendants after this observational tape subclass.
streams.Tape = TrackingTape
from streams import Meter, copy, need
from compact import Layout
from monomial import execute_monomial, binary_word
from arithmetic import Grid, c_axis


class Park:
    """A sequential LIFO above an opaque ancestor boundary; lengths are descriptors."""
    def __init__(self, meter, prefix):
        self.meter = meter
        self.cells = bytearray(prefix)
        self.floor = len(prefix)
        self.head = self.floor
        self.minimum_head = self.floor
        self.peak = self.floor

    def push(self, source):
        source.rewind()
        size = len(source.data)
        for _ in range(size):
            self.cells.append(source.read(1)[0])
            self.head += 1
            self.meter.writes += 1
            self.meter.moves += 1
        self.peak = max(self.peak, self.head)
        source.finish()
        source.erase()
        return size

    def pop(self, size):
        reverse = TrackingTape(self.meter)
        for _ in range(size):
            need(self.head > self.floor, 'opaque ancestor boundary')
            self.head -= 1
            self.minimum_head = min(self.minimum_head, self.head)
            value = self.cells.pop()
            self.meter.reads += 1
            self.meter.erases += 1
            self.meter.moves += 1
            reverse.write(bytes((value,)))
        # Read the temporary in the opposite direction, restoring stream order.
        out = TrackingTape(self.meter)
        while reverse.head:
            reverse.head -= 1
            out.write(bytes((reverse.data[reverse.head],)))
            self.meter.reads += 1
            self.meter.moves += 1
        reverse.erase()
        out.rewind()
        return out


def rows_monomial(source, layout, recipe, bits, outer_rows, inverse=False):
    """Apply the exact complete-field adapter to each outer row, then concatenate."""
    volume = layout.records * layout.record_bits
    need(len(source.data) == outer_rows * volume, 'whole nonbinary row packet')
    source.rewind()
    out = TrackingTape(source.meter)
    for _ in range(outer_rows):
        row = TrackingTape(source.meter)
        copy(source, row, volume)
        row.rewind()
        row = execute_monomial(row, layout, recipe, 1, 1, 1, 0, bits, inverse)
        copy(row, out, volume)
        row.finish()
        row.erase()
    source.finish()
    source.erase()
    out.rewind()
    return out


def child(source, recipe, grid, outer_rows, coefficients, inverse=False, round_child=False):
    fields = (('spectator', 1),) + tuple(('v' + str(i), 1) for i in range(9))
    layout = Layout(fields, 2 * grid.bits * coefficients)
    before, after = ('left', 'right') if inverse else ('right', 'left')
    source = rows_monomial(source, layout, recipe[before], grid.bits, outer_rows, inverse)
    for axis in reversed(range(8)) if inverse else range(8):
        source = c_axis(source, 10, axis + 1, coefficients, grid, inverse, outer_rows)
    if round_child:
        # Deliberate forbidden return quantization to the original four-bit grid.
        numbers = decode(source.data, grid.bits)
        quantum = 1 << (grid.fraction_bits - 4)
        numbers = [tuple((1 if v >= 0 else -1) * (abs(v) // quantum) * quantum for v in pair)
                   for pair in numbers]
        replacement = TrackingTape(source.meter, encode(numbers, grid.bits))
        source.erase()
        source = replacement
    source = rows_monomial(source, layout, recipe[after], grid.bits, outer_rows, inverse)
    need(not grid.workspace and source.head == 0, 'child scratch and head return')
    return source


def invoke(active, inactive, park, recipe, grid, outer_rows, coefficients,
           inverse=False, round_child=False, wrong_pop=False):
    extents = [park.push(tape) for tape in inactive]
    active.rewind()
    argument = TrackingTape(active.meter)
    copy(active, argument, len(active.data))
    active.finish()
    active.erase()
    argument.rewind()
    returned = child(argument, recipe, grid, outer_rows, coefficients, inverse, round_child)
    output = TrackingTape(returned.meter)
    copy(returned, output, len(returned.data))
    returned.finish()
    returned.erase()
    output.rewind()
    order = range(len(extents)) if wrong_pop else reversed(range(len(extents)))
    restored = [None] * len(extents)
    for i in order:
        restored[i] = park.pop(extents[i])
    need(park.head == park.floor and len(park.cells) == park.floor, 'parking extent restored')
    survivors = {id(tape) for tape in [output] + restored}
    need(all(not tape.data and tape.head == 0 for tape in active.meter.tapes if id(tape) not in survivors),
         'all actual working tapes cleared')
    return output, restored


def encode(values, bits):
    result = bytearray()
    for pair in values:
        for value in pair:
            need(-(1 << (bits - 1)) < value < (1 << (bits - 1)), 'strict signed input headroom')
            result.extend((value >> i) & 1 for i in range(bits))
    return result


def decode(raw, bits):
    need(len(raw) % (2 * bits) == 0, 'complete Gaussian words')
    values = []
    for start in range(0, len(raw), 2 * bits):
        pair = []
        for k in range(2):
            word = raw[start + k * bits:start + (k + 1) * bits]
            value = sum(bit << j for j, bit in enumerate(word)) - (word[-1] << bits)
            pair.append(value)
        values.append(tuple(pair))
    return values


def report(meter, grid, park, recipe):
    return {'data_bit_meter':asdict(meter), 'arithmetic_bit_work':grid.arithmetic_steps,
            'exact_divisions':grid.exact_divisions, 'peak_arithmetic_words':grid.peak_words,
            'peak_tape_bits_excluding_parking':meter.peak,
            'peak_parking_bits_including_ancestor':park.peak,
            'parking_minimum_head':park.minimum_head, 'ancestor_extent':park.floor,
            'adapter_elementary_gate_counts':{name:len(binary_word(recipe[name])) for name in ('right','left')}}
