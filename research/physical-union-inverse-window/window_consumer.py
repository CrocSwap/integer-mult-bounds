"""First narrow inverse union window on prepared complete E-line tapes.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Header emission/global union routing are preparation/model boundaries.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count,positive
from compact_counts import copy_bits
from encoded import compare,subtract
from records import Tape
from router_metadata import indices,owned
from scratch_pool import ScratchPool
from session import (OuterScope,borrowed_count,borrowed_tape,erase_marker,
                     initialize_marker,sealed_constructors)
from words import BLANK,need
from boundary_pages import ceiling_division
from fast_boundary import FastBoundaryPages,origin,dyadic
from window_tapes import (bit,zeros,zero_field,line,transpose,select_rows,merge_rows)


class UnionInverseWindow:
    def __init__(self):
        self.child=FastBoundaryPages()
        self.pool=ScratchPool(128);self.scope=OuterScope(self.pool)
        (self.archive,self.real,self.imaginary,self.columns,self.matrix,
         self.shear_result,self.selected_rhs,self.merged,self.returned,self.output)=(Tape() for _ in range(10))
        self.closed=True;self.pending=False
        self.calls=self.batches=self.lines=0
        for tape in (*self.pool.tapes,*self.buffers()):erase_marker(tape)

    def buffers(self):
        return (self.archive,self.real,self.imaginary,self.columns,self.matrix,
                self.shear_result,self.selected_rhs,self.merged,self.returned,self.output)

    def forbidden(self):
        return (*self.pool.tapes,*self.buffers(),*self.child.forbidden())

    def idle(self):
        need(self.closed and not self.pending and not self.pool.live and self.output.read()==BLANK,
             'consume prior union-window return')
        self.child.idle()
        need(self.child.closed and not self.child.pending and not self.child.pool.live,
             'consumed union boundary child')

    def consume(self):
        need(self.closed and self.pending,'one pending union-window return')
        self.output.clear();erase_marker(self.output);self.pending=False;self.idle()

    def apply_child(self,pages,rhs,length,block,width,precision):
        with self.scope.suspended():
            return self.child.run(*pages,rhs,length,block,block,width,precision)

    def return_batch(self,lines,length,padded,width,header_bits):
        self.archive.rewind();self.returned.rewind()
        with owned(Count.product(length,width),subtract(padded,length)) as (data_bits,pad_rows):
            with owned(Count.product(pad_rows,width),Count(width)) as (pad_bits,pair_bits):
                pair_bits.multiply_small(2)
                for _ in indices(lines):
                    copy_bits(self.returned,self.real,data_bits);zero_field(self.returned,pad_bits)
                    copy_bits(self.returned,self.imaginary,data_bits);zero_field(self.returned,pad_bits)
                    self.real.rewind();self.imaginary.rewind()
                    for _ in indices(length):
                        copy_bits(self.archive,self.output,header_bits)
                        for _ in indices(pair_bits):bit(self.archive)
                        copy_bits(self.real,self.output,width);copy_bits(self.imaginary,self.output,width)
                    need(self.real.read()==self.imaginary.read()==BLANK,'complete union returned line')
                    self.real.clear();self.imaginary.clear()
                while self.returned.read() in (0,1):need(bit(self.returned)==0,'zero inactive returned RHS column')
                need(self.returned.read()==self.archive.read()==BLANK,'complete union batch return')

    def batch(self,source,e_table,j_mask,shear_pages,schur_pages,metadata,e_padded,j_padded,header_bits):
        axes,h,tb,axis,round_index,length,selected,block,width,precision=metadata
        with owned(Count.literal(0),Count.literal(0),Count.literal(2),
                   Count.product(length,width),subtract(e_padded,length)) as (columns,lines_seen,two,data_bits,pad_rows):
            with owned(Count.product(pad_rows,width),Count.product(e_padded,width)) as (pad_bits,column_bits):
                while compare(columns,block)<0 and source.read()!=BLANK:
                    line(source,self.archive,self.real,self.imaginary,e_table,j_mask,
                         axes,h,tb,axis,round_index,length,selected,width,self.pool)
                    for component in (self.real,self.imaginary):
                        copy_bits(component,self.columns,data_bits)
                        need(component.read()==BLANK,'complete union component column')
                        zeros(self.columns,pad_bits);component.clear()
                    columns.add(two);lines_seen.increment();self.lines+=1
                need(not lines_seen.zero(),'nonempty union matrix batch')
                while compare(columns,block)<0:zeros(self.columns,column_bits);columns.increment()
            self.columns.rewind()
            transpose(self.columns,self.matrix,e_padded,block,width,self.pool)
            returned=self.apply_child(shear_pages,self.matrix,length,block,width,precision)
            try:
                with owned(Count.product(e_padded,block)) as (entries,):
                    with owned(Count.product(entries,width)) as (bits,):copy_bits(returned,self.shear_result,bits)
                need(returned.read()==BLANK,'complete nilpotent shear child return')
            finally:
                if self.child.pending:self.child.consume()
            self.shear_result.rewind()
            select_rows(self.shear_result,self.selected_rhs,j_mask,length,e_padded,j_padded,block,width)
            returned=self.apply_child(schur_pages,self.selected_rhs,selected,block,width,precision)
            try:
                merge_rows(self.shear_result,returned,self.merged,j_mask,length,e_padded,j_padded,block,width)
            finally:
                if self.child.pending:self.child.consume()
            transpose(self.merged,self.returned,e_padded,block,width,self.pool,inverse=True)
            self.return_batch(lines_seen,length,e_padded,width,header_bits)
        for tape in self.buffers():
            if tape is not self.output:tape.clear()
        self.batches+=1

    def run(self,source,e_table,j_mask,shear_pages,schur_pages,
            axes,h,tag_bits,axis,round_index,length,selected,block,width,precision):
        need(len(shear_pages)==len(schur_pages)==4,'four pages per union factor')
        source,e_table,j_mask=(borrowed_tape(t) for t in (source,e_table,j_mask))
        shear_pages=tuple(borrowed_tape(t) for t in shear_pages)
        schur_pages=tuple(borrowed_tape(t) for t in schur_pages)
        metadata=tuple(borrowed_count(c) for c in (axes,h,tag_bits,axis,round_index,length,selected,block,width,precision))
        axes,h,tag_bits,axis,round_index,length,selected,block,width,precision=metadata
        sources=(source,e_table,j_mask,*shear_pages,*schur_pages);forbidden=self.forbidden()
        need(len(set(sources))==len(sources) and all(t not in forbidden for t in sources)
             and all(c.tape not in forbidden and c.tape not in sources for c in metadata),
             'external distinct union-window sources and descriptors')
        self.idle()
        ports=(*sources,*(c.tape for c in metadata))
        for tape in ports:origin(tape)
        for value in (axes,h,tag_bits,length,selected,block,width):positive(value)
        need(compare(axis,axes)<0 and compare(round_index,axes)<0,'union axis and round range')
        need(compare(selected,length)<=0 and compare(precision,width)<0,'union mask and precision range')
        dyadic(block)
        for tape in (*self.pool.tapes,*self.buffers()):initialize_marker(tape)
        self.closed=False;succeeded=False
        try:
            with sealed_constructors(),self.scope.installed():
                with owned(Count.literal(2),ceiling_division(length,block),
                           ceiling_division(selected,block),Count.product(axes,h),Count(tag_bits)) as (two,eb,jb,header_bits,tags):
                    need(compare(block,two)>=0,'union complex batch block at least two')
                    header_bits.multiply_small(2);header_bits.add(axes)
                    tags.multiply_small(2);header_bits.add(tags);header_bits.add(two)
                    with owned(Count.product(eb,block),Count.product(jb,block)) as (e_padded,j_padded):
                        while source.read()!=BLANK:
                            self.batch(source,e_table,j_mask,shear_pages,schur_pages,metadata,
                                       e_padded,j_padded,header_bits)
                    self.child.idle();self.calls+=1;succeeded=self.pending=True
        finally:
            if self.child.pending:self.child.consume()
            for tape in ports:tape.rewind()
            for tape in self.buffers():
                if tape is not self.output:tape.clear()
            self.pool.empty()
            for tape in (*self.pool.tapes,*(t for t in self.buffers() if t is not self.output)):erase_marker(tape)
            self.output.rewind()
            if not succeeded:self.output.clear();erase_marker(self.output);self.pending=False
            self.closed=True
        return self.output
