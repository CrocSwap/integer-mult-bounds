"""Exact public/canonical source binding into one unchanged native cohort.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)

def load(name,path):
    need(name not in sys.modules,'cold source module: '+name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module

def authenticate():
    counts=[]
    for manifest in ('SOURCES.json','DEPENDENCIES.json'):
        rows=json.loads((HERE/manifest).read_text())['files']
        for row in rows:
            path=ROOT/row['path'];need(path.is_file() and not path.is_symlink(),'regular source')
            raw=path.read_bytes()
            need(sha256(raw).hexdigest()==row['sha256'] and
                 sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
                 'exact source bytes: '+row['path'])
        counts.append(len(rows))
    return counts

@contextmanager
def opened():
    authenticate();old=sys.path[:]
    gaussian=load('gaussian_sources',ROOT/'research/physical-gaussian-core/gaussian_sources.py')
    binder=load('_cached_join_tensor_sources',ROOT/'research/physical-gaussian-tensor/tensor_sources.py')
    try:
        with gaussian.opened() as state:
            with binder.bind_chirp(ROOT/'research/physical-chirp-middle',state):
                sys.path[:0]=[str(HERE/'retained/cached'),str(HERE)]
                from records import Tape
                from cardinal_counts import Count
                import cyclic_engine,chirp_consumer,chirp_tapes
                need(cyclic_engine.Tape is Tape and chirp_consumer.Tape is Tape and
                     chirp_tapes.Tape is Tape and cyclic_engine.Count is Count and
                     chirp_consumer.Count is Count,'one actual Tape/Count cohort')
                state.B=load('_cached_join_halo_tapes',HERE/'retained/halo_tapes.py')
                state.codec=load('_cached_join_codec',HERE/'retained/boundary_codec.py')
                state.intervals=load('_cached_join_intervals',ROOT/'research/certified-gaussian-recovery/intervals.py')
                yield state
    finally:sys.path[:]=old
