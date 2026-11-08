"""Exact seven-product matrix multiplication on a fixed physical tape inventory.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The Strassen identity is inherited. This file supplies its encoded, flat
seven-stage depth-first execution, tip-only frame parking and exact ABI.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count,positive
from compact_counts import copy_bits
from encoded import compare,divide
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from records import Tape
from ring_words import Signed,add,difference,read_signed,write_signed
from router_metadata import indices,owned
from scratch_pool import ScratchPool
from session import (OuterScope,borrowed_count,borrowed_tape,erase_marker,
                     initialize_marker,sealed_constructors)
from words import BLANK,LEFT,need

FRAME_BASE=5
LEFT_TERMS=((0,3,1),(2,3,1),(0,0,0),(3,3,0),(0,1,1),(2,0,-1),(1,3,-1))
RIGHT_TERMS=((0,3,1),(0,0,0),(1,3,-1),(2,0,-1),(3,3,0),(0,1,1),(2,3,1))
UPDATES=(((0,False),(3,False)),((2,False),(3,True)),
         ((1,False),(3,False)),((0,False),(2,False)),
         ((0,True),(1,False)),((3,False),),((0,False),))


def origin(tape):
    need(tape.read()!=LEFT,'canonical seven-product borrowed origin')
    tape.step(-1);correct=tape.read()==LEFT;tape.step(1)
    need(correct,'canonical seven-product borrowed origin')


def dyadic_log(value,one,two):
    positive(value);current=Count(value);logarithm=Count.literal(0)
    try:
        while compare(current,one)>0:
            quotient,remainder=divide(current,two)
            try:need(remainder.zero(),'seven-product block is a power of two')
            except BaseException:quotient.close();raise
            finally:remainder.close()
            current.close();current=quotient;logarithm.increment()
        need(compare(current,one)==0,'seven-product terminal dimension one')
        result,logarithm=logarithm,None;return result
    finally:
        current.close()
        if logarithm is not None:logarithm.close()


class SevenProduct:
    def __init__(self):
        self.word=FftWord(base_bits=4096)
        self.pool=ScratchPool(256);self.scope=OuterScope(self.pool)
        self.arithmetic=Arithmetic(self.word,self.scope)
        self.left,self.right=Tape(),Tape()
        self.qa=tuple(Tape() for _ in range(4));self.qb=tuple(Tape() for _ in range(4))
        self.acc=tuple(Tape() for _ in range(4))
        self.result,self.combine,self.parked,self.reverse,self.output=(Tape() for _ in range(5))
        self.closed=True;self.pending=False
        self.calls=self.nodes=self.leaves=self.pushes=self.pops=0
        for tape in (*self.pool.tapes,*self.buffers()):erase_marker(tape)

    def buffers(self):
        return (self.left,self.right,*self.qa,*self.qb,*self.acc,self.result,
                self.combine,self.parked,self.reverse,self.output)

    def forbidden(self):
        word=self.word
        return (*self.pool.tapes,*self.buffers(),*word.pool.tapes,word.output,
                *word.canonical,*word.base.pool.tapes,*word.product.pool.tapes,
                *word.product.word.pool.tapes,*word.product.twiddles.pool.tapes)

    def word_idle(self):
        self.word.idle()
        need(self.word.closed and not self.word.pool.live and self.word.output.read()==BLANK,
             'consumed seven-product scalar owner')

    def idle(self):
        need(self.closed and not self.pending and not self.pool.live and self.output.read()==BLANK,
             'consumed seven-product owner')
        self.word_idle()

    def consume(self):
        need(self.closed and self.pending,'one pending seven-product return')
        self.output.clear();erase_marker(self.output);self.pending=False
        self.idle()

    def promote(self,source,destination,entries,width,widened):
        source.rewind()
        try:
            for _ in indices(entries):
                with owned(read_signed(source,width)) as (value,):
                    write_signed(value,destination,widened)
            need(source.read()==BLANK,'complete seven-product input matrix')
        finally:source.rewind();destination.rewind()

    def split(self,source,quadrants,half,width):
        source.rewind()
        with owned(Count.product(half,width)) as (row_bits,):
            for left,right in ((quadrants[0],quadrants[1]),(quadrants[2],quadrants[3])):
                for _ in indices(half):
                    copy_bits(source,left,row_bits);copy_bits(source,right,row_bits)
        need(source.read()==BLANK,'complete streamed matrix quadrant split')
        for tape in quadrants:tape.rewind()
        source.clear()

    def zero_accumulators(self,entries,width):
        with owned(Count.product(entries,width)) as (bits,):
            for tape in self.acc:
                for _ in indices(bits):tape.append(0)
                tape.rewind()

    def operand(self,quadrants,term,destination,entries,width):
        first,second,sign=term;a=quadrants[first];b=quadrants[second]
        a.rewind();b.rewind()
        try:
            if sign==0:
                with owned(Count.product(entries,width)) as (bits,):copy_bits(a,destination,bits)
            else:
                for _ in indices(entries):
                    with owned(read_signed(a,width),read_signed(b,width)) as (x,y):
                        with owned(add(x,y) if sign==1 else difference(x,y)) as (value,):
                            write_signed(value,destination,width)
                need(b.read()==BLANK,'complete second quadrant operand')
            need(a.read()==BLANK,'complete first quadrant operand')
        finally:a.rewind();b.rewind();destination.rewind()

    def push(self,stage,entries,u,v):
        """Append one parent to the current parked tip; no ancestor rewind."""
        need(self.parked.read()==BLANK,'parked frame tip')
        for tapes,width in ((self.qa+self.qb,u),(self.acc,v)):
            with owned(Count.product(entries,width)) as (bits,):
                for tape in tapes:
                    tape.rewind();copy_bits(tape,self.parked,bits)
                    need(tape.read()==BLANK,'complete parked matrix')
                    tape.clear()
        self.parked.append(FRAME_BASE+stage);self.pushes+=1

    def pop(self,entries,u,v):
        """Read the finite continuation, then delete only the final frame."""
        need(self.parked.read()==BLANK,'parked return tip')
        self.parked.step(-1);symbol=self.parked.read()
        if symbol==LEFT:
            self.parked.step(1);return None
        need(FRAME_BASE<=symbol<FRAME_BASE+7,'seven-product finite continuation')
        stage=symbol-FRAME_BASE;self.parked.write(BLANK);self.parked.step(-1)
        with owned(Count(u),Count(v)) as (extent,part):
            extent.multiply_small(8);part.multiply_small(4);extent.add(part)
            with owned(Count.product(entries,extent)) as (bits,):
                for _ in indices(bits):
                    bit=self.parked.read();need(bit in(0,1),'complete parked frame body')
                    self.reverse.append(bit);self.parked.write(BLANK);self.parked.step(-1)
        self.parked.step(1);self.reverse.step(-1)
        for tapes,width in ((self.qa+self.qb,u),(self.acc,v)):
            with owned(Count.product(entries,width)) as (bits,):
                for tape in tapes:
                    for _ in indices(bits):
                        bit=self.reverse.read();need(bit in(0,1),'complete reversed frame body')
                        tape.append(bit);self.reverse.write(BLANK);self.reverse.step(-1)
                    tape.rewind()
        need(self.reverse.read()==LEFT,'exact reversed frame extent');self.reverse.step(1)
        self.pops+=1;return stage

    def dispatch(self,stage,n,two,u,v):
        half,remainder=divide(n,two)
        try:
            need(remainder.zero() and not half.zero(),'exact nonleaf dyadic split')
            with owned(Count.product(half,half)) as (entries,):
                self.operand(self.qa,LEFT_TERMS[stage],self.left,entries,u)
                self.operand(self.qb,RIGHT_TERMS[stage],self.right,entries,u)
                self.push(stage,entries,u,v)
            result,half=half,None;return result
        finally:
            remainder.close()
            if half is not None:half.close()

    def add_return(self,slot,negative,entries,v):
        accumulator=self.acc[slot];accumulator.rewind();self.result.rewind()
        try:
            for _ in indices(entries):
                with owned(read_signed(accumulator,v),read_signed(self.result,v)) as (old,value):
                    with owned(difference(old,value) if negative else add(old,value)) as (updated,):
                        write_signed(updated,self.combine,v)
            need(accumulator.read()==self.result.read()==BLANK,'complete returned product update')
            accumulator.clear();self.combine.rewind()
            with owned(Count.product(entries,v)) as (bits,):copy_bits(self.combine,accumulator,bits)
            need(self.combine.read()==BLANK,'complete accumulator replacement')
        finally:
            self.combine.clear();accumulator.rewind();self.result.rewind()

    def join(self,half,v):
        with owned(Count.product(half,v)) as (row_bits,):
            for left,right in ((self.acc[0],self.acc[1]),(self.acc[2],self.acc[3])):
                for _ in indices(half):
                    copy_bits(left,self.result,row_bits);copy_bits(right,self.result,row_bits)
                need(left.read()==right.read()==BLANK,'complete returned quadrant join')
        for tape in (*self.qa,*self.qb,*self.acc):tape.clear()
        self.result.rewind()

    def compute(self,block,one,two,u,v):
        """Flat finite-state DFS; only the current dimension remains live."""
        n=Count(block);returning=False
        try:
            while True:
                if not returning:
                    self.nodes+=1
                    if compare(n,one)==0:
                        with owned(read_signed(self.left,u),read_signed(self.right,u)) as (a,b):
                            with owned(self.arithmetic.multiply(a,b,u)) as (value,):
                                write_signed(value,self.result,v)
                        need(self.left.read()==self.right.read()==BLANK,'complete scalar leaf matrices')
                        self.left.clear();self.right.clear();self.result.rewind()
                        self.leaves+=1;returning=True
                    else:
                        half,remainder=divide(n,two)
                        try:
                            need(remainder.zero(),'internal dyadic quadrant split')
                            self.split(self.left,self.qa,half,u)
                            self.split(self.right,self.qb,half,u)
                            with owned(Count.product(half,half)) as (entries,):
                                self.zero_accumulators(entries,v)
                        finally:half.close();remainder.close()
                        child=self.dispatch(0,n,two,u,v);n.close();n=child
                        continue
                with owned(Count.product(n,n)) as (entries,):
                    stage=self.pop(entries,u,v)
                    if stage is None:break
                    for slot,negative in UPDATES[stage]:self.add_return(slot,negative,entries,v)
                self.result.clear()
                if stage==6:
                    self.join(n,v);n.multiply_small(2)
                    returning=True
                else:
                    n.multiply_small(2)
                    child=self.dispatch(stage+1,n,two,u,v);n.close();n=child
                    returning=False
            need(compare(n,block)==0,'root returned dimension')
        finally:n.close()

    def run(self,first,second,block,width,wide):
        first,second=borrowed_tape(first),borrowed_tape(second)
        block,width,wide=(borrowed_count(c) for c in (block,width,wide))
        sources=(first,second);metadata=(block,width,wide)
        forbidden=self.forbidden()
        need(first is not second and all(t not in forbidden for t in sources)
             and all(c.tape not in forbidden and c.tape not in sources for c in metadata),
             'external seven-product operands and metadata')
        ports=(*sources,*(c.tape for c in metadata))
        for tape in ports:origin(tape)
        self.idle();positive(width)
        for tape in (*self.pool.tapes,*self.buffers()):initialize_marker(tape)
        self.closed=False;succeeded=False
        try:
            with sealed_constructors(),self.scope.installed():
                with owned(Count.literal(1),Count.literal(2)) as (one,two):
                    with owned(dyadic_log(block,one,two),Count(width),Count(width),Count(width)) as (ell,u,v,expected):
                        u.add(ell);u.add(two)
                        v.multiply_small(2)
                        with owned(Count(ell)) as (four_ell,):
                            four_ell.multiply_small(4);v.add(four_ell)
                        v.add(two);v.add(two)
                        expected.multiply_small(2);expected.add(ell);expected.add(two)
                        need(compare(wide,expected)==0,'exact inherited matrix return width')
                        with owned(Count.product(block,block)) as (entries,):
                            self.promote(first,self.left,entries,width,u)
                            self.promote(second,self.right,entries,width,u)
                            self.compute(block,one,two,u,v)
                            for _ in indices(entries):
                                with owned(read_signed(self.result,v)) as (value,):
                                    write_signed(value,self.output,wide)
                            need(self.result.read()==BLANK,'complete exact root matrix')
                        self.result.clear();self.word_idle();self.calls+=1
                        succeeded=self.pending=True
        finally:
            for tape in ports:tape.rewind()
            for tape in self.buffers():
                if tape is not self.output:tape.clear()
            self.pool.empty()
            for tape in (*self.pool.tapes,*(t for t in self.buffers() if t is not self.output)):
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:self.output.clear();erase_marker(self.output);self.pending=False
            self.closed=True
        return self.output
