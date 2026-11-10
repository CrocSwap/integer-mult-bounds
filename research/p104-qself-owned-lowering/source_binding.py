"""Authenticate the exact, narrowly vendored source dependency capsule."""
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    pins = json.loads((ROOT/'DEPENDENCIES.json').read_bytes())
    for row in pins['files']:
        raw = (ROOT/row['local_path']).read_bytes()
        require(len(raw) == row['bytes'], 'source length: '+row['local_path'])
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: '+row['local_path'])
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
                'source Git blob: '+row['local_path'])
    return len(pins['files'])


def inputs():
    authenticate()
    def read(name):
        b = (ROOT/name).read_bytes()
        return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)
    return (read('data/caller_efree.json'), read('data/caller_6936.json'),
            read('data/word_6936.json.gz'), read('QUERY-BASES.json'))
