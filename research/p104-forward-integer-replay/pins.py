"""Authenticate retained bytes before source execution."""
from hashlib import sha1, sha256
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent

def check(raw, pin):
    if (len(raw) != pin['size'] or sha256(raw).hexdigest() != pin['sha256']
        or sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() != pin['git_blob']):
        raise ValueError('Retained source bytes differ: '+pin['path'])

def authenticate():
    pins = json.loads((HERE/'ORIGINS.json').read_text())
    for pin in pins:
        check((HERE/pin['path']).read_bytes(), pin)
    return pins
