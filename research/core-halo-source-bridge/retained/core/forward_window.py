"""Complete current E-lines through the unchanged #6909 forward action.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Packing/header validation is inherited from #6908; routing from Round1.
"""
from cardinal_counts import Count
from compact_counts import copy_bits
from encoded import compare,subtract
from records import Tape
from router_metadata import indices,owned
from scratch_pool import ScratchPool
from session import OuterScope,erase_marker
from words import BLANK,need
from window_consumer import UnionInverseWindow
from window_tapes import line,zeros,transpose
from banded_action import BandedAction
from union_bits import PART_END,BLOCK_END,bit,symbol,big,put_big,skip_bits
from union_catalogue import page_extents

class UnionForwardWindow(UnionInverseWindow):
    def __init__(self):
        self.child=BandedAction();self.pool=ScratchPool(128);self.scope=OuterScope(self.pool)
        (self.archive,self.real,self.imaginary,self.columns,self.matrix,
         self.shear_result,self.selected_rhs,self.merged,self.returned,self.output)=(Tape() for _ in range(10))
        self.closed=True;self.pending=False;self.calls=self.batches=self.lines=0
        for tape in (*self.pool.tapes,*self.buffers()):erase_marker(tape)

    def batch(self,source,e_table,j_mask,pages,reserved,metadata,e_padded,j_padded,header_bits):
        axes,h,tb,axis,round_index,length,selected,block,width,precision=metadata
        need(all(t.read()==BLANK for t in reserved),'empty reserved forward page banks')
        with owned(Count.literal(0),Count.literal(0),Count.literal(2),
                   Count.product(length,width),subtract(e_padded,length)) as (columns,lines_seen,two,data_bits,pad_rows):
            with owned(Count.product(pad_rows,width),Count.product(e_padded,width)) as (pad_bits,column_bits):
                while compare(columns,block)<0 and source.read()!=BLANK:
                    line(source,self.archive,self.real,self.imaginary,e_table,j_mask,
                         axes,h,tb,axis,round_index,length,selected,width,self.pool)
                    for component in (self.real,self.imaginary):
                        copy_bits(component,self.columns,data_bits)
                        need(component.read()==BLANK,'complete forward component column')
                        zeros(self.columns,pad_bits);component.clear()
                    columns.add(two);lines_seen.increment();self.lines+=1
                need(not lines_seen.zero(),'nonempty complete forward batch')
                while compare(columns,block)<0:zeros(self.columns,column_bits);columns.increment()
            self.columns.rewind();transpose(self.columns,self.matrix,e_padded,block,width,self.pool)
            with self.scope.suspended():
                returned=self.child.run(self.matrix,pages,length,block,block,width,precision)
            try:
                with owned(Count.product(e_padded,block)) as (entries,):
                    with owned(Count.product(entries,width)) as (bits,):copy_bits(returned,self.merged,bits)
                need(returned.read()==BLANK,'complete actual banded-action return')
            finally:
                if self.child.pending:self.child.consume()
            self.merged.rewind()
            transpose(self.merged,self.returned,e_padded,block,width,self.pool,inverse=True)
            self.return_batch(lines_seen,length,e_padded,width,header_bits)
        for tape in self.buffers():
            if tape is not self.output:tape.clear()
        self.batches+=1

def axis_body(bank,a,n,block,h,width,e_table,mask=None,pages=None):
    """Same E/J metadata; four pages for the literal 2a-row lift, four empty."""
    with owned(Count.literal(0),Count.literal(0)) as (seen,previous):
        for rank in indices(a):
            with owned(big(bank,h)) as (coordinate,):
                need(rank.zero() or compare(coordinate,previous)>0,'strict forward E coordinates')
                with owned(subtract(coordinate,previous)) as (delta,):previous.add(delta)
                put_big(coordinate,e_table,h)
        symbol(bank,PART_END)
        for _ in indices(a):
            flag=bit(bank)
            if mask is not None:mask.append(flag)
            if flag:seen.increment()
        symbol(bank,PART_END);need(compare(seen,n)==0,'forward original J mask cardinality')
    e_table.rewind()
    if mask is not None:mask.rewind()
    with owned(Count(a),Count.literal(0)) as (twice,zero):
        twice.multiply_small(2)
        with owned(*page_extents(twice,block,width)) as (diagonal,coupling):
            for role,extent in enumerate((diagonal,coupling,diagonal,coupling,zero,zero,zero,zero)):
                if pages is None:skip_bits(bank,extent)
                else:copy_bits(bank,pages[role],extent);pages[role].rewind()
                symbol(bank,PART_END)
    symbol(bank,BLOCK_END)

_owner_type=None

def owner_class():
    """Fresh namespaces preserve router bodies, adapting only page extents."""
    global _owner_type
    if _owner_type is not None:return _owner_type
    from join_sources import load,ROUTER
    catalogue=load('_join_forward_catalogue',ROUTER/'union_catalogue.py')
    catalogue.axis_body=axis_body
    router=load('_join_forward_router',ROUTER/'physical_router.py')
    router.axis_body=axis_body;router.build_membership=catalogue.build_membership
    _owner_type=router.UnionRouter
    return _owner_type
