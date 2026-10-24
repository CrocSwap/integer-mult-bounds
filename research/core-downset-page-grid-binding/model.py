"""Immutable-source binding of both Core RawGaussian consumers.
JoyboyBrian with OpenAI Codex assistance. Apache-2.0.
"""
import hashlib,json,sys
from pathlib import Path
from types import FunctionType
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(test,message):
    if not test:raise ValueError(message)

def load():
    raw={}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            path=ROOT/row['path'];data=path.read_bytes()
            need(not path.is_symlink() and hashlib.sha256(data).hexdigest()==row['sha256'],'source bytes: '+row['path'])
            raw[row['path']]=data
    sys.path[:0]=[str(ROOT/'research/rational-unitary-fft'),str(ROOT/'research/full-downset-allocation'),str(ROOT/'research/gaussian-downset-grid')]
    from allocation import adapted
    from bridge import bind
    from exact import ceil_log2
    import core,gaussian,raw_gaussian
    reduced,receipt=adapted(raw['research/rational-unitary-fft/full.py'],need,ceil_log2)
    _,Raw=bind(gaussian,raw_gaussian,reduced)
    original=core.Core.__init__
    clone=FunctionType(original.__code__,dict(original.__globals__,RawGaussian=Raw),original.__name__,original.__defaults__,original.__closure__)
    clone.__kwdefaults__=original.__kwdefaults__
    Bound=type('BoundCore',(core.Core,),{'__init__':clone})
    need(core.RawGaussian is raw_gaussian.RawGaussian,'unchanged original Core global')
    return raw,core,Bound,Raw,receipt
