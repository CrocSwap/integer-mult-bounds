"""Immutable source capsule for one exact QUERY-only interval transformation.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    pins = json.loads((ROOT/'DEPENDENCIES.json').read_bytes())['files']
    seen = set()
    for row in pins:
        rel = Path(row['local_path'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) not in seen,
             'unique internal immutable input')
        seen.add(str(rel))
        p = ROOT/rel
        need(p.is_file() and not p.is_symlink(), 'regular capsule input')
        b = p.read_bytes()
        need(len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256']
             and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == row['git_blob'],
             'exact immutable input bytes: '+str(rel))
    return len(pins)


def module(name):
    p = ROOT/'vendor'/(name+'.py')
    spec = importlib.util.spec_from_file_location('query_interval_'+name, p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    # Compile authenticated source bytes directly, without a .pyc lookup.
    exec(compile(p.read_bytes(), str(p), 'exec'), mod.__dict__)
    return mod


def inputs():
    authenticate()
    caller = json.loads((ROOT/'data/caller_efree.json').read_bytes())
    root = json.loads((ROOT/'data/root_A_efree.json').read_bytes())
    word = json.loads(gzip.decompress((ROOT/'data/word_6936.json.gz').read_bytes()))
    return caller, root, word
