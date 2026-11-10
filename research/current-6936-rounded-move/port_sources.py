"""Authenticated isolated source port; computational provider bodies unchanged.

Only two import lines are redirected to this fixed discovery object. This
is an explicit new catalogue binding, not equivalence of the two source words.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha1,sha256
import importlib.util,json,sys
from pathlib import Path,PurePosixPath
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
_base=_state=_direct=_provider=None

def need(ok,message):
    if not ok:raise ValueError(message)

def authenticate():
    seen=set()
    for row in json.loads((HERE/'DEPENDENCIES.json').read_text())['files']:
        name=PurePosixPath(row['path'])
        need(not name.is_absolute() and '..' not in name.parts and str(name) not in seen,
             'unique relative retained source')
        path=HERE/str(name);need(path.is_file() and not path.is_symlink(),'regular retained source')
        data=path.read_bytes();seen.add(str(name))
        need(sha256(data).hexdigest()==row['sha256'] and
             sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'exact public source '+str(name))
    return len(seen)

def load(name,path,imports=None):
    need(name not in sys.modules,'cold private module name')
    data=path.read_text()
    if imports:
        old,new=imports;need(data.count(old)==1,'one exact discovery import')
        data=data.replace(old,new)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    exec(compile(data,str(path),'exec'),module.__dict__)
    return module

def base():
    global _base
    if _base is None:
        authenticate();root=HERE/'vendor/rounded-source';sys.path.insert(0,str(root))
        _base=load('rounded_move_sources',root/'rounded_move_sources.py').activate()
        # Restore this package as the public import entry after the frozen
        # predecessor has discovered its private closure.
        sys.path.insert(0,str(HERE))
    return _base

def direct_activate():
    need(_direct is not None,'fixed port discovery before constructor')
    return _direct

def activate():
    global _state,_direct
    if _state is None:
        b=base();catalog=load('proposal6936_catalog',HERE/'source_catalog.py')
        direct_values=dict(vars(b.direct.S));direct_values['catalog']=catalog
        _direct=SimpleNamespace(**direct_values)
        direct=load('proposal6936_direct',HERE/'vendor/rounded-source/vendor/direct/direct_move.py',
                    ('from direct_sources import activate, need',
                     'from port_sources import direct_activate as activate, need'))
        state=dict(vars(b));state.update(catalog=catalog,direct=direct)
        _state=SimpleNamespace(**state)
    return _state

def provider_class():
    global _provider
    if _provider is None:
        activate()
        module=load('proposal6936_rounded',HERE/'vendor/rounded-source/rounded_move.py',
                    ('from rounded_move_sources import activate,need',
                     'from port_sources import activate,need'))
        _provider=module.RoundedMove
    return _provider
