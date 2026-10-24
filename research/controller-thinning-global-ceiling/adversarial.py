#!/usr/bin/env python3
"""Reject actual source/profile corruptions. Apache-2.0; Codex assistance."""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('thinning_mutation_target', HERE/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def reject(name, mutate):
    with TemporaryDirectory(prefix='thinning-control-') as directory:
        target = Path(directory)/'package'
        shutil.copytree(HERE, target)
        original = V.HERE
        V.HERE = target
        try:
            mutate(target)
            try:
                V.authenticate()
            except ValueError:
                return name
            raise RuntimeError('Mutation accepted: '+name)
        finally:
            V.HERE = original


def bad_live_pin(target):
    path = target/'SOURCES.json'
    value = json.loads(path.read_text())
    next(x for x in value['files'] if x['usage'] == 'input')['sha256'] = '0'*64
    path.write_text(json.dumps(value))


def bad_blob(target):
    path = target/'FROZEN-SOURCE.json'
    value = json.loads(path.read_text())
    value['git_blob'] = '0'*40
    path.write_text(json.dumps(value))


def change_profile(target, rebind):
    path = target/'inputs/PR4610-ARITHMETIC.json'
    value = json.loads(path.read_bytes())
    value['local_paid']['8'] = 0
    raw = (json.dumps(value)+'\n').encode()
    path.write_bytes(raw)
    if rebind:
        manifest_path = target/'FROZEN-SOURCE.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['sha256'] = sha256(raw).hexdigest()
        manifest['git_blob'] = sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        manifest_path.write_text(json.dumps(manifest))


V.authenticate()
results = [reject('live source pin', bad_live_pin), reject('frozen Git blob', bad_blob),
           reject('frozen source bytes', lambda p: change_profile(p, False)),
           reject('owned jobs removed with rebound hashes', lambda p: change_profile(p, True))]
print(json.dumps({'status':'PASS_FOUR_ACTUAL_MUTATION_REJECTIONS', 'rejected':results}))
