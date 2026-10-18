"""Authenticate the unchanged verifier before importing the optional adapter."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def authenticate():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage'] != 'input':
            continue
        raw = (ROOT/item['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('source SHA: '+item['path'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if blob != item['git_blob']:
            raise ValueError('source blob: '+item['path'])


def load():
    authenticate()
    path = ROOT/'research/eisenstein-reduction-copy-floor/verify.py'
    spec = importlib.util.spec_from_file_location('retained_eisenstein_2017', path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    return old


def install(old):
    import integer_rank
    original = old.rank
    def adapted(matrix, field='K'):
        return integer_rank.rank(matrix) if field == 'K' else original(matrix, field)
    old.rank = adapted
    return original
