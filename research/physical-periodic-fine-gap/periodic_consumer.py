"""Paid two-pass periodic Reference inverse on a fixed encoded tape cohort.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The Schur identity, RUN factors, band solver and fold permutation are inherited.
All variable loop bounds and all payload arithmetic below use encoded tapes.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from fft_arithmetic import Arithmetic
from gaussian_boundary import subtract_row, push_window
from gaussian_rationals import read_count
from folded_consumer import FoldedSolve, fold, unfold, origin
from run_consumer import RunInverse
from records import Tape
from ring_words import Signed, difference, read_signed, scaled, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


def bit(tape):
    value = tape.read()
    need(value in (0, 1), "complete periodic mask bit")
    tape.step(1)
    return value


def convert(source, target, length, source_width, target_width,
            source_precision, target_precision):
    """One monotone pass; negative downconversion truncates toward zero."""
    down = compare(source_precision, target_precision) >= 0
    with owned(subtract(source_precision, target_precision) if down else
               subtract(target_precision, source_precision)) as (shift,):
        for _ in indices(length):
            with owned(read_signed(source, source_width)) as (value,):
                with owned(truncate(value, shift) if down else scaled(value, shift)) as (result,):
                    write_signed(result, target, target_width)


def read_header(tape):
    """Five fixed control roles, never a variable host list of run headers."""
    values = [None] * 5
    try:
        for field in range(5):
            values[field] = read_count(tape)
        return tuple(values)
    except BaseException:
        for value in values:
            if value is not None:
                value.close()
        raise


class PeriodicInverse:
    def __init__(self):
        self.run_owner = RunInverse()
        self.folded_owner = FoldedSolve()
        self.pool = ScratchPool(512)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.folded_owner.solver.word, self.scope)
        self.output = Tape()
        self.closed, self.pending = True, False
        self.calls = self.block_passes = self.matrix_rows = self.run_converted_rows = 0
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def forbidden(self):
        return (*self.pool.tapes, self.output, *self.run_owner.forbidden(),
                *self.folded_owner.private_tapes())

    def idle(self):
        self.run_owner.idle()
        need(self.run_owner.closed and not self.run_owner.pool.live and
             self.run_owner.output.read() == BLANK, "consumed periodic run child")
        self.folded_owner.solver.idle()
        need(self.folded_owner.closed and not self.folded_owner.pending and
             not self.folded_owner.pool.live, "consumed periodic Schur child")

    def consume(self):
        need(self.closed and self.pending, "one pending periodic output")
        self.output.clear(); erase_marker(self.output)
        self.pending = False

    def extract(self, rhs, mask, real, imaginary, source_size, target_size, width):
        rhs.rewind(); mask.rewind()
        with owned(Count.literal(0)) as (seen,):
            for _ in indices(target_size):
                selected = bit(mask)
                for target in (real, imaginary):
                    with owned(read_signed(rhs, width)) as (value,):
                        if selected:
                            write_signed(value, target, width)
                if selected:
                    seen.increment()
            need(compare(seen, source_size) == 0, "selected mask cardinality")
            need(rhs.read() == mask.read() == BLANK, "complete target input and mask")
        rhs.rewind(); mask.rewind(); real.rewind(); imaginary.rewind()

    def merge(self, rhs, mask, real, imaginary, target_size, width):
        rhs.rewind(); mask.rewind(); real.rewind(); imaginary.rewind()
        for _ in indices(target_size):
            selected = bit(mask)
            for source in (real, imaginary):
                with owned(read_signed(rhs, width)) as (old,):
                    if selected:
                        copy_bits(source, self.output, width)
                    else:
                        write_signed(old, self.output, width)
        need(rhs.read() == mask.read() == real.read() == imaginary.read() == BLANK,
             "complete identity-hole merge")
        rhs.rewind(); mask.rewind(); real.rewind(); imaginary.rewind()

    def block_inverse(self, source, correction, result, pages, source_size,
                      boundary_size, run_count, width, precision):
        """Monotone per-run extraction; first pass returns only V B^-1 b."""
        buffers = [None] * 7
        try:
            for field in range(7):
                buffers[field] = self.pool.acquire()
            local_source, *local_pages = buffers
            source.rewind(); pages.boundary_mask.rewind(); pages.headers.rewind()
            for bank in pages.streams:
                bank.rewind()
            if correction is not None:
                correction.rewind()
            with owned(Count.literal(0), Count.literal(0)) as (seen, boundary_seen):
                for _ in indices(run_count):
                    header = read_header(pages.headers)
                    try:
                        n, cutoff, native_width, native_precision, residual_rows = header
                        for value in (n, cutoff, native_width, residual_rows):
                            positive(value)
                        need(compare(cutoff, n) <= 0 and compare(native_precision, native_width) < 0
                             and compare(native_precision, precision) <= 0,
                             "funded native run header")
                        seen.add(n)
                        need(compare(seen, source_size) <= 0, "run partition stays within source")
                        for field, (bank, local) in enumerate(zip(pages.streams, local_pages)):
                            with owned(Count.product(n if field < 4 else residual_rows, native_width)) as (extent,):
                                copy_bits(bank, local, extent)
                            local.rewind()
                        with owned(subtract(precision, native_precision)) as (shift,):
                            for _ in indices(n):
                                with owned(read_signed(source, width)) as (rhs,):
                                    if correction is None:
                                        value = rhs.copy()
                                    else:
                                        selected = bit(pages.boundary_mask)
                                        if selected:
                                            with owned(read_signed(correction, width)) as (change,):
                                                value = difference(rhs, change)
                                            boundary_seen.increment()
                                        else:
                                            value = rhs.copy()
                                    with owned(value):
                                        with owned(truncate(value, shift)) as (native,):
                                            write_signed(native, local_source, native_width)
                                self.run_converted_rows += 1
                        local_source.rewind()
                        with self.scope.suspended():
                            returned = self.run_owner.run(local_source, *local_pages,
                                n, cutoff, native_width, native_precision)
                        try:
                            with owned(subtract(precision, native_precision)) as (shift,):
                                for _ in indices(n):
                                    selected = bool(bit(pages.boundary_mask)) if correction is None else True
                                    with owned(read_signed(returned, native_width)) as (native,):
                                        if selected:
                                            with owned(scaled(native, shift)) as (common,):
                                                write_signed(common, result, width)
                                    if correction is None and selected:
                                        boundary_seen.increment()
                                    self.run_converted_rows += 1
                            need(returned.read() == BLANK, "complete periodic run return")
                        finally:
                            returned.clear(); erase_marker(returned)
                        for tape in buffers:
                            borrowed_tape(tape).clear()
                    finally:
                        for value in header:
                            value.close()
                need(compare(seen, source_size) == 0 and compare(boundary_seen, boundary_size) == 0,
                     "complete run and boundary partitions")
                need(source.read() == pages.boundary_mask.read() == pages.headers.read() == BLANK,
                     "complete monotone source, mask and header ports")
                need(all(bank.read() == BLANK for bank in pages.streams), "complete six run banks")
                need(correction is None or correction.read() == BLANK, "complete boundary correction")
            self.block_passes += 1
        finally:
            for tape in buffers:
                if tape is not None:
                    tape.clear()
            for tape in (source, result, pages.boundary_mask, pages.headers, *pages.streams):
                tape.rewind()
            if correction is not None:
                correction.rewind()

    def band_apply(self, source, coefficients, result, length, band, width, precision):
        """Fold, exact completed dot products, unfold; each local window is O(b)."""
        leases = [None] * 8
        try:
            for field in range(8):
                leases[field] = self.pool.acquire()
            reverse, folded, window, work, products, front, back, back_reverse = leases
            fold(source, reverse, folded, length, width)
            coefficients.rewind(); folded.rewind()
            with owned(Count(band), Count.literal(0), Signed(Count.literal(0))) as (terms, consumed, zero):
                terms.multiply_small(2); terms.increment()
                for _ in indices(band):
                    write_signed(zero, window, width)
                with owned(Count(band)) as (initial,):
                    initial.increment()
                    for _ in indices(initial):
                        if compare(consumed, length) < 0:
                            copy_bits(folded, window, width); consumed.increment()
                        else:
                            write_signed(zero, window, width)
                window.rewind()
                for _ in indices(length):
                    with owned(subtract_row(self.arithmetic, zero, coefficients, window,
                                            terms, width, precision)) as (negative,):
                        with owned(negative.negated()) as (exact,):
                            with owned(truncate(exact, precision)) as (rounded,):
                                write_signed(rounded, products, width)
                    if compare(consumed, length) < 0:
                        following = read_signed(folded, width); consumed.increment()
                    else:
                        following = zero.copy()
                    with owned(following):
                        push_window(window, work, following, terms, width)
                    window, work = work, window
                    borrowed_tape(work).clear()
                    self.matrix_rows += 1
                need(coefficients.read() == folded.read() == BLANK,
                     "complete padded matrix and folded vector")
            products.rewind()
            unfold(products, front, back, back_reverse, result, length, width)
        finally:
            for tape in leases:
                if tape is not None:
                    tape.clear()
            source.rewind(); coefficients.rewind(); result.rewind()

    def schur(self, source, result, pages, length, band, width, precision,
              native_width, native_precision):
        rhs = self.pool.acquire()
        try:
            source.rewind()
            convert(source, rhs, length, width, native_width, precision, native_precision)
            need(source.read() == BLANK, "complete Schur conversion input")
            rhs.rewind()
            with owned(Count.literal(1)) as (one,):
                with self.scope.suspended():
                    returned = self.folded_owner.run(pages.lower, pages.upper, rhs,
                                length, one, band, native_width, native_precision)
            try:
                convert(returned, result, length, native_width, width, native_precision, precision)
                need(returned.read() == BLANK, "complete Schur conversion output")
            finally:
                self.folded_owner.consume()
        finally:
            rhs.clear(); source.rewind(); result.rewind()

    def run(self, rhs, pages):
        """Borrow fixed prepared tape ports; return one target-sized complex body."""
        rhs = borrowed_tape(rhs)
        meta = tuple(borrowed_count(v) for v in pages.counts)
        need(len(meta) == 9, "nine periodic descriptor roles")
        S, T, m, runs, band, width, precision, native_width, native_precision = meta
        ports = (rhs, pages.target_mask, pages.boundary_mask, pages.headers,
                 *pages.streams, pages.sb, pages.k, pages.lower, pages.upper)
        tapes = ports + tuple(v.tape for v in meta)
        need(len(ports) == 14 and len({id(v) for v in tapes}) == len(tapes)
             and all(v not in self.forbidden() for v in tapes), "distinct external periodic ports")
        for tape in tapes:
            origin(tape)
        for value in (S, T, m, runs, band, width, native_width):
            positive(value)
        need(compare(S, T) <= 0 and compare(m, S) <= 0 and compare(runs, S) <= 0
             and compare(band, m) < 0 and compare(precision, width) < 0
             and compare(native_precision, native_width) < 0
             and compare(native_precision, precision) <= 0,
             "periodic dimensions and funded common grid")
        need(self.closed and not self.pending and not self.pool.live and self.output.read() == BLANK,
             "consume prior periodic output")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        leases = [None] * 8
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    for field in range(8):
                        leases[field] = self.pool.acquire()
                    real, imaginary, real_result, imaginary_result, vy, t, z, correction = leases
                    self.extract(rhs, pages.target_mask, real, imaginary, S, T, width)
                    for source, destination in ((real, real_result), (imaginary, imaginary_result)):
                        self.block_inverse(source, None, vy, pages, S, m, runs, width, precision)
                        self.band_apply(vy, pages.sb, t, m, band, width, precision)
                        self.schur(t, z, pages, m, band, width, precision, native_width, native_precision)
                        self.band_apply(z, pages.k, correction, m, band, width, precision)
                        self.block_inverse(source, correction, destination, pages, S, m, runs, width, precision)
                        for tape in (vy, t, z, correction):
                            borrowed_tape(tape).clear()
                    self.merge(rhs, pages.target_mask, real_result, imaginary_result, T, width)
                    self.idle(); self.calls += 1
                    succeeded = self.pending = True
                finally:
                    for tape in leases:
                        if tape is not None:
                            tape.clear()
                    for tape in tapes:
                        tape.rewind()
                    self.pool.empty()
        finally:
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear(); erase_marker(self.output)
                self.pending = False
            self.closed = True
        return self.output
