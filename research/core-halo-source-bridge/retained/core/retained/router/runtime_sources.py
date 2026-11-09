"""Authenticate and open unchanged #6908 numerical bodies.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
INVERSE = PACKAGE / 'retained/inverse_window'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    raw = {}
    for row in json.loads((PACKAGE / 'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        need(path.is_file() and not path.is_symlink(), 'regular source ' + row['path'])
        data = path.read_bytes()
        need(sha256(data).hexdigest() == row['sha256'], 'source SHA256 ' + row['path'])
        need(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == row['git_blob'], 'source Git blob ' + row['path'])
        raw[row['path']] = data
    for row in json.loads((PACKAGE / 'DEPENDENCIES.json').read_text())['files']:
        path = PACKAGE / row['retained']
        need(path.is_file() and not path.is_symlink(), 'regular retained ' + row['retained'])
        data = path.read_bytes()
        need(sha256(data).hexdigest() == row['sha256'], 'retained SHA256 ' + row['retained'])
        need(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == row['git_blob'], 'retained Git blob ' + row['retained'])
    return raw


@contextmanager
def physical_runtime():
    authenticate()
    need('gaussian_sources' not in sys.modules, 'cold union-router namespace')
    physical = ROOT / 'research/physical-gaussian-core'
    old = sys.path[:]
    sys.path[:0] = [str(physical), str(PACKAGE), str(INVERSE),
                   str(INVERSE / 'retained'), str(ROOT / 'research/physical-boundary-pages')]
    spec = importlib.util.spec_from_file_location('gaussian_sources', physical / 'gaussian_sources.py')
    source = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = source
    try:
        spec.loader.exec_module(source)
        with source.opened() as state:
            yield state
    finally:
        sys.path[:] = old


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
