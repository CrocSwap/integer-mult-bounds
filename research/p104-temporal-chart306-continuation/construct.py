"""Apply the authenticated causal split and retain the fixed-tape scalar contract."""
from fractions import Fraction
from temporal_construct import construct as split
from source import need


def scalar_width(word):
    widths = [abs(Fraction(event[-2]).numerator).bit_length()
              for event in word['program'] if event[0] in ('ADD', 'COPY', 'SCALE')]
    width = max(widths)
    need(width <= 24, 'Existing fixed-tape 24-bit scalar numerator limit')
    return dict(count=len(widths), maximum_bits=width, at_limit=widths.count(24))


def construct(word, hit, paths):
    candidate = split(word, hit, paths)
    scalar_width(candidate)
    return candidate
