#!/usr/bin/env python3
"""Replay Arham Tahir's PR1926 in its exact historical runtime context.

Original comparison, tests and result are unchanged. This bounded replay does
not run the full repository benchmark or replace the current isolated runner.
Maintenance: Douglas Colkitt with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = 'research/unittest-receipt-comparison'
ORIGINAL_FILES = {'README.md': '844e6fd9246bca2229d87f6560739fbe97da42aae789b2265c88c394ab6f7616', 'RESULT.json': 'a8f193d64552180ae75179fc8005886460e7cedb1ad88474cbf1855119025fbf', 'SOURCES.json': '4ac8f4f592806bad1adb4cb7310fe8ad115a1e7da3e581da487adb75ce8a2edb', 'TASK.json': '303a993d2c013076a554f4bd93b65f4588741e1b4620986b61ad3d5ae4c46f5f', 'VALIDATION.json': '37c96f1cfcbd42e12e00ffdb4c0dcff2cd3420d5a4a3629cfcee0157a3b9e930', 'VERIFY.json': '9b85e15adf00bed937ecd99c7309fd3620515383a903b43c29cf79701462b178', 'adapter.py': 'ee9240abbb57d991c6522dbbf1863a172dc6616ebc8a5fb507ec92783bc9c950', 'comparison.py': '7c306b2390d734580c87a9c7e6495f1a4e5107ac6cf4410c98deeaaf34d3d115', 'test_comparison.py': 'dc2cb3a658e75027c131743b482a7a0c5916b2cc08f98be50b351d3088710ef2', 'verify.py': '2abe01e65f46911a14573db799c4fd35cdf1a825724b301828476854473c8e7f'}
INPUTS = {'research/agent-07-verifeng-seed88/README.md': {'physical': 'research/agent-07-verifeng-seed88/README.md', 'sha256': 'c4d4e00f59ae9cf3b7a1b79377bd8c9539d2de8f035da669b92d6d3adcfeca14'}, 'research/agent-07-verifeng-seed88/benchmark.py': {'physical': 'research/agent-07-verifeng-seed88/benchmark.py', 'sha256': 'e6b55c19fc9c7af8242f624bba046fb20e90f6d25977196063dc2de974eb0a80'}, 'scripts/run_isolated_tests.py': {'physical': 'scripts/historical-ci-inputs/ledger-batch932-run_isolated_tests.py', 'sha256': '96ea543e6c707424afe247e77bd86c82152f90fc76a0773c4232145da5cdf8d1'}}
ARCHIVED_METADATA = {'README.md', 'SOURCES.json', 'VERIFY.json'}
MARKER = 'PASS_UNITTEST_RECEIPT_COMPARISON collisions=2 tests=20'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def prepare(root, snapshot):
    """Authenticate everything before creating the private replay tree."""
    root = Path(root)
    content = {}
    for name, digest in ORIGINAL_FILES.items():
        physical = root / PACKAGE / ('historical' if name in ARCHIVED_METADATA else '') / name
        raw = physical.read_bytes()
        require(sha256(raw).hexdigest() == digest, 'Original package changed: ' + name)
        content[PACKAGE + '/' + name] = raw
    for relative, row in INPUTS.items():
        raw = (root / row['physical']).read_bytes()
        require(sha256(raw).hexdigest() == row['sha256'], 'Historical input changed: ' + relative)
        content[relative] = raw
    require(not snapshot.exists(), 'Replay destination already exists')
    for relative, raw in content.items():
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return {name: sha256(raw).hexdigest() for name, raw in content.items()}


def inventory(root):
    return {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def replay(root=ROOT, optimized=False):
    with tempfile.TemporaryDirectory(prefix='pr1926-historical-') as td:
        snapshot = Path(td) / 'repo'
        before = prepare(root, snapshot)
        command = [sys.executable, '-B', *(['-O'] if optimized else []),
                   str(snapshot / PACKAGE / 'verify.py')]
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        result = subprocess.run(command, cwd=snapshot, env=env, capture_output=True,
                                text=True, timeout=120)
        require(result.returncode == 0, 'Historical verifier failed: ' + result.stdout + result.stderr)
        require(result.stdout.splitlines() and result.stdout.splitlines()[-1] == MARKER,
                'Historical verifier did not report complete 20-test replay')
        require(inventory(snapshot) == before, 'Historical replay inputs changed')
        print(result.stdout, end='')
    print('PASS_PR1926_HISTORICAL_CONTEXT optimized=' + str(optimized))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--optimized', action='store_true')
    args = parser.parse_args()
    replay(optimized=args.optimized)


if __name__ == '__main__':
    main()
