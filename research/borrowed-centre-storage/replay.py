#!/usr/bin/env python3
"""Check the frozen inputs and run the local storage checks in order."""

import argparse
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


PACKAGE = Path(__file__).resolve().parent
CAMPAIGN = PACKAGE / 'sources/work/centre-encoding-campaign-20261014'
MASKED = CAMPAIGN / 'lanes/portable-source-codes/dirty-record-hosting-20261015/masked-query'


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    require(not out.exists(), 'Use a new output directory.')
    require(PACKAGE not in out.parents, 'Put outputs outside the package.')
    require(shutil.disk_usage(PACKAGE).free >= 3 * 1024**3, 'At least three GiB must be free.')
    pins = json.loads((PACKAGE / 'SOURCE-PINS.json').read_text())['files']
    for name, entry in pins.items():
        path = PACKAGE / name
        require(digest(path) == entry['sha256'], 'Source pin: ' + name)
        if 'decompressed_sha256' in entry:
            require(sha256(gzip.decompress(path.read_bytes())).hexdigest() == entry['decompressed_sha256'],
                    'Payload pin: ' + name)
    adaptations = json.loads((PACKAGE / 'ADAPTATIONS.json').read_text())
    for name, entry in adaptations.items():
        require(digest(PACKAGE / 'checks' / name) == entry['adapted_sha256'], 'Checker pin: ' + name)
        require(digest(PACKAGE / entry['frozen_source']) == entry['source_sha256'], 'Original checker pin: ' + name)
    out.mkdir(parents=True)
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
    steps = [
        ('borrowed_core', PACKAGE / 'checks/borrowed_core.py', out / 'borrowed-core.json'),
        ('carried_alias', PACKAGE / 'checks/carried_alias.py', out / 'carried-alias.json'),
        ('relative_storage', PACKAGE / 'checks/relative_storage.py', out / 'relative-storage.json'),
        ('clean_storage', PACKAGE / 'checks/clean_storage.py', out / 'clean-storage.json'),
        ('unit_query', PACKAGE / 'checks/unit_query.py', out / 'unit-query.json'),
        ('masked_producer', MASKED / 'emit_masked_query.py', out / 'masked-unit'),
        ('masked_review', PACKAGE / 'checks/masked_query.py', out / 'masked-review.json'),
        ('cleanup_producer', MASKED / 'emit_stream_cleanup.py', out / 'cleanup'),
        ('cleanup_review', PACKAGE / 'checks/stream_cleanup.py', out / 'cleanup-review.json'),
    ]
    results = []
    for name, script, target in steps:
        command = [sys.executable, '-I', '-B', str(script), '--out', str(target)]
        start = time.monotonic()
        result = subprocess.run(command, cwd=out, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out / (name + '.log')).write_text(result.stdout)
        require(result.returncode == 0, name + ' failed; read ' + str(out / (name + '.log')))
        results.append({'name': name, 'returncode': result.returncode, 'seconds': round(time.monotonic() - start, 3)})
        print(result.stdout.strip(), flush=True)
    frozen_mask = MASKED / 'masked-sum/MASKED-QUERY-PROGRAM.json.gz'
    new_mask = out / 'masked-unit/MASKED-QUERY-PROGRAM.json.gz'
    require(gzip.decompress(new_mask.read_bytes()) == gzip.decompress(frozen_mask.read_bytes()),
            'The regenerated masked word differs from the frozen payload.')
    for name in ('STREAM-CLEANUP-WORD.json', 'STREAM-CLEANUP.json'):
        require((out / 'cleanup' / name).read_bytes() == (MASKED / 'stream-cleanup' / name).read_bytes(),
                'The regenerated cleanup differs: ' + name)
    for name, entry in pins.items():
        require(digest(PACKAGE / name) == entry['sha256'], 'A frozen input changed: ' + name)
    report = {
        'status': 'PASS_BORROWED_CENTRE_STORAGE_PACKAGE',
        'python': platform.python_version(), 'platform': platform.platform(),
        'source_files_checked': len(pins), 'adapted_checkers_checked': len(adaptations),
        'source_pins_sha256': digest(PACKAGE / 'SOURCE-PINS.json'),
        'steps': results, 'masked_payload_matches': True, 'cleanup_bytes_match': True,
        'frozen_inputs_unchanged': True, 'processes_at_once': 1,
        'archive_scope': 'Exact extracted members are checked. Full historical archives are not replayed.',
        'scope': 'Two all-512 storage witnesses, a local masked unit, and a cleanup conditional on its aligned cut.',
        'not_checked': ['Retained native child kernels', 'Changed masked global owner schedule',
                        'Mixed-frame target-code retirement', 'Recursive storage and precision',
                        'Complete supplier or kappa calculation'],
    }
    (out / 'REPLAY.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
