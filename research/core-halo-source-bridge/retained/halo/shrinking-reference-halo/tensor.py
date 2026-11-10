"""One local sparse rectangle on a fixed pool of sequential tape roles.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The full-source gather and the final dense unique-return merge are separate.
"""
from dataclasses import dataclass
import shrinking_halo_engine as M


def put_unsigned(tape, value, width):
    M.need(type(value) is int and 0 <= value < (1 << width), "unsigned key carrier")
    for shift in range(width - 1, -1, -1):
        tape.write((value >> shift) & 1); tape.step(1)


def get_unsigned(tape, width):
    value = 0
    for _ in range(width):
        value = 2 * value + tape.read(); tape.step(1)
    return value


@dataclass(frozen=True)
class Archive:
    tape: M.Tape
    plans: tuple
    source_ids: tuple


def pack_tables(tables, bill):
    """Consume one prepared axis table at a time into ONE protected archive.

    A generator is sufficient: no simultaneous family of physical axis tapes
    is required. Each old table body is erased before advancing the iterator.
    The finite tuple of descriptors is charged as an encoded control block.
    """
    archive = M.Tape(bill, "global band archive")
    plans, source_ids = [], []
    bits = None
    for table in tables:
        if bits is None:
            bits = table.plan.bits
        M.need(table.plan.bits == bits and table.tape.head == 0, "common archive grid/origin")
        table.tape.bill = bill
        for _ in range(table.plan.period * table.plan.band):
            coefficient = M.get_int(table.tape, table.plan.coefficient_width)
            M.put_int(archive, coefficient, table.plan.coefficient_width)
            bill.control_steps += 1
        table.tape.readonly = False; table.tape.clear()
        plans.append(table.plan); source_ids.append(table.source_id)
    M.need(plans, "nonempty band archive")
    archive.rewind(); archive.readonly = True
    return Archive(archive, tuple(plans), tuple(source_ids))


def archive_page(archive, axis, lower, length, page_tape, bill):
    """One/two full ARCHIVE scans per local axis, never per spectator line."""
    M.need(type(axis) is int and 0 <= axis < len(archive.plans), "archive axis")
    p = archive.plans[axis]
    M.need(type(lower) is int and type(length) is int and 0 < length < p.period,
           "nonaliasing local page")
    M.need(archive.tape.head == 0 and archive.tape.readonly, "protected archive origin")
    M.need(page_tape.head == 0 and not page_tape.readonly and page_tape.live_bits == 0,
           "reusable blank local page")
    archive.tape.bill = page_tape.bill = bill
    begin = lower % p.period
    first = min(length, p.period - begin)
    spans = [(begin, begin + first)]
    if first < length:
        spans.append((0, length - first))
    for begin, end in spans:
        for catalog_axis, pp in enumerate(archive.plans):
            for row in range(pp.period):
                emit = catalog_axis == axis and begin <= row < end
                for _ in range(pp.band):
                    coefficient = M.get_int(archive.tape, pp.coefficient_width)
                    if emit:
                        M.put_int(page_tape, coefficient, pp.coefficient_width)
                bill.control_steps += pp.band + 1
        archive.tape.rewind(); bill.page_scans += 1
    M.need(page_tape.live_bits == length * p.band * p.coefficient_width, "complete local page")
    page_tape.rewind(); page_tape.readonly = True
    return M.Page(page_tape, p, lower, length, archive.source_ids[axis])


@dataclass(frozen=True)
class Layout:
    targets: tuple
    lowers: tuple
    lengths: tuple
    field_widths: tuple
    field_shifts: tuple
    key_width: int
    data_width: int
    bits: int
    radius: int

    @classmethod
    def make(cls, plans, targets):
        M.need(len(plans) == len(targets) and plans, "complete tensor axis metadata")
        bits, radius = plans[0].bits, plans[0].radius
        M.need(all(p.bits == bits and p.radius == radius for p in plans),
               "one incoming/output tensor grid and radius")
        lowers, lengths, widths = [], [], []
        for p, target in zip(plans, targets):
            M.need(type(target) is tuple and len(target) == 2 and
                   all(type(x) is int for x in target) and target[1] > 0, "target axis interval")
            lo, length = target[0] - p.halo, target[1] + 2 * p.halo
            M.need(length < p.period, "each saved axis has unique canonical coordinates")
            lowers.append(lo); lengths.append(length); widths.append(max(1, (length - 1).bit_length()))
        shifts, total = [0] * len(plans), 0
        for i in range(len(plans) - 1, -1, -1):
            shifts[i] = total; total += widths[i]
        return cls(tuple(targets), tuple(lowers), tuple(lengths), tuple(widths), tuple(shifts),
                   total, plans[0].data_width, bits, radius)

    @property
    def record_bits(self):
        return self.key_width + 2 * self.data_width

    @property
    def volume(self):
        result = 1
        for length in self.lengths:
            result *= length
        return result

    def key(self, offsets):
        M.need(len(offsets) == len(self.lengths), "complete coordinate tuple")
        key = 0
        for offset, length, shift in zip(offsets, self.lengths, self.field_shifts):
            M.need(type(offset) is int and 0 <= offset < length, "local coordinate range")
            key += offset << shift
        return key

    def coordinate(self, key, axis):
        return (key >> self.field_shifts[axis]) & ((1 << self.field_widths[axis]) - 1)

    def without_axis(self, key, axis):
        mask = ((1 << self.field_widths[axis]) - 1) << self.field_shifts[axis]
        return key & ~mask


def put_record(tape, key, value, layout):
    put_unsigned(tape, key, layout.key_width)
    M.put_complex(tape, value, layout.data_width)


def get_record(tape, layout):
    return get_unsigned(tape, layout.key_width), M.get_complex(tape, layout.data_width)


def coordinate_odometer(lengths):
    """Metadata convenience; encoded carries are explicitly charged in proof."""
    coordinate = [0] * len(lengths)
    while True:
        yield tuple(coordinate)
        axis = len(lengths) - 1
        while axis >= 0 and coordinate[axis] + 1 == lengths[axis]:
            coordinate[axis] = 0; axis -= 1
        if axis < 0:
            return
        coordinate[axis] += 1


def rectangle_input(layout, values, bill, tape=None):
    """Charged codec from lexicographic payload stream, no indexed data lookup."""
    tape = tape if tape is not None else M.Tape(bill, "rectangle current")
    M.need(tape.head == 0 and tape.live_bits == 0 and not tape.readonly, "blank reusable rectangle role")
    tape.bill = bill
    stream = iter(values)
    for offsets in coordinate_odometer(layout.lengths):
        try:
            value = next(stream)
        except StopIteration as error:
            raise ValueError("incomplete saved rectangle") from error
        M.need(type(value) is tuple and len(value) == 2 and all(type(x) is int for x in value)
               and abs(value[0]) + abs(value[1]) <= layout.radius * (1 << layout.bits),
               "saved rectangle data/radius")
        put_record(tape, layout.key(offsets), value, layout)
        bill.control_steps += len(layout.lengths) + 1
    try:
        next(stream)
    except StopIteration:
        pass
    else:
        raise ValueError("extra saved rectangle payload")
    tape.rewind()
    return tape


def expose_axis(current, count, axis, layout, buckets, bill):
    """Stable LSD distribution into two fixed buckets, then full concatenation."""
    M.need(current.head == 0 and not current.readonly, "owned rectangle origin")
    M.need(current.live_bits == count * layout.record_bits, "complete sparse body")
    order = (axis,) + tuple(j for j in range(len(layout.lengths) - 1, -1, -1) if j != axis)
    passes = 0
    for field in order:
        for bit in range(layout.field_widths[field]):
            M.need(all(t.head == 0 and t.live_bits == 0 for t in buckets),
                   "blank fixed radix buckets")
            sizes = [0, 0]
            position = layout.field_shifts[field] + bit
            for _ in range(count):
                key, value = get_record(current, layout)
                destination = (key >> position) & 1
                put_record(buckets[destination], key, value, layout)
                sizes[destination] += 1
                bill.control_steps += 1
            current.clear()
            for bucket, size in zip(buckets, sizes):
                bucket.rewind()
                for _ in range(size):
                    key, value = get_record(bucket, layout)
                    put_record(current, key, value, layout)
                    bill.control_steps += 1
                bucket.clear()
            current.rewind(); passes += 1
    return passes


@dataclass(frozen=True)
class TensorOutput:
    tape: M.Tape
    count: int
    layout: Layout
    role_extents: tuple
    axis_receipts: tuple
    blank_roles: tuple


@dataclass(frozen=True)
class TensorWorkspace:
    rectangles: tuple
    buckets: tuple
    line_source: M.Tape
    iterates: tuple
    page: M.Tape

    @classmethod
    def create(cls, bill, first_rectangle=None):
        first = first_rectangle if first_rectangle is not None else M.Tape(bill, "rectangle current")
        return cls((first, M.Tape(bill, "rectangle next")),
                   (M.Tape(bill, "radix zero"), M.Tape(bill, "radix one")),
                   M.Tape(bill, "fixed borrowed line"),
                   (M.Tape(bill, "fixed iterate zero"), M.Tape(bill, "fixed iterate one")),
                   M.Tape(bill, "fixed local band page"))

    @property
    def roles(self):
        return self.rectangles + self.buckets + (self.line_source,) + self.iterates + (self.page,)


def apply_tensor(archive, targets, source, bill, workspace=None):
    """Consume one saved rectangle; return its complete target in lex order.

    There are eight local tape roles, independent of axis count and iteration
    count, plus the one protected global archive and bounded scalar/control
    tapes. No source/table preparation is repeated inside a spectator line.
    """
    layout = Layout.make(archive.plans, targets)
    M.need(source.head == 0 and not source.readonly
           and source.live_bits == layout.volume * layout.record_bits, "owned complete rectangle")
    pool = workspace if workspace is not None else TensorWorkspace.create(bill, source)
    roles = pool.roles
    M.need(len({id(t) for t in roles}) == 8 and any(t is source for t in pool.rectangles),
           "eight distinct fixed roles with designated input")
    M.need(all(t is source or (t.head == 0 and t.live_bits == 0 and not t.readonly) for t in roles),
           "all noninput fixed roles blank and reusable")
    for tape in roles:
        tape.bill = bill
    current = source
    following = pool.rectangles[1] if source is pool.rectangles[0] else pool.rectangles[0]
    buckets, line_source, iterates, page_tape = pool.buckets, pool.line_source, pool.iterates, pool.page
    count = layout.volume
    receipts = []
    for axis, p in enumerate(archive.plans):
        start_products, start_scans = bill.products, bill.page_scans
        page = archive_page(archive, axis, layout.lowers[axis], layout.lengths[axis], page_tape, bill)
        passes = expose_axis(current, count, axis, layout, buckets, bill)
        line_length = layout.lengths[axis]
        M.need(count % line_length == 0, "complete spectator lines")
        lines = count // line_length
        target_lower, target_length = layout.targets[axis]
        previous_spectator = -1
        for _ in range(lines):
            spectator = None
            for position in range(line_length):
                key, value = get_record(current, layout)
                other = layout.without_axis(key, axis)
                if spectator is None:
                    spectator = other
                    M.need(spectator > previous_spectator, "unique ordered spectator line")
                    previous_spectator = spectator
                M.need(other == spectator and layout.coordinate(key, axis) == position,
                       "full ordered local dependency line")
                M.put_complex(line_source, value, p.data_width)
                bill.control_steps += len(layout.lengths) + 1
            line_source.rewind(); line_source.readonly = True
            output = M.apply_line(page, line_source, target_lower, target_length, bill,
                                  workspace=iterates)
            for offset in range(target_length):
                value = M.get_complex(output.tape, p.data_width)
                coordinate = target_lower - layout.lowers[axis] + offset
                key = spectator | (coordinate << layout.field_shifts[axis])
                put_record(following, key, value, layout)
                bill.control_steps += len(layout.lengths) + 1
            output.tape.clear()
            line_source.readonly = False; line_source.clear()
        current.clear(); following.rewind()
        current, following = following, current
        page_tape.readonly = False; page_tape.clear()
        count = lines * target_length
        M.need(current.live_bits == count * layout.record_bits, "exact next tensor rectangle")
        receipts.append(dict(axis=axis, input_lines=lines, line_length=line_length,
                             target_length=target_length, radix_passes=passes,
                             page_scans=bill.page_scans - start_scans,
                             products=bill.products - start_products, output_records=count))
    blank = tuple(t for t in roles if t is not current)
    M.need(all(t.head == 0 and t.live_bits == 0 for t in blank),
           "all nonreturn fixed roles erased")
    M.need(current.head == archive.tape.head == 0, "tensor/archive return origins")
    return TensorOutput(current, count, layout,
                        tuple((t.name, t.extent) for t in roles), tuple(receipts), blank)


def consume_tensor(output):
    """Return lifted coordinates, payloads; consume and clear the live output."""
    layout = output.layout
    result = []
    previous = -1
    for _ in range(output.count):
        key, value = get_record(output.tape, layout)
        M.need(key > previous, "unique lexicographic target key")
        previous = key
        coordinates = tuple(layout.lowers[i] + layout.coordinate(key, i)
                            for i in range(len(layout.lengths)))
        M.need(all(lo <= x < lo + length for x, (lo, length) in zip(coordinates, layout.targets)),
               "target-only tensor output")
        result.append((coordinates, value))
    output.tape.clear()
    M.need(output.tape.head == 0 and output.tape.live_bits == 0, "tensor return cleanup")
    return tuple(result)
