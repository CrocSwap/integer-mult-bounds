#!/usr/bin/env python3
"""Full opt-in replay, independent controls and exact receipt comparison.
Tekalign / OpenAI Codex, Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent


def load(name):
    path = PACKAGE / (name + '.py')
    obj = types.ModuleType('anchor_' + name)
    obj.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), obj.__dict__)
    return obj


def calculate():
    replay = load('replay')
    result = replay.run('anchor')
    checks = load('controls').check()
    return {'status': 'PASS_CLIFFORD_PAULI_ANCHOR',
            'base_commit': '463113d675af7410ac91d53a4fed51ec6494eb9a',
            'dependency_pr3202': '259043321323717b7e816d6be38ad5e1f0b69b4c',
            'reference_result_sha256': result['reference_result_sha256'],
            'call_multiset_sha256': result['call_multiset_sha256'], 'decisions': result['calls'],
            'source_sha256': result['source_sha256'], 'controls': checks,
            'coverage': 'Exact equality on the 512-dimensional operator domain, via signed Pauli action and one whole anchor column; not 512 explicitly simulated input columns.',
            'new_kappa': False, 'formal_kernel_proof': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-result', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.emit_result:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / 'RESULT.json').read_bytes())
        if json.dumps(result, sort_keys=True) != json.dumps(expected, sort_keys=True):
            raise ValueError('stored result mismatch')
        print('PASS_CLIFFORD_PAULI_ANCHOR calls=253 accepted=244 rejected=9 matrix_controls=4704')


if __name__ == '__main__':
    main()
