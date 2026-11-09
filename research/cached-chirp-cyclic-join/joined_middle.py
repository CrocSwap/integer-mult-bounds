"""Actual cached phase / cyclic-convolution / common-grid composition.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Online values and counts remain on the inherited fixed tapes.
"""
from cardinal_counts import Count
from chirp_consumer import CachedChirp
from compact_counts import append_bits
from cyclic_engine import Cyclic
from encoded import compare,subtract
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from records import Tape
from ring_words import Signed,power_two,read_signed,write_signed
from router_metadata import indices,owned
from scratch_pool import ScratchPool
from session import OuterScope,borrowed_count,borrowed_tape,erase_marker,initialize_marker,sealed_constructors
from words import BLANK,need

class Middle:
    def __init__(self,state,prepared,cyclic=None):
        self.source=prepared
        self.B=state.B
        p=prepared.plan
        self.codec=state.codec.Codec(state.B,Tape,BLANK,initialize_marker,erase_marker,
                                    state.codec.Format(p.q+2,p.q,p.W,p.f,0))
        self.cached=CachedChirp();self.cyclic=Cyclic() if cyclic is None else cyclic
        need(isinstance(self.cyclic,Cyclic),'actual complete cyclic child')
        self.word=FftWord(base_bits=4096);self.pool=ScratchPool(64)
        self.scope=OuterScope(self.pool);self.arithmetic=Arithmetic(self.word,self.scope)
        self.ones,self.kernel,self.first,self.current=(Tape() for _ in range(4))
        self.banks=(self.ones,self.kernel,self.first,self.current)
        for t in (*self.pool.tapes,*self.banks):erase_marker(t)
        self.output=self.B.Tape('cached middle protected q-grid return')
        self.closed=True;self.pending=False

    def copy_width(self,source,destination,old,new):
        source.rewind()
        for _ in indices(self.source.volume):
            for _ in (0,1):
                with owned(read_signed(source,old)) as (value,):write_signed(value,destination,new)
        need(source.read()==BLANK,'complete same-grid middle field')
        source.rewind();destination.rewind()

    def check_radius(self,payload):
        p=self.source.tables
        with owned(Count(p.precision),Count.literal(2)) as (bits,two):
            bits.multiply_small(2)
            with owned(subtract(bits,two)) as (exponent,):
                with owned(power_two(exponent)) as (bound,):
                    for _ in indices(self.source.volume):
                        with owned(read_signed(payload,p.width),read_signed(payload,p.width)) as (real,imag):
                            with owned(self.arithmetic.multiply(real,real,p.width),
                                       self.arithmetic.multiply(imag,imag,p.width)) as (a,b):
                                a.magnitude.add(b.magnitude)
                                need(compare(a.magnitude,bound)<=0,'actual middle input disk radius at most one half')
        need(payload.read()==BLANK,'complete middle input field');payload.rewind()

    def cached_call(self,payload,conjugate):
        p=self.source.tables
        with self.scope.suspended():
            return self.cached.run(borrowed_tape(payload),borrowed_tape(p.shape),borrowed_tape(p.tables),
                                   borrowed_count(p.width),borrowed_count(p.precision),conjugate=conjugate)

    def consume(self):
        need(self.closed and self.pending,'one pending common-grid middle return')
        self.B.clear(self.output);self.B.home(self.output);self.pending=False

    def run(self,source):
        need(self.closed and not self.pending and not self.source.closed,'quiescent source-bound middle')
        need(source is not self.output,'external middle payload')
        p=self.source.tables;self.closed=False
        for t in (*self.pool.tapes,*self.banks):initialize_marker(t)
        returned=None;succeeded=False
        try:
            with sealed_constructors(),self.scope.installed():
                try:
                    payload=self.codec.prepare_input(source)
                    self.check_radius(payload)
                    with owned(Signed(power_two(p.precision)),Signed(Count.literal(0))) as (one,zero):
                        for _ in indices(self.source.volume):
                            write_signed(one,self.ones,p.width);write_signed(zero,self.ones,p.width)
                    self.ones.rewind()
                    returned=self.cached_call(self.ones,False)
                    self.copy_width(returned,self.kernel,p.width,self.source.cyclic_width)
                    self.cached.consume();returned=None;self.ones.clear()
                    returned=self.cached_call(payload,True)
                    self.copy_width(returned,self.first,p.width,self.source.cyclic_width)
                    self.cached.consume();returned=None
                    with self.scope.suspended():
                        returned=self.cyclic.run(borrowed_tape(self.kernel),borrowed_tape(self.first),
                            borrowed_tape(self.source.flags),*(borrowed_count(v) for v in
                            (self.source.axes,self.source.ell,p.precision,self.source.rows)))
                    self.copy_width(returned,self.current,self.source.cyclic_width,p.width)
                    returned.clear();erase_marker(returned);returned=None
                    self.kernel.clear();self.first.clear()
                    returned=self.cached_call(self.current,True)
                    normalized=self.codec.prepare_return(returned,source)
                    self.B.clone(normalized,self.output);self.B.home(self.output)
                    self.cached.consume();returned=None
                    self.word.idle();self.cyclic.idle();self.cached.idle()
                    succeeded=self.pending=True
                finally:
                    if self.cached.pending:self.cached.consume()
                    if returned is not None:
                        returned.clear();erase_marker(returned)
                    self.codec.abort()
                    for t in self.banks:t.clear()
                    self.pool.empty();self.B.home(source)
        finally:
            for t in (*self.pool.tapes,*self.banks):erase_marker(t)
            if not succeeded:self.B.clear(self.output);self.pending=False
            self.closed=True
        return self.output
