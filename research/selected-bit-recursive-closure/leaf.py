"""Completed weighted leaves from sequential digit swaps, ADDs and a sign.

The source527 factorization is inherited. No weighted-child or ordinary-swap
oracle is accepted by this implementation.
"""
from dataclasses import dataclass, field
from math import prod

from controlled_stream import Tape, Meter, copy_bits, controlled_add
from physical_stream import Layout, Execution, sign_pass
from provider import need, build_weights


@dataclass
class LeafMeter:
    movement: Meter = field(default_factory=Meter)
    digit_swaps: int = 0
    ordinary_atom_swaps: int = 0
    ordered_shifts: int = 0
    fixed_signs: int = 0
    opaque_child_calls: int = 0
    max_bucket_tapes: int = 0


def digit_swap(source,radices,first,second,payload,q,meter):
    """Swap two radix-q digits using q^2 sequential bucket streams."""
    need(0<=first<second<len(radices) and radices[first]==radices[second]==q,
         "two ordered radix-q digit positions")
    middle=prod(radices[first+1:second]);suffix=prod(radices[second+1:])*payload
    slab=q*q*middle*suffix
    need(len(source.bits)%slab==0,"complete digit-swap slabs")
    buckets=[Tape(meter.movement) for _ in range(q*q)]
    output=Tape(meter.movement);source.rewind()
    for _prefix in range(len(source.bits)//slab):
        for a in range(q):
            for _gap in range(middle):
                for b in range(q):
                    copy_bits(source,buckets[a*q+b],suffix)
        for bucket in buckets:
            bucket.rewind()
        for b in range(q):
            for _gap in range(middle):
                for a in range(q):
                    copy_bits(buckets[a*q+b],output,suffix)
        for bucket in buckets:
            bucket.finished();bucket.erase()
            need(not bucket.bits and bucket.head==0,"digit bucket cleanup")
    source.finished();source.erase();output.rewind()
    meter.digit_swaps+=1;meter.max_bucket_tapes=max(meter.max_bucket_tapes,q*q)
    return output


def ordinary_swap(source,layout,q,width,first_atom,second_atom,meter,omit_digit=False):
    n=layout.dimension
    need(layout.columns==1 and layout.modulus==q**width,"leaf atom radix")
    digits=(q,)*(n*width)+(layout.gap,)+(q,)*(n*width)
    def axis(atom,position):
        return atom*width+position+int(atom>=n)
    for position in range(width):
        if omit_digit and position==width-1:
            continue
        source=digit_swap(source,digits,axis(first_atom,position),axis(second_atom,position),
                          layout.payload,q,meter)
    meter.ordinary_atom_swaps+=1
    return source


def shift(source,recipes,layout,first_atom,second_atom,index,inverse,meter,
          wrong_inverse=False,low_ancestors=False):
    first,second=layout.axis(first_atom),layout.axis(second_atom)
    before=layout.unused*prod(layout.radices[:first])
    middle=prod(layout.radices[first+1:second])
    suffix=layout.payload*prod(layout.radices[second+1:])
    def evaluate(recipe):
        weights,arithmetic=build_weights(recipe,low_ancestors)
        a=weights.value(index)
        arithmetic.counts["leaf_weight_requests"]+=1
        c=-(a if wrong_inverse else arithmetic.inv(a))%layout.modulus if inverse else a
        return c,arithmetic
    output=controlled_add(source,recipes,before,layout.modulus,middle,suffix,evaluate)
    source.erase();meter.ordered_shifts+=1
    return output


def execute_leaf(raw,recipes,count,offset=0,unused=1,gap=1,payload=1,
                 wrong_inverse=False,low_ancestors=False,omit_digit=False):
    need(bool(recipes) and 0<=count<64 and offset>=0,"stopped leaf domain")
    q,width=recipes[0].q,recipes[0].width
    need(all((r.q,r.width)==(q,width) for r in recipes),"one leaf atom ring")
    layout=Layout(count,1,q**width,unused,gap,payload)
    need(len(raw)==len(recipes)*unused*layout.rows*payload,"complete weighted leaf payload")
    if count:
        for recipe in recipes:
            weights,_=build_weights(recipe)
            need(offset+count<=weights.size,"leaf weight slice extent")
    meter=LeafMeter();source=Tape(meter.movement,raw)
    for i in range(count):
        first,second=i,2*count-1-i
        source=ordinary_swap(source,layout,q,width,first,second,meter,omit_digit)
        source=shift(source,recipes,layout,first,second,offset+i,False,meter,
                     wrong_inverse,low_ancestors)
        source=ordinary_swap(source,layout,q,width,first,second,meter,omit_digit)
        source=shift(source,recipes,layout,first,second,offset+i,True,meter,
                     wrong_inverse,low_ancestors)
        source=ordinary_swap(source,layout,q,width,first,second,meter,omit_digit)
        source=shift(source,recipes,layout,first,second,offset+i,False,meter,
                     wrong_inverse,low_ancestors)
        source=ordinary_swap(source,layout,q,width,first,second,meter,omit_digit)
        sign_execution=Execution(meter.movement)
        source=sign_pass(source,layout,layout.axis(second),sign_execution)
        meter.fixed_signs+=sign_execution.fixed_sign_passes
    need(source.head==0 and len(source.bits)==len(raw),"completed leaf return boundary")
    need(meter.ordinary_atom_swaps==4*count and meter.ordered_shifts==3*count and
         meter.fixed_signs==count and meter.opaque_child_calls==0,"literal leaf call inventory")
    if not omit_digit:
        need(meter.digit_swaps==4*count*width,"elementary ordinary implementation bill")
    return source.bits,meter,layout


def direct_leaf(raw,recipes,layout,offset=0):
    """Independent direct F_A address permutation; no factor execution."""
    out=[None]*len(raw);n=layout.dimension;modulus=layout.modulus
    for parent,recipe in enumerate(recipes):
        descriptor,_=build_weights(recipe)
        weights=[descriptor.value(offset+i) for i in range(n)]
        for stock in range(layout.unused):
            for row in range(layout.rows):
                values=layout.decode(row);new=values[:]
                for i,a in enumerate(weights):
                    first,second=layout.axis(i),layout.axis(2*n-1-i)
                    new[first]=a*values[second]%modulus
                    new[second]=pow(a,-1,modulus)*values[first]%modulus
                destination=layout.encode(new)
                src=((parent*layout.unused+stock)*layout.rows+row)*layout.payload
                dst=((parent*layout.unused+stock)*layout.rows+destination)*layout.payload
                need(out[dst] is None,"direct leaf address bijection")
                out[dst:dst+layout.payload]=raw[src:src+layout.payload]
    need(all(x is not None for x in out),"direct leaf full coverage")
    return out
