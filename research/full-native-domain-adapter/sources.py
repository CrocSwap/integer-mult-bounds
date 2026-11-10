"""Authenticated unchanged source modules for the native-domain bridge.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor source ownership and licenses are retained in SOURCES.json/README.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/rational-fft-fixed-h/"
ROUNDED = "research/native-rounded-butterfly-contract/rounded.py"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(overrides=None):
    """Authenticate the complete declared closure before any source execution."""
    rows = json.loads((HERE / "SOURCES.json").read_text())['files']
    raw = {}
    for row in rows:
        if row['usage'] != 'input':
            continue
        path = row['path']
        content = (overrides or {}).get(path)
        if content is None:
            content = (ROOT / path).read_bytes()
        need(sha256(content).hexdigest() == row['sha256'], 'source SHA256: ' + path)
        raw[path] = content
    previous = sys.modules.get('lowering')
    lower = ModuleType('_native_domain_retained_lowering')
    lower.__file__ = str(ROOT / PREFIX / 'lowering.py')
    dense = ModuleType('_native_domain_retained_dense')
    dense.__file__ = str(ROOT / PREFIX / 'dense.py')
    try:
        exec(compile(raw[PREFIX + 'lowering.py'], lower.__file__, 'exec', optimize=0), lower.__dict__)
        sys.modules['lowering'] = lower
        exec(compile(raw[PREFIX + 'dense.py'], dense.__file__, 'exec', optimize=0), dense.__dict__)
        source = dense.DenseSources(raw)
    finally:
        if previous is None:
            sys.modules.pop('lowering', None)
        else:
            sys.modules['lowering'] = previous
    rounded = ModuleType('_native_domain_retained_butterfly')
    rounded.__file__ = str(ROOT / ROUNDED)
    exec(compile(raw[ROUNDED], rounded.__file__, 'exec', optimize=0), rounded.__dict__)
    return dense, lower, source, rounded
