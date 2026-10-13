#!/usr/bin/env python3
"""Bind fresh PR493/523 replays to the dependencies consumed by PR531.

This is a dependency check, not an all-size compiler proof. Apache-2.0.
Douglas Colkitt, with OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/direct-delivery504-global'


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(bit, predecessor, direct):
    b = read(bit / 'RESULT.json')
    expected_bit = read(PACKAGE / 'inputs/PR493-EXPECTED.json')['eleven']
    fields = {'bit_lower': 'bit_lower', 'bit_profile': 'profile',
              'bit': 'bit', 'emitted_program_sha256': 'emitted_program_sha256'}
    for fresh, cited in fields.items():
        require(b[fresh] == expected_bit[cited], 'Bit dependency differs: ' + fresh)
    require(read(predecessor / 'RESULT.json')['status'] ==
            'PASS_CONDITIONAL_PUNCTURED112_GLOBAL_KAPPA', 'Predecessor replay failed')
    bindings = []

    def same(fresh, frozen):
        require(read(fresh) == read(frozen), 'Rebuilt dependency differs: ' + str(frozen))
        bindings.append({'fresh': str(fresh), 'frozen': str(frozen.relative_to(ROOT)),
                         'frozen_sha256': hashlib.sha256(frozen.read_bytes()).hexdigest()})

    for name in ('CANONICAL-WORD.json.gz', 'CLIFFORD-RECIPES.json', 'LOCAL-CHECKS.json'):
        same(predecessor / 'local112' / name, PACKAGE / 'inputs/phase-baseline' / name)
    for name in ('split-centres/CANONICAL-WORD.json.gz',
                 'split-centres/GLOBAL-TEMPLATE.json.gz',
                 'work/complex-nine-native/DATA-PHASES.json'):
        same(predecessor / 'base112' / name, PACKAGE / 'inputs/data-base' / name)
    for name in ('moment.py', 'base_two_moment.py', 'outer.py'):
        rel = 'work/pr361/code/engines/' + name
        require((predecessor / 'base112' / rel).read_bytes() ==
                (PACKAGE / 'inputs/data-base' / rel).read_bytes(), 'Arithmetic engine differs')
    same(predecessor / 'audit/PREFIX-AND-INVOICE.json',
         PACKAGE / 'inputs/PR523-PREFIX-AND-INVOICE.json')
    same(direct / 'scalar/CANONICAL-WORD.json.gz', PACKAGE / 'evidence/local/CANONICAL-WORD.json.gz')
    same(direct / 'scalar/LOCAL-PROGRAMS.json.gz', PACKAGE / 'evidence/local/LOCAL-PROGRAMS.json.gz')
    same(direct / 'scalar/RESIDUAL-ADAPTERS.json', PACKAGE / 'evidence/local/RESIDUAL-ADAPTERS.json')
    answer = read(direct / 'audit/EXACT-ASSEMBLY.json')
    require(answer['kappa'] == read(PACKAGE / 'EXPECTED.json')['kappa'], 'Headline differs')
    require(answer['bit_lower'] == b['bit_lower'], 'Assembly uses another bit rate')
    return {'status': 'PASS_FRESH_DEPENDENCY_BINDINGS', 'kappa': answer['kappa'],
            'bindings': bindings, 'bit_fields_checked': fields,
            'scope': 'Fresh finite replays joined by exact content; all-size and analytic interfaces remain conditional.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('bit', 'predecessor', 'direct', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    result = check(a.bit, a.predecessor, a.direct)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['kappa'])


if __name__ == '__main__':
    main()
