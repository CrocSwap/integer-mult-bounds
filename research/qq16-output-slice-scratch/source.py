"""Authenticate pinned input bytes before loading credited formal operators."""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes()
            if sha256(raw).hexdigest()!=row['sha256']:
                raise ValueError('main source authentication')
    for row in json.loads((HERE/'VENDOR.json').read_text())['files']:
        raw=(HERE/row['path']).read_bytes()
        if sha256(raw).hexdigest()!=row['sha256'] or sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=row['git_blob']:
            raise ValueError('vendor source authentication: '+row['path'])
    spec=importlib.util.spec_from_file_location('credited2651',HERE/'vendor/verify.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module,json.loads((HERE/'vendor/WORD.json').read_text())
