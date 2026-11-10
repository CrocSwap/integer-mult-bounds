"""Authenticated unchanged Full/fixed-word source closure.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Full and fixed-H producers remain Jose Manuel's and Vlado Vojdanovski's work.
"""
from contextlib import contextmanager
from functools import wraps
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType
from threading import RLock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = 'research/rational-fft-fixed-h/'
_serialization_lock = RLock()


def need(condition, message):
    if not condition:
        raise ValueError(message)


@contextmanager
def trusted_exact_serialization():
    """Temporarily admit arbitrary-size trusted integer hashes, then restore.

    CPython's decimal-digit limit is process-wide. This serialized preparation
    context preserves it in finally; it never changes arithmetic or hash format.
    It encloses authenticated exact source/hash work, not input text parsing.
    """
    with _serialization_lock:
        previous = sys.get_int_max_str_digits()
        if previous:
            sys.set_int_max_str_digits(0)
        try:
            yield
        finally:
            if previous:
                sys.set_int_max_str_digits(previous)


def exact_preparation(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        with trusted_exact_serialization():
            return function(*args,**kwargs)
    return wrapped


def load(overrides=None):
    raw = {}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        path = row['path']
        content = (overrides or {}).get(path)
        if content is None:
            content = (ROOT/path).read_bytes()
        need(sha256(content).hexdigest() == row['sha256'], 'source SHA256: '+path)
        raw[path] = content
    previous = sys.modules.get('lowering')
    lower = ModuleType('_global_retained_lowering')
    lower.__file__ = str(ROOT/PREFIX/'lowering.py')
    dense = ModuleType('_global_retained_dense')
    dense.__file__ = str(ROOT/PREFIX/'dense.py')
    try:
        exec(compile(raw[PREFIX+'lowering.py'],lower.__file__,'exec',optimize=0),lower.__dict__)
        sys.modules['lowering'] = lower
        exec(compile(raw[PREFIX+'dense.py'],dense.__file__,'exec',optimize=0),dense.__dict__)
        source = dense.DenseSources(raw)
    finally:
        if previous is None:
            sys.modules.pop('lowering',None)
        else:
            sys.modules['lowering'] = previous
    return dense,lower,source
