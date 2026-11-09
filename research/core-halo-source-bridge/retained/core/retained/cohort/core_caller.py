"""Actual Core-root adapter to the unchanged global allocation/emission suffix.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The source global caller is frozen at the published dependency in
GLOBAL-DEPENDENCY.json; only its root-creation interface is replaced here.
"""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
from cohort_sources import VENDOR,need
from core_roots import Partition,CoreRoot


def allocation_suffix(runtime):
    tree = ast.parse((VENDOR/'compiler.py').read_bytes())
    classes = [n for n in tree.body if isinstance(n,ast.ClassDef) and n.name == 'FullTensor']
    need(len(classes) == 1,'one frozen global caller class')
    functions = [n for n in classes[0].body if isinstance(n,ast.FunctionDef) and n.name == '__init__']
    need(len(functions) == 1,'one frozen global allocation')
    original = functions[0]
    matches = [i for i,n in enumerate(original.body) if isinstance(n,ast.Assign)
        and len(n.targets) == 1 and ast.unparse(n.targets[0]) == 'self.depths']
    need(len(matches) == 1,'one complete post-root allocation suffix')
    body = copy.deepcopy(original.body[matches[0]:])
    signature = ast.parse('def completed(self,dense,source,endpoints,target,incoming,fractional_bits):\n pass').body[0]
    signature.body = body
    module = ast.fix_missing_locations(ast.Module(body=[signature],type_ignores=[]))
    namespace = dict(runtime.global_compiler.__dict__)
    exec(compile(module,'<unchanged frozen global post-root allocation>','exec',optimize=0),namespace)
    return namespace['completed'],sha256(ast.dump(module).encode()).hexdigest()


def _prepare(runtime,layout,references,kinds,caps,directions,*,target=12,radius_bits=0,
            incoming=0,widths=None,fractional_bits=None):
    """Prepare every actual label/axis source; no logical microbox is omitted."""
    Base = runtime.global_compiler.FullTensor
    finish,suffix_hash = allocation_suffix(runtime)

    class CoreTensor(Base):
        def validate(self):
            need(self.layout.record() == self.layout_seal,'same original full-field layout')
            need(tuple(ref.description_hash for ref in self.references) == self.reference_seals,
                 'same complete source reference family')
            for label,block in enumerate(self.roots):
                starts = self.layout.core_starts(label)
                for axis,root in enumerate(block):
                    need(root.partition.first == starts[axis]
                         and root.partition.reference is self.references[axis],
                         'actual coarse-label source origin')
            super().validate()

    need(type(target) is int and target >= 1 and type(radius_bits) is int and radius_bits >= 0
         and type(incoming) is int and incoming >= 0,'global target radius and incoming grid')
    need(len(references) == len(kinds) == len(caps) == layout.g,'complete selected source family')
    need(len(directions) == layout.labels and all(len(row) == layout.g and
         all(type(x) is bool for x in row) for row in directions),'every actual stored direction')
    need(all(ref.target_size == 1 << layout.lengths[a]
             for ref,a in zip(references,layout.selected)),'actual original source axis lengths')
    widths = (None,)*layout.g if widths is None else tuple(widths)
    need(len(widths) == layout.g,'every source physical band')
    self = object.__new__(CoreTensor)
    self.layout,self.layout_seal = layout,layout.record()
    self.references,self.reference_seals = tuple(references),tuple(r.description_hash for r in references)
    self.dense,self.lower,self.source = runtime.dense,runtime.lower,runtime.source
    self.labels,self.axes,self.size = layout.labels,layout.g,layout.size
    self.coarse_bits = layout.n-layout.g*layout.local_bits
    self.axis_bits,self.array_bits,self.records = layout.local_bits,layout.n,1 << layout.n
    self.target,self.radius_bits,self.incoming = target,radius_bits,incoming
    self.radius,self.tau = 1 << radius_bits,Q(1,1 << target)
    self.directions = tuple(tuple(row) for row in directions)
    self.partitions = [[Partition(runtime,references[a],kinds[a],start,layout.size,caps[a],widths[a])
                        for a,start in enumerate(layout.core_starts(label))]
                       for label in range(layout.labels)]
    endpoints = [[p.lambdas[self.directions[c][a]] for a,p in enumerate(block)]
                 for c,block in enumerate(self.partitions)]
    endpoint = max(x for block in endpoints for x in block)
    self.preparation_target = target+runtime.global_compiler.ceil_log2(
        8*self.axes*self.radius*(endpoint+1)**(self.axes-1))
    self.roots = [[CoreRoot(p,self.preparation_target) for p in block] for block in self.partitions]
    self.programs = [[root.lower(self.directions[c][a],incoming=0) for a,root in enumerate(block)]
                     for c,block in enumerate(self.roots)]
    self.suffix_hash = suffix_hash
    finish(self,runtime.dense,runtime.source,endpoints,target,incoming,fractional_bits)
    return self


def prepare(runtime,*args,**kwargs):
    with runtime.utility.trusted_exact_serialization():
        return _prepare(runtime,*args,**kwargs)
