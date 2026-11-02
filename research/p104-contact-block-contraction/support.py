"""Authenticate the live inputs and the two retained PR6353 files.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source readers and proof engines retain the credits in NOTICE.
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
TREE = 'research/balanced-query-tree/'
SOURCE = 'research/p104-native-input-lifting/'
RETAINED = 'research/p104-retained-operand-descent/'
PACKAGE = 'research/p104-contact-block-contraction/'
SOURCE_WORD = PACKAGE + 'inputs/pr6353-WORD.json.gz'
SOURCE_BASIS = PACKAGE + 'inputs/pr6353-construct.py'
INPUTS = {
    *(SOURCE + name for name in ('support.py', 'SOURCES.json', 'WORD.json.gz')),
    *(RETAINED + name for name in
      ('sources.py', 'SOURCES.json', 'inputs/pr5827-source.tar', 'pricing.py')),
    *(TREE + name for name in
      ('controller.py', 'CONTROLLER.json', 'physical.py', 'module_check.py', 'pricing.py')),
    'research/p104-frontier-compression-2/WORD.json.gz',
    SOURCE_WORD, SOURCE_BASIS,
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
    pins = read(HERE / 'SOURCES.json')['files']
    live = {pin['path']: pin for pin in pins if pin['usage'] == 'input'}
    need(set(live) == INPUTS, 'Complete live input inventory')
    out = {}
    for path in sorted(INPUTS):
        raw = (ROOT / path).read_bytes()
        authenticate(raw, live[path])
        out[path] = raw
    return out


@contextmanager
def checkers():
    inputs()
    source = load(ROOT / SOURCE / 'support.py', 'contact_retained_support')
    with source.checkers() as (local, root):
        yield local, root
