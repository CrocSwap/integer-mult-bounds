"""Paid native pointwise/recovery endpoints for three normalized transforms.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count,positive
from encoded import compare
from fft_arithmetic import Arithmetic
from records import Tape
from ring_words import Signed,nearest,power_two,read_signed,scaled,truncate,write_signed
from router_metadata import indices,owned
from scratch_pool import ScratchPool
from session import OuterScope,borrowed_count,borrowed_tape,erase_marker,initialize_marker,sealed_constructors
from words import BLANK,need

def inventory(value):
    """Construction-only fixed owner inventory; never scans payload cells."""
    seen=set();result=[]
    def visit(obj):
        if id(obj) in seen:return
        seen.add(id(obj))
        if isinstance(obj,Tape):result.append(obj);return
        if isinstance(obj,dict):
            for child in obj.values():visit(child)
        elif isinstance(obj,(tuple,list)):
            for child in obj:visit(child)
        elif hasattr(obj,'__dict__') and not callable(obj):
            for child in vars(obj).values():visit(child)
    visit(value);return tuple(result)

class DeferredTail:
    """Native endpoints only; T-to-S extraction and three transforms are external.

    S,b,q,Gamma are borrowed encoded counts, prepared and source-bound before
    construction. The exact source guard S<2^b is enforced, not inferred from
    an asymptotic label. Inputs are original-order compact S fields, each two
    signed q+2-bit components with denominator 2^q. Integer recovery returns
    one signed W-bit real record per source coordinate; W is an encoded Count.
    """
    def __init__(self,state,S,b,q,Gamma):
        borrowed=tuple(borrowed_count(x) for x in (S,b,q,Gamma))
        need(len({id(x.tape) for x in borrowed})==4,'distinct borrowed endpoint descriptors')
        positive(S);positive(b);positive(q)
        with owned(power_two(b),Count(b)) as (radix,minimum):
            minimum.increment();minimum.increment()
            need(compare(S,radix)<0,'source product fits radix')
            need(compare(q,minimum)>=0,'exact ingress grid')
        self.borrowed=tuple(x.tape for x in borrowed)
        self.S,self.b,self.q,self.Gamma=(Count(x) for x in borrowed)
        self.component_bits=Count(q);self.component_bits.increment();self.component_bits.increment()
        self.wide_bits=Count(self.component_bits);self.wide_bits.increment()
        self.shift=Count(b);self.shift.multiply_small(2)
        for _ in range(4):self.shift.increment()
        self.W=Count(q)
        with owned(Count(Gamma),Count(b)) as (triple,four_b):
            triple.multiply_small(3);self.shift.add(triple);self.W.add(triple)
            four_b.multiply_small(4);self.W.add(four_b)
        for _ in range(6):self.W.increment()
        with owned(Count(q),Count.literal(2)) as (exponent,two):
            exponent.multiply_small(2)
            from encoded import subtract
            with owned(subtract(exponent,two)) as (half,):self.half_bound=power_two(half)
        with owned(Count(q),Count.literal(4)) as (exponent,four):
            exponent.multiply_small(2)
            from encoded import subtract
            with owned(subtract(exponent,four)) as (quarter,):self.quarter_bound=power_two(quarter)
        self.word=state.word.FftWord(base_bits=4096)
        self.pool=ScratchPool(128);self.scope=OuterScope(self.pool)
        self.arithmetic=Arithmetic(self.word,self.scope)
        self.output=Tape();self.closed=True;self.pending=False;self.finished=False
        self.calls=dict(pointwise=0,recovery=0)
        for tape in (*self.pool.tapes,self.output):erase_marker(tape)
        self.private=inventory(self)

    def norm(self,real,imag,bound):
        with owned(self.arithmetic.multiply(real,real,self.component_bits)) as (a,):
            with owned(self.arithmetic.multiply(imag,imag,self.component_bits)) as (b,):
                a.magnitude.add(b.magnitude)
                need(compare(a.magnitude,bound)<=0,'actual endpoint disk radius')

    def run(self,first,second=None):
        first=borrowed_tape(first)
        if second is not None:second=borrowed_tape(second)
        ports=(first,) if second is None else (first,second)
        need(len({id(t) for t in ports})==len(ports),'distinct borrowed scalar fields')
        need(all(t not in self.private for t in ports),'external scalar endpoint ports')
        need(self.closed and not self.pending and not self.finished,'consume protected scalar endpoint return')
        self.word.idle()
        for tape in (*self.pool.tapes,self.output):initialize_marker(tape)
        self.closed=False;succeeded=False
        try:
            with sealed_constructors(),self.scope.installed():
                try:
                    for tape in ports:tape.rewind()
                    for _ in indices(self.S):
                        with owned(read_signed(first,self.component_bits),read_signed(first,self.component_bits)) as (a,b):
                            self.norm(a,b,self.half_bound)
                            if second is not None:
                                with owned(read_signed(second,self.component_bits),read_signed(second,self.component_bits)) as (c,d):
                                    self.norm(c,d,self.half_bound)
                                    with owned(*self.arithmetic.complex_product(a,b,c,d,self.component_bits)) as (real,imag):
                                        with owned(truncate(real,self.q),truncate(imag,self.q)) as (r,i):
                                            self.norm(r,i,self.quarter_bound)
                                            write_signed(r,self.output,self.component_bits);write_signed(i,self.output,self.component_bits)
                            else:
                                with owned(Signed(Count(self.S))) as (S,):
                                    with owned(self.arithmetic.multiply(a,S,self.W)) as (once,):
                                        with owned(self.arithmetic.multiply(once,S,self.W)) as (twice,):
                                            with owned(scaled(twice,self.shift)) as (numerator,):
                                                with owned(nearest(numerator,self.q)) as (integer,):
                                                    write_signed(integer,self.output,self.W)
                    need(all(t.read()==BLANK for t in ports),'complete compact source-field extent')
                    self.word.idle();self.pending=succeeded=True
                    self.calls['recovery' if second is None else 'pointwise']+=1
                finally:
                    for tape in ports:tape.rewind()
                    self.pool.empty()
        finally:
            for tape in self.pool.tapes:erase_marker(tape)
            self.output.rewind()
            if not succeeded:self.output.clear();erase_marker(self.output)
            self.closed=True
        return self.output

    def carrier(self,source,narrow=True,conjugate=False):
        """Exact q+3 <-> q+2 native carrier change and optional conjugation.

        The public radius-2/3 external return uses q+3 sign-magnitude bits.
        Its zero-drop codec first returns native q+3 words. Reached half-disk
        values fit q+2 without losing fractional bits or normalization.
        """
        need(type(narrow) is bool and type(conjugate) is bool,'literal carrier flags')
        source=borrowed_tape(source)
        need(source not in self.private,'external carrier field')
        need(self.closed and not self.pending and not self.finished,'consume protected scalar endpoint return')
        incoming,outgoing=(self.wide_bits,self.component_bits) if narrow else (self.component_bits,self.wide_bits)
        self.word.idle()
        for tape in (*self.pool.tapes,self.output):initialize_marker(tape)
        self.closed=False;succeeded=False
        try:
            with sealed_constructors(),self.scope.installed():
                try:
                    source.rewind()
                    for _ in indices(self.S):
                        with owned(read_signed(source,incoming),read_signed(source,incoming)) as (r,i):
                            self.norm(r,i,self.half_bound)
                            if conjugate and not i.magnitude.zero():i.negative=not i.negative
                            write_signed(r,self.output,outgoing);write_signed(i,self.output,outgoing)
                    need(source.read()==BLANK,'complete carrier field extent')
                    self.word.idle();self.pending=succeeded=True
                finally:source.rewind();self.pool.empty()
        finally:
            for tape in self.pool.tapes:erase_marker(tape)
            self.output.rewind()
            if not succeeded:self.output.clear();erase_marker(self.output)
            self.closed=True
        return self.output

    def consume(self):
        need(self.closed and self.pending,'one protected scalar endpoint output')
        self.output.clear();erase_marker(self.output);self.pending=False

    def close(self):
        need(self.closed and not self.pending and not self.finished,'quiescent scalar endpoint')
        self.finished=True;self.word.idle()
        for x in (self.S,self.b,self.q,self.Gamma,self.component_bits,self.wide_bits,self.shift,self.W,self.half_bound,self.quarter_bound):x.close()
