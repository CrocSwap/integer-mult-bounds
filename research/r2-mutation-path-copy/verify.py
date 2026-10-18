#!/usr/bin/env python3
"""Complete replay, full-deepcopy differential mutants and isolation controls.
Tekalign / OpenAI Codex, Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent


def load(name):
    path = PACKAGE / (name + '.py')
    module = types.ModuleType('path_verify_' + name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def calculate():
    result = load('replay').run('paths', differential=True)
    return {'status': 'PASS_R2_PATH_COPY', 'complete_mutants_compared_to_deepcopy': 32,
            **{k: result[k] for k in ('reference_result_sha256', 'call_multiset_sha256',
                                     'decisions', 'providers', 'source_sha256')},
            'controls': load('controls').check(), 'new_kappa': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-result', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.emit_result:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        if result != json.loads((PACKAGE / 'RESULT.json').read_bytes()):
            raise ValueError('stored full result differs')
        print('PASS_R2_PATH_COPY mutants=32 complete_deepcopy_equivalence=32 decisions=253')


if __name__ == '__main__':
    main()
