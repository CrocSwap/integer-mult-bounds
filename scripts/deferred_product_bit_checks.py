#!/usr/bin/env python3
"""Run PR #97's round-seven bit checks on a temporary copy of research/deferred-signed.

Runs, unchanged: the literal frame ledger (both shears, reflected continuity, event histogram),
Swapnil Jain's check_word.py (F2 and Z replay with arbitrary scratch) and check_frames.py
(exact frames, sigma/V-leaf nesting in time order, histogram). The ledger rewrites its receipt
with an elapsed time, so it runs on a copy and every other field is compared with the committed receipt.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/deferred-signed'


def main():
    assert not sys.flags.optimize, 'Run without -O'
    with tempfile.TemporaryDirectory(prefix='deferred-product-bit-') as tmp:
        copy = Path(tmp) / 'deferred-signed'
        shutil.copytree(SOURCE, copy, ignore=shutil.ignore_patterns('__pycache__'))
        subprocess.run([sys.executable, str(copy / 'round7_literal_frame_ledger.py')], check=True,
                       stdout=subprocess.DEVNULL)
        new = json.loads((copy / 'round7-literal-ledger/result.json').read_text())
        old = json.loads((SOURCE / 'round7-literal-ledger/result.json').read_text())
        drop = ('elapsed',)
        assert {k: v for k, v in new.items() if k not in drop} == {k: v for k, v in old.items() if k not in drop}, \
            'literal ledger receipt changed'
        checks = copy / 'swapnil-round7/independent/deferred-readout'
        for script in ('check_word.py', 'check_frames.py'):
            out = subprocess.run([sys.executable, script], cwd=checks, check=True, capture_output=True, text=True).stdout
            assert 'ALL PASS' in out, script
    print('PASS round-seven bit word: literal ledger, check_word, check_frames')


if __name__ == '__main__':
    main()
