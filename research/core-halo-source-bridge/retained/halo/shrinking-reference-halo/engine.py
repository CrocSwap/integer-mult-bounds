"""Sequential shrinking-domain normalized inverse action.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Classical fixed-source Horner iteration is inherited; this file supplies the
local shrinking domains, sequential band-page extraction and ownership trace.
Bit-tape movement is executed. Bounded integer arithmetic is a declared scalar
macro, with its ordinary schoolbook bit cost established in PROOF.md.
"""
from dataclasses import dataclass, field
from fractions import Fraction as Q
from hashlib import sha256


def need(condition, message):
    if not condition:
        raise ValueError(message)


def trunc(n, denominator):
    need(type(n) is int and type(denominator) is int and denominator > 0,
         "integer truncation domain")
    return (-1 if n < 0 else 1) * (abs(n) // denominator)


def inward(value, bits):
    value = Q(value)
    return trunc(value.numerator << bits, value.denominator)


@dataclass
class Bill:
    reads: int = 0
    writes: int = 0
    moves: int = 0
    products: int = 0
    additions: int = 0
    roundings: int = 0
    source_shifts: int = 0
    control_steps: int = 0
    peak_scalar_bits: int = 0
    setup_entries: int = 0
    setup_divisions: int = 0
    page_scans: int = 0
    maximum_single_tape_extent: int = 0

    def scalar(self, *values):
        self.peak_scalar_bits = max(self.peak_scalar_bits,
                                    *(abs(x).bit_length() + 1 for x in values))

    def record(self):
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


class Tape:
    """Binary tape; data may be accessed only at the current head.

    The host list implements tape cells, not a program-visible indexed array.
    snapshot() is an independent diagnostic, never a transition primitive.
    Blank cells are zero. Every cell beyond live_bits is already blank. Clear
    erases the complete current live body; retained blank backing stays paid
    in space but need not be erased again for every later shorter line.
    """
    def __init__(self, bill, name):
        self._cells = []
        self.head = 0
        self.live_bits = 0
        self.bill = bill
        self.name = name
        self.readonly = False

    @property
    def extent(self):
        return len(self._cells)

    def read(self):
        need(self.head < self.live_bits, "read beyond live encoded body")
        self.bill.reads += 1
        return self._cells[self.head] if self.head < self.extent else 0

    def write(self, bit):
        need(not self.readonly, "write to borrowed immutable tape")
        need(type(bit) is int and bit in (0, 1), "binary cell")
        if self.head >= self.extent:
            self._cells.extend([0] * (self.head + 1 - self.extent))
        self._cells[self.head] = bit
        self.live_bits = max(self.live_bits, self.head + 1)
        self.bill.writes += 1
        self.bill.maximum_single_tape_extent = max(self.bill.maximum_single_tape_extent, self.extent)

    def step(self, direction):
        need(type(direction) is int and direction in (-1, 1), "one-cell head move")
        need(self.head + direction >= 0, "left tape boundary")
        self.head += direction
        self.bill.moves += 1

    def walk(self, distance):
        need(type(distance) is int, "encoded head displacement")
        direction = -1 if distance < 0 else 1
        for _ in range(abs(distance)):
            self.step(direction)

    def rewind(self):
        self.walk(-self.head)

    def clear(self):
        need(not self.readonly, "clear borrowed immutable tape")
        self.rewind()
        occupied = self.live_bits
        for _ in range(occupied):
            self.write(0)
            self.step(1)
        self.rewind()
        self.live_bits = 0

    def snapshot(self):
        return bytes(self._cells)


def put_int(tape, value, width):
    need(type(value) is int and type(width) is int and width >= 2,
         "fixed-width integer")
    need(abs(value) < (1 << (width - 1)), "integer carrier overflow")
    tape.write(int(value < 0)); tape.step(1)
    for shift in range(width - 2, -1, -1):
        tape.write((abs(value) >> shift) & 1); tape.step(1)


def get_int(tape, width):
    sign = tape.read(); tape.step(1)
    magnitude = 0
    for _ in range(width - 1):
        magnitude = 2 * magnitude + tape.read(); tape.step(1)
    need(not (sign and magnitude == 0), "noncanonical negative zero")
    return -magnitude if sign else magnitude


def put_complex(tape, value, width):
    need(type(value) is tuple and len(value) == 2, "signed complex pair")
    put_int(tape, value[0], width); put_int(tape, value[1], width)


def get_complex(tape, width):
    return get_int(tape, width), get_int(tape, width)


@dataclass(frozen=True)
class Plan:
    period: int
    halfwidth: int
    bits: int
    terms: int
    normalizer_shift: int
    gap: Q
    radius: int = 1

    def __post_init__(self):
        need(all(type(x) is int for x in (self.period, self.halfwidth, self.bits,
             self.terms, self.normalizer_shift, self.radius)), "integer plan parameters")
        need(self.period > 0 and self.halfwidth >= 0
             and 2 * self.halfwidth < self.period, "unique cyclic band offsets")
        need(self.bits >= self.normalizer_shift >= 0 and self.terms >= 1
             and self.radius >= 1, "precision, iteration and radius domain")
        need(type(self.gap) in (int, Q) and 0 < self.gap <= 1, "positive rational gap")
        need((1 << self.normalizer_shift) * self.gap >= 1, "funded normalization")

    @property
    def band(self):
        return 2 * self.halfwidth + 1

    @property
    def halo(self):
        return (self.terms - 1) * self.halfwidth

    @property
    def coefficient_width(self):
        return self.bits + 2

    @property
    def data_width(self):
        return self.bits + self.radius.bit_length() + 1

    @property
    def numeric_error(self):
        return Q(self.band * self.radius + 2, 1 << self.bits) / self.gap

    @property
    def tail_error(self):
        return self.radius * (1 - self.gap) ** self.terms / (
            (1 << self.normalizer_shift) * self.gap)


@dataclass(frozen=True)
class Table:
    tape: Tape
    plan: Plan
    source_id: str


@dataclass(frozen=True)
class Page:
    tape: Tape
    plan: Plan
    lower: int
    length: int
    source_id: str


@dataclass(frozen=True)
class Output:
    tape: Tape
    lower: int
    length: int
    width: int
    blank_scratch: tuple = field(repr=False)


def prepare_table(plan, entry, source_id, bill):
    """entry(row, column) returns the exact fixed E=I-H coefficient.

    Generic entry-production cost remains explicit; source.py provides the
    authenticated Gaussian instantiation and its separately charged setup.
    All offsets, including zero entries, are generated and stored.
    """
    tape = Tape(bill, "global band table")
    largest_height = 0
    for row in range(plan.period):
        mass = Q(0)
        for offset in range(-plan.halfwidth, plan.halfwidth + 1):
            value = Q(entry(row, (row + offset) % plan.period))
            largest_height = max(largest_height, abs(value.numerator).bit_length(),
                                 value.denominator.bit_length())
            mass += abs(value)
            coefficient = inward(value, plan.bits)
            need(abs(Q(coefficient, 1 << plan.bits)) <= abs(value), "inward coefficient")
            need(abs(value - Q(coefficient, 1 << plan.bits)) < Q(1, 1 << plan.bits),
                 "coefficient error")
            put_int(tape, coefficient, plan.coefficient_width)
            bill.setup_entries += 1
            bill.setup_divisions += 1
        need(mass <= 1 - plan.gap, "actual source row gap")
        bill.control_steps += plan.band + 1
    tape.rewind(); tape.readonly = True
    return Table(tape, plan, source_id), largest_height


def extract_page(table, lower, length, bill, page_tape=None):
    """At most two COMPLETE ordered scans, including all skipped records.

    The lifted interval has length less than the physical period, so each
    canonical coordinate appears at most once. A wrapping tail is emitted
    before its head. No random seek into the global table is used.
    """
    plan = table.plan
    need(type(lower) is int and type(length) is int and 0 < length < plan.period,
         "nonaliasing lifted page interval")
    need(table.tape.head == 0, "global table origin")
    # Accounting ownership can change between calls; it is not encoded data.
    # Charge the repeated complete scan to THIS call, not to old preparation.
    table.tape.bill = bill
    start = lower % plan.period
    first = min(length, plan.period - start)
    spans = [(start, start + first)]
    if first < length:
        spans.append((0, length - first))
    page = page_tape if page_tape is not None else Tape(bill, "local band page")
    need(page.head == 0 and not page.readonly and page.live_bits == 0,
         "blank local page role")
    page.bill = bill
    for begin, end in spans:
        for row in range(plan.period):
            for _ in range(plan.band):
                value = get_int(table.tape, plan.coefficient_width)
                if begin <= row < end:
                    put_int(page, value, plan.coefficient_width)
            bill.control_steps += plan.band + 1
        table.tape.rewind()
        bill.page_scans += 1
    need(page.head == length * plan.band * plan.coefficient_width,
         "complete ordered page")
    page.rewind(); page.readonly = True
    return Page(page, plan, lower, length, table.source_id)


def input_tape(plan, values, bill):
    tape = Tape(bill, "borrowed input")
    for value in values:
        need(type(value) is tuple and len(value) == 2 and
             all(type(x) is int for x in value), "integer grid input")
        need(abs(value[0]) + abs(value[1]) <= plan.radius * (1 << plan.bits),
             "input radius")
        put_complex(tape, value, plan.data_width)
    tape.rewind(); tape.readonly = True
    return tape


def apply_line(page, source, target_lower, target_length, bill, workspace=None):
    """Return only the target; preserve borrowed input/page and both origins.

    source contains the entire saved dependency interval. All arithmetic is
    performed on encoded integer numerators; no Fraction or matrix oracle is
    used by the online recurrence. Other tensor coordinates are spectators.
    """
    p = page.plan
    need(type(target_lower) is int and type(target_length) is int and target_length > 0,
         "nonempty target interval")
    lower, length = target_lower - p.halo, target_length + 2 * p.halo
    need(page.lower == lower and page.length == length, "exact saved dependency domain")
    need(length < p.period, "no repeated canonical input coordinate")
    need(source.readonly and page.tape.readonly and source.head == page.tape.head == 0,
         "immutable origin-aligned input and page")
    source.bill = page.tape.bill = bill
    record_bits = 2 * p.data_width
    need(source.live_bits == length * record_bits, "complete input shape")
    if workspace is None:
        current, following = Tape(bill, "current iterate"), Tape(bill, "next iterate")
    else:
        need(type(workspace) is tuple and len(workspace) == 2
             and workspace[0] is not workspace[1], "two distinct fixed iterate roles")
        current, following = workspace
        need(all(t.head == 0 and not t.readonly and t.live_bits == 0 for t in workspace),
             "blank fixed iterate roles")
        current.bill = following.bill = bill
    scale = 1 << p.bits
    # First term z_1=trunc_q(x/a); no E row is needed for this term.
    for _ in range(length):
        x = get_complex(source, p.data_width)
        need(abs(x[0]) + abs(x[1]) <= p.radius * scale, "actual incoming radius")
        z = tuple(trunc(v, 1 << p.normalizer_shift) for v in x)
        put_complex(current, z, p.data_width)
        bill.roundings += 2; bill.source_shifts += 2; bill.control_steps += 1
        bill.scalar(*x, *z)
    source.rewind(); current.rewind()
    active_lower, active_length = lower, length
    for _ in range(1, p.terms):
        out_lower, out_length = active_lower + p.halfwidth, active_length - 2 * p.halfwidth
        source.walk((out_lower - lower) * record_bits)
        page.tape.walk((out_lower - lower) * p.band * p.coefficient_width)
        for row in range(out_length):
            x = get_complex(source, p.data_width)
            real = x[0] << (p.bits - p.normalizer_shift)
            imag = x[1] << (p.bits - p.normalizer_shift)
            bill.source_shifts += 2
            for _ in range(p.band):
                coefficient = get_int(page.tape, p.coefficient_width)
                z = get_complex(current, p.data_width)
                product_real, product_imag = coefficient * z[0], coefficient * z[1]
                real += product_real; imag += product_imag
                bill.products += 2; bill.additions += 2; bill.control_steps += 1
                bill.scalar(coefficient, *z, product_real, product_imag, real, imag)
                need(abs(real) + abs(imag) <= p.radius * scale * scale,
                     "partial exact accumulator radius")
            result = trunc(real, scale), trunc(imag, scale)
            need(abs(result[0]) + abs(result[1]) <= p.radius * scale,
                 "actual rounded iterate radius")
            put_complex(following, result, p.data_width)
            bill.roundings += 2; bill.control_steps += 1
            if row + 1 < out_length:
                current.walk(-2 * p.halfwidth * record_bits)
        need(current.head == active_length * record_bits, "complete neighbor-window traversal")
        source.rewind(); page.tape.rewind()
        current.clear(); following.rewind()
        current, following = following, current
        active_lower, active_length = out_lower, out_length
    need((active_lower, active_length) == (target_lower, target_length), "target-only return")
    need(source.head == page.tape.head == current.head == following.head == 0,
         "return origins")
    need(following.live_bits == 0, "cleared alternate iterate")
    return Output(current, active_lower, active_length, p.data_width, (following,))


def consume(output):
    """Caller read, clear and origin restoration; reads only the live prefix.

    An iterate buffer can retain a larger previously occupied blank suffix.
    The complete live body is cleared; the suffix is blank by invariant.
    """
    need(output.tape.head == 0, "output origin")
    result = tuple(get_complex(output.tape, output.width) for _ in range(output.length))
    output.tape.clear()
    need(output.tape.head == 0 and output.tape.live_bits == 0, "consumed output cleanup")
    return result


def tape_digest(tape):
    return sha256(tape.snapshot()).hexdigest()
