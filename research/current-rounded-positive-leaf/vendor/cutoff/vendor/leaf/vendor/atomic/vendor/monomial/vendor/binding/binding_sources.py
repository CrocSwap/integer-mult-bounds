"""Authenticate computational exports and establish one cold source vocabulary.

The new bootstrap replaces only archived host-side repository discovery. It
does not replay or admit the old selected theorem. Ordinary's rate is a named
predecessor premise. Computational exports remain byte-for-byte unchanged.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha1, sha256
import importlib.util
import ast
import json
import sys
from types import ModuleType, SimpleNamespace

HERE=Path(__file__).resolve().parent
_loaded=None

def need(ok,message):
    if not ok:raise ValueError(message)

def authenticate(root=HERE):
    manifest=json.loads((root/'DEPENDENCIES.json').read_text())
    original=ast.parse((root/'vendor/ordinary/source.py').read_text())
    anchors=next(ast.literal_eval(n.value) for n in original.body
                 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ARCHIVES' for t in n.targets))
    seen=set()
    for row in (*manifest['files'],*manifest['archive_members']):
        path=PurePosixPath(row['local_path'])
        need(not path.is_absolute() and '..' not in path.parts and path.parts[0]=='vendor','relative frozen export')
        need(str(path) not in seen,'unique frozen export');seen.add(str(path))
        actual=root/str(path);need(actual.is_file() and not actual.is_symlink(),'regular source export')
        data=actual.read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'changed SHA256 export: '+str(path))
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'changed Git blob export: '+str(path))
        if 'archive_name' in row:
            need(anchors[row['archive_name'].removesuffix('.tar')]==row['archive_sha256'],
                 'public loader archive SHA256 anchor')
    return len(seen)

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    out=importlib.util.module_from_spec(spec);sys.modules[name]=out
    exec(compile(Path(path).read_bytes(),str(path),'exec'),out.__dict__)
    return out

def activate():
    global _loaded
    if _loaded is not None:return _loaded
    authenticate()
    need(not any(x in sys.modules for x in ('loader','source','native_sources','words','records')),
         'cold computational namespace')
    runtime=HERE/'vendor/runtime'
    caller=runtime/'pr2809/inputs/pr2753'
    loader=ModuleType('loader');loader.CALLER=caller;sys.modules['loader']=loader
    for p in (caller/'predecessor/vendor',caller/'predecessor',caller,
              runtime/'pr2809',runtime/'pr2809/inputs/pr2769/vendor'):
        sys.path.insert(0,str(p))
    codec=module('bank_codec',runtime/'pr2809/inputs/pr2769/codec.py')
    loader.activate=lambda:codec
    padding=module('padding',runtime/'pr2808/vendor/pr2786/padding.py')
    outer=module('outer',runtime/'pr2808/outer.py')
    source=ModuleType('source');source.activate=lambda:(loader,padding,outer);sys.modules['source']=source
    sys.path.insert(0,str(HERE/'vendor/ordinary'))
    module('streams',HERE/'vendor/reference/streams.py')
    reference=module('compact_reference',HERE/'vendor/reference/compact.py')
    native=ModuleType('native_sources');native.activate=lambda:(source,reference);sys.modules['native_sources']=native
    sys.path.insert(0,str(HERE/'vendor/compact'))
    import compact_engine, records, words, cardinal_counts, ordinary, session, scratch_pool
    abi=module('current_lifecycle_abi',HERE/'vendor/lifecycle/machine.py')
    _loaded=SimpleNamespace(engine=compact_engine,records=records,words=words,
                           counts=cardinal_counts,ordinary=ordinary,session=session,
                           scratch=scratch_pool,abi=abi,parking=codec)
    return _loaded
