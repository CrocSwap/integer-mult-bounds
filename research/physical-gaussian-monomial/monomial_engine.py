"""Physical Gaussian phases joined to one reusable Compact inventory."""
import phase_sources
phase_sources.activate()
from cardinal_counts import Count,positive
from compact_counts import append_bits,copy_bits
from compact_layout import Layout
from compact_streams import digit_permutation,flip_digit
from encoded import compare,subtract
from pair_dispatch import PairDispatch
from phase_recipe import Recipe
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope,borrowed_count,borrowed_tape,erase_marker,
                     initialize_marker,sealed_constructors)
from signed_phase import SignedHeadroomError,scan
from words import BLANK,LEFT,need


class MonomialEngine:
    def __init__(self,names,vectors,literal,native):
        need(type(names) is tuple and len(names) == len(set(names)), "fixed monomial field schema")
        self.names = names
        self.recipe = Recipe(literal,vectors)
        positions = tuple(names.index(name) for name in self.recipe.vectors)
        need(not set(self.recipe.vectors)&{"u","t","b"} and
             names.index("u") < min(positions) and names.index("t") < min(positions) and
             names.index("b") > max(positions), "complete front/back compact placement")
        actions = tuple(self.action(gate) for gate in self.recipe.word)
        self.compact = PairDispatch(names,actions,self.recipe.vectors[0],native)
        self.pool = ScratchPool(8*len(names)+256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes,self.output):
            erase_marker(tape)
        self.closed = True

    def action(self,gate):
        kind,target,source = gate
        target_name = self.recipe.vectors[target]
        source_name = None if kind == "flip" else self.recipe.vectors[source]
        late = False if source_name is None else self.names.index(source_name) > self.names.index(target_name)
        return source_name,target_name,late

    def rearm(self):
        need(self.closed and self.output.read() == BLANK, "consume previous monomial output")
        self.output.step(-1)
        marker = self.output.read()
        need(marker in (LEFT,BLANK), "monomial output origin")
        if marker == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def compact_gate(self,current,gate,widths,n,K,G,rho,record_bits,rows):
        self.compact.select(self.action(gate))
        with self.scope.suspended():
            returned = self.compact.run(borrowed_tape(current),tuple(borrowed_count(value) for value in widths),
                                        *(borrowed_count(value) for value in (n,K,G,rho,record_bits,rows)))
        following = None
        try:
            following = self.pool.acquire()
            append_bits(returned,following)
            following.rewind()
            current.clear()
            result,following = following,None
            return result
        finally:
            returned.clear()
            erase_marker(returned)
            if following is not None:
                following.clear()

    def single_column_gate(self,current,gate,plan,rho):
        source,target,_late = self.action(gate)
        target_bit = plan.bit_position(target,rho)
        source_bit = None
        try:
            if source is None:
                return flip_digit(current,plan,target_bit,self.pool.acquire)
            source_bit = plan.bit_position(source,rho)
            early = compare(source_bit,target_bit) < 0
            first,second = (source_bit,target_bit) if early else (target_bit,source_bit)
            return digit_permutation(current,plan,first,second,
                                     (0,1,3,2) if early else (0,3,2,1),self.pool.acquire)
        finally:
            target_bit.close()
            if source_bit is not None:
                source_bit.close()

    def run(self,payload,widths,f,K,G,rho,component_bits,coefficients,outer_rows,inverse=False):
        need(type(inverse) is bool and len(widths) == len(self.names) and
             all(isinstance(value,Count) for value in widths), "compiled mode and encoded field inventory")
        for value in (f,K,G,component_bits,coefficients,outer_rows):
            positive(value)
        source = borrowed_tape(payload)
        need(source is not self.output, "distinct borrowed monomial input")
        self.rearm()
        plan = current = n = record_bits = wide = compact_width = total = one = two = None
        guard_error = None
        with sealed_constructors(),self.scope.installed():
            try:
                one,two = Count.literal(1),Count.literal(2)
                need(compare(component_bits,two) >= 0 and compare(rho,K) < 0, "signed width and selected residue")
                n = subtract(f,one)
                wide = Count.product(f,K)
                # G is unused at f=1 and need not fit the address extent.
                compact_width = Count.literal(0) if n.zero() else Count.product(n,G)
                need(all(compare(widths[self.names.index(name)],wide) == 0 for name in self.recipe.vectors),
                     "complete wide monomial slots")
                need(all(compare(widths[self.names.index(name)],compact_width) == 0 for name in ("u","t","b")),
                     "complete used compact slots")
                record_bits = Count.product(component_bits,coefficients)
                record_bits.multiply_small(2)
                plan = Layout(self.names,widths,record_bits)
                total = Count.product(plan.row_bits,outer_rows)
                current = self.pool.acquire()
                source.rewind()
                copy_bits(source,current,total)
                need(source.read() == BLANK, "complete Gaussian monomial packet")
                source.rewind()
                current.rewind()
                if not inverse:
                    current = scan(current,plan,self.recipe,f,K,rho,component_bits,coefficients,outer_rows,self.pool.acquire)
                for gate in reversed(self.recipe.word) if inverse else self.recipe.word:
                    if n.zero():
                        # Finish each complete outer row before concatenation.
                        current = self.single_column_rows(current,gate,plan,rho,outer_rows)
                    else:
                        current = self.compact_gate(current,gate,widths,n,K,G,rho,record_bits,outer_rows)
                if inverse:
                    current = scan(current,plan,self.recipe,f,K,rho,component_bits,coefficients,outer_rows,self.pool.acquire,True)
                append_bits(current,self.output)
                current.clear()
                current = None
            except SignedHeadroomError as error:
                guard_error = error
            finally:
                source.rewind()
                if current is not None:
                    current.clear()
                if plan is not None:
                    plan.close()
                for value in (n,record_bits,wide,compact_width,total,one,two):
                    if value is not None:
                        value.close()
                self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        if guard_error is not None:
            erase_marker(self.output)
            raise guard_error
        return self.output

    def single_column_rows(self,current,gate,plan,rho,outer_rows):
        """Reuse complete-row gates without folding the row label into a key."""
        from stream import Counter
        remaining = Counter(outer_rows)
        output,row = self.pool.acquire(),None
        current.rewind()
        try:
            while not remaining.finished:
                row = self.pool.acquire()
                copy_bits(current,row,plan.row_bits)
                row.rewind()
                row = self.single_column_gate(row,gate,plan,rho)
                append_bits(row,output)
                row.clear()
                row = None
                remaining.decrement()
            need(current.read() == BLANK, "complete one-column row packet")
            current.clear()
            output.rewind()
            result,output = output,None
            return result
        finally:
            remaining.close()
            if row is not None:
                row.clear()
            if output is not None:
                output.clear()
