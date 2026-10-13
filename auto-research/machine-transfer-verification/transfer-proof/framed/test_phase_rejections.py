#!/usr/bin/env python3
"""Adversarial controls for the phase checker; never modifies selected inputs.

Mutations are applied to an in-memory copy of the checker so that malformed
phase schedules can be tested even though the source word is hash-pinned.
Every replacement must occur exactly once and must fail for the named reason.
These controls test the independent checker, not a Lean kernel theorem.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

CASES = [
    ('missing_middle_destination_transport',
     '        raise_aux(a, frame + 2)\n', '', 'Unequal current gauges'),
    ('missing_middle_source_transport',
     '        raise_aux(b, frame + 2)\n', '', 'Unequal current gauges'),
    ('center_copy_read_without_transport',
     '        temporary_frame = 0\n', '        temporary_frame = frame\n', 'Unequal current gauges'),
    ('unpaid_center_copy_transport',
     '        paid[0, frame] += 1  # inverse partial swap is the SAME involution\n', '', 'Complete local auxiliary mass'),
    ('missing_side_read',
     '\n            late_scatter.append([v + i, 2 * v + slot])\n', '\n', 'Late scatter does not preserve'),
    ('missing_cleanup_before_final_inverse',
     '    for slot in range(R):\n        raise_aux(slot, 1)\n', '', 'Unequal current gauges'),
    ('incorrect_side_flag_vector',
     '{a: 1, b: -1}\n', '{a: 1, b: 1}\n', 'Basis-flag orthogonality'),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--receipt', required=True, type=Path)
    parser.add_argument('--binary', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    checker = HERE / 'full_forward_phase.py'
    source = checker.read_text()
    cases = []
    for name, old, new, expected in CASES:
        if source.count(old) != 1:
            raise RuntimeError('Mutation anchor not unique: ' + name)
        namespace = {'__name__': 'mutated_phase_checker', '__file__': str(checker)}
        exec(compile(source.replace(old, new), str(checker) + ':' + name, 'exec'), namespace)
        try:
            namespace['audit'](args.word, args.manifest, args.receipt, args.binary)
        except ValueError as error:
            if expected not in str(error):
                raise RuntimeError('Wrong rejection for ' + name + ': ' + str(error)) from error
            cases.append(dict(name=name, status='REJECTED', reason=str(error),
                              mutation_sha256=sha256((old + '\0' + new).encode()).hexdigest()))
        else:
            raise RuntimeError('Malformed phase schedule accepted: ' + name)
    report = dict(status='PASS', checker_sha256=sha256(checker.read_bytes()).hexdigest(),
                  controls=cases, scope='Seven in-memory phase-schedule mutations; no selected source or data was changed.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS seven malformed phase schedules rejected')


if __name__ == '__main__':
    main()
