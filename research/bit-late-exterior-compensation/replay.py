"""Offline replay for late BIT compensation and the fixed-prebirth quotient bound."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

EXPECTED = {
    'round22/RESULT.json': (726340, '6f4c3afc1185668de6e98ea1608170ae9db8ee5c2c5318b5d5a6577d609252e3'),
    'round23/RESULT.json': (5448489, '16863072b372547b6a062210da4d338704ce680ec22cd5e4e6702560c93a1bf7'),
    'round24/RESULT.json': (8170267, '1acd03fec0213cda8c44f4914c4c0b0c2e2124d7a0dc0586689e80bbc0fb8646'),
    'bit-price/RESULT.json': (2737, '3583ea672516c4def2d3973fcc5fd75e8903c2ad9f6c7154df4df1fd1bb349c7'),
    'PRIOR.json': (300884, '42d7c43180690bcbd062fe011d3e4a0f12305d952e823afb34a1f76a4872b82b'),
    'RESULT.json': (16740, 'aac28bfb7736f6d43e92d06e2c1d0ce1ca347604c62f7129882def63244dd50c'),
}
SCRATCH_CODE = frozenset({'SOURCES.tsv', 'audit.py', 'prior.py', 'verify.py'})
REPLAY_FILES = SCRATCH_CODE | frozenset({
    'AUDIT.json', 'RESULT.json',
    'inputs/pr7209/RESULT.json', 'inputs/pr7209/verify.py',
    'inputs/pr7244/PROPOSED-CLAIM.json', 'inputs/pr7258/SUMMARY.json',
    'inputs/research/paired-query-only-bit/EFREE-RESULT.json',
    'inputs/research/paired-query-only-bit/independent/interval_gate.py',
    'inputs/research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz',
    'predecessor/round22/SOURCES.tsv', 'predecessor/round22/verify.py',
    'predecessor/round23/SOURCES.tsv', 'predecessor/round23/verify.py',
    'predecessor/round24/SOURCES.tsv', 'predecessor/round24/verify.py',
    'predecessor/round25/AUDIT.json', 'predecessor/round25/audit.py',
    'predecessor/bit-price/verify.py',
})
SINGLETONS = (0, 1, 2, 3, 4, 5, 6, 10, 14, 17)


def stage(package, input_root, scratch):
    seen = set()
    for line in (package / 'REPLAY.sha256').read_text(encoding='ascii').splitlines():
        digest, key = line.split('  ', 1)
        rel = PurePosixPath(key)
        if rel.as_posix() != key or key not in REPLAY_FILES or key in seen:
            raise ValueError(f'Unexpected or duplicate replay path: {key}')
        seen.add(key)
        category, *path = rel.parts
        source = input_root.joinpath(*path) if category == 'inputs' else package / rel
        raw = source.read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
        if category in ('inputs', 'predecessor'):
            target = scratch.joinpath('inputs', *path)
        elif key in SCRATCH_CODE:
            target = scratch / rel
        else:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    if seen != REPLAY_FILES:
        raise ValueError(f'Missing replay paths: {sorted(REPLAY_FILES - seen)}')


def invoke(script, *args):
    return subprocess.run([sys.executable, '-I', '-B', str(script), *map(str, args)],
                          capture_output=True, check=False)


def success(script, *args):
    result = invoke(script, *args)
    if result.returncode or result.stderr:
        sys.stderr.buffer.write(result.stderr)
        raise ValueError(f'{script.name} did not finish cleanly (exit {result.returncode})')
    return result.stdout


def regenerate(root, path, script, *args):
    raw = success(script, *args)
    if (len(raw), sha256(raw).hexdigest()) != EXPECTED[path]:
        raise ValueError(f'Byte mismatch: generated {path}')
    (root / path).write_bytes(raw)
    return raw


def verify_quotient(result, audit):
    expected = [[bank, dim] for bank, dim in
                zip(SINGLETONS, audit['unrestricted_fixed_trace_expansions'], strict=True) if dim]
    if result['scope'][-1]['expansions'] != expected:
        raise ValueError('Independent fixed-prebirth quotient mismatch')
    if not expected and any(scope['expansions'] for scope in result['scope'][:-1]):
        raise ValueError('Constrained quotient exceeds the independent unrestricted bound')


def controls(scratch, raw, independent):
    forged = json.loads(raw)
    forged['scope'][2]['rank'] -= 1
    forged['scope'][2]['nullity'] += 1
    (scratch / 'RESULT.json').write_text(json.dumps(forged), encoding='utf-8')
    rejected = invoke(scratch / 'audit.py')
    if (rejected.returncode != 1 or rejected.stdout or
            b'assert ranks == [x["rank"]' not in rejected.stderr):
        raise ValueError('Independent audit did not reject the forged compensation rank')
    forged = json.loads(raw)
    forged['scope'][-1]['expansions'] = [[SINGLETONS[0], 1]]
    try:
        verify_quotient(forged, independent)
    except ValueError as error:
        if str(error) != 'Independent fixed-prebirth quotient mismatch':
            raise
    else:
        raise ValueError('Independent audit did not reject the forged quotient expansion')
    print('PASS_FORGED_COMPENSATION_RANK_AND_PREBIRTH_EXPANSION_REJECTION')


def main():
    if not __debug__:
        raise ValueError('Run with assertions enabled')
    package = Path(__file__).resolve().parent
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--inputs', type=Path, default=package / 'inputs')
    cli.add_argument('--controls', action='store_true')
    cli.add_argument('--write-carriers', type=Path, metavar='PATH',
                     help='save the authenticated predecessor carrier detail to a new file')
    args = cli.parse_args()
    with TemporaryDirectory(prefix='bit-late-compensation-') as temp:
        scratch = Path(temp)
        inputs = scratch / 'inputs'
        stage(package, args.inputs.resolve(), scratch)
        for prior in ('round22', 'round23', 'round24'):
            regenerate(inputs, f'{prior}/RESULT.json', inputs / prior / 'verify.py', inputs, '--seconds', 480)
        regenerate(inputs, 'bit-price/RESULT.json', inputs / 'bit-price/verify.py', inputs,
                   inputs / 'round24/RESULT.json')
        predecessor = regenerate(scratch, 'PRIOR.json', scratch / 'prior.py', inputs, '--seconds', 480)
        prior_audit = inputs / 'round25/audit.py'
        prior_audit.with_name('SOURCES.tsv').write_bytes((scratch / 'SOURCES.tsv').read_bytes())
        if success(prior_audit, inputs, scratch / 'PRIOR.json') != prior_audit.with_name('AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: regenerated predecessor audit')
        raw = regenerate(scratch, 'RESULT.json', scratch / 'verify.py')
        if raw != (package / 'RESULT.json').read_bytes():
            raise ValueError('Byte mismatch: checked-in RESULT.json')
        audit = success(scratch / 'audit.py')
        if audit != (package / 'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: independently regenerated AUDIT.json')
        report = json.loads(raw)
        independent = json.loads(audit)
        verify_quotient(report, independent)
        prior_price = next(r['price'] for r in json.loads(predecessor)['scopes'][-1]['recipients'] if 'price' in r)
        if any(scope['price'] != prior_price for scope in report['scope']):
            raise ValueError('Exact inherited tariff differs from the late scope prices')
        if args.controls:
            controls(scratch, raw, independent)
        if args.write_carriers:
            with args.write_carriers.open('xb') as output:
                output.write(predecessor)
    print('PASS_BIT_LATE_COMPENSATION ranks=148/148/100/0 nullities=0/0/48/148 fixed_prebirth_expansions=0/10 pooled_extra_dimensions=9_each no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
