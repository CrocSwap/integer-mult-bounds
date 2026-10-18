"""Use reversible quadratic phases around the pinned dirty-array solver."""
from dataclasses import dataclass
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys

_SPEC = importlib.util.spec_from_file_location(
    'dirty_phase_predecessor', Path(__file__).resolve().parent/'dirty_stride.py')
d = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = d
_SPEC.loader.exec_module(d)


def real_round(value, bits):
    scale = 1 << bits
    value = value*scale + F(1, 2)
    return F(value.numerator//value.denominator, scale)


@dataclass
class Meter(d.Meter):
    phase_evaluations: int = 0
    phase_passes: int = 0
    phase_terms: int = 0
    phase_products: int = 0
    phase_divisions: int = 0
    phase_record_moves: int = 0
    phase_recurrence_steps: int = 0
    input_reads: int = 0
    descriptor_bits: int = 0
    coefficient_bits: int = 0
    internal_bits: int = 0
    error_bound: F = F(0)
    initial_bound: F = F(0)
    phase_peak_l1: F = F(0)


def pi_approx(bits, meter):
    """Use the Machin identity and round each arctangent term."""
    value = F(0)
    for denominator, scale in ((5, 16), (239, -4)):
        power = denominator
        for k in range(bits):
            term = real_round(F(1, (2*k+1)*power), bits)
            value += scale*term if k % 2 == 0 else -scale*term
            power *= denominator*denominator
            meter.phase_terms += 1
            meter.phase_divisions += 1
            meter.phase_products += 2
    return value


@dataclass(frozen=True)
class Phase:
    numerator: int
    modulus: int
    bits: int
    internal: int
    pi: F
    meter: Meter

    @classmethod
    def prepare(cls, numerator, modulus, bits, meter):
        d.need(type(numerator) is int and type(modulus) is int and modulus > 0,
               'integer phase descriptor')
        d.need(type(bits) is int and bits >= 2, 'phase precision')
        coefficient_bits = bits+8
        internal = coefficient_bits + 2*(coefficient_bits+32).bit_length()+20
        d.need((8*internal+17)*F(1, 1 << internal)
               <= F(1, 1 << (coefficient_bits+2)), 'phase coefficient budget')
        meter.descriptor_bits += abs(numerator).bit_length()+modulus.bit_length()+2
        meter.coefficient_bits = coefficient_bits
        meter.internal_bits = internal
        return cls(numerator % modulus, modulus, bits, internal,
                   pi_approx(internal, meter), meter)

    def coefficients(self, residue):
        """Return a quarter-turn and two dyadic shear coefficients."""
        d.need(type(residue) is int and 0 <= residue < self.modulus, 'phase residue')
        self.meter.phase_evaluations += 1
        quadrant = (8*residue+self.modulus)//(2*self.modulus)
        remainder = 4*residue-quadrant*self.modulus
        if remainder == 0:
            return quadrant % 4, F(0), F(0)
        angle = real_round(self.pi*remainder/(2*self.modulus), self.internal)
        self.meter.phase_products += 1
        self.meter.phase_divisions += 1
        d.need(abs(angle) <= 1, 'reduced angle')
        sine = sine_term = angle
        cosine = cosine_term = F(1)
        for k in range(1, self.internal):
            sine_term = real_round(-sine_term*angle*angle/((2*k)*(2*k+1)), self.internal)
            cosine_term = real_round(-cosine_term*angle*angle/((2*k-1)*(2*k)), self.internal)
            sine += sine_term
            cosine += cosine_term
            self.meter.phase_terms += 2
            self.meter.phase_products += 4
            self.meter.phase_divisions += 2
        tangent = real_round(sine/(1+cosine), self.internal)
        self.meter.phase_divisions += 1
        tangent = real_round(tangent, self.bits+8)
        sine = real_round(sine, self.bits+8)
        d.need(abs(tangent) <= F(1, 2) and abs(sine) <= 1, 'bounded phase shears')
        return quadrant % 4, tangent, sine


def quarter_turn(value, quadrant):
    real, imag = value
    if quadrant == 0:
        return value
    if quadrant == 1:
        return -imag, real
    if quadrant == 2:
        return -real, -imag
    return imag, -real


def observe_phase(value, meter):
    if meter is not None:
        meter.phase_peak_l1 = max(meter.phase_peak_l1, abs(value[0])+abs(value[1]))


def rotate(value, coefficients, bits, inverse=False, meter=None):
    """Apply three grid shears. The inverse uses the reverse instruction order."""
    quadrant, tangent, sine = coefficients
    observe_phase(value, meter)
    if inverse:
        real, imag = quarter_turn(value, (-quadrant) % 4)
        real += real_round(tangent*imag, bits)
        observe_phase((real, imag), meter)
        imag -= real_round(sine*real, bits)
        observe_phase((real, imag), meter)
        real += real_round(tangent*imag, bits)
        observe_phase((real, imag), meter)
        result = real, imag
    else:
        real, imag = value
        real -= real_round(tangent*imag, bits)
        observe_phase((real, imag), meter)
        imag += real_round(sine*real, bits)
        observe_phase((real, imag), meter)
        real -= real_round(tangent*imag, bits)
        observe_phase((real, imag), meter)
        result = quarter_turn((real, imag), quadrant)
    if meter is not None:
        meter.phase_products += 3
    return result


def phase_pass(data, phase, inverse):
    """Scan one array. Use quadratic finite differences and no phase table."""
    meter = phase.meter
    before = meter.tape_moves
    residue = 0
    difference = phase.numerator
    for i in range(len(data)):
        coefficients = phase.coefficients(residue)
        meter.access(data, i)
        value = rotate(data[i], coefficients, phase.bits, inverse, meter)
        meter.access(data, i, True)
        data[i] = value
        residue = (residue+difference) % phase.modulus
        difference = (difference+2*phase.numerator) % phase.modulus
        meter.phase_recurrence_steps += 1
    meter.phase_passes += 1
    meter.phase_record_moves += meter.tape_moves-before


def _validate_arrays(arrays, bits, meter):
    d.need(type(bits) is int and bits >= 2, 'working precision')
    d.need(arrays and len(arrays[0]) > 0, 'nonempty arrays')
    d.need(len({id(a) for a in arrays}) == len(arrays), 'distinct arrays')
    length = len(arrays[0])
    d.need(all(len(a) == length for a in arrays), 'equal array lengths')
    bound = F(0)
    for data in arrays:
        for i in range(length):
            meter.access(data, i)
            meter.input_reads += 1
            value = data[i]
            d.need(isinstance(value, tuple) and len(value) == 2
                   and all(type(v) in (int, F) for v in value), 'rational complex data')
            d.need(d.rnd(value, bits) == value, 'fixed grid data')
            bound = max(bound, abs(value[0])+abs(value[1]))
    meter.initial_bound = bound
    return bound


def _word_budget(bits, beta, length, stride, base_error, operator_norm, bound):
    d.need(d.admitted(beta, bits, d.depth(length, stride)), 'inherited precision admission')
    unit = F(1, 1 << bits)
    d.need(3*base_error*unit <= 1, 'conjugation precision admission')
    return 32*(1+operator_norm+base_error)*(bound+1)*unit


def _phase_descriptor(numerator, modulus):
    d.need(type(numerator) is int and type(modulus) is int and modulus > 0,
           'integer phase descriptor')


def _coefficient(value):
    return isinstance(value, tuple) and len(value) == 2 and all(type(v) in (int, F) for v in value)


def lift(x, y, b, beta, bits, stride, numerator, modulus,
         sign=1, multiplier=d.ONE, shift=0):
    """Add D times the pinned cyclic inverse times D inverse to a dirty target."""
    _phase_descriptor(numerator, modulus)
    d.need(type(stride) is int and type(shift) is int
           and type(sign) is int and sign in (-1, 1), 'integer stride and sign')
    d.need(type(beta) in (int, F) and 0 < beta <= F(1, 2), 'stable margin')
    d.need(_coefficient(b) and d.norm2(b) <= (1-beta)**2, 'stable coefficient')
    d.need(_coefficient(multiplier), 'constant multiplier')
    d.need(len(x) > 0 and shift % len(x) in (0, stride % len(x)), 'supported output shift')
    meter = Meter()
    meter.layout = {id(x): (0, 0), id(y): (1, 0)}
    bound = _validate_arrays((x, y), bits, meter)
    multiplier_bound = max(F(1), abs(multiplier[0])+abs(multiplier[1]))
    base_error = 68*multiplier_bound/beta**5
    operator_norm = multiplier_bound/beta
    meter.error_bound = _word_budget(bits, beta, len(x), stride, base_error, operator_norm, bound)
    phase = Phase.prepare(numerator, modulus, bits, meter)
    phase_pass(x, phase, True)
    phase_pass(y, phase, True)
    meter.rewind()
    d.lift(x, y, b, beta, bits, stride, sign, multiplier, shift, meter)
    phase_pass(y, phase, False)
    phase_pass(x, phase, False)
    meter.rewind()
    return meter


def compose(x, y, factors, scratch, tau, beta, bits, stride, numerator, modulus, sign=1):
    """Conjugate a complete PR985 factor word. Restore all borrowed arrays."""
    _phase_descriptor(numerator, modulus)
    d.need(type(sign) is int and sign in (-1, 1) and type(stride) is int, 'integer stride and sign')
    d.need(type(beta) in (int, F) and 0 < beta <= F(1, 2), 'stable margin')
    d.need(factors and len(scratch) == (len(factors)-1).bit_length(), 'exact borrowed-array budget')
    d.need(_coefficient(tau) and d.norm2(tau) == 1, 'unit gauge')
    scale_bound = F(1)
    for factor in factors:
        d.need(isinstance(factor, tuple) and len(factor) == 3, 'factor descriptor')
        inside, b, scale = factor
        d.need(type(inside) is bool and _coefficient(b) and d.norm2(b) <= (1-beta)**2
               and type(scale) in (int, F), 'stable factor descriptor')
        scale_bound = max(scale_bound, abs(scale))
    scratch = list(scratch)
    arrays = [x, y]+scratch
    meter = Meter()
    if scratch:
        meter.layout = {id(a): (0, i*len(x)) for i, a in enumerate(arrays[:-1])}
        meter.layout[id(scratch[-1])] = (1, 0)
    else:
        meter.layout = {id(x): (0, 0), id(y): (1, 0)}
    bound = _validate_arrays(arrays, bits, meter)
    calls = d.leaf_calls(len(factors))
    growth = 2+scale_bound/beta
    base_error = calls*68*(scale_bound+1)/beta**5*growth**(calls-1)
    operator_norm = growth**calls
    meter.error_bound = _word_budget(bits, beta, len(x), stride, base_error, operator_norm, bound)
    phase = Phase.prepare(numerator, modulus, bits, meter)
    phase_pass(x, phase, True)
    phase_pass(y, phase, True)
    meter.rewind()
    d.compose(x, y, factors, scratch, tau, beta, bits, stride, sign, meter)
    phase_pass(y, phase, False)
    phase_pass(x, phase, False)
    meter.rewind()
    return meter


def working_bits(target_bits, incoming_bits, bound, beta, length, stride,
                 multiplier_bound=1, count=1, scale_bound=None):
    """Choose a conservative precision for the complete conjugated word."""
    d.need(type(target_bits) is int and target_bits >= 0
           and type(incoming_bits) is int and incoming_bits >= 0
           and type(bound) in (int, F) and type(beta) in (int, F)
           and bound >= 0 and 0 < beta <= F(1, 2)
           and type(length) is int and length > 0 and type(stride) is int
           and type(multiplier_bound) in (int, F) and multiplier_bound >= 1, 'working budget domain')
    if scale_bound is None:
        d.need(count == 1, 'leaf count')
        base_error = 68*multiplier_bound/beta**5
        operator_norm = multiplier_bound/beta
    else:
        d.need(type(scale_bound) in (int, F) and scale_bound >= 1, 'factor scale bound')
        calls = d.leaf_calls(count)
        growth = 2+F(scale_bound)/beta
        base_error = calls*68*(scale_bound+1)/beta**5*growth**(calls-1)
        operator_norm = growth**calls
    return max(2, incoming_bits,
               target_bits+1+d.ceil_log2(32*(1+operator_norm+base_error)*(bound+1)),
               d.ceil_log2(3*base_error),
               d.ceil_log2(48*(d.depth(length, stride)+1)/beta**3))
