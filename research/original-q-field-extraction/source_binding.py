"""Exact public/canonical inputs and the unchanged native scalar cohort.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from pathlib import Path
from hashlib import sha256,sha1
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,message):
    if not ok:raise ValueError(message)
def authenticate():
    counts=[]
    for name in ('SOURCES.json','DEPENDENCIES.json'):
        rows=json.loads((HERE/name).read_text())['files']
        for row in rows:
            p=ROOT/row['path'];need(p.is_file() and not p.is_symlink(),'regular exact source')
            raw=p.read_bytes();need(sha256(raw).hexdigest()==row['sha256'] and
                sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
                'bound complete source '+row['path'])
        counts.append(len(rows))
    return counts
@contextmanager
def opened():
    authenticate();need('gaussian_sources' not in sys.modules,'cold Gaussian source module')
    spec=importlib.util.spec_from_file_location('gaussian_sources',ROOT/'research/physical-gaussian-core/gaussian_sources.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    with module.opened() as state:
        sys.path.insert(0,str(ROOT/'research/physical-gaussian-core'))
        for name,file in (('_extract_tapes','halo_tapes.py'),):
            spec=importlib.util.spec_from_file_location(name,HERE/'retained'/file)
            obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
            if file=='halo_tapes.py':state.B=obj
            else:state.codec=obj
        yield state
