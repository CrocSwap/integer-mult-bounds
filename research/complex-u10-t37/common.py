"""Shared I/O only; no witness search or construction logic."""
import gzip, importlib.util, json, sys
from pathlib import Path
if not __debug__:
    raise RuntimeError("Assertions must remain enabled; do not use Python -O")
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
T21=ROOT/'research/complex-t21-owners'
def read(path):
    path=Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def load(path,name):
    path=Path(path)
    previous=sys.modules.get('common')
    external=not path.resolve().is_relative_to(P)
    if external:
        sys.modules.pop('common',None)
        sys.path.insert(0,str(path.parent))
    try:
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec)
        sys.modules[name]=module
        spec.loader.exec_module(module)
        return module
    finally:
        if external:
            sys.path.pop(0)
            if previous is not None: sys.modules['common']=previous
            else: sys.modules.pop('common',None)
