"""Retained dirty compact-control word with a sequential repair interpreter.

The algebra and original guard are Douglas Colkitt's retained construction.
This interpreter supplies payload movement, keyed repair and scratch closure.
"""
from dataclasses import dataclass
from math import prod

from streams import (Tape,need,copy,bit_key,key_value,stable_radix,
                     digit_permutation,flip_digit)


@dataclass(frozen=True)
class Layout:
    fields: tuple
    record_bits: int

    @property
    def bits(self):return sum(width for _,width in self.fields)
    @property
    def records(self):return 1<<self.bits
    @property
    def names(self):return tuple(name for name,_ in self.fields)

    def width(self,name):return dict(self.fields)[name]

    def position(self,name,low_bit=0):
        before=0
        for field,width in self.fields:
            if field==name:
                need(0<=low_bit<width,"field bit extent")
                return before+width-1-low_bit
            before+=width
        raise ValueError("unknown field")

    def decode(self,index):
        need(0<=index<self.records,"full record address")
        out={}
        for name,width in reversed(self.fields):
            out[name]=index% (1<<width);index>>=width
        return out

    def encode(self,state):
        out=0
        for name,width in self.fields:
            need(0<=state[name]<1<<width,"encoded field extent")
            out=(out<<width)+state[name]
        return out


@dataclass(frozen=True)
class Compact:
    n: int
    K: int
    G: int
    rho: int
    source: str | None
    target: str
    late: bool=False

    def validate(self,layout):
        need(self.n>=1 and self.K>=1 and self.G>=1 and 0<=self.rho<self.K,"compact domain")
        need(layout.width(self.target)==(self.n+1)*self.K,"wide target extent")
        need(all(layout.width(name)==self.n*self.G for name in ("u","t","b")),
             "complete equal compact fields")
        need(layout.names.index("u")<layout.names.index(self.target) and
             layout.names.index("t")<layout.names.index(self.target)<layout.names.index("b"),
             "front and back compact placement")
        if self.source is not None:
            need(layout.width(self.source)==(self.n+1)*self.K,"wide source extent")
            need((layout.names.index(self.source)>layout.names.index(self.target))==self.late,
                 "declared source order")
        else:need(not self.late,"constant toggle uses early routine")

    def select(self,value):
        return sum(((value>>(self.rho+i*self.K))&1)<<(i*self.G) for i in range(self.n))

    def mask(self,value,compact=False):
        return sum(((value>>(i*self.G if compact else self.rho+i*self.K))&1)
                   <<(self.rho+i*self.K) for i in range(self.n))

    def operations(self):
        ops=[]
        def rot(target,controls,kind,sign=1):ops.append(("rotate",target,controls,kind,sign))
        def load(front,controls,kind,sign=1):
            ops.append(("swap",front,"b"));rot("b",controls,kind,sign);ops.append(("swap",front,"b"))
        def flip(control,is_compact=False):
            tag="compact" if is_compact else "wide"
            controls=(() if control is None else (control,))+("t",)
            rot(self.target,controls,"first_"+tag)
            load("t",(self.target,),"selected_y")
            rot(self.target,controls,"second_"+tag)
            controls=(() if control is None else (control,))+(self.target,)
            load("t",controls,"original_"+tag,-1)
        if self.late:
            flip("u",True);load("u",(self.source,),"selected_x")
            flip("u",True);load("u",(self.source,),"selected_x",-1)
        else:flip(self.source)
        return tuple(ops)

    def offset(self,state,operation):
        _,target,controls,kind,sign=operation
        if kind=="selected_y":return sign*self.select(state[self.target])
        if kind=="selected_x":return sign*self.select(state[self.source])
        compact=kind.endswith("compact")
        control="u" if compact else self.source
        bits=[1 if control is None else (state[control]>>(i*self.G if compact else self.rho+i*self.K))&1
              for i in range(self.n)]
        if kind.startswith("original"):
            value=state[self.target]^sum(b<<(self.rho+i*self.K) for i,b in enumerate(bits))
            return sign*self.select(value)
        B=1<<self.G
        return sign*sum(bits[i]*(2*((state["t"]>>(i*self.G))&(B-1)) if kind.startswith("first")
                               else 1-2*((state["t"]>>(i*self.G))&(B-1)))
                       <<(self.rho+i*self.K) for i in range(self.n))

    def execute(self,state,layout,inverse=False):
        out=dict(state)
        for op in reversed(self.operations()) if inverse else self.operations():
            if op[0]=="swap":out[op[1]],out[op[2]]=out[op[2]],out[op[1]]
            else:out[op[1]]=(out[op[1]]+(-1 if inverse else 1)*self.offset(out,op))%(1<<layout.width(op[1]))
        return out

    def ideal(self,state,highest=False):
        out=dict(state);n=self.n+int(highest)
        value=(sum(1<<(self.rho+i*self.K) for i in range(n)) if self.source is None else
               sum(((state[self.source]>>(self.rho+i*self.K))&1)<<(self.rho+i*self.K) for i in range(n)))
        out[self.target]^=value
        return out

    def bad(self,state):
        B=1<<self.G;upper=(1<<(self.K-1))-2*B;mask=(1<<(self.K-1))-1
        return any(((state["t"]>>(i*self.G))&(B-1))==B-1 or
                   not 2*B<=((state[self.target]>>(self.rho+i*self.K+1))&mask)<upper or
                   (self.late and ((state["u"]>>(i*self.G))&(B-1))==B-1)
                   for i in range(self.n))


def ordinary(source,layout,first,second):
    """Completed elementary supplier used in tests; retain the abstract call bill."""
    width=layout.width(first);need(width==layout.width(second),"equal ordinary chunks")
    source.meter.ordinary_calls.append({"width":width,"volume":len(source.data)})
    for bit in range(width):
        a,b=sorted((layout.position(first,bit),layout.position(second,bit)))
        source=digit_permutation(source,layout.bits,a,b,layout.record_bits,(0,2,1,3))
    return source


def rotate(source,layout,word,op):
    _,target,controls,_,_=op;at=layout.names.index(target)
    need(all(layout.names.index(name)<at for name in controls),"all rotation controls precede target")
    before=sum(width for _,width in layout.fields[:at]);after=sum(width for _,width in layout.fields[at+1:])
    width=layout.width(target);radix=1<<width;suffix=(1<<after)*layout.record_bits
    source.rewind();left=Tape(source.meter);right=Tape(source.meter);out=Tape(source.meter)
    for prefix in range(1<<before):
        state=layout.decode(prefix<<(width+after));cut=word.offset(state,op)%radix
        source.meter.control_evaluations+=1
        copy(source,left,(radix-cut)*suffix);copy(source,right,cut*suffix)
    source.finish();left.rewind();right.rewind()
    for prefix in range(1<<before):
        state=layout.decode(prefix<<(width+after));cut=word.offset(state,op)%radix
        source.meter.control_evaluations+=1
        copy(right,out,cut*suffix);copy(left,out,(radix-cut)*suffix)
    left.finish();right.finish();left.erase();right.erase();source.erase();out.rewind()
    source.meter.rotation_passes+=1
    return out


def repair(source,layout,word,wrong_inverse=False):
    source.rewind();good=Tape(source.meter);bad=Tape(source.meter);holes=Tape(source.meter)
    for index in range(layout.records):
        state=layout.decode(index);exception=word.bad(state);holes.write(bytes((int(exception),)))
        if exception:
            old=state if wrong_inverse else word.execute(state,layout,True)
            destination=layout.encode(word.ideal(old))
            bad.write(bit_key(destination,layout.bits));copy(source,bad,layout.record_bits)
            source.meter.repair_records+=1;source.meter.control_evaluations+=1
        else:copy(source,good,layout.record_bits)
    source.finish();source.erase();bad.rewind();good.rewind();holes.rewind()
    bad=stable_radix(bad,layout.bits,layout.record_bits);out=Tape(source.meter)
    for index in range(layout.records):
        if holes.read(1)[0]:
            destination=key_value(bad.read(layout.bits))
            need(destination==index,"sorted exceptional keys fill precisely the marked holes")
            copy(bad,out,layout.record_bits)
        else:copy(good,out,layout.record_bits)
    for tape in (bad,good,holes):tape.finish();tape.erase()
    out.rewind();return out


def execute(source,layout,word,omit_repair=False,wrong_inverse=False):
    word.validate(layout);need(len(source.data)==layout.records*layout.record_bits,"complete record rectangle")
    for op in word.operations():
        source=ordinary(source,layout,op[1],op[2]) if op[0]=="swap" else rotate(source,layout,word,op)
    if not omit_repair:source=repair(source,layout,word,wrong_inverse)
    y=layout.position(word.target,word.rho+word.n*word.K)
    if word.source is None:source=flip_digit(source,layout.bits,y,layout.record_bits)
    else:
        x=layout.position(word.source,word.rho+word.n*word.K);a,b=sorted((x,y))
        mapping=(0,1,3,2) if x<y else (0,3,2,1)
        source=digit_permutation(source,layout.bits,a,b,layout.record_bits,mapping)
    need(source.head==0,"completed compact output origin")
    return source
