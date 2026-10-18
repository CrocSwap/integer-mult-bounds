"""Sequential payload permutations for full-prefix-controlled later-target ADDs."""
from collections import Counter
from dataclasses import dataclass,field
from controlled_normalizer import need


@dataclass
class Meter:
    payload_reads:int=0
    payload_writes:int=0
    head_moves:int=0
    scratch_erases:int=0
    preparation:Counter=field(default_factory=Counter)
    prefix_cells:int=0
    preparation_calls:int=0
    offset_multiplications:int=0
    ordinary_calls:int=0


class Tape:
    def __init__(self,meter,bits=()):
        self.meter=meter;self.bits=list(bits);self.head=0

    def read(self):
        need(self.head<len(self.bits),"read beyond stream")
        bit=self.bits[self.head];self.head+=1
        self.meter.payload_reads+=1;self.meter.head_moves+=1
        return bit

    def write(self,bit):
        need(self.head==len(self.bits) and bit in (0,1),"append bit")
        self.bits.append(bit);self.head+=1
        self.meter.payload_writes+=1;self.meter.head_moves+=1

    def rewind(self):
        self.meter.head_moves+=self.head;self.head=0

    def erase(self):
        self.rewind()
        for _ in self.bits:
            self.meter.scratch_erases+=1;self.meter.head_moves+=1;self.head+=1
        self.rewind();self.bits.clear()

    def finished(self):need(self.head==len(self.bits),"unconsumed fiber")


def copy_bits(source,destination,count):
    for _ in range(count):destination.write(source.read())


def controlled_add(source,parents,unused_count,modulus,middle,suffix,evaluate):
    """Layout: parent | unused stock | X | middle | Y | payload.

    Move the record at Y to Y+c(parent)X. The evaluator has no unused-stock
    argument. All payload access is sequential; no ordinary interchange occurs.
    This is an out-of-place pass with reusable split tapes.
    """
    need(modulus>=3 and unused_count>=1 and middle>=1 and suffix>=1,"complete field extents")
    volume=len(parents)*unused_count*modulus*middle*modulus*suffix
    need(len(source.bits)==volume,"complete controlled stream")
    meter=source.meter;left,right,out=(Tape(meter) for _ in range(3))
    source.rewind()
    for parent in parents:
        c,arithmetic=evaluate(parent)
        meter.preparation.update(arithmetic.counts);meter.prefix_cells+=arithmetic.prefix_cells
        meter.preparation_calls+=1
        for _unused in range(unused_count):
            for x in range(modulus):
                offset=c*x%modulus;meter.offset_multiplications+=1
                for _ in range(middle):
                    copy_bits(source,left,(modulus-offset)*suffix)
                    copy_bits(source,right,offset*suffix)
    source.finished();source.rewind();left.rewind();right.rewind()
    for parent in parents:
        c,arithmetic=evaluate(parent)
        meter.preparation.update(arithmetic.counts);meter.prefix_cells+=arithmetic.prefix_cells
        meter.preparation_calls+=1
        for _unused in range(unused_count):
            for x in range(modulus):
                offset=c*x%modulus;meter.offset_multiplications+=1
                for _ in range(middle):
                    copy_bits(right,out,offset*suffix)
                    copy_bits(left,out,(modulus-offset)*suffix)
    left.finished();right.finished();left.erase();right.erase();out.rewind()
    need(left.head==right.head==0 and not left.bits and not right.bits,"clean split scratch")
    need(source.head==out.head==0,"restored stream heads")
    return out
