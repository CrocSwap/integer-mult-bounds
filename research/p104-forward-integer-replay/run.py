"""Run one full current scalar replay with an explicit engine."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from driver import replay
from rows import Sparse, packed_type, radix_bound
from pins import authenticate

def retained():
    spec = importlib.util.spec_from_file_location('retained_scalar', HERE/'inputs/local.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def read_word():
    return json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))

def run(engine):
    authenticate()
    word = read_word()
    start = time.perf_counter()
    if engine == 'fraction':
        result = retained().replay(word)
    elif engine == 'sparse':
        result = replay(word, Sparse)
    elif engine == 'packed':
        width, size, _, _ = radix_bound(word)
        result = replay(word, packed_type(width, size))
    else:
        raise ValueError('Unknown row engine')
    seconds = time.perf_counter()-start
    expected = json.loads((HERE/'inputs/RESULT.json').read_text())['local']
    if json.loads(json.dumps(result)) != expected:
        raise ValueError('Complete scalar receipt differs')
    return result, seconds

if __name__ == '__main__':
    result, seconds = run(sys.argv[1])
    print(json.dumps({'result': result, 'seconds': seconds}, sort_keys=True))
