"""Literal cached tensor-chirp pass on axis0-packed polynomial coefficients.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
All variable coordinates/counts and numerical values stay on physical tapes.
The cached suffix schedule/travel proof is inherited from #4325/#5987.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from fft_arithmetic import Arithmetic
from fft_word_engine import FftWord
from records import Tape
from ring_words import Signed, power_two, read_signed, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, LEFT, RIGHT, need
AXIS_END, PAGE_BEGIN, PAGE_END = 5, 6, 7

def origin(tape):
    need(tape.read()!=LEFT,'canonical cached-chirp borrowed origin')
    tape.step(-1);correct=tape.read()==LEFT;tape.step(1)
    need(correct,'canonical cached-chirp borrowed origin')

def walk(tape,count,direction,binary=False):
    for _ in indices(count):
        if binary:need(tape.read() in (0,1),'complete chirp binary region')
        tape.step(direction)

def read_pair(tape,width):
    real=read_signed(tape,width)
    try:return real,read_signed(tape,width)
    except BaseException:real.close();raise

def write_pair(pair,tape,width):
    for value in pair:write_signed(value,tape,width)

def increment_field(counter):
    while counter.read()==1:
        counter.write(0);counter.step(1)
    if counter.read()==AXIS_END:
        counter.step(1);return True
    need(counter.read()==0,'complete cached-chirp counter field')
    counter.write(1);counter.step(-1)
    while counter.read() not in (LEFT,AXIS_END):
        need(counter.read() in (0,1),'binary local counter rewind');counter.step(-1)
    counter.step(1);return False

def read_field(counter):
    result=Count.literal(0);borrowed_tape(result.tape).clear()
    try:
        while counter.read()!=AXIS_END:
            need(counter.read() in (0,1),'complete cached-chirp digit')
            result.tape.append(counter.read());counter.step(1)
        result.tape.append(RIGHT);result.normalize();counter.step(-1)
        while counter.read() not in (LEFT,AXIS_END):counter.step(-1)
        counter.step(1);return result
    except BaseException:result.close();raise

def previous_field(counter):
    counter.step(-1)
    if counter.read()==LEFT:counter.step(1);return False
    need(counter.read()==AXIS_END,'previous cached-chirp field separator');counter.step(-1)
    while counter.read() not in (LEFT,AXIS_END):
        need(counter.read() in (0,1),'previous cached-chirp field bits');counter.step(-1)
    counter.step(1);return True

def next_page(tables):
    while tables.read()!=PAGE_END:
        need(tables.read() in (0,1),'complete forward chirp page');tables.step(1)
    tables.step(1)
    if tables.read()==BLANK:return False
    need(tables.read()==PAGE_BEGIN,'next chirp page separator');tables.step(1);return True

def previous_page(tables):
    tables.step(-1)
    while tables.read()!=PAGE_BEGIN:
        need(tables.read() in (0,1),'current backward chirp page');tables.step(-1)
    tables.step(-1);need(tables.read()==PAGE_END,'preceding chirp page end');tables.step(-1)
    while tables.read()!=PAGE_BEGIN:
        need(tables.read() in (0,1),'preceding backward chirp page');tables.step(-1)
    tables.step(1)

class CachedChirp:
    def __init__(self):
        self.word=FftWord(base_bits=4096)
        self.pool=ScratchPool(256);self.scope=OuterScope(self.pool)
        self.arithmetic=Arithmetic(self.word,self.scope)
        self.counter,self.cache,self.output=Tape(),Tape(),Tape()
        self.closed,self.pending=True,False
        self.calls=self.records=self.cache_updates=self.axes=0
        for tape in (*self.pool.tapes,self.counter,self.cache,self.output):erase_marker(tape)

    def forbidden(self):
        word=self.word
        return (*self.pool.tapes,self.counter,self.cache,self.output,
                *word.pool.tapes,word.output,*word.canonical,*word.base.pool.tapes,
                *word.product.pool.tapes,*word.product.word.pool.tapes,
                *word.product.twiddles.pool.tapes)

    def idle(self):
        self.word.idle()
        need(self.word.closed and not self.word.pool.live and self.word.output.read()==BLANK,
             'consumed cached-chirp scalar owner')

    def consume(self):
        need(self.closed and self.pending,'one pending cached-chirp return')
        self.output.clear();erase_marker(self.output);self.pending=False

    def rounded_product(self,left,right,width,precision):
        with owned(*self.arithmetic.complex_product(*left,*right,width)) as exact:
            real=truncate(exact[0],precision)
            try:return real,truncate(exact[1],precision)
            except BaseException:real.close();raise

    def initialize(self,shape,tables,width,precision,entry_bits):
        """One shape/table pass; every chirp zero entry is exactly one."""
        first_width=None
        try:
            with owned(power_two(precision),Count.literal(0)) as (unit,zero):
                one=Signed(Count(unit));imaginary=Signed(Count(zero))
                try:
                    need(shape.read()==0,'nonempty positive-axis chirp shape')
                    while shape.read()!=BLANK:
                        with owned(Count.literal(0)) as (length,):
                            while shape.read()==0:
                                self.counter.append(0);shape.step(1);length.increment()
                            positive(length)
                            need(shape.read()==AXIS_END,'chirp shape axis separator')
                            self.counter.append(AXIS_END);shape.step(1)
                            need(compare(length,width)<=0,'chirp coordinate fits scalar carrier')
                            if first_width is None:first_width=Count(length)
                            else:need(compare(length,first_width)<=0,'axis0 is a largest radix')
                            need(tables.read()==PAGE_BEGIN,'chirp table begins at each axis')
                            tables.step(1)
                            with owned(*read_pair(tables,width)) as value:
                                need(not value[0].negative and compare(value[0].magnitude,unit)==0
                                     and value[1].magnitude.zero(),'exact unit chirp zero entry')
                            with owned(power_two(length),Count.literal(1)) as (radix,one_count):
                                with owned(subtract(radix,one_count)) as (rest,):
                                    with owned(Count.product(rest,entry_bits)) as (bits,):
                                        walk(tables,bits,1,True)
                            need(tables.read()==PAGE_END,'exact radix-sized chirp page')
                            tables.step(1)
                            write_pair((one,imaginary),self.cache,width)
                            self.axes+=1
                    need(tables.read()==BLANK,'complete chirp table catalogue')
                    write_pair((one,imaginary),self.cache,width)
                finally:one.close();imaginary.close()
            self.counter.rewind();self.cache.rewind();tables.rewind();shape.rewind()
            need(tables.read()==PAGE_BEGIN,'first chirp page');tables.step(1)
            walk(tables,entry_bits,1,True)
        finally:
            if first_width is not None:first_width.close()

    def replace_cache(self,value,word_scratch,width,entry_bits):
        """Validate/encode before making an interior hole in the cache body."""
        write_pair(value,word_scratch,width);word_scratch.rewind()
        for _ in indices(entry_bits):
            need(self.cache.read() in (0,1),'complete overwritten cache slot')
            self.cache.write(BLANK);self.cache.step(1)
        walk(self.cache,entry_bits,-1)
        copy_bits(word_scratch,self.cache,entry_bits)
        need(word_scratch.read()==BLANK,'complete replacement cache word')
        borrowed_tape(word_scratch).clear()

    def advance(self,tables,width,precision,entry_bits,word_scratch):
        higher=False
        while increment_field(self.counter):
            walk(self.cache,entry_bits,1,True)
            has_page=next_page(tables)
            if self.counter.read()==BLANK:
                need(not has_page,'counter and page catalogue end together');return None
            need(has_page and self.counter.read() in (0,1),'carry has a following axis')
            higher=True
        if higher:
            with owned(read_field(self.counter)) as (digit,):
                with owned(Count.product(digit,entry_bits)) as (offset,):
                    walk(tables,offset,1,True)
        walk(self.cache,entry_bits,1,True)
        suffix=read_pair(self.cache,width)
        walk(self.cache,entry_bits,-1);walk(self.cache,entry_bits,-1)
        try:
            while True:
                with owned(*read_pair(tables,width)) as factor:
                    following=self.rounded_product(factor,suffix,width,precision)
                for value in suffix:value.close()
                suffix=following
                self.replace_cache(suffix,word_scratch,width,entry_bits)
                self.cache_updates+=1
                if not previous_field(self.counter):break
                walk(self.cache,entry_bits,-1);walk(self.cache,entry_bits,-1)
                previous_page(tables)
            walk(self.cache,entry_bits,-1)
            result,suffix=suffix,None;return result
        finally:
            if suffix is not None:
                for value in suffix:value.close()

    def emit(self,payload,phase,width,precision,conjugate):
        with owned(*read_pair(payload,width)) as value:
            with owned(phase[1].negated() if conjugate else phase[1].copy()) as (imaginary,):
                with owned(*self.rounded_product(value,(phase[0],imaginary),width,precision)) as result:
                    write_pair(result,self.output,width)
        self.records+=1

    def run(self,payload,shape,tables,width,precision,conjugate=False):
        payload,shape,tables=(borrowed_tape(v) for v in (payload,shape,tables))
        width,precision=borrowed_count(width),borrowed_count(precision)
        ports=(payload,shape,tables,width.tape,precision.tape)
        need(type(conjugate) is bool,'one finite conjugation mode')
        need(len({id(v) for v in ports})==5 and all(v not in self.forbidden() for v in ports),
             'distinct external cached-chirp ports')
        for tape in ports:origin(tape)
        positive(width)
        need(compare(precision,width)<0,'chirp fractional field fits width')
        need(self.closed and not self.pending and not self.pool.live and self.output.read()==BLANK,
             'consume prior cached-chirp output')
        self.idle()
        for tape in (*self.pool.tapes,self.counter,self.cache,self.output):initialize_marker(tape)
        self.closed=False;succeeded=False;word_scratch=None;phase=None
        try:
            with sealed_constructors(),self.scope.installed():
                try:
                    word_scratch=self.pool.acquire()
                    with owned(Count(precision)) as (guard,):
                        guard.increment();guard.increment()
                        need(compare(guard,width)<=0,'positive unit phase fits signed carrier')
                    with owned(Count(width)) as (entry_bits,):
                        entry_bits.multiply_small(2)
                        self.initialize(shape,tables,width,precision,entry_bits)
                        phase=(Signed(power_two(precision)),Signed(Count.literal(0)))
                        while True:
                            self.emit(payload,phase,width,precision,conjugate)
                            for value in phase:value.close()
                            phase=None
                            phase=self.advance(tables,width,precision,entry_bits,word_scratch)
                            if phase is None:break
                        need(payload.read()==BLANK,'complete axis0-packed polynomial payload')
                    self.idle();self.calls+=1;succeeded=self.pending=True
                finally:
                    if phase is not None:
                        for value in phase:value.close()
                    if word_scratch is not None:word_scratch.clear()
                    self.counter.clear();self.cache.clear();self.pool.empty()
                    for tape in ports:tape.rewind()
        finally:
            for tape in (*self.pool.tapes,self.counter,self.cache):erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear();erase_marker(self.output);self.pending=False
            self.closed=True
        return self.output
