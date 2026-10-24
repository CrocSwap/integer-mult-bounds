#!/usr/bin/env python3
"""Replay the pinned controller checks in isolated temporary copies."""

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
LANES = Path('work/centre-encoding-campaign-20261014/lanes')
JOBS = [
    ('ordered-normal-forms', 'controller-review-20261017/check_review.py', ['REVIEW.json']),
    ('content-decoders', 'controller-review-20261017/check_decoder.py', ['DECODER-CHECKS.json']),
    ('current-codes', 'encoded-controller/one-pair-current-codes-20261018/check_and_emit.py', ['CHECKS.json', 'PROGRAM.json']),
    ('general-units', 'encoded-controller/one-pair-general-units-20261018/check_general_units.py', ['CHECKS.json']),
    ('physical-line-flags', 'encoded-controller/physical-monomial-compiler-20261018/check_line_flags.py', ['LINE-FLAGS.json']),
    ('canonical-prefix-screen', 'encoded-controller/physical-monomial-compiler-20261018/screen_warped_matching.py', ['WARPED-MATCHING.json']),
    ('retained-helpers', 'encoded-controller/retained-helper-completion-20261018/check_and_emit.py', ['CHECKS.json', 'HELPER-COMPLETION-PROGRAMS.json.gz']),
    ('one-pair-admission', 'history-encoding/one-pair-admission-20261018/check_admission.py', ['CHECKS.json']),
    ('terminal-and-hosting', 'bridge-review-20261017/matched-stage-review-20261018/check_terminal_and_hosting.py', ['TERMINAL-HOSTING-REVIEW.json']),
    ('d25-access', 'bridge-review-20261017/matched-stage-review-20261018/check_access.py', ['ACCESS-REVIEW.json']),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        path = HERE / item['package_path']
        data = path.read_bytes()
        require(sha(data) == item['sha256'], 'Source hash: ' + item['package_path'])
        if 'decompressed_sha256' in item:
            require(sha(gzip.decompress(data)) == item['decompressed_sha256'],
                    'Payload hash: ' + item['package_path'])
    adaptation = json.loads((HERE / 'PORTABLE-ADAPTATION.json').read_text())
    for kind in ('original', 'portable'):
        require(sha((HERE / adaptation[kind]).read_bytes()) == adaptation[kind + '_sha256'],
                'Portable source hash: ' + kind)
    return manifest


def payload(path, access=False):
    data = path.read_bytes()
    if path.suffix == '.gz':
        return gzip.decompress(data)
    if access:
        value = json.loads(data)
        value.pop('checker_sha256')
        return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return data


def run_job(job, optimized, output):
    label, relative, outputs = job
    mode = 'optimized' if optimized else 'normal'
    destination = output / mode / label
    destination.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='ordered-centre-', dir=output) as temporary:
        workspace = Path(temporary)
        shutil.copytree(HERE / 'frozen', workspace / 'frozen')
        if label == 'd25-access':
            shutil.copytree(HERE / 'portable', workspace / 'portable')
            script = workspace / 'portable/check_access.py'
        else:
            script = workspace / 'frozen' / LANES / relative
        command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + [str(script)]
        environment = dict(os.environ)
        environment.update({key: '1' for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')})
        started = time.monotonic()
        result = subprocess.run(command, cwd=workspace / 'frozen', env=environment,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        (destination / 'stdout.txt').write_text(result.stdout)
        require(result.returncode == 0, label + ' failed; see ' + str(destination / 'stdout.txt'))
        hashes = {}
        for name in outputs:
            relative_output = LANES / Path(relative).parent / name
            actual = workspace / 'frozen' / relative_output
            expected = HERE / 'frozen' / relative_output
            actual_payload = payload(actual, label == 'd25-access')
            require(actual_payload == payload(expected, label == 'd25-access'),
                    'Changed proof receipt: ' + label + '/' + name)
            shutil.copyfile(actual, destination / name)
            hashes[name] = {'file_sha256': sha(actual.read_bytes()), 'compared_payload_sha256': sha(actual_payload)}
        return {'id': label, 'mode': mode, 'seconds': round(time.monotonic() - started, 3),
                'checker': 'portable/check_access.py' if label == 'd25-access' else 'frozen/' + str(LANES / relative),
                'outputs': hashes, 'matches_frozen_receipts': True,
                'comparison': 'Decompressed bytes for gzip; omit only checker_sha256 for the path-only access adaptation; exact bytes otherwise.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mode', choices=['normal', 'optimized', 'both'], default='both')
    parser.add_argument('--only', choices=[item[0] for item in JOBS], action='append')
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    require(shutil.disk_usage(output).free >= 3 * 1024 ** 3, 'Keep at least 3 GiB free before replay')
    manifest = verify_sources()
    results = []
    for optimized in ([False, True] if args.mode == 'both' else [args.mode == 'optimized']):
        for job in JOBS:
            if args.only and job[0] not in args.only:
                continue
            print(('optimized' if optimized else 'normal') + ' ' + job[0], flush=True)
            results.append(run_job(job, optimized, output))
    if args.mode == 'both':
        normal = {r['id']: r['outputs'] for r in results if r['mode'] == 'normal'}
        for result in results:
            if result['mode'] == 'optimized':
                require(result['outputs'] == normal[result['id']], 'Normal and optimized outputs differ: ' + result['id'])
    receipt = {
        'status': 'PASS_ORDERED_CENTRE_INTERFACES', 'source_files': len(manifest['files']),
        'source_manifest_sha256': sha((HERE / 'SOURCES.json').read_bytes()),
        'replay_sha256': sha(Path(__file__).read_bytes()),
        'python': sys.version, 'jobs': results, 'mode': args.mode,
        'normal_optimized_equal': args.mode == 'both',
        'scope': 'Ordered algebra, exact finite source checks, and conditional local/host proofs. No new native phase compiler sweep, selected replay, all-size compiler proof, finite precision proof, or complete kappa calculation.',
    }
    (output / 'REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
