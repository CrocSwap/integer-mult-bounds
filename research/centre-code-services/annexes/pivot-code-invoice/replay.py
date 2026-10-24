#!/usr/bin/env python3
"""Replay the frozen pivot word, prior review, and invoice-domain check."""

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
OLD_ROOT = Path('/Users/aliromman/Projects/IntegerMultiplicationBounds')
BASE = 'frozen/work/centre-encoding-campaign-20261014/lanes/'
PIVOT = BASE + 'new-core-transfer-20261017/low-displacement-20261020/pivot-codes/'
REVIEW = BASE + 'bridge-review-20261017/moving-code-review-20261020/'
JOBS = [
    ('pivot', PIVOT + 'emit_pivot_codes.py', True,
     PIVOT + 'final-normal/', ['CHECKS.json', 'PIVOT-CODES.json']),
    ('prior_review', REVIEW + 'check_moving_code.py', False,
     REVIEW, ['CHECKS.json', 'MOVING-CODE-PROGRAM.json.gz']),
    ('invoice_domain', 'check_invoice.py', True, '', ['CHECKS.json']),
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


def canonical_review(raw, root, sources):
    data = json.loads(raw)
    for entry in data['source_pins'].values():
        relative = str(Path(entry['path']).relative_to(root))
        need(relative in sources, 'Unregistered receipt source path')
        source = sources[relative]
        field = 'decompressed_sha256' if entry['decompressed'] else 'sha256'
        need(entry['sha256'] == source[field], 'Receipt source hash mismatch')
        entry['path'] = relative
    return (json.dumps(data, indent=2, sort_keys=True) + '\n').encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    need(shutil.disk_usage(output).free >= 3 * 1024 ** 3, 'Keep at least 3 GiB free')
    manifest = verify()
    sources = {item['source_path']: item for item in manifest['files']}
    env = dict(os.environ)
    env.update({name: '1' for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS',
                                     'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')})
    runs = []
    for optimized in (False, True):
        mode = 'optimized' if optimized else 'normal'
        for label, script, has_out, expected_dir, names in JOBS:
            saved = output / mode / label
            saved.mkdir(parents=True)
            with tempfile.TemporaryDirectory(prefix='pivot-invoice-', dir=output) as temporary:
                package = Path(temporary) / 'package'
                shutil.copytree(HERE, package)
                executable = package / script
                generated = Path(temporary) / 'generated' if has_out else executable.parent
                command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + [str(executable)]
                if has_out:
                    command += ['--out', str(generated)]
                start = time.monotonic()
                result = subprocess.run(command, cwd=package, env=env, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
                (saved / 'stdout.txt').write_text(result.stdout)
                need(result.returncode == 0, label + ' failed: ' + str(saved / 'stdout.txt'))
                comparisons = []
                for name in names:
                    actual = (generated / name).read_bytes()
                    frozen = (HERE / expected_dir / name).read_bytes()
                    (saved / name).write_bytes(actual)
                    if name.endswith('.gz'):
                        left, right = gzip.decompress(actual), gzip.decompress(frozen)
                        receipt = json.loads((generated / 'CHECKS.json').read_text())
                        need(digest(left) == receipt['program_decompressed_sha256'],
                             'Generated program hash does not match its receipt')
                        method = 'complete_decompressed_bytes'
                    elif label == 'prior_review':
                        left = canonical_review(actual, package / 'frozen', sources)
                        right = canonical_review(frozen, OLD_ROOT, sources)
                        (saved / 'CHECKS.canonical.json').write_bytes(left)
                        method = 'all_json_fields_after_registered_source_paths'
                    else:
                        left, right = actual, frozen
                        method = 'complete_bytes'
                    need(left == right, 'Frozen output mismatch: ' + label + '/' + name)
                    comparisons.append({'file': name, 'method': method, 'sha256': digest(left)})
                runs.append({'job': label, 'mode': mode, 'seconds': round(time.monotonic() - start, 3),
                             'comparisons': comparisons})
                print('PASS ' + mode + ' ' + label, flush=True)
    for label, *_ in JOBS:
        pair = [row['comparisons'] for row in runs if row['job'] == label]
        need(len(pair) == 2 and pair[0] == pair[1], 'Normal and optimized outputs differ')
    verify()
    receipt = {'status': 'PASS_PIVOT_CODE_INVOICE_ANNEX', 'source_files': len(sources),
               'source_manifest_sha256': digest((HERE / 'SOURCES.json').read_bytes()),
               'replay_sha256': digest(Path(__file__).read_bytes()), 'runs': runs,
               'normal_optimized_equal': True, 'frozen_sources_unchanged': True,
               'source_code_adaptations': 0,
               'scope': 'Existing common-entry pivot code and inverse invoice, local grid, valid-image divisions, and map order. No productive transport, raw decoder, complete native capture, or kappa improvement.'}
    (output / 'REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
