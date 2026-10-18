"""Closed high-header primitives with elementary ordinary interchanges.

The affine/carry and monotone-piece constructions come from PR2157. This
implementation supplies the ordinary base and explicit scratch closure.
Only fixed dyadic route coefficients may use the scale primitive below.
"""
from fractions import Fraction as F
from math import gcd

from controlled_stream import Tape,copy_bits
from physical_stream import pop_bit
from qadic_streams import low_update
from provider import need
from leaf import LeafMeter,digit_swap


def rotate(source,radix,block,fibres,offset,meter):
    need(len(source.bits)==radix*block*fibres,"complete affine header fibres")
    source.rewind();left,right,out=(Tape(meter.movement) for _ in range(3))
    for prefix in range(fibres):
        cut=offset(prefix)%radix
        copy_bits(source,left,(radix-cut)*block);copy_bits(source,right,cut*block)
    source.finished();left.rewind();right.rewind()
    for prefix in range(fibres):
        cut=offset(prefix)%radix
        copy_bits(right,out,cut*block);copy_bits(left,out,(radix-cut)*block)
    left.finished();right.finished();left.erase();right.erase();source.erase();out.rewind()
    meter.ordered_shifts+=1
    return out


def multiply_fixed(source,radix,block,fibres,integer,meter,inverse=False):
    need(integer>=1 and gcd(integer,radix)==1,"fixed integer unit")
    need(len(source.bits)==radix*block*fibres,"complete fixed-scale fibres")
    if integer==1 or radix==1:
        need(source.head==0,"identity scale origin")
        return source
    pieces=[Tape(meter.movement) for _ in range(integer)];out=Tape(meter.movement)
    source.rewind();inv=pow(radix,-1,integer)
    lengths=[((j+1)*radix+integer-1)//integer-(j*radix+integer-1)//integer
             for j in range(integer)]
    if not inverse:
        for _ in range(fibres):
            for j,length in enumerate(lengths):
                copy_bits(source,pieces[j],length*block)
        for piece in pieces:piece.rewind()
        for _ in range(fibres):
            for value in range(radix):
                copy_bits(pieces[(-value*inv)%integer],out,block)
    else:
        for _ in range(fibres):
            for value in range(radix):
                copy_bits(source,pieces[(-value*inv)%integer],block)
        for piece in pieces:piece.rewind()
        for _ in range(fibres):
            for j,length in enumerate(lengths):
                copy_bits(pieces[j],out,length*block)
    source.finished()
    for piece in pieces:piece.finished();piece.erase()
    source.erase();out.rewind()
    meter.max_bucket_tapes=max(meter.max_bucket_tapes,integer)
    return out


def negate(source,radix,block,fibres,meter):
    need(len(source.bits)==radix*block*fibres,"complete header sign fibres")
    source.rewind();out,reverse,small=(Tape(meter.movement) for _ in range(3))
    for _ in range(fibres):
        copy_bits(source,out,block)
        copy_bits(source,reverse,(radix-1)*block)
        for _value in range(radix-1):
            for _bit in range(block):small.write(pop_bit(reverse))
            for _bit in range(block):out.write(pop_bit(small))
        need(not reverse.bits and not small.bits,"header sign scratch closure")
    source.finished();source.erase();out.rewind();meter.fixed_signs+=1
    return out


def scale(source,radix,block,fibres,coefficient,meter):
    coefficient=F(coefficient);a,b=abs(coefficient.numerator),coefficient.denominator
    need(a>0 and a&(a-1)==0 and b&(b-1)==0,"fixed dyadic route alphabet")
    if coefficient<0:source=negate(source,radix,block,fibres,meter)
    source=multiply_fixed(source,radix,block,fibres,a,meter)
    return multiply_fixed(source,radix,block,fibres,b,meter,True)


def ordinary_fields(source,q,width,before,middle,suffix,meter):
    radix=q**width
    need(len(source.bits)==before*radix*middle*radix*suffix,"header ordinary extent")
    if width==0:
        return source
    radices=(q,)*width+(middle,)+(q,)*width
    for position in range(width):
        source=digit_swap(source,radices,position,width+1+position,suffix,q,meter)
    meter.ordinary_atom_swaps+=1
    return source


def add(source,q,width,low_x,low_y,coefficient,before,middle,suffix,meter,
        reversed_fields=False,omit_carry=False):
    coefficient=F(coefficient);radix=q**(width-1)
    new,carry=low_update(low_x,low_y,coefficient,q)
    if omit_carry:carry=0
    if radix==1:
        return source,new
    if reversed_fields:
        source=ordinary_fields(source,q,width-1,before,middle,suffix,meter)
    fibres=before*radix*middle
    source=scale(source,radix,suffix,fibres,F(coefficient.denominator),meter)
    source=rotate(source,radix,suffix,fibres,
        lambda prefix:coefficient.numerator*((prefix//middle)%radix)+carry,meter)
    source=scale(source,radix,suffix,fibres,F(1,coefficient.denominator),meter)
    if reversed_fields:
        source=ordinary_fields(source,q,width-1,before,middle,suffix,meter)
    return source,new


def finite_classes(source,before,classes,block,permutation,meter):
    need(sorted(permutation)==list(range(classes)),"fixed low-class permutation")
    need(len(source.bits)==before*classes*block,"low-class packet extent")
    pieces=[Tape(meter.movement) for _ in range(classes)];out=Tape(meter.movement)
    source.rewind()
    for _ in range(before):
        for old in range(classes):copy_bits(source,pieces[permutation[old]],block)
    source.finished()
    for piece in pieces:piece.rewind()
    for _ in range(before):
        for piece in pieces:copy_bits(piece,out,block)
    for piece in pieces:piece.finished();piece.erase()
    source.erase();out.rewind();meter.max_bucket_tapes=max(meter.max_bucket_tapes,classes)
    return out


def scale_affine(source,q,width,low,coefficient,before,suffix,meter):
    coefficient=F(coefficient);radix=q**(width-1)
    new,carry=low_update(0,low,coefficient,q,True)
    if radix==1:return source,new
    source=scale(source,radix,suffix,before,F(coefficient.numerator),meter)
    source=rotate(source,radix,suffix,before,lambda _p:carry,meter)
    source=scale(source,radix,suffix,before,F(1,coefficient.denominator),meter)
    return source,new
