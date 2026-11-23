"""Source-bound sufficient external precision for PR7849's Fourier word.

This selector assumes the exact source contracts in PROOF-DRAFT.md. It does not
estimate the minimum precision required by a numerical execution.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    public_bits: int
    axes: int
    address_bits: int
    interval_exponent: int
    local_error_exponent: int
    stage_bound: int
    envelope_coefficient: int
    fractional_bits: int


def precision_budget(public_bits: int, side_widths: tuple[int, ...]) -> Budget:
    if type(public_bits) is not int or public_bits < 1:
        raise ValueError("Public precision must be a positive integer")
    if not side_widths or any(type(w) is not int or w < 1 for w in side_widths):
        raise ValueError("Supply at least one positive binary side width")
    d = len(side_widths)
    length = sum(side_widths)
    interval = (1257 * length + 1) // 2 + 2154 * d
    local = 104 * length + 438 * d
    stages = 20000 * (d + 1) * (max(side_widths) + 2) ** 6
    coefficient = 4 * stages * (d + 1) ** 2 + d + 1
    bits = 4 * public_bits + local + 2 * interval + coefficient.bit_length()
    return Budget(public_bits, d, length, interval, local, stages, coefficient, bits)


def production_precision(public_bits: int, side_widths: tuple[int, ...]) -> int:
    """Return the fractional bits certified by the explicit source envelope."""
    return precision_budget(public_bits, side_widths).fractional_bits
