"""Build two accretive square-root calls from nonzero Gaussian-rational multipliers."""

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

from root_gate_plan import certify_accretivity


@dataclass(frozen=True)
class CartesianRoot:
    column: tuple[tuple[Fraction, Fraction], ...]
    compensation: tuple[Fraction, Fraction]
    margin: Fraction
    root_error: Fraction
    multiplier_error: Fraction


def sqrt_floor(value, bits):
    """Return floor(2^bits sqrt(value)) / 2^bits for a nonnegative rational."""
    scaled_square = (value.numerator << (2 * bits)) // value.denominator
    return Fraction(isqrt(scaled_square), 1 << bits)


def separated(cut, z, minimum_chord):
    """Test the chord distance from an exact unit cut to the phase of z."""
    dot = (z * cut.conjugate()).re
    threshold = 1 - minimum_chord**2 / 2
    return dot <= 0 or dot**2 <= threshold**2 * z.norm2()


def cartesian_root(compiler, symbols, target_bits):
    """Generate the column, exact scalar correction and error in the cyclic multiplier."""
    C, ceil_log2 = compiler.exact.C, compiler.exact.ceil_log2
    values = [C(re, im) for re, im in symbols]
    if type(target_bits) is not int or target_bits < 1 or not values:
        raise ValueError("A nonempty spectrum and positive target precision are required")
    r = len(values)
    smallest = min(max(abs(z.re), abs(z.im)) for z in values)
    if smallest == 0:
        raise ValueError("A cyclic multiplier is zero")
    amplitude = max(Fraction(1), max(abs(z.re) + abs(z.im) for z in values))
    sector = min(Fraction(1), smallest) / (6*r)
    tolerance = min(Fraction(1, 1 << target_bits) / (2*amplitude + 1), sector/4) / (4*r)
    phase_bits = max(ceil_log2(32*r), ceil_log2(amplitude/tolerance))
    phases = compiler.engine.Phases(phase_bits, compiler.raw[compiler.generator.ORACLE])
    chord = Fraction(1, 3*r)
    for j in range(4*r):
        cut = phases.phase(4*r, j)
        if all(separated(cut, z, chord) for z in values):
            rotation = -cut.conjugate()
            break
    else:
        raise ArithmeticError("No separated unit cut")

    work_bits = ceil_log2(32 * amplitude**2 / (tolerance * sector**3))
    roots = []
    for z in values:
        w = rotation * z
        norm_lower = sqrt_floor(w.norm2(), work_bits)
        real = sqrt_floor(max(Fraction(0), (norm_lower + w.re)/2), work_bits)
        if real < sector/2:
            raise ArithmeticError("Lost the certified real square-root margin")
        imag = compiler.exact.round_q(w.im/(2*real), work_bits)
        root = C(real, imag)
        if (root*root - w).norm2() > (sector*tolerance)**2:
            raise ArithmeticError("Square-root residual exceeded its bound")
        roots.append(root)

    column_bits = ceil_log2(1/tolerance)
    column = []
    for j in range(r):
        total = sum((root * phases.phase(r, j*k) for k, root in enumerate(roots)), C())
        column.append(compiler.exact.rounded(total/r, column_bits))
    margin = sector/2
    certify_accretivity(column, margin)
    root_error = 3*r*tolerance
    correction = rotation.conjugate()
    return CartesianRoot(tuple((z.re, z.im) for z in column), (correction.re, correction.im), margin,
                         root_error, (2*amplitude+root_error)*root_error)
