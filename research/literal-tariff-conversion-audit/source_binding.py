"""Authenticated frozen inputs for a cost audit, not a new caller registry.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows = json.loads((ROOT / 'DEPENDENCIES.json').read_text())['files']
    for row in rows:
        raw = (ROOT / row['local_path']).read_bytes()
        need(len(raw) == row['bytes'], 'dependency length: ' + row['local_path'])
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'dependency SHA256: ' + row['local_path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == row['git_blob'], 'dependency Git blob: ' + row['local_path'])
    return len(rows)


def vendor(name, path):
    # The unchanged compact constructor imports its original Builder path.
    if path == 'vendor/exact_scalar_tables.py':
        path = 'kernel/exact_builder.py'
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    need(spec is not None and spec.loader is not None, 'module loader')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
