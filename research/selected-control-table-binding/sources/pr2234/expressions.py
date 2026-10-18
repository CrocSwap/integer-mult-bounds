"""Generated weights refer to frozen prefix fields, not one sampled header.

One expression serves a complete high packet. A streaming evaluator substitutes
the current values of older high fields at each coefficient preparation.
Fresh row stock and the current invocation's fresh matrix are outside this API.
"""
from dataclasses import dataclass, field

from fallback_program import Ancestor
from provider import RawHeader, GeneralHeader, need


@dataclass(frozen=True)
class FieldSpecification:
    q: int
    width: int
    request: object
    low_matrix: tuple


@dataclass
class FrozenFields:
    high_matrices: tuple
    specifications: tuple = ()
    reads: list = field(default_factory=list)

    @classmethod
    def from_headers(cls,headers):
        return cls(tuple(h.raw.high for h in headers),
                   tuple(FieldSpecification(h.q,h.width,h.request,h.raw.low) for h in headers))

    def high(self,index,specification):
        need(0<=index<len(self.high_matrices),"ancestor reference cannot read a fresh field")
        need(len(self.specifications)==len(self.high_matrices) and
             self.specifications[index]==specification,"frozen header source binding")
        self.reads.append(index)
        return self.high_matrices[index]

    @property
    def unused(self):
        raise ValueError("weight expression read unused descendant stock")


@dataclass(frozen=True)
class AncestorReference:
    kind: str
    request: object
    low_matrix: tuple
    high_slot: int
    field: int = 0
    reverse: bool = False


@dataclass(frozen=True)
class Expression:
    q: int
    width: int
    root_size: int
    root_unit: int = 1
    path: tuple = ()
    birth_depth: int = 0

    @property
    def depth(self):
        return self.birth_depth+len(self.path)

    @property
    def size(self):
        size=self.root_size
        for node in self.path:
            f=size//64
            need(f>=1,"proper expression ancestor width")
            size=node.request.base.rank*f if node.kind=="good" else f
        return size

    def append(self,kind,request,low_matrix,high_slot,field=0,reverse=False):
        need(kind in ("good","pair"),"generated child expression kind")
        need(0<request.base.rank<64 and self.size>=64,"proper recursive child label")
        need(high_slot==self.depth,"append the newly frozen parent field")
        if kind=="pair":
            need(0<=field<127,"paired-diagonal child field")
        node=AncestorReference(kind,request,low_matrix,high_slot,field,reverse)
        result=Expression(self.q,self.width,self.root_size,self.root_unit,self.path+(node,),self.birth_depth)
        need(result.size<=42*(self.size//64)<self.size,"strict weighted-child descent")
        return result

    def unit_child(self,size):
        need(0<size<self.size,"proper unweighted child width")
        return Expression(self.q,self.width,size,birth_depth=self.depth+1)


@dataclass(frozen=True)
class BoundExpression:
    expression: Expression
    catalogue: object
    fields: FrozenFields

    @property
    def q(self): return self.expression.q
    @property
    def width(self): return self.expression.width
    @property
    def root_size(self): return self.expression.root_size
    @property
    def root_unit(self): return self.expression.root_unit

    @property
    def ancestors(self):
        out=[]
        need(len(self.fields.high_matrices)==self.expression.depth,
             "incoming weight scope excludes the current fresh matrix")
        for position,node in enumerate(self.expression.path):
            need(node.high_slot==self.expression.birth_depth+position,"causal ancestor field order")
            specification=FieldSpecification(self.q,self.width,node.request,node.low_matrix)
            raw=RawHeader(self.q,self.width,node.low_matrix,self.fields.high(node.high_slot,specification),
                          node.request.header_space)
            out.append(Ancestor(node.kind,GeneralHeader(raw,node.request,self.catalogue),
                                node.field,node.reverse))
        return tuple(out)
