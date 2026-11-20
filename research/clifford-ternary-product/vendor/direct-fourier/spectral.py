"""Generate bounded circulant roots and the diagonals of a signed Fourier mean."""

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt


def centered(turn):
    """Represent a rational number of turns in (-1/2, 1/2]."""
    turn %= 1
    return turn if 2 * turn <= 1 else turn - 1


def phase_value(phases, turns):
    return phases.phase(turns.denominator, turns.numerator)


def cut_rotation(turns):
    """Put the negative real axis in the middle of a largest empty arc."""
    ordered = sorted(q % 1 for q in turns)
    ends = ordered[1:] + [ordered[0] + 1]
    gap, left = max((b-a, a) for a, b in zip(ordered, ends, strict=True))
    return (left + gap/2 - Fraction(1, 2)) % 1


def lower_sqrt(value, bits):
    scale = 1 << bits
    return Fraction(isqrt((value.numerator * scale**2) // value.denominator), scale)


@dataclass
class RootColumn:
    column: list
    rotation: Fraction
    accretivity: Fraction
    phase_bits: int


def polar_root(compiler, radii, turns, bits, phase_grid=None):
    """Generate one dyadic circulant for the two-pass factorization."""
    if not turns or len(radii) != len(turns) or bits < 1:
        raise ValueError("Expected one modulus and phase per frequency")
    if any(not isinstance(q, Fraction) for q in (*radii, *turns)) or min(radii) <= 0:
        raise ValueError("Expected positive rational moduli and rational phase turns")
    r = len(turns)
    condition = max(Fraction(1), max(radii), 1/min(radii))
    cap = -(-condition.numerator // condition.denominator)
    if phase_grid is None:
        rotation = cut_rotation(turns)
        gap_scale = r
    else:
        if phase_grid < 1 or any((phase_grid*q).denominator != 1 for q in turns):
            raise ValueError("The declared phase grid misses a frequency")
        rotation = Fraction(-1, 2*phase_grid) if phase_grid % 2 == 0 else Fraction(0)
        gap_scale = phase_grid
    b = bits + 4*max(r, gap_scale).bit_length() + 4*cap.bit_length() + 16
    phases = compiler.engine.Phases(b+4, compiler.raw[compiler.generator.ORACLE])
    angles = [centered(q-rotation)/2 for q in turns]
    magnitudes = [lower_sqrt(q, b) for q in radii]
    column = []
    for j in range(r):
        total = compiler.exact.C()
        for k, (radius, angle) in enumerate(zip(magnitudes, angles, strict=True)):
            phase = phase_value(phases, angle + Fraction(j*k, r))
            total += phase * radius
        q = compiler.exact.rounded(total/r, b)
        column.append((q.re, q.im))
    return RootColumn(column, rotation, Fraction(1, 2*max(2, gap_scale)*cap), b), phases


@dataclass
class Axis:
    size: int
    width: int
    entrance: tuple
    exit: tuple
    layers: list


def fourier_axis(compiler, r, t, direction, bits):
    """Compile the signed mean on r original positions and identity on the holes."""
    from root_gate_plan import compile_padded_root

    if r < 2 or t < r or t & (t-1) or direction not in (-1, 1):
        raise ValueError("Invalid cyclic order, dyadic container or Fourier sign")
    turns = [Fraction(direction*j*(j+r), 2*r) for j in range(r)]
    root, phases = polar_root(compiler, [Fraction(1)]*r, turns, bits, phase_grid=2*r)
    plan, _ = compile_padded_root(compiler, root.column, t, bits, radius=2*t,
                                  margin=root.accretivity)
    chirps = [phase_value(phases, q) for q in turns]
    gauss_mean = sum((z.conjugate() for z in chirps), compiler.exact.C()) / r
    compensation = phase_value(phases, root.rotation) * gauss_mean
    rounded = compiler.exact.rounded
    entrance = [rounded(z, root.phase_bits) for z in chirps]
    exit_diag = [rounded(compensation*z, root.phase_bits) for z in chirps]
    holes = [compiler.exact.C(1)] * (t-r)
    return Axis(r, t, tuple(entrance+holes), tuple(exit_diag+holes), plan)
