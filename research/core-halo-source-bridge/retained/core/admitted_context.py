"""Validated original-coordinate interiors and complete global dense cohorts.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
import inspect
from core_roots import Partition,CoreRoot
from core_caller import allocation_suffix
from cohort_sources import need

class AdmittedPartition(Partition):
    """Explicit small-partition provider; does not replace production carving."""
    def __init__(self,runtime,reference,kind,first,size,cap,interiors,width=None):
        self.admitted_interiors=tuple(tuple(row) for row in interiors)
        super().__init__(runtime,reference,kind,first,size,cap,width)

    def _partition(self):
        occupied=set();cells=[];previous=-1
        for row in self.admitted_interiors:
            n=len(row)
            need(n>0 and n&(n-1)==0 and n<=self.cap,'nonempty dyadic admitted interior')
            need(all(type(i) is int for i in row) and row==tuple(range(row[0],row[0]+n))
                 and previous<row[0] and 0<=row[0] and row[-1]<self.size,
                 'ordered disjoint original-coordinate interiors')
            need(not occupied.intersection(row),'disjoint admitted interiors')
            start=self.reference.source_at.get(self.first+row[0])
            need(start is not None,'actual selected interior start')
            coordinates,center,beta=self.reference.interior(start,n)
            need(tuple(coordinates)==tuple(self.first+i for i in row),
                 'same actual phase-pure Reference interior')
            occupied.update(row);previous=row[-1]
            cells.append(dict(indices=list(row),source_start=start,center=str(center),beta=str(beta)))
        need(occupied and len(occupied)<self.size,'nonempty interior and boundary')
        for k,a in enumerate(self.admitted_interiors):
            for b in self.admitted_interiors[k+1:]:
                for i in a:
                    for j in b:
                        need(self.reference.entry(self.kind,self.first+i,self.first+j).value==0
                             and self.reference.entry(self.kind,self.first+j,self.first+i).value==0,
                             'exact zero cross-interior source coupling')
        token=sha256(inspect.getsource(type(self)._partition).encode()).hexdigest()
        return [],cells,'explicit-admitted-partition:'+token

def prepare(runtime,family,inverse,*,target,radius_bits,incoming=0,fractional_bits=None):
    """K complete contexts; router axis0 is most significant, dense axis0 low.

    Reversal concerns the input-independent source-axis list only. Payload stays
    in context-major, lexicographic router-coordinate order throughout.
    """
    with runtime.utility.trusted_exact_serialization():
        K=len(family);g=len(family[0]) if K else 0
        need(K>0 and K&(K-1)==0 and g>0 and all(len(row)==g for row in family),
             'complete dyadic coarse family and all local axes')
        size=family[0][0].size
        need(all(p.runtime is runtime and p.size==size for row in family for p in row),
             'same numerical identity and complete local side')
        need(type(inverse) is bool and target>=1 and radius_bits>=0 and incoming>=0,
             'global target radius and grid')
        obj=object.__new__(runtime.global_compiler.FullTensor)
        obj.dense,obj.lower,obj.source=runtime.dense,runtime.lower,runtime.source
        obj.labels,obj.axes,obj.size=K,g,size
        obj.coarse_bits,obj.axis_bits=K.bit_length()-1,size.bit_length()-1
        obj.array_bits=obj.coarse_bits+g*obj.axis_bits;obj.records=1<<obj.array_bits
        obj.target,obj.radius_bits,obj.incoming=target,radius_bits,incoming
        obj.radius,obj.tau=1<<radius_bits,Q(1,1<<target)
        ordered=[tuple(reversed(row)) for row in family]
        obj.directions=tuple(tuple(inverse for _ in row) for row in ordered)
        endpoints=[[p.lambdas[int(inverse)] for p in row] for row in ordered]
        endpoint=max(v for row in endpoints for v in row)
        obj.preparation_target=target+runtime.global_compiler.ceil_log2(
            8*g*obj.radius*(endpoint+1)**(g-1))
        obj.roots=[[CoreRoot(p,obj.preparation_target) for p in row] for row in ordered]
        obj.programs=[[root.lower(inverse,incoming=0) for root in row] for row in obj.roots]
        finish,obj.suffix_hash=allocation_suffix(runtime)
        finish(obj,runtime.dense,runtime.source,endpoints,target,incoming,fractional_bits)
        return obj
