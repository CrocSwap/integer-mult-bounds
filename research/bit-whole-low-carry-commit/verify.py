#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Registered exact complete-payload replay and source-bound checks."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check import MATRIX, complete_gl2, run_case
from compiler import compile_program
from source import authenticate, load, require
from source_checks import source_binding


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def table_digest(program):
    return hashlib.sha256(canonical(dict(tapes=program.tapes, entry=program.entry,
                                       instructions=program.instructions))).hexdigest()


def stable_case(*args, **kwargs):
    result = run_case(*args, **kwargs)
    result.pop('seconds')
    return result


def rejection(name, operation):
    try:
        operation()
    except ValueError as error:
        return dict(name=name, result='rejected', reason=str(error))
    raise ValueError('negative control was accepted: '+name)


def verify():
    modules, raw = load()
    source_result = source_binding(modules, raw)
    require(len(complete_gl2(3)) == 48, 'independent complete GL2(F3) count')
    positives, tables, programs = [], [], {}
    for inverse in (False, True):
        program, metadata = compile_program(modules, 3, MATRIX, inverse)
        require(tuple(metadata['types']) == complete_gl2(3), 'full independently enumerated low domain')
        require(set(row[0] for row in program.instructions) <= {'branch', 'move', 'write', 'goto', 'halt', 'reject'},
                'only finite local instruction alphabet')
        programs[inverse] = program, metadata
        tables.append(dict(inverse=inverse, instructions=len(program.instructions), tapes=program.tapes,
                           sha256=table_digest(program), local_instruction_census=dict(sorted(Counter(
                               row[0] for row in program.instructions).items()))))
        for Q, Z in ((1, 1), (1, 2), (3, 1), (3, 2)):
            pair = [stable_case(modules, program, metadata, Q, Z, mode,
                                boundary_checks=mode == 'sparse') for mode in ('sparse', 'dense')]
            for key in ('steps', 'spans', 'output_sha256', 'input_sha256'):
                require(pair[0][key] == pair[1][key], 'independent local interpreter agreement: '+key)
            positives.extend(pair)
    for pattern in ('zero', 'one'):
        positives.append(stable_case(modules, *programs[False], 3, 2, pattern=pattern,
                                     boundary_checks=True))

    controls = []
    input_pin = next(row for row in json.loads((HERE/'SOURCES.json').read_bytes())['files'] if row['usage'] == 'input')
    controls.append(rejection('pinned_source_byte_change',
                              lambda: authenticate(input_pin, raw[input_pin['path']]+b' ')))
    for mutant in ('wrong_cache_type', 'early_commit', 'negative_carries', 'erase_cache_early',
                   'omit_first_carry', 'alias_carry_owner', 'omit_installation', 'wrong_low_direction'):
        program, metadata = compile_program(modules, 3, MATRIX, mutant=mutant)
        require(table_digest(program) != tables[0]['sha256'], 'mutant actually changes literal program')
        controls.append(rejection(mutant,
                                  lambda p=program, m=metadata: stable_case(modules, p, m, 3, 1)))
    program, metadata = compile_program(modules, 3, MATRIX, mutant='extra_work')
    modified = stable_case(modules, program, metadata, 3, 1)
    original = next(row for row in positives if not row['inverse'] and row['Q'] == 3 and row['z'] == 1
                    and row['mode'] == 'sparse')
    require(modified['output_sha256'] == original['output_sha256'] and modified['steps'] == original['steps']+2,
            'endpoint-preserving extra-work control changes exact cost by two')
    controls.append(dict(name='endpoint_preserving_extra_work', result='detected', added_transitions=2,
                         scope='Exact instruction/count drift; the conservative upper bound still holds'))
    require(len(controls) == 10, 'all registered negative/resource controls')
    return dict(schema_version=1, base_commit='7c49fe32c55de02c2c873655c804b16e4c3fef0a',
                result='PASS_BIT_WHOLE_LOW_CARRY_COMMIT', kappa_changed=False,
                theorem_scope='Fixed N,q supplied complete-stream ABI; arbitrary runtime odd Q and positive Z',
                fixture=dict(q=3, n=2, complete_low_types=48,
                             matrix=[[str(x) for x in row] for row in MATRIX], payload_seed=12,
                             complete_payload_shapes=[[1, 1], [1, 2], [3, 1], [3, 2]],
                             source_direction_flags=[False, True], engines=['sparse', 'independent dense'],
                             execution_cap=100_000_000, stopping_rule='Exactly all listed complete cases and controls'),
                source_binding=source_result, literal_tables=tables, positive_cases=positives,
                negative_controls=controls,
                limitations=['No full GL8 payload execution', 'No homogeneous high route implementation',
                             'No literal selected-caller layout producer', 'No selected-rate physical dispatcher'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Regenerate only this package receipt')
    args = parser.parse_args()
    result = verify()
    output = HERE/'RESULT.json'
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        require(json.loads(output.read_bytes()) == result, 'exact registered result receipt')
    print('PASS_BIT_WHOLE_LOW_CARRY_COMMIT '+json.dumps(dict(
        kappa_changed=False, complete_low_types=48, literal_tables=len(result['literal_tables']),
        positive_cases=len(result['positive_cases']), controls=len(result['negative_controls'])), sort_keys=True))


if __name__ == '__main__':
    main()
