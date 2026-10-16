"""Authenticate source bytes before importing any predecessor executable."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def pins():
    checked={}
    for name,root in [('SOURCES.json',ROOT),('VENDOR.json',HERE)]:
        for row in json.loads((HERE/name).read_text())['files']:
            if row.get('usage','input')!='input': continue
            raw=(root/row['path']).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=row['sha256']: raise ValueError('source SHA256 '+row['path'])
            if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=row['git_blob']: raise ValueError('source Git blob '+row['path'])
            checked[row['path']]=row['sha256']
    return checked


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
