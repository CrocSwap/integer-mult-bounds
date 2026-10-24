"""Source-only import of the complete unchanged PR2697 runtime cohort."""
import hashlib
import importlib.abc
import importlib.util
import json
from pathlib import Path
import sys
from contextlib import contextmanager

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
COHORT='research/selected-bit-recursive-caller/predecessor'


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    data={}
    for row in manifest['files']:
        if row['usage']!='input':continue
        path=ROOT/row['path'];raw=path.read_bytes()
        need(not path.is_symlink(),'regular source input')
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256 '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
             'source blob '+row['path'])
        data[row['path']]=raw
    previous=json.loads(data['research/selected-bit-recursive-caller/PREDECESSOR.json'])
    need(previous['head']=='a53fdf4bcbe33c6732f0bec1badc8c023380f9d1','original PR2697 head')
    need(len(previous['files'])==50,'complete original cohort')
    for name,row in previous['files'].items():
        raw=data[COHORT+'/'+name]
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'original cohort identity '+name)
    return data


class Sources(importlib.abc.MetaPathFinder,importlib.abc.Loader):
    def __init__(self,data):
        self.files={}
        for name,raw in data.items():
            if name.startswith(COHORT+'/') and name.endswith('.py'):
                stem=Path(name).stem
                need(stem not in self.files,'unique runtime module '+stem)
                self.files[stem]=(ROOT/name,raw)
    def find_spec(self,fullname,path=None,target=None):
        if fullname in self.files:return importlib.util.spec_from_loader(fullname,self)
    def create_module(self,spec):return None
    def exec_module(self,module):
        path,raw=self.files[module.__name__]
        module.__file__=str(path)
        exec(compile(raw,str(path),'exec'),module.__dict__)


@contextmanager
def runtime(data):
    loader=Sources(data)
    saved={name:sys.modules.pop(name) for name in loader.files if name in sys.modules}
    sys.meta_path.insert(0,loader)
    try:
        yield loader
    finally:
        sys.meta_path.remove(loader)
        for name in loader.files:sys.modules.pop(name,None)
        sys.modules.update(saved)
