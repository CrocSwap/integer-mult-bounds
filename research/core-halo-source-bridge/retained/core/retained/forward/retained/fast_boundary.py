"""Seven-product replacement for the unchanged #5059 completed-product ABI.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from boundary_pages import BoundaryPages
from cardinal_counts import Count
from compact_counts import copy_bits
from router_metadata import owned
from session import borrowed_count, borrowed_tape, erase_marker
from words import BLANK, LEFT, RIGHT, need
from seven_product import SevenProduct


def origin(tape):
    need(tape.read()!=LEFT,'canonical fast-boundary borrowed origin')
    tape.step(-1);correct=tape.read()==LEFT;tape.step(1)
    need(correct,'canonical fast-boundary borrowed origin')


def dyadic(count):
    """One literal count scan; no decoded logarithm or host dimension."""
    source=count.tape;seen=False
    try:
        while source.read() in (0,1):
            if source.read()==1:
                need(not seen,'dyadic fast-boundary block size');seen=True
            source.step(1)
        need(source.read()==RIGHT and seen,'dyadic fast-boundary block size')
    finally:source.rewind()


class FastBoundaryPages(BoundaryPages):
    def __init__(self):
        super().__init__();self.kernel=SevenProduct();self.pending=False

    def forbidden(self):
        w=self.word
        return (*self.pool.tapes,self.output,*w.pool.tapes,w.output,*w.canonical,
                *w.base.pool.tapes,*w.product.pool.tapes,
                *w.product.word.pool.tapes,*w.product.twiddles.pool.tapes,
                *self.kernel.forbidden())

    def idle(self):
        super().idle();self.kernel.idle()
        need(self.kernel.closed and not self.kernel.pending,
             'consumed fast-boundary matrix child')

    def consume(self):
        need(self.closed and self.pending,'one pending fast-boundary return')
        self.output.clear();erase_marker(self.output);self.pending=False
        self.idle()

    def product(self,first,second,destination,block,width,wide):
        """Copy the complete exact wide product; no P-grid rounding here."""
        try:
            with self.scope.suspended():
                returned=self.kernel.run(first,second,block,width,wide)
            with owned(Count.product(block,block)) as (entries,):
                with owned(Count.product(entries,wide)) as (bits,):
                    copy_bits(returned,destination,bits)
            need(returned.read()==BLANK,'complete fast-boundary matrix result')
            self.products+=1
        finally:
            if self.kernel.pending:self.kernel.consume()
            first.rewind();second.rewind();destination.rewind()

    def run(self,lower_d,lower_b,upper_d,upper_b,rhs,length,columns,block,width,precision):
        sources=tuple(borrowed_tape(t) for t in (lower_d,lower_b,upper_d,upper_b,rhs))
        metadata=tuple(borrowed_count(c) for c in (length,columns,block,width,precision))
        forbidden=self.forbidden()
        need(len(set(sources))==5 and all(t not in forbidden for t in sources)
             and all(c.tape not in forbidden and c.tape not in sources for c in metadata),
             'external distinct fast-boundary ports')
        need(self.closed and not self.pending and not self.pool.live
             and self.output.read()==BLANK,'consume prior fast-boundary output')
        for tape in (*sources,*(c.tape for c in metadata)):origin(tape)
        self.idle();dyadic(metadata[2])
        result=super().run(*sources,*metadata)
        self.pending=True
        return result
