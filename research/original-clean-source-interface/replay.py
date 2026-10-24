#!/usr/bin/env python3
"""Replay the three original-frame component reviews in private copies."""

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
CONTENT = LANES / 'residual-syndrome/physical-algebra/review-gauss/original-clean-source'
PHYSICAL = LANES / 'paired-package-review/original-clean-native-review'
OWNERS = LANES / 'paired-package-review/original-owner-review'
JOBS = [
    ('content', 'frozen/' + str(CONTENT / 'check_review.py'), CONTENT / 'CHECK.json'),
    ('physical', 'portable/check_physical_binding.py', PHYSICAL / 'CHECKS.json'),
    ('owners', 'portable/check_binding.py', OWNERS / 'CHECKS.json'),
]


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        raw = (HERE / item['package_path']).read_bytes()
        require(digest(raw) == item['sha256'], 'Source hash: ' + item['package_path'])
        if 'decompressed_sha256' in item:
            require(digest(gzip.decompress(raw)) == item['decompressed_sha256'], 'Gzip payload hash')
    for item in json.loads((HERE / 'PORTABLE-ADAPTATIONS.json').read_text()):
        for kind in ('original', 'portable'):
            require(digest((HERE / item[kind]).read_bytes()) == item[kind + '_sha256'], 'Portable checker hash')
    return manifest


def run_one(job, optimized, output):
    label, script, receipt = job
    mode = 'optimized' if optimized else 'normal'
    destination = output / mode / label
    destination.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='original-clean-', dir=output) as temporary:
        workspace = Path(temporary)
        for folder in ['frozen', 'portable', 'archive-members']:
            shutil.copytree(HERE / folder, workspace / folder)
        command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + [str(workspace / script)]
        if label != 'content':
            command += ['--members', str(workspace / 'archive-members'), '--out', str(workspace / 'frozen' / receipt)]
        environment = dict(os.environ)
        environment.update({key: '1' for key in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS']})
        started = time.monotonic()
        result = subprocess.run(command, cwd=workspace / 'frozen', env=environment, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        (destination / 'stdout.txt').write_text(result.stdout)
        require(result.returncode == 0, label + ' failed; see ' + str(destination / 'stdout.txt'))
        raw = (workspace / 'frozen' / receipt).read_bytes()
        require(raw == (HERE / 'frozen' / receipt).read_bytes(), 'Changed receipt: ' + label)
        (destination / receipt.name).write_bytes(raw)
        return {'id': label, 'mode': mode, 'script': script, 'seconds': round(time.monotonic() - started, 3),
                'receipt_sha256': digest(raw), 'frozen_receipt_byte_equal': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mode', choices=['normal', 'optimized', 'both'], default='both')
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    require(shutil.disk_usage(output).free >= 3 * 1024 ** 3, 'Keep at least 3 GiB free before replay')
    manifest = verify_sources()
    results = []
    for optimized in ([False, True] if args.mode == 'both' else [args.mode == 'optimized']):
        for job in JOBS:
            print(('optimized' if optimized else 'normal') + ' ' + job[0], flush=True)
            results.append(run_one(job, optimized, output))
    if args.mode == 'both':
        normal = {r['id']: r['receipt_sha256'] for r in results if r['mode'] == 'normal'}
        require(all(r['receipt_sha256'] == normal[r['id']] for r in results), 'Normal and optimized receipts differ')
    receipt = {'status': 'PASS_ORIGINAL_CLEAN_SOURCE_INTERFACE', 'source_files': len(manifest['files']),
               'source_manifest_sha256': digest((HERE / 'SOURCES.json').read_bytes()),
               'replay_sha256': digest(Path(__file__).read_bytes()), 'python': sys.version,
               'mode': args.mode, 'jobs': results, 'normal_optimized_equal': args.mode == 'both',
               'scope': 'Fresh all-column ordered content, physical-helper source binding, and exact original owner binding. Inherited raw native kernel and phase-history proofs are not rerun; no global data controller, parser admission, full costs, or kappa claim.'}
    (output / 'REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
