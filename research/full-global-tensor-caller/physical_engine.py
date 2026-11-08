"""Whole-field raw H and exact-word rounded complex diagonals on fixed tapes.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Retained #3627 H, #3709 exact Karatsuba/codec and B1 raw-H source are credited.
"""
from composed_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits, power_two
from encoded import compare, subtract
from fft_arithmetic import Arithmetic
from global_h_boundary import GlobalBoundary, digit
from physical_controls import END, H_EVENT, D_EVENT, NAMES
from ring_words import read_signed, write_signed, truncate, power_two as linear_power_two
from router_metadata import owned
from session import borrowed_count, borrowed_tape, erase_marker, sealed_constructors
from stream import Counter
from word_product import WordProduct
from words import BLANK, Word, need
from records import Tape
from types import ModuleType


class NullCounters(dict):
    """Finite compiled tags; a passive increment always reads zero."""
    def __init__(self,keys):
        super().__init__((key,0) for key in keys)

    def __getitem__(self,key):
        need(key in self,'fixed diagnostic counter tag')
        return 0

    def __setitem__(self,key,value):
        need(key in self,'fixed diagnostic counter tag')


class UnobservedArithmetic(Arithmetic):
    @property
    def products(self):
        return 0

    @products.setter
    def products(self,value):
        pass


def private_tapes(owner):
    """Compile the fixed owners' port inventory before sealed execution.

    This graph walk reads object references only, never numerical tape cells.
    Tape-bank cardinalities are fixed by the already constructed source owner.
    """
    pending,seen,result = [owner],set(),[]
    while pending:
        value = pending.pop()
        identity = id(value)
        if identity in seen:
            continue
        seen.add(identity)
        if isinstance(value,(Tape,Word)):
            result.append(value)
        elif isinstance(value,dict):
            pending.extend(value.values())
        elif isinstance(value,(tuple,list,set,frozenset)):
            pending.extend(value)
        elif not isinstance(value,(ModuleType,type)) and not callable(value):
            fields = getattr(value,'__dict__',None)
            if fields is not None:
                pending.extend(fields.values())
    return tuple(result)


def maximum(*values):
    result = Count(values[0])
    try:
        for value in values[1:]:
            if compare(value,result) > 0:
                result.close()
                result = Count(value)
        return result
    except BaseException:
        result.close()
        raise


def signed_fits(value,width):
    with owned(Count.literal(1)) as (one,):
        with owned(subtract(width,one)) as (sign_position,):
            with owned(linear_power_two(sign_position)) as (limit,):
                order = compare(value.magnitude,limit)
                need(order <= 0 if value.negative else order < 0,'complete complex product temporary width')


class FullPhysical(GlobalBoundary):
    """One protected return; no payload decoding or runtime Tape allocation."""
    def __init__(self,root,word=None,observe=None):
        super().__init__(root,observe)
        self.word = WordProduct() if word is None else word
        need(type(self.word) is WordProduct,'actual authenticated exact Karatsuba owner')
        self.arithmetic = (Arithmetic if observe is not None else UnobservedArithmetic)(self.word,self.scope)
        self.full_calls = dict(admissions=0,lifts=0,H=0,diagonals=0,shrinks=0)
        if observe is None:
            self.word.calls = NullCounters(self.word.calls)
            self.calls = NullCounters(self.calls)
            self.full_calls = NullCounters(self.full_calls)
        self.private = private_tapes(self)

    def idle(self):
        super().idle()
        need(self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK
             and all(tape.read() == BLANK for tape in self.word.canonical),
             'consumed complete exact word child')

    def note(self,event):
        if self.observe is not None:
            self.observe(event)

    def admit_radius(self,width,incoming,radius_bits,gaussians):
        """Compute incoming squared magnitudes using actual word products."""
        with owned(Count(incoming),Count.literal(0)) as (exponent,total):
            exponent.add(radius_bits)
            exponent.multiply_small(2)
            with owned(linear_power_two(exponent)) as (limit,):
                remaining = Counter(gaussians)
                self.current.rewind()
                try:
                    while not remaining.finished:
                        for _ in (0,1):
                            with owned(read_signed(self.current,width)) as (value,):
                                with owned(self.arithmetic.multiply(value,value,width)) as (square,):
                                    need(not square.negative,'nonnegative actual squared magnitude')
                                    total.add(square.magnitude)
                            self.note('input_squares')
                            need(compare(total,limit) <= 0,'physical complete input Euclidean radius')
                        remaining.decrement()
                    need(self.current.read() == BLANK,'complete radius admission field')
                finally:
                    self.current.rewind()
                    remaining.close()
        self.full_calls['admissions'] += 1

    def lift_input(self,input_width,incoming,fractional,data_width,gaussians):
        with owned(subtract(fractional,incoming)) as (low,):
            with owned(Count(input_width)) as (minimal,):
                minimal.add(low)
                with owned(subtract(data_width,minimal)) as (high,):
                    self.idle()
                    with self.scope.suspended():
                        returned = self.grid.expand(borrowed_tape(self.current),
                            *(borrowed_count(x) for x in (input_width,low,high,gaussians)))
                    self.accept(returned)
        self.full_calls['lifts'] += 1

    def h_event(self,code,n,axes,position_width,width,gaussians):
        positions = self.pool.acquire()
        try:
            with owned(Count.product(axes,position_width),Count.literal(1),Count.literal(0)) as (bits,one,zero):
                copy_bits(code,positions,bits)
                positions.rewind()
                with owned(self.raw_h(positions,n,axes,position_width,width,one,one,gaussians)) as (wide,):
                    self.idle()
                    with self.scope.suspended():
                        returned = self.grid.truncate(borrowed_tape(self.current),
                            *(borrowed_count(x) for x in (wide,zero,width,gaussians)))
                    self.accept(returned)
            self.full_calls['H'] += 1
            self.full_calls['shrinks'] += 1
        finally:
            positions.clear()

    def product(self,left,right,word_width,fractional,output_width,temporary_width,output,kind):
        with owned(*self.arithmetic.complex_product(*left,*right,word_width)) as exact:
            for value in exact:
                signed_fits(value,temporary_width)
            with owned(*(truncate(value,fractional) for value in exact)) as rounded:
                for value in rounded:
                    write_signed(value,output,output_width)
            self.note(kind)

    def coefficient_field(self,code,axes,side,fractional,factor_width,cache_width,
                          temporary_width,word_width):
        """Highest-axis-first fresh suffix expansion; zero factors are legal."""
        current = self.pool.acquire()
        following = page = None
        length = Count(side)
        remaining_axes = Counter(axes)
        try:
            # R_F(d*1)=d exactly, so copy the highest-axis F-grid page.
            entries = Counter(side)
            try:
                while not entries.finished:
                    for _ in (0,1):
                        with owned(read_signed(code,factor_width)) as (value,):
                            write_signed(value,current,cache_width)
                    self.note('initial_coefficients')
                    entries.decrement()
            finally:
                entries.close()
            current.rewind()
            remaining_axes.decrement()
            while not remaining_axes.finished:
                page,following = self.pool.acquire(),self.pool.acquire()
                with owned(Count.product(side,factor_width)) as (page_bits,):
                    page_bits.multiply_small(2)
                    copy_bits(code,page,page_bits)
                page.rewind()
                old_entries = Counter(length)
                try:
                    while not old_entries.finished:
                        with owned(read_signed(current,cache_width),read_signed(current,cache_width)) as suffix:
                            page.rewind()
                            entries = Counter(side)
                            try:
                                while not entries.finished:
                                    with owned(read_signed(page,factor_width),read_signed(page,factor_width)) as factor:
                                        self.product(factor,suffix,word_width,fractional,cache_width,
                                                     temporary_width,following,'coefficient_products')
                                    entries.decrement()
                                need(page.read() == BLANK,'complete reusable local factor page')
                            finally:
                                entries.close()
                        old_entries.decrement()
                    need(current.read() == BLANK,'complete old rounded suffix field')
                finally:
                    old_entries.close()
                current.clear()
                page.clear()
                page = None
                current,following = following,None
                current.rewind()
                updated = Count.product(length,side)
                length.close()
                length = updated
                remaining_axes.decrement()
            result,current = current,None
            return result
        finally:
            remaining_axes.close()
            length.close()
            for value in (current,following,page):
                if value is not None:
                    value.clear()

    def diagonal(self,code,labels,axes,side,local_records,fractional,data_width,
                 factor_width,cache_width,temporary_width,word_width):
        following = self.pool.acquire()
        coefficients = None
        remaining_labels = Counter(labels)
        self.current.rewind()
        try:
            while not remaining_labels.finished:
                coefficients = self.coefficient_field(code,axes,side,fractional,factor_width,
                                                       cache_width,temporary_width,word_width)
                remaining = Counter(local_records)
                try:
                    while not remaining.finished:
                        with owned(read_signed(self.current,data_width),read_signed(self.current,data_width)) as value:
                            with owned(read_signed(coefficients,cache_width),read_signed(coefficients,cache_width)) as coefficient:
                                self.product(value,coefficient,word_width,fractional,data_width,
                                             temporary_width,following,'data_products')
                        remaining.decrement()
                    need(coefficients.read() == BLANK,'complete actual coarse-label coefficient field')
                finally:
                    remaining.close()
                coefficients.clear()
                coefficients = None
                self.note('coarse_resets')
                remaining_labels.decrement()
            need(self.current.read() == BLANK,'complete physical diagonal payload')
            self.replace_owned(following)
            following = None
            self.full_calls['diagonals'] += 1
        finally:
            remaining_labels.close()
            for value in (following,coefficients):
                if value is not None:
                    value.clear()
            self.current.rewind()

    def run(self,payload,code,*parameters):
        need(len(parameters) == len(NAMES),'fixed complete Full metadata ports')
        source,program = borrowed_tape(payload),borrowed_tape(code)
        values = tuple(borrowed_count(x) for x in parameters)
        private = self.private
        need(source is not program and source not in private and program not in private
             and all(x.tape not in (*private,source,program) for x in values),
             'external distinct physical Full input and metadata ports')
        n,c,m,g,F,W,factor_width,cache_width,temporary_width,F0,W0,radius_bits,position_width,stages,h_count,d_count = values
        for value in (n,m,g,F,W,factor_width,cache_width,temporary_width,W0,position_width,stages):
            positive(value)
        need(compare(F,F0) >= 0,'nondecreasing incoming common grid')
        self.rearm()
        succeeded = False
        source.rewind()
        program.rewind()
        try:
            with sealed_constructors(),self.scope.installed():
                with owned(Count.product(g,m)) as (local_bits,):
                    with owned(Count(local_bits)) as (total_bits,):
                        total_bits.add(c)
                        need(compare(total_bits,n) == 0,'complete global tensor address geometry')
                    with owned(power_two(n),power_two(c),power_two(m),power_two(local_bits),
                               maximum(W,factor_width,cache_width)) as (gaussians,labels,side,local_records,word_width):
                        with owned(Count.product(gaussians,W0)) as (input_bits,):
                            input_bits.multiply_small(2)
                            self.current = self.pool.acquire()
                            copy_bits(source,self.current,input_bits)
                        need(source.read() == BLANK,'complete borrowed incoming Gaussian field')
                        source.rewind()
                        self.current.rewind()
                        self.admit_radius(W0,F0,radius_bits,gaussians)
                        self.lift_input(W0,F0,F,W,gaussians)
                        remaining,remaining_h,remaining_d = Counter(stages),Counter(h_count),Counter(d_count)
                        try:
                            while not remaining.finished:
                                opcode = digit(program) | (digit(program) << 1)
                                if opcode == H_EVENT:
                                    need(not remaining_h.finished,'remaining declared H event')
                                    remaining_h.decrement()
                                    self.h_event(program,n,g,position_width,W,gaussians)
                                else:
                                    need(opcode == D_EVENT,'complete chronological Full opcode')
                                    need(not remaining_d.finished,'remaining declared diagonal event')
                                    remaining_d.decrement()
                                    self.diagonal(program,labels,g,side,local_records,F,W,factor_width,
                                                  cache_width,temporary_width,word_width)
                                remaining.decrement()
                            need(remaining_h.finished and remaining_d.finished,'all declared Full H/D events executed')
                            need((digit(program) | (digit(program) << 1)) == END
                                 and program.read() == BLANK,'exact complete Full program ending')
                        finally:
                            remaining.close()
                            remaining_h.close()
                            remaining_d.close()
                        self.idle()
                        append_bits(self.current,self.output)
                self.current.clear()
                self.current = None
                self.pool.empty()
                succeeded = True
        finally:
            source.rewind()
            program.rewind()
            for value in values:
                value.rewind()
            if self.current is not None:
                self.current.clear()
                self.current = None
            if not self.pool.live:
                for tape in self.pool.tapes:
                    erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output


def production_owner():
    """Actual production H natives and exact Karatsuba at every word width."""
    from composed_engine import production_layer
    return FullPhysical(production_layer(),WordProduct())
