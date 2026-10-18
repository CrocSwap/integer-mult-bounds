"""One fixed physical word inventory around compiled scalar recipes."""
import scalar_sources
scalar_sources.activate()
from cardinal_counts import Count,positive
from compact_counts import append_bits,copy_bits
from encoded import compare
from records import Tape
from scalar_recipe import Recipe
from scalar_words import instruction,require_zero,restored_source,zero_word
from scratch_pool import ScratchPool
from session import (OuterScope,borrowed_tape,erase_marker,initialize_marker,
                     sealed_constructors)
from signed_linear import CoefficientDomainError
from stream import Counter
from words import BLANK,LEFT,need


class ScalarEngine:
    def __init__(self,literals):
        need(type(literals) is tuple and 0 < len(literals) <= 96 and len(set(literals)) == len(literals),
             "fixed finite scalar recipe catalogue")
        self.recipes = {literal:Recipe(*literal) for literal in literals}
        self.recipe = self.recipes[literals[0]]
        self.pool = ScratchPool(128)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes,self.output):
            erase_marker(tape)
        self.closed = True

    def select(self,literal):
        need(literal in self.recipes, "scalar selection belongs to compiled catalogue")
        need(self.closed and self.output.read() == BLANK and not self.pool.live,
             "closed consumed scalar selection boundary")
        self.recipe = self.recipes[literal]

    def rearm(self):
        need(self.closed and self.output.read() == BLANK, "consume previous scalar output")
        self.output.step(-1)
        marker = self.output.read()
        need(marker in (LEFT,BLANK), "scalar output origin")
        if marker == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def run(self,target,source,width,gaussians):
        positive(width)
        positive(gaussians)
        left = borrowed_tape(target)
        right = None if source is None else borrowed_tape(source)
        need((self.recipe.kind == "scale") == (right is None), "compiled scalar operand arity")
        need(left is not self.output and right is not self.output and left is not right,
             "distinct borrowed scalar operands and return")
        self.rearm()
        two = components = remaining = None
        registers = ()
        work = zero = None
        error = None
        with sealed_constructors(),self.scope.installed():
            try:
                two = Count.literal(2)
                need(compare(width,two) >= 0, "signed scalar component width")
                components = Count(gaussians)
                components.multiply_small(2)
                remaining = Counter(components)
                registers = tuple(self.pool.acquire() for _ in range(3))
                work,zero = self.pool.acquire(),self.pool.acquire()
                left.rewind()
                if right is not None:
                    right.rewind()
                while not remaining.finished:
                    copy_bits(left,registers[0],width)
                    registers[0].rewind()
                    if right is None:
                        zero_word(registers[1],width)
                    else:
                        copy_bits(right,registers[1],width)
                        registers[1].rewind()
                    zero_word(registers[2],width)
                    zero_word(zero,width)
                    for operation in self.recipe.program:
                        instruction(registers,operation,width,work,zero)
                    if right is None:
                        require_zero(registers[1],width)
                    else:
                        restored_source(registers[1],right,width)
                    require_zero(registers[2],width)
                    append_bits(registers[0],self.output)
                    for tape in (*registers,work,zero):
                        borrowed_tape(tape).clear()
                    remaining.decrement()
                need(left.read() == BLANK and (right is None or right.read() == BLANK),
                     "complete scalar Gaussian operands")
            except CoefficientDomainError as failure:
                error = failure
            finally:
                left.rewind()
                if right is not None:
                    right.rewind()
                for tape in (*registers,work,zero):
                    if tape is not None:
                        tape.clear()
                for value in (two,components,remaining):
                    if value is not None:
                        value.close()
                self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        if error is not None:
            self.output.clear()
            erase_marker(self.output)
            raise error
        return self.output
