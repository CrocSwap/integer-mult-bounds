#!/usr/bin/env python3
"""Run the pinned phase-caller checks in private repository copies."""

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ORIGIN = '/Users/aliromman/Projects/IntegerMultiplicationBounds'
LANES = 'work/centre-encoding-campaign-20261014/lanes/'
JOBS = [
    ('local', 'controller-followthrough-20261017/phase-coded-clean-20261020/emit_phase_coded.py',
     'final-normal', ['CHECKS.json', 'PHASE-CODED.json.gz'], '--out'),
    ('triple', 'native-escape-20261017/owner-review/phase-coded-triple-review-20261020/check_review.py',
     '.', ['CHECKS.json', 'BLOCK-PROOF.json', 'FRAME-CERTIFICATE.json', 'FULL-SHEARS.json',
           'SOURCE-MANIFEST.json', 'TERMINAL-PHASES.json'], '--out'),
    ('chain', 'native-escape-20261017/phase-coded-chain-20261020/check_chain.py',
     'run-normal', ['CHECKS.json'], '--out'),
    ('geometry', 'bridge-access-20261017/phase-section-review-20261018/check_review.py',
     '.', ['CHECKS.json'], None),
    ('translation', 'native-escape-20261017/translation-service-review/check_service_review.py',
     '.', ['REVIEW.json'], None),
    ('inplace', 'native-escape-20261017/inplace-service-review/check_inplace_review.py',
     '.', ['REVIEW.json'], None),
    ('closure', 'native-escape-20261017/owner-review/unitary-code-closure-binding-20261020/check_binding.py',
     '.', ['CHECKS.json', 'SOURCE-MANIFEST.json'], '--out'),
]


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_inputs():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        raw = (HERE / item['package_path']).read_bytes()
        require(digest(raw) == item['sha256'], 'Source hash: ' + item['package_path'])
        if 'decompressed_sha256' in item:
            require(digest(gzip.decompress(raw)) == item['decompressed_sha256'], 'Payload hash')
    adaptation = json.loads((HERE / 'PORTABLE-ADAPTATION.json').read_text())
    for key in ('original', 'portable'):
        require(digest((HERE / adaptation[key]).read_bytes()) == adaptation[key + '_sha256'],
                'Adaptation hash: ' + key)
    return manifest, adaptation


def load_outputs(folder, names):
    result = {}
    for name in names:
        raw = (folder / name).read_bytes()
        payload = gzip.decompress(raw) if name.endswith('.gz') else raw
        result[name] = {'raw': raw, 'payload': payload, 'value': json.loads(payload)}
    for record in result.values():
        value = record['value']
        if not isinstance(value, dict):
            continue
        for name, pin in value.get('output_sha256', {}).items():
            require(name in result and digest(result[name]['raw']) == pin,
                    'Generated output hash: ' + name)
        if 'source_manifest_sha256' in value:
            require(digest(result['SOURCE-MANIFEST.json']['raw']) == value['source_manifest_sha256'],
                    'Generated source manifest hash')
        if 'payload_decompressed_sha256' in value:
            payloads = [v for name, v in result.items() if name.endswith('.gz')]
            require(len(payloads) == 1 and digest(payloads[0]['payload']) == value['payload_decompressed_sha256'],
                    'Generated compressed payload hash')
    return result


def transform(value, string_map):
    if isinstance(value, str):
        return string_map(value)
    if isinstance(value, list):
        return [transform(v, string_map) for v in value]
    if isinstance(value, dict):
        return {string_map(k): transform(v, string_map) for k, v in value.items()}
    return value


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def normalized(records, root, self_hashes=None):
    def path_and_self(value):
        for prefix in (str(root), ORIGIN):
            if value.startswith(prefix + '/'):
                return '<repo>/' + value[len(prefix) + 1:]
        return (self_hashes or {}).get(value, value)
    values = {name: transform(record['value'], path_and_self) for name, record in records.items()}
    hashes = {}
    for name, record in records.items():
        if name not in ('CHECKS.json', 'REVIEW.json'):
            canonical = digest(encoded(values[name]))
            hashes[digest(record['raw'])] = canonical
            hashes[digest(record['payload'])] = canonical
    return {name: transform(value, lambda s: hashes.get(s, s)) for name, value in values.items()}


def run_one(job, optimized, output, adaptation):
    label, script, frozen_folder, names, option = job
    mode = 'optimized' if optimized else 'normal'
    saved = output / mode / label
    saved.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='phase-callers-', dir=output) as temporary:
        repo = Path(temporary) / 'repo'
        shutil.copytree(HERE / 'frozen', repo)
        script_path = repo / LANES / script
        if label == 'translation':
            shutil.copyfile(HERE / adaptation['portable'], repo / adaptation['runtime_path'])
        command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + [str(script_path)]
        produced = Path(temporary) / 'generated' if option else script_path.parent
        if option:
            command += [option, str(produced)]
        env = dict(os.environ)
        env.update({key: '1' for key in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS']})
        start = time.monotonic()
        completed = subprocess.run(command, cwd=repo, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, check=False)
        (saved / 'stdout.txt').write_text(completed.stdout)
        require(completed.returncode == 0, label + ' failed; see ' + str(saved / 'stdout.txt'))
        actual = load_outputs(produced, names)
        expected = load_outputs(HERE / 'frozen' / LANES / Path(script).parent / frozen_folder, names)
        self_hashes = None
        if label == 'translation':
            require(actual['REVIEW.json']['value']['checker_sha256'] == adaptation['portable_sha256'],
                    'Portable checker receipt hash')
            self_hashes = {adaptation['portable_sha256']: adaptation['original_sha256']}
        left, right = normalized(actual, repo, self_hashes), normalized(expected, ORIGIN)
        require(left == right, 'Changed normalized output: ' + label)
        hashes = {}
        for name, record in actual.items():
            (saved / name).write_bytes(record['raw'])
            hashes[name] = {'sha256': digest(record['raw']), 'canonical_sha256': digest(encoded(left[name])),
                            'frozen_byte_equal': record['raw'] == expected[name]['raw']}
        return {'id': label, 'mode': mode, 'seconds': round(time.monotonic() - start, 3),
                'outputs': hashes, 'all_canonical_outputs_equal': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mode', choices=['normal', 'optimized', 'both'], default='both')
    parser.add_argument('--only', choices=[job[0] for job in JOBS])
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    require(shutil.disk_usage(output).free >= 3 * 1024 ** 3, 'Keep at least 3 GiB free')
    manifest, adaptation = verify_inputs()
    jobs = [job for job in JOBS if args.only in (None, job[0])]
    runs = []
    for optimized in ([False, True] if args.mode == 'both' else [args.mode == 'optimized']):
        for job in jobs:
            print(('optimized' if optimized else 'normal') + ' ' + job[0], flush=True)
            runs.append(run_one(job, optimized, output, adaptation))
    if args.mode == 'both':
        normal = {r['id']: r['outputs'] for r in runs if r['mode'] == 'normal'}
        for run in runs:
            require(all(v['canonical_sha256'] == normal[run['id']][n]['canonical_sha256']
                        for n, v in run['outputs'].items()), 'Normal and optimized output mismatch')
    verify_inputs()
    receipt = {'status': 'PASS_PHASE_CODED_CALLERS', 'mode': args.mode, 'only': args.only,
               'source_files': len(manifest['files']), 'source_manifest_sha256': digest((HERE / 'SOURCES.json').read_bytes()),
               'replay_sha256': digest(Path(__file__).read_bytes()), 'python': sys.version,
               'jobs': runs, 'normal_optimized_equal': args.mode == 'both',
               'comparison': 'All output fields retained. Normalize repository path prefixes, validated hashes of normalized generated artifacts, and the one input-only portable checker self-hash.',
               'scope': 'Local 640-column transcript, independent D25 triple, actual D73 chain, section spectrum, translation services, and corrected current-scalar closure binding. Native spatial kernels and general-width proofs remain separate pinned proof premises. No global host, full map price, recursive common-q consumer, or kappa gain.'}
    (output / 'REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
