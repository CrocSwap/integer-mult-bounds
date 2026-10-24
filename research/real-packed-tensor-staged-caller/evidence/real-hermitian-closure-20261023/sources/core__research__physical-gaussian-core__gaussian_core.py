"""Complete C/interior/Schur/interior/D normalized principal-core consumer."""
from gaussian_sources import active
active()
from cardinal_counts import Count
from compact_counts import append_bits, copy_bits
from encoded import compare, subtract
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from gaussian_boundary import BandedSolve, subtract_row
from gaussian_interior import Interior, InteriorFactors
from gaussian_page import Cell, Header, skip_bits
from gaussian_rationals import read_count
from records import Tape
from ring_words import read_signed, scaled, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import OuterScope, borrowed_tape, erase_marker, initialize_marker, sealed_constructors
from words import BLANK, need


class Core:
    def __init__(self):
        self.word = FftWord(base_bits=4096)
        self.interior = Interior(self.word)
        self.boundary = BandedSolve(self.word)
        self.pool = ScratchPool(512)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.interior.idle()
        self.boundary.idle()
        need(self.interior.closed and not self.interior.pool.live and self.interior.output.read() == BLANK
             and self.boundary.closed and not self.boundary.pool.live and self.boundary.output.read() == BLANK,
             "consumed complete Gaussian child returns")

    def norm(self, real, imaginary, header):
        with owned(self.arithmetic.multiply(real, real, header.input_width)) as (first,):
            with owned(self.arithmetic.multiply(imaginary, imaginary, header.input_width)) as (second,):
                first.magnitude.add(second.magnitude)
                need(compare(first.magnitude, header.norm_bound) <= 0, "Gaussian disk-grid packet")

    def gather(self, source, page, selected, header, component):
        source.rewind()
        next_position = read_count(page)
        selected_count = Count.literal(0)
        try:
            need(compare(next_position, header.target_length) < 0, "first Gaussian selection offset")
            for index in indices(header.target_length):
                with owned(read_signed(source, header.input_width)) as (real,):
                    with owned(read_signed(source, header.input_width)) as (imaginary,):
                        if component == 0:
                            self.norm(real, imaginary, header)
                        if next_position is not None:
                            order = compare(index, next_position)
                            need(order <= 0, "monotone Gaussian target selection")
                            if order == 0:
                                with owned(scaled(real if component == 0 else imaginary, header.shift)) as (value,):
                                    write_signed(value, selected, header.width)
                                selected_count.increment()
                                previous, next_position = next_position, None
                                try:
                                    if compare(selected_count, header.m) < 0:
                                        next_position = read_count(page)
                                        need(compare(previous, next_position) < 0
                                             and compare(next_position, header.target_length) < 0,
                                             "strictly increasing in-range Gaussian selection")
                                finally:
                                    previous.close()
            need(source.read() == BLANK and next_position is None and compare(selected_count, header.m) == 0,
                 "complete Gaussian target halo and source selection")
        finally:
            if next_position is not None:
                next_position.close()
            selected_count.close()
            selected.rewind()
            source.rewind()

    def split(self, source, cell, header):
        boundary, inside = self.pool.acquire(), self.pool.acquire()
        try:
            if cell.inside.zero():
                copy_bits(source, boundary, cell.bits)
            else:
                copy_bits(source, boundary, header.prefix_bits)
                copy_bits(source, inside, cell.inside_bits)
                copy_bits(source, boundary, header.prefix_bits)
            boundary.rewind()
            inside.rewind()
            return boundary, inside
        except BaseException:
            boundary.clear()
            inside.clear()
            raise

    def first_cell(self, source, page, right_hand, cell, header):
        boundary = inside = edges = factors = None
        try:
            boundary, inside = self.split(source, cell, header)
            if cell.inside.zero():
                append_bits(boundary, right_hand)
            else:
                factors = InteriorFactors(cell.inside, header.width, header.P, self.pool)
                factors.load(page)
                edges = self.pool.acquire()
                with self.scope.suspended():
                    returned = self.interior.run(factors, inside)
                try:
                    copy_bits(returned, edges, header.prefix_bits)
                    with owned(subtract(cell.inside, header.band)) as (middle,):
                        with owned(Count.product(middle, header.width)) as (bits,):
                            skip_bits(returned, bits)
                    copy_bits(returned, edges, header.prefix_bits)
                    need(returned.read() == BLANK, "complete first Gaussian interior return")
                finally:
                    returned.clear()
                    erase_marker(returned)
                edges.rewind()
                for _ in indices(cell.boundary):
                    with owned(read_signed(boundary, header.width)) as (rhs,):
                        with owned(subtract_row(self.arithmetic, rhs, page, edges,
                                                header.band, header.width, header.P)) as (residual,):
                            with owned(truncate(residual, header.P)) as (rounded,):
                                write_signed(rounded, right_hand, header.width)
                need(boundary.read() == BLANK, "complete first-pass Gaussian boundary rows")
                skip_bits(page, header.coupling_bits)
            skip_bits(page, cell.bits)
        finally:
            if factors is not None:
                factors.close()
            for value in (boundary, inside, edges):
                if value is not None:
                    value.clear()

    def normalize_cell(self, boundary, inside, page, destination, position, emitted, cell, header):
        boundary.rewind()
        if inside is not None:
            inside.rewind()
        with owned(subtract(cell.length, header.w) if not cell.inside.zero() else Count.literal(0)) as (last_start,):
            for index in indices(cell.length):
                is_inside = not cell.inside.zero() and compare(index, header.w) >= 0 and compare(index, last_start) < 0
                with owned(read_signed(inside if is_inside else boundary, header.width)) as (value,):
                    with owned(read_signed(page, header.width)) as (diagonal,):
                        need(not diagonal.negative and compare(diagonal.magnitude, header.work_unit) <= 0,
                             "normalized Gaussian diagonal in the unit interval")
                        with owned(self.arithmetic.multiply(value, diagonal, header.width)) as (product,):
                            with owned(truncate(product, header.normal_shift)) as (rounded,):
                                if compare(position, header.core_offset) >= 0 and compare(position, header.core_end) < 0:
                                    write_signed(rounded, destination, header.input_width)
                                    emitted.increment()
                position.increment()
        need(boundary.read() == BLANK and (inside is None or inside.read() == BLANK),
             "complete source-order Gaussian merge")

    def second_cell(self, source, solution, page, destination, position, emitted, cell, header):
        original_boundary = original_inside = boundary = recovered_rhs = factors = None
        returned = None
        try:
            original_boundary, original_inside = self.split(source, cell, header)
            boundary = self.pool.acquire()
            copy_bits(solution, boundary, cell.boundary_bits)
            boundary.rewind()
            if not cell.inside.zero():
                factors = InteriorFactors(cell.inside, header.width, header.P, self.pool)
                factors.load(page)
                skip_bits(page, header.coupling_bits)
                recovered_rhs = self.pool.acquire()
                with owned(subtract(cell.inside, header.w)) as (last_edge,):
                    for index in indices(cell.inside):
                        with owned(read_signed(original_inside, header.width)) as (value,):
                            if compare(index, header.w) < 0 or compare(index, last_edge) >= 0:
                                with owned(subtract_row(self.arithmetic, value, page, boundary,
                                                        header.band, header.width, header.P)) as (residual,):
                                    with owned(truncate(residual, header.P)) as (rounded,):
                                        write_signed(rounded, recovered_rhs, header.width)
                            else:
                                write_signed(value, recovered_rhs, header.width)
                need(original_inside.read() == BLANK, "complete second Gaussian interior right-hand side")
                recovered_rhs.rewind()
                with self.scope.suspended():
                    returned = self.interior.run(factors, recovered_rhs)
            self.normalize_cell(boundary, returned, page, destination, position, emitted, cell, header)
        finally:
            if returned is not None:
                returned.clear()
                erase_marker(returned)
            if factors is not None:
                factors.close()
            for value in (original_boundary, original_inside, boundary, recovered_rhs):
                if value is not None:
                    value.clear()

    def scalar(self, source, page, destination, header, component):
        selected = right_hand = lower = upper = solution = None
        try:
            selected, right_hand, lower, upper, solution = (self.pool.acquire() for _ in range(5))
            self.gather(source, page, selected, header, component)
            with owned(Count.literal(0), Count.literal(0)) as (rows, boundaries):
                for _ in indices(header.cell_count):
                    with owned(Cell(page, header)) as (cell,):
                        self.first_cell(selected, page, right_hand, cell, header)
                        rows.add(cell.length)
                        boundaries.add(cell.boundary)
                need(compare(rows, header.m) == 0 and compare(boundaries, header.boundary_length) == 0
                     and selected.read() == BLANK, "complete first Gaussian cell pass")
            copy_bits(page, lower, header.lower_bits)
            copy_bits(page, upper, header.upper_bits)
            need(page.read() == BLANK, "complete Gaussian factor-page extent")
            for value in (lower, upper, right_hand):
                value.rewind()
            with self.scope.suspended():
                returned = self.boundary.run(lower, upper, right_hand, header.boundary_length,
                                              header.band, header.width, header.P)
            try:
                append_bits(returned, solution)
            finally:
                returned.clear()
                erase_marker(returned)
            solution.rewind()
            selected.rewind()
            header.repeat(page)
            header.skip_selection(page)
            with owned(Count.literal(0), Count.literal(0)) as (position, emitted):
                for _ in indices(header.cell_count):
                    with owned(Cell(page, header)) as (cell,):
                        self.second_cell(selected, solution, page, destination, position, emitted, cell, header)
                need(compare(position, header.m) == 0 and compare(emitted, header.core_length) == 0
                     and selected.read() == solution.read() == BLANK, "complete second Gaussian cell pass and core")
            skip_bits(page, header.lower_bits)
            skip_bits(page, header.upper_bits)
            need(page.read() == BLANK, "complete repeated Gaussian factor page")
            destination.rewind()
        finally:
            for value in (selected, right_hand, lower, upper, solution):
                if value is not None:
                    value.clear()

    def run(self, page, source):
        page, source = borrowed_tape(page), borrowed_tape(source)
        forbidden = (*self.pool.tapes, self.output, *self.interior.pool.tapes, self.interior.output,
                     *self.interior.convolution.pool.tapes, self.interior.convolution.output,
                     *self.boundary.pool.tapes, self.boundary.output, *self.word.pool.tapes,
                     self.word.output, *self.word.canonical)
        need(page is not source and page not in forbidden and source not in forbidden, "external Gaussian core ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK, "consume prior Gaussian core output")
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        header = real = imaginary = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    page.rewind()
                    header = Header(page)
                    real, imaginary = self.pool.acquire(), self.pool.acquire()
                    self.scalar(source, page, real, header, 0)
                    header.repeat(page)
                    self.scalar(source, page, imaginary, header, 1)
                    for _ in indices(header.core_length):
                        with owned(read_signed(real, header.input_width)) as (first,):
                            with owned(read_signed(imaginary, header.input_width)) as (second,):
                                self.norm(first, second, header)
                                write_signed(first, self.output, header.input_width)
                                write_signed(second, self.output, header.input_width)
                    need(real.read() == imaginary.read() == BLANK, "complete complex Gaussian core return")
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (real, imaginary):
                        if value is not None:
                            value.clear()
                    if header is not None:
                        header.close()
                    page.rewind()
                    source.rewind()
                    self.pool.empty()
        finally:
            for value in self.pool.tapes:
                erase_marker(value)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
