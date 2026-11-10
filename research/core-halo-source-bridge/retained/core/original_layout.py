"""Two actual global support routes around the complete packed five-stage word.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count
from compact_counts import append_bits
from encoded import compare
from records import Tape
from router_metadata import owned
from session import (borrowed_count,borrowed_tape,erase_marker,sealed_constructors)
from words import BLANK,need
from fast_boundary import origin
from global_h_boundary import GlobalBoundary
from physical_engine import private_tapes
from physical_controls import emit_unsigned
from physical_join import CompleteCore

class OriginalCore(GlobalBoundary):
    """One owner; the same quiescent composed root serves both route boundaries."""
    def __init__(self,root,observe=None):
        super().__init__(root)
        self.core=CompleteCore(root,observe=observe)
        self.pending=False
        self.private=private_tapes(self)

    def idle(self):
        super().idle()
        if hasattr(self,'core'):self.core.idle()

    def forbidden(self):return self.private

    def consume(self):
        need(self.closed and self.pending,'protected original-coordinate Core return')
        self.output.clear();erase_marker(self.output);self.pending=False;self.idle()

    def run(self,payload,forward,inverse,route_parameters,
            inverse_code,forward_code,inverse_banks,forward_banks,keys,
            inverse_parameters,forward_parameters,union_parameters):
        data=tuple(borrowed_tape(t) for t in (payload,forward,inverse,inverse_code,
                                            forward_code,inverse_banks,forward_banks,keys))
        payload,forward,inverse,inverse_code,forward_code,inverse_banks,forward_banks,keys=data
        rp=tuple(borrowed_count(x) for x in route_parameters)
        ip=tuple(borrowed_count(x) for x in inverse_parameters)
        fp=tuple(borrowed_count(x) for x in forward_parameters)
        up=tuple(borrowed_count(x) for x in union_parameters)
        need(len(rp)==4 and len(ip)==len(fp)==16 and len(up)==6,'complete original route/control ports')
        ports=(*data,*(x.tape for x in (*rp,*ip,*fp,*up)))
        need(len(set(data))==len(data) and all(t not in self.private for t in ports)
             and all(x.tape not in data for x in (*rp,*ip,*fp,*up)),
             'external original-coordinate source/control ports')
        need(not self.pending,'consume previous original-coordinate return')
        for t in ports:origin(t)
        self.rearm();succeeded=False
        try:
            with sealed_constructors(),self.scope.installed():
                n,precision,support,pw=rp
                need(compare(n,ip[0])==compare(n,fp[0])==0,'same complete original and packed field')
                with owned(Count.literal(1)) as (one,):
                    self.current=self.pool.acquire();append_bits(payload,self.current)
                    payload.rewind();self.current.rewind()
                    self.gather(forward,n,precision,support,pw,up[4],one,one)
                    with self.scope.suspended():
                        returned=self.core.run(self.current,inverse_code,forward_code,
                            inverse_banks,forward_banks,keys,ip,fp,up)
                    following=self.pool.acquire()
                    try:append_bits(returned,following)
                    finally:
                        if self.core.pending:self.core.consume()
                    self.current.clear();self.current=following;self.current.rewind()
                    self.gather(inverse,n,precision,support,pw,up[4],one,one)
                    append_bits(self.current,self.output)
                self.current.clear();self.current=None;self.pool.empty()
                succeeded=self.pending=True
        finally:
            if self.core.pending:self.core.consume()
            if self.current is not None:self.current.clear();self.current=None
            self.pool.empty()
            for t in ports:t.rewind()
            for t in self.pool.tapes:erase_marker(t)
            self.output.rewind()
            if not succeeded:self.output.clear();erase_marker(self.output);self.pending=False
            self.closed=True
        return self.output

class PreparedRoutes:
    def __init__(self,layout,family,width):
        """Bind original starts and source-axis order before emitting route bits."""
        need(len(family)==layout.labels and all(len(row)==layout.g for row in family),
             'all original coarse labels and selected axes')
        for c,row in enumerate(family):
            starts=layout.core_starts(c)
            for a,p in enumerate(reversed(row)):
                need(p.first==starts[a] and p.size==layout.size
                     and p.reference.target_size==1<<layout.lengths[layout.selected[a]],
                     'same original Reference coordinates at dense/sparse axis reversal')
                p.validate()
        self.layout_seal=layout.record();self.forward,self.inverse=Tape(),Tape()
        pw=max(1,(layout.n-1).bit_length())
        for tape,mapping in ((self.forward,layout.gather),(self.inverse,layout.inverse)):
            for old,new in sorted(mapping.items()):
                emit_unsigned(tape,old,pw);emit_unsigned(tape,new,pw)
            tape.rewind()
        self.parameters=tuple(Count.literal(x) for x in
            (layout.n,width+layout.g,len(layout.gather),pw))

    def close(self):
        for x in self.parameters:x.close();erase_marker(x.tape)
        for t in (self.forward,self.inverse):t.clear();erase_marker(t)
