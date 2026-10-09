"""Exact unit-magnitude splitting of fixed rational readout shears.

The selected PR117 DAG has numerator magnitudes at most 55 over 42. Two
pieces suffice; audit.py checks this bound on every expanded coefficient.
A second piece uses the same frame, so adds scalar work and no rank child.
"""
DENOMINATOR = 42
MAX_PIECES = 2

def validate_pieces(numerator, pieces):
    assert len(pieces) <= MAX_PIECES, 'Unpaid readout pieces'
    assert all(0 < abs(x) <= DENOMINATOR for x in pieces), 'Non-unit readout shear'
    assert sum(pieces) == numerator, 'Readout coefficient changed'
    return len(pieces)

def split_numerator(numerator):
    assert isinstance(numerator, int)
    sign = -1 if numerator < 0 else 1
    whole, remainder = divmod(abs(numerator), DENOMINATOR)
    assert whole + bool(remainder) <= MAX_PIECES, 'Unpaid readout pieces'
    pieces = (sign * DENOMINATOR,) * whole + ((sign * remainder,) if remainder else ())
    validate_pieces(numerator, pieces)
    return pieces
