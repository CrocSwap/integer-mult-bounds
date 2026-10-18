"""Authenticate live inputs and the immutable PR3122 controller/circuit sources."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def module(raw, name):
    result = types.ModuleType(name)
    sys.modules[name] = result
    exec(compile(raw, name, 'exec'), result.__dict__)
    return result


def authenticate():
    manifest = loads((HERE/'SOURCES.json').read_bytes())
    declared = loads((HERE/'VERIFY.json').read_bytes())['inputs']
    live = [row for row in manifest['files'] if row['usage'] == 'input']
    need(set(declared) == {row['path'] for row in live}, 'complete live input inventory')
    data = {}
    for pin in live:
        raw = (ROOT/pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'live source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
             'live source Git blob')
        data[pin['path']] = raw
    archive = manifest['archives'][0]
    raw = (HERE/archive['path']).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == archive['sha256'], 'immutable PR3122 archive')
    prior = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as contents:
        members = contents.getmembers()
        need(len({item.name for item in members}) == len(members) and
             all(item.isfile() for item in members), 'unique regular archive members')
        need({item.name for item in members} == {row['member'] for row in archive['members']},
             'complete source archive inventory')
        for pin in archive['members']:
            body = contents.extractfile(pin['member']).read()
            need(hashlib.sha256(body).hexdigest() == pin['sha256'] and
                 hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest() == pin['git_blob'],
                 'immutable member source binding')
            prior[pin['member']] = body
    return (module(data['research/batched-spaced-lifting/model.py'], 'spaced_model'),
            module(prior['checkpoint.py'], 'prior_checkpoint'),
            module(prior['gaussian.py'], 'prior_gaussian'))
