#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate unchanged PR2776 exports before interpreting their source bytes."""
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def load():
    manifest = json.loads((HERE / 'EXPORTS.json').read_text())
    for entry in manifest['files']:
        raw = (HERE / entry['local']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('source SHA256: ' + entry['local'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if blob != entry['git_blob']:
            raise ValueError('source Git blob: ' + entry['local'])
    result = {}
    for name, filename in (('machine', 'machine.py'), ('counters', 'counters.py'),
                           ('shear', 'shear.py'), ('carry_dense', 'independent_check.py'),
                           ('carry_qadic', 'qadic_streams.py')):
        if name in sys.modules:
            raise ValueError('refuse preloaded source module: ' + name)
        path = HERE / 'predecessor' / filename
        module = types.ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
        result[name] = module
    return result
