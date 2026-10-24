"""Apply original-axis Gaussian pages to complete short tensor lines."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from expansion_records import Fields, read_integer, same_integer
from expansion_tile import Tile
from expansion_tile_geometry import TileHeader, advance, source_index, stencil_bounds
from gaussian_core import Core
from gaussian_page import Header as CoreHeader
from gaussian_prepare import endpoint
from gaussian_rationals import read_count
from records import Tape
from ring_words import Signed, difference
from router_metadata import ceiling_log, indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from tensor_catalogue import Catalogue, STREAMS, read_frame, skip_frame
from tensor_windows import zeros
from tensor_word import adapt_fft_word
from tensor_arithmetic import adapt_arithmetic
from words import BLANK, need


def check_descriptor(stream, origin, length):
    with owned(read_integer(stream), read_count(stream)) as (actual_origin, actual_length):
        need(same_integer(origin, actual_origin) and compare(length, actual_length) == 0,
             "tensor descriptor matches its original global coordinates")


class Binding(Fields):
    def __init__(self, plan, profile, k):
        super().__init__()
        try:
            row = profile.axis
            self.keep("target", Signed(Count.product(k, plan.L)))
            self.keep("core", source_index(row.s, row.t, self.target))
            with owned(advance(self.target, plan.L)) as (end,):
                with owned(source_index(row.s, row.t, end)) as (last,):
                    with owned(difference(last, self.core)) as (length,):
                        need(not length.negative and not length.magnitude.zero()
                             and compare(length.magnitude, plan.L) <= 0, "complete source core fits its output slot")
                        self.keep("core_length", Count(length.magnitude))
            with owned(Signed(Count(plan.halo))) as (halo,):
                self.keep("halo", difference(self.target, halo))
            self.keep("source", endpoint(row.s, row.t, self.halo))
            with owned(advance(self.halo, plan.target_halo)) as (end,):
                with owned(endpoint(row.s, row.t, end)) as (last,):
                    with owned(difference(last, self.source)) as (length,):
                        need(not length.negative and not length.magnitude.zero(), "positive original compression window")
                        self.keep("source_length", Count(length.magnitude))
            with owned(difference(self.core, self.source)) as (offset,):
                need(not offset.negative, "source core starts inside its principal window")
                self.keep("offset", Count(offset.magnitude))
            with owned(Count(self.source_length), Count(self.offset)) as (gap, end):
                gap.add(plan.w)
                end.add(self.core_length)
                need(compare(gap, row.s) < 0 and compare(end, self.source_length) <= 0,
                     "principal complement and core containment")
            if plan.mode.zero():
                first, last = stencil_bounds(row.s, row.t, plan.radius, self.target, plan.L)
                self.keep("expansion", first)
                with owned(last):
                    with owned(difference(last, first)) as (length,):
                        need(not length.negative, "positive explicit expansion source span")
                        self.keep("expansion_length", Count(length.magnitude))
            else:
                self.keep("expansion", self.source.copy())
                self.keep("expansion_length", Count(self.source_length))
            need(compare(self.expansion_length, plan.expansion_capacity) <= 0,
                 "original expansion span fits its capacity")
            check_descriptor(profile.expansion_windows, self.expansion, self.expansion_length)
            check_descriptor(profile.compression_windows, self.halo, plan.target_halo)
            check_descriptor(profile.cores, self.core, self.core_length)
            check_descriptor(profile.compression_sources, self.source, self.source_length)
        except BaseException:
            self.close()
            raise

    def expansion_header(self, header, plan, row):
        for name in ("p", "P", "alpha", "radius", "sigma"):
            need(compare(getattr(header, name), getattr(plan, name)) == 0, "common tensor expansion policy")
        for name in ("s", "t"):
            need(compare(getattr(header, name), getattr(row, name)) == 0, "original tensor expansion axis")
        need(same_integer(header.source_start, self.expansion)
             and same_integer(header.target_start, self.target)
             and compare(header.source_count, self.expansion_length) == 0
             and compare(header.input_capacity, plan.expansion_capacity) == 0
             and compare(header.target_length, plan.L) == 0, "complete original expansion tile binding")

    def compression_header(self, header, plan):
        for name in ("p", "P"):
            need(compare(getattr(header, name), getattr(plan, name)) == 0, "common tensor compression precision")
        need(compare(header.target_length, plan.target_halo) == 0
             and compare(header.m, self.source_length) == 0
             and compare(header.core_offset, self.offset) == 0
             and compare(header.core_length, self.core_length) == 0
             and compare(header.w, plan.w) == 0, "complete original compression core binding")
        with owned(Count(plan.P), Count(plan.p), Count.literal(34)) as (width, guard, constant):
            guard.multiply_small(8)
            width.add(guard)
            with owned(ceiling_log(plan.component_bits)) as (logarithm,):
                logarithm.multiply_small(8)
                width.add(logarithm)
            width.add(constant)
            need(compare(header.width, width) == 0, "exact global producer work width")


class LineApply:
    """[outer][axis tile][lines][input slot] to equal L-record output slots."""
    def __init__(self):
        self.expansion, self.compression = Tile(), Core()
        adapt_fft_word(self.expansion.word)
        adapt_fft_word(self.compression.word)
        for owner in (self.expansion, self.expansion.block, self.compression,
                      self.compression.interior, self.compression.boundary):
            adapt_arithmetic(owner)
        self.pool = ScratchPool(512)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.calls = dict(expansion=0, compression=0)
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        for owner in (self.expansion, self.compression):
            owner.idle()
            need(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                 "consumed original Gaussian line child")

    def run(self, payload, catalogue, index, outer, lines, compression=False):
        need(type(compression) is bool, "compiled tensor line direction")
        source, catalogue = borrowed_tape(payload), borrowed_tape(catalogue)
        index, outer, lines = (borrowed_count(value) for value in (index, outer, lines))
        positive(outer)
        positive(lines)
        forbidden = (*self.pool.tapes, self.output)
        need(source is not catalogue and source not in forbidden and catalogue not in forbidden
             and all(value.tape not in forbidden for value in (index, outer, lines)), "external tensor line ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume previous tensor line return")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(pages=0, lines=0)
        book = profile = line = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    book = Catalogue(catalogue, self.pool.acquire)
                    plan = book.plan
                    profile = book.profile(index)
                    line = self.pool.acquire()
                    source.rewind()
                    owner = self.compression if compression else self.expansion
                    for _ in indices(outer):
                        for name in STREAMS:
                            getattr(profile, name).rewind()
                        for k in indices(profile.axis.tiles):
                            with owned(Binding(plan, profile, k)) as (binding,):
                                pages = profile.compression_pages if compression else profile.expansion_pages
                                unused = profile.expansion_pages if compression else profile.compression_pages
                                skip_frame(unused)
                                page = read_frame(pages, self.pool.acquire)
                                try:
                                    with owned(CoreHeader(page) if compression else TileHeader(page)) as (header,):
                                        if compression:
                                            binding.compression_header(header, plan)
                                        else:
                                            binding.expansion_header(header, plan, profile.axis)
                                    page.rewind()
                                    input_length = plan.target_halo if compression else plan.expansion_capacity
                                    output_length = binding.core_length if compression else plan.L
                                    with owned(Count.product(input_length, plan.record_bits),
                                               Count.product(output_length, plan.record_bits),
                                               subtract(plan.L, output_length)) as (input_bits, output_bits, padding):
                                        for _ in indices(lines):
                                            borrowed_tape(line).clear()
                                            copy_bits(source, line, input_bits)
                                            line.rewind()
                                            with self.scope.suspended():
                                                returned = owner.run(page, line)
                                            try:
                                                copy_bits(returned, self.output, output_bits)
                                                need(returned.read() == BLANK, "complete Gaussian child line return")
                                                zeros(None, self.output, padding, plan.record_bits)
                                            finally:
                                                returned.clear()
                                                erase_marker(returned)
                                            self.last_counts["lines"] += 1
                                finally:
                                    page.clear()
                            self.last_counts["pages"] += 1
                        need(all(getattr(profile, name).read() == BLANK for name in STREAMS),
                             "complete tensor line profile streams")
                    need(source.read() == BLANK, "complete tensor line input rectangle")
                    self.idle()
                    self.calls["compression" if compression else "expansion"] += 1
                    succeeded = True
                finally:
                    if line is not None:
                        line.clear()
                    for value in (profile, book):
                        if value is not None:
                            value.close()
                    source.rewind()
                    catalogue.rewind()
                    for value in (index, outer, lines):
                        value.rewind()
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
