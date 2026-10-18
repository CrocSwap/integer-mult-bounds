#!/usr/bin/env python3
"""Failure-detection and relocated-package checks; standard library only.

Copyright 2026 martinxxx9. Apache-2.0. Substantial OpenAI Codex assistance.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(root, program, *extra):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(root / program), *extra],
                            cwd=root.parent, capture_output=True, text=True, timeout=60)
    return result.returncode, result.stdout + result.stderr


def main():
    checked = 0
    with tempfile.TemporaryDirectory(prefix='five cube package ') as scratch:
        root = Path(scratch) / 'relocated package with spaces'
        shutil.copytree(HERE, root, ignore=shutil.ignore_patterns('__pycache__'))
        for program in ('verify.py', 'independent.py'):
            code, output = run(root, program)
            require(code == 0 and output.startswith('PASS_'), 'relocated optimized replay: ' + output)
        checked += 1

        path = root / 'sources/PR958-PROOF.md'
        original = path.read_bytes()
        path.write_bytes(original + b'\ncorrupted source\n')
        for program in ('verify.py', 'independent.py'):
            code, output = run(root, program)
            require(code != 0 and 'SHA256' in output, 'corrupt source not rejected: ' + output)
        path.write_bytes(original)
        checked += 1

        path = root / 'SOURCES.json'
        original = path.read_bytes()
        altered = json.loads(original)
        altered['files'].pop()
        path.write_text(json.dumps(altered), encoding='utf-8')
        for program in ('verify.py', 'independent.py'):
            code, output = run(root, program)
            require(code != 0 and 'inventory' in output, 'omitted source not rejected: ' + output)
        path.write_bytes(original)
        checked += 1

        path = root / 'CERTIFICATE.json'
        original = path.read_bytes()
        altered = json.loads(original)
        altered['cross_rank_table'][0][0] += 1
        path.write_text(json.dumps(altered), encoding='utf-8')
        for program in ('verify.py', 'independent.py'):
            code, output = run(root, program)
            require(code != 0 and ('certificate' in output.lower() or 'rank table' in output.lower()),
                    'corrupt rank not rejected: ' + output)
        path.write_bytes(original)
        checked += 1

        path = root / 'INDEPENDENT.json'
        original = path.read_bytes()
        altered = json.loads(original)
        altered['cross_rank_table'][0][0] += 1
        path.write_text(json.dumps(altered), encoding='utf-8')
        code, output = run(root, 'independent.py')
        require(code != 0 and 'receipt' in output.lower(), 'corrupt independent receipt not rejected: ' + output)
        path.write_bytes(original)
        checked += 1

        for program in ('verify.py', 'independent.py'):
            path = root / 'existing receipt.json'
            sentinel = b'preserve existing output\n'
            path.write_bytes(sentinel)
            code, output = run(root, program, '--write-certificate', str(path))
            require(code != 0 and 'FileExistsError' in output and path.read_bytes() == sentinel,
                    'existing output not preserved: ' + output)
        checked += 1
    print(f'PASS_FIVE_CUBE_CODED_COPY_PACKAGE tests={checked} optimized_relocation=true corruption_rejected=true')


if __name__ == '__main__':
    main()
