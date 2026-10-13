#!/usr/bin/env python3
"""Bind the rebuilt PR543 bit circuit to PR588's complete complex replay."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check(bit, complex_dir):
    actual = read(bit / 'RESULT9.json')
    cited_path = ROOT / 'research/complex-multicold/inputs/PR543-EXPECTED.json'
    cited = read(cited_path)['nine']
    fields = {'bit_lower': 'bit_lower', 'bit_lower_decimal': 'bit_lower_decimal',
              'bit_profile': 'profile', 'bit': 'bit'}
    for name, key in fields.items():
        require(actual[name] == cited[key], 'Bit input differs: ' + name)
    require(actual['stages'] == 9 and actual['replicas'] == 32, 'Bit layout')
    interface = read(bit / 'xcheck.json')
    require(len(interface['hypotheses']) == 5 and
            all(v is True for v in interface['hypotheses'].values()), 'Bit H1-H5')
    require(all(v is True for v in interface['conclusion'].values()), 'Bit scalar endpoint')
    hosted = read(bit / 'v9/hosted/AUDIT.json')
    require(hosted['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT', 'Bit physical audit')
    require(hosted['hosted_residuals'] == 120960 and hosted['bank_assignments'] == 0, 'Bit owners')
    require(len(hosted['mutations_rejected']) == 16, 'Bit physical controls')
    require(hosted['profile'] == actual['bit_profile'], 'Bit physical profile')
    require(hosted['emitted_program_sha256'] == actual['emitted_program_sha256'], 'Bit program')
    columns = read(bit / 'cout/columns_k4.json')
    require(columns['formal_columns_checked'] == 1380, 'Bit column count')
    require(len(columns['negative_controls']) == 18 and
            all(x['rejected'] for x in columns['negative_controls']), 'Bit bridge controls')

    receipt = read(complex_dir / 'RECEIPT.json')
    require(receipt['steps'] and all(s['exit_code'] == 0 for s in receipt['steps']), 'Complex stage completion')
    for name, digest in receipt['artifacts'].items():
        require(sha(complex_dir / name) == digest, 'Complex artifact changed: ' + name)
    for step in receipt['steps']:
        require(sha(complex_dir / (step['name'] + '.log')) == step['log_sha256'],
                'Complex stage log changed: ' + step['name'])
    assembly = read(complex_dir / 'ASSEMBLY.json')
    result = read(complex_dir / 'RESULT.json')
    require(assembly['bit_lower'] == actual['bit_lower'], 'Assembly bit rate')
    require(assembly['input_sha256']['inputs/PR543-EXPECTED.json'] == sha(cited_path), 'Assembly bit input hash')
    require(assembly['kappa'] == result['kappa'], 'Assembly result')
    require(len(assembly['outer']) == 47 and
            all(Fraction(x) > 0 for x in assembly['outer'].values()), 'Strict outer constraints')
    require(assembly['surcharge_model'] == {'complex': False, 'bit': True}, 'Recurrence model')
    return {
        'status': 'PASS_REBUILT_PR543_PR588_COMPOSITION',
        'kappa': assembly['kappa'], 'decimal': assembly['kappa_decimal'],
        'conservative_kappa': assembly['conservative_kappa'],
        'bit_fields': fields, 'bit_input_sha256': sha(cited_path),
        'complex_receipt_sha256': sha(complex_dir / 'RECEIPT.json'),
        'complex_assembly_sha256': sha(complex_dir / 'ASSEMBLY.json'),
        'scope': 'Rebuilt finite operators bound to their exact assembly. Common-label/mutable-basis realization, '
                 'pooled whole-call correlated-helper hosting, all-size compilation, precision/tape and analytic '
                 'transfer remain conditional. This does not instantiate the stricter PR458 bit ownership rule.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('bit', 'complex', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    a = ap.parse_args()
    result = check(a.bit, a.complex)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['decimal'])


if __name__ == '__main__':
    main()
