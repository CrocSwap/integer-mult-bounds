"""Sequential fallback adapters with explicit completed-child oracle calls.

Only child_oracle uses a random-access permutation model. Its full logical
volume and recursive width remain charged; its implementation is a premise.
The ADD and fixed-sign adapters below access payload tapes sequentially.
"""
from dataclasses import dataclass, field
from math import prod

from controlled_stream import Tape, Meter, controlled_add, copy_bits
from descriptor import require
from fallback_program import prepare, coefficient, child_descriptor, logical_column, paid_children, shape


@dataclass(frozen=True)
class Layout:
    dimension: int
    columns: int
    modulus: int
    unused: int
    gap: int
    payload: int

    @property
    def radices(self):
        n = self.dimension * self.columns
        return (self.modulus,)*n + (self.gap,) + (self.modulus,)*n

    @property
    def rows(self):
        return prod(self.radices)

    def axis(self, atom):
        n = self.dimension * self.columns
        return atom + int(atom >= n)

    def decode(self, row):
        values = []
        for radix in reversed(self.radices):
            row, digit = divmod(row, radix)
            values.append(digit)
        require(row == 0, "layout row extent")
        return values[::-1]

    def encode(self, values):
        row = 0
        for value, radix in zip(values, self.radices):
            require(0 <= value < radix, "layout digit extent")
            row = row*radix + value
        return row


@dataclass
class Execution:
    meter: Meter = field(default_factory=Meter)
    child_calls: list = field(default_factory=list)
    fixed_sign_passes: int = 0
    ordered_add_passes: int = 0
    matrix_preparations: int = 0


def prepared_for(control, execution, expected_shape, low_ancestors=False):
    form = prepare(control, low_only_ancestors=low_ancestors)
    require((form.dimension, form.columns, form.modulus, shape(form.operations)) == expected_shape,
            "one low-class instruction schedule")
    execution.matrix_preparations += form.matrix_preparations
    return form


def add_pass(source, controls, layout, operation_index, logical_j, execution,
             expected_shape, wrong_final=False, wrong_orientation=False,
             low_ancestors=False):
    reference = prepare(controls[0]);op = reference.operations[operation_index]
    f, m = layout.columns, layout.dimension
    target_t = logical_j if op.target < m else f-1-logical_j
    source_t = logical_j if op.source < m else f-1-logical_j
    target = layout.axis(op.target*f + target_t)
    src = layout.axis(op.source*f + source_t)
    require(target > src, "physical later-target atom")
    radices = layout.radices
    before = layout.unused * prod(radices[:src])
    middle = prod(radices[src+1:target])
    suffix = layout.payload * prod(radices[target+1:])

    def evaluate(control):
        form = prepared_for(control, execution, expected_shape, low_ancestors)
        current = form.operations[operation_index]
        field = current.coefficient.first if wrong_orientation else current.target
        j = logical_column(field, target_t, m, f)
        c = coefficient(form, current.coefficient, j, wrong_final)
        return c, form.arithmetic

    out = controlled_add(source, controls, before, layout.modulus, middle, suffix, evaluate)
    execution.ordered_add_passes += 1
    source.erase()
    return out


def pop_bit(tape):
    """One backward read/erase at the end of a scratch stream."""
    require(tape.head == len(tape.bits) and tape.head > 0, "scratch pop boundary")
    tape.head -= 1
    tape.meter.head_moves += 1
    tape.meter.payload_reads += 1
    tape.meter.scratch_erases += 1
    return tape.bits.pop()


def sign_pass(source, layout, axis, execution):
    """Y -> -Y: retain block0, reverse other block order, retain inner bits."""
    suffix = layout.payload * prod(layout.radices[axis+1:])
    slab = layout.modulus * suffix
    require(len(source.bits) % slab == 0, "complete fixed-sign slabs")
    source.rewind()
    out, reverse, block = (Tape(execution.meter) for _ in range(3))
    for _ in range(len(source.bits)//slab):
        copy_bits(source, out, suffix)
        copy_bits(source, reverse, (layout.modulus-1)*suffix)
        for _digit in range(layout.modulus-1):
            for _bit in range(suffix):
                block.write(pop_bit(reverse))
            for _bit in range(suffix):
                out.write(pop_bit(block))
        require(not reverse.bits and not block.bits and reverse.head == block.head == 0,
                "fixed-sign scratch closure")
    source.finished();source.erase();out.rewind()
    execution.fixed_sign_passes += 1
    return out


def child_oracle(source, controls, layout, first, second, width, weight_function,
                 execution, label):
    """Exact F_a on two blocks, standing in for a charged completed callee.

    This oracle is deliberately separate from sequential adapter measurements.
    Its list destination writes are not an implementation of the child.
    """
    require(width >= 1 and first+width <= second, "disjoint ordered child blocks")
    volume = len(source.bits)
    require(volume == len(controls)*layout.unused*layout.rows*layout.payload,
            "full child logical volume")
    execution.child_calls.append({"width":width, "volume":volume, "kind":label})
    out = [None]*volume
    for parent_index, control in enumerate(controls):
        weights = weight_function(control)
        require(len(weights) == width, "child descriptor extent")
        inverse = [pow(a, -1, layout.modulus) for a in weights]
        for stock in range(layout.unused):
            for row in range(layout.rows):
                values = layout.decode(row);target = values[:]
                for t in range(width):
                    i, k = layout.axis(first+t), layout.axis(second+width-1-t)
                    target[i] = weights[t]*values[k] % layout.modulus
                    target[k] = inverse[t]*values[i] % layout.modulus
                new_row = layout.encode(target)
                src = ((parent_index*layout.unused+stock)*layout.rows+row)*layout.payload
                dst = ((parent_index*layout.unused+stock)*layout.rows+new_row)*layout.payload
                require(out[dst] is None, "callee oracle address bijection")
                out[dst:dst+layout.payload] = source.bits[src:src+layout.payload]
    require(all(x is not None for x in out), "callee oracle full packet coverage")
    source.erase()
    return Tape(execution.meter, out)


def swap_pass(source, controls, layout, operation_index, execution, expected_shape,
              omit_reversal=False, low_ancestors=False):
    reference = prepare(controls[0]);op = reference.operations[operation_index]
    i, k, f, m = op.target, op.source, layout.columns, layout.dimension
    require(i < k, "ordered swap fields")
    same = (i < m) == (k < m)

    def reversal(tape):
        half = f//2
        if half == 0:
            return tape
        return child_oracle(tape, controls, layout, k*f, k*f+f-half, half,
                            lambda _p:[1]*half, execution, "orientation reversal")

    if same and not omit_reversal:
        source = reversal(source)

    def weights(control):
        form = prepared_for(control, execution, expected_shape, low_ancestors)
        current = form.operations[operation_index]
        descriptor = child_descriptor(form, current)
        values = [descriptor.value(t) for t in range(f)]
        require(values == [coefficient(form, current.coefficient, logical_column(i,t,m,f))
                           for t in range(f)], "generated child descriptor and physical weight order")
        return values

    source = child_oracle(source, controls, layout, i*f, k*f, f, weights,
                          execution, "weighted reversed child")
    if same:
        source = reversal(source)
    return source


def execute(raw, controls, layout, wrong_final=False, wrong_orientation=False,
            omit_reversal=False, low_ancestors=False):
    require(bool(controls) and layout.unused >= 1 and layout.gap >= 1 and
            layout.payload >= 1, "complete payload layout")
    reference = prepare(controls[0])
    expected = (reference.dimension, reference.columns, reference.modulus, shape(reference.operations))
    require((reference.dimension,reference.columns,reference.modulus) ==
            (layout.dimension,layout.columns,layout.modulus), "physical program dimensions")
    execution = Execution();source = Tape(execution.meter, raw)
    omitted = False
    for index, op in enumerate(reference.operations):
        if op.kind == "lower":
            for j in range(layout.columns):
                source = add_pass(source, controls, layout, index, j, execution,
                                  expected, wrong_final, wrong_orientation, low_ancestors)
        elif op.kind == "swap":
            omit_this = (omit_reversal and not omitted and layout.columns//2 > 0 and
                         (op.target < layout.dimension) == (op.source < layout.dimension))
            source = swap_pass(source, controls, layout, index, execution, expected,
                               omit_this, low_ancestors)
            omitted = omitted or omit_this
        else:
            for t in range(layout.columns):
                source = sign_pass(source, layout, layout.axis(op.target*layout.columns+t), execution)
    if not omit_reversal:
        require([x["width"] for x in execution.child_calls] == paid_children(reference),
                "literal recursive child widths")
    else:
        require(omitted, "one orientation child was removed")
    require(source.head == 0 and len(source.bits) == len(raw), "final payload boundary")
    return source.bits, execution
