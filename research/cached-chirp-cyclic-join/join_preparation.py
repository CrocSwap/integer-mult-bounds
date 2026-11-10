"""Paid, input-independent phase/shape/grid preparation for the exact seam.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass
from functools import reduce
from operator import mul
from chirp_tables import prepare
from chirp_tapes import EncodedChirpTables
from cardinal_counts import Count
from records import Tape
from session import erase_marker
from words import need

def ceil_log2(x):return (x-1).bit_length()

@dataclass(frozen=True)
class Allocation:
    q:int
    f:int
    W:int
    D:int
    A:int
    M:int
    volume:int
    chi:int
    coefficient:int

def allocate(radices,slopes,q,chi):
    need(type(q) is int and type(chi) is int and chi>=0 and q>=chi+2,'funded external middle grid')
    need(len(radices)==len(slopes)>=2,'at least two source axes')
    r=radices[0]
    need(type(r) is int and r>=4 and not r&(r-1),'largest even dyadic polynomial axis')
    need(all(type(t) is int and t in (r//2,r) for t in radices),'canonical two-scale axis family')
    need(all(type(s) is int and 0<s<t and s%2 for s,t in zip(slopes,radices)),'original odd source slopes')
    D=len(radices);volume=reduce(mul,radices,1);M=volume//r;A=M.bit_length()-1
    C=8*M+9*D+18
    f=max(q,16,A+13,chi+1+ceil_log2(C),ceil_log2(6*D))
    return Allocation(q,f,f+3,D,A,M,volume,chi,C)

class Prepared:
    """Immutable certified source specification and borrowed encoded ports.

    Host preparation is charged separately; online code never decodes these
    Count fields or uses the tuples to control payload operations.
    """
    def __init__(self,radices,slopes,q,chi,oracle):
        self.radices=tuple(radices);self.slopes=tuple(slopes)
        self.plan=allocate(self.radices,self.slopes,q,chi)
        p=self.plan
        self.bundle=prepare(self.radices,self.slopes,1,0,oracle=oracle,incoming_precision=p.f)
        need((self.bundle.plan.f,self.bundle.plan.W)==(p.f,p.W),'unchanged cached source allocation')
        self.tables=EncodedChirpTables(self.radices,self.bundle.tables,p.W,p.f)
        self.flags=Tape()
        ell=self.radices[0].bit_length()-1
        # Cached shape is fastest first; Cyclic flags are slowest first.
        for t in reversed(self.radices[1:]):self.flags.append(int(t==self.radices[0]))
        self.flags.rewind()
        self.axes=Count.literal(p.D-1);self.ell=Count.literal(ell)
        self.rows=Count.literal(1);self.volume=Count.literal(p.volume)
        self.cyclic_width=Count.literal(p.f+2)
        self.closed=False

    def ports(self):
        return (self.tables.shape,self.tables.tables,self.tables.width.tape,
                self.tables.precision.tape,self.flags,self.axes.tape,self.ell.tape,
                self.rows.tape,self.volume.tape,self.cyclic_width.tape)

    def close(self):
        need(not self.closed,'one prepared source close')
        self.tables.close()
        for value in (self.axes,self.ell,self.rows,self.volume,self.cyclic_width):value.close()
        self.flags.clear();erase_marker(self.flags);self.closed=True
