"""Authenticated same-source numerical and physical five-stage dependencies.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
COHORT=HERE/'retained/cohort'
ROUTER=HERE/'retained/router'
INVERSE=ROUTER/'retained/inverse_window'
FORWARD=HERE/'retained/forward'

def need(ok,message):
    if not ok:raise ValueError(message)

def authenticate():
    checked={}
    for name,key,root in [('SOURCES.json','path',ROOT),('DEPENDENCIES.json','retained',HERE)]:
        for row in json.loads((HERE/name).read_text())['files']:
            if row.get('usage','input')!='input':continue
            path=root/row[key]
            need(path.is_file() and not path.is_symlink(),'regular source '+row[key])
            raw=path.read_bytes()
            need(sha256(raw).hexdigest()==row['sha256'],'source SHA256 '+row[key])
            need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
                 'source Git blob '+row[key])
            checked[row[key]]=row['sha256']
    return checked

def load(name,path):
    need(name not in sys.modules,'cold join module '+name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

@contextmanager
def numerical():
    authenticate();old=sys.path[:]
    sys.path[:0]=[str(COHORT),str(INVERSE),str(HERE)]
    source=load('cohort_sources',COHORT/'cohort_sources.py');source.ROOT=ROOT
    try:
        with source.opened() as state:yield state
    finally:sys.path[:]=old

class RelocatedRoot:
    def __truediv__(self,path):
        prefix='research/full-global-tensor-caller/';name=str(path)
        return COHORT/'vendor/global-caller'/name[len(prefix):] if name.startswith(prefix) else ROOT/name

@contextmanager
def physical():
    authenticate();old=sys.path[:];gaussian=ROOT/'research/physical-gaussian-core'
    sys.path[:0]=[str(HERE),str(ROUTER),str(INVERSE),str(INVERSE/'retained'),
                 str(gaussian),str(ROOT/'research/physical-boundary-pages')]
    source=load('gaussian_sources',gaussian/'gaussian_sources.py')
    try:
        with source.opened() as state:
            expected={
                'composed_sources':'5b9a507a5f5eb7d32d76792cac4b876070d29e91',
                'composed_engine':'646c451a4cbdf0244c7782d958f257f6606b962f',
                'composed_plan':'300ee75d4171c8f0d97118a01a4e439b72ca01d6',
                'word_product':'67e09e91103535fd1eb0b2d7d6db1fdc13de07d2',
                'ring_words':'1cb44ce6d95a1e0f9d2c6f78ecd5c7a8e8b39ba9',
                'fft_arithmetic':'606bb6c5e32ca813c927fba1a45315aae3e7de52'}
            for name,blob in expected.items():
                module=__import__(name);raw=Path(module.__file__).read_bytes()
                need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,
                     'identical dense/sparse physical dependency '+name)
            vendor=COHORT/'vendor/global-caller'
            ps=load('physical_sources',vendor/'physical_sources.py')
            ps.ROOT,ps.HERE=RelocatedRoot(),vendor;ps.authenticate()
            load('frontend',vendor/'vendor/global-boundary/frontend.py')
            state.global_boundary=load('global_h_boundary',vendor/'vendor/global-boundary/bridge.py')
            state.controls=load('physical_controls',vendor/'physical_controls.py')
            state.physical=load('physical_engine',vendor/'physical_engine.py')
            state.forward=load('banded_action',FORWARD/'action.py')
            from cardinal_counts import Count
            from records import Tape
            need(state.global_boundary.Count is Count and state.global_boundary.Tape is Tape,
                 'one actual Count/Tape identity for all five stages')
            yield state
    finally:sys.path[:]=old
