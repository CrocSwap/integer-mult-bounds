#!/usr/bin/env python3
"""Source-bound local QQ16 caller precision; ywz65 with OpenAI Codex assistance."""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import measure
import phase
import sources


def typed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def experiment():
    old = sources.load()
    retained, word = old.calculate()
    phase.need(typed(retained) == typed(json.loads((HERE/'vendor/pr2540/RESULT.json').read_text())),
               'retained complete receipt mismatch')
    phase.need(typed(word) == typed(json.loads((HERE/'vendor/pr2540/WORD.json').read_text())),
               'retained literal word mismatch')
    R, records, _ = old.N.load_sources()
    expected, _ = old.logical_reference()
    result = measure.measure(old, word, R, records, expected)
    phase.need(result['fractional_reserve'] == 7 and result['amplification'] == '2448'
               and result['magnitude_guard_bits'] == 12, 'declared caller bounds')
    witness = result['debt_witness']
    values = [Q(witness[k]) for k in ('physical_real', 'physical_imag')]
    phase.need(all((v*128).denominator == 1 for v in values), 'seven-bit reserve is sufficient for witness')
    phase.need(any((v*64).denominator != 1 for v in values), 'six-bit rejection control ineffective')
    phase.need(2048 < Q(result['amplification']) <= 4096, 'eleven/twelve guard-bit boundary')
    # C1 real/imaginary box gain is two, although its complex Euclidean norm is one.
    a, edges = phase.polynomial(((1, 1),), 1)
    z = [phase.gaussian(a, edges, x) for x in range(2)]
    phase.need(sum(abs(x)+abs(y) for x, y in z) == 2, 'complex-unitary/real-box distinction')
    # Coefficients sharing a source/map must be combined, including cancellation.
    phase.need(measure.debt(Q(4)) == -2 and Q(1, 4)-Q(1, 4) == 0,
               'numerator cancellation control')
    # Eight independent C1 factors have final Gaussian denominator16, not256.
    a, edges = phase.polynomial(tuple((1 << j, 1) for j in range(8)), 8)
    c8 = phase.witness(a, edges)
    phase.need(c8['rank'] == 8 and c8['bits'] == 4, 'rank-eight child boundary debt')
    result.update({'retained_controls': len(retained['controls']), 'unchanged_invoice': retained['invoice'],
                   'controls': {'six_fraction_bits_reject_single_term': True,
                                'eleven_magnitude_bits_below_triangle_envelope': True,
                                'real_box_unitarity_control': 2, 'scalar_v2_numerator': -2,
                                'rank_eight_boundary_fraction_bits': 4},
                   'scope': 'All declared caller-event boundaries, exact atomic native/cover semantics, 240 independent temporal-source relaxation; sufficient for actual F0/B1 trajectories. No child-internal precision or new supplier claim.'})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='create an absent receipt only')
    parser.add_argument('--authenticate-only', action='store_true')
    args = parser.parse_args()
    if args.authenticate_only:
        sources.authenticate()
        print('PASS_QQ16_CALLER_SOURCE_PINS')
        return
    result = experiment()
    receipt = HERE/'RESULT.json'
    if args.write:
        with receipt.open('x', encoding='utf-8', newline='\n') as out:
            out.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        phase.need(typed(json.loads(receipt.read_text())) == typed(result), 'typed receipt mismatch')
    print('PASS_QQ16_CALLER_GRID all_lambda_fraction=4L+3 all_lambda_magnitude=4L+8 '
          'lambda1_amplification=2448 events=2463')


if __name__ == '__main__':
    main()
