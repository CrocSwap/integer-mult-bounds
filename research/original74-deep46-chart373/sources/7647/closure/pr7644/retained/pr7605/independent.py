#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the timed update with exact forward and reverse row interpreters.

Ali Romman, with substantial OpenAI Codex assistance. The retained independent
interpreters are by Hao Yan/7604. They do not import this construction.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
BUILD = runpy.run_path(str(HERE / 'build.py'))
require = BUILD['require']


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def timed_identity(word, engine):
    """Read both 1255 values and the two removed input rows independently."""
    public = word['public']
    rows = [{r: Q(1)} for r in range(public)] + [{} for _ in range(word['owned_fields'])]
    values = {}
    for i, event in enumerate(word['program']):
        if i == 33518:
            values['early'] = rows[1255].copy()
        if i == 38585:
            values['first'] = rows[902].copy()
        if i == 42714:
            values['second'] = rows[1557].copy()
        if i == 42716:
            values['late'] = rows[1255].copy()
            break
        op, dest = event[:2]
        if op in ('ADD', 'COPY'):
            engine['axpy'](rows[dest], rows[event[2]], Q(event[3]))
        elif op == 'SCALE':
            rows[dest] = {k: v * Q(event[2]) for k, v in rows[dest].items()}
        elif op in ('INIT', 'CLEAR'):
            rows[dest] = {}
        else:
            require(op == 'MOVE', 'known opcode')
    difference = values['late'].copy()
    engine['axpy'](difference, values['early'], Q(-1))
    required = {}
    engine['axpy'](required, values['first'], Q(-1))
    engine['axpy'](required, values['second'], Q(-2, 3))
    require(difference == required, 'exact timed update identity on all public inputs')
    return dict(early_terms=len(values['early']), late_terms=len(values['late']),
                update_terms=len(required), update_sha256=engine['matrix_digest']([required]))


def verify():
    BUILD['authenticate']()
    engine = runpy.run_path(str(HERE / 'retained/pr7604/independent.py'))
    old = read(HERE / 'retained/pr7604/word.json.gz')
    new = read(HERE / 'data/word.json.gz')
    require(new == BUILD['build_word'](), 'candidate source binding')
    identity = timed_identity(old, engine)
    baseline = engine['audit_word'](old, 'PR7604')
    candidate = engine['audit_word'](new, 'helper757')
    preserved = ('rows', 'chart', 'grid', 'owned_moves', 'lifetimes', 'peak',
                 'erased', 'helpers', 'rises')
    for key in preserved:
        require(candidate[key] == baseline[key], 'preserve ' + key)
    changed = sorted(r for r in baseline['chains'] if baseline['chains'][r] != candidate['chains'][r])
    require(changed == [757], 'only helper757 changes its paid route')
    delta = candidate['paid'].copy()
    delta.subtract(baseline['paid'])
    require({r: n for r, n in delta.items() if n} == {1: -2, 2: 1}, 'native paid delta')
    counts = candidate['operations'].copy()
    counts.subtract(baseline['operations'])
    require({op: n for op, n in counts.items() if n} == {'MOVE': -1}, 'one fewer MOVE; same scalar count')
    old_bill = read(HERE / 'retained/pr7604/invoice-new.json')
    new_bill = read(HERE / 'data/invoice-new.json')
    p = Counter({int(r): n for r, n in old_bill['paid'].items()})
    for r, count in delta.items():
        p[r] += 17 * count
    require(dict(p) == {int(r): n for r, n in new_bill['paid'].items()}, 'all 17 native calls charged')
    require(old_bill['targets'] == new_bill['targets'], 'unchanged complete productive bill')

    controls = {}
    preload = ['ADD', 757, 1255, '-1', 3]
    restore = ['ADD', 757, 1255, '1', 603]
    move = ['MOVE', 757, 3, 603, False]
    faults = {}
    for name, event in (('omit_early_subtraction', preload), ('omit_late_addition', restore),
                        ('omit_paid_move', move)):
        bad = copy.deepcopy(new)
        bad['program'].remove(event)
        faults[name] = bad
    bad = copy.deepcopy(new)
    index = bad['program'].index(preload)
    require(bad['program'][index - 1] == ['ADD', 1143, 757, '-1', 3], 'crossed read control')
    bad['program'][index - 1:index + 1] = [preload, bad['program'][index - 1]]
    faults['preload_before_last_read'] = bad
    for name, bad in faults.items():
        try:
            got = engine['forward_audit'](bad)
            require(all(got[key] == baseline[key] for key in preserved), 'changed complete endpoint or retirement')
        except ValueError:
            controls[name] = True
        else:
            raise ValueError('mutation survived: ' + name)
    return dict(status='PASS_HELPER757_EXACT_WORD', timed_identity=identity,
                public_inputs=old['public'], endpoint_rows=len(candidate['rows']),
                erased_rows=len(candidate['erased']), owned_lifetimes=len(candidate['lifetimes']),
                owned_peak=candidate['peak'], grid=candidate['grid'],
                endpoint_sha256=engine['matrix_digest'](candidate['rows']),
                erasure_sha256=engine['matrix_digest']([row for _, _, row in candidate['erased']]),
                native_paid_delta={'1': -2, '2': 1}, complete_paid_delta={'1': -34, '2': 17},
                unchanged_header=True, unchanged_owned_paths=True, controls=controls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = verify()
    path = HERE / 'data/EXACT.json'
    if args.write:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    require(report == read(path), 'deterministic exact receipt')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
