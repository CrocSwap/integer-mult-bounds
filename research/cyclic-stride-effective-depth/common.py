"""Load the immutable predecessor and expose exact arithmetic helpers."""
from pathlib import Path
import importlib.util
import sys

P=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:
        raise ValueError(message)


def load(path,name):
    path=path.resolve()
    if name in sys.modules:
        module=sys.modules[name]
        need(Path(module.__file__).resolve()==path,'local module binding: '+name)
        return module
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


predecessor=load(P/'vendor/pr846/verify.py','effective_depth_predecessor')
original=predecessor.st
need(Path(original.__file__).resolve()==P/'vendor/pr846/stride.py','original solver binding')
