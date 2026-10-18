#!/usr/bin/env python3
"""Replay the finite H6 audit; no supplier or theorem admission."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(relative):
    return json.loads((HERE / relative).read_text())


def step(relative, *args):
    command = [sys.executable, '-I', '-O', '-B', str(HERE / relative), *args]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    require(result.returncode == 0,
            relative + ' failed:\n' + result.stdout + result.stderr)
    print(relative + ': PASS', flush=True)


def summaries():
    invoice = read('invoice/RESULT.json')
    expected = {'pr890_rounded': [80558, 89683, 80753],
                'pr890_checkpoint': [80558, 89683, 80753],
                'pr1424_pending_title': [79617, 88409, 79399],
                'current_selected': [79880, 88765, 79778]}
    for target in invoice['targets']:
        require([r['max_helpers'] for r in target['rows']] == expected[target['name']],
                'fixed invoice boundaries')
        for row in target['rows']:
            require(row['boundary_slack_scaled_1e24'][0] > 0
                    and row['next_slack_scaled_1e24'][1] < 0,
                    'strict adjacent invoice signs')
    walsh = read('walsh/results.json')
    histogram = {int(k): v for k, v in walsh['pairing_histogram'].items()}
    require(sum(histogram.values()) == walsh['ordered_pairs_checked'] == 30960**2,
            'complete ordered-pair coverage')
    require(sum(v for t, v in histogram.items() if t % 2)
            == walsh['compensation_nonzeros'] == 480337920, 'compensation support')
    exception = histogram.get(-3, 0) + histogram.get(3, 0)
    require(exception == walsh['exceptional_abs_t_3_pairs'] == 3363840,
            'exception summary agrees with exhaustive histogram')
    require(Fraction(walsh['exceptional_share_of_nonzeros_exact'])
            == Fraction(exception, walsh['compensation_nonzeros']), 'exception ratio')
    require(sum(n * count for n, count in walsh['label_multiplicity_histogram']) == 30960,
            'label multiplicities cover every port')
    require(walsh['binary_rank'] == 16 and walsh['root_gram_determinant'] == 1,
            'unimodular binary-rank certificate')
    frames = read('helper/FRAME-SUPPORT.json')
    require(len(frames['coordinate_supports']) == 16
            and all(x['binary_support_span'] == 17 for x in frames['coordinate_supports']),
            'scoped character support evidence')
    require(frames['restricted_label_positive_control']['common_target_cap_dimension'] == 16,
            'separate bucket positive control')
    spectral = read('spectral/results.json')
    require(spectral['corrected_ordered_off_diagonal_blocks'] == 14280
            and spectral['diagonal_blocks'] == 120, 'canonical block count')
    require(spectral['off_diagonal_compensation_sign_fixture']['correct_I_minus_K']
            == '-5/16', 'compensation block sign')
    trace2 = sum(Fraction(count * (t**3 - 4*t)**2, 48**2)
                 for t, count in histogram.items())
    require(trace2 == Fraction(spectral['trace_square_from_exhaustive_pairing_histogram'])
            == 2222640, 'independent spectrum/histogram consistency')
    require(spectral['kernel_rank'] == 816
            and spectral['compensation_rank_over_real_numbers'] == 30960,
            'spectral scope and rank')
    lifecycle = read('lifecycle/RESULT.json')
    require(lifecycle['actual_compensation_submatrix']['total_local_rank_mass'] == 81,
            'actual finite compensation lifecycle profile')
    return {'ports': 30960, 'ordered_pairs': 30960**2,
            'selected_helper_limits': expected['current_selected'],
            'corrected_ordered_off_diagonal_blocks': 14280, 'no_new_kappa': True}


def main():
    for name, digest in read('SOURCES.json')['sha256'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest,
                'frozen source pin: ' + name)
    step('provenance/check.py')
    step('invoice/verify.py')
    step('walsh/audit.py', '--output', str(HERE/'walsh/results.json'))
    step('helper/frame_support.py')
    step('review/walsh/replay.py')
    step('helper/charged_screen.py')
    step('review/charged/replay.py')
    step('spectral/audit.py')
    step('lifecycle/probe.py')
    summary = summaries()
    (HERE/'SUMMARY.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    print('PASS_H6_INDEPENDENT_AUDIT pairs=958521600 selected_limits=79880,88765,79778 no_new_kappa')


if __name__ == '__main__':
    main()
