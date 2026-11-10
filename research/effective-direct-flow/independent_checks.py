#!/usr/bin/env python3
"""Independent rational controls for the new interval arithmetic implementation.

This exercises verify.py's implementation but computes expected ranges with
fractions.Fraction, without using its grid arithmetic. The finite controls do
not replace the written proofs of directed rounding or the analytic theorem.

Prepared for @alephnan with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import importlib.util


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_implementation():
    path = Path(__file__).resolve().with_name('verify.py')
    spec = importlib.util.spec_from_file_location('effective_interval_under_test', path)
    require(spec is not None and spec.loader is not None, 'cannot load interval implementation')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    implementation = load_implementation()
    Box = implementation.Box

    # Non-dyadic endpoints force outward rounding. The deterministic stride
    # keeps a small fixture containing positive, negative, crossing-zero and
    # singleton intervals; the expected case counts are explicit below.
    values = sorted({Fraction(n, d) for n in range(-5, 6) for d in (1, 3, 7)})
    intervals = [(a, b) for a, b in product(values, repeat=2) if a <= b][::7]
    require(len(intervals) == 63, 'interval fixture changed')
    require(any(a < b < 0 for a, b in intervals), 'missing negative interval')
    require(any(0 < a < b for a, b in intervals), 'missing positive interval')
    require(any(a < 0 < b for a, b in intervals), 'missing crossing interval')
    require(any(a == b for a, b in intervals), 'missing singleton interval')

    pairs = divisions = zero_rejections = 0
    for a, b in intervals:
        left = Box(a, b)
        require(left.lo <= a <= b <= left.hi, 'constructor rounded inward')
        for c, d in intervals:
            right = Box(c, d)
            corners = (a*c, a*d, b*c, b*d)
            result = left*right
            require(result.lo <= min(corners) <= max(corners) <= result.hi,
                    'product excludes an exact rational corner')

            if c*d > 0:
                corners = (a/c, a/d, b/c, b/d)
                result = left/right
                require(result.lo <= min(corners) <= max(corners) <= result.hi,
                        'quotient excludes an exact rational corner')
                divisions += 1
            else:
                try:
                    left/right
                except ValueError:
                    zero_rejections += 1
                else:
                    raise ValueError('division by interval containing zero accepted')
            pairs += 1

    require(pairs == 3969, 'pair coverage changed')
    require(divisions + zero_rejections == pairs, 'division partition incomplete')

    # This tests ceil(a/b) for both denominator signs independently of the
    # implementation's formula. The characterizing inequalities are exact.
    ceilings = 0
    denominators = list(range(-9, 0)) + list(range(1, 10))
    for numerator, denominator in product(range(-17, 18), denominators):
        exact = Fraction(numerator, denominator)
        rounded = implementation.ceiling(numerator, denominator)
        require(type(rounded) is int and rounded-1 < exact <= rounded,
                'signed ceiling violates its defining inequalities')
        ceilings += 1
    require(ceilings == 630, 'ceiling coverage changed')

    print('PASS_INDEPENDENT_INTERVAL_CONTROLS '
          f'interval_pairs={pairs} valid_divisions={divisions} '
          f'zero_interval_rejections={zero_rejections} signed_ceilings={ceilings}')


if __name__ == '__main__':
    run()
