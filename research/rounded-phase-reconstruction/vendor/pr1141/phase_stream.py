"""Generate quadratic phases with reversible rounded state updates."""
from dataclasses import dataclass
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys


_SPEC = importlib.util.spec_from_file_location(
    'fast_phase_predecessor', Path(__file__).resolve().parent/'vendor/pr1038/chirp.py')
old = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = old
_SPEC.loader.exec_module(old)
d = old.d
real_round = old.real_round
rotate = old.rotate
quarter_turn = old.quarter_turn


@dataclass
class Meter(old.Meter):
    seed_terms: int = 0
    seed_products: int = 0
    seed_divisions: int = 0
    seed_cleanups: int = 0
    seed_peak_bits: int = 0
    stream_charts: int = 0
    stream_steps: int = 0
    stream_reverse_steps: int = 0
    stream_cleanups: int = 0
    preparation_cleanups: int = 0
    state_bits: int = 0
    state_peak_l1: F = F(0)


def _width(value, meter):
    value = F(value)
    meter.seed_peak_bits = max(meter.seed_peak_bits,
                              abs(value.numerator).bit_length(),
                              value.denominator.bit_length())


def _machin_add(total, denominator, weight, terms, meter, inverse=False):
    """Add an exact arctangent sum and clear its power register."""
    power = denominator
    if inverse:
        for _ in range(terms):
            power *= denominator*denominator
            meter.seed_products += 1
    indices = range(terms-1, -1, -1) if inverse else range(terms)
    for k in indices:
        if inverse:
            power //= denominator*denominator
            meter.seed_divisions += 1
        term = F(weight if k % 2 == 0 else -weight, (2*k+1)*power)
        total = total-term if inverse else total+term
        meter.seed_terms += 1
        meter.seed_products += 1
        meter.seed_divisions += 1
        _width(total, meter)
        _width(power, meter)
        if not inverse:
            power *= denominator*denominator
            meter.seed_products += 1
    if not inverse:
        for _ in range(terms):
            power //= denominator*denominator
            meter.seed_divisions += 1
    power -= denominator
    d.need(power == 0, 'Machin power cleanup')
    return total


def seed_coefficients(numerator, modulus, coefficient_bits, meter,
                      destination=(0, F(0), F(0)), inverse=False):
    """Add or remove seed coefficients and clear the exact series state."""
    sign = -1 if inverse else 1
    residue = numerator % modulus
    quadrant = (8*residue+modulus)//(2*modulus)
    remainder = 4*residue-quadrant*modulus
    if remainder == 0:
        meter.seed_cleanups += 1
        return destination[0]+sign*(quadrant % 4), destination[1], destination[2]
    precision = coefficient_bits+16
    pi_sum = _machin_add(F(0), 5, 16, precision, meter)
    pi_sum = _machin_add(pi_sum, 239, -4, precision, meter)
    pi_grid = real_round(pi_sum, precision)
    angle = real_round(pi_grid*remainder/(2*modulus), precision)
    meter.seed_products += 1
    meter.seed_divisions += 1
    d.need(abs(angle) < 1, 'seed reduced angle')
    sine = sine_term = angle
    cosine = cosine_term = F(1)
    if angle:
        squared = angle*angle
        meter.seed_products += 1
        for k in range(1, precision):
            sine_term = -sine_term*squared/(2*k*(2*k+1))
            cosine_term = -cosine_term*squared/((2*k-1)*2*k)
            sine += sine_term
            cosine += cosine_term
            meter.seed_terms += 2
            meter.seed_products += 2
            meter.seed_divisions += 2
            for value in (sine, cosine, sine_term, cosine_term):
                _width(value, meter)
    tangent = real_round(sine/(1+cosine), coefficient_bits)
    sine_output = real_round(sine, coefficient_bits)
    output = (destination[0]+sign*(quadrant % 4),
              destination[1]+sign*tangent, destination[2]+sign*sine_output)
    meter.seed_divisions += 1
    if angle:
        for k in range(precision-1, 0, -1):
            sine -= sine_term
            cosine -= cosine_term
            sine_term = -sine_term*(2*k*(2*k+1))/squared
            cosine_term = -cosine_term*((2*k-1)*2*k)/squared
            meter.seed_terms += 2
            meter.seed_products += 2
            meter.seed_divisions += 2
        squared -= angle*angle
        meter.seed_products += 1
        d.need(squared == 0, 'Taylor square cleanup')
    sine -= angle
    sine_term -= angle
    cosine -= 1
    cosine_term -= 1
    d.need(sine == sine_term == cosine == cosine_term == 0, 'Taylor cleanup')
    angle -= real_round(pi_grid*remainder/(2*modulus), precision)
    pi_grid -= real_round(pi_sum, precision)
    meter.seed_products += 1
    meter.seed_divisions += 1
    pi_sum = _machin_add(pi_sum, 239, -4, precision, meter, True)
    pi_sum = _machin_add(pi_sum, 5, 16, precision, meter, True)
    d.need(angle == pi_grid == pi_sum == 0, 'seed cleanup')
    d.need(abs(tangent) <= F(1, 2) and abs(sine_output) <= 1,
           'bounded seed coefficients')
    meter.seed_cleanups += 1
    return output


def chart(value, bits, meter, destination=(0, F(0), F(0)), inverse=False):
    """Add or remove chart coefficients without changing their source."""
    x, y = value
    if x >= abs(y):
        quadrant = 0
    elif y >= abs(x):
        quadrant = 1
    elif -x >= abs(y):
        quadrant = 2
    else:
        quadrant = 3
    cosine, sine = quarter_turn(value, (-quadrant) % 4)
    d.need(cosine >= abs(sine), 'phase chart domain')
    tangent = real_round(sine/(1+cosine), bits+8)
    sine = real_round(sine, bits+8)
    tangent = min(F(1, 2), max(-F(1, 2), tangent))
    sine = min(F(1), max(-F(1), sine))
    meter.phase_divisions += 1
    meter.stream_charts += 1
    sign = -1 if inverse else 1
    return (destination[0]+sign*quadrant, destination[1]+sign*tangent,
            destination[2]+sign*sine)


@dataclass
class State:
    phase: object
    value: tuple
    ratio: tuple
    index: int = 0

    def coefficients(self):
        d.need(0 <= self.index < self.phase.length, 'phase stream index')
        self.phase.meter.phase_evaluations += 1
        return chart(self.value, self.phase.bits, self.phase.meter)

    def erase_coefficients(self, coefficients):
        result = chart(self.value, self.phase.bits, self.phase.meter, coefficients, True)
        d.need(result == (0, 0, 0), 'emitted coefficient cleanup')
        return result

    def step(self, inverse=False):
        p = self.phase
        if inverse:
            d.need(self.index > 0, 'phase reverse index')
            self.ratio = rotate(self.ratio, p.omega, p.state_bits, True, p.meter)
            coefficients = chart(self.ratio, p.state_bits, p.meter)
            self.value = rotate(self.value, coefficients, p.state_bits, True, p.meter)
            coefficients = chart(self.ratio, p.state_bits, p.meter, coefficients, True)
            self.index -= 1
            p.meter.stream_reverse_steps += 1
        else:
            d.need(self.index < p.length, 'phase forward index')
            coefficients = chart(self.ratio, p.state_bits, p.meter)
            self.value = rotate(self.value, coefficients, p.state_bits, False, p.meter)
            coefficients = chart(self.ratio, p.state_bits, p.meter, coefficients, True)
            self.ratio = rotate(self.ratio, p.omega, p.state_bits, False, p.meter)
            self.index += 1
            p.meter.stream_steps += 1
        d.need(coefficients == (0, 0, 0), 'state coefficient cleanup')
        p.meter.state_peak_l1 = max(p.meter.state_peak_l1,
                                  abs(self.value[0])+abs(self.value[1]),
                                  abs(self.ratio[0])+abs(self.ratio[1]))

    def clear(self):
        """Reverse the state word and clear its two initial values."""
        d.need(self.phase.busy, 'open phase stream')
        while self.index:
            self.step(True)
        self.value = d.sub(self.value, d.ONE)
        self.ratio = d.sub(self.ratio, self.phase.seed)
        d.need(self.value == self.ratio == d.ZERO, 'phase state cleanup')
        self.phase.busy = False
        self.phase.meter.stream_cleanups += 1


@dataclass
class Phase:
    numerator: int
    modulus: int
    bits: int
    length: int
    state_bits: int
    seed: tuple
    omega: tuple
    meter: Meter
    active: bool = True
    busy: bool = False

    @classmethod
    def prepare(cls, numerator, modulus, bits, meter, length):
        d.need(type(numerator) is int and type(modulus) is int and modulus > 0,
               'integer phase descriptor')
        d.need(type(bits) is int and bits >= 2 and type(length) is int and length > 0,
               'phase stream domain')
        state_bits = bits+2*(length+1).bit_length()+20
        meter.state_bits = state_bits
        meter.coefficient_bits = bits+8
        meter.internal_bits = state_bits+24
        meter.descriptor_bits += abs(numerator).bit_length()+modulus.bit_length()+2
        a = numerator % modulus
        first = seed_coefficients(a, modulus, state_bits+8, meter)
        seed = rotate(d.ONE, first, state_bits, False, meter)
        first = seed_coefficients(a, modulus, state_bits+8, meter, first, True)
        d.need(first == (0, 0, 0), 'first seed coefficient cleanup')
        omega = seed_coefficients(2*a, modulus, state_bits+8, meter)
        return cls(a, modulus, bits, length, state_bits, seed, omega, meter)

    def start(self):
        d.need(self.active, 'active phase preparation')
        d.need(not self.busy, 'one open phase stream')
        self.busy = True
        return State(self, d.ONE, self.seed)

    def clear(self):
        """Recompute the two seeds and subtract them from their registers."""
        d.need(self.active, 'active phase preparation')
        d.need(not self.busy, 'phase stream must be clear')
        first = seed_coefficients(self.numerator, self.modulus, self.state_bits+8, self.meter)
        self.seed = rotate(self.seed, first, self.state_bits, True, self.meter)
        self.seed = d.sub(self.seed, d.ONE)
        first = seed_coefficients(self.numerator, self.modulus, self.state_bits+8,
                                  self.meter, first, True)
        d.need(first == (0, 0, 0), 'last seed coefficient cleanup')
        self.omega = seed_coefficients(2*self.numerator, self.modulus, self.state_bits+8,
                                      self.meter, self.omega, True)
        d.need(self.seed == d.ZERO and self.omega == (0, 0, 0), 'phase preparation cleanup')
        self.active = False
        self.meter.preparation_cleanups += 1


def phase_pass(data, phase, inverse):
    """Apply one data pass and then reverse its phase state."""
    d.need(len(data) == phase.length, 'phase data length')
    meter = phase.meter
    before = meter.tape_moves
    state = phase.start()
    for i in range(len(data)):
        coefficients = state.coefficients()
        meter.access(data, i)
        value = rotate(data[i], coefficients, phase.bits, inverse, meter)
        meter.access(data, i, True)
        data[i] = value
        coefficients = state.erase_coefficients(coefficients)
        state.step()
    state.clear()
    meter.phase_passes += 1
    meter.phase_record_moves += meter.tape_moves-before
