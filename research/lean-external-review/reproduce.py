#!/usr/bin/env python3
"""Reproduce the Lean 4.21 contribution with a fresh ordinary Lake build."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'research/lean-multi-host-source'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake', help='Lake executable selection only')
    parser.add_argument('--receipt-dir', required=True, type=Path)
    args = parser.parse_args()
    build = PROJECT / '.lake/build'
    if build.exists() and any(build.iterdir()):
        raise RuntimeError('Fresh reproduction requires an empty local .lake/build; use a clean checkout')
    out = args.receipt_dir.resolve()
    if out.is_relative_to(ROOT):
        raise RuntimeError('Write reproduction receipts outside the checkout')
    out.mkdir(parents=True, exist_ok=False)
    commands = [
        ['research/lean-external-review/verify_package.py', '--allow-pending-port',
         '--receipt', str(out / 'inventory-before.json')],
        ['research/lean-multi-host-source/check_sources.py',
         '--receipt', str(out / 'source-binding.json')],
        ['research/lean-multi-host-source/test_flat_data.py'],
        ['research/lean-multi-host-source/test_verifier_stack.py'],
        ['research/lean-multi-host-source/verify.py', '--lake', args.lake,
         '--receipt', str(out / 'lean421-fresh.json')],
        ['research/lean-external-review/verify_package.py',
         '--build-receipt', str(out / 'lean421-fresh.json'),
         '--receipt', str(out / 'inventory-after.json')],
    ]
    for index, arguments in enumerate(commands, 1):
        print('Running ' + arguments[0], flush=True)
        log_path = out / f'{index}.log'
        with log_path.open('w') as log:
            result = subprocess.run([sys.executable, *arguments], cwd=ROOT,
                                    stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            print(f'FAILED: see {log_path}', file=sys.stderr)
            raise SystemExit(result.returncode)
    print(json.dumps({'status': 'PASS', 'receipts': str(out),
                      'local_build': 'fresh', 'runner': 'ordinary Lake',
                      'differential_test': 'separate delegated work; not run here'}))


if __name__ == '__main__':
    main()
