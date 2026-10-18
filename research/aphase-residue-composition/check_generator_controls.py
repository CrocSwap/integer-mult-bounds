#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reject four invalid variants of the exact P53 width-7 relay.

The declarations are mutated only in memory. Immutable source files and the
frozen candidate are never edited. The positive generator is also exercised.
Marius-Paul Dumitrean, with substantial OpenAI Codex assistance.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path,
                        default=HERE.parent/'gmx-t74-borrow43-handoff')
    parser.add_argument('--generator', type=Path, default=HERE/'generate.py')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(), 'fresh receipt required')
        need(not args.out.resolve().is_relative_to(HERE),
             'receipt must be outside the package')
        need(not args.out.resolve().is_relative_to(args.source.resolve()),
             'receipt must be outside the immutable source')
    generator_bytes = args.generator.read_bytes()
    generator_hash = hashlib.sha256(generator_bytes).hexdigest()
    generator = types.ModuleType('portable_relay_generator')
    generator.__file__ = str(args.generator.resolve())
    exec(compile(generator_bytes, str(args.generator), 'exec'), generator.__dict__)
    source_before = generator.authenticate(args.source)
    original = copy.deepcopy(generator.MOVES)
    generator.build(args.source)
    controls = []

    def reject(name, mutate, reason):
        generator.MOVES = copy.deepcopy(original)
        mutate(generator.MOVES)
        try:
            generator.build(args.source)
        except ValueError as error:
            need(str(error) == reason, name + ': unexpected rejection: ' + str(error))
            controls.append({'name': name, 'reason': str(error)})
        else:
            raise ValueError('accepted invalid relay: ' + name)

    def wrong_width(moves):
        destination = moves.pop((0, 228))
        moves[(0, 236)] = destination

    reject('replace_width7_role_with_actual_width8_role', wrong_width,
           'four actual width7 roles')
    reject('move_outside_initial_source_window',
           lambda moves: moves.__setitem__((29, 327), (0, 0, 2)),
           'relay destination source window')
    reject('reuse_originally_busy_family_at_time0',
           lambda moves: moves.__setitem__((0, 228), (66, 10, 90)),
           'relay destination family initially free')
    reject('merge_both_terminal_roles_into_one_full_carrier',
           lambda moves: moves.__setitem__((30, 360), (66, 10, 90)),
           'changed-bin capacity')
    generator.MOVES = original
    need(source_before == generator.authenticate(args.source), 'source drift')
    need(sha(args.generator) == generator_hash, 'generator drift')
    report = {
        'status': 'PASS_FOUR_PORTABLE_RELAY_MUTATION_CONTROLS',
        'generator_sha256': generator_hash,
        'runner_sha256': sha(Path(__file__)),
        'positive_generator_passed': True,
        'controls': controls,
        'source_unchanged': True,
        'mutation_scope': 'Only declaration copies in isolated memory are changed. '
                          'Source files and the frozen candidate are untouched.',
    }
    encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
