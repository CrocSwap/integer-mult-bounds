"""Explicit fast-scalar owner for unchanged source-emitted Full stages.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a new owner ABI. The original Karatsuba-only constructor is unchanged.
"""
from fft_word_sources import active
active()
from fft_word_engine import FftWord
from fft_arithmetic import Arithmetic
from global_h_boundary import GlobalBoundary
from physical_engine import (FullPhysical,NullCounters,UnobservedArithmetic,
                             private_tapes)
from ring_engine import RingProduct
from twiddle_setup import Twiddles
from word_product import WordProduct
from words import BLANK,need

PRODUCTION_CUTOFF=4096


class FastFullPhysical(FullPhysical):
    """Same stage methods; an explicitly declared exact FftWord child."""
    def __init__(self,root,*,base_bits=PRODUCTION_CUTOFF,observe=None):
        # This class declares its own constructor contract. It does not call,
        # patch or pass an inadmissible argument to FullPhysical.__init__.
        GlobalBoundary.__init__(self,root,observe)
        self.word=FftWord(base_bits=base_bits)
        need(type(self.word) is FftWord and type(self.word.base) is WordProduct
             and type(self.word.product) is RingProduct
             and type(self.word.product.word) is WordProduct
             and type(self.word.product.twiddles) is Twiddles
             and self.word.base is not self.word.product.word,
             'actual acyclic FFT-word owner graph')
        self.arithmetic=(Arithmetic if observe is not None else UnobservedArithmetic)(self.word,self.scope)
        self.full_calls=dict(admissions=0,lifts=0,H=0,diagonals=0,shrinks=0)
        if observe is None:
            for owner in (self,self.word,self.word.base,self.word.product,self.word.product.word):
                owner.calls=NullCounters(owner.calls)
            self.full_calls=NullCounters(self.full_calls)
            self.word.product.arithmetic=UnobservedArithmetic(self.word.product.word,
                                                            self.word.product.scope)
        self.private=private_tapes(self)

    def idle(self):
        GlobalBoundary.idle(self)
        self.word.idle()
        need(self.word.closed and self.word.a is self.word.b is None
             and not self.word.pool.live and self.word.output.read()==BLANK,
             'consumed complete exact FFT-word child')


def production_owner():
    """The unchanged native H owner and one fixed-cutoff exact FFT scalar."""
    from composed_engine import production_layer
    return FastFullPhysical(production_layer())
