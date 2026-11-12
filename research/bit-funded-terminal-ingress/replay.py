"""Offline replay of the exact funded-ingress census and coupled split price."""

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

FROZEN = {
    'round22/RESULT.json': (726340, '6f4c3afc1185668de6e98ea1608170ae9db8ee5c2c5318b5d5a6577d609252e3'),
    'round23/RESULT.json': (5448489, '16863072b372547b6a062210da4d338704ce680ec22cd5e4e6702560c93a1bf7'),
    'RESULT.json': (8170267, '1acd03fec0213cda8c44f4914c4c0b0c2e2124d7a0dc0586689e80bbc0fb8646'),
}
REPLAY_FILES = frozenset({
    'AUDIT.json', 'SOURCES.tsv', 'SUMMARY.json', 'audit.py', 'verify.py',
    'inputs/pr7209/RESULT.json', 'inputs/pr7209/verify.py',
    'inputs/pr7244/PROPOSED-CLAIM.json', 'inputs/pr7258/SUMMARY.json',
    'inputs/research/paired-query-only-bit/EFREE-RESULT.json',
    'inputs/research/paired-query-only-bit/independent/interval_gate.py',
    'inputs/research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz',
    'predecessor/round22/SOURCES.tsv', 'predecessor/round22/verify.py',
    'predecessor/round23/SOURCES.tsv', 'predecessor/round23/verify.py',
    'price/AUDIT.stdout', 'price/RESULT.json', 'price/audit.py', 'price/verify.py',
})


def summary(raw):
    report = json.loads(raw)
    short = {key: value for key, value in report.items() if key != 'incidence'}
    short['receipt_bytes'] = len(raw)
    short['receipt_sha256'] = sha256(raw).hexdigest()
    short['literal_midpoint_incidences'] = sum(
        len(port['compatible_literal_charts']) for port in report['incidence']
    )
    short['paid_ingress_witnesses_by_scope'] = [
        sum(len(chart['paid_ingress']) for port in report['incidence']
            for chart in port['clocks'][i]['compatible_charts'])
        for i in range(len(report['scopes']))
    ]
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
            target = scratch.joinpath(*rel.parts[1:])
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


def reject(script, args, expected):
    result = call(script, args, expect_ok=False)
    if result.returncode != 1 or result.stdout or expected not in result.stderr:
        raise ValueError(f'{script.name} did not reject the forged receipt')


def controls(root, scratch, incidence_raw, price_raw):
    price = json.loads(price_raw)
    target = json.loads(incidence_raw)['target']
    assert price[target][2]['needed_singleton_expansions'] == 4
    price[target][2]['needed_singleton_expansions'] = 3
    price_path = scratch / 'PRICE.json'
    price_path.write_text(json.dumps(price), encoding='utf-8')
    reject(root / 'price/audit.py', (scratch / 'RESULT.json', price_path),
           b'== [7, 5, 4]')

    report = json.loads(incidence_raw)
    witness = next(w for port in report['incidence'] for clock in port['clocks']
                   for chart in clock['compatible_charts'] for w in chart['paid_ingress'])
    assert witness['after_cut'] == witness['event'] + 1
    witness['after_cut'] += 1
    incidence = scratch / 'RESULT.json'
    incidence.write_text(json.dumps(report), encoding='utf-8')
    reject(root / 'audit.py', (scratch, incidence),
           b"assert candidates==seen and all(v['after_cut']==v['event']+1")
    print('PASS_FORGED_PAID_CLOCK_AND_UNDERPRICED_THRESHOLD_REJECTION')


def main():
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=root / 'inputs')
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--write-incidence', type=Path, metavar='PATH',
                        help='save the verified full incidence receipt to a new file')
    args = parser.parse_args()
    with TemporaryDirectory(prefix='bit-funded-ingress-') as name:
        scratch = Path(name)
        stage(root, args.inputs.resolve(), scratch)
        for prior in ('round22', 'round23'):
            exact(scratch, f'{prior}/RESULT.json', scratch / prior / 'verify.py', (scratch, '--seconds', 480))
        raw = exact(scratch, 'RESULT.json', root / 'verify.py', (scratch, '--seconds', 480))
        if summary(raw) != json.loads((root / 'SUMMARY.json').read_text(encoding='utf-8')):
            raise ValueError('Mismatch: SUMMARY.json')
        incidence = scratch / 'RESULT.json'
        if call(root / 'audit.py', (scratch, incidence)).stdout != (root / 'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: AUDIT.json')
        price = call(root / 'price/verify.py', (scratch, incidence)).stdout
        if price != (root / 'price/RESULT.json').read_bytes():
            raise ValueError('Byte mismatch: price/RESULT.json')
        price_path = scratch / 'PRICE.json'
        price_path.write_bytes(price)
        if call(root / 'price/audit.py', (incidence, price_path)).stdout != (root / 'price/AUDIT.stdout').read_bytes():
            raise ValueError('Byte mismatch: price/AUDIT.stdout')
        if args.controls:
            controls(root, scratch, raw, price)
        if args.write_incidence:
            with args.write_incidence.open('xb') as output:
                output.write(raw)
    print('PASS_BIT_FUNDED_INGRESS ports=185 added_useful=0 returns=14 target=7/5/4 strict=8/6/unaffordable no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
