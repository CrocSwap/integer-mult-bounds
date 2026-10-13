#!/usr/bin/env python3
"""Join the rebuilt PR510 bit supplier to PR535's complete finite complex replay."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check(bit, complex_dir, local):
    package = ROOT / 'research/post-center-rank4-global'
    actual = read(bit / 'RESULT.json')
    expected = read(package / 'inputs/PR510-EXPECTED.json')['nine']
    checked = {'bit_lower': 'bit_lower', 'bit_lower_decimal': 'bit_lower_decimal',
               'bit_profile': 'profile', 'bit': 'bit', 'stages': 'stages', 'replicas': 'replicas'}
    for key, frozen in checked.items():
        require(actual[key] == expected[frozen], 'Bit dependency differs: ' + key)
    hosted = read(bit / 'v9/hosted/AUDIT.json')
    require(hosted['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT', 'Bit physical audit')
    require(hosted['hosted_residuals'] == 138240 and hosted['bank_assignments'] == 0, 'Bit owner counts')
    columns = read(bit / 'columns_k4.json')
    require(columns['formal_columns_checked'] == 1440 and columns['payload_prefix_bits'] == expected['nine_stage_payload_bits'], 'Bit columns')
    require(len(columns['negative_controls']) == 18 and all(x['rejected'] for x in columns['negative_controls']), 'Bit controls')
    bindings = []
    for name in ['CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'RESIDUAL-ADAPTERS.json', 'CLIFFORD-RECIPES.json']:
        frozen = package / 'evidence/local' / name
        require(read(local / name) == read(frozen), 'Complex finite dependency differs: ' + name)
        bindings.append({'path': str(frozen.relative_to(ROOT)), 'sha256': hashlib.sha256(frozen.read_bytes()).hexdigest()})
    require(read(local / 'CLIFFORD-REVIEW.json')['all_child_equalities_include_global_phase'], 'Complex phases')
    require(read(local / 'INDEPENDENT-LOCAL-REPLAY.json')['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'Complex scalar replay')
    answer = read(complex_dir / 'audit/EXACT-ASSEMBLY.json')
    require(answer['bit_lower'] == actual['bit_lower'], 'Assembly bit rate')
    require(answer['kappa'] == read(package / 'EXPECTED.json')['kappa'], 'Assembly headline')
    require(len(answer['strict_outer_constraints']) == 47, 'Outer constraint count')
    return {'status': 'PASS_REBUILT_BIT_AND_COMPLEX_BINDINGS', 'kappa': answer['kappa'],
            'bit_fields': checked, 'complex_bindings': bindings,
            'scope': 'Rebuilt finite operators and invoice bound to exact composition. All-size realization and analytic interfaces remain conditional.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ['bit', 'complex', 'local', 'out']:
        ap.add_argument('--' + name, type=Path, required=True)
    a = ap.parse_args()
    result = check(a.bit, a.complex, a.local)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['kappa'])


if __name__ == '__main__':
    main()
