"""Check nonzero helper preservation and the stated error margins."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    lanes = args.package / 'frozen/work/centre-encoding-campaign-20261014/lanes'
    payload = gzip.decompress((lanes / 'history-encoding/FULL-MODE-PROGRAMS.json.gz').read_bytes())
    require(sha256(payload).hexdigest() == 'f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205', 'Raw word pin')
    events = json.loads(payload)['backward']
    matrix = json.loads((lanes / 'circuit-interface/INTERFACE.json').read_text())['R']
    centres = [92, 57, 81, 224, 11, 240, 9, 256]
    modes = [225, 226, 229, 232, 241, 242, 257, 258]

    def run(mode, preserve):
        state = [Q(0) for _ in range(704)]
        state[modes[mode]] = Q(1)
        for index, event in enumerate(events):
            if index == 12995:
                require([state[field] for field in centres] == [Q(k == mode) for k in range(8)],
                        'The centre holds the nonzero helper baseline.')
                for k, field in enumerate(centres):
                    state[field] = Q(preserve and k == mode)
            elif 12996 <= index <= 13003:
                continue
            elif event[0] == 'scalar':
                gate = event[1]
                target = gate[1][1]
                if gate[0] == 'add':
                    state[target] += Q(gate[3], gate[4]) * state[gate[2][1]]
                elif gate[0] == 'scale':
                    state[target] *= Q(gate[2], gate[3])
                else:
                    raise ValueError('Unknown scalar operation.')
        return state

    for mode in range(8):
        expected = [Q(j == modes[mode]) for j in range(704)]
        require(run(mode, True) == expected, 'The nonzero helper input must return.')
        wrong = run(mode, False)
        require(wrong[modes[mode]] == 0, 'The false zero reset loses the helper input.')
        require(wrong[:112] == [-Q(matrix[mode].get(str(j), 0)) for j in range(112)],
                'The false zero reset also changes the data by minus R transpose.')
        require(wrong != expected, 'A zero helper assumption must fail.')

    # Coordinates are t, B*e, H, G, and the constant term. Set g=t+B*e.
    def plus(*terms):
        return [sum(term[k] for term in terms) for k in range(5)]

    def times(coefficient, term):
        return [coefficient * item for item in term]

    t, be, h, g, one = [[int(j == k) for j in range(5)] for k in range(5)]
    grid = plus(t, be)
    p = plus(times(2, be), times(2, h), times(4, g), times(32, one))
    coarse = plus(t, p, times(-18, one), times(-2, g), times(-1, grid), times(-1, h), times(-4, one))
    fine = plus(times(2, t), p, times(-18, one), times(-3, g), times(-2, grid), times(-2, h), times(-8, one))
    suffix = plus(t, p, times(-18, one), times(-3, g), times(-1, grid), times(-2, h), times(-4, one))
    require(coarse == [0, 1, 1, 2, 10] and fine == [0, 0, 0, 1, 6] and suffix == [0, 1, 0, 1, 10],
            'The three margins are exact polynomial identities.')
    quantum = Q(1, 2**24)
    exact_component = quantum / 2
    nearest = quantum
    require(abs(nearest - exact_component) / quantum == Q(1, 2),
            'Exact child computation does not imply a small relative parent return error.')
    report = {'status': 'PASS_ADDITIONAL_INDEPENDENT_REVIEW_CONTROLS',
              'helper_modes_checked': 8, 'false_zero_helper_reset_rejected': True,
              'zero_reset_data_error': '-R^T times the lost helper input',
              'symbolic_margin_coordinates': ['t', 'B*e', 'H', 'G', 'constant'],
              'coarse_margin': coarse, 'fine_margin': fine, 'suffix_margin': suffix,
              'relative_only_parent_return_counterexample': '1/2',
              'scope': 'Independent scalar cut controls and symbolic margin identities. Native frames remain inherited.'}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
