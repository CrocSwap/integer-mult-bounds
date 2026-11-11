"""Regenerate and authenticate the exact fixed-payload BIT quotient receipt."""

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

RESULT_SHA = '6f4c3afc1185668de6e98ea1608170ae9db8ee5c2c5318b5d5a6577d609252e3'
RESULT_BYTES = 726340
REPLAY_FILES = frozenset({
    'AUDIT.json',
    'SOURCES.tsv',
    'SUMMARY.json',
    'audit.py',
    'inputs/pr7209/RESULT.json',
    'inputs/pr7209/verify.py',
    'inputs/pr7244/PROPOSED-CLAIM.json',
    'inputs/research/paired-query-only-bit/EFREE-RESULT.json',
    'inputs/research/paired-query-only-bit/independent/interval_gate.py',
    'inputs/research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz',
    'verify.py',
})


def summary(raw):
    report = json.loads(raw)
    short = {key: value for key, value in report.items() if key != 'scope'}
    short['scopes'] = []
    for s in report['scope']:
        endpoint = s['endpoint_consistency']
        short['scopes'].append({
            'clock': s['scope'],
            'raw_quotient_stock': s['compatible_stock_upper'],
            'endpoint_preserving_independent_stock': endpoint['endpoint_preserving_independent_upper'],
            'endpoint_preserving_nonzero_stock': endpoint['endpoint_preserving_nonzero_upper'],
            'endpoint_block_choices': sum(x['tested_choices'] for x in endpoint['blocks']),
            'endpoint_block_sizes': [len(x['banks']) for x in endpoint['blocks']],
            'target_clearing_assignments_pending': s['unresolved_target_clearing_assignments_within_scope'],
            'raw_quotient_price': s['raw_quotient_price'],
            'endpoint_preserving_price': s['endpoint_preserving_price'],
        })
    short['receipt_bytes'] = len(raw)
    short['receipt_sha256'] = sha256(raw).hexdigest()
    return short


def authenticate(root, inputs):
    seen = set()
    for row in (root / 'REPLAY.sha256').read_text(encoding='ascii').splitlines():
        digest, key = row.split('  ', 1)
        rel = PurePosixPath(key)
        if rel.as_posix() != key or key not in REPLAY_FILES or key in seen:
            raise ValueError(f'Unexpected or duplicate replay path: {key}')
        seen.add(key)
        path = inputs.joinpath(*rel.parts[1:]) if rel.parts[0] == 'inputs' else root / rel
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
    if seen != REPLAY_FILES:
        raise ValueError(f'Missing replay paths: {sorted(REPLAY_FILES - seen)}')


def call(script, args, expect_ok=True):
    command = [sys.executable, '-I', '-B', str(script), *map(str, args)]
    result = subprocess.run(command, capture_output=True, check=False)
    if expect_ok and (result.returncode or result.stderr):
        sys.stderr.buffer.write(result.stderr)
        raise ValueError(f'{script.name} did not finish cleanly (exit {result.returncode})')
    return result


def audit_mutation(root, inputs, path, raw):
    report = json.loads(raw)
    endpoint = report['scope'][0]['endpoint_consistency']
    assert endpoint['endpoint_preserving_independent_upper'] == 6
    endpoint['endpoint_preserving_independent_upper'] = 7
    path.write_text(json.dumps(report), encoding='utf-8')
    result = call(root / 'audit.py', (inputs, path), expect_ok=False)
    expected = b"assert independent == endpoint['endpoint_preserving_independent_upper']"
    if result.returncode != 1 or result.stdout or expected not in result.stderr:
        raise ValueError('Independent audit did not reject a forged endpoint stock')
    print('PASS_MIXED_SOURCE_CONTROLS_AND_FORGED_ENDPOINT_REJECTION')


def main():
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=root / 'inputs')
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    inputs = args.inputs.resolve()
    authenticate(root, inputs)
    raw = call(root / 'verify.py', (inputs, '--seconds', 480)).stdout
    if len(raw) != RESULT_BYTES or sha256(raw).hexdigest() != RESULT_SHA:
        raise ValueError('Byte mismatch: generated RESULT.json')
    if summary(raw) != json.loads((root / 'SUMMARY.json').read_text(encoding='utf-8')):
        raise ValueError('Mismatch: SUMMARY.json')
    with TemporaryDirectory(prefix='bit-prebirth-') as scratch:
        path = Path(scratch) / 'RESULT.json'
        path.write_bytes(raw)
        audit = call(root / 'audit.py', (inputs, path)).stdout
        if audit != (root / 'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: AUDIT.json')
        if args.controls:
            audit_mutation(root, inputs, path, raw)
    print('PASS_BIT_FIXED_PAYLOAD_QUOTIENT literal=6 quiet=12 banks=22 pending=0 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
