"""Complete GL2 high-packet controls and sequential restricted-fibre XOR."""
from dataclasses import dataclass
from itertools import product
from ring_algebra import need


def matrix_product(a,b,modulus):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2))%modulus
                 for i in range(2) for j in range(2))


def inverse2(a,modulus):
    u=pow((a[0]*a[3]-a[1]*a[2])%modulus,-1,modulus)
    return tuple(u*x%modulus for x in (a[3],-a[1],-a[2],a[0]))


def low_matrices(q):
    return [g for g in product(range(q),repeat=4) if (g[0]*g[3]-g[1]*g[2])%q]


def high_fibre(low,q,width):
    high=q**(width-1)
    return [tuple(a+q*b for a,b in zip(low,h)) for h in product(range(high),repeat=4)]


def binary_rank(rows):
    pivots={}
    for value in rows:
        while value:
            bit=value.bit_length()-1
            if bit in pivots:value^=pivots[bit]
            else:pivots[bit]=value;break
    return len(pivots)


def alias_control():
    q,modulus=3,9;identity=(1,0,0,1);sigma=(1,3,0,1)
    fibre=high_fibre(identity,q,2);index={g:i for i,g in enumerate(fibre)}
    sources=[matrix_product(g,inverse2(sigma,modulus),modulus) for g in fibre]
    need(all(g!=h for g,h in zip(fibre,sources)),"distinct point owners")
    need(set(sources)==set(fibre),"same complete low fibre")
    edges=[index[g] for g in sources]
    snapshot=[(1<<i)^(1<<j) for i,j in enumerate(edges)]
    serial=[1<<i for i in range(len(fibre))];bits=[1]*len(fibre)
    for i,j in enumerate(edges):serial[i]^=serial[j];bits[i]^=bits[j]
    need(binary_rank(snapshot)==54 and binary_rank(serial)==81,"snapshot/serial operator distinction")
    need(sum(bits)==27,"retained serial payload")
    remaining=set(range(81));lengths=[]
    while remaining:
        start=min(remaining);current=start;length=0
        while current in remaining:
            remaining.remove(current);length+=1;current=edges[current]
        need(current==start,"owner cycle closure");lengths.append(length)
    need(lengths==[3]*27,"high-only chart cycles")
    for other in ((0,1,1,0),(1,1,0,1)):
        images={matrix_product(g,inverse2(other,modulus),modulus) for g in fibre}
        need(len(images)==81 and not images.intersection(fibre),"different low charts separate complete packets")
    return {"q":3,"width":2,"high_fibre_size":81,"distinct_fixed_d_owners":81,
            "overlapping_packet_rows":81,"three_cycles":27,"snapshot_rank":54,
            "serial_rank":81,"snapshot_ones":0,"serial_ones":27,
            "separated_positive_controls":2,"status":"REJECT_WEAK_POINT_OWNER_CHECK"}


@dataclass
class Meter:
    reads:int=0
    writes:int=0
    moves:int=0
    erases:int=0
    full_family_scans:int=0
    high_shift_passes:int=0
    ordinary_calls:int=0


class Tape:
    def __init__(self,meter,bits=()):
        self.meter=meter;self.bits=list(bits);self.head=0
    def read(self):
        need(self.head<len(self.bits),"sequential read bound")
        bit=self.bits[self.head];self.head+=1
        self.meter.reads+=1;self.meter.moves+=1
        return bit
    def write(self,bit):
        need(bit in (0,1) and self.head==len(self.bits),"append bit")
        self.bits.append(bit);self.head+=1
        self.meter.writes+=1;self.meter.moves+=1
    def rewind(self):
        self.meter.moves+=self.head;self.head=0
    def finished(self):need(self.head==len(self.bits),"unconsumed block")
    def erase(self):
        self.rewind()
        for _ in self.bits:self.meter.erases+=1;self.meter.moves+=1;self.head+=1
        self.rewind();self.bits.clear()


def copy_bits(source,target,count):
    for _ in range(count):target.write(source.read())


def cyclic_shift(source,radix,block,fibres,offset):
    need(len(source.bits)==radix*block*fibres,"complete high target fibres")
    meter=source.meter;meter.high_shift_passes+=1
    left,right,out=(Tape(meter) for _ in range(3));source.rewind()
    for prefix in range(fibres):
        cut=offset(prefix)%radix
        copy_bits(source,left,(radix-cut)*block);copy_bits(source,right,cut*block)
    source.finished();left.rewind();right.rewind()
    for prefix in range(fibres):
        cut=offset(prefix)%radix
        copy_bits(right,out,cut*block);copy_bits(left,out,(radix-cut)*block)
    left.finished();right.finished();left.erase();right.erase();source.erase();out.rewind()
    return out


def align_unit_shear(source,source_low,q,width,suffix,omit_carry=False):
    """Right multiply g by [[1,1],[0,1]], with complete high fields."""
    high=q**(width-1);target_low=list(source_low)
    need(high>1,"bounded high-fibre fixture")
    for row in range(2):
        x,y=source_low[2*row:2*row+2]
        low=(x+y)%q;carry=(x+y-low)//q
        target_low[2*row+1]=low
        if omit_carry:carry=0
        target=2*row+1
        block=high**(3-target)*suffix
        fibres=high**target
        source=cyclic_shift(source,high,block,fibres,lambda prefix,c=carry:prefix%high+c)
    return source,tuple(target_low)


def scoped_xor(full,low_types,target_low,source_low,q,width,suffix,omit_carry=False):
    """One same-family ADD: two extracts, one nontrivial header alignment, merge."""
    need(target_low!=source_low,"disjoint low packet requirement")
    high=q**(width-1);fibre_size=high**4*suffix
    need(len(full.bits)==len(low_types)*fibre_size,"whole family extent")
    target,source=Tape(full.meter),Tape(full.meter)
    full.rewind();full.meter.full_family_scans+=1
    for low in low_types:
        for _ in range(fibre_size):
            bit=full.read()
            if low==target_low:target.write(bit)
            elif low==source_low:source.write(bit)
    full.finished();full.rewind();target.rewind();source.rewind()
    need(len(target.bits)==len(source.bits)==fibre_size,"complete selected packets")
    # The target chart is identity. The source needs two ordered high shears.
    source,new_low=align_unit_shear(source,source_low,q,width,suffix,omit_carry)
    need(new_low==target_low,"common invocation low chart")
    replacement=Tape(full.meter)
    for _ in range(fibre_size):replacement.write(target.read()^source.read())
    target.finished();source.finished();target.erase();source.erase();replacement.rewind()
    # Target return chart is identity. Replace only its old low-class block.
    out=Tape(full.meter);full.meter.full_family_scans+=1
    for low in low_types:
        for _ in range(fibre_size):
            old=full.read();out.write(replacement.read() if low==target_low else old)
    full.finished();replacement.finished();replacement.erase();full.rewind();out.rewind()
    need(not source.bits and not target.bits and not replacement.bits,"clean selector work")
    return out


def physical_fibre_check():
    q,width,modulus=3,2,9;low_types=low_matrices(q);high=3
    target_low=(1,0,0,1);sigma=(1,1,0,1)
    source_low=matrix_product(target_low,inverse2(sigma,q),q)
    unused,payload=3,17;suffix=unused*payload
    row_count=len(low_types)*high**4
    raw=[((row*unused+stock)>>bit)&1 for row in range(row_count)
         for stock in range(unused) for bit in range(payload)]
    meter=Meter();out=scoped_xor(Tape(meter,raw),low_types,target_low,source_low,q,width,suffix)
    matrices=[g for low in low_types for g in high_fibre(low,q,width)]
    index={g:i for i,g in enumerate(matrices)};expected=raw[:]
    # Independent full-ring oracle reads the original physical source.
    for d in high_fibre(target_low,q,width):
        target=index[d];source=index[matrix_product(d,inverse2(sigma,modulus),modulus)]
        for i in range(suffix):expected[target*suffix+i]=raw[target*suffix+i]^raw[source*suffix+i]
    need(out.bits==expected,"restricted physical XOR with full-ring owner alignment")
    for low_index,low in enumerate(low_types):
        if low!=target_low:
            start=low_index*81*suffix;end=start+81*suffix
            need(out.bits[start:end]==raw[start:end],"unowned physical fibre preserved")
    need(meter.full_family_scans==2 and meter.high_shift_passes==2 and meter.ordinary_calls==0,"literal selector bill")
    wrong=scoped_xor(Tape(Meter(),raw),low_types,target_low,source_low,q,width,suffix,True)
    need(wrong.bits!=expected,"omitted alignment carry changes physical ADD")
    return {"q":3,"width":2,"low_classes":len(low_types),"full_group_rows":row_count,
            "unused_classes":unused,"payload_bits":len(raw),"changed_low_classes":1,
            "preserved_low_classes":len(low_types)-1,"target_low":target_low,"source_low":source_low,
            "whole_family_scans":2,"ordered_high_shift_passes":2,"ordinary_calls":0,
            "payload_reads":meter.reads,"payload_writes":meter.writes,"head_moves":meter.moves,
            "scratch_erases":meter.erases,"carry_omission_control":"REJECT"}
