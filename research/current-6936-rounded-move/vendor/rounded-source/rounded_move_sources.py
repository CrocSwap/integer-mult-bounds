"""One authenticated object vocabulary for a once-rounded exact raw MOVE.

Computational source bytes are unchanged. The direct coordinator's positive
child is deliberately replaced by the proved private-cutoff child; this is
an explicit supplier substitution, not an invisible discovery equivalence.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha1,sha256
import importlib.util
import json
from pathlib import Path,PurePosixPath
import sys
from types import ModuleType,SimpleNamespace

HERE=Path(__file__).resolve().parent
_state=None

def need(ok,message):
    if not ok:raise ValueError(message)

def authenticate(root=HERE):
    seen=set()
    for row in json.loads((root/'DEPENDENCIES.json').read_text())['files']:
        name=PurePosixPath(row['path'])
        need(not name.is_absolute() and '..' not in name.parts and name.parts[0]=='vendor',
             'relative retained source')
        file=root/str(name);need(file.is_file() and not file.is_symlink() and str(name) not in seen,
                                'unique regular source')
        data=file.read_bytes();seen.add(str(name))
        need(sha256(data).hexdigest()==row['sha256'] and
             sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'exact public rounded-MOVE dependency: '+str(name))
    for row in json.loads((root/'SHARED-SOURCE-JOIN.json').read_text())['files']:
        data=(root/row['shared_path']).read_bytes()
        need(sha256(data).hexdigest()==row['sha256'] and
             sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'unchanged serial shared source: '+row['serial_path'])
    return len(seen)

def load(name,path):
    need(name not in sys.modules,'cold source name: '+name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module

def activate():
    global _state
    if _state is None:
        authenticate();root=HERE/'vendor/rounded';sys.path.insert(0,str(root))
        discovery=load('rounded_sources',root/'rounded_sources.py')
        prior=discovery.activate()
        rounded=load('rounded_leaf',root/'rounded_leaf.py')
        common=prior.common;leaf=prior.old.old
        serial_state=SimpleNamespace(adapter=common.monomial,state=common.shared,
            rows=prior.old.rows,abi=common.abi,codec=common.codec,selected=common.selected)
        shim=ModuleType('serial_sources');shim.activate=lambda:serial_state;shim.need=need
        need('serial_sources' not in sys.modules,'cold serial source namespace')
        sys.modules['serial_sources']=shim
        serial=load('rounded_move_serial_view',HERE/'vendor/direct/vendor/serial/column_view.py')
        direct_state=SimpleNamespace(leaf=leaf,child=prior.cutoff.PositiveChild,
            catalog=prior.catalog,serial=serial.SerialProvider,abi=common.abi,
            common=common,atomic=leaf.core.AtomicMove)
        shim=ModuleType('direct_sources');shim.activate=lambda:direct_state
        shim.need=need;shim.load=load;shim.HERE=prior.root
        need('direct_sources' not in sys.modules,'cold direct source namespace')
        sys.modules['direct_sources']=shim
        direct=load('direct_move',HERE/'vendor/direct/direct_move.py')
        need(serial.S.adapter is common.monomial and serial.S.abi is rounded.A
             and serial.S.codec is rounded.C and direct.S.abi is rounded.A
             and direct.S.child is prior.cutoff.PositiveChild,
             'one exact numerical vocabulary and explicit cutoff-child substitution')
        _state=SimpleNamespace(prior=prior,rounded=rounded,direct=direct,serial=serial,
                               catalog=prior.catalog,common=common,abi=common.abi,root=root)
    return _state
