"""Whole-file pins and named source clauses, without projected execution.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1,sha256
import ast,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)

def authenticate():
    counts=[]
    for name in ('SOURCES.json','DEPENDENCIES.json'):
        rows=json.loads((HERE/name).read_text())['files']
        for row in rows:
            p=ROOT/row['path'];need(p.is_file() and not p.is_symlink(),'regular pinned source')
            raw=p.read_bytes()
            need(sha256(raw).hexdigest()==row['sha256'] and
                 sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
                 'exact source bytes '+row['path'])
        counts.append(len(rows))
    return counts

def node_at(text,names):
    node=ast.parse(text)
    for name in names:
        selected=[n for n in node.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==name]
        need(len(selected)==1,'one bound source clause');node=selected[0]
    return ast.dump(node,include_attributes=False)

def bind_clauses():
    rows=json.loads((HERE/'CLAUSES.json').read_text())['clauses']
    for row in rows:
        node=node_at((ROOT/row['path']).read_text(),row['names'])
        need(sha256(node.encode()).hexdigest()==row['sha256'],'bound original source clause')
    return len(rows)

def load(name,path):
    need(name not in sys.modules,'cold source module '+name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

@contextmanager
def opened():
    authenticate();old=sys.path[:]
    gaussian=load('gaussian_sources',ROOT/'research/physical-gaussian-core/gaussian_sources.py')
    try:
        with gaussian.opened() as state:
            state.B=load('_expansion_return_tapes',HERE/'retained/halo_tapes.py')
            state.codec=load('_expansion_return_codec',HERE/'retained/boundary_codec.py')
            yield state
    finally:sys.path[:]=old
