#!/usr/bin/env python3
"""Independently bind suffix recipes to the complete resulting literal word.

This does not import the search or constructor. Native scalar/frame, exact
phase, omission, hosting and invoice checks remain separate obligations.
"""

import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accumulate(target, source, factor):
    for index, value in source.items():
        target[index] = target.get(index, 0) + factor * value
        if not target[index]:
            del target[index]


def check(source, word, recipes):
    expected = copy.deepcopy(source)
    records = []
    require(len({r['pivot'] for r in recipes}) == len(recipes), 'Repeated pivot')
    for recipe in sorted(recipes, key=lambda r: -r['index']):
        index, pivot, frame = recipe['index'], recipe['pivot'], recipe['frame']
        require(recipe['part'] == 'B' and 0 <= index <= len(expected['B']), 'Invalid cut')
        require(224 <= pivot < 728 and str(pivot) not in expected['start_extra'],
                'Pivot is not a previously cold helper')
        span = {0}
        for vector in frame:
            require(type(vector) is int and 0 < vector < 512 and vector not in span,
                    'Dependent or invalid frame basis')
            span |= {x ^ vector for x in tuple(span)}
        require(frame, 'Empty entrance frame')
        prefix = expected['A'] + expected['cut'] + expected['B'][:index]
        require(all(pivot not in (e[1:3] if e[0] == 'add' else e[1:2]) for e in prefix),
                'Pivot used before its kernel')
        columns = [{} for _ in range(728)]
        for target in range(112):
            columns[112 + target] = {target: Fraction(1)}
        for event in reversed(expected['B'][index:]):
            if event[0] == 'add':
                accumulate(columns[event[2]], columns[event[1]], Fraction(event[3], event[4]))
            else:
                require(event[0] == 'scale', 'Unknown scalar operation')
                factor = Fraction(event[2], event[3])
                columns[event[1]] = {key: value * factor for key, value in columns[event[1]].items()}
        residual = columns[pivot].copy()
        gates = []
        for donor_text, coefficient in sorted(recipe['coefficients'].items(), key=lambda x: int(x[0])):
            donor, factor = int(donor_text), Fraction(coefficient)
            require(0 <= donor < 728 and donor != pivot and not 112 <= donor < 224,
                    'Invalid donor')
            require(factor and factor.denominator & (factor.denominator - 1) == 0,
                    'Zero or non-dyadic coefficient')
            accumulate(residual, columns[donor], -factor)
            gates.append(['add', donor, pivot, -factor.numerator, factor.denominator, frame])
        require(not residual, 'Suffix response identity failed')
        expected['B'][index:index] = gates
        expected['start_extra'][str(pivot)] = frame
        records.append({'pivot': pivot, 'original_index': index, 'gate_count': len(gates),
                        'suffix_identity_exact': True, 'untouched_before_cut': True})
    cleanup = []
    for event in reversed(expected['A'] + expected['B']):
        if 112 <= event[1] < 224:
            continue
        inverse = copy.deepcopy(event)
        if event[0] == 'add':
            inverse[3] = -inverse[3]
        else:
            inverse[2], inverse[3] = inverse[3], inverse[2]
        inverse[-1] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        cleanup.append(inverse)
    expected['cleanup'] = cleanup
    require(set(expected) == set(word), 'Changed word schema')
    for field in expected:
        if field != 'report':
            require(expected[field] == word[field], 'Unexpected literal change: ' + field)
    allowed = {'local_profile', 'entrance_rank', 'entering_helpers'}
    require(set(source['report']) == set(word['report']), 'Changed report schema')
    require(all(source['report'][key] == word['report'][key]
                for key in source['report'] if key not in allowed), 'Unexplained report change')
    for record in records:
        record['final_index'] = record['original_index'] + sum(
            len(r['coefficients']) for r in recipes if r['index'] < record['original_index'])
    return sorted(records, key=lambda r: r['final_index'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--recipe', type=Path, action='append', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Use a new receipt path')
    source, word = read(args.source), read(args.word)
    recipes = [read(path) for path in args.recipe]
    checks = check(source, word, recipes)
    controls = []
    for label in ('changed_donor_coefficient', 'omitted_new_entrance', 'unrelated_scalar_edit'):
        mutant = copy.deepcopy(word)
        if label == 'changed_donor_coefficient':
            mutant['B'][checks[0]['final_index']][3] += 1
        elif label == 'omitted_new_entrance':
            del mutant['start_extra'][str(checks[0]['pivot'])]
        else:
            mutant['A'][0][3] += 1
        try:
            check(source, mutant, recipes)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('Mutation accepted: ' + label)
    receipt = {'status': 'PASS_INDEPENDENT_SUFFIX_COMPOSITION',
               'source_sha256': sha(args.source), 'word_sha256': sha(args.word),
               'recipe_sha256': {path.name: sha(path) for path in args.recipe},
               'auditor_sha256': sha(Path(__file__)), 'checks': checks,
               'negative_controls_rejected': controls,
               'scope': 'Exact rational suffix identities, complete literal changes and inverse cleanup checked independently of constructor/search imports. Legacy report fields remain inherited; admission must derive profile and widths from actual frames/programs. Native, phase, scalar omission and global admission are separate.'}
    args.out.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(checks), len(controls))


if __name__ == '__main__':
    main()
