"""Authenticated frozen RUN/D components and unchanged physical runtime.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
RUN = ROOT / 'research/physical-fine-gap-run'
FOLDED = ROOT / 'research/folded-cyclic-tape'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def authenticated_inputs():
    raw = {}
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            need(path.is_file() and not path.is_symlink(), 'regular periodic source: '+row['path'])
            value = path.read_bytes()
            need(sha256(value).hexdigest() == row['sha256'], 'pinned periodic source: '+row['path'])
            raw[row['path']] = value
    return raw


def components():
    """Call only after authenticated_inputs has checked their complete bytes."""
    return (load('_periodic_run_sources', RUN / 'sources.py'),
            load('_periodic_run_coefficients', RUN / 'coefficients.py'),
            load('_periodic_folded_pages', FOLDED / 'pages.py'),
            load('_periodic_run_rounded_oracle', RUN / 'rounded_oracle.py'))


@contextmanager
def physical_runtime(run_sources):
    previous = sys.path[:]
    try:
        sys.path[:0] = [str(PACKAGE), str(FOLDED)]
        with run_sources.physical_runtime() as state:
            yield state
    finally:
        sys.path[:] = previous
