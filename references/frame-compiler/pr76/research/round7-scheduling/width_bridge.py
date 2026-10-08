"""Refresh derived role-logarithm/product-row constants after a width change.

Formulas are inherited from PR48/PR65 balanced_assembly.validate_bridge.
Dominik Scholz with substantial OpenAI GPT-6 Astra assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q


def bridge_for_width(inherited, width):
    assert type(width) is int and width > 0
    bridge = deepcopy(inherited)
    bridge['bit']['W'] = width
    bridge['bit']['wire_bits'] = width.bit_length()
    coefficient = sum(
        bridge[axis]['halving_degree'] * bridge[axis]['wire_bits']
        for axis in ('bit', 'complex')
    )
    bridge['rows']['coefficient'] = coefficient
    bridge['rows']['degree_gap'] = Q(bridge['rows']['degree']) - Q(51, 25) * coefficient
    assert bridge['rows']['degree_gap'] > 0
    return bridge
