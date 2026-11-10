"""Three global dense cohorts and two complete context-wise sparse windows.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count,positive
from compact_counts import copy_bits,power_two
from encoded import compare,subtract
from records import Tape
from router_metadata import indices,owned
from scratch_pool import ScratchPool
from session import (OuterScope,borrowed_count,borrowed_tape,erase_marker,
                     initialize_marker,sealed_constructors)
from words import BLANK,RIGHT,need
from physical_engine import FullPhysical
from word_product import WordProduct
from physical_router import UnionRouter
from forward_window import UnionForwardWindow,owner_class
from union_bits import PART_END,BLOCK_START,BLOCK_END,bit,symbol,copy_until,same_context
from fast_boundary import origin

FRAME_END=8

def convert_word(source,target,before,after):
    """Exact little-endian two's-complement sign extension or checked shrink."""
    with owned(Count.literal(1)) as (one,):
        if compare(before,after)<=0:
            with owned(subtract(before,one),subtract(after,before)) as (low,high):
                copy_bits(source,target,low);sign=bit(source,target)
                for _ in indices(high):target.append(sign)
        else:
            with owned(subtract(after,one),subtract(before,after)) as (low,high):
                copy_bits(source,target,low);sign=bit(source,target)
                for _ in indices(high):need(bit(source)==sign,'exact signed carrier shrink')

def convert_field(source,target,before,after):
    positive(before);positive(after)
    while source.read()!=BLANK:
        for _ in (0,1):convert_word(source,target,before,after)

def increment_address(address):
    """Binary carry without decoding; true only on the final all-ones carry."""
    address.rewind()
    while address.read()==1:address.write(0);address.step(1)
    if address.read()==BLANK:address.rewind();return True
    need(address.read()==0,'literal local address digit')
    address.write(1);address.rewind();return False

def copy_context_payload(source,target,address,axes,bits,width):
    """Copy exactly 2^(g*m) complex records with a raw gm-bit odometer."""
    need(address.read()==BLANK,'empty local raw address role')
    for _ in indices(axes):
        for _ in indices(bits):address.append(0)
    address.rewind()
    try:
        while True:
            copy_bits(source,target,width);copy_bits(source,target,width)
            if increment_address(address):break
    finally:address.clear()

def copy_catalogue_frame(source,target):
    """End-delimited source-bank transport; no long bank-length Count."""
    while source.read()!=FRAME_END:
        value=source.read()
        need(value in (0,1,RIGHT,PART_END,BLOCK_START,BLOCK_END),'complete source catalogue frame')
        target.append(value);source.step(1)
    source.step(1);target.rewind()

class CompleteCore:
    def __init__(self,root,observe=None,dense_leaf_bits=64):
        self.dense=FullPhysical(root,word=WordProduct(leaf_bits=dense_leaf_bits))
        self.inverse=UnionRouter();self.forward=owner_class()(UnionForwardWindow())
        self.pool=ScratchPool(128);self.scope=OuterScope(self.pool)
        self.first,self.second,self.local,self.bank,self.address,self.output=(Tape() for _ in range(6))
        self.closed=True;self.pending=False;self.observe=observe
        for tape in (*self.pool.tapes,*self.buffers()):erase_marker(tape)

    def buffers(self):return self.first,self.second,self.local,self.bank,self.address,self.output

    def forbidden(self):
        return (*self.pool.tapes,*self.buffers(),*self.dense.private,
                *self.inverse.forbidden(),*self.forward.forbidden())

    def idle(self):
        need(self.closed and not self.pending and not self.pool.live and self.output.read()==BLANK,
             'consume protected complete Core return')
        self.dense.idle();self.inverse.idle();self.forward.idle()
        need(self.dense.closed and self.dense.current is None and self.dense.output.read()==BLANK,
             'consumed global dense child')

    def consume(self):
        need(self.closed and self.pending,'one protected Core return')
        self.output.clear();erase_marker(self.output);self.pending=False;self.idle()

    def note(self,stage,phase,tape):
        if self.observe is not None:self.observe(stage,phase,tape)

    def dense_stage(self,current,other,code,parameters,width,stage):
        self.note(stage,'input',current)
        convert_field(current,other,width,parameters[10])
        current.clear();other.rewind()
        with self.scope.suspended():returned=self.dense.run(other,code,*parameters)
        try:
            convert_field(returned,current,parameters[5],width)
            need(returned.read()==BLANK,'complete global dense return conversion')
        finally:returned.clear();erase_marker(returned)
        other.clear();current.rewind();self.note(stage,'output',current)
        return current,other

    def sparse_stage(self,current,other,catalogues,keys,metadata,child,stage):
        axes,side,h,tags,width,precision=metadata
        self.note(stage,'input',current);catalogues.rewind();keys.rewind()
        while catalogues.read()!=BLANK:
            copy_catalogue_frame(catalogues,self.bank)
            while keys.read() in (0,1):bit(keys,self.local)
            symbol(keys,PART_END);self.local.append(PART_END)
            copy_context_payload(current,self.local,self.address,axes,h,width)
            self.local.rewind()
            with self.scope.suspended():returned=child.run(self.local,self.bank,*metadata)
            try:
                self.local.rewind();same_context(returned,self.local)
                copy_context_payload(returned,other,self.address,axes,h,width)
                need(returned.read()==BLANK,'exact complete context return')
            finally:
                if child.pending:child.consume()
            self.local.clear();self.bank.clear()
        need(current.read()==keys.read()==BLANK,'complete K-context packed field and key inventory')
        current.clear();other.rewind();catalogues.rewind();keys.rewind()
        self.note(stage,'output',other)
        return other,current

    def run(self,payload,inverse_code,forward_code,inverse_banks,forward_banks,keys,
            inverse_parameters,forward_parameters,union_parameters):
        """All parameters are immutable prepared ports, not payload callbacks."""
        data=tuple(borrowed_tape(t) for t in
                   (payload,inverse_code,forward_code,inverse_banks,forward_banks,keys))
        payload,inverse_code,forward_code,inverse_banks,forward_banks,keys=data
        ip=tuple(borrowed_count(x) for x in inverse_parameters)
        fp=tuple(borrowed_count(x) for x in forward_parameters)
        up=tuple(borrowed_count(x) for x in union_parameters)
        need(len(ip)==len(fp)==16 and len(up)==6,'complete five-stage metadata inventory')
        ports=(*data,*(x.tape for x in (*ip,*fp,*up)));private=self.forbidden()
        need(len(set(data))==len(data) and all(t not in private for t in ports)
             and all(x.tape not in data for x in (*ip,*fp,*up)),
             'external distinct Core source/control/metadata ports')
        self.idle()
        for tape in ports:origin(tape)
        for tape in (*self.pool.tapes,*self.buffers()):initialize_marker(tape)
        self.closed=False;succeeded=False
        try:
            with sealed_constructors(),self.scope.installed():
                axes,side,h,tags,width,precision=up
                for i in (0,1,2,3):need(compare(ip[i],fp[i])==0,'same complete global dense geometry')
                need(compare(ip[3],axes)==0 and compare(ip[2],h)==0,'same dense/sparse axis geometry')
                with owned(power_two(h)) as (expected_side,):
                    need(compare(expected_side,side)==0,'complete dyadic sparse context side')
                for parameters in (ip,fp):
                    need(compare(parameters[4],precision)==compare(parameters[9],precision)==0,
                         'one common grid at every dense/sparse boundary')
                copy_until(payload,self.first);payload.rewind();self.first.rewind()
                current,other=self.first,self.second
                current,other=self.dense_stage(current,other,inverse_code,ip,width,'D_Ainv_1')
                current,other=self.sparse_stage(current,other,inverse_banks,keys,up,self.inverse,'T1')
                current,other=self.dense_stage(current,other,forward_code,fp,width,'D_A')
                current,other=self.sparse_stage(current,other,forward_banks,keys,up,self.forward,'T2')
                current,other=self.dense_stage(current,other,inverse_code,ip,width,'D_Ainv_2')
                copy_until(current,self.output);current.clear()
                self.dense.idle();self.inverse.idle();self.forward.idle()
                succeeded=self.pending=True
        finally:
            for child in (self.inverse,self.forward):
                if child.pending:child.consume()
            if self.dense.closed and self.dense.output.read()!=BLANK:
                self.dense.output.clear();erase_marker(self.dense.output)
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
