"""Actual heterogeneous Full words emitted as one complete global program.

This is a new global rounded execution, not a tensor power of local rounders.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The Full/fixed-word compiler is credited to #4205/#4253; cache bounds to #4178.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import prod

from sources import need,exact_preparation


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def ceil_log2(value):
    value = Q(value)
    need(value > 0,'positive logarithm argument')
    k = value.numerator.bit_length()-value.denominator.bit_length()
    bound = Q(1 << k) if k >= 0 else Q(1,1 << -k)
    return k if bound >= value else k+1


def power_two(value):
    return type(value) is int and value > 0 and value & (value-1) == 0


def freeze(stages):
    return tuple((kind,value if kind == 'H' else tuple((Q(z),Q(0)) if type(z) in (int,Q)
                                                      else (z.re,z.im) for z in value))
                 for kind,value in stages)


def word_hash(stages):
    return sha256(canonical([(kind,value if kind == 'H' else
                              [(str(a),str(b)) for a,b in value])
                             for kind,value in stages])).hexdigest()


def signature(stages):
    return tuple((kind,value if kind == 'H' else None) for kind,value in stages)


def truncate_fraction(value,bits):
    return int(value*(1 << bits))


@dataclass(frozen=True)
class Hadamard:
    step: int
    array_bits: int
    positions: tuple[int,...]
    fractional_bits: int
    data_width: int

    def validate(self):
        need(type(self.array_bits) is int and self.array_bits >= 1,'global field bits')
        need(self.positions and len(set(self.positions)) == len(self.positions)
             and all(type(p) is int and 0 <= p < self.array_bits for p in self.positions),
             'complete global H mask')
        need(type(self.fractional_bits) is int and self.fractional_bits >= 1
             and type(self.data_width) is int and self.data_width >= self.fractional_bits+2,
             'global H common grid and signed width')


@dataclass(frozen=True)
class Diagonal:
    step: int
    coarse_bits: int
    axis_bits: int
    axes: int
    fractional_bits: int
    data_width: int
    factor_width: int
    cache_width: int
    temporary_width: int
    pages: tuple

    @property
    def array_bits(self):
        return self.coarse_bits+self.axes*self.axis_bits

    def validate(self):
        need(type(self.coarse_bits) is int and self.coarse_bits >= 0
             and type(self.axis_bits) is int and self.axis_bits >= 1
             and type(self.axes) is int and self.axes >= 1,'global diagonal geometry')
        need(len(self.pages) == 1 << self.coarse_bits
             and all(len(block) == self.axes and all(len(row) == 1 << self.axis_bits
                     for row in block) for block in self.pages),'all encoded factor pages')
        need(all(len(z) == 2 for block in self.pages for row in block for z in row),
             'complex encoded factor records')
        need(all(type(x) is int and -(1 << (self.factor_width-1)) <= x < 1 << (self.factor_width-1)
                 for block in self.pages for row in block for z in row for x in z),
             'encoded factor word widths')


class FullTensor:
    """Prepare actual Full roots; synchronize only with complete idle words.

    A service consumes complete global integer arrays on one common F-grid.
    H returns exact raw H; D computes the declared rounded suffix product and
    data multiplication. Physical services, not this producer, own tape work.
    """
    @exact_preparation
    def __init__(self,dense,lower,source,matrices,directions,*,target=16,
                 radius_bits=0,incoming=0,indices=None,fractional_bits=None):
        self.dense,self.lower,self.source = dense,lower,source
        self.labels,self.axes = len(matrices),len(matrices[0]) if matrices else 0
        need(power_two(self.labels) and self.axes >= 1
             and all(len(block) == self.axes for block in matrices),'complete coarse/axis family')
        self.size = len(matrices[0][0])
        need(power_two(self.size) and self.size >= 2
             and all(len(matrix) == self.size and all(len(row) == self.size for row in matrix)
                     for block in matrices for matrix in block),'uniform complete dyadic Full sides')
        need(len(directions) == self.labels and all(len(row) == self.axes
             and all(type(x) is bool for x in row) for row in directions),'every actual Full direction')
        need(type(target) is int and target >= 1 and type(radius_bits) is int and radius_bits >= 0
             and type(incoming) is int and incoming >= 0,'global exact accuracy/radius/grid')
        self.directions = tuple(tuple(row) for row in directions)
        self.target,self.radius_bits,self.incoming = target,radius_bits,incoming
        self.radius = 1 << radius_bits
        self.coarse_bits,self.axis_bits = self.labels.bit_length()-1,self.size.bit_length()-1
        self.array_bits = self.coarse_bits+self.axes*self.axis_bits
        self.records = 1 << self.array_bits
        self.tau = Q(1,1 << target)
        if indices is None:
            indices = [[list(range(self.size)) for _ in range(self.axes)] for _ in range(self.labels)]
        need(len(indices) == self.labels and all(len(block) == self.axes for block in indices),
             'every source wire permutation')
        admission = [[source.full.admission(source.e.Mat(matrix)) for matrix in block] for block in matrices]
        endpoints = [[admission[c][a][int(self.directions[c][a])] for a in range(self.axes)]
                     for c in range(self.labels)]
        exact_endpoint = max(x for block in endpoints for x in block)
        self.preparation_target = target+ceil_log2(8*self.axes*self.radius*(exact_endpoint+1)**(self.axes-1))
        self.roots = [[dense.FullRoot(source,matrix,1,self.preparation_target,indices[c][a])
                       for a,matrix in enumerate(block)] for c,block in enumerate(matrices)]
        self.programs = [[root.lower(self.directions[c][a],incoming=0)
                          for a,root in enumerate(block)] for c,block in enumerate(self.roots)]
        self.depths = tuple(tuple(p.logical_layers for p in block) for block in self.programs)
        self.layers = max(n for block in self.depths for n in block)
        self.padding = dense.NativeProgram(source,self.size,[[]],1,1,1,1)
        self.idle_word = freeze(self.padding.raw_stages)
        self.idle_seal = word_hash(self.idle_word)
        self.layer_signature = signature(self.idle_word)
        self.layer_stages = 16*self.axis_bits+5
        need(len(self.idle_word) == self.layer_stages,'actual complete idle compiler word')
        self.words = tuple(tuple(freeze(p.raw_stages) for p in block) for block in self.programs)
        self.word_seals = tuple(tuple(word_hash(w) for w in block) for block in self.words)
        for c,block in enumerate(self.words):
            for a,word in enumerate(block):
                need(len(word) == self.depths[c][a]*self.layer_stages,'whole source matching layers')
                need(signature(word) == self.layer_signature*self.depths[c][a],
                     'actual coefficient-independent H signature')
        self.stages = self.layers*self.layer_stages
        self.diagonal_count = self.layers*(8*self.axis_bits+3)
        self.h_count = self.layers*(8*self.axis_bits+2)
        self.prefix = max(prod(2*p.compiled_bound for p in block) for block in self.programs)
        self.endpoint = max(prod(p.endpoint for p in block) for block in self.programs)
        defects=[]
        for c,block in enumerate(self.programs):
            suffix=[Q(1)]*(self.axes+1)
            for a in range(self.axes-1,-1,-1):
                suffix[a]=endpoints[c][a]*suffix[a+1]
            preceding,total=Q(1),Q(0)
            for a,p in enumerate(block):
                total += preceding*p.upstream_error*suffix[a+1]
                preceding *= p.endpoint
            defects.append(total)
        self.source_operator_defects=tuple(defects)
        self.source_error=self.radius*max(defects)
        need(self.source_error <= self.tau/8,'funded complete source tensor defect')
        values = [abs(a)+abs(b) for block in self.words for word in block
                  for kind,page in word if kind == 'D' for a,b in page]
        values += [abs(a)+abs(b) for kind,page in self.idle_word if kind == 'D' for a,b in page]
        bound = max(Q(1),*values)
        self.factor_bound = -(-bound.numerator//bound.denominator)
        b,A,E,R,D,g = self.factor_bound+1,self.prefix,self.endpoint,self.radius,self.diagonal_count,self.axes
        self.norm_conversion = 1 << ((self.array_bits+1)//2)
        self.coefficient_constant = 8*E*D*A*A*g*b**(g-1)*R
        self.rounding_constant = 4*E*A*D*self.norm_conversion
        minimum = max(incoming,1,target+ceil_log2(4*(self.coefficient_constant+self.rounding_constant)))
        self.bits = minimum if fractional_bits is None else fractional_bits
        need(type(self.bits) is int and self.bits >= minimum,'funded global common grid')
        self.unit = Q(1,1 << self.bits)
        self.diagonal_error = 4*g*b**(g-1)*self.unit
        self.perturbation = D*A*A*self.diagonal_error
        self.arithmetic_error = (self.coefficient_constant+self.rounding_constant)*self.unit
        need(self.perturbation <= Q(1,2) and self.arithmetic_error <= self.tau/4,
             'global perturbed-prefix and complete numerical budgets')
        self.total_error = self.source_error+self.arithmetic_error
        need(self.total_error < self.tau,'strict complete root target')
        self.amplitude = 4*A*(R+1)
        self.amplitude_bits = ceil_log2(self.amplitude)
        self.cache_bits = ceil_log2(2*b**g)
        self.factor_width = self.bits+ceil_log2(b)+2
        self.data_width = self.bits+self.amplitude_bits+2
        self.cache_width = self.bits+self.cache_bits+2
        self.temporary_width = 2*self.bits+max(self.amplitude_bits,ceil_log2(b))+self.cache_bits+3
        self._seal = self._allocation_seal()
        self.validate()

    def _allocation_seal(self):
        names = ('labels','axes','size','target','radius_bits','radius','incoming','tau',
                 'coarse_bits','axis_bits','array_bits','records','preparation_target','depths',
                 'layers','layer_stages','layer_signature','idle_seal','word_seals','stages',
                 'diagonal_count','h_count','prefix','endpoint','source_operator_defects','source_error',
                 'factor_bound','norm_conversion','coefficient_constant','rounding_constant','bits',
                 'unit','diagonal_error','perturbation','arithmetic_error','total_error','amplitude',
                 'amplitude_bits','cache_bits','factor_width','data_width','cache_width',
                 'temporary_width','directions')
        return sha256(canonical({name:str(getattr(self,name)) for name in names})).hexdigest()

    @exact_preparation
    def validate(self):
        need(self._allocation_seal() == self._seal,'unchanged global request/allocation')
        for c,block in enumerate(self.programs):
            for a,p in enumerate(block):
                need(p.context is self.roots[c][a],'same actual Full root context')
                p.context.validate()
                need(p.contract_hash() == p.contract_seal
                     and self.lower.plan_hash(p.source,p.plan) == p.reference_hash
                     and self.lower.stage_hash(p.source,p.reference_stages) == p.reference_stage_seal
                     and self.lower.stage_hash(p.source,p.stages) == p.stage_seal,
                     'unchanged actual Full/native source')
                need(word_hash(freeze(p.raw_stages)) == self.word_seals[c][a]
                     and word_hash(self.words[c][a]) == self.word_seals[c][a],'immutable source raw pages')
                for j,((kind,value),(kind2,reference)) in enumerate(zip(p.raw_stages,p.reference_stages)):
                    need(kind == kind2,'raw/compensated stage type')
                    if kind == 'H':
                        need(value == reference,'raw/compensated bit')
                    else:
                        scale = 2 if j and p.raw_stages[j-1][0] == 'H' else 1
                        need(all(scale*x == y for x,y in zip(value,reference)),
                             'actual immediate H0 compensation relation')
        need(freeze(self.padding.raw_stages) == self.idle_word
             and word_hash(self.idle_word) == self.idle_seal
             and signature(self.idle_word) == self.layer_signature,'immutable compiled identity padding')

    def reference_stage(self,coarse,axis,step):
        word = self.words[coarse][axis]
        return word[step] if step < len(word) else self.idle_word[step % self.layer_stages]

    def events(self):
        self.validate()
        for step in range(self.stages):
            kind,bit = self.layer_signature[step % self.layer_stages]
            if kind == 'H':
                event = Hadamard(step,self.array_bits,tuple(a*self.axis_bits+bit for a in range(self.axes)),
                                 self.bits,self.data_width)
            else:
                pages = tuple(tuple(tuple((truncate_fraction(a,self.bits),truncate_fraction(b,self.bits))
                                          for a,b in self.reference_stage(c,axis,step)[1])
                                    for axis in range(self.axes)) for c in range(self.labels))
                event = Diagonal(step,self.coarse_bits,self.axis_bits,self.axes,self.bits,self.data_width,
                                 self.factor_width,self.cache_width,self.temporary_width,pages)
            event.validate()
            yield event
        self.validate()

    def execute(self,values,service):
        self.validate()
        original = tuple(tuple(z) for z in values)
        need(len(original) == self.records and all(len(z) == 2 and all(type(x) is int for x in z)
             for z in original),'complete incoming encoded field')
        need(all(abs(x).bit_length()+1 <= self.incoming+self.radius_bits+2
                 for z in original for x in z),'incoming signed component width')
        need(sum(a*a+b*b for a,b in original) <= self.radius*self.radius*(1 << (2*self.incoming)),
             'actual global input Euclidean radius')
        state = [(a << (self.bits-self.incoming),b << (self.bits-self.incoming)) for a,b in original]
        counts = dict(input_real_squares=2*self.records,initial_component_lifts=2*self.records,
                      global_H_calls=0,global_diagonal_calls=0,generated_factor_components=0)
        for event in self.events():
            if isinstance(event,Hadamard):
                returned = service.apply_h(state,event)
                counts['global_H_calls'] += 1
            else:
                returned = service.apply_diagonal(state,event)
                counts['global_diagonal_calls'] += 1
                counts['generated_factor_components'] += 2*self.labels*self.axes*self.size
            need(returned is state and len(state) == self.records,'complete in-place global field return')
            need(all(len(z) == 2 and all(type(x) is int and -(1 << (self.data_width-1)) <= x
                                        < 1 << (self.data_width-1) for x in z) for z in state),
                 'proved completed data width')
        need(counts['global_H_calls'] == self.h_count and counts['global_diagonal_calls'] == self.diagonal_count,
             'all padded global events executed')
        need(original == tuple(tuple(z) for z in values),'borrowed encoded input preserved')
        self.validate()
        return state,counts

    @exact_preparation
    def record(self):
        self.validate()
        return dict(labels=self.labels,axes=self.axes,side=self.size,array_bits=self.array_bits,
                    records=self.records,directions=self.directions,logical_depths=self.depths,
                    padded_depth=self.layers,padding_layers=sum(self.layers-n for row in self.depths for n in row),
                    stages=self.stages,global_H_calls=self.h_count,global_diagonal_calls=self.diagonal_count,
                    target_bits=self.target,incoming_bits=self.incoming,radius_bits=self.radius_bits,
                    preparation_target_bits=self.preparation_target,global_grid=self.bits,
                    signed_data_width=self.data_width,factor_width=self.factor_width,cache_width=self.cache_width,
                    temporary_width=self.temporary_width,source_error_log2_upper=ceil_log2(self.source_error)
                    if self.source_error else None,arithmetic_error=str(self.arithmetic_error),
                    total_error=str(self.total_error),prefix_log2_upper=ceil_log2(self.prefix),
                    endpoint_log2_upper=ceil_log2(self.endpoint),amplitude_bits=self.amplitude_bits,
                    raw_word_sha256=self.word_seals,allocation_sha256=self._seal)
