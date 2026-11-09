"""Authenticate frozen source bytes and load the exact retained tape models.

PUBLIC-CORE-PIN.json records the independent remote Git-blob comparison.
Byte availability does not discharge the Core's admitted source hypotheses.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    require(name not in sys.modules, "cold retained source import " + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    manifest = json.loads((HERE / 'DEPENDENCIES.json').read_text())
    for row in manifest['files']:
        path = HERE / row['path']
        require(path.is_file() and not path.is_symlink(), 'regular retained source')
        raw = path.read_bytes()
        require(sha256(raw).hexdigest() == row['sha256'], 'retained SHA256 ' + row['path'])
        require(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
                'retained Git blob ' + row['path'])
    return manifest


def core_source():
    authenticate()
    source = load('join_sources', HERE / 'retained/core/join_sources.py')
    source.ROOT = ROOT
    return source


def transport_source():
    return load('bridge_retained_transport',
                HERE / 'retained/halo/sparse-halo-tape-transaction/tapes.py')


@contextmanager
def native_models():
    source = core_source()
    B = transport_source()
    with source.physical() as state:
        from records import Tape
        from session import initialize_marker, erase_marker
        from words import BLANK
        yield B, Tape, BLANK, initialize_marker, erase_marker, source, state
