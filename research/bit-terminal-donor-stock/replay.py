"""Offline exact replay of the old-payload BIT donor and charged-split stock bounds."""

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

FROZEN = {
    'round22/RESULT.json': (
        726340, '6f4c3afc1185668de6e98ea1608170ae9db8ee5c2c5318b5d5a6577d609252e3'
    ),
    'RESULT.json': (
        5448489, '16863072b372547b6a062210da4d338704ce680ec22cd5e4e6702560c93a1bf7'
    ),
}
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
    'predecessor/SOURCES.tsv',
    'predecessor/verify.py',
    'verify.py',
})


def summary(raw):
    report = json.loads(raw)
    short = {key: value for key, value in report.items() if key != 'scopes'}
    short['scopes'] = []
    for scope in report['scopes']:
        quotient = scope['marked_quotient_rank']
        singleton = scope['isolated_singleton_projection_rank']
        short['scopes'].append({
            'scope': scope['scope'],
            'donors': len(scope['donors']),
            'donors_with_nonzero_old_marked_projection': scope['donors_with_nonzero_old_marked_projection'],
            'marked_quotient_rank': quotient['rank'],
            'marked_quotient_witnesses': quotient['assignments'],
            'singleton_projection_rank': singleton['rank'],
            'singleton_witnesses': singleton['assignments'],
            'stock_upper': scope['raw_stock_upper'],
            'price_upper': scope['price_upper'],
        })
    short['receipt_bytes'] = len(raw)
    short['receipt_sha256'] = sha256(raw).hexdigest()
    return short


def stage(root, inputs, scratch):
    seen = set()
    for row in (root / 'REPLAY.sha256').read_text(encoding='ascii').splitlines():
        digest, key = row.split('  ', 1)
        rel = PurePosixPath(key)
        if rel.as_posix() != key or key not in REPLAY_FILES or key in seen:
            raise ValueError(f'Unexpected or duplicate replay path: {key}')
        seen.add(key)
        path = inputs.joinpath(*rel.parts[1:]) if rel.parts[0] == 'inputs' else root / rel
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
        if rel.parts[0] in ('inputs', 'predecessor'):
            base = scratch / 'round22' if rel.parts[0] == 'predecessor' else scratch
            target = base.joinpath(*rel.parts[1:])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    if seen != REPLAY_FILES:
        raise ValueError(f'Missing replay paths: {sorted(REPLAY_FILES - seen)}')


def call(script, args, expect_ok=True):
    command = [sys.executable, '-I', '-B', str(script), *map(str, args)]
    result = subprocess.run(command, capture_output=True, check=False)
    if expect_ok and (result.returncode or result.stderr):
        sys.stderr.buffer.write(result.stderr)
        raise ValueError(f'{script.name} did not finish cleanly (exit {result.returncode})')
    return result


def exact(scratch, name, script, args):
    raw = call(script, args).stdout
    if (len(raw), sha256(raw).hexdigest()) != FROZEN[name]:
        raise ValueError(f'Byte mismatch: generated {name}')
    (scratch / name).write_bytes(raw)
    return raw


def audit_mutation(root, scratch, path, raw):
    report = json.loads(raw)
    assert report['scopes'][1]['raw_stock_upper'] == 14
    report['scopes'][1]['raw_stock_upper'] = 15
    path.write_text(json.dumps(report), encoding='utf-8')
    result = call(root / 'audit.py', (scratch, path), expect_ok=False)
    expected = b"assert s['raw_stock_upper'] == min(22,12+sum(upper))"
    if result.returncode != 1 or result.stdout or expected not in result.stderr:
        raise ValueError('Independent audit did not reject the forged quiet stock')
    print('PASS_DONOR_CONTROLS_AND_FORGED_QUIET_STOCK_REJECTION')


def main():
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=root / 'inputs')
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    with TemporaryDirectory(prefix='bit-terminal-donors-') as name:
        scratch = Path(name)
        stage(root, args.inputs.resolve(), scratch)
        exact(scratch, 'round22/RESULT.json', scratch / 'round22/verify.py', (scratch, '--seconds', 480))
        raw = exact(scratch, 'RESULT.json', root / 'verify.py', (scratch, '--seconds', 480))
        if summary(raw) != json.loads((root / 'SUMMARY.json').read_text(encoding='utf-8')):
            raise ValueError('Mismatch: SUMMARY.json')
        path = scratch / 'RESULT.json'
        audit = call(root / 'audit.py', (scratch, path)).stdout
        if audit != (root / 'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: AUDIT.json')
        if args.controls:
            audit_mutation(root, scratch, path, raw)
    print('PASS_BIT_TERMINAL_DONOR_STOCK donors=523 live=12 quiet=14 charged_cases=10 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
