#!/usr/bin/env python3
"""Git-free replay plus pre-import source and typed-receipt failure controls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def call(package):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                          cwd=package.parent, capture_output=True, text=True, timeout=90)


with tempfile.TemporaryDirectory(prefix='directory-reserve-') as temporary:
    root = Path(temporary)
    package = root/'research'/HERE.name
    shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
    for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage'] == 'input':
            target = root/row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/row['path'], target)
    good = call(package)
    need(good.returncode == 0 and 'PASS_SELECTED_DIRECTORY_RESERVE' in good.stdout,
         'Git-free replay: '+good.stderr)
    for relative in ('research/'+HERE.name+'/vendor/directory.py',
                     'research/'+HERE.name+'/vendor/PROOF-2590.md',
                     'notes/three-stage-cover-bit.tex'):
        target = root/relative
        raw = target.read_bytes()
        target.write_bytes(raw+b'\nSOURCE CORRUPTION\n')
        result = call(package)
        need(result.returncode != 0 and 'source authentication' in result.stderr,
             'reject authenticated input corruption: '+relative)
        target.write_bytes(raw)
    target = package/'RESULT.json'
    receipt = json.loads(target.read_text(encoding='utf-8'))
    receipt['schema_version'] = True  # Python equality alone would accept 1.
    target.write_text(json.dumps(receipt), encoding='utf-8')
    result = call(package)
    need(result.returncode != 0 and 'typed complete receipt mismatch' in result.stderr,
         'reject bool/int receipt substitution')
print('PASS_DIRECTORY_RESERVE_INTEGRITY git_free=1 source_corruptions=3 typed_receipt=1')
