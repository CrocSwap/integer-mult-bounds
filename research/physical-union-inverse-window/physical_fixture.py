"""Finite setup and observations; only the online consumer is literal.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys
import time
PACKAGE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def body(tape):
    from session import borrowed_tape
    from words import BLANK
    raw=bytes(borrowed_tape(tape).cells);at=raw.find(bytes((BLANK,)),1)
    if at<0:at=len(raw)
    need(all(v==BLANK for v in raw[at:]),'empty observer backing suffix')
    return raw[1:at]

def snapshot(tapes):
    from session import borrowed_tape
    return tuple((bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in tapes)

def word(raw):
    return sum(v<<i for i,v in enumerate(raw))-(raw[-1]<<len(raw))

def load_header():
    spec=importlib.util.spec_from_file_location('retained_union_header',PACKAGE/'retained/union-header-encoding__header.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
    spec.loader.exec_module(module);return module

class Fixture:
    def __init__(self,window,all_tapes):
        from cardinal_counts import Count
        from records import Tape
        from scratch_pool import ScratchPool
        from session import OuterScope,initialize_marker,erase_marker,sealed_constructors
        from check_support import no_decode
        from boundary_pages import prepare_pages
        from source_window import physical_factors,rounded_pages
        from window_consumer import UnionInverseWindow
        self.window=window;self.all_tapes=all_tapes;self.owner=UnionInverseWindow()
        self.pool=ScratchPool(192);self.scope=OuterScope(self.pool)
        for tape in self.pool.tapes:erase_marker(tape);initialize_marker(tape)
        self.source,self.e_table,self.mask,self.dirty=(Tape() for _ in range(4))
        for v in (1,0,0,1,1,0):self.dirty.append(v)
        self.dirty.rewind()
        self.descriptors=tuple(Count.literal(x) for x in (len(window.E),len(window.J),window.block,window.w,window.P))
        self.pages=[];self.receipts=[];self.codec=load_header();self.shape=();self.header_codec=None
        matrices=[];before=self.meter();started=time.monotonic()
        try:
            with sealed_constructors(),self.scope.installed():
                matrices=physical_factors(window,self.pool)
                for pair in (matrices[:2],matrices[2:]):
                    with no_decode():self.pages.append(prepare_pages(*pair,*self.descriptors[2:],self.pool))
                for matrix in matrices:matrix.close()
                matrices=[]
            for bank,pair in zip(self.pages,((window.shear_lower,window.shear_upper),(window.f_lower,window.f_upper))):
                expected=rounded_pages(*pair,window.block,window.P)
                for tape,values in zip(bank,expected):
                    raw=body(tape);observed=[word(raw[i:i+window.w]) for i in range(0,len(raw),window.w)]
                    need(observed==[int(v*(1<<window.P)) for v in values],
                         'actual physical pages match exact source oracle')
            self.preparation=dict(actions=self.delta(before),seconds=time.monotonic()-started,
                                  page_bits=[len(body(t)) for bank in self.pages for t in bank],
                                  page_sha256=[sha256(body(t)).hexdigest() for bank in self.pages for t in bank])
        except BaseException:
            for matrix in matrices:matrix.close()
            self.close();raise

    def meter(self):
        return tuple(sum(getattr(t.meter,key) for t in self.all_tapes) for key in ('reads','writes','moves'))

    def delta(self,before):return tuple(x-y for x,y in zip(self.meter(),before))

    def shape_for(self,axes):
        from cardinal_counts import Count
        if self.shape and self.header_codec.g==axes:return
        for c in self.shape:c.close()
        self.header_codec=self.codec.Layout(self.window.length,(self.window.E,)*axes)
        self.shape=tuple(Count.literal(x) for x in (axes,self.header_codec.h,self.header_codec.b))
        self.e_table.clear();self.mask.clear()
        for x,flag in zip(self.window.E,self.window.j_mask):
            for v in format(x,'0'+str(self.header_codec.h)+'b'):self.e_table.append(int(v))
            self.mask.append(flag)
        self.e_table.rewind();self.mask.rewind()

    def close(self):
        from session import erase_marker
        if self.owner.pending:self.owner.consume()
        for bank in self.pages:
            for tape in bank:tape.clear()
        self.pages=[]
        for c in (*self.shape,*self.descriptors):c.close()
        self.shape=();self.descriptors=()
        for tape in (self.source,self.e_table,self.mask,self.dirty):tape.clear()
        self.pool.empty()
        for tape in self.pool.tapes:erase_marker(tape)

    def call(self,records,axis,round_index,axes):
        from cardinal_counts import Count
        from ring_words import Signed,write_signed
        from router_metadata import owned
        from check_support import no_decode
        from words import BLANK
        from independent_oracle import window_action
        self.shape_for(axes);layout=self.header_codec;W=self.window
        a=len(W.E);need(records and len(records)%a==0,'complete fixture lines')
        self.source.clear();headers=[];inputs=[]
        for point,pair in records:
            need(sum(map(abs,pair))<=W.radius*(1<<W.P),'actual current-input admission')
            head=layout.retag(layout.encode(point),round_index);headers.append(head);inputs.append(tuple(pair))
            for v in head:self.source.append(int(v))
            for value in pair:
                need(-(1<<(W.w-1))<=value<1<<(W.w-1),'fixture signed word fits')
                with owned(Signed(Count.literal(abs(value)),value<0)) as (encoded,):
                    write_signed(encoded,self.source,self.descriptors[3])
        self.source.rewind()
        with owned(Count.literal(axis),Count.literal(round_index)) as (f,r):
            metadata=(*self.shape,f,r,*self.descriptors)
            ports=(self.source,self.e_table,self.mask,*self.pages[0],*self.pages[1],
                   *(x.tape for x in metadata),self.dirty)
            saved=snapshot(ports);before=self.meter();leaves=self.owner.child.kernel.leaves
            started=time.monotonic()
            with no_decode():out=self.owner.run(self.source,self.e_table,self.mask,*self.pages,*metadata)
            run_actions=self.delta(before);raw=[]
            while out.read()!=BLANK:
                need(out.read() in (0,1),'returned union bits');raw.append(out.read());out.step(1)
            returned=[];record_bits=layout.width+2*W.w
            need(len(raw)==len(records)*record_bits,'exact union output extent')
            for i,point_pair in enumerate(records):
                start=i*record_bits
                need(''.join(map(str,raw[start:start+layout.width]))==headers[i],
                     'exact retained header bit return')
                first=start+layout.width
                returned.append((point_pair[0],(word(raw[first:first+W.w]),word(raw[first+W.w:first+2*W.w]))))
            consume_before=self.meter()
            with no_decode():self.owner.consume()
            consume_actions=self.delta(consume_before)
            need(snapshot(ports)==saved,'all borrowed union bodies and origins preserved')
            need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in self.owner.forbidden()),
                 'all union owned roles and retained history erased')
            expected=[];max_error=Q()
            for start in range(0,len(records),a):
                current=inputs[start:start+a]
                predicted=window_action(W,current);expected.extend(predicted)
                exact=W.exact_action([[Q(v,1<<W.P) for v in pair] for pair in current])
                actual=[pair for _,pair in returned[start:start+a]]
                max_error=max(max_error,max(sum(abs(Q(v,1<<W.P)-x) for v,x in zip(pair,row))
                                           for pair,row in zip(actual,exact)))
            need([pair for _,pair in returned]==expected,'independent completed-block return words')
            need(max_error<=W.total_error,'actual current-input original-reference first-window error')
            for old,new,flag in zip(inputs,[p for _,p in returned],W.j_mask*(len(records)//a)):
                need(flag or old==new,'exact untouched E minus J component words')
            expected_calls=2*(2*((a+W.block-1)//W.block)-1)+2*(2*((len(W.J)+W.block-1)//W.block)-1)
            batches=(2*len(records)//a+W.block-1)//W.block
            scalar=self.owner.child.kernel.leaves-leaves
            need(scalar==batches*expected_calls*7**(W.block.bit_length()-1),'complete union scalar invoice')
            receipt=dict(axis=axis,round=round_index,records=len(records),lines=len(records)//a,
                         batches=batches,scalar_products=scalar,run_actions=run_actions,
                         consume_actions=consume_actions,seconds=time.monotonic()-started,
                         exact_reference_error=str(max_error),output_sha256=sha256(bytes(raw)).hexdigest())
            self.receipts.append(receipt)
            return returned
