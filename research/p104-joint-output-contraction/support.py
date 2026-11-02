"""Authenticate the source word, caller and retained proof engines.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source reader and all proof engines retain the credits in NOTICE.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/p104-native-input-lifting/'
TREE = 'research/balanced-query-tree/'
RETAINED = 'research/p104-retained-operand-descent/'
WORD = SOURCE + 'WORD.json.gz'
INPUTS = {
    *(SOURCE + name for name in ('support.py', 'SOURCES.json', 'WORD.json.gz')),
    *(RETAINED + name for name in
      ('sources.py', 'SOURCES.json', 'inputs/pr5827-source.tar', 'pricing.py')),
    *(TREE + name for name in
      ('controller.py', 'CONTROLLER.json', 'physical.py', 'module_check.py', 'pricing.py')),
    'research/p104-frontier-compression-2/WORD.json.gz',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin['sha256'], 'Exact source SHA256: ' + pin['path'])
    blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
    need(sha1(blob).hexdigest() == pin['git_blob'], 'Exact source Git blob: ' + pin['path'])


def inputs():
    pins = [pin for pin in read(HERE / 'SOURCES.json')['files'] if pin['usage'] == 'input']
    need(len(pins) == len(INPUTS) and {p['path'] for p in pins} == INPUTS,
         'Complete live source inventory')
    out = {}
    for pin in pins:
        raw = (ROOT / pin['path']).read_bytes()
        authenticate(raw, pin)
        out[pin['path']] = raw
    return out


@contextmanager
def checkers():
    inputs()
    source = load(ROOT / SOURCE / 'support.py', 'joint_retained_support')
    with source.checkers() as (local, root):
        yield local, root
