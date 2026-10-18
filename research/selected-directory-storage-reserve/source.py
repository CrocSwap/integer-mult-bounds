"""Authenticate every consumed source before importing the retained producer."""
from hashlib import sha1, sha256
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT/row['path']).read_bytes()
        if sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('main source authentication: '+row['path'])
    for row in json.loads((HERE/'VENDOR.json').read_text())['files']:
        raw = (HERE/row['path']).read_bytes()
        blob = sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if sha256(raw).hexdigest() != row['sha256'] or blob != row['git_blob']:
            raise ValueError('vendor source authentication: '+row['path'])


def load():
    authenticate()
    sys.path.insert(0, str(HERE/'vendor'))
    return {name: importlib.import_module(name)
            for name in ('words', 'records', 'counts', 'low_codes', 'directory')}
