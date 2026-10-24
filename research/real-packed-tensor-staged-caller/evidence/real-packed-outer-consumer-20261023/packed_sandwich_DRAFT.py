"""DRAFT: one packed actual forward Tensor and one opposite Tensor.

Derived from JoyboyBrian PR5095 e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1.
No factory/runtime execution yet. Substantial OpenAI Codex assistance.
Predecessor notices and Apache-2.0 retained.
"""
from cardinal_counts import Count,positive
from compact_counts import append_bits,copy_bits,read_fixed
from encoded import compare,subtract
from fft_arithmetic import Arithmetic
from records import Tape
from ring_words import add,difference,Signed,nearest,power_two,read_signed,right_shift,scaled,truncate,write_signed
from router_metadata import indices,owned
from scratch_pool import ScratchPool
from session import OuterScope,borrowed_count,borrowed_tape,erase_marker,initialize_marker,sealed_constructors
from stream import Counter
from tensor_catalogue import Catalogue
from tensor_word import DigitWordProduct
from words import BLANK,LEFT,RIGHT,need

class RealPackedSandwich:
    def __init__(self,tensor,converter):
        # Transfer only fresh top-level owners; failure leaves them untouched.
        need(tensor.closed and not tensor.pool.live and tensor.calls==0 and tensor.last_counts is None,"fresh Tensor owner")
        need(converter.closed and not converter.pool.live and converter.last_counts is None,"fresh Converter owner")
        left,right=private_tapes(tensor),private_tapes(converter)
        need(not ({id(t) for t in left}&{id(t) for t in right}),"disjoint child owners")
        self.tensor,self.converter=tensor,converter
        self.pool,self.word=ScratchPool(128),DigitWordProduct()
        self.scope=OuterScope(self.pool)
        self.arithmetic=Arithmetic(self.word,self.scope)
        self.output=Tape();self.closed=True;self.last_counts=None;self.pending=False
        for t in (*self.pool.tapes,self.output):erase_marker(t)
        self.private=private_tapes(self)
        for t in self.private:
            need(t.read()==BLANK,"empty transferred resident tape")
            t.step(-1)
            try:need(t.read() in (BLANK,LEFT),"empty transferred resident origin")
            finally:t.step(1)

    def consume(self):
        """Release the borrowed return; valid after any read-only head movement."""
        need(self.closed and self.pending,"pending sandwich return")
        self.output.clear();erase_marker(self.output);self.pending=False

    def child(self,operation,*args,**options):
        returned=result=None
        try:
            with self.scope.suspended():returned=operation(*args,**options)
            result=self.pool.acquire();append_bits(returned,result);result.rewind()
            saved,result=result,None
            return saved
        finally:
            for t in (returned,result):
                if t is not None:
                    t.clear()
                    if t is returned:erase_marker(t)

    def ingress(self,source,plan,b,q):
        out=self.pool.acquire();source.rewind()
        with owned(Count(b),Count.literal(0)) as (shift,index):
            shift.increment();shift.increment()
            with owned(subtract(plan.p,shift)) as (amount,):
                for _ in indices(plan.source_product):
                    magnitude=read_fixed(source,b) if compare(index,q)<0 else Count.literal(0)
                    with owned(Signed(magnitude),Signed(Count.literal(0))) as (digit,zero):
                        with owned(scaled(digit,amount)) as (value,):
                            write_signed(value,out,plan.component_bits);write_signed(zero,out,plan.component_bits)
                    index.increment()
        need(source.read()==BLANK,'complete packed radix digits')
        source.rewind();out.rewind();return out

    def pack_real(self,first,second,plan):
        """Two independent converted real banks, same exact p-grid."""
        out=self.pool.acquire();first.rewind();second.rewind()
        for _ in indices(plan.source_product):
            with owned(*(read_signed(t,plan.component_bits) for t in (first,first,second,second))) as (a,ai,b,bi):
                need(ai.magnitude.zero() and bi.magnitude.zero(),'two real converted operand banks')
                write_signed(a,out,plan.component_bits);write_signed(b,out,plan.component_bits)
                self.last_counts['packed_records']+=1
        need(first.read()==second.read()==BLANK,'complete two-real packing inputs')
        first.rewind();second.rewind();out.rewind();return out

    @staticmethod
    def move_bits(tape,length,direction):
        for _ in indices(length):tape.step(direction)

    def negate_frequencies(self,bank,plan):
        """Charged axis passes: preserve group0, reverse nonzero groups.

        Bits inside each suffix group retain their order. Original H stays
        owned/intact. This is frequency negation, not whole-bank reversal.
        """
        current=bank
        for axis in indices(plan.dimensions):
            prefix,suffix=Count.literal(1),Count.literal(1)
            try:
                with owned(plan.axis(axis)) as (row,):
                    for position in indices(plan.dimensions):
                        side=compare(position,axis)
                        if side:
                            with owned(plan.axis(position)) as (other,):
                                following=Count.product(prefix if side<0 else suffix,other.s)
                                if side<0:prefix.close();prefix=following
                                else:suffix.close();suffix=following
                    with owned(Count.literal(1)) as (one,):groups=subtract(row.s,one)
                    with owned(groups,Count.product(suffix,plan.record_bits)) as (groups,group_bits):
                        with owned(Count.product(groups,group_bits)) as (skip,):
                            out=self.pool.acquire();current.rewind()
                            for _ in indices(prefix):
                                copy_bits(current,out,group_bits)
                                self.move_bits(current,skip,1)
                                for _ in indices(groups):
                                    self.move_bits(current,group_bits,-1)
                                    copy_bits(current,out,group_bits)
                                    self.move_bits(current,group_bits,-1)
                                self.move_bits(current,skip,1)
                            need(current.read()==BLANK,'complete frequency-negation axis input')
                            current.rewind();out.rewind()
                            if current is not bank:current.clear()
                            current=out;self.last_counts['J_axis_passes']+=1
            finally:prefix.close();suffix.close()
        bank.rewind();current.rewind();return current

    def pointwise(self,first,reflected,plan):
        """Exact split grid p+1; exact product; one truncation to grid p."""
        out=self.pool.acquire();first.rewind();reflected.rewind()
        with owned(Count(plan.component_bits),Count(plan.p)) as (split_width,shift):
            split_width.increment();shift.increment();shift.increment()
            for _ in indices(plan.source_product):
                with owned(*(read_signed(t,plan.component_bits) for t in (first,first,reflected,reflected))) as (a,b,c,d):
                    # H#=c-id. A=(H+H#)/2; B=(H-H#)/(2i).
                    # Raw sums have denominator2^(p+1); NO split rounding.
                    with owned(add(a,c),difference(b,d),add(b,d),difference(c,a)) as (ar,ai,br,bi):
                        with owned(*self.arithmetic.complex_product(ar,ai,br,bi,split_width)) as (real,imag):
                            with owned(truncate(real,shift),truncate(imag,shift)) as (r,i):
                                write_signed(r,out,plan.component_bits);write_signed(i,out,plan.component_bits)
                    self.last_counts['split_records']+=1
                    self.last_counts['split_exact_adds']+=4
                    self.last_counts['pointwise_real_products']+=4
        need(first.read()==reflected.read()==BLANK,'complete packed/reflected inputs')
        first.rewind();reflected.rewind();out.rewind();return out

    def recover(self,source,plan,b,width):
        out=self.pool.acquire()
        with owned(Count(b),Signed(Count(plan.source_product))) as (shift,S):
            shift.multiply_small(2)
            for _ in range(4):shift.increment()
            for _ in indices(plan.source_product):
                with owned(read_signed(source,plan.component_bits),read_signed(source,plan.component_bits)) as (real,imag):
                    with owned(self.arithmetic.multiply(real,S,width)) as (once,):
                        with owned(self.arithmetic.multiply(once,S,width)) as (twice,):
                            with owned(scaled(twice,shift)) as (numerator,):
                                with owned(nearest(numerator,plan.p)) as (integer,):write_signed(integer,out,width)
        need(source.read()==BLANK,'complete opposite return')
        source.rewind();out.rewind();return out

    def carries(self,coefficients,plan,b,q,width):
        low=self.pool.acquire();carry=Count.literal(0)
        with owned(Count(q)) as (digits,):
            digits.multiply_small(2);remaining=Counter(digits)
            try:
                for _ in indices(plan.source_product):
                    with owned(read_signed(coefficients,width)) as (coefficient,):
                        need(not coefficient.negative,'nonnegative recovered coefficient')
                        coefficient.magnitude.add(carry);carry.close()
                        carry=right_shift(coefficient.magnitude,b);coefficient.magnitude.rewind()
                        emitted=not remaining.finished
                        for _ in indices(b):
                            symbol=coefficient.magnitude.read();bit=0 if symbol==RIGHT else symbol
                            need(bit in (0,1),'canonical carry digit')
                            if emitted:low.append(bit)
                            else:need(bit==0,'zero high product coefficient')
                            if symbol!=RIGHT:coefficient.magnitude.step(1)
                        if emitted:remaining.decrement()
                need(coefficients.read()==BLANK,'complete coefficient return')
                if not remaining.finished:
                    carry.rewind()
                    for _ in indices(b):
                        symbol=carry.read();low.append(0 if symbol==RIGHT else symbol)
                        if symbol!=RIGHT:carry.step(1)
                    need(carry.read()==RIGHT,'final carry fits radix')
                    remaining.decrement();need(remaining.finished,'one final carry digit')
                else:need(carry.zero(),'zero terminal carry')
                low.step(-1)
                with owned(Count.product(digits,b)) as (bits,):
                    for _ in indices(bits):
                        need(low.read() in (0,1),'complete reversed product bits')
                        self.output.append(low.read());low.step(-1)
                    low.step(1)
            finally:remaining.close();carry.close();low.clear();coefficients.rewind()

    def admit(self,plan,b):
        need(not plan.mode.zero(),'production coefficient/locality contract required')
        with owned(Count.product(plan.p,plan.p),power_two(plan.outer_bits),Count(plan.dimensions)) as (p2,M,extra):
            with owned(Count.product(plan.dimensions,p2)) as (E,):
                M.multiply_small(6);E.add(M);extra.multiply_small(2);E.add(extra)
                with owned(Count.literal(22)) as (constant,):E.add(constant)
                with owned(Signed(Count(E))) as (signedE,):
                    with owned(scaled(signedE,plan.gamma)) as (restored,):
                        restored.magnitude.multiply_small(3)
                        with owned(Count.literal(2)) as (two,):restored.magnitude.add(two)
                        with owned(Count.product(plan.source_product,plan.source_product)) as (S2,):
                            with owned(Count.product(restored.magnitude,S2),Count(b)) as (bound,shift):
                                shift.multiply_small(2)
                                # Include 2 for the strict half-integer error threshold.
                                for _ in range(5):shift.increment()
                                with owned(Signed(Count(bound))) as (signed,):
                                    with owned(scaled(signed,shift),power_two(plan.p)) as (numerator,denominator):
                                        need(compare(numerator.magnitude,denominator)<0,'strict integer recovery error guard')

    def run(self,first,second,catalogue,b,q,require_recovery=True):
        need(type(require_recovery) is bool,'literal recovery policy')
        first,second,catalogue=(borrowed_tape(t) for t in (first,second,catalogue))
        b,q=borrowed_count(b),borrowed_count(q)
        ports=(first,second,catalogue,borrowed_tape(b.tape),borrowed_tape(q.tape))
        need(len({id(t) for t in ports})==5,'five distinct input ports')
        need(all(all(t is not private for private in self.private) for t in ports),'external sandwich ports')
        need(self.closed and not self.pool.live and not self.pending,'consume prior sandwich output')
        positive(b);positive(q)
        self.tensor.idle();self.converter.idle()
        for t in (*self.pool.tapes,self.output):initialize_marker(t)
        self.closed=False;book=None;succeeded=False
        self.last_counts={'conversions':0,'transforms':0,'pointwise_products':0,'packed_records':0,'J_axis_passes':0,'split_records':0,'split_exact_adds':0,'pointwise_real_products':0}
        try:
            with sealed_constructors(),self.scope.installed():
                try:
                    book=Catalogue(catalogue,self.pool.acquire);plan=book.plan
                    with owned(Count(q),power_two(b),Count(b),Count(plan.component_bits),Count.literal(1)) as (twiceq,radix,minp,width,rows):
                        twiceq.multiply_small(2)
                        with owned(subtract(twiceq,rows)) as (demand,):need(compare(demand,plan.source_product)<=0,'no wraparound')
                        minp.increment();minp.increment()
                        need(compare(plan.source_product,radix)<0,'source product fits radix')
                        need(compare(minp,plan.p)<=0,'exact ingress grid')
                        if require_recovery:self.admit(plan,b)
                        with owned(Count(b)) as (extra,):
                            extra.multiply_small(4)
                            for _ in range(4):extra.increment()
                            width.add(extra)
                        naturals=[]
                        for incoming in (first,second):
                            digits=self.ingress(incoming,plan,b,q)
                            natural=self.child(self.converter.run_plan,digits,plan,rows)
                            self.last_counts['conversions']+=1;digits.clear();naturals.append(natural)
                        packed=self.pack_real(*naturals,plan)
                        for t in naturals:t.clear()
                        transformed=self.child(self.tensor.run,packed,catalogue,rows)
                        self.last_counts['transforms']+=1;packed.clear()
                        reflected=self.negate_frequencies(transformed,plan)
                        product=self.pointwise(transformed,reflected,plan);self.last_counts['pointwise_products']=1
                        transformed.clear();reflected.clear()
                        opposite=self.child(self.tensor.run,product,catalogue,rows,opposite=True)
                        self.last_counts['transforms']+=1;product.clear()
                        recovered=self.recover(opposite,plan,b,width);opposite.clear()
                        ordinary=self.child(self.converter.run_plan,recovered,plan,rows,inverse=True,record_bits=width)
                        self.last_counts['conversions']+=1;recovered.clear()
                        self.carries(ordinary,plan,b,q,width);ordinary.clear()
                        self.tensor.idle();self.converter.idle();succeeded=True
                finally:
                    if book is not None:book.close()
                    for t in (first,second,catalogue):t.rewind()
                    b.rewind();q.rewind()
                    for lease in tuple(self.pool.live.values()):lease.clear()
                    self.pool.empty()
        finally:
            for t in self.pool.tapes:erase_marker(t)
            self.output.rewind()
            if not succeeded:self.output.clear();erase_marker(self.output)
            self.closed=True
        self.pending=True
        return self.output


def private_tapes(owner):
    """Construction-only inventory of the fixed resident owner graph.

    Stops at every Tape without inspecting its cells. The retained constructors
    allocate a parameter-independent graph; no input Count or packet is reachable.
    No reflection occurs in the charged run. Children transfer exclusive ownership.
    """
    seen=set();tapes=[]
    def visit(value):
        if id(value) in seen:return
        seen.add(id(value))
        if isinstance(value,Tape):tapes.append(value);return
        if isinstance(value,ScratchPool):need(not value.live,'lease-free transferred resident pool')
        if hasattr(value,'closed'):need(value.closed,'closed transferred resident owner')
        if isinstance(value,dict):
            for item in value.values():visit(item)
        elif isinstance(value,(tuple,list)):
            for item in value:visit(item)
        elif hasattr(value,'__dict__') and not callable(value):
            for item in vars(value).values():visit(item)
    visit(owner)
    return tuple(tapes)
