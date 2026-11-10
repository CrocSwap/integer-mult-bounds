"""Paid T-record clock for the dimension-changing native return.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count,positive
from records import Tape
from router_metadata import indices
from scratch_pool import ScratchPool
from session import OuterScope,initialize_marker,erase_marker,sealed_constructors,borrowed_count,borrowed_tape
from words import BLANK,need

class ExpansionReturn:
    """Admitted return owner, not a complete encoded expansion controller.

    ``records`` is a borrowed positive encoded Count prepared by the caller.
    The host q/J scalars describe input-independent format templates whose
    O(q+J) construction is charged separately, as is the O(log T) Count copy.
    Source and native work owners must be distinct; run checks every native
    alias available through this owner's ports before entering the codec.
    """
    def __init__(self,state,records,q,normalizer_bits):
        records=borrowed_count(records);positive(records)
        self.B=state.B;self.borrowed_volume_tape=records.tape;self.volume=Count(records)
        self.codec=state.codec.Codec(state.B,Tape,BLANK,initialize_marker,erase_marker,
                                    state.codec.Format(q+2,q,q+2,q,normalizer_bits))
        self.clock=state.B.Tape('owned full target record clock')
        self.output=state.B.Tape('protected expanded common-grid return')
        self.pool=ScratchPool(32);self.scope=OuterScope(self.pool)
        self.closed=True;self.pending=False;self.finished=False;self.calls=0
        for tape in self.pool.tapes:erase_marker(tape)

    def prepare_clock(self):
        B=self.B;B.clear(self.clock)
        for _ in indices(self.volume):
            for _ in (0,1):
                B.append(self.clock,'0');B.home(self.codec.magnitude_clock)
                while self.codec.magnitude_clock.read()=='1':
                    B.append(self.clock,'0');self.codec.magnitude_clock.move(1)
            B.append(self.clock,'#')
        B.home(self.codec.magnitude_clock);B.home(self.clock)

    def run(self,native):
        native=borrowed_tape(native)
        need(self.closed and not self.pending and not self.finished,'consume protected expansion return')
        forbidden=(self.codec.input,self.volume.tape,self.borrowed_volume_tape,*self.pool.tapes)
        need(native not in forbidden and isinstance(native,Tape),'disjoint external native field and metadata')
        self.closed=False;succeeded=False
        for tape in self.pool.tapes:initialize_marker(tape)
        try:
            with sealed_constructors(),self.scope.installed():
                try:
                    self.prepare_clock()
                    self.codec.prepare_input(self.clock)
                    result=self.codec.prepare_return(native,self.clock)
                    self.B.clone(result,self.output);self.B.home(self.output)
                    self.pending=succeeded=True;self.calls+=1
                finally:
                    self.codec.abort();self.B.clear(self.clock);self.B.home(self.clock)
                    self.pool.empty()
        finally:
            for tape in self.pool.tapes:erase_marker(tape)
            if not succeeded:self.B.clear(self.output);self.B.home(self.output)
            self.closed=True
        return self.output

    def consume(self):
        need(self.closed and self.pending,'one protected expansion return')
        self.B.clear(self.output);self.B.home(self.output);self.pending=False

    def close(self):
        need(self.closed and not self.pending and not self.finished,'quiescent expansion adapter')
        self.finished=True
        self.volume.close();self.codec.abort()
        for tape in self.codec.templates:self.B.clear(tape);self.B.home(tape)
