"""Source-bound in-place Core interiors; no Schur/LU construction.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Core/RawGaussian/Full: Jose Manuel; carve/compiler: Vlado Vojdanovski and
retained lineage; downset grid binding: JoyboyBrian.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json
from functools import wraps
from cohort_sources import need


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def serialized(method):
    @wraps(method)
    def call(self,*args,**kwargs):
        with self.runtime.utility.trusted_exact_serialization():
            return method(self,*args,**kwargs)
    return call


class Partition:
    """Validated attributes for the unchanged Core.load_carve/partition bodies."""
    def __init__(self,runtime,reference,kind,first,size,cap,width=None):
        with runtime.utility.trusted_exact_serialization():
            self._prepare(runtime,reference,kind,first,size,cap,width)

    def _prepare(self,runtime,reference,kind,first,size,cap,width):
        need(type(reference) is runtime.reference.Reference,'actual canonical Reference constructor')
        need(kind in ('narrow','broad') and all(type(x) is int for x in (first,size,cap))
             and size >= 2 and size & (size-1) == 0 and cap >= 1 and cap & (cap-1) == 0,
             'complete dyadic source core and cap')
        minimum = (2*reference.spec.source_halfwidth+2 if kind == 'narrow'
                   else reference.spec.target_halfwidth)
        width = max(1,minimum) if width is None else width
        need(type(width) is int and width >= max(1,minimum),'actual source physical core band')
        need(0 <= first < first+size <= reference.target_size and first % size == 0
             and reference.target_size-size >= width and 2*cap <= reference.spec.source_size,
             'original complete core and complementary gap')
        self.runtime,self.reference,self.kind = runtime,reference,kind
        self.first,self.size,self.cap,self.width = first,size,cap,width
        self.spec = tuple(getattr(reference.spec,k) for k in reference.spec.__dataclass_fields__)
        self.description = reference.description_hash
        self.pieces,self.cells,self.carve_ast = self._partition()
        self.indices = tuple(tuple(cell['indices']) for cell in self.cells)
        occupied = {i for row in self.indices for i in row}
        self.boundary = tuple(i for i in range(size) if i not in occupied)
        self.matrices,self.inverses = [],[]
        for cell in self.cells:
            coords = tuple(first+i for i in cell['indices'])
            matrix = runtime.exact.Mat(reference.window(kind,coords))
            inverse = runtime.source.full.solve(runtime.source.full.Matrix(matrix),
                runtime.source.full.Matrix(runtime.exact.eye(len(matrix))))
            self.matrices.append(matrix)
            self.inverses.append(inverse)
        norm = runtime.source.full.norm_upper
        self.lambdas = (max([Q(1)]+[norm(x) for x in self.matrices]),
                        max([Q(1)]+[norm(x) for x in self.inverses]))
        self.seal = self.state()

    def _partition(self):
        shell = object.__new__(self.runtime.core.Core)
        shell.raw,shell.reference = self.runtime.raw,self.reference
        shell.n,shell.coordinates = self.size,tuple(range(self.first,self.first+self.size))
        shell.width,shell.cap = self.width,self.cap
        shell.carve,shell.carve_ast = shell.load_carve()
        pieces,cells = shell.partition()
        return pieces,cells,shell.carve_ast

    @serialized
    def state(self):
        E = self.runtime.source
        return sha256(canonical(dict(first=self.first,size=self.size,cap=self.cap,width=self.width,
            kind=self.kind,spec=self.spec,description=self.description,pieces=self.pieces,
            cells=self.cells,carve=self.carve_ast,indices=self.indices,boundary=self.boundary,
            matrices=[E.matrix_hash(x) for x in self.matrices],
            inverses=[E.matrix_hash(x) for x in self.inverses],
            lambdas=list(map(str,self.lambdas))))).hexdigest()

    @serialized
    def validate(self):
        need(self.state() == self.seal,'unchanged original partition and reference pages')
        need(self.spec == tuple(getattr(self.reference.spec,k)
             for k in self.reference.spec.__dataclass_fields__) and
             self.reference.description_hash == self.description,'same immutable reference geometry')
        pieces,cells,carve = self._partition()
        need((pieces,cells,carve) == (self.pieces,self.cells,self.carve_ast),
             'same actual Core.partition positions and holes')
        for cell,matrix in zip(self.cells,self.matrices):
            coordinates = tuple(self.first+i for i in cell['indices'])
            need(self.reference.window(self.kind,coordinates) == matrix,
                 'same exact actual interior reference')


class CoreRoot:
    """One source-qualified direct sum in its original whole-core positions."""
    def __init__(self,partition,target):
        with partition.runtime.utility.trusted_exact_serialization():
            self._prepare(partition,target)

    def _prepare(self,partition,target):
        need(type(target) is int and target >= 2,'strengthened source target')
        self.partition,self.runtime,self.target = partition,partition.runtime,target
        partition.validate()
        r = self.runtime
        self.children,self.bounds = [],[]
        for cell in partition.cells:
            child = r.Raw(r.raw,partition.reference,partition.kind,cell['source_start'],
                          len(cell['indices']),1,target,0)
            child.compile()
            cb = child.child.builder.bound
            eta,G,H = child.diagonal_error,child.gauge_bound,child.middle_bound
            need(0 <= eta <= 1,'stored gauge and reciprocal perturbation at most one')
            middle = (cb['coefficient_error']+child.child.kernel_error,
                      cb['coefficient_error']+2*child.qbar**2*child.child.kernel_error)
            gauge = H*eta*(2*G+eta)
            defect = tuple((G+eta)**2*e+gauge+ref for e,ref in zip(middle,
                (child.reference_error,2*child.raw_inverse_bound**2*child.reference_error)))
            need(max(defect) <= Q(1,1 << target),'funded exact prepared raw operator defect')
            prefix = (G+1)**2*cb['execution_bound']
            self.children.append(child)
            self.bounds.append(dict(prefix=prefix,defect=defect,middle=middle,gauge=gauge))
        self.prefix = max([Q(1)]+[row['prefix'] for row in self.bounds])
        self.defects = tuple(max([Q(0)]+[row['defect'][direction] for row in self.bounds])
                             for direction in (0,1))
        self.lambdas = partition.lambdas
        self.plan = self._union(False)
        self.inverse_plan = self._union(True)
        self.plan_seals = tuple(r.lower.plan_hash(r.source,plan)
                               for plan in (self.plan,self.inverse_plan))
        self.child_seals = tuple(self._child_state(child) for child in self.children)
        self.seal = self.state()

    def _union(self,inverse):
        plans = [x.inverse_plan if inverse else x.plan for x in self.children]
        depth = max((len(p) for p in plans),default=1)
        result = []
        for level in range(depth):
            layer = []
            for indices,plan in zip(self.partition.indices,plans):
                if level < len(plan):
                    for ids,gate in plan[level]:
                        layer.append((tuple(indices[i] for i in ids),gate))
            result.append(layer)
        return result

    def _child_state(self,child):
        r = self.runtime
        return (child.reference_hash,child.reference_description,child.target,child.radius,
            child.start,child.n,child.kind,child.child.root_hash,
            child.child.source_ast,child.child.callsite_ast,
            r.lower.plan_hash(r.source,child.plan),r.lower.plan_hash(r.source,child.inverse_plan),
            r.dense.budget_hash(r.source,child.child.builder.bound),
            tuple(child.a_values),tuple(child.b_values),
            tuple(getattr(child,name) for name in ('diagonal_error','gauge_bound',
                'middle_bound','qbar','reference_error','raw_inverse_bound')),
            child.child.kernel_error)

    def state(self):
        return (self.partition.seal,self.target,self.prefix,self.defects,self.lambdas,
                self.plan_seals,self.child_seals)

    @serialized
    def validate(self):
        self.partition.validate()
        need(self.state() == self.seal,'unchanged complete source root contract')
        r = self.runtime
        need(tuple(self._child_state(x) for x in self.children) == self.child_seals,
             'same raw gauges and actual stored Full children')
        need(tuple(r.lower.plan_hash(r.source,p) for p in (self.plan,self.inverse_plan))
             == self.plan_seals,'unchanged complete embedded source words')
        need(all(r.lower.plan_hash(r.source,p) == s for p,s in zip(
             (self._union(False),self._union(True)),self.plan_seals)),
             'actual disjoint source matching-layer union')

    @serialized
    def lower(self,inverse=False,incoming=0):
        need(type(inverse) is bool,'actual source stored direction')
        self.validate()
        return self.runtime.dense.NativeProgram(self.runtime.source,self.partition.size,
            self.inverse_plan if inverse else self.plan,self.prefix,
            self.lambdas[inverse]+self.defects[inverse],1,self.target-1,incoming,
            upstream_error=self.defects[inverse],context=self)

    @serialized
    def record(self):
        self.validate()
        return dict(first=self.partition.first,size=self.partition.size,kind=self.partition.kind,
            indices=self.partition.indices,boundary=self.partition.boundary,
            source_target=self.target,prefix=str(self.prefix),defects=list(map(str,self.defects)),
            endpoint_bounds=list(map(str,self.lambdas)),plans=self.plan_seals,
            full_roots=[x.child.root_hash for x in self.children],
            source_starts=[x.start for x in self.children],
            depths=[len(x.plan) for x in self.children])
