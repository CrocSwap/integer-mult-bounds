"""Use the phase stream around the pinned dirty-array word."""
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys

_SPEC = importlib.util.spec_from_file_location(
    'dirty_fast_phase_stream', Path(__file__).resolve().parent/'phase_stream.py')
stream = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = stream
_SPEC.loader.exec_module(stream)
d = stream.d
Meter, Phase, phase_pass = stream.Meter, stream.Phase, stream.phase_pass


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
    phase = Phase.prepare(numerator, modulus, bits, meter, len(x))
    phase_pass(x, phase, True)
    phase_pass(y, phase, True)
    meter.rewind()
    d.lift(x, y, b, beta, bits, stride, sign, multiplier, shift, meter)
    phase_pass(y, phase, False)
    phase_pass(x, phase, False)
    meter.rewind()
    phase.clear()
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
    phase = Phase.prepare(numerator, modulus, bits, meter, len(x))
    phase_pass(x, phase, True)
    phase_pass(y, phase, True)
    meter.rewind()
    d.compose(x, y, factors, scratch, tau, beta, bits, stride, sign, meter)
    phase_pass(y, phase, False)
    phase_pass(x, phase, False)
    meter.rewind()
    phase.clear()
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
