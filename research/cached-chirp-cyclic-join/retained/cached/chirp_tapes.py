"""Separately paid serialization for cached chirp source tables and shape.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Host integer loops occur only in input-independent preparation/fixture loading.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count
from chirp_consumer import AXIS_END,PAGE_BEGIN,PAGE_END
from records import Tape
from ring_words import Signed,write_signed
from router_metadata import owned
from session import erase_marker
from words import need


def emit_pairs(values,tape,width):
    for pair in values:
        need(len(pair)==2,'two prepared complex components')
        for value in pair:
            need(type(value) is int,'prepared integer component')
            with owned(Signed(Count.literal(abs(value)),value<0)) as (word,):
                write_signed(word,tape,width)


class EncodedChirpTables:
    def __init__(self,radices,values,width,precision):
        self.width=self.precision=self.shape=self.tables=None
        try:
            need(type(width) is int and type(precision) is int and 0<=precision<=width-2,
                 'prepared chirp signed grid')
            need(len(radices)==len(values)>0,'one table per prepared axis')
            need(all(type(t) is int and t>=2 and not t&(t-1) for t in radices),
                 'prepared even dyadic radices')
            need(radices[0]==max(radices),'prepared axis0 largest')
            self.width=Count.literal(width);self.precision=Count.literal(precision)
            self.shape,self.tables=Tape(),Tape()
            unit=1<<precision
            for radix,table in zip(radices,values):
                need(len(table)==radix and table[0]==(unit,0),'complete prepared chirp table')
                need(all(a*a+b*b<=unit*unit for a,b in table),'prepared unit-disk table')
                for _ in range(radix.bit_length()-1):self.shape.append(0)
                self.shape.append(AXIS_END);self.tables.append(PAGE_BEGIN)
                emit_pairs(table,self.tables,self.width);self.tables.append(PAGE_END)
            self.shape.rewind();self.tables.rewind()
        except BaseException:
            self.close();raise

    def ports(self):
        return self.shape,self.tables,self.width.tape,self.precision.tape

    def close(self):
        for name in ('shape','tables'):
            tape=getattr(self,name)
            if tape is not None:tape.clear();erase_marker(tape);setattr(self,name,None)
        for name in ('width','precision'):
            count=getattr(self,name)
            if count is not None:count.close();erase_marker(count.tape);setattr(self,name,None)

    def __enter__(self):return self
    def __exit__(self,*_):self.close()
