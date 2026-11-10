"""Whole #4327 union rounds with literal #4583 headers and #6908 payloads.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from records import Tape
from router_metadata import indices, owned, ceiling_log
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need
from fast_boundary import origin
from window_consumer import UnionInverseWindow
from union_bits import (BLOCK_START, BLOCK_END, bit, skip_bits, copy_until,
                            copy_record, top_block, rewind_block, pop_block,
                            stack_empty, same_context, skip_context)
from union_fields import Geometry, unit
from union_catalogue import (axis_metadata, axis_body, build_membership, state_init,
                       advance, header)


class UnionRouter:
    def __init__(self, child=None):
        self.child = UnionInverseWindow() if child is None else child
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        (self.main0, self.main1, self.zero, self.one, self.radix_log,
         self.segment0, self.segment1, self.left, self.right, self.prefix,
         self.membership, self.state, self.header_buffer, self.e_table,
         self.mask, self.keep_stack, self.rest_stack, self.indicator,
         self.output) = (Tape() for _ in range(19))
        self.pages = tuple(Tape() for _ in range(8))
        self.closed, self.pending = True, False
        self.rounds = self.visits = self.substreams = self.dense_records = 0
        for tape in (*self.pool.tapes, *self.buffers()):
            erase_marker(tape)

    def buffers(self):
        return (self.main0, self.main1, self.zero, self.one, self.radix_log,
                self.segment0, self.segment1, self.left, self.right, self.prefix,
                self.membership, self.state, self.header_buffer, self.e_table,
                self.mask, self.keep_stack, self.rest_stack, self.indicator,
                *self.pages, self.output)

    def forbidden(self):
        return (*self.pool.tapes, *self.buffers(), *self.child.forbidden())

    def idle(self):
        need(self.closed and not self.pending and not self.pool.live
             and self.output.read() == BLANK, 'consume protected whole-union return')
        self.child.idle()

    def consume(self):
        need(self.closed and self.pending, 'one pending whole-union return')
        self.output.clear(); erase_marker(self.output)
        self.pending = False
        self.idle()

    def form(self, source, shape, side):
        state_init(self.membership, self.state, shape.axes, shape.h)
        while True:
            member = header(self.state, self.header_buffer, shape.axes, shape.h, shape.tag_bits)
            self.indicator.append(int(member))
            if member:
                copy_until(self.header_buffer, self.main0)
                copy_bits(source, self.main0, shape.payload)
            else:
                skip_bits(source, shape.payload)
            self.header_buffer.clear()
            self.dense_records += 1
            if advance(self.membership, self.state, side, shape.h):
                break
        need(source.read() == BLANK, 'exact dense L^g input payload extent')
        self.main0.rewind(); self.indicator.rewind()

    def tag(self, current, other, shape, round_index):
        while current.read() != BLANK:
            shape.retag(current, other, round_index)
            self.visits += 1
        current.clear(); other.rewind()
        return other, current

    def radix_forward(self, current, other, shape):
        need(stack_empty(self.radix_log), 'empty per-round radix ledger')
        for position in indices(shape.tag_bits):
            self.radix_log.append(BLOCK_START)
            while current.read() != BLANK:
                digit = shape.radix_bit(current, position)
                self.radix_log.append(digit)
                copy_record(current, self.one if digit else self.zero, shape.record)
            self.radix_log.append(BLOCK_END)
            current.clear()
            self.zero.rewind(); self.one.rewind()
            copy_until(self.zero, other); copy_until(self.one, other)
            self.zero.clear(); self.one.clear()
            other.rewind(); current, other = other, current
        return current, other

    def radix_inverse(self, current, other, shape):
        while not stack_empty(self.radix_log):
            top_block(self.radix_log)
            while self.radix_log.read() != BLOCK_END:
                if bit(self.radix_log) == 0:
                    copy_record(current, self.zero, shape.record)
            rewind_block(self.radix_log)
            while self.radix_log.read() != BLOCK_END:
                if bit(self.radix_log) == 1:
                    copy_record(current, self.one, shape.record)
            need(current.read() == BLANK, 'radix split consumes every current record')
            rewind_block(self.radix_log)
            self.zero.rewind(); self.one.rewind()
            while self.radix_log.read() != BLOCK_END:
                selected = self.one if bit(self.radix_log) else self.zero
                copy_record(selected, other, shape.record)
            need(self.zero.read() == self.one.read() == BLANK, 'complete inverse radix replay')
            pop_block(self.radix_log)
            self.zero.clear(); self.one.clear(); current.clear()
            other.rewind(); current, other = other, current
        return current, other

    def inside(self, tape, shape, prefix_bits, lo, upper):
        if tape.read() == BLANK:
            return False
        ordinal, equal = shape.key(tape, prefix_bits, equal=self.prefix)
        try:
            return equal and compare(lo, ordinal) <= 0 and compare(ordinal, upper) < 0
        finally:
            ordinal.close()

    def zip_level(self, source, target, shape, axis, length, level, inverse):
        with owned(Count.product(axis, shape.h)) as (prefix_bits,):
            while source.read() != BLANK:
                ordinal, _ = shape.key(source, prefix_bits)
                try:
                    lo, size, half, role = unit(ordinal, length, level)
                    with owned(lo, size, half):
                        copy_record(source, self.right if role == 2 else self.left, shape.record)
                finally:
                    ordinal.close()
            source.clear(); self.left.rewind(); self.right.rewind()
            while self.left.read() != BLANK:
                ordinal, _ = shape.key(self.left, prefix_bits, saved=self.prefix)
                self.prefix.rewind()
                lo = size = half = None
                try:
                    lo, size, half, role = unit(ordinal, length, level)
                    need(role != 2, 'left zip stream starts at A or a pass unit')
                    with owned(Count(lo)) as (upper,):
                        upper.add(size)
                        if role == 0:
                            while self.inside(self.left, shape, prefix_bits, lo, upper):
                                copy_record(self.left, target, shape.record)
                        elif inverse:
                            while self.inside(self.left, shape, prefix_bits, lo, upper):
                                copy_record(self.left, target, shape.record)
                            while self.inside(self.right, shape, prefix_bits, lo, upper):
                                copy_record(self.right, target, shape.record)
                        else:
                            with owned(subtract(size, half)) as (remainder,):
                                while self.inside(self.left, shape, prefix_bits, lo, upper):
                                    for tape, count in ((self.left, half), (self.right, remainder)):
                                        for _ in indices(count):
                                            need(self.inside(tape, shape, prefix_bits, lo, upper),
                                                 'matching complete non-dyadic zip chunk')
                                            copy_record(tape, target, shape.record)
                                need(not self.inside(self.right, shape, prefix_bits, lo, upper),
                                     'zip child runs end together')
                finally:
                    for value in (ordinal, lo, size, half):
                        if value is not None:
                            value.close()
                    self.prefix.clear()
            need(self.right.read() == BLANK, 'complete right zip stream')
            self.left.clear(); self.right.clear(); target.rewind()
            return target, source

    def apply_segment(self, shape, axis, round_index, length, selected, block):
        current, other = self.segment0, self.segment1
        with owned(ceiling_log(length)) as (top,):
            for index in indices(top):
                with owned(Count(index)) as (level,):
                    level.increment()
                    current, other = self.zip_level(current, other, shape, axis, length, level, False)
            with self.scope.suspended():
                returned = self.child.run(current, self.e_table, self.mask,
                    self.pages[:4], self.pages[4:], shape.axes, shape.h, shape.tag_bits,
                    axis, round_index, length, selected, block, shape.width, self.precision)
            try:
                copy_until(returned, other)
            finally:
                if self.child.pending:
                    self.child.consume()
            current.clear(); other.rewind(); current, other = other, current
            level = Count(top)
            try:
                with owned(Count.literal(1)) as (one,):
                    while not level.zero():
                        current, other = self.zip_level(current, other, shape, axis, length, level, True)
                        after = subtract(level, one)
                        level.close(); level = after
            finally:
                level.close()
        self.substreams += 1
        return current

    def axes(self, current, other, bank, shape, side, round_index):
        bank.rewind(); skip_context(bank)
        for axis in indices(shape.axes):
            with owned(*axis_metadata(bank, side)) as (length, selected, block):
                axis_body(bank, length, selected, block, shape.h, shape.width,
                          self.e_table, self.mask, self.pages)
                active_axis = False
                if current.read() != BLANK:
                    with owned(shape.tag(current)) as (tag,):
                        need(compare(tag, axis) >= 0, 'stable ascending axis substreams')
                        active_axis = compare(tag, axis) == 0
                if active_axis:
                    need(not length.zero(), 'nonempty source exposed axis for active tag')
                    while current.read() != BLANK:
                        with owned(shape.tag(current)) as (tag,):
                            if compare(tag, axis) != 0:
                                break
                        copy_record(current, self.segment0, shape.record)
                    self.segment0.rewind()
                    returned = self.apply_segment(shape, axis, round_index, length, selected, block)
                    copy_until(returned, other)
                    self.segment0.clear(); self.segment1.clear()
                for tape in (self.e_table, self.mask, *self.pages):
                    tape.clear()
        need(current.read() == bank.read() == BLANK, 'complete current axis pass and bank')
        current.clear(); other.rewind()
        return other, current

    def split(self, current, other, shape, round_index):
        self.keep_stack.append(BLOCK_START); self.rest_stack.append(BLOCK_START)
        with owned(Count(round_index)) as (after,):
            after.increment()
            while current.read() != BLANK:
                with owned(shape.count(current)) as (count,):
                    need(compare(count, after) >= 0, 'live record count at split')
                    keep = compare(count, after) > 0
                self.keep_stack.append(int(keep))
                copy_record(current, other if keep else self.rest_stack, shape.record)
        self.keep_stack.append(BLOCK_END); self.rest_stack.append(BLOCK_END)
        current.clear(); other.rewind()
        return other, current

    def restore(self, current, other, shape):
        while not stack_empty(self.keep_stack):
            top_block(self.keep_stack); top_block(self.rest_stack)
            while self.keep_stack.read() != BLOCK_END:
                source = current if bit(self.keep_stack) else self.rest_stack
                copy_record(source, other, shape.record)
            need(current.read() == BLANK and self.rest_stack.read() == BLOCK_END,
                 'exact keep/rest reconstruction')
            pop_block(self.keep_stack); pop_block(self.rest_stack)
            current.clear(); other.rewind(); current, other = other, current
        need(stack_empty(self.rest_stack), 'matching finished/keep stack depths')
        return current, other

    def merge(self, source, current, shape, side):
        source.rewind(); skip_context(source)
        self.state.clear(); state_init(self.membership, self.state, shape.axes, shape.h)
        self.indicator.rewind()
        while True:
            member = header(self.state, self.header_buffer, shape.axes, shape.h, shape.tag_bits)
            need(bit(self.indicator) == int(member), 'forming indicator matches source-produced flags')
            if member:
                for _ in indices(shape.tag_at):
                    need(bit(self.header_buffer) == bit(current), 'protected union return address/header')
                skip_bits(current, shape.tag_bits)
                copy_bits(current, self.output, shape.payload)
                skip_bits(source, shape.payload)
            else:
                copy_bits(source, self.output, shape.payload)
            self.header_buffer.clear()
            if advance(self.membership, self.state, side, shape.h):
                break
        need(source.read() == current.read() == self.indicator.read() == BLANK,
             'complete dense scatter and source/union extents')

    def run(self, source, catalogue, axes, side, h, tag_bits, width, precision):
        source, catalogue = borrowed_tape(source), borrowed_tape(catalogue)
        metadata = tuple(borrowed_count(value) for value in
                         (axes, side, h, tag_bits, width, precision))
        axes, side, h, tag_bits, width, precision = metadata
        ports = (source, catalogue, *(value.tape for value in metadata))
        forbidden = self.forbidden()
        need(source is not catalogue and all(tape not in forbidden for tape in ports)
             and all(value.tape not in (source, catalogue) for value in metadata),
             'external whole-union sources and descriptors')
        self.idle()
        for tape in ports:
            origin(tape)
        for value in (axes, side, h, tag_bits, width):
            positive(value)
        need(compare(precision, width) < 0, 'common union precision/carrier')
        for tape in (*self.pool.tapes, *self.buffers()):
            initialize_marker(tape)
        self.closed = False
        self.precision = precision
        succeeded = False
        shape = None
        try:
            with sealed_constructors(), self.scope.installed():
                with owned(Count.literal(2), ceiling_log(side), Count(axes)) as (two, expected_h, successor):
                    successor.increment()
                    with owned(ceiling_log(successor)) as (expected_t,):
                        need(compare(side, two) >= 0 and compare(h, expected_h) == 0
                             and compare(tag_bits, expected_t) == 0, 'exact #4583 dimensions')
                shape = Geometry(axes, h, tag_bits, width)
                try:
                    same_context(source, catalogue, self.output)
                    build_membership(catalogue, self.membership, self.e_table,
                                     axes, side, h, width)
                    self.form(source, shape, side)
                    current, other = self.main0, self.main1
                    with owned(Count.literal(0)) as (round_index,):
                        while current.read() != BLANK:
                            need(compare(round_index, axes) < 0, 'at most g union rounds')
                            current, other = self.tag(current, other, shape, round_index)
                            current, other = self.radix_forward(current, other, shape)
                            current, other = self.axes(current, other, catalogue, shape, side, round_index)
                            current, other = self.radix_inverse(current, other, shape)
                            current, other = self.split(current, other, shape, round_index)
                            round_index.increment(); self.rounds += 1
                    current, other = self.restore(current, other, shape)
                    self.merge(source, current, shape, side)
                    self.child.idle()
                    succeeded = self.pending = True
                finally:
                    shape.close(); shape = None
        finally:
            if self.child.pending:
                self.child.consume()
            for tape in ports:
                tape.rewind()
            for tape in self.buffers():
                if tape is not self.output:
                    tape.clear()
            self.pool.empty()
            for tape in (*self.pool.tapes, *(t for t in self.buffers() if t is not self.output)):
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear(); erase_marker(self.output); self.pending = False
            self.closed = True
        return self.output
