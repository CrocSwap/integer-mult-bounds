"""Fail closed on exact canonical and published executable source bytes."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent


def hashes(data):
    return (hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),
            hashlib.sha256(data).hexdigest())


def check_payload(data,row,label):
    if hashes(data)!=(row['git_blob'],row['sha256']):
        raise ValueError('source byte pin: '+label)


def check_dependencies():
    rows=json.loads((ROOT/'DEPENDENCIES.json').read_text())['files']
    for row in rows:
        path=ROOT/row['local_path']
        check_payload(path.read_bytes(),row,row['local_path'])
    return len(rows)


def check_inputs():
    rows=json.loads((ROOT/'SOURCES.json').read_text())['files']
    checked=[]
    for row in rows:
        if row['usage']!='input':continue
        path=ROOT.parents[1]/row['path']
        check_payload(path.read_bytes(),row,row['path'])
        checked.append(row['path'])
    return tuple(checked)
