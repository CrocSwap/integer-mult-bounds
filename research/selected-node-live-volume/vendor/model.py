"""Complete small caller fixture; production streams execute its residuals.

The selected source/grammar checks are separate. This model has two-dimensional
projectors and four live families, not a sampled selected GL64 payload.
"""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as F

from cardinal_counts import Count
from directory import produce
from forms import fallback_form, good_form
from layout import Layout
from low_codes import LowCodes
from matrices import Matrices
from numeric import Geometry, Page
import oracle
import packet_engine
from plan import compile_plan
from records import BLANK, RECORD_END, Tape, append_word, read_finite, read_word, seek_record
from topology import Call, Owner
from trace import execute
from words import need

I=((F(1),F(0)),(F(0),F(1)))
S=((F(0),F(1)),(F(1),F(0)))
A=((F(1),F(1)),(F(0),F(1)))


@dataclass(frozen=True)
class Request:
    kind: str
    base: int
    family: int
    chart: tuple = I


class Catalogue:
    q=3
    dimension=2

    def __init__(self):
        self.requests=[]
        for _stage in range(2):
            self.requests.extend((Request("MOVE",0,0),Request("COPY",0,4),Request("MOVE",0,0,S)))
        for family in range(4):
            self.requests.extend((Request("IDLE",0,family,A),Request("IDLE",1,family,A)))
        self.codes=LowCodes(3,2,len(self.requests))

    def low_classes(self):
        for ordinal in range(self.codes.size):yield self.codes.unrank(ordinal)


class Topology:
    replicas=1
    pairs=2
    ports=1
    families=4
    stride=4

    def __init__(self,catalogue):
        self.catalogue=catalogue
        self.idles={i:(6+i,) for i in range(8)}
        self.schedule=tuple(
            [{"kind":"local_cover_sweep","stage":0},{"kind":"local_cover_sweep","stage":1}]
            +[{"kind":"idle","idx":i} for i in range(8)]
            +[{"kind":"bridge","dst":0,"src":1,"coefficient":c} for c in (1,-1)]
            +[{"kind":"local_cover_sweep","stage":i} for i in (2,3)]
            +[{"kind":"exchange"}])

    def call(self,stage,replica):
        need(replica==0,"model replica")
        if stage<2:
            events=((0,0,0,1,1,0),(2,0,3,1,0,1,0),(1,2,3,1,0,0),
                    (1,2,3,1,0,0),(3,0,3,1,0,0,0),(0,1,0,1,1,0))
            requests=(3*stage,3*stage+1,None,None,None,3*stage+2)
            return Call(stage,0,(Owner(0,I),Owner(0,S),Owner(1,I)),(0,0,0),(1,1,0),events,requests,False)
        pair=stage-2
        return Call(stage,0,(Owner(2*pair,I),Owner(2*pair+1,I)),(0,0),(0,0),
                    ((1,1,0,1,0,0),(1,0,1,1,0,0),(1,1,0,1,0,0)),(None,None,None),False)

    @staticmethod
    def matrix(chart):return chart

    def idle_family(self,identifier,replica):
        need(replica==0,"model native replica")
        return self.catalogue.requests[identifier].family

    @staticmethod
    def family(replica,pair,side,port):
        need(replica==port==0,"model family coordinates")
        return 2*pair+side


class Incoming:
    def __init__(self,context,indices,values):
        self.context,self.indices=context,indices
        self.tape=Tape()
        for value in values:
            word=context.arena.input(value)
            append_word(self.tape,word);self.tape.append(RECORD_END)
            context.arena.free(word)
        self.tape.rewind()

    def weight(self,coordinate):
        seek_record(self.tape,coordinate)
        value=read_word(self.tape,self.context.arena)
        need(self.tape.read()==RECORD_END,"complete encoded fixture weight")
        self.tape.rewind()
        return value

    def coefficient(self,prefix,request):
        need(prefix.read()==BLANK and request.kind=="incoming","model frozen-only root context")
        value=self.weight(request.coordinate)
        if request.negative_inverse:
            inverse=self.context.ring.inverse(value)
            need(inverse is not None,"fixture unit weight")
            opposite=self.context.ring.negate(inverse)
            self.context.arena.free_many(value,inverse);value=opposite
        return value

    def close(self):self.tape.clear()


class Consumer:
    def __init__(self,context,indices,program,parent_size,depth,catalogue,incoming):
        self.context,self.indices,self.program=context,indices,program
        self.parent_size,self.depth,self.catalogue,self.incoming=parent_size,depth,catalogue,incoming
        self.calls=Counter();self.children=Counter()

    def apply(self,source,identifier,common,low,old_directory,old_count,before,gap,suffix,observe=None):
        context,indices,arena=self.context,self.indices,self.context.arena
        request=self.catalogue.requests[identifier]
        need(common==(request.kind!="IDLE"),"model current source view")
        self.calls[request.kind]+=1
        basis=I if request.base==0 else S
        chart=I if common else request.chart
        preparation=tuple(tuple(sum(chart[i][k]*basis[k][j] for k in range(2)) for j in range(2)) for i in range(2))
        low_header=oracle.multiply(low,oracle.reduce_rational(preparation,context.q),context.q)
        p=oracle.multiply([[row[0]] for row in low_header],oracle.inverse(low_header,context.q)[:1],context.q)
        good=p[0][0]!=0
        plan=compile_plan(p,1,context.q,good)
        code=context.codes.encode(identifier,common,low)
        directory,prefixes=produce(old_directory,self.depth,old_count,code,context)
        columns,one=indices.literal(1),indices.literal(1)
        geometry=Geometry(plan,indices,columns,self.depth,code,self.program)
        fields,carry=geometry.raw.add(self.depth,one);indices.free(one)
        need(not carry,"model current field count")
        layout=Layout(geometry,self.parent_size,context.ring,context.q,before,gap,suffix)
        def coefficient(prefix,reference):
            seek_record(prefix,self.depth)
            need(read_finite(prefix,context.codes.bits)==code,"model produced request/view field")
            high=[[read_word(prefix,arena) for _ in range(2)] for _ in range(2)]
            need(prefix.read()==RECORD_END,"model raw high record")
            prefix.step(1);need(prefix.read()==BLANK,"model current field is last");prefix.rewind()
            matrices=Matrices(context.ring)
            header=matrices.raw_header(low,high,context.q)
            prepared=matrices.constants(preparation)
            full=matrices.multiply(header,prepared)
            projector=matrices.projector(full,1)
            form=good_form(projector,1,context.ring) if good else fallback_form(projector,context.ring)
            page=Page(plan,form,context.ring,indices,columns,self.incoming.weight,self.depth,code,self.program)
            value=page.evaluate(reference);page.close()
            for matrix in (high,header,prepared,full,projector):matrices.free(matrix)
            return value
        def boundary(kind):
            self.children[kind]+=1
            if observe is not None:observe(kind)
        try:return packet_engine.run(source,execute(geometry),layout,directory,prefixes,fields,coefficient,observe=boundary)
        finally:
            layout.close();geometry.close();indices.free_many(columns,fields)
            directory.clear();prefixes.close()
