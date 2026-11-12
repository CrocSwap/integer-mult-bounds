"""Offline replay for the fixed 60-carrier BIT exterior-rank exclusion."""
import argparse
import gzip
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
    'RESULT.json': (300884, '42d7c43180690bcbd062fe011d3e4a0f12305d952e823afb34a1f76a4872b82b'),
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
    'predecessor/round24/SOURCES.tsv', 'predecessor/round24/verify.py',
    'predecessor/bit-price/verify.py',
})


def summary(raw):
    r = json.loads(raw)
    report = {k: r[k] for k in ('status', 'target', 'completed_carriers',
              'pending_carriers', 'new_sites', 'protected_paid_contact_count',
              'protected_exterior_output_count', 'terminal_arrival_inputs_deferred')}
    report['result_bytes'] = len(raw)
    report['result_sha256'] = sha256(raw).hexdigest()
    report['nonzero_paid_contact_markers'] = len(r['nonzero_protected_contact_markers'])
    report['nonzero_exterior_markers'] = len(r['nonzero_exterior_markers'])
    report['target_rank_seven_charts'] = len({c['target_chart'] for c in r['carriers']})
    report['carrier_event_ids'] = [c['event'] for c in r['carriers']]
    report['scopes'] = [{k: s[k] for k in ('source_scope', 'variables',
                       'equation_rank', 'joint_kernel_dimension',
                       'protected_only_coefficient_rank', 'exterior_only_coefficient_rank',
                       'exterior_scalar_marker_rank', 'exterior_basis_roles')}
                       for s in r['scopes']]
    report['directed_prices'] = [p['price'] for p in r['scopes'][0]['recipients'] if 'price' in p][0]
    return report


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
            target = scratch.joinpath(*path)
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


def regenerate(scratch, path, script, *args):
    raw = success(script, scratch, *args)
    if (len(raw), sha256(raw).hexdigest()) != EXPECTED[path]:
        raise ValueError(f'Byte mismatch: generated {path}')
    (scratch / path).write_bytes(raw)
    return raw


def reject(audit, scratch, data, assertion):
    forged = scratch / 'FORGED.json'
    forged.write_text(json.dumps(data), encoding='utf-8')
    result = invoke(audit, scratch, forged)
    if result.returncode != 1 or result.stdout or assertion not in result.stderr:
        raise ValueError('Independent audit did not reject the forged receipt')


def verify_carrier_input_clocks(scratch, raw):
    path = scratch / 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
    word = json.loads(gzip.decompress(path.read_bytes()))
    events = {c['event']: (c['owner'], c['index']) for c in json.loads(raw)['carriers']}
    markers = [0] * (word['public'] + word['owned_fields'])
    checked = 0
    for t, (op, role, *args) in enumerate(word['program']):
        if op == 'MOVE':
            if t in events:
                owner, index = events[t]
                if owner != role or markers[role]:
                    raise ValueError(f'Incoming owner has an earlier carrier marker at MOVE {t}')
                markers[role] = 1 << index
                checked += 1
        elif op == 'ADD':
            markers[role] ^= markers[args[0]]
        elif op == 'SWAP':
            peer = args[0]
            markers[role], markers[peer] = markers[peer], markers[role]
        elif op in ('INIT', 'CLEAR'):
            markers[role] = 0
        else:
            raise ValueError(f'Unexpected operation at event {t}: {op}')
    if checked != 60:
        raise ValueError(f'Expected 60 owner clocks, checked {checked}')


def controls(audit, scratch, raw):
    data = json.loads(raw)
    peer = next(p for c in data['carriers'] for p in c['live_other_coframed_sources'] if p['row'])
    peer['row'].append(max(peer['row']) + 1)
    reject(audit, scratch, data, b'assert source_rows[t]==')

    data = json.loads(raw)
    masks = data['nonzero_exterior_markers']
    del masks[next(iter(masks))]
    reject(audit, scratch, data, b"==r['nonzero_exterior_markers']")
    print('PASS_FORGED_COFRAMED_SOURCE_AND_EXTERIOR_MASK_REJECTION')


def main():
    if not __debug__:
        raise ValueError('Run with assertions enabled')
    package = Path(__file__).resolve().parent
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--inputs', type=Path, default=package / 'inputs')
    cli.add_argument('--controls', action='store_true')
    cli.add_argument('--write-result', type=Path, metavar='PATH',
                     help='save the authenticated detailed carrier receipt to a new file')
    args = cli.parse_args()
    with TemporaryDirectory(prefix='bit-carrier-exterior-') as temp:
        scratch = Path(temp)
        stage(package, args.inputs.resolve(), scratch)
        for prior in ('round22', 'round23', 'round24'):
            regenerate(scratch, f'{prior}/RESULT.json', scratch / prior / 'verify.py', '--seconds', 480)
        regenerate(scratch, 'bit-price/RESULT.json', scratch / 'bit-price/verify.py',
                   scratch / 'round24/RESULT.json')
        raw = regenerate(scratch, 'RESULT.json', package / 'verify.py', '--seconds', 480)
        if summary(raw) != json.loads((package / 'SUMMARY.json').read_text(encoding='utf-8')):
            raise ValueError('Mismatch: SUMMARY.json')
        verify_carrier_input_clocks(scratch, raw)
        audit = package / 'audit.py'
        if success(audit, scratch, scratch / 'RESULT.json') != (package / 'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: AUDIT.json')
        if args.controls:
            controls(audit, scratch, raw)
        if args.write_result:
            with args.write_result.open('xb') as output:
                output.write(raw)
    print('PASS_BIT_CHANGED_CARRIER_EXTERIOR impulses=60 source_ranks=88/88/148 kernel=0 expansions=0 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
