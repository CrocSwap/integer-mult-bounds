# SPDX-License-Identifier: Apache-2.0
"""Authenticate the actual source bytes before loading the retained macros."""
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(overrides=None):
    overrides = overrides or {}
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    contents = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        raw = overrides.get(row['path'], (ROOT / row['path']).read_bytes())
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'source Git blob: ' + row['path'])
        contents[row['path']] = raw
    return contents


def load_macros(contents):
    modules = {}
    names = ('machine', 'counters', 'shear')
    need(all(name not in sys.modules for name in names), 'no preloaded predecessor modules')
    try:
        for name in names:
            path = 'research/fixed-tape-ordered-shear/' + name + '.py'
            module = types.ModuleType(name)
            module.__file__ = str(ROOT / path)
            sys.modules[name] = module
            exec(compile(contents[path], module.__file__, 'exec'), module.__dict__)
            modules[name] = module
    finally:
        for name in names:
            sys.modules.pop(name, None)
    return modules
