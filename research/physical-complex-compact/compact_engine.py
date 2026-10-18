"""A fixed physical inventory for complete Compact operations through B1."""
import native_sources
native_sources.activate()
from binary import Binary
from compact_control import Control
from compact_counts import append_bits, copy_bits
from compact_layout import Layout
from compact_streams import digit_permutation, flip_digit, repair, rotate
from cardinal_counts import Count, positive
from encoded import compare
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, need


class CompactEngine:
    """Compile names/order once; receive numerical widths only on Count tapes.

    run() preserves its borrowed payload/descriptors and returns a protected
    owned output. Consume that output before reuse. The successful-input
    contract does not include interrupted-macro rollback.
    """
    def __init__(self, names, source, target, late, native):
        need(type(names) is tuple and len(names) == len(set(names)), "fixed field schema")
        need(not native.closed, "fresh private ordinary engine at compilation")
        self.names, self.source, self.target, self.late = names,source,target,late
        self.pool = ScratchPool(8*len(names)+256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        native.finish(False)
        erase_marker(native.output)
        self.binary = Binary(native)
        # Establish one completely blank owned baseline before input loading.
        for tape in (*self.binary.pool.tapes,self.binary.output,*self.pool.tapes,self.output):
            erase_marker(tape)
        self.binary.closed = self.closed = True
        self.calls = dict(ordinary=0,rotations=0,rows=0)  # Checker observations only.

    def rearm(self):
        need(self.closed and self.output.read() == BLANK, "consume previous compact output")
        self.output.step(-1)
        marker = self.output.read()
        need(marker in (LEFT,BLANK), "compact output origin")
        if marker == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def swap(self, source, plan, first, second):
        width = plan.width(first)
        need(compare(width,plan.width(second)) == 0, "equal binary compact fields")
        before,middle,suffix = plan.paired_extents(first,second)
        output = None
        try:
            with self.scope.suspended():
                returned = self.binary.run(borrowed_tape(source),borrowed_count(width),
                                           borrowed_count(before),borrowed_count(middle),borrowed_count(suffix))
            try:
                output = self.pool.acquire()
                append_bits(returned,output)
                output.rewind()
            finally:
                returned.clear()
                erase_marker(returned)
            source.clear()
            self.calls["ordinary"] += 1
            result,output = output,None
            return result
        finally:
            for value in (before,middle,suffix):
                value.close()
            if output is not None:
                output.clear()

    def complete_row(self, source, plan, control):
        current = source
        try:
            for operation in control.operations:
                if operation[0] == "swap":
                    following = self.swap(current,plan,*operation[1:])
                else:
                    following = rotate(current,plan,control,operation,self.pool.acquire)
                    self.calls["rotations"] += 1
                current = following
            current = repair(current,plan,control,self.pool.acquire)
            last = Count.product(control.n,control.K)
            last.add(control.rho)
            target = plan.bit_position(control.target,last)
            source_bit = None
            try:
                if control.source is None:
                    following = flip_digit(current,plan,target,self.pool.acquire)
                else:
                    source_bit = plan.bit_position(control.source,last)
                    early = compare(source_bit,target) < 0
                    first,second = (source_bit,target) if early else (target,source_bit)
                    mapping = (0,1,3,2) if early else (0,3,2,1)
                    following = digit_permutation(current,plan,first,second,mapping,self.pool.acquire)
                current = following
            finally:
                last.close()
                target.close()
                if source_bit is not None:
                    source_bit.close()
            result,current = current,None
            return result
        finally:
            if current is not None:
                current.clear()

    def run(self, payload, widths, n, K, G, rho, record_bits, outer_rows):
        source = borrowed_tape(payload)
        need(source is not self.output, "distinct borrowed compact input")
        positive(outer_rows)
        self.rearm()
        plan = rows = current = None
        source.rewind()
        with sealed_constructors(),self.scope.installed():
            try:
                plan = Layout(self.names,widths,record_bits)
                control = Control(n,K,G,rho,self.source,self.target,self.late)
                control.validate(plan)
                rows = Counter(outer_rows)
                while not rows.finished:
                    current = self.pool.acquire()
                    copy_bits(source,current,plan.row_bits)
                    current.rewind()
                    current = self.complete_row(current,plan,control)
                    append_bits(current,self.output)
                    current.clear()
                    current = None
                    rows.decrement()
                    self.calls["rows"] += 1
                need(source.read() == BLANK, "complete outer-row packet")
            finally:
                source.rewind()
                if current is not None:
                    current.clear()
                if rows is not None:
                    rows.close()
                if plan is not None:
                    plan.close()
            self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        return self.output
