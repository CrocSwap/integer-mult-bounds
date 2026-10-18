#!/usr/bin/env python3
"""Bind the rebuilt PR589 bit supplier to the PR741 complex replay.

Finite verification only; the inherited realization and analytic assumptions
remain. Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/complex-sw4-frame8'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def check(bit, complex_dir):
    cited_path = PACKAGE / 'inputs/PR589-EXPECTED.json'
    cited = read(cited_path)
    original = ROOT / 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
    require(cited_path.read_bytes() == original.read_bytes(), 'PR589 source binding')
    actual = read(bit / 'RESULT9.json')
    for field, key in [('bit_lower', 'bit_lower'), ('bit_lower_decimal', 'bit_lower_decimal'),
                       ('bit_profile', 'profile'), ('bit', 'bit')]:
        require(actual[field] == cited['nine'][key], 'Rebuilt bit differs: ' + field)
    require(actual['stages'] == 9 and actual['replicas'] == 32, 'Bit layout')
    interface = read(bit / 'xcheck.json')
    for key in ('hypotheses', 'conclusion', 'interleaving'):
        require(interface[key] == cited['interface'][key], 'Bit interface: ' + key)
    require(all(v is True for v in interface['hypotheses'].values()) and
            all(v is True for v in interface['conclusion'].values()), 'Bit scalar contract')
    hosted = read(bit / 'v9/hosted/AUDIT.json')
    require(hosted['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT', 'Bit owner audit')
    require(hosted['hosted_residuals'] == 32 * 9 * 439 and hosted['bank_assignments'] == 0,
            'Bit owner inventory')
    require(len(hosted['mutations_rejected']) == 16, 'Bit owner controls')
    require(hosted['profile'] == actual['bit_profile'] and
            hosted['emitted_program_sha256'] == actual['emitted_program_sha256'], 'Bit emitted program')
    columns = read(bit / 'cout/columns_k4.json')
    require(columns['formal_columns_checked'] == 1327, 'Bit formal columns')
    require(len(columns['negative_controls']) == 18 and
            all(x['rejected'] is True for x in columns['negative_controls']), 'Bit bridge controls')

    receipt = read(complex_dir / 'RECEIPT.json')
    require(receipt['manifest_sha256'] == digest(PACKAGE / 'MANIFEST.json') and
            receipt['spec_sha256'] == digest(PACKAGE / 'data/SPEC.json'), 'Complex source binding')
    stages = receipt['stages']
    require(len(stages) == 22 and len({s['name'] for s in stages}) == 22 and
            all(s['exit_code'] == 0 for s in stages), 'Complex stage completion')
    for name, pin in receipt['artifacts'].items():
        p = (complex_dir / name).resolve()
        require(p.is_relative_to(complex_dir.resolve()) and digest(p) == pin,
                'Complex artifact binding: ' + name)
    for stage in stages:
        require(digest(complex_dir / (stage['name'] + '.log')) == stage['log_sha256'],
                'Complex stage log: ' + stage['name'])
    assembly_path = complex_dir / 'global-replay/ASSEMBLY.json'
    assembly = read(assembly_path)
    result = read(complex_dir / 'RESULT.json')
    require(assembly['bit_lower'] == actual['bit_lower'], 'Assembly bit endpoint')
    require(assembly['input_sha256']['package:inputs/PR589-EXPECTED.json'] == digest(cited_path),
            'Assembly bit source')
    require(assembly['bit_supplier']['derived_deficit'] == 10272, 'Bit punctured deficit')
    require(assembly['kappa'] == result['kappa'] == '1661202643272239/1000000000000000000',
            'Selected exact result')
    require(len(assembly['outer']) == 47 and all(Fraction(x) > 0 for x in assembly['outer'].values()),
            'Strict outer constraints')
    require(assembly['surcharge_model'] == {'complex': False, 'bit': True}, 'Recurrence model')
    return dict(status='PASS_REBUILT_PR589_PR741_COMPOSITION', kappa=assembly['kappa'],
                decimal=assembly['kappa_decimal'], bit_input_sha256=digest(cited_path),
                bit_result_sha256=digest(bit / 'RESULT9.json'),
                complex_receipt_sha256=digest(complex_dir / 'RECEIPT.json'),
                complex_assembly_sha256=digest(assembly_path),
                scope='Rebuilt finite suppliers and exact composition. All-size/compiler, '
                      'common-label/mutable-source, whole-call hosting, precision/tape and '
                      'analytic transfer hypotheses remain conditional; not a full Lean theorem.')


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('bit', 'complex', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    result = check(a.bit, a.complex)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['decimal'])


if __name__ == '__main__':
    main()
