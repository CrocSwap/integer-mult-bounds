"""Complete source-box Gaussian expansion, chirp and compression caller."""
from tensor_sources import active
active()
from tensor_records import bounded_record_io
from cardinal_counts import Count, positive
from chirp_engine import Chirp
from compact_counts import append_bits
from encoded import compare, subtract
from expansion_records import Fields
from fft_arithmetic import Arithmetic
from records import Tape
from ring_words import Signed, power_two, read_signed, scaled, write_signed
from root_streams import RowPadding
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from tensor_catalogue import Catalogue
from tensor_gather import Gather
from tensor_lines import LineApply
from tensor_moves import FieldMove
from tensor_router import FullRouter
from tensor_windows import CoreAssembly, PeriodicWindows
from tensor_word import adapt_chirp
from tensor_twiddles import adapt_small_chirp
from words import BLANK, need


def product(*values):
    result = Count.literal(1)
    try:
        for value in values:
            following = Count.product(result, value)
            result.close()
            result = following
        return result
    except BaseException:
        result.close()
        raise


class Layout(Fields):
    """Encoded spectators for one original axis at a fixed schedule phase."""
    def __init__(self, plan, index, rows, before, after):
        super().__init__()
        try:
            self.keep("axis", plan.axis(index))
            for name in ("K_before", "K_after", "I_before", "I_after"):
                self.keep(name, Count.literal(1))
            for position in indices(plan.dimensions):
                side = compare(position, index)
                if side == 0:
                    continue
                with owned(plan.axis(position)) as (row,):
                    suffix = "before" if side < 0 else "after"
                    for prefix, factor in (("K_", row.tiles), ("I_", before if side < 0 else after)):
                        name = prefix+suffix
                        following = Count.product(getattr(self, name), factor)
                        self.fields[name].close()
                        self.fields[name] = following
            self.keep("move_C", product(rows, self.K_before, self.axis.tiles))
            self.keep("move_A", product(self.K_after, self.I_before))
            self.keep("move_R", product(plan.record_bits, self.I_after))
            self.keep("halo_C", product(rows, self.K_before))
            self.keep("halo_R", product(self.move_A, self.move_R))
            self.keep("line_C", product(rows, plan.coarse_product, self.I_before))
            self.keep("line_A", Count(self.I_after))
            self.keep("line_outer", product(rows, self.K_before))
            self.keep("line_count", product(self.K_after, self.I_before, self.I_after))
        except BaseException:
            self.close()
            raise


class Tensor:
    def __init__(self, chirp, router):
        need(isinstance(chirp, Chirp) and isinstance(router, FullRouter), "actual full tensor numerical and routing children")
        self.chirp, self.gather = adapt_small_chirp(adapt_chirp(chirp)), Gather(router)
        self.lines, self.move = LineApply(), FieldMove()
        self.windows, self.assembly, self.padding = PeriodicWindows(), CoreAssembly(), RowPadding()
        self.pool = ScratchPool(512)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.lines.expansion.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        self.current = self.following = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        for owner in (self.chirp, self.gather, self.lines, self.move):
            owner.idle()
        for owner in (self.chirp, self.gather, self.lines, self.move, self.windows, self.assembly, self.padding):
            need(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                 "consumed complete tensor child return")

    def call(self, owner, *parameters, **options):
        with self.scope.suspended():
            returned = owner.run(self.current, *parameters, **options)
        try:
            borrowed_tape(self.following).clear()
            append_bits(returned, self.following)
        finally:
            returned.clear()
            erase_marker(returned)
        borrowed_tape(self.current).clear()
        self.current, self.following = self.following, self.current
        self.current.rewind()

    def natural_padding(self, plan, rows, remove):
        for index in indices(plan.dimensions):
            with owned(plan.axis(index)) as (row,):
                prefixes, suffix = Count(rows), Count(plan.record_bits)
                try:
                    for position in indices(plan.dimensions):
                        side = compare(position, index)
                        if side == 0:
                            continue
                        with owned(plan.axis(position)) as (other,):
                            factor = other.s if (remove and side < 0) or (not remove and side > 0) else other.t
                            if side < 0:
                                following = Count.product(prefixes, factor)
                                prefixes.close()
                                prefixes = following
                            else:
                                following = Count.product(suffix, factor)
                                suffix.close()
                                suffix = following
                    self.call(self.padding, prefixes, row.s, row.t, suffix, remove)
                    self.last_counts["natural_padding"] += 1
                finally:
                    prefixes.close()
                    suffix.close()

    def regroup(self, plan, rows, inverse):
        self.call(self.gather, plan.flags, plan.axes, plan.ell, plan.inner_bits,
                  plan.p, plan.record_bits, rows, inverse=inverse)
        self.last_counts["gathers"] += 1

    def halo(self, plan, profile, layout, capacity, compression):
        self.call(self.move, layout.move_C, layout.move_A, plan.L, layout.move_R)
        row = layout.axis
        windows = profile.compression_windows if compression else profile.expansion_windows
        period = row.t if compression else row.s
        self.call(self.windows, windows, layout.halo_C, period, row.t, row.tiles, capacity, layout.halo_R)
        self.call(self.move, layout.move_C, layout.move_A, capacity, layout.move_R, right=True)
        self.last_counts["halos"] += 1

    def apply_lines(self, catalogue, plan, index, layout, capacity, compression):
        self.call(self.move, layout.line_C, layout.line_A, capacity, plan.record_bits, right=True)
        self.call(self.lines, catalogue, index, layout.line_outer, layout.line_count, compression=compression)
        self.call(self.move, layout.line_C, layout.line_A, plan.L, plan.record_bits)
        self.last_counts["compression_axes" if compression else "expansion_axes"] += 1

    def assemble(self, plan, profile, layout):
        self.call(self.move, layout.move_C, layout.move_A, plan.L, layout.move_R)
        row = layout.axis
        self.call(self.assembly, profile.cores, layout.halo_C, row.s, row.t, row.tiles, plan.L, layout.halo_R)
        self.call(self.move, layout.move_C, layout.move_A, plan.L, layout.move_R, right=True)
        self.last_counts["assembled_axes"] += 1

    def norm(self, real, imaginary, width, bound):
        with owned(self.arithmetic.multiply(real, real, width)) as (first,):
            with owned(self.arithmetic.multiply(imaginary, imaginary, width)) as (second,):
                first.magnitude.add(second.magnitude)
                need(compare(first.magnitude, bound) <= 0, "complete tensor disk-grid boundary")

    def boundary(self, source, target, plan, rows, opposite, restore):
        source.rewind()
        with owned(product(rows, plan.source_product)) as (records,):
            norm_bits = Count(plan.p)
            try:
                norm_bits.multiply_small(2)
                if not restore:
                    with owned(Count.literal(2)) as (two,):
                        smaller = subtract(norm_bits, two)
                    norm_bits.close()
                    norm_bits = smaller
                with owned(power_two(norm_bits)) as (bound,):
                    for _ in indices(records):
                        with owned(read_signed(source, plan.component_bits), read_signed(source, plan.component_bits)) as (real, imaginary):
                            first = second = None
                            try:
                                first = scaled(real, plan.gamma) if restore else real.copy()
                                second = scaled(imaginary, plan.gamma) if restore else imaginary.copy()
                                if opposite and not second.magnitude.zero():
                                    second.negative = not second.negative
                                self.norm(first, second, plan.component_bits, bound)
                                write_signed(first, target, plan.component_bits)
                                write_signed(second, target, plan.component_bits)
                            finally:
                                for value in (first, second):
                                    if value is not None:
                                        value.close()
                    need(source.read() == BLANK, "complete original source-box boundary")
            finally:
                norm_bits.close()
        source.rewind()

    def run(self, payload, catalogue, rows, opposite=False):
        need(type(opposite) is bool, "compiled source tensor Fourier direction")
        source, catalogue, rows = borrowed_tape(payload), borrowed_tape(catalogue), borrowed_count(rows)
        positive(rows)
        forbidden = (*self.pool.tapes, self.output)
        need(source is not catalogue and source not in forbidden and catalogue not in forbidden
             and rows.tape not in forbidden, "external complete tensor ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume previous complete tensor return")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(natural_padding=0, gathers=0, halos=0, expansion_axes=0,
                                compression_axes=0, assembled_axes=0, chirps=0)
        book = None
        succeeded = False
        try:
            with bounded_record_io(), sealed_constructors(), self.scope.installed():
                try:
                    book = Catalogue(catalogue, self.pool.acquire)
                    plan = book.plan
                    self.current, self.following = self.pool.acquire(), self.pool.acquire()
                    self.boundary(source, self.current, plan, rows, opposite, False)
                    self.current.rewind()
                    self.natural_padding(plan, rows, False)
                    self.regroup(plan, rows, False)
                    for index in indices(plan.dimensions):
                        with owned(book.profile(index), Layout(plan, index, rows, plan.L, plan.L)) as (profile, layout):
                            self.halo(plan, profile, layout, plan.expansion_capacity, False)
                            self.apply_lines(catalogue, plan, index, layout, plan.expansion_capacity, False)
                    self.regroup(plan, rows, True)
                    self.call(self.chirp, plan.sources, plan.flags, plan.axes, plan.ell, plan.p, rows)
                    self.last_counts["chirps"] += 1
                    self.regroup(plan, rows, False)
                    for index in indices(plan.dimensions):
                        with owned(book.profile(index), Layout(plan, index, rows, plan.target_halo, plan.L)) as (profile, layout):
                            self.halo(plan, profile, layout, plan.target_halo, True)
                    for index in indices(plan.dimensions):
                        with owned(Layout(plan, index, rows, plan.L, plan.target_halo)) as (layout,):
                            self.apply_lines(catalogue, plan, index, layout, plan.target_halo, True)
                    for index in indices(plan.dimensions):
                        with owned(book.profile(index), Layout(plan, index, rows, plan.L, plan.L)) as (profile, layout):
                            self.assemble(plan, profile, layout)
                    self.regroup(plan, rows, True)
                    self.natural_padding(plan, rows, True)
                    self.boundary(self.current, self.output, plan, rows, opposite, True)
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for tape in (self.current, self.following):
                        if tape is not None:
                            tape.clear()
                    self.current = self.following = None
                    if book is not None:
                        book.close()
                    source.rewind()
                    catalogue.rewind()
                    rows.rewind()
                    self.pool.empty()
        finally:
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
