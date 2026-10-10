"""Immutable data acquisition contract. No upstream program is imported.

Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import gzip,hashlib,json,os
ROOT=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('PR275_INPUTS',ROOT/'inputs')).resolve()
OUTPUT=Path(os.environ.get('PR275_OUTPUTS',ROOT/'generated')).resolve()
HEAD='10b40041d4ab8a6610083e95bc571aee3468bca2'
def pins():
    value=json.loads((ROOT/'inputs.json').read_text())
    assert value['commit']==HEAD
    return value
def validate(name,raw):
    pin=pins()['files'][name]
    assert len(raw)==pin['bytes'],('Length mismatch',name)
    assert hashlib.sha256(raw).hexdigest()==pin['sha256'],('SHA256 mismatch',name)
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],('Git blob mismatch',name)
    return raw
def read_bytes(name):
    return validate(name,(SOURCE/pins()['files'][name]['local']).read_bytes())
def read(name):
    raw=read_bytes(name)
    return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
def verify():
    if not __debug__:raise RuntimeError('Assertions are required; do not use python -O')
    for name in pins()['files']:read_bytes(name)
    return len(pins()['files'])
