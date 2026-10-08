#!/usr/bin/env python3
"""Reproduce every selected word/profile in scratch; --record writes only a run log/receipt."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
from pin_sources import check as check_sources

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='Write timing/log receipts only; mathematical artifacts are compared.')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    manifest = check_sources()
    before = {name: digest(ROOT / name) for name in manifest['files']}
    for name in ('independent-audit.json', 'endpoint-check.json', 'corner-audit.json'):
        path = HERE / name
        before[str(path.relative_to(ROOT))] = digest(path)
    source_before = digest(HERE / 'SOURCE.json')
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    steps, exit_code = [], 0
    if args.record:
        logpath = HERE / 'verification.log'
    else:
        with tempfile.NamedTemporaryFile(prefix='merged-span-verification-', suffix='.log', delete=False) as log:
            logpath = Path(log.name)
    with tempfile.TemporaryDirectory(prefix='merged-span-verification-') as directory:
        work = Path(directory)
        commands = [
            [sys.executable, str(HERE / 'producer.py'), '--output', str(work)],
            [sys.executable, str(HERE / 'check.py'), '--work', str(work), '--workers', str(args.workers)],
            [sys.executable, str(HERE / 'endpoint_check.py')],
            [sys.executable, str(HERE / 'corner_check.py')],
            [sys.executable, str(HERE / 'independent_check.py')],
        ]
        with logpath.open('w') as log:
            for command in commands:
                label = Path(command[1]).name
                print('RUN', label, flush=True)
                log.write('\nRUN ' + ' '.join(command) + '\n')
                log.flush()
                step_start = time.monotonic()
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                steps.append(dict(step=label, exit_code=result.returncode, elapsed_seconds=round(time.monotonic()-step_start, 3)))
                if result.returncode:
                    exit_code = result.returncode
                    break
            changed = [name for name, value in before.items() if not (ROOT / name).exists() or digest(ROOT / name) != value]
            if digest(HERE / 'SOURCE.json') != source_before:
                changed.append('SOURCE.json')
            if changed and not exit_code:
                exit_code = 1
            log.write('\nchanged_frozen_files=' + json.dumps(changed) + '\nexit_code=' + str(exit_code) + '\n')
    if not exit_code:
        check_sources()
    certificate = json.loads((HERE / 'certificate.json').read_text())
    receipt = dict(status='PASS' if not exit_code else 'FAIL', started_utc=started,
                   finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=round(time.monotonic()-tick, 3),
                   exit_code=exit_code, steps=steps, changed_frozen_files=changed,
                   source_manifest_sha256=source_before, certificate_sha256=digest(HERE / 'certificate.json'),
                   kappa=certificate['kappa'], log_sha256=digest(logpath),
                   scope='Fresh PR91 h23 and frozen deferred-span h25, exact final label actions, full dirty replay both orientations, literal paths, exact CRT and merged profiles, endpoint proof controls and independent paid arithmetic. Inherited all-size transfer hypotheses remain assumed.')
    if args.record:
        (HERE / 'validation.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print('Log:', logpath, flush=True)
    if exit_code:
        print('\n'.join(logpath.read_text().splitlines()[-80:]), flush=True)
    print('PASS merged-span finite gate' if not exit_code else 'FAIL merged-span finite gate', flush=True)
    raise SystemExit(exit_code)

if __name__ == '__main__':
    main()
