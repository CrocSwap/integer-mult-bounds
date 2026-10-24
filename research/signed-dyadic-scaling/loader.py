# SPDX-License-Identifier: Apache-2.0
"""Authenticate exact retained macros; no predecessor verifier is executed."""
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, text):
    if not ok:
        raise ValueError(text)


def authenticate(overrides=None):
    overrides = overrides or {}
    contents = {}
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        data = overrides.get(row['path'], (ROOT / row['path']).read_bytes())
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256')
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == row['git_blob'], 'source Git blob')
        contents[row['path']] = data
    return contents


def load_modules(contents):
    modules = {}
    names = ('machine', 'counters', 'shear', 'independent_check')
    need(all(name not in sys.modules for name in names), 'preloaded source module')
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
