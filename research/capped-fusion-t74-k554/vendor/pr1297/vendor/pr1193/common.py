"""Strict shared I/O; construction and independent audit remain separate."""
import gzip, hashlib, importlib.util, json, sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
if not __debug__:raise RuntimeError('Assertions must remain enabled')
def read(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def identity(value):return hashlib.sha256(canonical(value)).hexdigest()
def dump(path,value):
    raw=canonical(value)
    if path.suffix=='.gz':
        raw=bytearray(gzip.compress(raw,mtime=0));raw[9]=255
    path.write_bytes(raw)
def load(path,name):
    previous=sys.modules.pop('common',None);sys.path.insert(0,str(path.parent))
    try:
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0);sys.modules.pop('common',None)
        if previous is not None:sys.modules['common']=previous
