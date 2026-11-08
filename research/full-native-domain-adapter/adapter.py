"""Whole-program domain and accuracy adapter for actual fixed-H programs.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The frozen Full compiler and fixed-H words remain Jose Manuel's/Vlado's work.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json

from sources import need


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def norm2(values):
    return sum((z.re*z.re + z.im*z.im for z in values), Q(0))


def ceil_log2(value):
    value = Q(value)
    need(value > 0, 'positive logarithm argument')
    k = value.numerator.bit_length() - value.denominator.bit_length()
    p = Q(1 << k) if k >= 0 else Q(1, 1 << -k)
    return k if p >= value else k+1


@dataclass(frozen=True)
class Request:
    """A Euclidean whole-field defect request, not a per-coordinate request."""
    size: int
    bit: int
    incoming_bits: int
    error_bits: int

    def validate(self):
        need(type(self.size) is int and self.size >= 2 and self.size & (self.size-1) == 0,
             'native complete dyadic field')
        need(type(self.bit) is int and 0 <= self.bit < self.size.bit_length()-1,
             'native selected bit')
        need(type(self.incoming_bits) is int and self.incoming_bits >= 0,
             'native incoming grid')
        need(type(self.error_bits) is int and self.error_bits >= 0,
             'native requested error')

    @property
    def sigma(self):
        return Q(1, 1 << self.error_bits)


class AdaptedProgram:
    """Keep the source plan/pages, run scaled data, replace H by a typed service.

    The service must implement H0 on the actual stored unit-disk input with
    the requested *whole-field Euclidean* error. It may be nonlinear.
    Only the verifier's optional observer computes an exact H0 comparison.
    """
    def __init__(self, program, lower):
        self.program, self.lower, self.e = program, lower, program.e
        self._validate_source()
        c, r, e0 = program.compiled_bound, program.radius, program.endpoint
        self.scale_bits = max(0, ceil_log2(8*c*(r+1)))
        self.scale = 1 << self.scale_bits
        self.bits = program.bits + self.scale_bits
        self.tau = Q(1, 1 << program.target)
        self.baseline = program.total_error
        self.margin = self.tau - self.baseline
        need(self.margin > 0, 'strict remaining source error margin')
        h = program.h_count
        self.error_bits = max(0, ceil_log2(max(4*e0*c*h*self.scale/self.margin,
                                             8*c*c*h))) if h else None
        self.sigma = Q(1, 1 << self.error_bits) if h else Q(0)
        self.extra_error = 2*e0*c*h*self.scale*self.sigma
        self.domain_bound = program.amplitude/self.scale + 2*c*c*h*self.sigma
        need(program.amplitude == 4*c*(r+1), 'retained source amplitude formula')
        need(self.domain_bound <= Q(3,4) and self.extra_error <= self.margin/2,
             'native domain and final-error budgets')
        self.total_error = self.baseline + self.extra_error
        need(self.total_error < self.tau, 'strict complete target')
        # Stored normalized values have modulus <=3/4. A signed component
        # word of bits+2 is ample; diagonal products use F+bits fractional bits.
        self.data_width = self.bits + 2
        self.temporary_fractional = program.bits + self.bits
        self.temporary_width = self.temporary_fractional + program.gamma_bits + 7
        self._seal = self._seal_value()

    def _validate_source(self):
        p = self.program
        need(p.contract_hash() == p.contract_seal, 'unchanged source contract')
        if p.context is not None:
            p.context.validate()
        need(self.lower.plan_hash(p.source, p.plan) == p.reference_hash
             and self.lower.stage_hash(p.source, p.reference_stages) == p.reference_stage_seal
             and self.lower.stage_hash(p.source, p.stages) == p.stage_seal,
             'unchanged source plan and coefficient pages')

    def _seal_value(self):
        return sha256(canonical({name:str(getattr(self,name)) for name in (
            'scale_bits','scale','bits','tau','baseline','margin','error_bits','sigma',
            'extra_error','domain_bound','total_error','data_width','temporary_fractional',
            'temporary_width')})).hexdigest()

    def validate(self):
        self._validate_source()
        need(self._seal_value() == self._seal, 'unchanged adapter allocation')

    def request(self, bit):
        need(self.program.h_count > 0, 'no native call in an H-free program')
        request = Request(self.program.size, bit, self.bits, self.error_bits)
        request.validate()
        return request

    def execute(self, vector, service, observer=None):
        self.validate()
        p, E = self.program, self.e
        original = E.Vec(vector)
        need(len(original) == p.size and norm2(original) <= p.radius*p.radius,
             'original input dimension and radius')
        need(all((part*(1 << p.incoming)).denominator == 1
                 for z in original for part in (z.re,z.im)), 'original input grid')
        state = E.Vec(z/self.scale for z in original)
        need(all((part*(1 << self.bits)).denominator == 1
                 for z in state for part in (z.re,z.im)), 'normalized initial grid')
        stats = dict(input_admission_real_squares=2*p.size,
                     diagonal_real_products=0,host_complex_roundings=0,native_calls=0,
                     rescale_components=4*p.size,maximum_data_bits=0,
                     maximum_diagonal_temporary_bits=0)

        def temporary(value):
            integer = value*(1 << self.temporary_fractional)
            need(integer.denominator == 1, 'diagonal temporary grid')
            width = abs(integer.numerator).bit_length()+1
            need(width <= self.temporary_width, 'diagonal temporary width')
            stats['maximum_diagonal_temporary_bits'] = max(
                stats['maximum_diagonal_temporary_bits'], width)
            return value

        def store(value):
            result = E.rounded(value,self.bits)  # source: nearest, ties upward
            for part in (result.re,result.im):
                integer = part*(1 << self.bits)
                need(integer.denominator == 1, 'normalized stored grid')
                width = abs(integer.numerator).bit_length()+1
                need(width <= self.data_width, 'normalized signed word width')
                stats['maximum_data_bits'] = max(stats['maximum_data_bits'],width)
            stats['host_complex_roundings'] += 1
            return result

        for index,(kind,value) in enumerate(p.stages):
            if kind == 'D':
                for i,(a,x) in enumerate(zip(value,state)):
                    ar,ai = temporary(a.re*x.re),temporary(a.re*x.im)
                    br,bi = temporary(a.im*x.re),temporary(a.im*x.im)
                    state[i] = store(E.C(temporary(ar-bi),temporary(ai+br)))
                    stats['diagonal_real_products'] += 4
            else:
                need(kind == 'H', 'source native stage kind')
                request = self.request(value)
                # Domain checking/oracle snapshots belong to optional evidence,
                # not to the accelerated service's production tariff.
                before = E.Vec(state) if observer is not None else None
                returned = service.apply(state,request,E)
                need(returned is state and len(state) == p.size, 'native in-place field return')
                if observer is not None:
                    observer(index,request,before,E.Vec(state),self)
                for i,z in enumerate(state):
                    state[i] = store(z)
                stats['native_calls'] += 1
        need(stats['native_calls'] == p.h_count
             and stats['host_complex_roundings'] == p.stage_count*p.size
             and stats['diagonal_real_products'] == 4*p.diagonal_count*p.size,
             'all original stages and ordinary work retained')
        output = E.Vec(z*self.scale for z in state)
        need(all((part*(1 << p.bits)).denominator == 1
                 for z in output for part in (z.re,z.im)), 'original output grid restored')
        need(original == E.Vec(vector), 'borrowed caller input preserved')
        self.validate()
        return output,stats

    def record(self):
        self.validate()
        p = self.program
        return dict(size=p.size,target_bits=p.target,incoming_bits=p.incoming,
                    logical_layers=p.logical_layers,stages=p.stage_count,
                    hadamard_calls=p.h_count,source_grid=p.bits,
                    scale_bits=self.scale_bits,working_grid=self.bits,
                    requested_whole_field_bits=self.error_bits,
                    margin=str(self.margin),baseline=str(self.baseline),
                    extra_error=str(self.extra_error),total_error=str(self.total_error),
                    domain_bound=str(self.domain_bound),data_width=self.data_width,
                    diagonal_temporary_width=self.temporary_width,
                    source_plan=p.reference_hash,source_pages=p.stage_seal,
                    allocation_sha256=self._seal)
