"""Exact fixed-grid Gaussian words; no rounding at a child return.

Word arrays stand for local arithmetic tapes. Each loop traverses them in
order; arithmetic_steps charges their bit traversals separately from payload.
"""
from dataclasses import dataclass,field
from fractions import Fraction

from streams import need,Tape,copy


@dataclass
class Grid:
    bits: int
    fraction_bits: int
    arithmetic_steps: int=0
    exact_divisions: int=0
    workspace: list=field(default_factory=list)
    peak_words: int=0

    def track(self,word):
        self.workspace.append(word);self.peak_words=max(self.peak_words,len(self.workspace))
        return word

    def close(self):
        for word in self.workspace:
            for i in range(len(word)):word[i]=0
            self.arithmetic_steps+=len(word)
        self.workspace.clear()

    def check(self,a):
        need(len(a)==self.bits and all(x in (0,1) for x in a),"one signed grid word")

    def zero(self):return self.track(bytearray(self.bits))

    def add(self,a,b):
        self.check(a);self.check(b);out=bytearray();carry=0
        for x,y in zip(a,b):
            value=x+y+carry;out.append(value&1);carry=value>>1
        self.arithmetic_steps+=8*self.bits
        need(a[-1]!=b[-1] or out[-1]==a[-1],"signed addition headroom")
        return self.track(out)

    def neg(self,a):
        self.check(a);out=bytearray();carry=1
        for x in a:
            value=1-x+carry;out.append(value&1);carry=value>>1
        self.arithmetic_steps+=6*self.bits
        need(not (a[-1] and out[-1]),"signed negation headroom")
        return self.track(out)

    def subtract(self,a,b):return self.add(a,self.neg(b))

    def divide(self,a,k):
        self.check(a);need(0<=k<self.bits,"binary division extent")
        need(not any(a[:k]),"division discards only reserved zero bits")
        self.arithmetic_steps+=6*self.bits;self.exact_divisions+=int(k>0)
        return self.track(bytearray(a[k:])+bytearray((a[-1],))*k)

    def scale(self,a,coefficient):
        c=Fraction(coefficient);n=abs(c.numerator);den=c.denominator
        need(den&(den-1)==0,"Gaussian-dyadic scalar")
        out=self.zero()
        for bit in bin(n)[2:]:
            out=self.add(out,out)
            if bit=="1":out=self.add(out,a)
        if c<0:out=self.neg(out)
        return self.divide(out,den.bit_length()-1)

    def phase(self,z,k):
        real,imag=z;k%=4
        if k==0:return real,imag
        if k==1:return self.neg(imag),real
        if k==2:return self.neg(real),self.neg(imag)
        return imag,self.neg(real)

    def pair(self,a,b,inverse=False):
        p=(self.add(a[0],b[0]),self.add(a[1],b[1]))
        q=self.phase((self.subtract(a[0],b[0]),self.subtract(a[1],b[1])),
                     -1 if inverse else 1)
        first=(self.divide(self.add(p[0],q[0]),1),self.divide(self.add(p[1],q[1]),1))
        second=(self.divide(self.subtract(p[0],q[0]),1),self.divide(self.subtract(p[1],q[1]),1))
        return first,second


def read_number(tape,grid):return grid.track(tape.read(grid.bits)),grid.track(tape.read(grid.bits))


def write_number(tape,value):
    tape.write(value[0]);tape.write(value[1])


def c_axis(source,address_bits,position,coefficients,grid,inverse=False,outer_rows=1):
    """One exact C axis on complete Gaussian records, with sequential tapes."""
    need(0<=position<address_bits and coefficients>=1 and outer_rows>=1,"selected C axis")
    record=2*grid.bits*coefficients;suffix=(1<<(address_bits-position-1))*record
    need(len(source.data)==outer_rows*(1<<address_bits)*record,"complete C payload")
    source.rewind();left=Tape(source.meter);right=Tape(source.meter)
    for _ in range(outer_rows*(1<<position)):copy(source,left,suffix);copy(source,right,suffix)
    source.finish();left.rewind();right.rewind()
    out_left=Tape(source.meter);out_right=Tape(source.meter)
    for _ in range(outer_rows*(1<<(address_bits-1))*coefficients):
        a,b=grid.pair(read_number(left,grid),read_number(right,grid),inverse)
        write_number(out_left,a);write_number(out_right,b)
        grid.close()
    left.finish();right.finish();left.erase();right.erase()
    out_left.rewind();out_right.rewind();out=Tape(source.meter)
    for _ in range(outer_rows*(1<<position)):copy(out_left,out,suffix);copy(out_right,out,suffix)
    out_left.finish();out_right.finish();out_left.erase();out_right.erase();source.erase()
    out.rewind();return out


def scalar_add(target,source,coefficient,grid):
    need(target is not source and len(target.data)==len(source.data),"distinct aligned scalar operands")
    size=2*grid.bits;need(len(target.data)%size==0,"complete Gaussian scalar records")
    target.rewind();source.rewind();out=Tape(target.meter)
    for _ in range(len(target.data)//size):
        a=read_number(target,grid);b=read_number(source,grid)
        write_number(out,tuple(grid.add(x,grid.scale(y,coefficient)) for x,y in zip(a,b)))
        grid.close()
    target.finish();source.finish();target.erase();source.rewind();out.rewind()
    return out


def scalar_scale(source,coefficient,grid):
    need(len(source.data)%(2*grid.bits)==0,"complete scalar scale records")
    source.rewind();out=Tape(source.meter)
    for _ in range(len(source.data)//(2*grid.bits)):
        write_number(out,tuple(grid.scale(x,coefficient) for x in read_number(source,grid)))
        grid.close()
    source.finish();source.erase();out.rewind();return out


def clear_packet(source):
    size=len(source.data);source.erase();source.write(bytes(size));source.rewind()
    return source


def normalize_b(source,axes,grid):
    """b^axes, b=(1-i)/2, using one variable shift rather than axes passes."""
    need(axes>=0 and len(source.data)%(2*grid.bits)==0,"normalization extent")
    source.rewind();out=Tape(source.meter);k,odd=divmod(axes,2)
    for _ in range(len(source.data)//(2*grid.bits)):
        z=read_number(source,grid)
        if odd:
            z=(grid.divide(grid.add(z[0],z[1]),1),
               grid.divide(grid.subtract(z[1],z[0]),1))
        z=grid.phase(z,-k)
        write_number(out,tuple(grid.divide(x,k) for x in z))
        grid.close()
    source.finish();source.erase();out.rewind();return out
