#!/usr/bin/env python3
"""Replay the three frozen phase-access reviews in private copies."""

import argparse
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
BASE = 'work/centre-encoding-campaign-20261014/'
JOBS = [
    ('walsh', 'lanes/interface-proof/review_walsh_frames.py', None,
     'WALSH-FRAME-REVIEW.json', 'WALSH-FRAME-REVIEW.json'),
    ('rational', 'lanes/independent-review-20261017/phase-class-reduction-review-20261020/check_review.py',
     '--out', 'CHECKS.json', 'verified-normal/CHECKS.json'),
    ('dyadic', 'lanes/bridge-review-20261017/dyadic-phase-capture-review-20261020/check_review.py', None,
     'REVIEW.json', 'REVIEW.json'),
]


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def verify():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        raw = (HERE / item['package_path']).read_bytes()
        need(len(raw) == item['bytes'] and digest(raw) == item['sha256'],
             'Frozen source mismatch: ' + item['package_path'])
        if 'decompressed_sha256' in item:
            need(digest(gzip.decompress(raw)) == item['decompressed_sha256'],
                 'Frozen payload mismatch: ' + item['package_path'])
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    need(shutil.disk_usage(output).free >= 3 * 1024 ** 3, 'Keep at least 3 GiB free')
    manifest = verify()
    runs = []
    env = dict(os.environ)
    env.update({name: '1' for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS',
                                     'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')})
    for optimized in (False, True):
        mode = 'optimized' if optimized else 'normal'
        for label, script, option, receipt, expected in JOBS:
            saved = output / mode / label
            saved.mkdir(parents=True)
            with tempfile.TemporaryDirectory(prefix='phase-access-', dir=output) as temporary:
                repository = Path(temporary) / 'repository'
                shutil.copytree(HERE / 'frozen', repository)
                executable = repository / BASE / script
                generated = Path(temporary) / 'generated' if option else executable.parent
                command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + [str(executable)]
                if option:
                    command += [option, str(generated)]
                start = time.monotonic()
                process = subprocess.run(command, cwd=repository, env=env, text=True,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
                (saved / 'stdout.txt').write_text(process.stdout)
                need(process.returncode == 0, label + ' failed: ' + str(saved / 'stdout.txt'))
                raw = (generated / receipt).read_bytes()
                frozen = (HERE / 'frozen' / BASE / Path(script).parent / expected).read_bytes()
                need(raw == frozen, 'Complete receipt bytes differ: ' + label)
                (saved / receipt).write_bytes(raw)
                runs.append({'job': label, 'mode': mode, 'seconds': round(time.monotonic() - start, 3),
                             'receipt_sha256': digest(raw), 'receipt': str((saved / receipt).relative_to(output)),
                             'complete_frozen_receipt_byte_equal': True})
                print('PASS ' + mode + ' ' + label, flush=True)
    for label, *_ in JOBS:
        pair = [r['receipt_sha256'] for r in runs if r['job'] == label]
        need(len(pair) == 2 and pair[0] == pair[1], 'Normal and optimized receipt mismatch')
    verify()
    result = {'status': 'PASS_PHASE_ACCESS_ANNEX', 'source_files': len(manifest['files']),
              'source_manifest_sha256': digest((HERE / 'SOURCES.json').read_bytes()),
              'replay_sha256': digest(Path(__file__).read_bytes()), 'runs': runs,
              'normal_optimized_byte_equal': True, 'source_files_unchanged': True,
              'source_code_adaptations': 0,
              'scope': 'Exact growing-frame kernels and route ranks; rational and dyadic scalar capture; conditional common-frame geometry. No emitted full native capture, source-access or owner program, recursive supplier, or kappa improvement.'}
    (output / 'REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
