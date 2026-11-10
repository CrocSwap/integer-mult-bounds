"""Exact immutable inputs; no runtime source acquisition.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
ROOT = Path(__file__).resolve().parent
def need(ok,message):
    if not ok: raise ValueError(message)
def authenticate():
    rows=json.loads((ROOT/'DEPENDENCIES.json').read_text())['files']
    for row in rows:
        data=(ROOT/row['local_path']).read_bytes()
        need(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'], 'source bytes')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'], 'source blob')
    return len(rows)
def vendor(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module
