"""Sequential bit-stream simulator with charged contiguous transfers.

Bulk methods abbreviate consecutive tape transitions; they charge each bit.
Payload destinations are append-only. Random lookup is confined to controls.
"""
from dataclasses import dataclass,field


def need(condition,message):
    if not condition:
        raise ValueError(message)


@dataclass
class Meter:
    reads: int=0
    writes: int=0
    moves: int=0
    erases: int=0
    control_evaluations: int=0
    digit_passes: int=0
    rotation_passes: int=0
    radix_passes: int=0
    repair_records: int=0
    ordinary_calls: list=field(default_factory=list)


class Tape:
    def __init__(self,meter,data=b""):
        self.meter=meter;self.data=bytearray(data);self.head=0

    def read(self,size):
        need(0<=size<=len(self.data)-self.head,"sequential read boundary")
        value=self.data[self.head:self.head+size];self.head+=size
        self.meter.reads+=size;self.meter.moves+=size
        return value

    def write(self,value):
        need(self.head==len(self.data),"append-only output")
        self.data.extend(value);self.head+=len(value)
        self.meter.writes+=len(value);self.meter.moves+=len(value)

    def rewind(self):
        self.meter.moves+=self.head;self.head=0

    def finish(self):
        need(self.head==len(self.data),"complete sequential consumption")

    def erase(self):
        self.rewind();size=len(self.data)
        self.meter.erases+=size;self.meter.moves+=2*size
        self.data.clear();self.head=0


def copy(source,target,size):
    target.write(source.read(size))


def bit_key(value,width):
    need(0<=value<1<<width,"binary control key extent")
    return bytes((value>>i)&1 for i in range(width))


def key_value(bits):
    need(all(b in (0,1) for b in bits),"binary control encoding")
    return sum(b<<i for i,b in enumerate(bits))


def digit_permutation(source,total_bits,first,second,record_bits,mapping):
    """Two physical address-bit positions, numbered from the left."""
    need(0<=first<second<total_bits,"two ordered bit fields")
    need(sorted(mapping)==list(range(4)),"four-state permutation")
    middle=1<<(second-first-1);suffix=(1<<(total_bits-second-1))*record_bits
    slab=4*middle*suffix;need(len(source.data)%slab==0,"complete digit slabs")
    source.rewind();out=Tape(source.meter);buckets=[Tape(source.meter) for _ in range(4)]
    inverse=[mapping.index(i) for i in range(4)]
    for _prefix in range(len(source.data)//slab):
        for a in range(2):
            for _mid in range(middle):
                for b in range(2):copy(source,buckets[2*a+b],suffix)
        for bucket in buckets:bucket.rewind()
        for a in range(2):
            for _mid in range(middle):
                for b in range(2):copy(buckets[inverse[2*a+b]],out,suffix)
        for bucket in buckets:bucket.finish();bucket.erase()
    source.finish();source.erase();out.rewind();source.meter.digit_passes+=1
    return out


def flip_digit(source,total_bits,position,record_bits):
    suffix=(1<<(total_bits-position-1))*record_bits;slab=2*suffix
    need(len(source.data)%slab==0,"complete bit-flip slabs")
    source.rewind();out=Tape(source.meter);left=Tape(source.meter);right=Tape(source.meter)
    for _ in range(len(source.data)//slab):
        copy(source,left,suffix);copy(source,right,suffix)
        left.rewind();right.rewind();copy(right,out,suffix);copy(left,out,suffix)
        left.finish();right.finish();left.erase();right.erase()
    source.finish();source.erase();out.rewind();source.meter.digit_passes+=1
    return out


def stable_radix(source,key_bits,payload_bits):
    """LSD binary partition and concatenation; no sorting or seek oracle."""
    width=key_bits+payload_bits;need(len(source.data)%width==0,"complete keyed records")
    for position in range(key_bits):
        source.rewind();buckets=[Tape(source.meter),Tape(source.meter)]
        for _ in range(len(source.data)//width):
            key=source.read(key_bits)
            bucket=buckets[key[position]]
            bucket.write(key);copy(source,bucket,payload_bits)
        source.finish();source.erase();out=Tape(source.meter)
        for bucket in buckets:
            bucket.rewind();copy(bucket,out,len(bucket.data));bucket.finish();bucket.erase()
        out.rewind();source=out;source.meter.radix_passes+=1
    return source
