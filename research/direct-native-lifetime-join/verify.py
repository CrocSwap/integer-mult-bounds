#!/usr/bin/env python3
"""Frozen lifetime evidence and separate source-method census. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def invoke(script, args, optimized):
    with tempfile.TemporaryDirectory(prefix='native-lifetime-cache-') as cache:
        cmd = [sys.executable, '-X', 'pycache_prefix=' + cache]
        if optimized:
            cmd.append('-O')
        cmd += ['-B', str(ROOT / script), *map(str, args)]
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=100)


def run(mode):
    for rel, want in json.loads((ROOT / 'author/FROZEN.json').read_text())['files'].items():
        need(hashlib.sha256((ROOT / 'author' / rel).read_bytes()).hexdigest() == want,
             'author freeze ' + rel)
    for rel, want in json.loads((ROOT / 'REVIEW-FREEZE.json').read_text()).items():
        need(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == want, 'review freeze ' + rel)
    for optimized in (False, True):
        suffix = '-OPTIMIZED' if optimized else ''
        script = 'author/check.py' if mode == 'author' else 'review/independent.py'
        args = [] if mode == 'author' else [ROOT / 'author/retained']
        result = invoke(script, args, optimized)
        need(result.returncode == 0, result.stderr + result.stdout)
        evidence = ROOT / ('author' if mode == 'author' else 'review') / ('EVIDENCE' + suffix + '.json')
        need(json.loads(result.stdout) == json.loads(evidence.read_text()), 'evidence mismatch')
        if mode == 'independent':
            with tempfile.TemporaryDirectory(prefix='lifetime-corruption-') as tmp:
                for name in ('product.py', 'tensor_word.py'):
                    shutil.copyfile(ROOT / 'author/retained' / name, Path(tmp) / name)
                source = Path(tmp) / 'product.py'
                source.write_bytes(source.read_bytes() + b'\n# corruption control\n')
                bad = invoke(script, [Path(tmp)], optimized)
                need(bad.returncode != 0 and 'source hash product.py' in bad.stderr,
                     'source corruption not rejected')
    print('PASS_NATIVE_LIFETIME_' + mode.upper() + '_NORMAL_OPTIMIZED_FRESH_CACHE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('author', 'independent'), required=True)
    run(parser.parse_args().mode)
