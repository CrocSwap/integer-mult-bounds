"""Load exact retained source modules. Ali Romman, with Codex. Apache-2.0."""

from hashlib import sha1, sha256
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent


def authenticate():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    for pin in pins:
        raw = (ROOT / pin['path']).read_bytes()
        if sha256(raw).hexdigest() != pin['sha256'] or sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != pin['git_blob']:
            raise ValueError('retained source changed: ' + pin['path'])
    return len(pins)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


authenticate()
arithmetic = load('nonunit_source_arithmetic', 'retained/arithmetic/circuit.py')
domain = load('nonunit_source_domain', 'retained/inverse-domain/verify.py')
entry = load('nonunit_source_entry', 'retained/phase-entry/interface.py')
