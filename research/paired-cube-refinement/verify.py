#!/usr/bin/env python3
"""Reconstruct the complete conditional successor certificate without writes.

Use --write only to author the certificate and its generated numerical report.
The search, frame checker, scalar checker and arithmetic remain separate.
"""
import argparse
import copy
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRAMES = ROOT / 'research/paired-cube-bit-descent'
sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
sys.path.insert(0, str(FRAMES))
sys.path.insert(0, str(HERE))

from arithmetic import certificate as arithmetic_certificate, js
from paid_moment import require
from plan_validation import validate_plan
from report import render


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def pins():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    require(manifest['prerequisite_commit'] ==
            '98c115b53742b6613ad630de4d493f37b0119da7', 'PR168 prerequisite')
    require(bool(manifest['files']), 'nonempty source closure')
    actual = {name: digest(ROOT / name) for name in manifest['files']}
    require(actual == manifest['files'], 'source closure drift')
    return digest(HERE / 'SOURCE.json'), actual


def build():
    from word import Candidate
    from prime_check import certificate as prime_certificate
    from formal_complex import certify as complex_certificate

    print('Checking the complete bit geometry and paid child ledger.', file=sys.stderr, flush=True)
    plan = json.loads((FRAMES / 'frames.json').read_text())
    original = Candidate()
    validate_plan(plan, len(original.ops))
    candidate = Candidate(plan=plan)
    candidate.exact_frames()
    row = candidate.row()
    original.exact_frames()
    baseline_row = original.row()
    require(row['W_per_vertex'] == baseline_row['W_per_vertex'] == 25772,
            'unchanged persistent bit stock')
    require(row['deficit_per_vertex'] == baseline_row['deficit_per_vertex'] == 1936,
            'unchanged telescoping bit deficit')
    require(row['reused_registers'] == 0, 'no unsupported bit alias')
    require(row['changed_operation_frames'] == len(plan['frames']), 'frame coverage')
    primes = prime_certificate(FRAMES / 'frames.json')
    require(primes['total_operation_frames'] == len(plan['frames']), 'prime coverage')

    print('Checking every F2 and integer bit source, target and dirty column.', file=sys.stderr, flush=True)
    formal = [candidate.formal(ring) for ring in (2, 0)]
    controls = []

    def reject(name, operation):
        try:
            operation()
        except (ValueError, AssertionError, KeyError):
            controls.append(name)
        else:
            raise ValueError('Adverse control accepted: ' + name)

    for mutation in ('omit_compensation', 'missing_partner'):
        reject(mutation, lambda mutation=mutation: candidate.formal(2, mutation))
    bad = Candidate(plan=plan)
    bad.opframe[bad.changed_frames[0]] = bad.register([])
    reject('operation frame omits its source span', bad.exact_frames)
    # Raising past a proper successor is forbidden even if source support fits.
    successor_bad = Candidate(plan=plan)
    successor_bad.exact_frames()
    role_last = {}
    adjacent = []
    for index, (left, right, _) in enumerate(successor_bad.ops):
        for role in (left, right):
            if role in role_last:
                adjacent.append((role_last[role], index))
            role_last[role] = index
    predecessor, _ = next((previous, following) for previous, following in adjacent
                          if successor_bad.C.dimf[successor_bad.opframe[following]] < successor_bad.h)
    successor_bad.opframe[predecessor] = successor_bad.w['full_frame']
    reject('operation frame exceeds its successor', successor_bad.row)
    duplicate = copy.deepcopy(plan)
    duplicate['frames'].append(copy.deepcopy(duplicate['frames'][0]))
    reject('duplicate frame entry', lambda: validate_plan(duplicate, len(candidate.ops)))
    negative = copy.deepcopy(plan)
    negative['frames'][0][0] = -1
    reject('negative operation index', lambda: validate_plan(negative, len(candidate.ops)))
    boolean = copy.deepcopy(plan)
    boolean['frames'][0][0] = True
    reject('boolean operation index', lambda: validate_plan(boolean, len(candidate.ops)))

    print('Checking every rational complex column, both signs and reversed cleanup.', file=sys.stderr, flush=True)
    complex_result = complex_certificate()
    print('Recomputing paid suppliers, full bridge, 47 constraints and seven margins.', file=sys.stderr, flush=True)
    arithmetic = arithmetic_certificate(row)
    physical = complex_result['physical_profile']
    complex_row = arithmetic['complex_profile']
    for key in ('W_per_vertex', 'rank_per_vertex', 'deficit_per_vertex', 'child_histogram'):
        require(js(physical[key]) == js(complex_row[key]), 'complex physical profile binding: ' + key)
    require(complex_row['scalar_role_reserve'] == physical['R'], 'logical scalar bill')
    require(complex_row['R'] == physical['physical_R'], 'physical stock binding')
    require(arithmetic['kappa'] > Q(6096379, 10**10), 'strict improvement over PR168')
    require(arithmetic['kappa'] > Q(594035602295411, 10**18), 'strict improvement over PR164')
    return js(dict(
        status='PASS conditional finite successor to PR168',
        baseline_commit='98c115b53742b6613ad630de4d493f37b0119da7',
        baseline_kappa=Q(6096379, 10**10), kappa=arithmetic['kappa'],
        bit=dict(profile=row, formal=formal, prime_witnesses=primes,
                 plan_sha256=digest(FRAMES / 'frames.json'), controls=controls),
        complex=complex_result, arithmetic=arithmetic,
        scope='Finite scalar words, rational/local-ring frames, complete paid profiles, '
              'full finite bridge and strict balanced assembly. The inherited all-size '
              'Clifford/tensor, uniform weighted bit compiler, restored internal rows, '
              'balanced positional layout, analytic recovery and fixed-tape interfaces '
              'remain assumptions. No global optimality or practical runtime claim.'))


def main():
    require(not sys.flags.optimize, 'Run without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Author derived certificate and numerical report')
    args = parser.parse_args()
    before = pins()
    record = build()
    certificate = HERE / 'certificate.json'
    report = HERE / 'RESULTS.md'
    if args.write:
        certificate.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
        report.write_text(render(record), encoding='utf-8', newline='\n')
    else:
        require(record == json.loads(certificate.read_text()), 'canonical certificate changed')
        require(report.read_text(encoding='utf-8') == render(record), 'generated numerical report drift')
    require(pins() == before, 'source closure changed during verification')
    print('PASS paired-cube-refinement; kappa=' + record['kappa'] +
          '; all formal columns; exact primes; 47 constraints; seven margins.')


if __name__ == '__main__':
    main()
