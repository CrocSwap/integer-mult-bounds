"""Check cold key preparation and the removed interpreter recursion boundary."""
from pathlib import Path
import json
import os
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def check(R, C, S, old):
    requests = calls = occurrences = copies = 0
    for length in range(257):
        S.clear()
        old.clear()
        op = C.Op(1,C.identity(1),[('phase',0)]*length)
        if op.zero_state() != old.prefix_state(op):
            raise ValueError('Cold state differs')
        misses = old.prefix.cache_info().misses
        if misses != length+1 or S._next != length+1:
            raise ValueError('Cold prefix/path construction count')
        requests += 1
        calls += misses
        occurrences += sum(range(length+1))
        copies += sum(range(length))
    prior = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(256)
        old.clear()
        S.clear()
        op = C.Op(1,C.identity(1),[('phase',0)]*512)
        try:
            old.prefix_state(op)
        except RecursionError:
            pass
        else:
            raise ValueError('Expected retained cold recursion boundary')
        if op.zero_state() != ([(1,0),(0,0)],0):
            raise ValueError('Deep iterative exact state')
    finally:
        sys.setrecursionlimit(prior)
        old.clear()
        S.clear()
    return {'status':'PASS_COMPACT_PREFIX_DEPTH','cold_requests':requests,
            'retained_cold_cache_misses':calls,'retained_key_gate_occurrences':occurrences,
            'retained_slice_references':copies,'deep_length':512,'recursion_limit':256,
            'retained_recursion_error':True,'iterative_exact_state':True}


def main():
    if len(sys.argv)!=1:
        raise ValueError('No checker arguments')
    sys.dont_write_bytecode = True
    sys.path.insert(0,str(HERE))
    with tempfile.TemporaryDirectory(prefix='key-depth-bytecode-',dir=os.environ.get('IMB_SCRATCH_ROOT')) as cache:
        sys.pycache_prefix = cache
        import run as R
        R.authenticate()
        C = R.load(HERE/'indexed_clifford.py','depth_compiler')
        import compact_state as S
        old = R.load(HERE/'vendor/state.py','retained_prefix_depth')
        result = check(R,C,S,old)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
