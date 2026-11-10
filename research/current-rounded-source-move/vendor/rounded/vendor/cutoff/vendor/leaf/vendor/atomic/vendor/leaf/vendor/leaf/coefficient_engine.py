"""Fixed physical inventory for exact Gaussian leaves and aligned additions."""
import leaf_sources
leaf_sources.activate()
from axis_stream import c_axis
from cardinal_counts import Count,positive
from compact_counts import append_bits,copy_bits
from compact_layout import Layout
from encoded import compare,subtract
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope,borrowed_tape,erase_marker,initialize_marker,
                     sealed_constructors)
from signed_linear import CoefficientDomainError,add_component
from stream import Counter
from words import BLANK,LEFT,need


class CoefficientEngine:
    def __init__(self,names,field):
        need(type(names) is tuple and len(names) == len(set(names)) and field in names,
             "fixed coefficient field schema")
        self.names,self.field = names,field
        self.pool = ScratchPool(8*len(names)+192)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes,self.output):
            erase_marker(tape)
        self.closed = True

    def rearm(self):
        need(self.closed and self.output.read() == BLANK, "consume previous coefficient output")
        self.output.step(-1)
        marker = self.output.read()
        need(marker in (LEFT,BLANK), "coefficient output origin")
        if marker == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def finish(self,error):
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        if error is not None:
            self.output.clear()
            erase_marker(self.output)
            raise error
        return self.output

    def run_leaf(self,payload,widths,f,K,rho,component_bits,coefficients,outer_rows,inverse=False):
        need(type(inverse) is bool and len(widths) == len(self.names) and
             all(isinstance(value,Count) for value in widths), "encoded leaf schema and direction")
        for value in (f,K,component_bits,coefficients,outer_rows):
            positive(value)
        source = borrowed_tape(payload)
        need(source is not self.output, "distinct borrowed coefficient payload")
        self.rearm()
        plan = current = one = two = wide = record_bits = total = remaining = low = position = None
        error = None
        with sealed_constructors(),self.scope.installed():
            try:
                one,two = Count.literal(1),Count.literal(2)
                need(compare(component_bits,two) >= 0 and compare(rho,K) < 0, "leaf signed width and residue")
                wide = Count.product(f,K)
                need(compare(widths[self.names.index(self.field)],wide) == 0, "complete selected leaf field")
                record_bits = Count.product(component_bits,coefficients)
                record_bits.multiply_small(2)
                plan = Layout(self.names,widths,record_bits)
                total = Count.product(plan.row_bits,outer_rows)
                current = self.pool.acquire()
                source.rewind()
                copy_bits(source,current,total)
                need(source.read() == BLANK, "complete borrowed leaf packet")
                source.rewind()
                current.rewind()
                remaining = Counter(f)
                if inverse:
                    count = subtract(f,one)
                    try:
                        low = Count.product(count,K)
                    finally:
                        count.close()
                    low.add(rho)
                else:
                    low = Count(rho)
                while not remaining.finished:
                    position = plan.bit_position(self.field,low)
                    current = c_axis(current,plan,position,component_bits,coefficients,outer_rows,
                                     self.pool.acquire,inverse)
                    position.close()
                    position = None
                    remaining.decrement()
                    if not remaining.finished:
                        if inverse:
                            following = subtract(low,K)
                            low.close()
                            low = following
                        else:
                            low.add(K)
                append_bits(current,self.output)
                current.clear()
                current = None
            except CoefficientDomainError as failure:
                error = failure
            finally:
                source.rewind()
                if current is not None:
                    current.clear()
                if plan is not None:
                    plan.close()
                for value in (one,two,wide,record_bits,total,remaining,low,position):
                    if value is not None:
                        value.close()
                self.pool.empty()
        return self.finish(error)

    def run_add(self,target,source,component_bits,gaussians,subtract_source=False):
        need(type(subtract_source) is bool, "compiled aligned-add direction")
        positive(component_bits)
        positive(gaussians)
        left,right = borrowed_tape(target),borrowed_tape(source)
        need(left is not right and left is not self.output and right is not self.output,
             "distinct aligned Gaussian operands and return")
        self.rearm()
        two = count = remaining = None
        buffers = ()
        error = None
        with sealed_constructors(),self.scope.installed():
            try:
                two = Count.literal(2)
                need(compare(component_bits,two) >= 0, "aligned-add signed width")
                count = Count(gaussians)
                count.multiply_small(2)
                remaining = Counter(count)
                buffers = tuple(self.pool.acquire() for _ in range(2))
                left.rewind()
                right.rewind()
                while not remaining.finished:
                    add_component(left,right,self.output,component_bits,buffers,subtract_source)
                    remaining.decrement()
                need(left.read() == right.read() == BLANK, "complete aligned Gaussian operands")
            except CoefficientDomainError as failure:
                error = failure
            finally:
                left.rewind()
                right.rewind()
                for buffer in buffers:
                    buffer.clear()
                for value in (two,count,remaining):
                    if value is not None:
                        value.close()
                self.pool.empty()
        return self.finish(error)
