"""Authenticate the unchanged physical framework before importing it.

Tekalign with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_loaded = False


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_bytes(raw, name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def activate():
    global _loaded
    if _loaded:
        return
    data = {}
    pins = json.loads((HERE/'SOURCES.json').read_bytes())['files']
    declared = json.loads((HERE/'VERIFY.json').read_bytes())['inputs']
    need(set(declared) == {pin['path'] for pin in pins if pin['usage'] == 'input'},
         'complete live normalization input inventory')
    for pin in pins:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT/pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'live source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == pin['git_blob'], 'live source Git blob')
        data[pin['path']] = raw
    prefix = 'research/physical-gaussian-leaf/'
    need('leaf_sources' not in sys.modules, 'cold coefficient namespace')
    old = load_bytes(data[prefix+'leaf_sources.py'], 'leaf_sources', ROOT/prefix/'leaf_sources.py')
    old.activate()  # Authenticated immutable archives retain all original notices.
    _loaded = True
