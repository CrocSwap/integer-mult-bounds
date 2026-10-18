#!/usr/bin/env python3
"""Path isolation, actual failure modes and source-hook controls.
Tekalign / OpenAI Codex, Apache-2.0.
"""
import copy
import json
from pathlib import Path
import random
import types

PACKAGE = Path(__file__).resolve().parent


def load(name):
    path = PACKAGE / (name + '.py')
    module = types.ModuleType('path_copy_' + name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def check():
    A = load('adapter')
    rng = random.Random(21)
    def rejected(action, text):
        try:
            action()
        except ValueError as error:
            A.need(text in str(error), 'wrong control rejection: ' + str(error))
        else:
            raise ValueError('control accepted: ' + text)

    for _ in range(100):
        tree, path = {'payload': [[rng.randrange(-1000, 1001)], ['unicode \u03ba', 2 ** 90]]}, []
        for _ in range(rng.randrange(1, 6)):
            if rng.randrange(2):
                tree, path = {'target': tree, 'unchanged': [[7]]}, ['target'] + path
            else:
                tree, path = [tree, [[7]]], [0] + path
        before = A.fixture_guard(tree)
        expected, forked = copy.deepcopy(tree), A.fork_path(tree, path)
        a, b = expected, forked
        for key in path:
            a, b = a[key], b[key]
        a['payload'][0].append(42)
        b['payload'][0].append(42)
        A.need(forked == expected, 'nested full-copy equivalence')
        A.need(A.fixture_guard(tree) == before, 'nested original changed')

    # Outer-list splice needs no mutable-event copy, but the event cells stay read-only.
    original = {'stream': [[i, [i * i]] for i in range(7)]}
    before = A.fixture_guard(original)
    forked = A.fork_path(original, ['stream'], False)
    expected = copy.deepcopy(original)
    for value in (forked, expected):
        block = value['stream'][3:-1]
        del value['stream'][3:-1]
        value['stream'][1:1] = block
    A.need(forked == expected and A.fixture_guard(original) == before, 'splice isolation')
    A.need(forked['stream'][0] is original['stream'][0], 'read-only sharing not exercised')

    marshal_raw = (PACKAGE / 'vendor/pr1939/fast_copy.py').read_bytes()
    copier, counts = A.checked_marshal_function(marshal_raw)
    shared = []
    source = [shared, shared]
    copied = copier(source)
    A.need(copied == source and copied[0] is copied[1] and copied[0] is not shared,
           'credited full-copy alias isolation')
    A.need(counts['marshal'] == 1, 'credited marshal baseline executed')

    # A shallow event copy would leak its nested scalar write to the original.
    word = {'restore': []}
    data = {A.PROGRAM: {'forward': [['scalar', ['add', ['L', 40], ['L', 54], -2, 1]]]}}
    H = A.Harness('paths', marshal_raw)
    H.begin('control', word, data)
    wrong = A.fork_path(data, [A.PROGRAM, 'forward', 0], False)
    wrong[A.PROGRAM]['forward'][0][1][3] = 2
    rejected(lambda: H.end('control', word, data), 'original fixture mutated')

    # A future mutation outside the pinned footprint must fail the end guard.
    word, data = {'restore': [], 'outside': [0]}, {A.PROGRAM: {'forward': [
        ['scalar', ['add', ['L', 40], ['L', 54], -2, 1]]]}}
    H = A.Harness('paths', marshal_raw)
    H.begin('control', word, data)
    w, d = H.copy('forward fan-in sign', word, data)
    w['outside'][0] = 1
    rejected(lambda: H.end('control', word, data), 'original fixture mutated')

    # An incorrect replacement payload must fail complete differential comparison.
    word, data = {}, {'x': [0]}
    H = A.Harness('paths', marshal_raw, differential=True)
    H.begin('control', word, data)
    def mutate(w, d):
        d['x'][0] = 1
    rejected(lambda: H.observe('wrong payload', mutate, {}, {'x': [2]}, word, data),
             'complete mutant differs')
    rejected(lambda: A.plan('future unknown mutation', {}, {}), 'unrecognized pinned mutation')
    rejected(lambda: A.fork_path({'a': 1}, ['a']), 'path container')

    raw = (PACKAGE / 'vendor/pr3218/vendor/pr3202/verify.py').read_bytes()
    point = b'        w, d = copy.deepcopy(word), copy.deepcopy(data)'
    rejected(lambda: A.transform_audit(raw.replace(point, b'        w, d = word, data')),
             'unique source hook')
    rejected(lambda: A.transform_audit(raw + b'\n' + point), 'unique source hook')
    replay = (PACKAGE / 'vendor/pr3218/replay.py').read_bytes()
    point = b'        verifier._install_comparator = install'
    rejected(lambda: A.transform_replay(replay.replace(point, b'        pass')), 'unique source hook')
    return {'seed': 21, 'generated_full_copy_equivalences': 100,
            'outer_list_splice': True, 'credited_marshal_alias_isolation': True,
            'leaked_nested_write_rejected': True, 'out_of_footprint_write_rejected': True,
            'wrong_full_mutant_rejected': True, 'unknown_mutation_rejected': True,
            'noncontainer_path_rejected': True, 'source_hook_mutants_rejected': 3}


if __name__ == '__main__':
    print('PASS_PATH_COPY_CONTROLS', json.dumps(check(), sort_keys=True))
