#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify a signed invoice cost at one exact rational power, using integer bounds.

Usage: evaluate_recursive_power.py OLD.json NEW.json --exponent 0.9969
See docs/research/recursive-power-comparison.md for the interval argument.
Prepared for aliromman with OpenAI Codex assistance. The invoice schema and
signed accounting retain the compare_recursive_invoices predecessor credits.
"""
import argparse
from fractions import Fraction as Q
import json
import re
from math import isqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import compare_invoices, load_invoice, require, MAX_RANK
finally:
    sys.path.pop(0)


def parse_exponent(text):
    require(isinstance(text, str) and len(text) <= 128, 'exponent needs at most 128 characters')
    require(re.fullmatch(r'[+-]?(?:[0-9]+(?:/[0-9]+)?|[0-9]*\.[0-9]+)', text) is not None,
            'use a fraction or decimal without scientific notation')
    exponent = Q(text)
    require(0 < exponent < 1, 'exponent must satisfy 0 < t < 1')
    return exponent


def power_bounds(rank, exponent, bits=128):
    """Enclose rank**exponent by directed integer square roots and products."""
    require(type(rank) is int and 1 <= rank <= MAX_RANK, 'rank is outside 1..10^9')
    require(isinstance(exponent, Q) and 0 < exponent < 1, 'need an exact rational 0 < t < 1')
    require(type(bits) is int and 16 <= bits <= 256, 'bits must be an integer in 16..256')
    scale = 1 << bits
    digits, remainder = divmod(exponent.numerator * scale, exponent.denominator)
    lower = upper = scale
    root_lower = root_upper = rank * scale
    for shift in range(bits - 1, -1, -1):
        root_lower = isqrt(root_lower * scale)
        radicand = root_upper * scale
        root_upper = isqrt(radicand)
        root_upper += root_upper * root_upper < radicand
        if digits & (1 << shift):
            lower = lower * root_lower // scale
            upper = (upper * root_upper + scale - 1) // scale
    if remainder:
        upper = (upper * root_upper + scale - 1) // scale
    return Q(lower, scale), Q(upper, scale)


def evaluate(old, new, exponent, bits=128):
    report = compare_invoices(old, new)
    require(isinstance(exponent, Q) and 0 < exponent < 1, 'need an exact rational 0 < t < 1')
    require(type(bits) is int and 16 <= bits <= 256, 'bits must be an integer in 16..256')
    delta = report['signed_net_delta']
    require(len(delta) <= 512, 'power comparison supports at most 512 nonzero ranks')
    lower = upper = Q(0)
    terms = []
    for rank, count in delta.items():
        lo, hi = power_bounds(int(rank), exponent, bits)
        lower += count * (lo if count > 0 else hi)
        upper += count * (hi if count > 0 else lo)
        terms.append({'rank': int(rank), 'signed_count': count, 'power_lower': str(lo), 'power_upper': str(hi)})
    sign = ('new_cost_lower' if upper < 0 else 'new_cost_higher' if lower > 0
            else 'equal' if lower == upper == 0 else 'unresolved')
    return {'schema': 'integer-mult-recursive-power-comparison/v1', 'contract': report['contract'],
            'exponent': str(exponent), 'bits': bits, 'classification': sign,
            'new_minus_old': {'lower': str(lower), 'upper': str(upper)}, 'terms': terms,
            'quantity': report['quantity'],
            'scope': 'Exact arithmetic on declared invoices at this exponent only. No circuit, ownership, '
                     'compiler, applicability or kappa claim is verified. Unresolved is not equality.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old'); parser.add_argument('new')
    parser.add_argument('--exponent', required=True, help='exact fraction or decimal t in r^t')
    parser.add_argument('--bits', type=int, default=128, help='dyadic grid bits, 16..256; default 128')
    args = parser.parse_args(argv)
    try:
        exponent = parse_exponent(args.exponent)
        old, old_pin = load_invoice(args.old); new, new_pin = load_invoice(args.new)
        report = evaluate(old, new, exponent, args.bits)
        report['inputs'] = {'old': old_pin, 'new': new_pin}
    except (OSError, ValueError, TypeError, RecursionError, ZeroDivisionError) as exc:
        print(json.dumps({'status': 'INVALID_POWER_COMPARISON', 'error': str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
