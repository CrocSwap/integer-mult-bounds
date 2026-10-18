"""Authenticate main and unmodified predecessor inputs before execution."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def authenticate():
    for filename, root in [('SOURCES.json', ROOT), ('VENDOR.json', HERE)]:
        for row in json.loads((HERE/filename).read_text())['files']:
            if row.get('usage', 'input') != 'input': continue
            data = (root/row['path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('source SHA256 ' + row['path'])
            if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() != row['git_blob']:
                raise ValueError('source Git blob ' + row['path'])


def predecessor():
    authenticate()
    spec = importlib.util.spec_from_file_location('credited_2538', HERE/'predecessor/PR2538-synth.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
