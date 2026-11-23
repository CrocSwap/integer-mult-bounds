#!/usr/bin/env python3
"""Fresh-cache sequential proof witnesses. CubeJerry, OpenAI-assisted, Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(mode):
    for name, expected in json.loads((ROOT / 'PUBLICATION-FREEZE.json').read_text())['files'].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, 'frozen bytes: ' + name)
    for optimized in (False, True):
        with tempfile.TemporaryDirectory(prefix='decoder-sequential-replay-') as folder:
            temporary = Path(folder)
            output = temporary / 'actual.json'
            argv = [sys.executable, '-X', 'pycache_prefix=' + str(temporary / 'bytecode')]
            if optimized:
                argv.append('-O')
            argv.append('-B')
            if mode == 'author':
                argv += [str(ROOT / 'author/sequential/check_sequential.py'), '--output', str(output)]
                evidence = ROOT / 'author/evidence' / ('SEQUENTIAL-OPTIMIZED.json' if optimized else 'SEQUENTIAL.json')
            else:
                argv += [str(ROOT / 'review/independent.py'), '--package', str(ROOT / 'author'), '--output', str(output)]
                evidence = ROOT / 'review' / ('EVIDENCE-OPTIMIZED.json' if optimized else 'EVIDENCE.json')
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=285)
            need(result.returncode == 0, result.stdout + result.stderr)
            need(output.is_file(), 'missing fresh receipt')
            need(json.loads(output.read_text()) == json.loads(evidence.read_text()), 'fresh evidence differs: ' + str(evidence))
    print('PASS_DECODER_SEQUENTIAL_' + mode.upper() + '_NORMAL_OPTIMIZED_FRESH_CACHE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=('author', 'independent'))
    run(parser.parse_args().mode)
