"""Run one complete native component with the selected exact state engine."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import sys
import tempfile
import time
import types

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticate():
    pins = json.loads((HERE/'ORIGINS.json').read_bytes())['files']
    need(len(pins) == 9, 'Fixed source closure')
    for pin in pins:
        path = HERE/pin['path']
        need(path.is_file() and not path.is_symlink(), 'Regular source file')
        raw = path.read_bytes()
        need(len(raw) == pin['bytes'] and len(raw) <= 131072, 'Source byte bound')
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Source bytes: '+pin['path'])


def load(path, name):
    raw = path.read_bytes()
    need(len(raw) <= 131072, 'Module byte bound')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def native(engine):
    need(engine in ('baseline','candidate'), 'Known state engine')
    authenticate()
    sys.path.insert(0,str(HERE/'vendor'))
    sys.path.insert(0,str(HERE))
    compiler = 'vendor/prefix_clifford.py' if engine == 'baseline' else 'indexed_clifford.py'
    C = load(HERE/compiler,'compiler_'+engine)
    V = load(HERE/'vendor/native_gray.py','independent_native')
    D = load(HERE/'vendor/native.py','native_driver')
    word = json.loads(gzip.decompress((HERE/'vendor/inputs/WORD.json.gz').read_bytes()))
    start = time.perf_counter()
    result = D.native(word,C,V)
    component_seconds = time.perf_counter()-start
    expected = json.loads((HERE/'vendor/inputs/RESULT.json').read_bytes())['native']
    need(json.loads(json.dumps(result)) == expected, 'Complete native receipt')
    return {'native':result,'component_seconds':component_seconds}


def main():
    need(len(sys.argv) == 2, 'Supply exactly one engine')
    sys.dont_write_bytecode = True
    with tempfile.TemporaryDirectory(prefix='clifford-bytecode-', dir=os.environ.get('IMB_SCRATCH_ROOT')) as cache:
        sys.pycache_prefix = cache
        result = native(sys.argv[1])
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
